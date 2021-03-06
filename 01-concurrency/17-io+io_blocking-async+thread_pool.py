import os
import asyncio
import time
import concurrent.futures

from tasks import get_url_non_blocking, get_url_blocking, URLS

URLS = URLS[:20]
pool = concurrent.futures.ThreadPoolExecutor(max_workers=min(32, os.cpu_count() + 4))


async def get_url_non_blocking_plus_cpu_or_blocking(url):
    loop = asyncio.get_event_loop()
    await get_url_non_blocking(url)
    await loop.run_in_executor(pool, get_url_blocking, url)


async def main():
    await asyncio.gather(*[get_url_non_blocking_plus_cpu_or_blocking(url) for url in URLS])

start = time.time()
asyncio.run(main())
print(time.time() - start, 'sec, for ', len(URLS), ' items')
