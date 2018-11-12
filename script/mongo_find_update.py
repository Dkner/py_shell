import re
import pymongo

right_format = 'http://qxb-img.oss-cn-hangzhou.aliyuncs.com/trademark/50ecaea23158e8323c71e18fd1b7a6cc.jpg'
error_format = 'http://qxb-img.oss-cn-hangzhou.aliyuncs.com.oss-proxy-sandbox.qixin.com/trademark/50ecaea23158e8323c71e18fd1b7a6cc.jpg'

error_format = re.sub(r'\.oss-proxy-sandbox.qixin.com', '', error_format)
print(error_format)
assert error_format == right_format

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
mongo_collection = eval('db.{}'.format('MONGO_COLLECTION'))
count = mongo_collection.count()
start, step = 0, 50
while start < count:
    print(start)
    this_loop_records = mongo_collection.find({'image_url': {'$regex': '.*\.oss-proxy-sandbox.qixin.com.*'}}).limit(step).skip(start)
    for i in this_loop_records:
        right_image_url = re.sub(r'\.oss-proxy-sandbox.qixin.com', '', i['image_url'])
        mongo_collection.update_one({'_id': i['_id']}, {'$set': {'image_url': right_image_url}}, upsert=False)
    start += step