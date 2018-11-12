import collections
import functools
import time


class RateLimiter(object):

    def __init__(self, max_calls, period=1.0, callback=None):
        self.calls = collections.deque()
        self.period = period
        self.max_calls = max_calls
        self.callback = callback

    def __call__(self, f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            with self:
                if not self.exceed:
                    return f(*args, **kwargs)
                raise Exception("rate exceed")
        return wrapped

    def __enter__(self):
        # TODO
        pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.calls.append(time.time())
        while self._timespan >= self.period:
            self.calls.popleft()
        # print(id(self.calls), self.calls)

    @property
    def _timespan(self):
        return self.calls[-1] - self.calls[0]

    @property
    def exceed(self):
        start_time = time.time()
        exceed = False
        calls_count = len(self.calls)
        if calls_count > 0:
            if calls_count > self.max_calls:
                print('exceed max call')
                exceed = True
            if start_time - self.calls[-1] <= self.period:
                print('exceed period frequency')
                exceed = True
        print(id(self.calls), self.calls)
        return exceed
