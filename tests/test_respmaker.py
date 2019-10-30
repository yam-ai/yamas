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
from yamas.ex import ResponseError
from copy import deepcopy


class TestReponseMaker(TestCase):
    def setUp(self):
        self.headers = {'a': 1, 'b': 2}
        self.body_dict = {'x': '{0}', 'y': '{1}'}
        self.body_str = '{"x": "{0}", "y": "{1}"}'
        self.body_bytes = self.body_str.encode('utf-8')
        self.headers_with_content_type = deepcopy(self.headers)
        self.headers_with_content_type['Content-Type'] = 'application/json'
        self.tests = [
            {
                'input': {
                    'status': HTTPStatus.OK,
                    'headers': deepcopy(self.headers),
                    'body': self.body_str,
                    'interpolate': False
                },
                'expect': {
                    'status': HTTPStatus.OK,
                    'headers': self.headers,
                    'body_bytes': self.body_str.encode('utf-8'),
                    'template': None,
                    'interpolate': False
                }
            },
            {
                'input': {
                    'status': HTTPStatus.OK,
                    'headers': deepcopy(self.headers),
                    'body': deepcopy(self.body_dict),
                    'interpolate': False
                },
                'expect': {
                    'status': HTTPStatus.OK,
                    'headers': self.headers_with_content_type,
                    'body_bytes': self.body_str.encode('utf-8'),
                    'template': None,
                    'interpolate': False
                }
            },
            {
                'input': {
                    'status': HTTPStatus.OK,
                    'headers': deepcopy(self.headers),
                    'body': deepcopy(self.body_bytes),
                    'interpolate': False
                },
                'expect': {
                    'status': HTTPStatus.OK,
                    'headers': self.headers,
                    'body_bytes': self.body_str.encode('utf-8'),
                    'template': None,
                    'interpolate': False
                }
            },
            {
                'input': {
                    'status': HTTPStatus.OK,
                    'headers': deepcopy(self.headers),
                    'body': self.body_str,
                    'interpolate': True
                },
                'expect': {
                    'status': HTTPStatus.OK,
                    'headers': self.headers,
                    'body_bytes': None,
                    'template': self.body_str,
                    'interpolate': True
                }
            },
            {
                'input': {
                    'status': HTTPStatus.OK,
                    'headers': deepcopy(self.headers),
                    'body': deepcopy(self.body_dict),
                    'interpolate': True
                },
                'expect': {
                    'status': HTTPStatus.OK,
                    'headers': self.headers_with_content_type,
                    'body_bytes': None,
                    'template': self.body_dict,
                    'interpolate': True
                }
            },
            {
                'input': {
                    'status': HTTPStatus.OK,
                    'headers': deepcopy(self.headers),
                    'body': deepcopy(self.body_bytes),
                    'interpolate': True
                },
                'raises': ResponseError
            },
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
                self.assertEqual(rm.body_bytes, t['expect']['body_bytes'])
                self.assertEqual(rm.template, t['expect']['template'])
                self.assertEqual(rm.interpolate, t['expect']['interpolate'])
