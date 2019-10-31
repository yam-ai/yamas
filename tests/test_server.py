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

from unittest import TestCase
from unittest.mock import patch, mock_open
from yamas.server import Yamas
from yamas.ex import ServerError


class TestYamas(TestCase):
    VALID_JSON = '''
{
    "^/users/(\\\\w+)/todo/(\\\\d+)$": {
        "GET": {
            "status": 200,
            "content": {
                "user": "{0}",
                "taskid": "{1}",
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
            "content": "<profile><user>{0}</user><org>yam.ai</org><grade>premium</grade></profile>",
            "contentType": "text",
            "interpolate": true
        },
        "PUT": {
            "status": 409,
            "content": "object already updated",
            "contentType": "text"
        }
    }
}
    '''

    INVALID_JSON = 'this is not a json'

    @patch('builtins.open', new_callable=mock_open, read_data=VALID_JSON)
    def test_load_data(self, mock_file):
        mock_spec = '/some/mock/response/json'
        server = Yamas()
        server.load_data(mock_spec)
        mock_file.assert_called_with(mock_spec, 'r')

    @patch('builtins.open', new_callable=mock_open, read_data=INVALID_JSON)
    def test_http_reqestus(self, mock_file):
        mock_spec = '/some/mock/response/json'
        server = Yamas()
        self.assertRaises(ServerError, server.load_data, mock_spec)
        mock_file.assert_called_with(mock_spec, 'r')
