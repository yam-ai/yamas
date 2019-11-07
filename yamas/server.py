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
from yamas.ex import MockSpecError, ServerError
from yamas.config import VERSION, SERVER_NAME


class Yamas:

    @staticmethod
    def make_handler_class(name: str, respgen: ResponseGenerator) -> Callable:
        handler_class = type(name, (MockRequestHandler,), {'respgen': respgen})
        if respgen.server_header:
            handler_class.server_version = ''
            handler_class.sys_version = respgen.server_header
        else:
            handler_class.server_version = SERVER_NAME
            handler_class.sys_version = VERSION
        return handler_class

    def __init__(self):
        self.respgen = PatternResponseGenerator()
        self.server_header = None
        return

    def load_file(self, spec_file: str):
        with open(spec_file, 'r') as f:
            spec_json = f.read()
        self.load_json(spec_json)
        return

    def load_json(self, spec_json: str):
        self.respgen.load_spec_json(spec_json)

    def load_dict(self, spec_dict: dict):
        self.respgen.load_spec_dict(spec_dict)
        self.server_header = self.respgen.server_header
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
