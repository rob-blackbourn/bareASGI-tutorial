# Server for blog-rest

Here we will write a REST server for a simple blogging application.

## The Repository

First we will create a simple repository using sqlite as the backend storage
with the asynchronous `aiosqlite` package.

The source code for the repository can be found
[here](bareasgi_glog/blog_repository.py).

We're not too interested in the details of the repository, but there are a few
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

We implement the controller as a class.

The source code for the controller can be found
[here](bareasgi_glog/blog_controller.py).

The class is initialised with the repository.

```python
class BlogRestController:
    """BlogRestController"""

    def __init__(self, repository: BlogRepository) -> None:
        self._repository = repository
```

Each of the route handlers are then implemented. Here is the handler which
creates a blog.

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

After creating the routes we implement a method to register them.

```python
    def add_routes(self, app):
        app.http_router.add({'POST', 'OPTIONS'}, '/blog/api/post', self._create)
        app.http_router.add({'GET'}, '/blog/api/post/{id:int}', self._read)
        ...
```

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
    cors_middleware = CORSMiddleware()
    app = Application(info={}, middlewares=[cors_middleware])
    app.startup_handlers.append(partial(_on_startup, app))
    app.shutdown_handlers.append(_on_shutdown)
    return app
```

There are a couple of interesting things to note here.

The startup handler is added using a `partial` in order to pass in the 
application instance.

The `info` parameter is used to make the sqlite connection available to the
shutdown handler.
