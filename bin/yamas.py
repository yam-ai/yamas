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
from getopt import getopt, GetoptError
from http.server import HTTPServer, HTTPStatus
from yamas.server import Yamas
from yamas.ex import YamasException

DEFAULT_IP = '0.0.0.0'
DEFAULT_PORT = 7777

def halt(progname: str, err: str, exit_code: int = 0):
    print(err, file=sys.stderr)
    print(f'Usage: {progname} [-e|--endpoint server_address:port] -f|--file mock_responses_file',
          file=sys.stderr)
    sys.exit(0)
    return


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
        halt(progname, 'The mock responses file path must be given', 2)

    try:
        server = Yamas()
        server.load_data(path)
        print(f'Loaded mock data file: {path}')
        print(f'Starting server on {ip}:{port}')
        server.run(ip, port)
    except YamasException as e:
        halt(progname, e, 3)
