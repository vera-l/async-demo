import asyncio
import time


async def foo(n, with_exception=False):
    await asyncio.sleep(n)
    if with_exception:
        raise Exception
    print(f'n: {n}!')


async def main():
    start = time.monotonic()
    print('start!')
    try:
        await asyncio.wait_for(foo(10), timeout=5)
    except asyncio.TimeoutError:
        print('timeout!')
    print('ready!', time.monotonic() - start)

asyncio.run(main())
