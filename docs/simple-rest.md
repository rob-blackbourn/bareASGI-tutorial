# Simple REST

This example sends and receives data using REST. You will need something like
[postman](https://www.getpostman.com/) to try it out.

```python
import asyncio
import json

from hypercorn.asyncio import serve
from hypercorn.config import Config
from bareasgi import Application, text_reader, text_writer
import bareutils.header as header

async def get_info(scope, info, matches, content):
    accept = header.find(b'accept', scope['headers'])
    if accept != b'application/json':
        return 500
    text = json.dumps(info)
    headers = [
        (b'content-type', b'application/json')
    ]
    return 200, headers, text_writer(text)

async def set_info(scope, info, matches, content):
    content_type = header.find(b'content-type', scope['headers'])
    if content_type != b'application/json':
        return 500
    text = await text_reader(content)
    data = json.loads(text)
    info.update(data)
    return 204

app = Application(info={'name': 'Michael Caine'})
app.http_router.add({'GET'}, '/info', get_info)
app.http_router.add({'POST'}, '/info', set_info)

config = Config()
config.bind = ["0.0.0.0:9009"]
asyncio.run(serve(app, config))
```

To try this out make a `GET` request to http://localhost:9009/info with the
`accept` header set to `application/json`. It should response with a
`content-type` of `application/json` and *body* of `{“name": “Michael Caine"}`.
Sending a `POST` to the same endpoint with the body `{“name": “Peter Sellers"}`
and a `content-type` of `application/json` should respond with a `204` status
code. A subsequent `GET` should return `{“name": “Peter Sellers"}`.

In this example we start to use some of the request parameters. The `scope` is
passed directly from the ASGI server, and is used to fetch the headers. The
`content` is the complement of the body in the response. It is an asynchronous
generator to read the body of the request. The `text_reader` helper function is
used to retrieve the body (note this is awaited). The `info` is a user supplied
argument to the application, and is used to share information between the
handlers.

The handlers respond with `500` if the request was incorrect. We can see that it
is not necessary to provide all the elements of the response, where all elements
to the right would be `None`.

