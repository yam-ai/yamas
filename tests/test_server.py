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
from unittest.mock import patch, mock_open
from yamas.server import Yamas
from yamas.ex import MockSpecError
from threading import Thread
from json import loads
import requests
from yamas.config import SERVER_NAME, VERSION
import logging
LOGGER = logging.getLogger(__name__)

VALID_JSON = '''
{
    "global": {
        "headers": {
                "Access-Control-Allow-Origin": "*"
        },
        "serverHeader": "YetAnotherMockAPIServer 0.0.1"
    },
    "rules": {
        "^/users/(\\\\w+)/todo/(\\\\d+)$": {
            "GET": {
                "status": 200,
                "content": {
                    "user": "$p0",
                    "taskid": "$p1",
                    "task": "Buy milk",
                    "pri": "low"
                },
                "contentType": "json",
                "interpolate": true
            },
            "DELETE": {
                "status": 410
            }
        },
        "^/users/\\\\w+/todo/?": {
            "GET": {
                "status": 200,
                "content": [
                    "123",
                    "456",
                    "789"
                ],
                "contentType": "json"
            },
            "POST": {
                "content": {
                    "taskid": "123"
                },
                "contentType": "json",
                "interpolate": false
            }
        },
        "^/users/(\\\\w+)/profile.xml$": {
            "GET": {
                "status": 200,
                "headers": {
                    "Content-Type": "application/xml"
                },
                "content": "<profile><user>$p0</user><org>yam.ai</org><grade>premium</grade></profile>",
                "contentType": "text",
                "interpolate": true
            },
            "PUT": {
                "status": 409,
                "content": "object already updated",
                "contentType": "text"
            }
        },
        "^/users/(\\\\w+)/profile$": {
            "GET": {
                "status": 200,
                "headers": {
                    "Content-Type": ""
                },
                "content": "Hello $p0",
                "contentType": "text",
                "interpolate": true
            },
            "POST": {
                "status": 200,
                "headers": {
                    "Content-Type": ""
                },
                "content": {"hello": "$p0"},
                "contentType": "json",
                "interpolate": true
            }
        }
    }
}
'''

INVALID_JSON = 'this is not a json'

HELLO_JSON = '''
{ 
    "global": {
        "headers": {
            "Access-Control-Allow-Origin": "*"
        }
    },
    "rules": {
        "^/hello/(\\\\w+)$": {
            "GET": {
                "status": 201,
                "headers": { "X-Hello": "World" },
                "contentType": "text",
                "content": "Hello, $p0",
                "interpolate": true
            }
        }
    }
}
'''

HOST = 'localhost'
PORT = 7777
PORT2 = 6666


@pytest.fixture(scope='session', autouse=True)
def yamas():
    server = Yamas()
    server.load_json(VALID_JSON)
    thread = Thread(target=server.run, args=(HOST, PORT))
    thread.daemon = True
    thread.start()
    return server


class TestYamas:

    @patch('builtins.open', new_callable=mock_open, read_data=HELLO_JSON)
    def test_hello_world(self, mock_file):
        mock_spec = '/some/mock/response/json'
        server = Yamas()
        server.load_file(mock_spec)
        mock_file.assert_called_with(mock_spec, 'r')
        thread = Thread(target=server.run, args=(HOST, PORT2))
        thread.daemon = True
        thread.start()
        response = requests.get(
            f'http://{HOST}:{PORT2}/hello/world', headers={}, data={})
        del response.headers['Date']
        assert response.headers == {
            'Server': f'{SERVER_NAME} {VERSION}',
            'X-Hello': 'World',
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'text/plain'
        }
        assert response.status_code == 201
        assert response.content == b'Hello, world'

    @patch('builtins.open', new_callable=mock_open, read_data=VALID_JSON)
    def test_load_file(self, mock_file):
        mock_spec = '/some/mock/response/json'
        server = Yamas()
        server.load_file(mock_spec)
        mock_file.assert_called_with(mock_spec, 'r')

    @patch('builtins.open', new_callable=mock_open, read_data=INVALID_JSON)
    def test_loading_invalid_mock(self, mock_file):
        mock_spec = '/some/mock/response/json'
        server = Yamas()
        with pytest.raises(MockSpecError):
            server.load_file(mock_spec)
        mock_file.assert_called_with(mock_spec, 'r')

    reqresps = [
        (
            {
                'path': '/users/tomlee/todo/123',
                'request': requests.get,
                'headers': {'a': '1'},
                'data': 'Hello World'
            },
            {
                'status': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'data': {
                    'user': 'tomlee',
                    'taskid': '123',
                    'task': 'Buy milk',
                    'pri': 'low'
                },
            }
        ),
        (
            {
                'path': '/users/tomlee/todo/123',
                'request': requests.delete,
                'headers': {'a': '1'},
                'data': 'Hello World'
            },
            {
                'status': 410,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                },
                'data': ''
            }
        ),
        (
            {
                'path': '/users/tomlee/todo/',
                'request': requests.get,
                'headers': {'a': '1'},
                'data': 'Hello World'
            },
            {
                'status': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'data': [
                    '123', '456', '789'
                ]
            }
        ),
        (
            {
                'path': '/users/tomlee/todo/',
                'request': requests.post,
                'headers': {'a': '1'},
                'data': 'Hello World'
            },
            {
                'status': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'data': {'taskid': "123"}
            }
        ),
        (
            {
                'path': '/users/tomlee/profile.xml',
                'request': requests.get,
                'headers': {
                    'Content-Type': 'application/xml'
                },
                'data': 'Hello World'
            },
            {
                'status': 200,
                'headers': {
                    'Content-Type': 'application/xml',
                    'Access-Control-Allow-Origin': '*',
                },
                'data': '<profile><user>tomlee</user><org>yam.ai</org><grade>premium</grade></profile>'
            }
        ),
        (
            {
                'path': '/users/tomlee/profile.xml',
                'request': requests.put,
                'headers': {
                    'Content-Type': 'application/xml'
                },
                'data': 'Hello World'
            },
            {
                'status': 409,
                'headers': {
                    'Content-Type': 'text/plain',
                    'Access-Control-Allow-Origin': '*',
                },
                'data': 'object already updated'
            }
        ),
        (
            {
                'path': '/users/tomlee/todo/abc',
                'request': requests.get,
                'headers': {},
                'data': 'Hello World'
            },
            {
                'status': 404,
                'headers': {},
                'data': ''
            }
        ),
        (
            {
                'path': '/users/tomlee/todo/123',
                'request': requests.post,
                'headers': {},
                'data': 'Hello World'
            },
            {
                'status': 404,
                'headers': {},
                'data': ''
            }
        ),
        (
            {
                'path': '/users/tomlee/profile',
                'request': requests.get,
                'headers': {},
                'data': 'Hello World'
            },
            {
                'status': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                },
                'data': 'Hello tomlee'
            }
        ),
        (
            {
                'path': '/users/tomlee/profile',
                'request': requests.post,
                'headers': {},
                'data': 'Hello World'
            },
            {
                'status': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                },
                'data': {'hello': 'tomlee'}
            }
        )
    ]

    @pytest.mark.parametrize('req, resp', reqresps)
    def test_responses(self, req, resp):
        response = req['request'](
            f'http://{HOST}:{PORT}{req["path"]}', headers=req['headers'], data=req['data'])
        assert response.status_code == resp['status']
        assert response.headers['Server'] == "YetAnotherMockAPIServer 0.0.1"
        del response.headers['Server']
        del response.headers['Date']
        assert response.headers == resp['headers']
        respdata = resp['data']
        if isinstance(respdata, str):
            assert response.text == respdata
        else:
            assert loads(response.text) == respdata
