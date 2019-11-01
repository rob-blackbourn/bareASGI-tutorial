"""Blog Repository"""

from datetime import datetime
from typing import (
    Any,
    Dict,
    List,
    Optional
)

import aiosqlite

from bareasgi_blog.repository import Repository, make_unpacker

class BlogRepository(Repository):
    """"BlogRepository"""

    def __init__(self, conn: aiosqlite.Connection) -> None:
        super().__init__(conn, 'blog_entries')

    async def create(self, **kwargs) -> int:
        now = datetime.utcnow()
        inserts = {
            'created': now,
            'updated': now
        }
        inserts.update(kwargs)
        return await super().create(**inserts)

    async def read_by_column(
            self,
            column: str,
            value: Any,
            columns: Optional[List[str]]
    ) -> Optional[Dict[str, Any]]:
        """Read a record by a column value"""
        stmt = f"""
SELECT users.username,{','.join(f'{self.table}.{column}' for column in columns) if columns else '*'}
FROM {self.table}
JOIN users
ON users.id = {self.table}.user_id
WHERE {self.table}.{column} = ?
"""
        args = (value,)

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            row = await cur.fetchone()
            if row is None:
                return None
            result = make_unpacker(cur)(row)
            return result

    async def read_many(
            self,
            columns: Optional[List[str]],
            order_by_column: str,
            order_by_ascending: bool,
            limit: int
    ) -> List[Dict[str, Any]]:
        """Read many records"""
        stmt = f"""
SELECT users.username,{','.join(f'{self.table}.{column}' for column in columns) if columns else '*'}
FROM {self.table}
JOIN users
ON users.id = {self.table}.user_id
ORDER BY {order_by_column} {'ASC' if order_by_ascending else 'DESC'}
LIMIT ?
"""
        args = (limit,)

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            unpack = make_unpacker(cur)
            values = [unpack(row) async for row in cur]
            return values

    async def read_between(
            self,
            start_date: datetime,
            end_date: datetime,
            columns: Optional[List[str]],
            limit: int
    ) -> List[Dict[str, Any]]:
        """Read between the start and end date

        :param start_date: The start date
        :type start_date: datetime
        :param end_date: The end date
        :type end_date: datetime
        :param columns: The columns to return
        :type columns: Optional[List[str]]
        :param limit: The maximum number of entries to return
        :type limit: int
        :return: The entries found
        :rtype: List[Dict[str, Any]]
        """
        return await self.read_between_column(
            'created',
            start_date,
            end_date,
            columns,
            'created',
            False,
            limit
        )

    async def update(
        self,
        id_: int,
        **kwargs
    ) -> bool:
        updates = {
            'updated': datetime.utcnow()
        }
        updates.update(kwargs)
        return await super().update(id_, **updates)


    async def initialise(self) -> None:
        await self._conn.execute(f"""
CREATE TABLE IF NOT EXISTS {self.table}
(
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NULL,
    content TEXT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,

    UNIQUE(title)
)
""")
        await self._conn.commit()
