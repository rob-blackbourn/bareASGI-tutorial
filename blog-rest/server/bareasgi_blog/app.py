"""Application"""

from functools import partial
import sqlite3

import aiosqlite
from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    Message,
    HttpResponse
)
import bareasgi_jinja2
import jinja2
import pkg_resources

from .blog_repository import BlogRepository
from .blog_rest_controller import BlogRestController

async def _on_startup(
        app: Application,
        path_prefix: str,
        _scope: Scope,
        info: Info,
        _request: Message
) -> None:
    conn = await aiosqlite.connect(
        ':memory:',
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
    )

    blog_repository = BlogRepository(conn)
    await blog_repository.initialise()

    blog_controller = BlogRestController(blog_repository, path_prefix)
    blog_controller.add_routes(app)
    info['aiosqlite_conn'] = conn

async def _on_shutdown(
        _scope: Scope,
        info: Info,
        _request: Message
) -> None:
    conn: aiosqlite.Connection = info['aiosqlite_conn']
    await conn.close()

def create_application(path_prefix: str) -> Application:
    """Create the application"""
    api_path_prefix = path_prefix + '/api'
    ui_path_prefix = path_prefix + '/ui'
    templates = pkg_resources.resource_filename(__name__, "templates")

    app = Application(info={})


    app.startup_handlers.append(partial(_on_startup, app, api_path_prefix))
    return app
