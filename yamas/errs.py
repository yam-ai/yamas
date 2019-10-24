class HTTPMockException(Exception):
    pass


class ResponseError(HTTPMockException):
    pass


class RequestError(HTTPMockException):
    pass


class GeneratorError(HTTPMockException):
    pass
