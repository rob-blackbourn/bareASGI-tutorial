# Getting Started with bareASGI

## Prerequisites

### ASGI Servers

The [bareASGI](https://github.com/rob-blackbourn/bareasgi) package is a
web framework package for [ASGI](https://asgi.readthedocs.io/en/latest/)
servers, so the first thing required is a server.

The servers I have been using are:

* [hypercorn](https://pgjones.gitlab.io/hypercorn/)
* [uvicorn](https://www.uvicorn.org/)

At the time of writing hypercorn has the best support for HTTP/2, while
uvicorn is the most simple to use. Checkout the links above for installation
instructions,

The examples will use both servers.

### bareASGI

Finally we must install bareASGI. The bare libraries use
[poetry](https://poetry.eustace.io/), but you can just use pip if you prefer.

```bash
$ pip install bareasgi
```

### Visual Studio Code

I use [Visual Studio Code](https://code.visualstudio.com/) as my development
environment, and I have left the .vscode files with my settings and launch
configurations.

## Hello, World!

Here's a simple hello world program:

```python
import uvicorn
from bareasgi import Application

app = Application()


@app.on_http_request({'GET'}, '/')
async def http_request_handler(scope, info, matches, content):
    return 200, [(b'content-type', b'text/plain')], text_writer('Hello, World!')

uvicorn.run(app, port=9009)
```
