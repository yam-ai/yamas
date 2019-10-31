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

from typing import List, Tuple
from http import HTTPStatus
from yamas.respgen import ResponseMaker, ResponseSelector
from yamas.reqresp import ContentType
import pytest


class TestResponseSelector:

    respmakers = [
        ResponseMaker(HTTPStatus.OK, {}, str(i), ContentType.TEXT, False)
        for i in range(3)
    ]
    respsels = []

    for loop in [True, False]:
        respsel = ResponseSelector(loop)
        respsels.append((respsel, loop))
        for rm in respmakers:
            respsel.add_response_maker(rm)

    @pytest.mark.parametrize('respsel, loop', respsels)
    def test_select_response_selector(self, respsel, loop):
        for i in range(5):
            if loop:
                assert respsel.make_response(tuple()).content_bytes.decode(
                    'utf-8') == str(i % 3)
            else:
                assert respsel.make_response(tuple()).content_bytes.decode(
                    'utf-8') == str(min(i, 2))
