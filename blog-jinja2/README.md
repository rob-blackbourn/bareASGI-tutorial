# blog-jinja2

This project contains a simple blogging web site using server side scripting
using the popular [jinja2](https://jinja.palletsprojects.com/en/2.10.x/)
templating package.

## Environment

We will need the following packages:

* bareASGI - the web framework
* bareASGI-jinja2 - The package providing support for jinja2 in bareASGI
* aiosqlite - an asynchronous sqlite package
* hypercorn - the ASGI server
* PyYaml - a yaml parser for the config file.

These can be installed in a virtual environment with poetry.

```bash
blog-jinja2$ python3.7 -m venv .venv
blog-jinja2$ . .venv/bin/activate
(.venv) blog-jinja2$ pip install bareASGI-jinja2
```


## Setting up the application for jinja2.

The following code fragment shows how we add jinja2 support to bareASGI.

```python
import pkg_resources
from bareasgi import Application
import bareasgi_jinja2
import jinja2

...

app = Application(info=dict(config=config))

templates = pkg_resources.resource_filename(__name__, "templates")
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(templates),
    autoescape=jinja2.select_autoescape(['html', 'xml']),
    enable_async=True
)
bareasgi_jinja2.add_jinja2(app, env)
```

Note how we first create a jinja2 environment. To create the environment we need
to specify where our templates will be. In this case they will be in a folder
called `templates` at the save level as the above file. We also setup auto
escaping for `.html` and `.xml` files to stop a malicious user injecting html.
Finally we enable asynchronous support.

After creating the environment we simply add it to the bareASGI application with
`bareasgi_jinja2.add_jinja2`.

## The repository

We will need a repository to store the blog posts. A simple repository is
implemented using aiosqlite as the storage engine 
[here](bareasgi_blog/blog_repository).

We will not discuss the implementation here, but it should be noted that all
calls are asynchronous. For example the method to create a blog is as follows:

```python
    async def create(self, **kwargs) -> int:
        """Create a blog entry"""

        now = datetime.utcnow()
        inserts = {
            'created': now,
            'updated': now
        }
        inserts.update(kwargs)

        stmt = f"""
INSERT INTO blog_entries({','.join(inserts.keys())})
VALUES ({','.join('?' for _ in range(len(inserts)))})
"""
        args = tuple(inserts.values())

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            await self._conn.commit()
            return cur.lastrowid
```

This would be called in the following manner:

```python
post_id = await repository.create(**{
    'title': 'My First Post',
    'description': 'A short post',
    'content': 'Words of wisdom'
})
```

The repository takes the `aiosqlite` connection as an input argument:

```python
class BlogRepository:

    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    ...
```

This presents a problem.