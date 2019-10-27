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

from http.server import HTTPServer, HTTPStatus
from typing import Callable
from yamas.respgen import Method, ResponseGenerator, PatternResponseGenerator
from yamas.handler import MockRequestHandler
from yamas.ex import GeneratorError, ServerError

SERVER_HEADER = 'yamas'

class Yamas:

    @staticmethod
    def make_handler_class(name: str, respgen: ResponseGenerator) -> Callable:
        handler_class = type(name, (MockRequestHandler,), {'respgen': respgen})
        handler_class.server_version = SERVER_HEADER
        handler_class.sys_version = '0.1'
        return handler_class

    def __init__(self):
        self.respgen = PatternResponseGenerator()
        return

    def load_data(self, mock_file: str):
        try:
            with open(mock_file, 'r') as f:
                mock_data = f.read()
            self.respgen.load_from_json(mock_data)
        except Exception as e:
            raise ServerError(e)
        return


    def run(self, ip: str, port: int):
        server_address = (ip, port)
        PatternRequestHandler = self.make_handler_class(
            'PatternRequestHandler', self.respgen)
        try:
            httpd = HTTPServer(server_address, PatternRequestHandler)
            httpd.serve_forever()
        except Exception as e:
            raise ServerError(e)
        return

