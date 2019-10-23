from collections import defaultdict
from collections import OrderedDict
import json
from http import HTTPStatus
from io import BufferedIOBase
from enum import Enum
from httpmock.errs import RequestError, ResponseError


class Method(Enum):
    GET = 'GET'
    POST = 'POST'


class Request:
    def __init__(self, method: Method, headers: dict, body: BufferedIOBase):
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
            return json.loads(self.body_utf8)
        except Exception as e:
            raise RequestError(e)


class Response:
    def __init__(self, status: HTTPStatus, headers: dict, body: any):
        self.status = status
        self.headers = headers
        self.body = body

    def write_body(self, wfile: BufferedIOBase):
        body_content = self.body
        body_type = type(body_content)
        try:
            if body_type == str:
                wfile.write(body_content.encode())
            elif body_type == dict:
                json.dump(body_content, wfile)
            elif body_type == bytes:
                wfile.write(body_content)
            elif body_content is None:
                wfile.write(b'')
        except Exception as e:
            raise ResponseError(e)


class ResponseGenerator:

    def respond(self, request: Request) -> Response:
        return Response(HTTPStatus.NOT_IMPLEMENTED, {}, None)


class RegexRespGen(ResponseGenerator):
    pass
