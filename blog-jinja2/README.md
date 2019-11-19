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

## Configuration

We will use a configuration file rather than storing the parameters in code.
We use a yaml file which looks like this:

```yaml
app:
  host: 0.0.0.0
  port: 9501

sqlite:
  filename: ":memory:"

logging:
  version: 1
  formatters:
    simple:
      format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  handlers:
    stdout:
      class: logging.StreamHandler
      formatter: simple
      stream: ext://sys.stdout
  loggers:
    bareasgi_blog:
      level: DEBUG
      handlers:
        - stdout
      propagate: false
    bareasgi:
      level: DEBUG
      handlers:
        - stdout
      propagate: false
  root:
    level: DEBUG
    handlers:
      - stdout
```

And the config is loaded as follows:

```python
import yaml

def load_config(filename: str) -> Dict[str, Any]:
    with open(filename, 'rt') as file_ptr:
        return yaml.load(file_ptr, Loader=yaml.FullLoader)
```

In the config file there is an `app` section where the `host` and `port` are set.
If this was an https server we could put the certificate and key file locations
here.

There is a section for `sqlite` where we store the location of the file that
sqlite will use. The special `:memory:` file name is used for testing.

The last section is `logging`. This will use the 
[`logging.config.dictConfig`](https://docs.python.org/3/library/logging.config.html#logging.config.dictConfig)
module from the standard library.

## The repository

We will need a repository to store the blog posts. A simple repository is
implemented using aiosqlite as the storage engine 
[here](bareasgi_blog/blog_repository.py).

The implementation is not relevant for this tutorial, but it should be noted
that all calls are asynchronous. For example the method to create a blog is as
follows:

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

Whenever an `await` call is made the interpreter has the opportunity to give up
control to another part of code that has been waiting. This keeps our web server
responsive to other incoming requests.

The repository takes the `aiosqlite` connection as an input argument:

```python
class BlogRepository:

    def __init__(self, conn: aiosqlite.Connection):
        self._conn = conn

    ...
```

This presents a problem. As discussed
[here](../docs/background-tasks.md#gotcha!), anything that uses the asyncio
event loop needs to be started by the ASGI server. We accomplish this with a
startup task.

```python
async def on_startup(scope, info, request):
    sqlite_filename = info['config']['sqlite']['filename']

    conn = await aiosqlite.connect(
        sqlite_filename,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )

    blog_repository = BlogRepository(conn)
    await blog_repository.initialise()

    info['aiosqlite_conn'] = conn
    ...

async def on_shutdown(scope, info, request):
    conn: aiosqlite.Connection = info['aiosqlite_conn']
    await conn.close()

def create_application(config):

    app = Application(
        info=dict(config=config),
        startup_handlers=[on_startup],
        shutdown_handlers=[on_shutdown]
    )

    return app

```

Now we have a repository we can look at how jinja2 provides templating.

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
to specify where our templates can be found. In this case they will be in a
folder called `templates` at the same level as the above file. We also setup
automatic escaping for `.html` and `.xml` files to stop a malicious user
injecting html. Finally we enable asynchronous support.

After creating the environment we simply add it to the bareASGI application with
`bareasgi_jinja2.add_jinja2`.

## Templates

Typically all templates in a jinja2 application inherit from a *base* template.
Here is the basic layout we want.

```html
<!DOCTYPE html>
<html>
<head>
    {% block head %}

    <title>{{title}}</title>

    {% endblock %}
</head>
<body>
{% block content %}
{% endblock %}

</body>
</html>
```

The `{% block %} .. {% endblock %}` are where we can add content for the header
and the body.

Rather than leave this as an embarrassingly unstyled page we can add a styling
framework. Here we use [bootstrap](https://getbootstrap.com/).

```html
<!DOCTYPE html>
<html lang="en">
<head>
    {% block head %}

    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    
    <title>{{title}}</title>

    <!-- Use Bootstrap for styling -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">

    {% endblock %}
</head>
<body>
{% block content %}
{% endblock %}

    <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>

</body>
</html>
```

The jinja2 template will be passed a dictionary of the data to be displayed.
Our *index* page will be passed the `title` for the header, and
a list of the ten latest `posts`.

The template will look like this:

```html
{% extends "base.html" %}

{% block content %}
<div class="container">
    <h1>Blog</h1>

    {% if posts %}

    <dl>
        {% for post in posts %}

        <dt>
            {{ post['title']}}
        </dt>
        <dd>
            {{ post['description']}}

            [
            <a href="/read.html?id={{ post['id'] }}">read</a>,
            <a href="/update.html?id={{ post['id'] }}">edit</a>,
            <a href="/delete.html?id={{ post['id'] }}">delete</a>
            ]

        </dt>

        {% endfor %}
    </dl>
    {% endif %}

    <p><a href="/create.html">Create</a> a new post</p>
</div>
{% endblock %}
```

We can see this template `extends` from the base template which we defined
earlier.

Then we provide the `content` block. The `<div class="container">` applies the
basic styling for the page. Then we check if the `posts` variable passed into
the template has any values with `{% if posts %}`. If it does we iterate over
each post with `{% for post in posts %}` to create a list, including links for
viewing, editing and deleting.

Finally we provide a link to create a new post.

The other templates work in a similar manner.

## Controller

We create a controller class to define the route handlers. The code for the
controller can be found [here](bareasgi_blog/blog_controller.py).

The class takes the repository at initialisation.

```python
class BlogController:

    def __init__(self, repository: BlogRepository) -> None:
        self._repository = repository
    
    ...
```

The route handlers take the same arguments as standard route handlers, by they
are decorated with `@bareasgi_jinja2.template("template.html")` and they return
a dictionary of variables for the template to use.

### Index

Here is the index page route handler:

```python
    @bareasgi_jinja2.template('index.html')
    async def index(self, scope, info, matches, content):
        last_ten_posts = await self._repository.read_many(
            ['title', 'description'],
            'created',
            False,
            10
        )
        return {
            'title': 'blog',
            'posts': last_ten_posts
        }
```

Note how the keys of the returned dictionary match the variable names in the
template.

Finally we need to register the route. The controller has a convenience method
for this:

```python
    def add_routes(self, app: Application) -> None:
        app.http_router.add(
            {'GET'},
            '/index.html',
            self._index
        )
        ...
```

It is not necessary to add the `.html`, but it seems consistent.

### Create & Edit

The create and edit handlers can reuse the same template.

```html
{% extends "base.html" %}

{% set title = "New blog entry" %}

{% block content %}
<div class="container">
    <h1>New Blog Entry</h1>

    <form action="{{ action }}" method="post">

        {% if action != '/create.html' %}
        <input type="hidden" name="id" value="{{ blog_entry['id'] }}">
        {% endif %}

        <div class="form-group">
            <label for"titleInput">Title</label>
            <input type="text" class="form-control" id="titleInput" name="title" value="{{ blog_entry['title'] }}">
        </div>

        <div class="form-group">
            <label for"descriptionInput">Description</label>
            <textarea class="form-control" id="descriptionInput" name="description" rows="3">{{ blog_entry['description'] }}</textarea>
        </div>

        <div class="form-group">
            <label for"contentInput">Content</label>
            <textarea class="form-control" id="contentInput" name="content" rows="10">{{ blog_entry['content'] }}</textarea>
        </div>

        <button type="submit" class="btn btn-primary">Save</button>

    </form>

</div>
{% endblock %}
```

We pass in the `action` endpoint as one of the parameters. If we are not creating
(`{% if action != '/create.html' %})` a hidden input field holds the `id` of
the post which then gets returned with the rest of the post data.

The create handler is very simple.

```python
    @bareasgi_jinja2.template('edit.html')
    async def create(self, scope, info, matches, content):
        return {
            'action': '/create.html',
            'blog_entry': {
                'title': '',
                'description': '',
                'content': '',
            }
        }
```

When the form is *posted* the request is handled as follows:

```python
    async def save_create(self, scope, info, matches, content):
        try:
            text = await text_reader(content)
            args = dict(parse_qsl(text))

            id_ = await self._repository.create(**args)
            href = f'/read.html?id={id_}'

            return 303, [(b'location', href.encode())]
        except:  # pylint: disable=bare-except
            return 500
```

The form will post a `content-type` of `application/x-www-form-urlencoded` which
is read with the asynchronous `text_reader` and parsed by the standard library
function [`urllib.parse.parse_qsl`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.parse_qsl). Once the data has been decoded, this
is saved in the repository. If all goes to plan an id is returned and the
request handler returns a 303 redirect with the read location of the post.

The route handlers can now be added to the application.

```python
        app.http_router.add(
            {'GET'},
            '/create.html',
            self.create
        )
        app.http_router.add(
            {'POST'},
            '/create.html',
            self.save_create
        )
```


The update handler must first load the selected entry.

```python
    @bareasgi_jinja2.template('edit.html')
    async def update(self, scope, info, matches, content):
        args = dict(parse_qsl(scope['query_string'] or b''))
        id_ = int(args[b'id'])
        blog_entry = await self._repository.read_by_id(id_, None)
        return {
            'action': f'/update.html?id={id_}',
            'blog_entry': blog_entry
        }
```

Note how it finds the `id` to be found in the query string of the url. In
the template file we made the link `<a href=/update.html?id={{id}}>`.

Finally we need to save the update.

```python
    async def _save_update(self, scope, info, matches, content):
        try:
            text = await text_reader(content)
            args = dict(parse_qsl(text))
            id_ = int(args.pop('id'))

            await self._repository.update(id_, **args)
            href = f'/read.html?id={id_}'

            return 303, [(b'location', href.encode())]
        except:  # pylint: disable=bare-except
            return 500
```

## Wrapping up

Take a look at [`app.py`](bareasgi_blog/app.py) to see how the controller gets
wired in to the application
and [`server.py`](bareasgi_blog/server.py)
to see how the application is launched.