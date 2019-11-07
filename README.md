# Yamas - Yet Another Mock API Server

This project develops a simple mock API server for prototyping and testing client applications.  

Based on [`http.server`](https://docs.python.org/3.6/library/http.server.html) of Python3.6+, Yamas is a testing API server which can accept HTTP requests from a client and reply with pre-defined mock HTTP responses. (*Note: Yamas should not be used for production.*)

The mock responses and the rules of selecting them are specified in a JSON file. Processing an request, Yamas locates the wanted mock response by matching the request path with a sequence of user-specified regular expressions and then looking up the response by the request method.

## Usage

Yamas has been published to [PyPI](https://pypi.org/project/yamas/). You can use `pip` to install Yamas:

```sh
pip install yamas
```

The command-line interface of Yamas is as follows:

```sh
yamas [-e|--endpoint host:port] -f|--file mock_responses_spec
```

* `-e` or `--endpoint` specifies the host address and the port number of the endpoint; if this is not specified, `127.0.0.1:7000` will be used.
* `-f` or `--file` specifies the path of the JSON file which defines the mock responses and the selection rules.

For example,

```sh
yamas -e localhost:8000 -f mock_responses.json
```

To run Yamas using the source code under the project root directory (e.g., `/home/yam/git/yamas`):

```sh
pip install .
yamas -e localhost:8000 -f data/mock_responses.json
```

To run the tests:

```sh
python -m pytest tests/
```

## Specification of mock responses

The mock responses and the rules of selecting them are specified in a JSON file, which is given on the command line. A sample specification is given as follows:

```json
{
    "global": {
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "serverHeader": "YetAnotherMockAPIServer 0.0.1"
    },
    "rules": {
        "^/users/(\\w+)/todo/(\\d+)$": {
            "GET": {
                "status": 200,
                "content": {
                    "user": "$p_0",
                    "taskid": "$p_1",
                    "task": "Buy milk",
                    "pri": "low"
                },
                "contentType": "json",
                "interpolate": true
            },
            "DELETE": {
                "status": 410
            }
        },
        "^/users/\\w+/todo/?": {
            "GET": {
                "status": 200,
                "content": [
                    "123",
                    "456",
                    "789"
                ],
                "contentType": "json"
            },
            "POST": {
                "content": {
                    "taskid": "123"
                },
                "contentType": "json",
                "interpolate": false
            }
        },
        "^/users/(\\w+)/profile.xml$": {
            "GET": {
                "status": 200,
                "headers": {
                    "Content-Type": "application/xml"
                },
                "content": "<profile><user>$p_0</user><org>yam.ai</org><grade>premium</grade></profile>",
                "contentType": "text",
                "interpolate": true
            },
            "PUT": {
                "status": 409,
                "content": "object already updated",
                "contentType": "text"
            }
        },
        "^/users/(\\w+)/profile$": {
            "GET": {
                "status": 200,
                "headers": {
                    "Content-Type": ""
                },
                "content": "Hello $p_0",
                "contentType": "text",
                "interpolate": true
            },
            "POST": {
                "status": 200,
                "headers": {
                    "Content-Type": ""
                },
                "content": {
                    "hello": "$p_0"
                },
                "contentType": "json",
                "interpolate": true
            }
        }
    }
}
```

The root level is a JSON object. Inside the root object, there are optional objects `global` and `rules`.

Under `global`, there are optional objects `headers` and `serverHeader`. The `headers` object specifies the default HTTP response headers to be included in the response to each request matching any of the rules specified below. The `serverHeader` field gives a string value that customizes the default HTTP response header `Server`.

The `rules` object maps the pattern ([Python regular expressions](https://docs.python.org/3.6/howto/regex.html)) of an HTTP request path (i.e., key) to an object containing the mock responses for different HTTP methods (i.e., value). The matching is done in the order of the key-value pairs specified under `rules`. In other words, a key is selected one at a time from the top to the bottom and its regular expression is used to match the request path.

When the request path matches the pattern in a key, the associated JSON object specifying the mock responses associated with the HTTP methods will be selected. When the request path does not match the regular expression, the regular expression in the next key will be selected. If the request path matches no regular expression, a [404 Not Found](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) response will be replied.

When a request path matches the pattern in a key, the corresponding JSON object will be used to construct the response. Inside this JSON object, the keys are [HTTP methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods). The JSON object value corresponding to each HTTP method key specifies a mock response.

The mock response object contains the following:

* `status` specifies the status code of the response. If `status` is not specified, `200 OK` will be used.
* `headers` specifies a JSON object containing the header names and values. If there are no user-defined headers, `headers` can be omitted. If the value of a header is an empty string, the corresponding header which may be automatically added, (e.g., `Content-Type` and a globally specified header) will be removed.
* `content` specifies the content (or body) of the response. Its value should match its `contentType`.
* `contentType` specifies the data type of the content. The following types can be used:
  * `text`: `content` must be a string of the [UTF-8](https://en.wikipedia.org/wiki/UTF-8) text content. The header `Content-Type: text/plain` will be automatically added unless it is overriden by a user-specified `Content-Type` header.
  * `json`: `content` is treated as a JSON value. The header `Content-Type: application/json` will be automatically added unless it is overriden by a user-specified `Content-Type` header.
  * `contentType` is omitted: `content` is treated as `text` except the header `Content-Type: text/plain` is not automatically added.
* `interpolate` specifies whether the matched values of the capturing groups in the request path will replace the placeholders in the content template. It is `false` by default. When `interpolate` is `true`, every string value in `content` is expected to be a [Python template string](https://docs.python.org/3/library/string.html#template-strings). If `content` is `text`, the value is treated as a template. If the `content` is `json`, every string value in the object is treated as a template. As shown in the the above example, the placeholder `$p_i` will be replaced with the matched value of the *i*-th capturing group in the request path pattern. As in the above example, `$p_0` will be substituted with the matched value of the first capturing group `(\w+)` in the pattern path `^/users/(\w+)/todo/(\d+)$`, `$p_1` will be substituted with the value of the second matched capturing group `(\d+)`. Note: the special character `$` should be escaped as `$$`.

## Professional services

If you need any support or consultancy services from YAM AI Machinery, please find us at:

* https://www.yam.ai
* https://twitter.com/theYAMai
* https://www.linkedin.com/company/yamai
* https://www.facebook.com/theYAMai
* https://github.com/yam-ai
* https://hub.docker.com/u/yamai
