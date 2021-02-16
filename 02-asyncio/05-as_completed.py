import asyncio


async def foo(n):
    print(f'{n} will sleep for: {n} seconds')
    await asyncio.sleep(n)
    return f'ready {n}!'


async def main():
    tasks = [foo(2), foo(5), foo(3), foo(4), foo(1), foo(7)]

    for future in asyncio.as_completed(tasks):
        result = await future
        print(f'result: {result}')


asyncio.run(main())
