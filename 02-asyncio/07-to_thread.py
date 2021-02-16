import asyncio
import time

N = 5


def blocking_io(n):
    print(n, ' start sync')
    time.sleep(n)
    print(n, ' ready sync')


async def foo(n):
    print(n, ' start Async')
    await asyncio.sleep(n)
    print(n, ' ready Async')
    # blocking_io(n)
    await asyncio.to_thread(blocking_io, n)


async def main():
    await asyncio.gather(*[foo(n) for n in range(N)])

start = time.monotonic()
asyncio.run(main())
print(time.monotonic() - start, 'sec, for ', N, ' items')
