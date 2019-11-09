"""Application"""

from functools import partial
import sqlite3

import aiosqlite
from bareasgi import (
    Application,
    Scope,
    Info,
    Message
)
from bareasgi_cors import CORSMiddleware

from .blog_repository import BlogRepository
from .blog_controller import BlogController


async def _on_startup(
        app: Application,
        _scope: Scope,
        info: Info,
        _request: Message
) -> None:
    conn = await aiosqlite.connect(
        ':memory:',
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


def create_application() -> Application:
    """Create the application"""
    cors_middleware = CORSMiddleware(
        # allow_methods=ALL_METHODS
    )
    app = Application(info={}, middlewares=[cors_middleware])
    app.startup_handlers.append(partial(_on_startup, app))
    app.shutdown_handlers.append(_on_shutdown)
    return app
