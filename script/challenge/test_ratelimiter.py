import time
from script.challenge.ratelimit import RateLimiter

def callback(value):
    """value 表示还需要等待多久才能下次执行"""
    pass

# 可以用作 decorator
@RateLimiter(max_calls=10, period=1, callback=callback)
def func1():
    print("func1...\n")
    pass

def func2():
    print("func2...\n")
    pass

if __name__ == '__main__':
    func1()
    # 可以用作上下文管理器
    with RateLimiter(max_calls=10, period=1, callback=callback) as r:
        while 1:
            time.sleep(0.1)
            if not r.exceed:
                func2()