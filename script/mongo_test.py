import pymongo
import time

MONGO = {
    "password":"rock",
    "port":"27017",
    "host":"192.168.8.28",
    "user":"liliang",
    "db":"d_weixin_robot"
}

conn = pymongo.MongoClient(MONGO['host'], int(MONGO['port']))
db = eval("conn." + MONGO['db'])
ret = db.authenticate(MONGO['user'], MONGO['password'], MONGO['db'])
print(db,ret)
robot_info = {
    'id': 11111,
    'name': 'shit',
    'status': 1,
    'duty': 'robot',
    'last_update': int(time.time())
}
rows = db.robot.find()
for row in rows:
    print(row)
ret = db.robot.update_one({'name': 'shit'}, {'$set': robot_info}, True)
print(ret)