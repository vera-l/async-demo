#!/usr/bin/env python3

import asyncio
import uvloop
from sanic import Sanic
from sanic.response import json
from signal import signal, SIGINT


PORT = 8080

loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)
app = Sanic('Sanc')


@app.route('/')
async def test(request):
    return json({
        'status': 'OK',
    })

if __name__ == '__main__':
    server_coro = app.create_server(
        host='0.0.0.0',
        port=PORT,
        return_asyncio_server=True,
        debug=True,
        access_log=True,
    )
    task = asyncio.ensure_future(server_coro)
    signal(SIGINT, lambda s, f: loop.stop())
    try:
        loop.run_forever()
    except:
        loop.stop()
