import asyncio
import time


async def foo(n):
    await asyncio.sleep(n)
    print(f'n: {n}!')


async def main():
    start = time.monotonic()
    print('start!')
    await foo(1)
    await foo(3)
    await foo(5)
    print('ready!', time.monotonic() - start)

asyncio.run(main())
