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
    tasks = [foo(1), foo(3, True), foo(5)]
    # await asyncio.gather(*tasks)
    result = await asyncio.gather(*tasks, return_exceptions=True)
    print('ready!', time.monotonic() - start)
    print(result)

asyncio.run(main())
