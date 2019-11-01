"""Application"""

from datetime import timedelta
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

from .auth_repository import AuthRepository
from .token_manager import TokenManager
from .jwt_authenticator import JwtAuthenticator
from .auth_controller import AuthController
from .blog_repository import BlogRepository
from .blog_controller import BlogController

from .utils import parse_timedelta


async def _on_startup(
        app: Application,
        _scope: Scope,
        info: Info,
        _request: Message
) -> None:
    config = info['config']

    sqlite_filename = config['sqlite']['filename']

    conn = await aiosqlite.connect(
        sqlite_filename,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )

    admin_username = config['auth']['admin_username']
    admin_password = config['auth']['admin_password']
    auth_repository = AuthRepository(conn, admin_username, admin_password)
    await auth_repository.initialise()

    auth_config = config['authentication']
    token_manager = TokenManager(
        auth_config['secret'],
        parse_timedelta(auth_config['token_expiry']) or timedelta(hours=1),
        auth_config['issuer'],
        auth_config['cookie_name'],
        auth_config['domain'],
        auth_config['path'],
        parse_timedelta(auth_config['max_age']) or timedelta(days=1)
    )

    authenticator = JwtAuthenticator(
        auth_repository,
        token_manager,
        '/auth/login',
        auth_config['login_expiry']
    )

    auth_controller = AuthController(auth_repository, authenticator)
    auth_controller.add_routes(app)

    blog_repository = BlogRepository(conn)
    await blog_repository.initialise()

    blog_controller = BlogController(blog_repository, authenticator)
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
