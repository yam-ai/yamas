
from typing import Callable
from http.server import BaseHTTPRequestHandler
from httpmock.respgen import ResponseGenerator, Response, Request, Method


def make_handler_class(name: str, respgen: ResponseGenerator) -> Callable:
    return type(name, (ResponseGenerator,), {'respgen': respgen})


class MockRequestHandler(BaseHTTPRequestHandler):

    respgen = ResponseGenerator()

    def respond(self, method: Method):
        request = Request(Method.GET, self.path, self.headers, self.rfile)
        response = self.respgen.respond(request)
        for k, v in response.headers:
            self.send_header(k, v)
        status_value = response.status.value
        if 200 <= status_value < 300:
            self.send_response(response.status.value)
        else:
            self.send_response(response.status.value)
        response.write_body(self.wfile)
        return

    def do_GET(self):
        self.respond(Method.GET, self.path, self.headers)
        return

    def do_POST(self):
        self.respond(Method.GET, self.path, self.headers)
        return
