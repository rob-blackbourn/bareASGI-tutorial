"""Auth Controller"""

import logging
from typing import Any, Dict
from urllib.parse import parse_qsl

from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    text_reader
)
from bareasgi.middleware import mw
import bareasgi_jinja2

from .auth_repository import AuthRepository
from .jwt_authenticator import JwtAuthenticator

LOGGER = logging.getLogger(__name__)

class AuthController:
    """AuthController"""

    def __init__(
            self,
            repository: AuthRepository,
            authenticator: JwtAuthenticator
    ) -> None:
        self._repository = repository
        self._authenticator = authenticator

    def add_routes(self, app: Application) -> None:
        """Add routes to the application

        :param app: The ASGI application
        :type app: Application
        """
        app.http_router.add(
            {'GET'},
            '/',
            self._index_redirect
        )
        app.http_router.add(
            {'GET'},
            '/auth/register',
            self._register
        )
        app.http_router.add(
            {'POST'},
            '/auth/register',
            self._save_register
        )
        app.http_router.add(
            {'GET'},
            '/auth/login',
            self._login
        )
        app.http_router.add(
            {'POST'},
            '/auth/login',
            self._approve_login
        )
        app.http_router.add(
            {'GET'},
            '/auth/admin',
            mw(self._authenticator, handler=self._admin)
        )
        app.http_router.add(
            {'GET'},
            '/auth/grant',
            mw(self._authenticator, handler=self._grant)
        )
        app.http_router.add(
            {'GET'},
            '/auth/change-password',
            self._change_password
        )
        app.http_router.add(
            {'POST'},
            '/auth/change-password',
            self._save_change_password
        )

    async def _index_redirect(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpResponse:
        """Redirect to the index"""
        return 303, [(b'Location', b'auth/login')]

    @bareasgi_jinja2.template('auth/register.html')
    async def _register(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> Dict[str, Any]:
        return {}

    async def _save_register(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            content: Content
    ) -> HttpResponse:
        try:
            text = await text_reader(content)
            args = dict(parse_qsl(text))
            role = 'reader'
            args['role'] = role

            is_ok = await self._repository.create(**args)
            if not is_ok:
                raise RuntimeError("Failed to register")

            set_cookie = self._authenticator.create_token(args['username'], role)

            return (
                303,
                [
                    (b'set-cookie', set_cookie),
                    (b'location', b'/blog/index')
                ]
            )
        except:  # pylint: disable=bare-except
            LOGGER.exception('save register failed')
            return 500


    @bareasgi_jinja2.template('auth/login.html')
    async def _login(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> Dict[str, Any]:
        return {}


    async def _approve_login(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            content: Content
    ) -> HttpResponse:
        try:
            text = await text_reader(content)
            args = dict(parse_qsl(text))

            username = args['username']
            if not await self._repository.is_valid_password(username, args['password']):
                return 303, [(b'Location', b'/auth/login')]

            user = await self._repository.read_by_username(username)
            if user is None:
                raise RuntimeError("Failed to find user")

            set_cookie = self._authenticator.create_token(username, user['role'])
            location = b'/auth/admin' if user['role'] == 'admin' else b'/blog/index'

            return (
                303,
                [
                    (b'set-cookie', set_cookie),
                    (b'Location', location)
                ]
            )
        except:  # pylint: disable=bare-except
            LOGGER.exception('login failed')
            return 500

    @bareasgi_jinja2.template('auth/admin.html')
    async def _admin(
            self,
            _scope: Scope,
            info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> Dict[str, Any]:
        jwt = info.get('jwt')
        if jwt is None or not jwt.get('role') == 'admin':
            raise RuntimeError("Unauthenticated")

        users = await self._repository.read_many(
            ['username', 'role'],
            'username',
            True,
            10000
        )
        return {'users': users}

    async def _grant(
            self,
            scope: Scope,
            info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpResponse:
        try:
            jwt = info['jwt']
            if jwt.get('role') != 'admin':
                return 401
            
            args: Dict[bytes, Any] = dict(parse_qsl(scope['query_string']))
            id_ = int(args[b'id'])
            role = args[b'role'].decode()

            is_ok = await self._repository.update(id_, role=role)
            if not is_ok:
                raise RuntimeError("Failed to update role")

            return 303, [(b'Location', b'/auth/admin')]
        except:  # pylint: disable=bare-except
            LOGGER.exception('grant failed')
            return 500


    @bareasgi_jinja2.template('auth/change-password.html')
    async def _change_password(
            self,
            _scope: Scope,
            info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> Dict[str, Any]:
        jwt = info['jwt']
        return {'username': jwt['sub']}

    async def _save_change_password(
            self,
            scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpResponse:
        try:
            args: Dict[bytes, Any] = dict(parse_qsl(scope['query_string']))
            username = args[b'username'].decode()
            old_password = args[b'old_password'].decode()
            new_password = args[b'new_password'].decode()

            if not await self._repository.is_valid_password(username, old_password):
                return 303, [(b'location', b'/auth/change-password')]

            is_ok = await self._repository.change_password(username, new_password)
            if not is_ok:
                raise RuntimeError("Failed to change password")

            return 303, [(b'Location', b'/blog/index')]
        except:  # pylint: disable=bare-except
            LOGGER.exception('grant failed')
            return 500
