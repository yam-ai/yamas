from http.server import BaseHTTPRequestHandler
from httpmock.respgen import ResponseGenerator, Response, Request, Method


class MockRequestHandler(BaseHTTPRequestHandler):

    respgen = ResponseGenerator()

    def respond(self, method: Method):
        request = Request(Method.GET, self.headers, self.rfile)
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
        self.respond(Method.GET)
        return

    def do_POST(self):
        self.respond(Method.POST)
        return
