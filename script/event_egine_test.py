# encoding: UTF-8
import time
from threading import Thread, Timer
from event_egine import EventManager, MyEvent

#事件名称  新文章
EVENT_ARTICAL = "Event_Artical"

#事件源 公众号
class PublicAccounts:
    def __init__(self,eventManager):
        self.__eventManager = eventManager

    def WriteNewArtical(self):
        while 1:
            #事件对象，写了新文章
            event = MyEvent(type_=EVENT_ARTICAL)
            event.dict["artical"] = u'如何写出更优雅的代码\n'
            #发送事件
            print 'new shit'
            self.__eventManager.SendEvent(event)
            print u'公众号发送新文章\n'
            time.sleep(2)

#监听器 订阅者
class Listener:
    def __init__(self,username):
        self.__username = username

    #监听器的处理函数 读文章
    def ReadArtical(self,event):
        print(u'%s 收到新事件：%s' % (self.__username, event))
        print(u'正在阅读新文章内容：%s'  % event.dict["artical"])

"""测试函数"""
#--------------------------------------------------------------------
def test():
    listner1 = Listener("thinkroom") #订阅者1
    listner2 = Listener("steve")#订阅者2

    eventManager = EventManager()

    #绑定事件和监听器响应函数(新文章)
    eventManager.AddEventListener(EVENT_ARTICAL, listner1.ReadArtical)
    eventManager.AddEventListener(EVENT_ARTICAL, listner2.ReadArtical)
    eventManager.Start()

    publicAcc = PublicAccounts(eventManager)
    an_editor = Thread(target=publicAcc.WriteNewArtical)
    an_editor.start()

if __name__ == '__main__':
    test()