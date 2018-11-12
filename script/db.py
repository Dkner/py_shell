# -*- coding: utf-8 -*-

import os
import sha
import contextlib
import functools
import random
import uuid
import time
import threading
import logging

import gevent
from sqlalchemy import event
from sqlalchemy import create_engine as sqlalchemy_create_engine
from sqlalchemy import types
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import (
    Executable, ClauseElement, Insert, _literal_as_text)
from etrace import trace

from .conf import settings
from .huskar import (
    get_infra_settings, explore_infra_settings, is_infra_settings_enabled)
from .log import get_sql_logger
from .utils import gen_task_hash
from .tx_task import gen_task_hash as gen_tx_task_hash
from .ves.env import is_in_dev
from .sam.utils import _format_db_dsn
from .tracker import get_rpc_meta_by_name
from .ves.config import load_app_config
from .tracker import ZeusTracker
from .etrace_wrapper import is_etrace_enabled


def patch_column_type_checker():
    def coerce_compared_value(self, op, value):
        return self

    def predicate_type(types):
        def wrapper(func):
            @functools.wraps(func)
            def bind_processor(*args, **kwds):
                processor = func(*args, **kwds)
                if processor is None:
                    def validator(value):
                        if not isinstance(value, types):
                            raise TypeError("ONLY IN DEV: Column type defined"
                                            " in model: %s, Got: %s"
                                            % (types, type(value)))
                        return value
                else:
                    def validator(value):
                        res = processor(value)
                        if not isinstance(res, types):
                            raise TypeError("ONLY IN DEV: Column type defined"
                                            " in model: %s, Got: %s"
                                            % (types, type(value)))
                        return res
                return validator
            return bind_processor
        return wrapper

    Integer.coerce_compared_value = coerce_compared_value
    Integer.bind_processor = predicate_type((int, long))(
        Integer.bind_processor
        )

    String.coerce_compared_value = coerce_compared_value
    String.bind_processor = predicate_type(basestring)(String.bind_processor)


class StrongInteger(types.TypeDecorator):
    impl = types.Integer

    def process_bind_param(self, value, dialect):
        if not isinstance(value, (int, long)):
            value = int(value)
        return value


RAISE_CLOSING_EXCEPTION = False
db_ctx = threading.local()
logger = logging.getLogger(__name__)


class TaskHashMixin(object):
    @classmethod
    def gen_task_hash(cls, conn, task_name, task_args):
        raise NotImplementedError


class ShardedTaskHashMixin(TaskHashMixin):
    _hash_seq_name = None

    @classmethod
    def _query_for_task_hash(cls, conn, vanilla_task_hash, **kwargs):
        params = {
            'seq_name': cls._hash_seq_name,
            'task_hash': vanilla_task_hash,
        }
        params.update(kwargs)
        stmt = "SELECT next_value FROM dal_dual" \
               " WHERE seq_name=:seq_name" \
               " AND task_hash=:task_hash"
        for kw in kwargs:
            stmt += " AND {0}=:{0}".format(kw)
        res = conn.execute(stmt, params)
        return res.scalar().strip().lower()

    @classmethod
    def gen_vanilla_task_hash(cls, conn, task_name, task_args):
        tbl_name = cls.__tablename__
        if tbl_name.endswith('_mysql_task'):
            # mysql async task
            return gen_tx_task_hash(conn, task_name, task_args)
        elif tbl_name.endswith('_task'):
            # mysql write task
            return gen_task_hash(conn, task_name, task_args)
        else:
            raise ValueError('unknown task type for model: {!r}'.format(cls))

    @classmethod
    def gen_sharded_task_hash(cls, conn, task_name, task_args):
        raise NotImplementedError

    @classmethod
    def gen_task_hash(cls, conn, task_name, task_args):
        return cls.gen_sharded_task_hash(conn, task_name, task_args)


class UpsertMixin(object):
    @classmethod
    def upsert(cls):
        """Build :class:`zeus_core.db.Upsert` statement.

        Example::

            class Foo(ModelBase, UpsertMixin):
                @classmethod
                def ensure(cls, name):
                    with DBSession() as db:
                        db.execute(cls.upsert().values(name=name))
        """
        return Upsert(cls.__table__)


class Explain(Executable, ClauseElement):
    def __init__(self, stmt, analyze=False):
        self.statement = _literal_as_text(stmt)
        self.analyze = analyze


class Upsert(Insert):
    pass


@compiles(Explain, 'mysql')
def mysql_explain(element, compiler, **kw):
    text = 'EXPLAIN '
    if element.analyze:
        text += 'EXTENDED '
    text += compiler.process(element.statement)
    return text


@compiles(Upsert, 'mysql')
def mysql_upsert(insert_stmt, compiler, **kwargs):
    # A modified version of https://gist.github.com/timtadh/7811458.
    # The license (3-Clause BSD) is in the repository root.
    parameters = insert_stmt.parameters
    if insert_stmt._has_multi_parameters:
        parameters = parameters[0]
    keys = list(parameters or {})
    pk = insert_stmt.table.primary_key
    auto = None
    if (len(pk.columns) == 1 and
            isinstance(pk.columns.values()[0].type, Integer) and
            pk.columns.values()[0].autoincrement):
        auto = pk.columns.keys()[0]
        if auto in keys:
            keys.remove(auto)
    insert = compiler.visit_insert(insert_stmt, **kwargs)
    ondup = 'ON DUPLICATE KEY UPDATE'
    updates = ', '.join(
        '%s = VALUES(%s)' % (c.name, c.name)
        for c in insert_stmt.table.columns
        if c.name in keys
    )
    if auto is not None:
        last_id = '%s = LAST_INSERT_ID(%s)' % (auto, auto)
        if updates:
            updates = ', '.join((last_id, updates))
        else:
            updates = last_id
    upsert = ' '.join((insert, ondup, updates))
    return upsert


def scope_func():
    if not getattr(db_ctx, 'session_stack', None):
        db_ctx.session_stack = 0
    return (threading.current_thread().ident, db_ctx.session_stack)


@contextlib.contextmanager
def session_stack():
    if not getattr(db_ctx, 'session_stack', None):
        db_ctx.session_stack = 0

    try:
        db_ctx.session_stack += 1
        yield
    finally:
        db_ctx.session_stack -= 1


def close_connections(engines, transactions):
    if engines and transactions:
        for engine in engines:
            for parent in transactions:
                conn = parent._connections.get(engine)
                if conn:
                    conn[0].invalidate()


def comfirm_close_when_exception(exc):
    def wrapper(func):
        @functools.wraps(func)
        def comfirm_close(self, *args, **kwds):
            current_transactions = tuple()
            if self.transaction is not None:
                current_transactions = self.transaction._iterate_parents()
            try:
                func(self, *args, **kwds)
            except exc:
                logger.debug("Exception occurred and close connections.")
                close_connections(
                    self.engines.itervalues(), current_transactions)
                raise
        return comfirm_close
    return wrapper


class RoutingSession(Session):
    _name = None
    CLOSE_ON_EXIT = True

    def __init__(self, engines, *args, **kwds):
        super(RoutingSession, self).__init__(*args, **kwds)
        self.engines = engines
        self.slave_engines = [e for role, e in engines.items()
                              if role != 'master']
        assert self.slave_engines, ValueError("DB slave configs is wrong!")
        self._id = self.gen_id()
        self._close_on_exit = self.CLOSE_ON_EXIT
        get_sql_logger().ctx.current_session_id = self._id

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_val is None:
                self.flush()
                self.commit()
            elif isinstance(exc_val, SQLAlchemyError):
                self.rollback()
        except SQLAlchemyError:
            self.rollback()
            raise
        finally:
            if self._close_on_exit:
                self.close()
            self._close_on_exit = self.CLOSE_ON_EXIT

    def close_on_exit(self, value):
        self._close_on_exit = bool(value)
        return self

    def explain(self, query, analyze=False):
        """EXPLAIN for mysql
        :param query: `Query` Object
        :param analyze: if add `EXTENDED` before query statement
        """
        plan = self.execute(Explain(query, analyze)).fetchall()
        for item in plan:
            for k, v in item.items():
                print '%s: %s' % (k, v)

    def get_bind(self, mapper=None, clause=None):
        if self._name:
            return self.engines[self._name]
        elif self._flushing:
            return self.engines['master']
        else:
            return random.choice(self.slave_engines)

    def using_bind(self, name):
        self._name = name
        return self

    @comfirm_close_when_exception(gevent.Timeout)
    def commit(self):
        super(RoutingSession, self).commit()

    @comfirm_close_when_exception(gevent.Timeout)
    def flush(self):
        super(RoutingSession, self).flush()

    @comfirm_close_when_exception(BaseException)
    def rollback(self):
        with gevent.Timeout(5):
            super(RoutingSession, self).rollback()

    @comfirm_close_when_exception(BaseException)
    def close(self):
        with gevent.Timeout(5):
            super(RoutingSession, self).close()

    def gen_id(self):
        pid = os.getpid()
        tid = threading.current_thread().ident
        clock = time.time() * 1000
        address = id(self)
        hash_key = self.hash_key
        return sha.new('{0}\0{1}\0{2}\0{3}\0{4}'.format(
            pid, tid, clock, address, hash_key)).hexdigest()[:20]


def patch_engine(engine):
    pool = engine.pool
    pool._origin_recyle = pool._recycle
    del pool._recycle
    setattr(pool.__class__, '_recycle', RecycleField())
    return engine


def create_engine(*args, **kwds):
    engine = patch_engine(sqlalchemy_create_engine(*args, **kwds))
    get_sql_logger().register(engine)
    event.listen(engine, 'before_cursor_execute', sql_commenter, retval=True)
    return engine


def make_session(engines, force_scope=False, info=None):
    if is_in_dev() or force_scope:
        scopefunc = scope_func
    else:
        scopefunc = None

    session = scoped_session(
        sessionmaker(
            class_=RoutingSession,
            expire_on_commit=False,
            engines=engines,
            info=info or {"name": uuid.uuid4().hex},
        ),
        scopefunc=scopefunc
    )
    return session


def gen_commit_deco(session_factory, raise_exc, error_code):
    def decorated(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                with session_factory():
                    return func(*args, **kwargs)
            except SQLAlchemyError as e:
                raise_exc(error_code, repr(e))
        return wrapper
    return decorated


def sql_commenter(conn, cursor, statement, params, context, executemany):
    comment_map = {}

    if is_etrace_enabled():
        request_id = ZeusTracker.get_request_id()
        trace.gen_next_remote_id()
        role = conn._execution_options.get('role', 'unknown')

        comment_map.update(
            rid=request_id,
            rpcid=trace.get_current_rpc_id(),
            role=role,
            appid=load_app_config().app_id,
        )

    routing_key = get_rpc_meta_by_name('routing-key')

    if routing_key:
        routing_key = routing_key.split("=", 1)
        if len(routing_key) == 2:
            shardkey, shardvalue = routing_key
            comment_map.update(shardkey=shardkey, shardvalue=shardvalue)

    if comment_map:
        statement = "/* E:%s:E */ %s" % (
            '&'.join(
                '{}={}'.format(key, value) for key, value
                in comment_map.iteritems()
                ),
            statement,
        )

    return statement, params


class ModelMeta(DeclarativeMeta):
    def __new__(self, name, bases, attrs):
        cls = DeclarativeMeta.__new__(self, name, bases, attrs)

        from .cache import CacheMixinBase
        for base in bases:
            if issubclass(base, CacheMixinBase) and hasattr(cls, "_hook"):
                cls._hook.add(cls)
                break
        return cls


def model_base(cls=object, **kwds):
    """Construct a base class for declarative class definitions, kwds params
    must be a subset of ``declarative_base`` params in sqlalchemy.

    :param cls:
      Atype to use as the base for the generated declarative base class.
      Defaults to :class:`object`. May be a class or tuple of classes.
    """
    return declarative_base(cls=cls, metaclass=ModelMeta, **kwds)


class RecycleField(object):
    def __get__(self, instance, klass):
        if instance is not None:
            return int(random.uniform(0.75, 1) * instance._origin_recyle)
        raise AttributeError


class DBManager(object):
    def __init__(self):
        self.session_map = {}

    def create_sessions(self):
        if is_infra_settings_enabled('database'):
            names = explore_infra_settings('database')
            self._create_sessions_via_infra_settings(names)
        else:
            from zeus_core.utils import EmptyValue
            from zeus_core.conf import settings
            if not EmptyValue.is_empty(settings.DB_SETTINGS):
                self._create_sessions_via_traditional_settings()

    def _create_sessions_via_infra_settings(self, names):
        for name in names:
            db_settings = get_infra_settings('database', name)
            try:
                self.add_session(name, {
                    'urls': {
                        'master': db_settings['master'],
                        'slave': db_settings.get('slave',
                                                 db_settings['master']),
                    },
                    'pool_recycle': settings.DB_POOL_RECYCLE,
                    'max_overflow': db_settings.get(
                        'max_overflow',
                        db_settings.get(
                            'max_pool_overflow', settings.DB_MAX_OVERFLOW)),
                    'pool_size': db_settings.get(
                        'pool_size',
                        db_settings.get(
                            'max_pool_size', settings.DB_POOL_SIZE)),
                })
            except KeyError as e:
                raise KeyError((
                    'Your are using infra settings with database '
                    'but the key is not configure: {0}\nSee also the '
                    'document https://ele.to/NXlW5U'
                ).format(e))

    def _create_sessions_via_traditional_settings(self):
        if not settings.DB_SETTINGS:
            raise ValueError('DB_SETTINGS is empty, check it')
        for db, db_configs in settings.DB_SETTINGS.iteritems():
            self.add_session(db, db_configs)

    def get_session(self, name):
        try:
            return self.session_map[name]
        except KeyError:
            raise KeyError(
                '`%s` session not created, check `DB_SETTINGS`'
                ' or `database` if use infra key.' % name)

    def add_session(self, name, config):
        if name in self.session_map:
            raise ValueError("Duplicate session name {},"
                             "please check your config".format(name))
        session = self._make_session(name, config)
        self.session_map[name] = session
        return session

    @classmethod
    def _make_session(cls, db, config):
        urls = config['urls']
        for name, url in urls.iteritems():
            assert url, "Url configured not properly for %s:%s" % (db, name)
        pool_size = config.get('pool_size', settings.DB_POOL_SIZE)
        max_overflow = config.get(
            'max_overflow', settings.DB_MAX_OVERFLOW)
        pool_recycle = settings.DB_POOL_RECYCLE
        engines = {
            role: cls.create_engine(_format_db_dsn(dsn),
                                    pool_size=pool_size,
                                    max_overflow=max_overflow,
                                    pool_recycle=pool_recycle,
                                    execution_options={'role': role})
            for role, dsn in urls.iteritems()
        }
        return make_session(engines, info={"name": db})

    def close_sessions(self, should_close_connection=False):
        dbsessions = self.session_map
        for dbsession in dbsessions.itervalues():
            if should_close_connection:
                session = dbsession()
                if session.transaction is not None:
                    close_connections(session.engines.itervalues(),
                                      session.transaction._iterate_parents())
            try:
                dbsession.remove()
            except: # noqa
                logger.exception("Error closing session")

    @classmethod
    def create_engine(cls, *args, **kwds):
        engine = patch_engine(sqlalchemy_create_engine(*args, **kwds))
        get_sql_logger().register(engine)
        event.listen(engine, 'before_cursor_execute', sql_commenter,
                     retval=True)
        return engine


db_manager = DBManager()
