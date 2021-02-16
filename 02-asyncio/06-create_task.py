import asyncio
import time


async def foo(n):
    await asyncio.sleep(n)
    print(f'n: {n}!')


def got_result(task):
    print(f'got the result! { task.result() }')


async def hello_world():
    start = time.monotonic()
    task = asyncio.create_task(foo(6))
    await task
    task.add_done_callback(got_result)
    print('current time: ', time.monotonic() - start)
    print(task._state)
    await asyncio.sleep(2)
    print('current time: ', time.monotonic() - start)
    await asyncio.sleep(8)
    print('current time: ', time.monotonic() - start)
    print(task._state)


asyncio.run(hello_world())
