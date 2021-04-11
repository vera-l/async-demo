#!/usr/bin/env python3

from sanic import Sanic, __version__
from sanic.response import json
import time
from pympler import asizeof
import random
import string

app = Sanic("My Hello, world app")


@app.route('/')
async def test(request):
    return json({'status': 'ok'})


@app.route('/cpu_task')
async def test(request):
    n = request.get_args('n')
    time.sleep(2)
    return json({'hello': 'world'})


@app.route('/blocking_io_task')
async def test(request):
    return json({'hello': 'world'})


def memory_leak(str_arg, large_data=[]):
    large_data.append(str_arg)
    return asizeof.asizeof(large_data), len(large_data)


@app.route('/memory_leak')
async def test(request):
    random_string = ''.join(random.choice(string.ascii_lowercase) for i in range(10_000))
    mem, count = memory_leak(random_string)
    return json({
        'status': 'ok',
        'mem': mem,
        'count': count,
    })


if __name__ == '__main__':
    print(f'SANIC {__version__}')
    app.run()
