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
import io
import sys
from collections import OrderedDict
from json import dumps
from http import HTTPStatus
from yamas.respgen import ResponseMaker
from yamas.reqresp import ContentType
from yamas.ex import ResponseError
from copy import deepcopy


class TestReponseMaker(TestCase):
    def setUp(self):
        self.headers = {'a': '1', 'b': '2'}
        self.content_dict = {'x': '{0}', 'y': '{1}'}
        self.content_str = '{"x": "{0}", "y": "{1}"}'
        self.content_bytes = self.content_str.encode('utf-8')
        self.headers_with_json_type = deepcopy(self.headers)
        self.headers_with_json_type['Content-Type'] = 'application/json'
        self.headers_with_text_type = deepcopy(self.headers)
        self.headers_with_text_type['Content-Type'] = 'text/plain'
        self.headers_with_empty_type = deepcopy(self.headers)
        self.headers_with_empty_type['Content-Type'] = ''
        self.tests = [
            {
                'input': {
                    'status': HTTPStatus.OK,
                    'headers': deepcopy(self.headers),
                    'content': self.content_str,
                    'content_type': ContentType.TEXT,
                    'interpolate': False
                },
                'expect': {
                    'status': HTTPStatus.OK,
                    'headers': self.headers_with_text_type,
                    'content_bytes': self.content_str.encode('utf-8'),
                    'content_type': ContentType.TEXT,
                    'template': None,
                    'interpolate': False
                }
            },
            {
                'input': {
                    'status': HTTPStatus.OK,
                    'headers': deepcopy(self.headers),
                    'content': deepcopy(self.content_dict),
                    'content_type': ContentType.JSON,
                    'interpolate': False
                },
                'expect': {
                    'status': HTTPStatus.OK,
                    'headers': self.headers_with_json_type,
                    'content_bytes': self.content_str.encode('utf-8'),
                    'content_type': ContentType.JSON,
                    'template': None,
                    'interpolate': False
                }
            },
            {
                'input': {
                    'status': HTTPStatus.OK,
                    'headers': deepcopy(self.headers),
                    'content': self.content_str,
                    'content_type': ContentType.TEXT,
                    'interpolate': True
                },
                'expect': {
                    'status': HTTPStatus.OK,
                    'headers': self.headers_with_text_type,
                    'content_bytes': None,
                    'content_type': ContentType.TEXT,
                    'template': self.content_str,
                    'interpolate': True
                }
            },
            {
                'input': {
                    'status': HTTPStatus.OK,
                    'headers': deepcopy(self.headers),
                    'content': deepcopy(self.content_dict),
                    'content_type': ContentType.JSON,
                    'interpolate': True
                },
                'expect': {
                    'status': HTTPStatus.OK,
                    'headers': self.headers_with_json_type,
                    'content_bytes': None,
                    'content_type': ContentType.JSON,
                    'template': self.content_dict,
                    'interpolate': True
                }
            },
            {
                'input': {
                    'status': HTTPStatus.OK,
                    'headers': deepcopy(self.headers),
                    'content': deepcopy(self.content_dict),
                    'content_type': ContentType.JSON,
                    'interpolate': True
                },
                'expect': {
                    'status': HTTPStatus.OK,
                    'headers': self.headers_with_json_type,
                    'content_bytes': None,
                    'content_type': ContentType.JSON,
                    'template': self.content_dict,
                    'interpolate': True
                }
            }
        ]

    def test_members(self):
        for t in self.tests:
            ex = t.get('raises')
            if ex:
                self.assertRaises(ex, ResponseMaker,
                                  *t['input'].values())
            else:
                rm = ResponseMaker(**t['input'])
                self.assertEqual(rm.status, t['expect']['status'])
                self.assertDictEqual(rm.headers, t['expect']['headers'])
                self.assertEqual(rm.content_bytes,
                                 t['expect']['content_bytes'])
                self.assertEqual(rm.content_type, t['expect']['content_type'])
                self.assertEqual(rm.template, t['expect']['template'])
                self.assertEqual(rm.interpolate, t['expect']['interpolate'])
