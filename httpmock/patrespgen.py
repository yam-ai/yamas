import re
from collections import OrderedDict
from json import loads
from http import HTTPStatus
from typing import Pattern
from httpmock.respgen import Method, Request, Response, ResponseGenerator
from httpmock.errs import GeneratorError


class PatternResponseGenerator(ResponseGenerator):
    def __init__(self):
        self.matchers = {
            x: OrderedDict() for x in list(Method)
        }
        return

    def load_from_dict(self, matcher_dict: dict):
        for method in list(Method):
            patresp = matcher_dict.get(method.value)
            if not patresp:
                continue
            for pat, resp in patresp.items():
                try:
                    cpat = re.compile(pat)
                except:
                    raise GeneratorError(f'Failed to compile pattern {pat}')
                status_code = resp['status'] if 'status' in resp else 200
                headers = resp.get('headers')
                body = resp.get('body')
                self.add_matcher(method, cpat, HTTPStatus(
                    status_code), headers, body)

    def load_from_json(self, matcher_json: str):
        try:
            matcher_dict = loads(matcher_json)
        except Exception as e:
            raise GeneratorError(f'Failed to parse JSON: {e}')
        self.load_from_dict(matcher_dict)

    def add_matcher(self, method: Method, pattern: Pattern, status: HTTPStatus, headers: dict, body: any):
        pat_resp_dict = self.matchers[method]
        if pattern in pat_resp_dict:
            raise GeneratorError('pattern already exists')
        pat_resp_dict[pattern] = Response(status, headers, body)
        return

    def del_matcher(self, method: Method, pattern: Pattern):
        try:
            del(self.matchers[method][pattern])
        except KeyError as e:
            raise GeneratorError(e)

    def respond(self, request: Request) -> Response:
        pat_resp_dict = self.matchers[request.method]
        for pat, resp in pat_resp_dict.items():
            if pat.fullmatch(request.path):
                return resp
        return Response(HTTPStatus.NOT_FOUND, {}, None)
