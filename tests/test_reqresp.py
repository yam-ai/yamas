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

from yamas.ex import RequestError
from json import load
from io import BufferedIOBase
from enum import Enum
from io import BytesIO
from collections import OrderedDict
from json import dumps
from yamas.reqresp import Request, Method, Response
from http import HTTPStatus
import pytest
import inspect

PATH = '/p1/p2'
METHOD = Method.GET
HEADERS = {'a': '1', 'b': '2'}
CONTENT_JSON = OrderedDict([('x', 1), ('y', 2)])
CONTENT_UTF8 = dumps(CONTENT_JSON)
CONTENT_BYTES = CONTENT_UTF8.encode('utf-8')
STATUS = HTTPStatus.OK


@pytest.fixture(scope='session')
def req() -> Request:
    return Request(PATH, METHOD, HEADERS, BytesIO(CONTENT_BYTES))


def test_request(req):
    assert req.path == PATH
    assert req.method == METHOD
    assert req.headers == HEADERS
    assert req.content_bytes() == CONTENT_BYTES
    assert req.content_utf8() == CONTENT_UTF8
    assert req.content_json() == CONTENT_JSON


@pytest.fixture(scope='session')
def resp() -> Response:
    return Response(HTTPStatus.OK, HEADERS, CONTENT_BYTES)


def test_response(resp):
    assert resp.status == HTTPStatus.OK
    assert resp.headers == HEADERS
    assert resp.content_bytes == CONTENT_BYTES
