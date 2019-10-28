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

import re
from collections import OrderedDict
from json import loads, dumps
from http import HTTPStatus
from typing import Pattern
from yamas.reqresp import Request, Response, Method
from yamas.ex import GeneratorError, RequestError, ResponseError


class ResponseMaker:
    def __init__(self, status: HTTPStatus, headers: dict, body: any, interpolate: bool):
        self.status = status
        self.interpolate = interpolate
        self.headers = headers
        self.body_bytes = None
        self.template = None
        if not body:
            if self.interpolate:
                self.template = ''
            else:
                self.body_types = b''
        elif isinstance(body, str):
            self.make_body_str(body)
        elif isinstance(body, dict):
            self.make_body_dict(body)
            if not headers:
                headers = dict()
            if not headers.get('Content-Type'):
                headers['Content-Type'] = 'application/json'
        elif isinstance(body, bytes):
            self.make_body_bytes(body)
        return

    def make_body_str(self, body: str):
        if self.interpolate:
            self.template = body
        else:
            self.body_bytes = body.encode('utf-8')

    def make_body_dict(self, body: dict):
        if self.interpolate:
            self.template = body
        else:
            try:
                json_str = dumps(body)
                self.body_bytes = json_str.encode('utf-8')
            except Exception:
                raise ResponseError('Failed to encode dict into JSON')

    def make_body_bytes(self, body: bytes):
        if interpolate:
            raise ResponseError('Bytes-type body does not interpolation')
        self.body_bytes = body

    @staticmethod
    def format_body_template(template_item: any, vars: tuple) -> any:
        if isinstance(template_item, str):
            return template_item.format(*vars)
        if isinstance(template_item, dict):
            body_dict = OrderedDict()
            for k, v in template_item.items():
                body_dict[k] = ResponseMaker.format_body_template(v, vars)
            return body_dict
        if isinstance(template_item, list):
            body_list = []
            for v in body_list:
                body_list.append(ResponseMaker.format_body_template(v, vars))
            return body_list
        return template_item

    def make_response(self, groups: tuple) -> Response:
        if not self.interpolate:
            return Response(self.status, self.headers, self.body_bytes)
        try:
            formatted_body = ResponseMaker.format_body_template(
                self.template, groups)
            if isinstance(formatted_body, str):
                body_bytes = formatted_body.encode('utf-8')
            else:
                body_bytes = dumps(formatted_body).encode('utf-8')
        except Exception as e:
            return Response(HTTPStatus.INTERNAL_SERVER_ERROR, {'Content-Type': 'text/plain'}, str(e).encode('utf-8'))
        return Response(self.status, self.headers, body_bytes)


class ResponseGenerator:

    def respond(self, request: Request) -> Response:
        return Response(HTTPStatus.NOT_IMPLEMENTED, {}, b'')


class ResponseSelector:
    def __init__(self, loop=False):
        self.response_makers = []
        self.loop = loop
        self.idx = 0

    def add_response_maker(self, response_maker: ResponseMaker):
        self.response_makers.append(response_maker)
        return

    def select_response_maker(self, groups):
        if not self.response_makers:
            return None
        num_response_makers = len(self.response_makers)
        if self.idx >= num_response_makers:
            self.idx == 0
        response_maker = self.response_makers[self.idx]
        self.idx + 1
        if self.loop:
            self.idx = (self.idx + 1) % num_response_makers
        else:
            self.idx = min(self.idx, num_response_makers - 1)
        return response_maker.make_response(groups)


class PatternResponseGenerator(ResponseGenerator):

    class MockResponse:
        def __init__(self, status: HTTPStatus, headers: dict, body: any, interpolate: bool):
            self.status = status
            self.headers = headers
            self.body = body
            self.interpolate = interpolate

    def __init__(self):
        self.matchers = OrderedDict()
        return

    def load_from_dict(self, matcher_dict: OrderedDict):
        for pat, resps in matcher_dict.items():
            try:
                cpat = re.compile(pat)
            except:
                raise GeneratorError(f'Failed to compile pattern {pat}')
            for method in list(Method):
                resp = resps.get(method.value)
                if not resp:
                    continue
                mock_response = PatternResponseGenerator.parse_mock_response(
                    resp)
                self.add_matcher(cpat, method, mock_response)
        return

    @classmethod
    def parse_mock_response(cls, resp: dict) -> MockResponse:
        status_code = resp['status'] if 'status' in resp else 200
        try:
            status = HTTPStatus(status_code)
        except:
            raise GeneratorError(f'Unrecognized status code {status_code}')
        headers = resp.get('headers')
        body = resp.get('body')
        interpolate = resp.get('interpolate')
        if interpolate is None:
            interpolate = False
        elif not isinstance(interpolate, bool):
            raise GeneratorError(
                f'The interpolate field must be boolean')
        return cls.MockResponse(status, headers, body, interpolate)

    def load_from_json(self, matcher_json: str):
        try:
            matcher_dict = loads(matcher_json, object_pairs_hook=OrderedDict)
        except Exception as e:
            raise GeneratorError(f'Failed to parse JSON: {e}')
        self.load_from_dict(matcher_dict)
        return

    def add_matcher(self, pattern: Pattern, method: Method,
                    mock_response: MockResponse):
        respsel_dict = self.matchers.get(pattern)
        if not respsel_dict:
            respsel_dict = {method: ResponseSelector()
                            for method in list(Method)}
            self.matchers[pattern] = respsel_dict
        respsel_dict[method].add_response_maker(
            ResponseMaker(mock_response.status, mock_response.headers,
                          mock_response.body, mock_response.interpolate))

    def respond(self, request: Request) -> Response:
        for cpat, respsel_dict in self.matchers.items():
            match = cpat.fullmatch(request.path)
            if match:
                respsel = respsel_dict[request.method]
                if respsel:
                    return respsel.select_response_maker(match.groups())
                else:
                    break
        return Response(HTTPStatus.NOT_FOUND, {}, None)
