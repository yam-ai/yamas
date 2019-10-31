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

from unittest import TestCase
from io import BytesIO
from http import HTTPStatus
from json import dumps
from yamas.respgen import ResponseMaker, ResponseSelector, PatternResponseGenerator
from yamas.reqresp import Request, Response, Method
from yamas.ex import GeneratorError


class TestPatternResponseGenerator(TestCase):
    def setUp(self):
        self.mock_dict_norm = {
            '^/users/(\\w+)/todo/(\\d+)$': {
                'GET': {
                    'status': 200,
                    'content': {
                        'user': '{0}',
                        'taskid': '{1}',
                        'task': 'Buy milk',
                        'pri': 'low'
                    },
                    'contentType': 'json',
                    'interpolate': True
                },
                'DELETE': {
                    'status': 410
                }
            },
            '^/users/\\w+/todo/?$': {
                'GET': {
                    'status': 200,
                    'content': ['123', '456', '789'],
                    'contentType': 'json'
                },
                'POST': {
                    'content': {
                        'taskid': '123'
                    },
                    'contentType': 'json',
                    'interpolate': False
                }
            },
            '^/users/(\\w+)/profile.xml$': {
                'GET': {
                    'status': 200,
                    'headers': {
                        'Content-Type': 'application/xml'
                    },
                    'content': '<profile><user>{0}</user><org>yam.ai</org><grade>premium</grade></profile>',
                    'interpolate': True
                },
                'PUT': {
                    'status': 409,
                    'content': 'object already updated',
                    'contentType': 'text'
                }
            },
            '^/users/(\\w+)/profile$': {
                'GET': {
                    'status': 200,
                    'headers': {
                        'Content-Type': ''
                    },
                    'content': 'Hello {0}',
                    'contentType': 'text',
                    'interpolate': True
                },
                'POST': {
                    'status': 200,
                    'headers': {
                        'Content-Type': ''
                    },
                    'content': {'hello': '{0}'},
                    'contentType': 'json',
                    'interpolate': True
                }
            },
        }
        self.mock_json_norm = dumps(self.mock_dict_norm)

    def test_valid_mock(self):
        g0 = PatternResponseGenerator()
        g0.load_from_dict(self.mock_dict_norm)
        g1 = PatternResponseGenerator()
        g1.load_from_json(self.mock_json_norm)
        gens = [g0, g1]
        for g in gens:
            tests = [
                {
                    'request': {
                        'path': '/users/tomlee/todo/123',
                        'method': Method.GET,
                        'headers': {'a': '1'},
                        'content_io': BytesIO(b'Hello World')
                    },
                    'response': {
                        'status': 200,
                        'headers': {
                            'Content-Type': 'application/json'
                        },
                        'content_bytes': dumps({
                            'user': 'tomlee',
                            'taskid': '123',
                            'task': 'Buy milk',
                            'pri': 'low'
                        }).encode('utf-8'),
                    }
                },
                {
                    'request': {
                        'path': '/users/tomlee/todo/123',
                        'method': Method.DELETE,
                        'headers': {'a': '1'},
                        'content_io': BytesIO(b'Hello World')
                    },
                    'response': {
                        'status': 410,
                        'headers': {},
                        'content_bytes': b'',
                    }
                },
                {
                    'request': {
                        'path': '/users/tomlee/todo/',
                        'method': Method.GET,
                        'headers': {'a': '1'},
                        'content_io': BytesIO(b'Hello World')
                    },
                    'response': {
                        'status': 200,
                        'headers': {
                            'Content-Type': 'application/json'
                        },
                        'content_bytes': dumps([
                            '123', '456', '789'
                        ]).encode('utf-8'),
                    }
                },
                {
                    'request': {
                        'path': '/users/tomlee/todo/',
                        'method': Method.POST,
                        'headers': {'a': '1'},
                        'content_io': BytesIO(b'Hello World')
                    },
                    'response': {
                        'status': 200,
                        'headers': {'Content-Type': 'application/json'},
                        'content_bytes': dumps({
                            'taskid': "123"
                        }).encode('utf-8'),
                    }
                },
                {
                    'request': {
                        'path': '/users/tomlee/profile.xml',
                        'method': Method.GET,
                        'headers': {
                            'Content-Type': 'application/xml'
                        },
                        'content_io': BytesIO(b'Hello World')
                    },
                    'response': {
                        'status': 200,
                        'headers': {'Content-Type': 'application/xml'},
                        'content_bytes': b'<profile><user>tomlee</user><org>yam.ai</org><grade>premium</grade></profile>'
                    }
                },
                {
                    'request': {
                        'path': '/users/tomlee/profile.xml',
                        'method': Method.PUT,
                        'headers': {
                            'Content-Type': 'xml/plain'
                        },
                        'content_io': BytesIO(b'Hello World')
                    },
                    'response': {
                        'status': 409,
                        'headers': {'Content-Type': 'text/plain'},
                        'content_bytes': b'object already updated'
                    }
                },
                {
                    'request': {
                        'path': '/users/tomlee/todo/abc',
                        'method': Method.GET,
                        'headers': {},
                        'content_io': BytesIO(b'Hello World')
                    },
                    'response': {
                        'status': 404,
                        'headers': {},
                        'content_bytes': b''
                    }
                },
                {
                    'request': {
                        'path': '/users/tomlee/todo/123',
                        'method': Method.POST,
                        'headers': {},
                        'content_io': BytesIO(b'Hello World')
                    },
                    'response': {
                        'status': 404,
                        'headers': {},
                        'content_bytes': b''
                    }
                },
                {
                    'request': {
                        'path': '/users/tomlee/profile',
                        'method': Method.GET,
                        'content_io': BytesIO(b'Hello World')
                    },
                    'response': {
                        'status': 200,
                        'headers': {},
                        'content_bytes': b'Hello tomlee'
                    }
                },
                {
                    'request': {
                        'path': '/users/tomlee/profile',
                        'method': Method.POST,
                        'content_io': BytesIO(b'Hello World')
                    },
                    'response': {
                        'status': 200,
                        'headers': {},
                        'content_bytes': dumps({'hello': 'tomlee'}).encode('utf-8')
                    }
                }
            ]
            for t in tests:
                resp = g.respond(
                    Request(
                        t['request']['path'],
                        t['request']['method'],
                        t['request'].get('headers'),
                        t['request']['content_io'],
                    )
                )
                self.assertEqual(resp.status, t['response']['status'])
                self.assertEqual(resp.headers, t['response']['headers'])
                self.assertEqual(resp.content_bytes,
                                 t['response']['content_bytes'])

    def test_invalid_mock(self):
        tests = {
            'invalid_regex': {
                '(': {
                    'GET': {
                        'status': 200
                    }
                }
            },
            'invalid_content_type': {
                '/abc': {
                    'GET': {
                        'status': 200,
                        'content': 'abc',
                        'contentType': 'str'
                    }
                }
            },
            'invalid_status': {
                '/abc': {
                    'GET': {
                        'status': 777,
                    }
                }
            },
            'text_type_not_number': {
                '/abc': {
                    'GET': {
                        'content': 123,
                        'contentType': 'text'
                    }
                }
            },
            'text_type_not_object': {
                '/abc': {
                    'GET': {
                        'content': {'x': 1},
                        'contentType': 'text'
                    }
                }
            },
            'null_type_not_number': {
                '/abc': {
                    'GET': {
                        'content': 123
                    }
                }
            },
            'null_type_not_object': {
                '/abc': {
                    'GET': {
                        'content': {'x': 1},
                    }
                }
            },
            'header_not_number': {
                '/abc': {
                    'GET': {
                        'headers': {'x': 1},
                    }
                }
            },
            'header_not_object': {
                '/abc': {
                    'GET': {
                        'headers': {'x': {'y': '1'}},
                    }
                }
            }
        }
        for _, t in tests.items():
            g = PatternResponseGenerator()
            self.assertRaises(
                GeneratorError,
                g.load_from_dict,
                t
            )

    def test_response_not_found(self):
        g = PatternResponseGenerator()
        g.load_from_dict(self.mock_dict_norm)
        tests = {
            'pattern_not_matched': {
                'path': '/users/tomlee/todo/xyz',
                'method': Method.GET,
                'headers': {'a': '1'},
                'content_io': BytesIO(b'Hello World')
            },
            'method_not_matched': {
                'path': '/users/tomlee/todo/123',
                'method': Method.PATCH,
                'headers': {'a': '1'},
                'content_io': BytesIO(b'Hello World')

            },
        }
        for _, t in tests.items():
            resp = g.respond(
                Request(
                    t['path'],
                    t['method'],
                    t.get('headers'),
                    t['content_io']
                )
            )
            self.assertEqual(resp.status, HTTPStatus.NOT_FOUND)
            self.assertEqual(resp.content_bytes, b'')

    def test_interpolation_errors(self):
        mock = {
            '^/hello/(\\w)+$': {
                'GET': {
                    'status': 200,
                    'content': 'hello {0} and {1}',
                    'interpolate': True
                }
            },
            '^/hello/(\\w)+/world/(\\d)+$': {
                'POST': {
                    'status': 200,
                    'content': 'hello {0}',
                    'interpolate': True
                }
            }
        }

        tests = [
            {
                'request': {
                    'path': '/hello/tomlee',
                    'method': Method.GET
                },
                'response': {
                    'status': HTTPStatus.INTERNAL_SERVER_ERROR
                }
            },
            {
                'request': {
                    'path': '/hello/tomlee/world/123',
                    'method': Method.POST
                },
                'response': {
                    'status': HTTPStatus.OK
                }
            }
        ]

        g = PatternResponseGenerator()
        g.load_from_dict(mock)

        for t in tests:
            req = t['request']
            resp = t['response']
            actual_resp = g.respond(Request(
                req['path'], req['method'], None, BytesIO(b'')
            ))
            self.assertEqual(actual_resp.status, resp['status'])
