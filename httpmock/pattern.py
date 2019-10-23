from httpmock.mock import MockRequestHandler
from collections import OrderedDict
from http import HTTPStatus
from typing import Pattern
from httpmock.respgen import Method, Request, Response
from httpmock.errs import GeneratorError


class PatternResponseGenerator(MockRequestHandler):
    def __init__(self):
        self.matchers = {
            x.value: OrderedDict() for x in list(Method)
        }
        return

    def add_matcher(self, method: Method, pattern: Pattern, status: HTTPStatus, headers: dict, body: any):
        pat_resp_dict = self.matchers(method)
        if pattern in pat_resp_dict:
            raise GeneratorError('pattern already exists')
        pat_resp_dict[pattern] = Response(status, headers, body)
        return

    def del_matcher(self, method: Method, pattern: Pattern):
        try:
            del(self.matchers(method)[pattern])
        except KeyError as e:
            raise GeneratorError(e)

    def respond(self, request: Request) -> Response:
        pat_resp_dict = self.matchers[request.method]
        for pat, resp in self.matchers[request.method]:
            if pat.fullmatch(request.path):
                return resp
        return Response(HTTPStatus.NOT_FOUND, {}, None)
