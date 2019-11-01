"""Blog controller"""

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

from .blog_repository import BlogRepository
from .jwt_authenticator import JwtAuthenticator


class BlogController:
    """BlogController"""

    def __init__(
            self,
            repository: BlogRepository,
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
            '/blog/index',
            mw(self._authenticator, handler=self._index)
        )
        app.http_router.add(
            {'GET'},
            '/blog/create',
            mw(self._authenticator, handler=self._create)
        )
        app.http_router.add(
            {'POST'},
            '/blog/create',
            mw(self._authenticator, handler=self._save_create)
        )
        app.http_router.add(
            {'GET'},
            '/blog/read',
            mw(self._authenticator, handler=self._read)
        )
        app.http_router.add(
            {'GET'},
            '/blog/update',
            mw(self._authenticator, handler=self._update)
        )
        app.http_router.add(
            {'POST'},
            '/blog/update',
            mw(self._authenticator, handler=self._save_update)
        )
        app.http_router.add(
            {'GET'},
            '/blog/delete',
            mw(self._authenticator, handler=self._delete)
        )


    @bareasgi_jinja2.template('blog/index.html')
    async def _index(
            self,
            _scope: Scope,
            info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> Dict[str, Any]:
        jwt = info['jwt']
        latest_ten_entries = await self._repository.read_many(
            None,
            'created',
            False,
            10
        )
        return {
            'blog_entries': latest_ten_entries,
            'role': jwt['role'],
            'username': jwt['sub'],
            'user_id': jwt['user_id']
        }

    @bareasgi_jinja2.template('blog/edit.html')
    async def _create(
            self,
            _scope: Scope,
            info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> Dict[str, Any]:
        jwt = info['jwt']
        if jwt['role'] not in ['admin', 'blogger']:
            raise RuntimeError("Unauthorized")

        return {
            'action': '/blog/create',
            'blog_entry': {
                'title': '',
                'description': '',
                'content': '',
            },
            'role': jwt['role'],
            'username': jwt['sub'],
            'user_id': jwt['user_id']
        }

    async def _save_create(
            self,
            _scope: Scope,
            info: Info,
            _matches: RouteMatches,
            content: Content
    ) -> HttpResponse:
        try:
            jwt = info['jwt']
            if jwt['role'] not in ['admin', 'blogger']:
                return 401

            text = await text_reader(content)
            args = dict(parse_qsl(text))
            args['user_id'] = jwt['user_id']

            id_ = await self._repository.create(**args)
            href = f'/blog/read?id={id_}'

            return 303, [(b'Location', href.encode())]
        except:  # pylint: disable=bare-except
            return 500

    @bareasgi_jinja2.template('blog/read.html')
    async def _read(
            self,
            scope: Scope,
            info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> Dict[str, Any]:
        jwt = info['jwt']
        args = dict(parse_qsl(scope['query_string'] or b''))
        blog_entry_id = int(args[b'id'])
        blog_entry = await self._repository.read_by_id(blog_entry_id, None)
        return {
            'blog_entry': blog_entry,
            'role': jwt['role'],
            'username': jwt['sub'],
            'user_id': jwt['user_id']
        }

    @bareasgi_jinja2.template('blog/edit.html')
    async def _update(
            self,
            scope: Scope,
            info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> Dict[str, Any]:
        jwt = info['jwt']
        if jwt['role'] not in ['admin', 'blogger']:
            raise RuntimeError("Unauthorized")

        args = dict(parse_qsl(scope['query_string'] or b''))
        blog_entry_id = int(args[b'id'])
        blog_entry = await self._repository.read_by_id(blog_entry_id, None)
        if blog_entry is None:
            raise RuntimeError("Not found")
        if blog_entry['user_id'] != jwt['id']:
            raise RuntimeError("Unauthorized")

        return {
            'action': f'/blog/update?id={blog_entry_id}',
            'blog_entry': blog_entry,
            'role': jwt['role'],
            'username': jwt['sub'],
            'user_id': jwt['user_id']
        }

    async def _save_update(
            self,
            _scope: Scope,
            info: Info,
            _matches: RouteMatches,
            content: Content
    ) -> HttpResponse:
        try:
            jwt = info['jwt']

            text = await text_reader(content)
            args = dict(parse_qsl(text))
            blog_entry_id = int(args.pop('id'))

            original_blog_entry = await self._repository.read_by_id(blog_entry_id, ['user_id'])
            if original_blog_entry is None or original_blog_entry['user_id'] != jwt['user_id']:
                return 401

            await self._repository.update(blog_entry_id, **args)
            href = f'/blog/read?id={blog_entry_id}'

            return 303, [(b'Location', href.encode())]
        except:  # pylint: disable=bare-except
            return 500

    async def _delete(
            self,
            scope: Scope,
            info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpResponse:
        try:
            jwt = info['jwt']
            args = dict(parse_qsl(scope['query_string'] or b''))
            blog_entry_id = int(args[b'id'])

            original_blog_entry = await self._repository.read_by_id(blog_entry_id, ['user_id'])
            if original_blog_entry is None or original_blog_entry['user_id'] != jwt['user_id']:
                return 401

            await self._repository.delete(blog_entry_id)
            return 303, [(b'Location', b'/blog/index')]
        except:  # pylint: disable=bare-except
            return 500
