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

from typing import Callable
from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
from yamas.respgen import ResponseGenerator, Response, Request, Method

class MockRequestHandler(BaseHTTPRequestHandler):

    respgen = ResponseGenerator()

    def respond(self, method: Method, path: str, headers: dict):
        request = Request(self.path, method, self.headers, self.rfile)
        response = self.respgen.respond(request)
        if not response:
            self.send_response(HTTPStatus.NOT_FOUND.value)
            self.end_headers()
            return
        status_value = response.status.value
        self.send_response(status_value)
        if response.headers:
            for k, v in response.headers.items():
                self.send_header(k, v)
        self.end_headers()
        if response.body:
            self.wfile.write(response.body)
        return

    def do_GET(self):
        self.respond(Method.GET, self.path, self.headers)
        return

    def do_POST(self):
        self.respond(Method.POST, self.path, self.headers)
        return
