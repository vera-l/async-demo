#!/usr/bin/env python3

from bottle import route, run, template, __version__


@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)


if __name__ == '__main__':
    print(f'BOTTLE {__version__}')
    run(host='localhost', port=8080)

