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
    def __init__(self, method: Method, path: str, headers: dict, body: BufferedIOBase):
        self.method = method
        self.path = path
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
        return

    def write_body(self, wfile: BufferedIOBase):
        body_content = self.body
        body_type = type(body_content)
        try:
            if body_type is str:
                wfile.write(body_content.encode())
            elif body_type is dict:
                if not self.headers:
                    self.headers = dict()
                if 'Content-Type' not in self.headers:
                    self.headers['Content-Type'] = 'application/json'
                wfile.write(json.dumps(body_content).encode('utf-8'))
            elif body_type is bytes:
                wfile.write(body_content)
            elif body_content is None:
                wfile.write(b'')
            else:
                raise ResponseError(f'Unsupported body type {body_type}')
        except Exception as e:
            raise ResponseError(e)
        return


class ResponseGenerator:

    def respond(self, request: Request) -> Response:
        return Response(HTTPStatus.NOT_IMPLEMENTED, {}, None)
