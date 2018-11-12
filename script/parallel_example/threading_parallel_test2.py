import logging, threading
from queue import Queue

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

shared_queue = Queue()
queue_condition = threading.Condition()
queue_lock = threading.Lock()


def print_task(condition):
    with condition:
        while True:
            if shared_queue.empty():
                logger.info("[%s] - waiting for elements in queue.." % threading.current_thread().name)
                condition.wait()
            else:
                value = shared_queue.get()
                if value > 100:
                    break
                logger.debug("[%s] print [%d]" % (threading.current_thread().name, value))

def print_task_by_lock():
    while True:
        with queue_lock:
            if shared_queue.empty():
                logger.info("[%s] - waiting for elements in queue.." % threading.current_thread().name)
            else:
                value = shared_queue.get()
                if value > 100:
                    break
                logger.debug("[%s] print [%d]" % (threading.current_thread().name, value))

def put(condition):
    with condition:
        for i in range(1, 200):
            shared_queue.put(i)
            logger.debug("put element [%d] into queue.." % i)
            condition.notifyAll()

def put_by_lock():
    with queue_lock:
        for i in range(1, 200):
            shared_queue.put(i)
            logger.debug("put element [%d] into queue.." % i)

# producer = threading.Thread(daemon=True, target=put, args=(queue_condition,))
producer = threading.Thread(daemon=True, target=put_by_lock, args=())
producer.start()

# consumers = [threading.Thread(daemon=True, target=print_task, args=(queue_condition,)) for i in range(4)]
consumers = [threading.Thread(daemon=True, target=print_task_by_lock, args=()) for i in range(4)]
[consumer.start() for consumer in consumers]

[consumer.join() for consumer in consumers]