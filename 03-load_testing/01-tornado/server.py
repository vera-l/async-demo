#!/usr/bin/env python3

import tornado.ioloop
import tornado.web
import time


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        time.sleep(10)
        self.write('Hello, world')


def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
    ])


if __name__ == '__main__':
    print(f'TORNADO {tornado.version}')
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
