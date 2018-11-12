import threading
import time

# try:
#     from synchronize import make_synchronized
# except ImportError:
#     def make_synchronized(func):
#         import threading
#         func.__lock__ = threading.Lock()
#
#         def synced_func(*args, **kws):
#             with func.__lock__:
#                 return func(*args, **kws)
#
#         return synced_func
#
# class Singleton(object):
#     instance = None
#     __lock = threading.Lock()
#
#     @make_synchronized
#     def __new__(cls, *args, **kw):
#         if cls.instance is None:
#             cls.instance = object.__new__(cls, *args, **kw)
#         return cls.instance


class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance

class MyClass(metaclass=Singleton):

    def __init__(self):
        self.a = 0

    def revise(self):
        while 1:
            self.a = time.time()
            print(self.a)
            time.sleep(3)

one = MyClass()
one.a = 1
two = MyClass()
print(two.a)

print(one is two)
exit(0)

p = threading.Thread(target=one.revise)
p.setDaemon(True)
p.start()
time.sleep(1)
while 1:
    print('=========',MyClass().a)
    time.sleep(1)