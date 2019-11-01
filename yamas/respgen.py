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
from yamas.reqresp import Request, Response, Method, ContentType
from yamas.ex import MockSpecError, RequestError, ResponseError


class ResponseMaker:
    def __init__(self, status: HTTPStatus, headers: dict, content: any, content_type: ContentType, interpolate: bool):
        self.status = status
        self.content_type = content_type
        self.headers = headers
        self.headers = headers if headers is not None else dict()
        self.content_bytes = None
        self.template = None
        self.interpolate = interpolate

        if self.content_type is ContentType.JSON:
            self.make_content_dict(content)
        elif content is None or isinstance(content, str):
            self.make_content_str(content, content_type)
        elif content is not None:
            raise MockSpecError(
                f'Content "{dumps(content)}" is not a string but its type is text or not given')
        self.process_headers()
        return

    def process_headers(self):
        headers_to_delete = []
        for k, v in self.headers.items():
            if v is None or v == '':
                headers_to_delete.append(k)
            elif not isinstance(v, str):
                raise MockSpecError(
                    f'The value for the header {k} must be a string')
        for k in headers_to_delete:
            del self.headers[k]
        return

    def make_content_str(self, content: str, content_type: ContentType):
        if content is None:
            content = ''
        if content == '':
            self.interpolate = False
        elif not isinstance('content', str):
            raise MockSpecError('Text content must be given as a string.')
        if self.interpolate:
            self.template = content
        else:
            self.content_bytes = content.encode('utf-8')
        content_type_header = self.headers.get('Content-Type')
        if content_type is ContentType.TEXT and content_type_header is None:
            self.headers['Content-Type'] = 'text/plain'
        return

    def make_content_dict(self, content: dict):
        if not content:
            self.interpolate = False
            self.content_bytes = b''
        if self.interpolate:
            self.template = content
        else:
            try:
                json_str = dumps(content)
                self.content_bytes = json_str.encode('utf-8')
            except Exception as e:
                raise MockSpecError(f'Failed to encode dict into JSON {e}')
        content_type_header = self.headers.get('Content-Type')
        if content_type_header is None:
            self.headers['Content-Type'] = 'application/json'
        return

    @staticmethod
    def format_content_template(template_item: any, vars: tuple) -> any:
        if isinstance(template_item, str):
            return template_item.format(*vars)
        if isinstance(template_item, dict):
            content_dict = OrderedDict()
            for k, v in template_item.items():
                content_dict[k] = ResponseMaker.format_content_template(
                    v, vars)
            return content_dict
        if isinstance(template_item, list):
            content_list = []
            for v in content_list:
                content_list.append(
                    ResponseMaker.format_content_template(v, vars))
            return content_list
        return template_item

    def make_response(self, groups: tuple) -> Response:
        if not self.interpolate:
            return Response(self.status, self.headers, self.content_bytes)
        try:
            formatted_content = ResponseMaker.format_content_template(
                self.template, groups)
            if self.content_type is ContentType.JSON:
                content_bytes = dumps(formatted_content).encode('utf-8')
            else:
                content_bytes = formatted_content.encode('utf-8')
        except Exception as e:
            return Response(HTTPStatus.INTERNAL_SERVER_ERROR,
                            {'Content-Type': 'text/plain'},
                            str(e).encode('utf-8'))
        return Response(self.status, self.headers, content_bytes)


class ResponseGenerator:

    def respond(self, request: Request) -> Response:
        return Response(HTTPStatus.NOT_IMPLEMENTED, {}, b'')


class ResponseSelector:
    def __init__(self, loop):
        self.response_makers = []
        self.loop = loop
        self.idx = 0

    def add_response_maker(self, response_maker: ResponseMaker):
        self.response_makers.append(response_maker)
        return

    def make_response(self, groups):
        if not self.response_makers:
            return Response(HTTPStatus.NOT_FOUND, {}, b'')
        num_response_makers = len(self.response_makers)
        if self.idx >= num_response_makers:
            self.idx == 0
        response_maker = self.response_makers[self.idx]
        if self.loop:
            self.idx = (self.idx + 1) % num_response_makers
        else:
            self.idx = min(self.idx + 1, num_response_makers - 1)
        return response_maker.make_response(groups)


class MockResponse:
    def __init__(self, status: HTTPStatus, headers: dict, content: any, content_type: ContentType, interpolate: bool):
        self.status = status
        self.headers = headers
        self.content = content
        self.content_type = content_type
        self.interpolate = interpolate


class PatternResponseGenerator(ResponseGenerator):

    def __init__(self):
        self.matchers = OrderedDict()
        return

    def load_dict(self, matcher_dict: OrderedDict):
        for pat, resps in matcher_dict.items():
            try:
                cpat = re.compile(pat)
            except:
                raise MockSpecError(f'Failed to compile pattern {pat}')
            for method in list(Method):
                resp = resps.get(method.value)
                if not resp:
                    continue
                try:
                    mock_response = PatternResponseGenerator.parse_mock_response(
                        resp)
                except MockSpecError as e:
                    raise MockSpecError(
                        f'Error parsing mock responses for pattern {pat} and {method.value}: {e}')
                self.add_matcher(cpat, method, mock_response)
        return

    @staticmethod
    def parse_mock_response(resp: dict) -> MockResponse:
        status_code = resp['status'] if 'status' in resp else 200
        try:
            status = HTTPStatus(status_code)
        except:
            raise MockSpecError(f'Unrecognized status code {status_code}')
        headers = resp.get('headers')
        content = resp.get('content')
        interpolate = resp.get('interpolate')
        content_type_str = resp.get('contentType')
        if content_type_str:
            try:
                content_type = ContentType(content_type_str)
            except Exception:
                raise MockSpecError(
                    f'Unsupported contenntType {content_type_str}')
        else:
            content_type = None
        if interpolate is None:
            interpolate = False
        elif not isinstance(interpolate, bool):
            raise MockSpecError(
                f'The interpolate field must be boolean')
        return MockResponse(status, headers, content,
                            content_type, interpolate)

    def load_json(self, matcher_json: str):
        try:
            matcher_dict = loads(matcher_json, object_pairs_hook=OrderedDict)
        except Exception as e:
            raise MockSpecError(f'Failed to parse JSON: {e}')
        self.load_dict(matcher_dict)
        return

    def add_matcher(self, pattern: Pattern, method: Method,
                    mock_response: MockResponse):
        respsel_dict = self.matchers.get(pattern)
        if not respsel_dict:
            respsel_dict = {method: ResponseSelector(loop=False)
                            for method in list(Method)}
            self.matchers[pattern] = respsel_dict
        respsel_dict[method].add_response_maker(
            ResponseMaker(mock_response.status, mock_response.headers,
                          mock_response.content, mock_response.content_type, mock_response.interpolate))

    def respond(self, request: Request) -> Response:
        for cpat, respsel_dict in self.matchers.items():
            match = cpat.fullmatch(request.path)
            if match:
                respsel = respsel_dict.get(request.method)
                if respsel:
                    resp = respsel.make_response(match.groups())
                    return resp
                else:
                    break
        return Response(HTTPStatus.NOT_FOUND, {}, b'')
