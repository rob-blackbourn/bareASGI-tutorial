"""Blog REST Controller"""

from datetime import datetime, timedelta
import json
from typing import Optional
from urllib.parse import parse_qsl

from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse
)
from bareutils import (
    text_reader,
    text_writer
)
import bareutils.header as header

from .blog_repository import BlogRepository


class DateEncoder(json.JSONEncoder):
    """JSONEncoder with date support"""

    def default(self, obj):  # pylint: disable=method-hidden,arguments-differ
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def _is_form_data(scope: Scope) -> bool:
    content_type, *_ = header.content_type(scope['headers']) or (None,)
    return content_type == b'application/x-www-form-urlencoded'


def _parse_date(value: Optional[bytes], default: datetime) -> datetime:
    return default if not value else datetime.fromisoformat(value.decode())


def _parse_int(value: Optional[bytes], default: int) -> int:
    return default if not value else int(value[0])


class BlogRestController:
    """BlogRestController"""

    def __init__(self, repository: BlogRepository, path_prefix: str) -> None:
        self._repository = repository
        self._path = f'{path_prefix}/blog_entry'

    def add_routes(self, app: Application) -> None:
        """Add routes to the application

        :param app: The ASGI application
        :type app: Application
        """
        app.http_router.add({'POST', 'OPTIONS'}, f'{self._path}', self._create)
        app.http_router.add({'GET'}, f'{self._path}/{{id:int}}', self._read)
        app.http_router.add({'GET'}, f'{self._path}', self._read_between)
        app.http_router.add({'POST', 'OPTIONS'}, f'{self._path}/{{id:int}}', self._update)
        app.http_router.add(
            {'DELETE', 'OPTIONS'},
            f'{self._path}/{{id:int}}',
            self._delete
        )

    async def _create(
            self,
            scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            content: Content
    ) -> HttpResponse:
        try:
            media_type, *_ = header.content_type(scope['headers'])
            if media_type != b'application/json':
                raise RuntimeError("Invalid media type")

            text = await text_reader(content)
            args = json.loads(text)

            id_ = await self._repository.create(**args)

            return (
                200,
                [(b'content-type', b'application/json')],
                text_writer(
                    json.dumps({
                        'id': id_,
                        'read': f'{self._path}/{id_}'
                    })
                )
            )
        except:  # pylint: disable=bare-except
            return 500

    async def _read(
            self,
            _scope: Scope,
            _info: Info,
            matches: RouteMatches,
            _content: Content
    ) -> HttpResponse:
        try:
            id_: Optional[int] = matches.get('id')
            if id_ is None:
                raise RuntimeError('Invalid id')

            entry = await self._repository.read_by_id(id_, None)
            if entry is None:
                return 404

            return (
                200,
                [(b'content-type', b'application/json')],
                text_writer(
                    json.dumps(
                        entry,
                        cls=DateEncoder
                    )
                )
            )
        except:  # pylint: disable=bare-except
            return 500

    async def _read_between(
            self,
            scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpResponse:
        try:
            query = dict(parse_qsl(scope['query_string'] or b''))

            end_date = _parse_date(query.get(b'to'), datetime.utcnow())
            start_date = _parse_date(
                query.get(b'from'), end_date - timedelta(5))
            limit = _parse_int(query.get(b'limit'), 20)

            entries = await self._repository.read_between(
                start_date,
                end_date,
                ['title', 'description'],
                limit
            )

            return (
                200,
                [(b'content-type', b'application/json')],
                text_writer(
                    json.dumps(
                        entries,
                        cls=DateEncoder
                    )
                )
            )
        except:  # pylint: disable=bare-except
            return 500

    async def _update(
            self,
            scope: Scope,
            _info: Info,
            matches: RouteMatches,
            content: Content
    ) -> HttpResponse:
        try:
            media_type, *_ = header.content_type(scope['headers'])
            if media_type != b'application/json':
                raise RuntimeError("Invalid media type")

            text = await text_reader(content)
            args = json.loads(text)

            id_ = matches.get('id')
            if not await self._repository.update(id_, **args):
                raise RuntimeError("Failed to update blog entry")

            return (
                200,
                [(b'content-type', b'application/json')],
                text_writer(
                    json.dumps({
                        'id': id_,
                        'read': f'{self._path}/{id_}'
                    })
                )
            )
        except:  # pylint: disable=bare-except
            return 500

    async def _delete(
            self,
            _scope: Scope,
            _info: Info,
            matches: RouteMatches,
            _content: Content
    ) -> HttpResponse:
        try:
            id_ = matches.get('id')
            if not await self._repository.delete(id_):
                raise RuntimeError("Failed to delete blog entry")
            return 204
        except:  # pylint: disable=bare-except
            return 500
