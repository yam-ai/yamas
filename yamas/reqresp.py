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

from enum import Enum
from io import BufferedIOBase
from http import HTTPStatus
from collections import OrderedDict
from json import load
from yamas.ex import RequestError


class Method(Enum):
    GET = 'GET'
    HEAD = 'HEAD'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'
    TRACE = 'TRACE'
    PATCH = 'PATCH'
    CONNECT = 'CONNECT'


class Request:
    def __init__(self, path: str, method: Method, headers: dict, body_io: BufferedIOBase):
        self.path = path
        self.method = method
        self.headers = headers
        self.body_io = body_io

    def body_bytes(self) -> bytes:
        return self.body_io.read()

    def body_utf8(self) -> str:
        try:
            return self.body_bytes().decode('utf-8')
        except Exception as e:
            raise RequestError(e)

    def body_json(self) -> str:
        try:
            return load(self.body_io, object_pairs_hook=OrderedDict)
        except Exception as e:
            raise RequestError(e)


class Response:
    def __init__(self, status: HTTPStatus, headers: dict, body_bytes: bytes):
        self.status = status
        self.headers = headers
        self.body_bytes = body_bytes
