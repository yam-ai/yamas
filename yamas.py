#!/usr/bin/env python3
# coding=utf-8
# Copyright 2019 YAM AI Machinery Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import re
from getopt import getopt, GetoptError
from http.server import HTTPServer, HTTPStatus
from yamas.handler import make_handler_class
from yamas.respgen import Method, ResponseGenerator, PatternResponseGenerator
from yamas.errs import GeneratorError

DEFAULT_IP = '0.0.0.0'
DEFAULT_PORT = 7777


def run(ip: str, port: int, generator: PatternResponseGenerator):
    print(f'HTTP server is starting on {ip}:{port}...')
    server_address = (ip, port)
    PatternRequestHandler = make_handler_class(
        'PatternRequestHandler', generator)
    httpd = HTTPServer(server_address, PatternRequestHandler)
    print('HTTP server is running.')
    httpd.serve_forever()
    return


def halt(progname: str, err: str, exit_code: int = 0):
    print(err, file=sys.stderr)
    print(f'Usage: {progname} [-e | --endpoint server_address:port] -f mock_responses_file',
          file=sys.stderr)
    sys.exit(0)
    return


def load_data(path):
    with open(path, 'r') as f:
        return f.read()


if __name__ == '__main__':
    progname = sys.argv[0]
    try:
        opts, args = getopt(sys.argv[1:], 'e:f:', ['endpoint=', 'file='])
    except GetoptError as err:
        halt(progname, err, 2)
    ip, port = DEFAULT_IP, DEFAULT_PORT
    path = None
    for k, v in opts:
        if k in ('-e', '--endpoint'):
            parts = v.split(':')
            if len(parts) > 0:
                ip = parts[0]
            if len(parts) > 1:
                port = int(parts[1])
        if k in ('-f', '--file'):
            path = v
    if not path:
        halt(progname, 'The matcher file path must be given', 2)
    try:
        matcher_json = load_data(path)
    except:
        halt(progname, f'Failed to read matcher file {path}', 3)
    try:
        generator = PatternResponseGenerator()
        generator.load_from_json(matcher_json)
    except GeneratorError as e:
        halt(progname, f'Invalid data in matcher file {path}: {e}', 4)

    try:
        run(ip, port, generator)
    except OSError as e:
        halt(progname, f'Failed to start server: {e}', 5)
