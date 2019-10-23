# coding=utf-8

from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys
from getopt import getopt, GetoptError

DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 8000


class HTTPMock(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.wfile.write('GET {}'.format(self.path).encode())
        return

    def do_POST(self):
        self.send_response(200)
        self.wfile.write('POST {}'.format(self.path).encode())
        return


def run(ip, port):
    print('HTTP server is starting on {}:{}...'.format(ip, port))
    server_address = (ip, port)
    httpd = HTTPServer(server_address, HTTPMock)
    print('HTTP server is running.')
    httpd.serve_forever()


def usage(progname, err):
    print(err)
    print(
        'Usage: {} [-e | --endpoint server_address:port]'.format(progname), file=sys.stderr)


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
        print('Failed to start server: {}'.format(e))
