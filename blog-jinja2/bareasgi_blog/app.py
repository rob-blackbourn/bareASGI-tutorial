"""Application"""

from functools import partial
import sqlite3
from typing import Mapping, Any

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
from .blog_jinja2_controller import BlogJinja2Controller


async def _on_startup(
        app: Application,
        path_prefix: str,
        _scope: Scope,
        info: Info,
        _request: Message
) -> None:
    sqlite_filename = info['config']['sqlite']['filename']

    conn = await aiosqlite.connect(
        sqlite_filename,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
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


async def _index_redirect(
        redirect_path: str,
        _scope: Scope,
        _info: Info,
        _matches: RouteMatches,
        _content: Content
) -> HttpResponse:
    """Redirect to the example"""
    return 303, [(b'Location', redirect_path.encode())]


def create_application(config: Mapping[str, Any]) -> Application:
    """Create the application"""
    path_prefix = config['app']['path_prefix']

    api_path_prefix = path_prefix + '/api'
    ui_path_prefix = path_prefix + '/ui'
    templates = pkg_resources.resource_filename(__name__, "templates")

    app = Application(info=dict(config=config))
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
        enable_async=True
    )
    bareasgi_jinja2.add_jinja2(app, env)
    blog_jinja2_controller = BlogJinja2Controller(
        ui_path_prefix, api_path_prefix)
    blog_jinja2_controller.add_routes(app)

    app.http_router.add(
        {'GET'}, '/', partial(_index_redirect, ui_path_prefix + '/index.html'))

    app.startup_handlers.append(partial(_on_startup, app, api_path_prefix))
    return app
