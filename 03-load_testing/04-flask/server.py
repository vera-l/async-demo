#!/usr/bin/env python3

from flask import Flask, __version__
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    print(f'FLASK {__version__}')
    app.run()
