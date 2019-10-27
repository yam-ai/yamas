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
    POST = 'POST'


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
            return loads(self.body_utf8)
        except Exception as e:
            raise RequestError(e)


class Response:
    def __init__(self, status: HTTPStatus, headers: dict, body: any):
        self.status = status
        content = None
        if body:
            body_type = type(body)
            content_type = None
            if body_type is str:
                content = body.encode('utf-8')
                content_type = 'text/plain'
            elif body_type in [dict, OrderedDict]:
                try:
                    content = dumps(body).encode('utf-8')
                except Exception:
                    raise ResponseError('Failed to encode dict into JSON')
                content_type = 'application/json'
            elif body_type is bytes:
                content = body
            if content_type:
                if not headers:
                    headers = dict()
                if not headers.get('Content-Type'):
                    headers['Content-Type'] = content_type
        self.headers = headers
        self.body = content
        return


class ResponseGenerator:

    def respond(self, request: Request) -> Response:
        return Response(HTTPStatus.NOT_IMPLEMENTED, {}, None)


class ResponseSelector:
    def __init__(self):
        self.responses = []
        self.loop = False
        self.idx = 0

    def add_response(self, response: Response):
        self.responses.append(response)
        return

    def select_response(self):
        if not self.responses:
            return None
        num_responses = len(self.responses)
        if self.idx >= num_responses:
            self.idx == 0
        response = self.responses[self.idx]
        self.idx + 1
        if self.loop:
            self.idx = (self.idx + 1) % num_responses
        else:
            self.idx = min(self.idx, num_responses - 1)
        return response


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
                self.add_matcher(cpat, method, status, headers, body)
        return

    def load_from_json(self, matcher_json: str):
        try:
            matcher_dict = loads(matcher_json, object_pairs_hook=OrderedDict)
        except Exception as e:
            raise GeneratorError(f'Failed to parse JSON: {e}')
        self.load_from_dict(matcher_dict)
        return

    def add_matcher(self, pattern: Pattern, method: Method, status: HTTPStatus, headers: dict, body: any):
        respsel_dict = self.matchers.get(pattern)
        if not respsel_dict:
            respsel_dict = {method: ResponseSelector()
                            for method in list(Method)}
            self.matchers[pattern] = respsel_dict
        respsel_dict[method].add_response(Response(status, headers, body))

    def respond(self, request: Request) -> Response:
        for cpat, respsel_dict in self.matchers.items():
            if cpat.fullmatch(request.path):
                respsel = respsel_dict[request.method]
                if respsel:
                    return respsel.select_response()
                else:
                    break
        return Response(HTTPStatus.NOT_FOUND, {}, None)
