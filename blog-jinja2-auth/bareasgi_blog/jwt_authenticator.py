"""
JWT Authenticator
"""

from datetime import datetime, timedelta
import logging
from typing import Optional

from baretypes import (
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    HttpRequestCallback
)
from bareutils import response_code

from .token_manager import TokenManager
from .auth_repository import AuthRepository

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


class JwtAuthenticator:
    """JTW authentication middleware"""

    def __init__(
            self,
            repository: AuthRepository,
            token_manager: TokenManager,
            authentication_path: str,
            login_expiry: timedelta
    ) -> None:
        """Initialise the JWT Authenticator"""
        self._repository = repository
        self._token_manager = token_manager
        self._authentication_path = authentication_path.encode()
        self._login_expiry = login_expiry

    async def _renew_cookie(
            self,
            token: bytes
    ) -> Optional[bytes]:

        payload = self._token_manager.decode(token)

        username: str = payload['sub']
        issued_at: datetime = payload['iat']
        role: str = payload['role']

        logger.debug(
            'Token renewal request: user=%s, iat=%s',
            username,
            issued_at
        )

        utc_now = datetime.utcnow()

        authentication_expiry = issued_at + self._login_expiry
        if utc_now > authentication_expiry:
            logger.debug(
                'Token expired for user %s issued at %s expired at %s',
                username,
                issued_at,
                authentication_expiry
            )
            return None

        user = await self._repository.read_by_username(username)
        if user is None or user['role'] not in ['admin', 'blogger', 'reader']:
            return None

        logger.debug('Token renewed for %s', user)
        token = self._token_manager.encode(username, utc_now, issued_at, role)
        logger.debug('Sending token %s', token)

        set_cookie = self._token_manager.make_cookie(token)

        return set_cookie

    def create_token(self, username: str, role: str) -> bytes:
        """Create a token"""
        now = datetime.utcnow()
        token = self._token_manager.encode(username, now, now, role)
        return self._token_manager.make_cookie(token)

    async def __call__(
            self,
            scope: Scope,
            info: Info,
            matches: RouteMatches,
            content: Content,
            handler: HttpRequestCallback
    ) -> HttpResponse:

        logger.debug('Jwt Authentication Request: %s', scope["path"])

        try:
            token = self._token_manager.get_token_from_headers(scope['headers'])
            if token is None:
                return response_code.FOUND, [(b'location', self._authentication_path)]

            now = datetime.utcnow()

            payload = self._token_manager.decode(token)
            if payload['exp'] > now:
                logger.debug('Cookie still valid')
                cookie = None
            else:
                logger.debug('Renewing cookie')
                cookie = await self._renew_cookie(token)
                if cookie is None:
                    return response_code.UNAUTHORIZED

            if info is None:
                info = dict()
            info['jwt'] = payload

            status, headers, body, pushes = await handler(scope, info, matches, content)

            if cookie:
                if headers is None:
                    headers = []
                headers.append((b"set-cookie", cookie))

            return status, headers, body, pushes

        except: # pylint: disable=bare-except
            logger.exception("JWT authentication failed")
            return response_code.INTERNAL_SERVER_ERROR
