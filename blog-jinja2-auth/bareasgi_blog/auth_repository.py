"""Auth Repository"""

import hashlib
from typing import Any, Dict, List, Optional, Tuple
import uuid

import aiosqlite

from .repository import Repository


class AuthRepository(Repository):
    "Auth Repository"""

    def __init__(
            self,
            conn: aiosqlite.Connection,
            admin_username: str,
            admin_password: str
    ) -> None:
        super().__init__(conn, 'users')
        self._admin_username = admin_username
        self._admin_password = admin_password

    async def create(self, **kwargs) -> int:
        inserts = dict(kwargs)
        password = inserts.pop('password')
        hash_, salt = self._hash_password(password)
        inserts['hash'] = hash_
        inserts['salt'] = salt
        return await super().create(**inserts)

    async def read_by_username(
            self,
            username: str
    ) -> Optional[Dict[str, Any]]:
        """Read by username"""
        return await self.read_by_column('username', username, None)

    async def initialise(self) -> None:
        await self._conn.execute("""
CREATE TABLE IF NOT EXISTS users
(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL,

    UNIQUE(username)
)
""")
        await self._conn.commit()

        admins = await self.read_many_by_role('admin', 1)
        if not admins:
            await self._create_admin_user()

    async def read_many_by_role(
            self,
            role: str,
            limit: int
    ) -> List[Dict[str, Any]]:
        """Read many by role"""
        return await self.read_many_by_column(
            'role',
            role,
            None,
            'username',
            True,
            limit
        )

    async def is_valid_password(self, username: str, password: str) -> bool:
        """Check a password"""
        auth = await self.read_by_column('username', username, ['hash', 'salt'])
        if auth is None:
            return False
        hash_ = self._create_hash(password, auth['salt'])
        return auth['hash'] == hash_

    async def change_password(self, username: str, password: str) -> bool:
        """Change a users password"""
        hash_, salt = self._hash_password(password)
        user = await self.read_by_username(username)
        if user is None:
            return False
        return await self.update(user['id'], hash=hash_, salt=salt)

    async def _create_admin_user(self) -> None:
        admin = {
            'username': self._admin_username,
            'password': self._admin_password,
            'role': 'admin'
        }
        await self.create(**admin)

    @classmethod
    def _hash_password(cls, password: str) -> Tuple[str, str]:
        salt = uuid.uuid4().hex
        hash_ = cls._create_hash(password, salt)
        return hash_, salt

    @classmethod
    def _create_hash(cls, password, salt) -> str:
        return hashlib.sha512((password + salt).encode()).hexdigest()
