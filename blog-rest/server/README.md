# Server for blog-rest

Here we will write a REST server for a simple blogging application.

## The Repository

First we will create a simple repository using sqlite as the backend storage
with the asynchronous `aiosqlite` package.

The source code for the repository can be found
[here](bareasgi_glog/blog_rest_controller.py).

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

The class is initialised with

```python

```