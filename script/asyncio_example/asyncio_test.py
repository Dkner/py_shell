import asyncio
import time

now = lambda: time.time()

async def do_some_work(x):
    print('Waiting: ', x)
    await asyncio.sleep(x)

start = now()
tasks, coroutines = [], []

[coroutines.append(do_some_work(i)) for i in range(1, 5)]
loop = asyncio.get_event_loop()
# task = asyncio.ensure_future(coroutine)
[tasks.append(loop.create_task(coroutine)) for coroutine in coroutines]
print(tasks)
[loop.run_until_complete(task) for task in tasks]
print('TIME: ', now() - start)