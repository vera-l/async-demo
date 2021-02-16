import time
import asyncio


def callback(n, loop):
    print('callback {} invoked at {}'.format(n, loop.time()))


async def main():
    loop = asyncio.get_event_loop()
    now = loop.time()
    print('clock time: {}'.format(time.time()))
    print('loop time: {}'.format(now))
    print('registering callbacks')
    loop.call_at(now + 0.2, callback, 1, loop)
    loop.call_at(now + 0.1, callback, 2, loop)
    loop.call_soon(callback, 3, loop)
    loop.call_at(now + 0.2, callback, 1, loop)
    loop.call_at(now + 0.1, callback, 2, loop)
    loop.call_soon(callback, 3, loop)
    await asyncio.sleep(1)

asyncio.run(main())
