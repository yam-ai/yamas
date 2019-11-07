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
from copy import copy, deepcopy
from jsonschema import validate
from string import Template

spec_schema = {
    'title': 'Yamas Specification',
    'description': 'Specification on mock response data for Yamas',
    'type': 'object',
    'properties': {
        'global': {
            'description': 'Global parameters',
            'type': 'object',
            'properties': {
                'headers': {
                    'description': 'Default HTTP headers',
                    'type': 'object',
                    'propertyNames': {
                        'description': 'HTTP header name',
                        'pattern': '^.+$'
                    },
                    'patternProperties': {
                        '^.+$': {
                            'description': 'HTTP header value',
                            'type': 'string'
                        }
                    },
                    'additionalProperties': False
                },
                'serverHeader': {
                    'description': 'Server header',
                    'type': 'string',
                    'minLength': 1
                }
            }
        },
        'rules': {
            'description': 'Rules of URL path patterns',
            'type': 'object',
            'propertyNames': {
                'pattern': '^.+$'
            },
            'patternProperties': {
                '^.+$': {
                    'description': 'Mock response per HTTP method',
                    'type': 'object',
                    'propertyNames': {
                        'description': 'HTTP method',
                        'enum': [x.value for x in list(Method)]
                    },
                    'patternProperties': {
                        '[A-Z]+': {
                            'description': 'Mock response',
                            'type': 'object',
                            'properties': {
                                'status': {
                                    'description': 'HTTP response status code',
                                    'type': 'integer',
                                    'minimum': 100,
                                    'maximum': 599
                                },
                                'headers': {
                                    'description': 'HTTP response headers',
                                    'type': 'object',
                                    'propertyNames': {
                                        'description': 'HTTP header name',
                                        'pattern': '^.+$'
                                    },
                                    'patternProperties': {
                                        '^.+$': {
                                            'description': 'HTTP header value',
                                            'type': 'string'
                                        }
                                    },
                                    'additionalProperties': False
                                },
                                'interpolate': {
                                    'description': 'Whether interpolation is applied',
                                    'type': 'boolean'
                                },
                                'content': {
                                    'description': 'String or JSON response content'
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    'additionalProperties': False
}


def check_headers(headers: dict):
    if headers.get('Server'):
        raise MockSpecError(
            f'Server header should only be given as a global field')


class ResponseMaker:
    def __init__(self, status: HTTPStatus, headers: dict, content: any, content_type: ContentType, interpolate: bool, global_headers: dict):
        self.status = status
        self.content_type = content_type
        self.headers = copy(
            global_headers) if global_headers is not None else OrderedDict()
        check_headers(self.headers)
        if headers:
            for h in headers:
                self.headers[h] = headers[h]
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
            kv = dict()
            for i, v in enumerate(vars):
                kv[f'p_{i}'] = v
            return Template(template_item).substitute(kv)
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
        self.rules = OrderedDict()
        self.global_headers = OrderedDict()
        self.server_header = None
        return

    def load_spec_json(self, spec_json: str):
        try:
            spec_dict = loads(spec_json, object_pairs_hook=OrderedDict)
            self.load_spec_dict(spec_dict)
        except Exception as e:
            raise MockSpecError(f'Failed to parse JSON: {e}')
        return

    def load_spec_dict(self, spec_dict: dict):
        validate(instance=spec_dict, schema=spec_schema)
        global_dict = spec_dict.get('global')
        if global_dict:
            global_headers = global_dict.get('headers')
            if global_headers:
                check_headers(global_headers)
                for header in global_headers:
                    self.global_headers[header] = global_headers[header]
            self.server_header = global_dict.get('serverHeader')
            if self.server_header is not None and not isinstance(self.server_header, str):
                raise MockSpecError(f'Server header must be a string if given')
        rule_dict = spec_dict.get('rules')
        if rule_dict:
            self.load_rule_dict(rule_dict)

    def load_rule_dict(self, rule_dict: OrderedDict):
        for pat, resps in rule_dict.items():
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
                self.add_rule(cpat, method, mock_response)
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

    def add_rule(self, pattern: Pattern, method: Method,
                 mock_response: MockResponse):
        respsel_dict = self.rules.get(pattern)
        if not respsel_dict:
            respsel_dict = {method: ResponseSelector(loop=False)
                            for method in list(Method)}
            self.rules[pattern] = respsel_dict
        respsel_dict[method].add_response_maker(
            ResponseMaker(mock_response.status, mock_response.headers,
                          mock_response.content, mock_response.content_type,
                          mock_response.interpolate, self.global_headers))

    def respond(self, request: Request) -> Response:
        for cpat, respsel_dict in self.rules.items():
            match = cpat.fullmatch(request.path)
            if match:
                respsel = respsel_dict.get(request.method)
                if respsel:
                    resp = respsel.make_response(match.groups())
                    return resp
                else:
                    break
        return Response(HTTPStatus.NOT_FOUND, {}, b'')
