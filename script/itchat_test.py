import itchat
from itchat.content import *

@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    print(msg)
    if '微信机器人测试' in msg['Text']:
        itchat.send('中文测试成功', msg['FromUserName'])
        # itchat.send('@img@{}'.format('test.jpg'), msg['FromUserName'])

@itchat.msg_register(FRIENDS)
def add_friend(msg):
    print(msg)
    itchat.add_friend(**msg['Text']) # 该操作会自动将新好友的消息录入，不需要重载通讯录
    itchat.send_msg('Nice to meet you!', msg['RecommendInfo']['UserName'])
    friend = itchat.search_friends(userName=msg['RecommendInfo']['UserName'])
    chatrooms = itchat.search_chatrooms(name='CC微信机器人开发')
    itchat.add_member_into_chatroom(chatrooms[0]['UserName'], [friend], useInvitation=True)

itchat.auto_login(hotReload=True)
itchat.run(blockThread=True)