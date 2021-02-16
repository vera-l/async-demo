import asyncio


def callback(n):
    print('callback {} invoked'.format(n))


async def main():
    loop = asyncio.get_event_loop()
    print('registering callbacks')
    loop.call_soon(callback, 1)
    loop.call_soon(callback, 2)
    loop.call_soon(callback, 3)
    await asyncio.sleep(0.1)

asyncio.run(main())
