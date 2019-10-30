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
from collections import OrderedDict
from json import dumps
from yamas.reqresp import Request, Method, Response
from http import HTTPStatus


class TestRequest(TestCase):

    def setUp(self):
        self.path = '/p1/p2'
        self.method = Method('GET')
        self.headers = {'a': 1, 'b': 2}
        self.content_dict = OrderedDict()
        self.content_dict['x'] = 1
        self.content_dict['y'] = 2
        self.content_str = dumps(self.content_dict)
        self.content_io = io.BytesIO(self.content_str.encode('utf-8'))
        self.req = Request(self.path, self.method, self.headers, self.content_io)

    def test_members(self):
        self.assertEqual(self.req.path, self.path)
        self.assertEqual(self.req.method, self.method)
        self.assertEqual(self.req.headers, self.headers)

    def test_content_bytes(self):
        self.assertEqual(self.req.content_bytes(), self.content_str.encode('utf-8'))

    def test_content_utf8(self):
        self.assertEqual(self.req.content_utf8(), self.content_str)

    def test_content_json(self):
        self.assertEqual(self.req.content_json(), self.content_dict)


class TestResponse(TestCase):
    def setUp(self):
        self.status = HTTPStatus.OK
        self.headers = {'a': 1, 'b': 2}
        self.content_bytes = b'abc'

    def test_members(self):
        resp = Response(HTTPStatus.OK, self.headers, self.content_bytes)
        self.assertEqual(resp.status, self.status)
        self.assertEqual(resp.headers, self.headers)
        self.assertEqual(resp.content_bytes, self.content_bytes)
