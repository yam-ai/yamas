from enum import Enum
from io import BufferedIOBase
from http import HTTPStatus
from collections import OrderedDict
from json import loads
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
    def __init__(self, path: str, method: Method, headers: dict, body: BufferedIOBase):
        self.path = path
        self.method = method
        self.headers = headers
        self.body = body

    def body_utf8(self) -> str:
        try:
            return self.body.read()
        except Exception as e:
            raise RequestError(e)

    def body_json(self) -> str:
        try:
            return loads(self.body_utf8, object_pairs_hook=OrderedDict)
        except Exception as e:
            raise RequestError(e)


class Response:
    def __init__(self, status: HTTPStatus, headers: dict, body_bytes: bytes):
        self.status = status
        self.headers = headers
        self.body_bytes = body_bytes
