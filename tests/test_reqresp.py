import unittest
import io
from collections import OrderedDict
from json import dumps
from yamas.reqresp import Request, Method, Response
from http import HTTPStatus


class TestRequest(unittest.TestCase):

    def setUp(self):
        self.path = '/p1/p2'
        self.method = Method('GET')
        self.headers = {'a': 1, 'b': 2}
        self.body_dict = OrderedDict()
        self.body_dict['x'] = 1
        self.body_dict['y'] = 2
        self.body_str = dumps(self.body_dict)
        self.body_io = io.BytesIO(self.body_str.encode('utf-8'))
        self.req = Request(self.path, self.method, self.headers, self.body_io)

    def test_members(self):
        self.assertEqual(self.req.path, self.path)
        self.assertEqual(self.req.method, self.method)
        self.assertEqual(self.req.headers, self.headers)

    def test_body_bytes(self):
        self.assertEqual(self.req.body_bytes(), self.body_str.encode('utf-8'))

    def test_body_utf8(self):
        self.assertEqual(self.req.body_utf8(), self.body_str)

    def test_body_json(self):
        self.assertEqual(self.req.body_json(), self.body_dict)


class TestResponse(unittest.TestCase):
    def setUp(self):
        self.status = HTTPStatus.OK
        self.headers = {'a': 1, 'b': 2}
        self.body_bytes = b'abc'

    def test_members(self):
        resp = Response(HTTPStatus.OK, self.headers, self.body_bytes)
        self.assertEqual(resp.status, self.status)
        self.assertEqual(resp.headers, self.headers)
        self.assertEqual(resp.body_bytes, self.body_bytes)
