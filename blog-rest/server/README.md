# Server for blog-rest

Here we will write a REST server for a simple blogging application.

It will respond to the following end points:

* POST /blog/api/post - create a blog post
* GET /blog/api/post/{id:int} - read a blog post
* GET /blog/api/post - read the latest blog posts
* POST /blog/api/post/{id:int} - update a blog post
* DELETE /blog/api/post/{id:int} - delete a blog post

## Usage

This project uses poetry.

First install the dependencies.

```bash
$ poetry install
```

Then run the server.

```bash
$ poetry run start-server
```

## The Repository

First we will create a simple repository using sqlite as the backend storage
with the asynchronous 
[`aiosqlite`](https://github.com/jreese/aiosqlite)
package.

The source code for the repository can be found
[here](bareasgi_glog/blog_repository.py).

The implementation of the repository isn't relevant here , but there are a few
points to note.

The repository is implemented as a class which receives the connection at
initialisation:


```python
class BlogRepository:
    """"Repository"""

    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn
```

All the calls are asynchronous. For example to read the latest posts we call the
following method:

```python
    async def read_between(
            self,
            start_value: Any,
            end_value: Any,
            columns: Optional[List[str]],
            order_by: str,
            limit: int
    ) -> List[Dict[str, Any]]:
        stmt = f"""
SELECT rowid AS id,{','.join(columns) if columns else '*'}
FROM blog_entries
WHERE created BETWEEN ? AND ?
ORDER BY {order_by}
LIMIT ?
"""
        args = (start_value, end_value, limit)

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            unpack = _make_unpacker(cur)
            values = [unpack(row) async for row in cur]
            return values
```

## The controller

I have chosen to implement the controller as a class.

The source code for the controller can be found
[here](bareasgi_glog/blog_controller.py).

The class is initialised with the repository.

```python
class BlogController:
    """BlogController"""

    def __init__(self, repository: BlogRepository) -> None:
        self._repository = repository
```

### The Handlers

Each of the route handlers are then implemented.

Here is the handler which creates a blog when it receives a `POST` on
`/blog/api/post` with the body containing the post as JSON.

```python
    async def _create(self, scope, info, matches, content):
        try:
            media_type, *_ = header.content_type(scope['headers'])
            if media_type != b'application/json':
                raise RuntimeError("Invalid media type")

            text = await text_reader(content)
            args = json.loads(text)

            id_ = await self._repository.create(**args)

            return (
                200,
                [(b'content-type', b'application/json')],
                text_writer(
                    json.dumps({
                        'id': id_,
                        'read': f'/blog/api/post/{id_}'
                    })
                )
            )
        except:
            return 500
```

The JSON payload would look like this.

```json
{
    "title": "My First Post",
    "description": "A short post",
    "contents": "More next week"
}
```

The handler wraps it's code in a try-except block, and returns a 500 on any
exception.

It first checks the  content type to ensure it is being sent JSON. Then it
reads the body and parses the text. Then it calls the `create` method of the
repository and is passed the id of the post that was created. Finally it returns
a 200 response with a HATEOAS style payload.

### The Routes

After creating the routes we implement a method to register them.

```python
    def add_routes(self, app):
        app.http_router.add({'POST', 'OPTIONS'}, '/blog/api/post', self._create)
        app.http_router.add({'GET'}, '/blog/api/post/{id:int}', self._read)
        ...
```

Note that the `POST` and `DELETE` routes contain an `OPTIONS` method to allow
the browser to perform CORS detection.

## The Application

The application must create the repository and the controller.

The source code for the application can be found
[here](bareasgi_glog/app.py).

As the repository
will acquire the event loop of the running context we use a startup handler.

```python
async def _on_startup(app, scope, info, request):
    conn = await aiosqlite.connect(
        ':memory:',
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
    )

    blog_repository = BlogRepository(conn)
    await blog_repository.initialise()

    blog_controller = BlogRestController(blog_repository)
    blog_controller.add_routes(app)
    info['aiosqlite_conn'] = conn

async def _on_shutdown(scope, info, request):
    conn: aiosqlite.Connection = info['aiosqlite_conn']
    await conn.close()

def create_application() -> Application:
    # Use the CORS middleware
    cors_middleware = CORSMiddleware()
    app = Application(info={}, middlewares=[cors_middleware])
    # Add the startup and shutdown handlers
    app.startup_handlers.append(partial(_on_startup, app))
    app.shutdown_handlers.append(_on_shutdown)
    return app
```

There are a couple of interesting things to note here.

The server expects to serve data to clients from a different web server, so it
uses the CORS middleware.

The startup handler is added using a `partial` in order to pass in the 
application instance.

The `info` parameter is used to make the sqlite connection available to the
shutdown handler.

## The Server

The last thing to do is to start the web server.

The source code for the server can be found
[here](bareasgi_glog/server.py).

Much of this code has been discussed in previous tutorials, however a new
feature if the use of a config file. The config  file is written in yaml, and
it holds application and logging configuration.
