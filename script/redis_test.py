import redis

def connect_redis(**kw):
    connection = redis.Redis(**kw)
    return connection


redis_config = {
    "host": "localhost",
    "port": 26381,
    "password": "A3fg839j1ca",
    "db": 15,
    "encoding": "utf-8"
}
conn = connect_redis(**redis_config)
print(conn.ping())
conn.zadd('zset_test', 'alibaba', 2)
conn.zadd('zset_test', 'jingdong', 1)
conn.zincrby('zset_test', 'tencent', 1)
print(conn.zrangebyscore('zset_test', 0, 1))
score = conn.zscore('zset_test', 'alibaba')
if score < 3:
    print(str(redis_config))