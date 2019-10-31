"""Blog jinja2 controller"""

from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpRequestCallback
)
import bareasgi_jinja2

class BlogJinja2Controller:
    """BlogJinja2Controller"""

    def __init__(self, ui_path_prefix: str, api_path_prefix) -> None:
        self._ui_path_prefix = ui_path_prefix
        self._api_path_prefix = api_path_prefix

    def add_routes(self, app: Application) -> None:
        """Add routes to the application

        :param app: The ASGI application
        :type app: Application
        """
        app.http_router.add(
            {'GET'},
            self._ui_path_prefix + '/index.html',
            self._index
        )

    @bareasgi_jinja2.template('index.html')
    async def _index(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpRequestCallback:
        return {'api_path': self._api_path_prefix}

    @bareasgi_jinja2.template('create.html')
    async def _create(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpRequestCallback:
        return {'api_path': self._path_prefix}

    @bareasgi_jinja2.template('read.html')
    async def _read(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpRequestCallback:
        return {'api_path': self._path_prefix}

    @bareasgi_jinja2.template('update.html')
    async def _update(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpRequestCallback:
        return {'api_path': self._path_prefix}

    @bareasgi_jinja2.template('delete.html')
    async def _delete(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpRequestCallback:
        return {'api_path': self._path_prefix}
