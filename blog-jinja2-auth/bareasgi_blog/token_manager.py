"""
Token Manager
"""

from datetime import datetime, timedelta
import logging
from typing import Mapping, Any, List, Optional

from baretypes import Header
from bareutils import encode_set_cookie
import bareutils.header as header
import jwt

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


class TokenManager:
    """Token Manager"""

    def __init__(
            self,
            secret: str,
            token_expiry: timedelta,
            issuer: str,
            cookie_name: str,
            domain: str,
            path: str,
            max_age: timedelta
    ) -> None:
        """Initialise the token manager

        :param secret: The secret shared by all authenticators
        :type secret: str
        :param token_expiry: The time before a token requires renewing.
        :type token_expiry: timedelta
        :param issuer: The cookie issuer
        :type issuer: str
        :param cookie_name: The name of the cookie in which the token is stored.
        :type cookie_name: str
        :param domain: The cookie domain
        :type domain: str
        :param path: The cookie path
        :type path: str
        :param max_age: The cookie maximum age
        :type max_age: timedelta
        """
        self.secret = secret
        self.token_expiry = token_expiry
        self.issuer = issuer
        self.cookie_name = cookie_name.encode()
        self.domain = domain.encode()
        self.path = path.encode()
        self.max_age = max_age

    def encode(
            self,
            username: str,
            now: datetime,
            issued_at: datetime,
            role: str
    ) -> bytes:
        """Encode the cookie as a JSON web token

        :param username: The username
        :type username: str
        :param now: The current time in UTC
        :type now: datetime
        :param issued_at: The time the cookie was issued
        :type issued_at: datetime
        :param role: The role
        :type role: str
        :return: The information encoded as a JSON web token
        :rtype: bytes
        """
        expiry = now + self.token_expiry
        logger.debug("Token will expire at %s", expiry)
        payload = {
            'iss': self.issuer,
            'sub': username,
            'exp': expiry,
            'iat': issued_at,
            'role': role
        }
        return jwt.encode(payload, key=self.secret)

    def decode(self, token: bytes) -> Mapping[str, Any]:
        """Decode the JSON web token

        :param token: The token
        :type token: bytes
        :return: The decoded token
        :rtype: Mapping[str, Any]
        """
        payload = jwt.decode(
            token,
            key=self.secret,
            options={'verify_exp': False}
        )
        payload['exp'] = datetime.utcfromtimestamp(payload['exp'])
        payload['iat'] = datetime.utcfromtimestamp(payload['iat'])
        return payload

    def get_token_from_headers(self, headers: List[Header]) -> Optional[bytes]:
        """Get the token from the headers or None if not present

        :param headers: The headers
        :type headers: List[Header]
        :return: The token of None if not present
        :rtype: Optional[bytes]
        """
        tokens = header.cookie(headers).get(self.cookie_name)
        if tokens is None or not tokens:
            return None
        if len(tokens) > 1:
            logger.warning('Multiple tokens in header - using first')
        token = tokens[0]
        return token

    def get_jwt_payload_from_headers(self, headers: List[Header]) -> Optional[Mapping[str, Any]]:
        """Gets the JSON web token from the headers of None if not present

        :param headers: The headers
        :type headers: List[Header]
        :return: The payload of the JSON web token if found, otherwise None.
        :rtype: Optional[Mapping[str, Any]]
        """
        token = self.get_token_from_headers(headers)
        payload = self.decode(token) if token is not None else None
        return payload

    def generate_cookie(self, username: str, role: str) -> bytes:
        """Generate a new cookie

        :param username: The username
        :type username: str
        :return: The generated cookie
        :rtype: bytes
        """
        now = datetime.utcnow()
        token = self.encode(username, now, now, role)
        return self.make_cookie(token)

    def make_cookie(self, token: bytes) -> bytes:
        """Make a cookie from a token

        :param token: The token
        :type token: bytes
        :return: A cookie that can be used in an HTTP header
        :rtype: bytes
        """
        cookie = encode_set_cookie(
            self.cookie_name,
            token,
            max_age=self.max_age,
            domain=self.domain,
            path=self.path,
            http_only=True
        )
        return cookie
