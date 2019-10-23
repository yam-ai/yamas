# coding=utf-8

import os
import sys
from getopt import getopt, GetoptError
from http.server import HTTPServer
from httpmock.mock import MockRequestHandler

DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 8000


def run(ip: str, port: int):
    print(f'HTTP server is starting on {ip}:{port}...')
    server_address = (ip, port)
    httpd = HTTPServer(server_address, MockRequestHandler)
    print('HTTP server is running.')
    httpd.serve_forever()
    return


def usage(progname: str, err: Exception):
    print(err)
    print(f'Usage: {progname} [-e | --endpoint server_address:port]',
          file=sys.stderr)
    return


if __name__ == '__main__':
    try:
        opts, args = getopt(sys.argv[1:], 'e:', ['endpoint='])
    except GetoptError as err:
        usage(sys.argv[0], err)
        sys.exit(2)
    ip, port = DEFAULT_IP, DEFAULT_PORT
    for k, v in opts:
        if k in ('-e', '--endpoint'):
            parts = v.split(':')
            if len(parts) > 0:
                ip = parts[0]
            if len(parts) > 1:
                port = int(parts[1])
    try:
        run(ip, port)
    except OSError as e:
        print(f'Failed to start server: {e}')
