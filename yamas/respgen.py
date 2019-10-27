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
from io import BufferedIOBase
from enum import Enum
from typing import Pattern
from yamas.ex import GeneratorError, RequestError, ResponseError


class Method(Enum):
    GET = 'GET'
    HEAD = 'HEAD'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'
    TRACE = 'TRACE'
    PATCH = 'PATCH'
    CONNECT = 'CONNECT'

class Request:
    def __init__(self, path: str, method: Method, headers: dict, body: BufferedIOBase):
        self.path = path
        self.method = method
        self.headers = headers
        self.body = body

    def body_utf8(self) -> str:
        try:
            return self.body.read()
        except Exception as e:
            raise RequestError(e)

    def body_json(self) -> str:
        try:
            return loads(self.body_utf8, object_pairs_hook=OrderedDict)
        except Exception as e:
            raise RequestError(e)

class Response:
    def __init__(self, status: HTTPStatus, headers: dict, body_bytes: bytes):
        self.status = status
        self.headers = headers
        self.body_bytes = body_bytes


class ResponseMaker:
    def __init__(self, status: HTTPStatus, headers: dict, body: any, interpolate: bool):
        self.status = status
        self.interpolate = interpolate
        self.body_bytes = None
        self.template = None
        if body:
            content_type = None
            if isinstance(body, str):
                if interpolate:
                    self.template = body
                else:
                    self.body_bytes = body.encode('utf-8')
            elif isinstance(body, dict):
                if interpolate:
                    self.template = body
                try:
                    json_str = dumps(body)
                    self.body_bytes = json_str.encode('utf-8')
                except Exception:
                    raise ResponseError('Failed to encode dict into JSON')
                content_type = 'application/json'
            elif isinstance(body, bytes):
                self.body_bytes = body
                if interpolate:
                    raise ResponseError('Bytes-type body does not interpolation')
            if content_type:
                if not headers:
                    headers = dict()
                if not headers.get('Content-Type'):
                    headers['Content-Type'] = content_type
        self.headers = headers
        return

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
            formatted_body = ResponseMaker.format_body_template(self.template, groups)
            if isinstance(formatted_body, str):
                body_bytes = formatted_body.encode('utf-8')
            else:
                body_bytes = dumps(formatted_body).encode('utf-8')
        except Exception as e:
            return Response(HTTPStatus.INTERNAL_SERVER_ERROR, {'Content-Type': 'text/plain'}, str(e).encode('utf-8'))
        return Response(self.status, self.headers, body_bytes)


class ResponseGenerator:

    def respond(self, request: Request) -> Response:
        return Response(HTTPStatus.NOT_IMPLEMENTED, {}, None)


class ResponseSelector:
    def __init__(self):
        self.response_makers = []
        self.loop = False
        self.idx = 0

    def add_response(self, response: Response):
        self.response_makers.append(response)
        return

    def select_response(self, groups):
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
                status_code = resp['status'] if 'status' in resp else 200
                try:
                    status = HTTPStatus(status_code)
                except:
                    raise GeneratorError(
                        f'Unrecognized status code {status_code}')
                headers = resp.get('headers')
                body = resp.get('body')
                interpolate = resp.get('interpolate')
                if interpolate is None:
                    interpolate = False
                if not isinstance(interpolate, bool):
                    raise GeneratorError(f'The interpolate field is expected to be boolean')
                self.add_matcher(cpat, method, status, headers, body, interpolate)
        return

    def load_from_json(self, matcher_json: str):
        try:
            matcher_dict = loads(matcher_json, object_pairs_hook=OrderedDict)
        except Exception as e:
            raise GeneratorError(f'Failed to parse JSON: {e}')
        self.load_from_dict(matcher_dict)
        return

    def add_matcher(self, pattern: Pattern, method: Method, status: HTTPStatus, headers: dict, body: any, interopolate: bool):
        respsel_dict = self.matchers.get(pattern)
        if not respsel_dict:
            respsel_dict = {method: ResponseSelector()
                            for method in list(Method)}
            self.matchers[pattern] = respsel_dict
        respsel_dict[method].add_response(ResponseMaker(status, headers, body, interopolate))

    def respond(self, request: Request) -> Response:
        for cpat, respsel_dict in self.matchers.items():
            matches = cpat.fullmatch(request.path)
            if matches:
                respsel = respsel_dict[request.method]
                if respsel:
                    return respsel.select_response(matches.groups())
                else:
                    break
        return Response(HTTPStatus.NOT_FOUND, {}, None)
