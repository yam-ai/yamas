from typing import Callable
from http.server import BaseHTTPRequestHandler
from yamas.respgen import ResponseGenerator, Response, Request, Method
from http import HTTPStatus


def make_handler_class(name: str, respgen: ResponseGenerator) -> Callable:
    handler_class = type(name, (MockRequestHandler,), {'respgen': respgen})
    handler_class.server_version = 'Yamas - Yet another mock API server'
    handler_class.sys_version = ''
    return handler_class


class MockRequestHandler(BaseHTTPRequestHandler):

    respgen = ResponseGenerator()

    def respond(self, method: Method, path: str, headers: dict):
        request = Request(self.path, method, self.headers, self.rfile)
        response = self.respgen.respond(request)
        if not response:
            self.send_response(HTTPStatus.NOT_FOUND.value)
            self.end_headers()
            return
        status_value = response.status.value
        self.send_response(status_value)
        if response.headers:
            for k, v in response.headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(response.body)
        return

    def do_GET(self):
        self.respond(Method.GET, self.path, self.headers)
        return

    def do_POST(self):
        self.respond(Method.POST, self.path, self.headers)
        return
