# coding=utf-8
from collections import defaultdict
from multiprocessing import Queue, Process, current_process, cpu_count
import random


def getter(name, queue, fibo_dict):
    print('Son process %s' % name)
    while True:
        try:
            value = queue.get(True, 3)
            a, b = 0, 1
            for item in range(value):
                a, b = b, a + b
            fibo_dict[value] = a
            print("consumer [%s] getting value [%d] from queue..." % (current_process().name, value))
        except Exception as e:
            print(e)
            break


def putter(name, queue):
    print("Son process %s" % name)
    for i in range(0, 50):
        value = random.randint(1, 15)
        queue.put(value)
        print("Process putter put: %f" % value)


if __name__ == '__main__':
    queue = Queue()
    fibo_dict = defaultdict(list)
    producer = Process(target=putter, args=("Putter", queue))
    producer.start()
    producer.join()

    consumers = []
    cpu = cpu_count()
    print(cpu)
    consumers = [Process(target=getter, args=("Getter", queue, fibo_dict)) for i in range(cpu)]
    [consumer.start() for consumer in consumers]
    [consumer.join() for consumer in consumers]