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
import io
import sys
from collections import OrderedDict
from json import dumps
from http import HTTPStatus
from yamas.respgen import ResponseMaker
from yamas.reqresp import ContentType
from yamas.ex import ResponseError
from copy import deepcopy, copy


class TestResponseMaker:
    HEADERS = {'a': '1', 'b': '2'}
    GLOBAL_HEADERS = { 'b':  'two', 'c' :  'three' }
    CONTENT_DICT = {'x': '{0}', 'y': '{1}'}
    CONTENT_STR = dumps(CONTENT_DICT)
    CONTENT_BYTES = CONTENT_STR.encode('utf-8')
    HEADERS_WITH_JSON_TYPE = copy(GLOBAL_HEADERS)
    HEADERS_WITH_JSON_TYPE.update(HEADERS)
    HEADERS_WITH_JSON_TYPE['Content-Type'] = 'application/json'
    HEADERS_WITH_TEXT_TYPE = copy(GLOBAL_HEADERS)
    HEADERS_WITH_TEXT_TYPE.update(HEADERS)
    HEADERS_WITH_TEXT_TYPE['Content-Type'] = 'text/plain'
    HEADERS_WITH_EMPTY_TYPE = copy(GLOBAL_HEADERS)
    HEADERS_WITH_EMPTY_TYPE.update(HEADERS)
    HEADERS_WITH_EMPTY_TYPE['Content-Type'] = 'text/plain'

    tests = [
        (
            {
                'status': HTTPStatus.OK,
                'headers': deepcopy(HEADERS),
                'content': CONTENT_STR,
                'content_type': ContentType.TEXT,
                'interpolate': False,
                'global_headers': GLOBAL_HEADERS
            
            },
            {
                'status': HTTPStatus.OK,
                'headers': HEADERS_WITH_TEXT_TYPE,
                'content_bytes': CONTENT_STR.encode('utf-8'),
                'content_type': ContentType.TEXT,
                'template': None,
                'interpolate': False
            }
        ),
        (
            {
                'status': HTTPStatus.OK,
                'headers': deepcopy(HEADERS),
                'content': deepcopy(CONTENT_DICT),
                'content_type': ContentType.JSON,
                'interpolate': False,
                'global_headers': GLOBAL_HEADERS
            },
            {
                'status': HTTPStatus.OK,
                'headers': HEADERS_WITH_JSON_TYPE,
                'content_bytes': CONTENT_STR.encode('utf-8'),
                'content_type': ContentType.JSON,
                'template': None,
                'interpolate': False
            }
        ),
        (
            {
                'status': HTTPStatus.OK,
                'headers': deepcopy(HEADERS),
                'content': CONTENT_STR,
                'content_type': ContentType.TEXT,
                'interpolate': True,
                'global_headers': GLOBAL_HEADERS
            },
            {
                'status': HTTPStatus.OK,
                'headers': HEADERS_WITH_TEXT_TYPE,
                'content_bytes': None,
                'content_type': ContentType.TEXT,
                'template': CONTENT_STR,
                'interpolate': True
            }
        ),
        (
            {
                'status': HTTPStatus.OK,
                'headers': deepcopy(HEADERS),
                'content': deepcopy(CONTENT_DICT),
                'content_type': ContentType.JSON,
                'interpolate': True,
                'global_headers': GLOBAL_HEADERS
            },
            {
                'status': HTTPStatus.OK,
                'headers': HEADERS_WITH_JSON_TYPE,
                'content_bytes': None,
                'content_type': ContentType.JSON,
                'template': CONTENT_DICT,
                'interpolate': True
            }
        ),
        (
            {
                'status': HTTPStatus.OK,
                'headers': deepcopy(HEADERS),
                'content': deepcopy(CONTENT_DICT),
                'content_type': ContentType.JSON,
                'interpolate': True,
                'global_headers': GLOBAL_HEADERS
            },
            {
                'status': HTTPStatus.OK,
                'headers': HEADERS_WITH_JSON_TYPE,
                'content_bytes': None,
                'content_type': ContentType.JSON,
                'template': CONTENT_DICT,
                'interpolate': True
            }
        )
    ]

    @pytest.mark.parametrize('input, expected', tests)
    def test_response_maker(self, input, expected):
        rm = ResponseMaker(**input)
        assert rm.status == expected['status']
        assert rm.headers == expected['headers']
        assert rm.content_bytes == expected['content_bytes']
        assert rm.content_type == expected['content_type']
        assert rm.template == expected['template']
        assert rm.interpolate == expected['interpolate']
