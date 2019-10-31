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

import pytest
from io import BytesIO
from http import HTTPStatus
from json import dumps
from yamas.respgen import ResponseMaker, ResponseSelector, \
    PatternResponseGenerator
from yamas.reqresp import Request, Response, Method
from yamas.ex import MockSpecError


mock_dict_valid = {
    '^/users/(\\w+)/todo/(\\d+)$': {
        'GET': {
            'status': 200,
            'content': {
                'user': '{0}',
                'taskid': '{1}',
                'task': 'Buy milk',
                'pri': 'low'
            },
            'contentType': 'json',
            'interpolate': True
        },
        'DELETE': {
            'status': 410
        }
    },
    '^/users/\\w+/todo/?$': {
        'GET': {
            'status': 200,
            'content': ['123', '456', '789'],
            'contentType': 'json'
        },
        'POST': {
            'content': {
                'taskid': '123'
            },
            'contentType': 'json',
            'interpolate': False
        }
    },
    '^/users/(\\w+)/profile.xml$': {
        'GET': {
            'status': 200,
            'headers': {
                'Content-Type': 'application/xml'
            },
            'content': '<profile><user>{0}</user><org>yam.ai</org><grade>premium</grade></profile>',
            'interpolate': True
        },
        'PUT': {
            'status': 409,
            'content': 'object already updated',
            'contentType': 'text'
        }
    },
    '^/users/(\\w+)/profile$': {
        'GET': {
            'status': 200,
            'headers': {
                'Content-Type': ''
            },
            'content': 'Hello {0}',
            'contentType': 'text',
            'interpolate': True
        },
        'POST': {
            'status': 200,
            'headers': {
                'Content-Type': ''
            },
            'content': {'hello': '{0}'},
            'contentType': 'json',
            'interpolate': True
        }
    },
}

prg_valid_json = PatternResponseGenerator()
prg_valid_json.load_from_json(dumps(mock_dict_valid))

prg_valid_dict = PatternResponseGenerator()
prg_valid_dict.load_from_dict(mock_dict_valid)


class TestPatternResponseGenerator:

    tests = [
        (
            {
                'path': '/users/tomlee/todo/123',
                'method': Method.GET,
                'headers': {'a': '1'},
                'content_io': BytesIO(b'Hello World')
            },
            {
                'status': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'content_bytes': dumps({
                    'user': 'tomlee',
                    'taskid': '123',
                    'task': 'Buy milk',
                    'pri': 'low'
                }).encode('utf-8'),
            }
        ),
        (
            {
                'path': '/users/tomlee/todo/123',
                'method': Method.DELETE,
                'headers': {'a': '1'},
                'content_io': BytesIO(b'Hello World')
            },
            {
                'status': 410,
                'headers': {},
                'content_bytes': b'',
            }
        ),
        (
            {
                'path': '/users/tomlee/todo/',
                'method': Method.GET,
                'headers': {'a': '1'},
                'content_io': BytesIO(b'Hello World')
            },
            {
                'status': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'content_bytes': dumps([
                    '123', '456', '789'
                ]).encode('utf-8'),
            }
        ),
        (
            {
                'path': '/users/tomlee/todo/',
                'method': Method.POST,
                'headers': {'a': '1'},
                'content_io': BytesIO(b'Hello World')
            },
            {
                'status': 200,
                'headers': {'Content-Type': 'application/json'},
                'content_bytes': dumps({
                    'taskid': "123"
                }).encode('utf-8'),
            }
        ),
        (
            {
                'path': '/users/tomlee/profile.xml',
                'method': Method.GET,
                'headers': {
                    'Content-Type': 'application/xml'
                },
                'content_io': BytesIO(b'Hello World')
            },
            {
                'status': 200,
                'headers': {'Content-Type': 'application/xml'},
                'content_bytes': b'<profile><user>tomlee</user><org>yam.ai</org><grade>premium</grade></profile>'
            }
        ),
        (
            {
                'path': '/users/tomlee/profile.xml',
                'method': Method.PUT,
                'headers': {
                    'Content-Type': 'xml/plain'
                },
                'content_io': BytesIO(b'Hello World')
            },
            {
                'status': 409,
                'headers': {'Content-Type': 'text/plain'},
                'content_bytes': b'object already updated'
            }
        ),
        (
            {
                'path': '/users/tomlee/todo/abc',
                'method': Method.GET,
                'headers': {},
                'content_io': BytesIO(b'Hello World')
            },
            {
                'status': 404,
                'headers': {},
                'content_bytes': b''
            }
        ),
        (
            {
                'path': '/users/tomlee/todo/123',
                'method': Method.POST,
                'headers': {},
                'content_io': BytesIO(b'Hello World')
            },
            {
                'status': 404,
                'headers': {},
                'content_bytes': b''
            }
        ),
        (
            {
                'path': '/users/tomlee/profile',
                'method': Method.GET,
                'content_io': BytesIO(b'Hello World')
            },
            {
                'status': 200,
                'headers': {},
                'content_bytes': b'Hello tomlee'
            }
        ),
        (
            {
                'path': '/users/tomlee/profile',
                'method': Method.POST,
                'content_io': BytesIO(b'Hello World')
            },
            {
                'status': 200,
                'headers': {},
                'content_bytes': dumps({'hello': 'tomlee'}).encode('utf-8')
            }
        )
    ]

    @pytest.mark.parametrize('req, resp', tests)
    def test_valid_mock_json(self, req, resp):
        actual_resp = prg_valid_json.respond(
            Request(
                req.get('path'),
                req.get('method'),
                req.get('headers'),
                req.get('content_io')
            )
        )
        assert actual_resp.status == resp['status']
        assert actual_resp.headers == resp['headers']
        assert actual_resp.content_bytes == resp['content_bytes']
