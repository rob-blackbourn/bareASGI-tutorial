"""Application"""

from functools import partial
import sqlite3
from typing import Mapping, Any

import aiosqlite
from bareasgi import (
    Application,
    Scope,
    Info,
    Message
)
import bareasgi_jinja2
import jinja2
import pkg_resources

from .blog_repository import BlogRepository
from .blog_controller import BlogController


async def _on_startup(
        app: Application,
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

    blog_controller = BlogController(blog_repository)
    blog_controller.add_routes(app)

    info['aiosqlite_conn'] = conn


async def _on_shutdown(
        _scope: Scope,
        info: Info,
        _request: Message
) -> None:
    conn: aiosqlite.Connection = info['aiosqlite_conn']
    await conn.close()


def create_application(config: Mapping[str, Any]) -> Application:
    """Create the application"""
    templates = pkg_resources.resource_filename(__name__, "templates")

    app = Application(info=dict(config=config))

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
        enable_async=True
    )
    bareasgi_jinja2.add_jinja2(app, env)

    app.startup_handlers.append(partial(_on_startup, app))
    return app
