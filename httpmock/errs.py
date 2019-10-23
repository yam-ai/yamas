class HTTPMockException(Exception):
    pass


class ResponseError(HTTPMockException):
    pass


class RequestError(HTTPMockException):
    pass
