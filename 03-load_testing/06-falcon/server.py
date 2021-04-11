#!/usr/bin/env python3

import falcon


class QuoteResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        quote = {
            'quote': (
                "I've always been more interested in "
                "the future than in the past."
            ),
            'author': 'Grace Hopper'
        }

        resp.media = quote


if __name__ == '__main__':
    print(f'FALCON {falcon.__version__}')
    api = falcon.API()
    api.add_route('/quote', QuoteResource())
