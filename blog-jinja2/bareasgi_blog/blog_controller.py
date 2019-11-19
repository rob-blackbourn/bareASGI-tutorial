"""Blog jinja2 controller"""

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
import bareasgi_jinja2

from .blog_repository import BlogRepository


class BlogController:
    """BlogController"""

    def __init__(self, repository: BlogRepository) -> None:
        self._repository = repository

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
            '/index.html',
            self._index
        )
        app.http_router.add(
            {'GET'},
            '/create.html',
            self._create
        )
        app.http_router.add(
            {'POST'},
            '/create.html',
            self._save_create
        )
        app.http_router.add(
            {'GET'},
            '/read.html',
            self._read
        )
        app.http_router.add(
            {'GET'},
            '/update.html',
            self._update
        )
        app.http_router.add(
            {'POST'},
            '/update.html',
            self._save_update
        )
        app.http_router.add(
            {'GET'},
            '/delete.html',
            self._delete
        )

    async def _index_redirect(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpResponse:
        """Redirect to the index"""
        return 303, [(b'Location', b'/index.html')]

    @bareasgi_jinja2.template('index.html')
    async def _index(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> Dict[str, Any]:
        latest_ten_entries = await self._repository.read_many(
            ['title', 'description'],
            'created',
            False,
            10
        )
        return {
            'title': 'blog',
            'posts': latest_ten_entries
        }

    @bareasgi_jinja2.template('edit.html')
    async def _create(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> Dict[str, Any]:
        return {
            'action': '/create.html',
            'blog_entry': {
                'title': '',
                'description': '',
                'content': '',
            }
        }

    async def _save_create(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            content: Content
    ) -> HttpResponse:
        try:
            text = await text_reader(content)
            args = dict(parse_qsl(text))

            id_ = await self._repository.create(**args)
            href = f'/read.html?id={id_}'

            return 303, [(b'location', href.encode())]
        except:  # pylint: disable=bare-except
            return 500

    @bareasgi_jinja2.template('read.html')
    async def _read(
            self,
            scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> Dict[str, Any]:
        args = dict(parse_qsl(scope['query_string'] or b''))
        id_ = int(args[b'id'])
        blog_entry = await self._repository.read_by_id(id_, None)
        return {'blog_entry': blog_entry}

    @bareasgi_jinja2.template('edit.html')
    async def _update(
            self,
            scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> Dict[str, Any]:
        args = dict(parse_qsl(scope['query_string'] or b''))
        id_ = int(args[b'id'])
        blog_entry = await self._repository.read_by_id(id_, None)
        return {
            'action': f'/update.html?id={id_}',
            'blog_entry': blog_entry
        }

    async def _save_update(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            content: Content
    ) -> HttpResponse:
        try:
            text = await text_reader(content)
            args = dict(parse_qsl(text))
            id_ = int(args.pop('id'))

            await self._repository.update(id_, **args)
            href = f'/read.html?id={id_}'

            return 303, [(b'Location', href.encode())]
        except:  # pylint: disable=bare-except
            return 500

    async def _delete(
            self,
            scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpResponse:
        try:
            args = dict(parse_qsl(scope['query_string'] or b''))
            id_ = int(args[b'id'])
            await self._repository.delete(id_)
            return 303, [(b'Location', b'/index.html')]
        except:  # pylint: disable=bare-except
            return 500
