#!/usr/bin/env python3

from aiohttp import web, __version__


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)

app = web.Application()
app.add_routes([
    web.get('/', handle),
    web.get('/{name}', handle)
])

if __name__ == '__main__':
    print(f'AIOHTTP {__version__}')
    web.run_app(app, port=8080)
