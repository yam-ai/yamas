# Yamas - Yet Another Mock API Server

This project develops a simple mock API server for prototyping and testing client applications.  

Based on [`http.server`](https://docs.python.org/3.6/library/http.server.html) of Python3.6+, Yamas is a testing API server which can accept HTTP requests from a client and reply with mock HTTP responses. (*Note: Yamas should not be used for production.*)

The mock responses and the rules of selecting them are specified in a JSON file. Processing an request, Yamas locates the wanted mock response by matching the request path with a sequence of user-specified regular expressions and then looking up the response by the request method.

## Usage

Yamas has been published on [PyPI](https://pypi.org). You can use `pip3` to install Yamas:

```sh
pip3 install yamas
```

The command-line interface of Yamas as follows:

```sh
yamas [-e|--endpoint host:port] -f|--file mock_responses_file
```

* `-e` or `--endpoint` specifies the host address and the port number of the endpoint; if this is not specified, `0.0.0.0:7777` will be used.
* `-f` or `--file` specifies the path of the JSON file which defines the mock responses and the selection rules.

For example,

```sh
yamas.py -e localhost:8080 -f mock_responses.json
```

## Specification of mock responses

The mock responses and the rules of selecting them are specified in a JSON file, which is given on the command line. A sample specification is given as follows:

```json
{
    "^/users/(\\w+)/todo/(\\d+)$": {
        "GET": {
            "status": 200,
            "body": {
                "user": "{0}",
                "taskid": "{1}",
                "task": "Buy milk",
                "pri": "low"
            },
            "interpolate": true
        },
        "DELETE": {
            "status": 410
        }
    },
    "^/users/\\w+/todo/?$": {
        "POST": {
            "taskid": 123
        }
    },
    "^/users/(\\w+)/profile.xml$": {
        "GET": {
            "status": 200,
            "headers": {
                "Content-Type": "application/xml"
            },
            "body": "<profile><user>{0}</user><org>yam.ai</org><grade>premium</grade></profile>",
            "interpolate": true
        },
        "PUT": {
            "status": 409,
            "headers": {
                "Content-Type": "text/plain"
            },
            "body": "object already updated"
        }
    }
}
```

The root level is a JSON object. Inside the root object, the keys are [Python regular expressions](https://docs.python.org/3.6/howto/regex.html) and the associated values are JSON ojbects. The regular expressions are used to match the path of a request. The JSON object value specifies the mock responses for each HTTP method. The matching is done in the order of the keys specified in the file. In other words, a key is selected one by one from the top to the bottom and its regular expression is used to match the request path.

When the request path matches the regular expression of a key, the associated JSON object which specifies the mock responses will be selected. When the request path does not match the regular expression, the regular expression in the next key will be selected. If the request path matches no regular expression, a [404 Not Found](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) response will be replied.

When the request path matches the regular expression in a key, the corresponding JSON object value will be used to construct the response. Inside this JSON object, the keys are [HTTP methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods). The JSON object corresponding to each HTTP method key specifies a mock response.

The mock response object contains the following:

* `status` specifies the status code of the response. If `status` is not specified, `200 OK` will be used.
* `headers` specifies a JSON object containing the header names and values. If there are no user-defined headers, `headers` can be omitted.
* `body` specifies the body of the response. Its value can be either a JSON object or a string. If the value is a JSON object, the response body will be the same JSON object; and the `Content-Type: application/json` header will be automatically added unless it is overrided by a different `Content-Type` header specified in the `headers` value. If the value is a string, the response body will be a [UTF-8](https://en.wikipedia.org/wiki/UTF-8) text.
* `interpolate` specifies whether the values of the matched capturing groups will be inserted into the body string. It is `false` by default. When `interpolate` is `true`, every string value in `body` is expected to be a [Python format string](https://docs.python.org/3.6/library/string.html#format-string-syntax). If `body` is a string, the value is treated as a format string. If the `body` is a JSON object, every string value in the object is treated as a format string. In the first format string of the the above example, `{0}` will be substituted with the value of the first matched capturing group in the regular expression (i.e., `(\w+)`), `{1}` will be substituted with the value of the second matched capturing group (i.e., `(\d+)` ). Note the special character `\` in a regular expression needs to be escaped as `\\`. 

## Professional services

If you need any support or consultancy services from YAM AI Machinery, please find us at:

* https://www.yam.ai
* https://twitter.com/theYAMai
* https://www.linkedin.com/company/yamai
* https://www.facebook.com/theYAMai
* https://github.com/yam-ai
* https://hub.docker.com/u/yamai
