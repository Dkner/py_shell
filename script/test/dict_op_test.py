'''
根据key_2_trans将source_data中对应的数据字段改名并提取出来，得到一个新列表clean_data
clean_data = [
    {
        "desc": "90后连续创业者，15岁时靠自编游戏吸引数十万玩家，大三时曾参与创办互联网公司。",
        "founder": "李夏炜",
        "pos": "创始人兼CEO"
    },
    ...
]
'''
source_data = [
    {
        "attachUid": 0,
        "avatar": "",
        "cid": 24649709,
        "id": 259275,
        "intro": "90后连续创业者，15岁时靠自编游戏吸引数十万玩家，大三时曾参与创办互联网公司。",
        "isFounder": 1,
        "isFundManager": 0,
        "isShow": 1,
        "name": "李夏炜",
        "position": "创始人兼CEO",
        "positionValue": 1000,
        "updateTime": 1495679755000,
        "weixinQr": ""
    },
    {
        "attachUid": 0,
        "avatar": "",
        "cid": 24649709,
        "id": 259274,
        "intro": "大学时打造过一款果汁品牌，成为航空公司的特供品，从美国留学归来后与黄贤振共同创业，涉足汽车、健身等多个领域。",
        "isFounder": 1,
        "isFundManager": 0,
        "isShow": 1,
        "name": "卓佳鑫",
        "position": "创始人",
        "positionValue": 900,
        "updateTime": 1495679755000,
        "weixinQr": ""
    },
    {
        "attachUid": 0,
        "avatar": "",
        "cid": 24649709,
        "id": 259276,
        "intro": "90后，17岁时靠国际进出口贸易赚得数百万美金，从新西兰留学归来后自主创业，从事地产、金融投资等领域。",
        "isFounder": 1,
        "isFundManager": 0,
        "isShow": 1,
        "name": "黄贤振",
        "position": "联合创始人",
        "positionValue": 800,
        "updateTime": 1495679755000,
        "weixinQr": ""
    }
]

key_2_trans = {
    'intro': 'desc',
    'name': 'founder',
    'position': 'pos',
}