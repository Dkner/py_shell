import sys
import pymongo
import requests
import pymysql

reload(sys)
sys.setdefaultencoding('utf-8')

mongo_conf = {
    'host':'10.0.6.147',
    'port':'27017',
    'user':'ccinforoot',
    'password':'283CC4B26042010B'
}

mysql_conf = {
    'host':'10.0.4.111',
    'user':'yunying_new',
    'port':3306,
    'password':'5v3v8p7eJNzUTidW',
    'charset':'utf8',
    'cursorclass':pymysql.cursors.DictCursor
}


def connect_mongo(dbname):
    if not mongo_conf or not mongo_conf.has_key('host') or not mongo_conf.has_key(
            'port') or not mongo_conf.has_key('user') or not mongo_conf.has_key('password'):
        return False
    conn = pymongo.MongoClient(mongo_conf['host'], int(mongo_conf['port']))
    db = eval("conn." + dbname)
    ret = db.authenticate(mongo_conf['user'], mongo_conf['password'], dbname)
    if not ret:
        return (conn, False)
    return (conn, db)


def connect_mysql(dbname):
    try:
        conn = pymysql.connect(host=mysql_conf['host'],
                               port=mysql_conf['port'],
                               user=mysql_conf['user'],
                               password=mysql_conf['password'],
                               db=dbname,
                               charset=mysql_conf['charset'],
                               cursorclass=pymysql.cursors.DictCursor)
    except Exception,e:
        print e
        return False
    return conn


def write(connection, sql='', args=()):
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, args)

        connection.commit()
        return True
    finally:
        pass


def read(connection, sql='', args=()):
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, args)
            result = cursor.fetchall()
            return result, cursor.rowcount
    finally:
        pass


def dump_wx_content():
    # get src_id from mysql table:t_msg_target_label_history
    conn = connect_mysql('d_push')
    sql = "SELECT `src_id` FROM `t_msg_target_label_history` WHERE `msg_template_id`=%s ORDER BY `create_time` DESC LIMIT 2500"
    result, ret = read(conn, sql, (446,))
    if ret > 0:
        try:
            for index, item in enumerate(result):
                try:
                    # get wx content from ccinfo api
                    params = {'rec_id': item['src_id']}
                    r = requests.get('http://10.0.5.43/ccinfo/v2/weixin_article', params=params)
                    ret = r.json()
                    # get html and save file
                    print ret['title'], ret['content']
                    html = requests.get('http://articles.camcard.com/gzh/'+ret['content'], verify=False)
                    if not html:
                        continue
                    filename = ret['title'].replace('/','') .replace('\\','')
                    with open('file/' + filename + '.html', 'w') as f:
                        f.write(html.content.encode('utf8'))
                except Exception,e:
                    print e
        finally:
            pass


def dump_news_content():
    # get src_id from mysql table:t_msg_target_label_history
    conn = connect_mysql('d_push')
    sql = "SELECT `src_id` FROM `t_msg_target_label_history` WHERE `msg_template_id` in (%s,%s,%s,%s,%s) ORDER BY `create_time` DESC LIMIT 2500"
    result, ret = read(conn, sql, (440,441,450,457,477))
    if ret > 0:
        try:
            for index, item in enumerate(result):
                try:
                    # get news content from ccinfo api
                    params = {'rec_id': item['src_id']}
                    r = requests.get('http://10.0.5.43/ccinfo/v2/query_news', params=params)
                    ret = r.json()
                    # get html and save file
                    link = ret['link']
                    print ret['title'],link
                    if 'http' not in link:
                        link = 'http://'+link
                    html = requests.get(link, verify=False)
                    if not html:
                        continue
                    filename = ret['title'].replace('/', '').replace('\\', '')
                    with open('file/' + filename + '.html', 'w') as f:
                        f.write(html.content.encode('utf8'))
                except Exception,e:
                    print e
        finally:
            pass


def main():
    dump_wx_content()
    dump_news_content()


if __name__ == '__main__':
    main()


