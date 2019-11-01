"""Repository"""

from datetime import datetime
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple
)

import aiosqlite


def _make_unpacker(cur: aiosqlite.Cursor) -> Callable[[Tuple], Dict[str, Any]]:
    columns = [name for name, *_ in cur.description]
    return lambda row: dict(zip(columns, row))


class BlogRepository:
    """"Repository"""

    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    async def create(self, **kwargs) -> int:
        """Create a blog entry"""

        now = datetime.utcnow()
        inserts = {
            'created': now,
            'updated': now
        }
        inserts.update(kwargs)

        stmt = f"""
INSERT INTO blog_entries({','.join(inserts.keys())})
VALUES ({','.join('?' for _ in range(len(inserts)))})
"""
        args = tuple(inserts.values())

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            await self._conn.commit()
            return cur.lastrowid

    async def read_by_id(
            self,
            id_: int,
            columns: Optional[List[str]]
    ) -> Optional[Dict[str, Any]]:
        """Read a blog entry by id"""
        return await self.read_by_column('rowid', id_, columns)

    async def read_by_column(
            self,
            column: str,
            value: Any,
            columns: Optional[List[str]]
    ) -> Optional[Dict[str, Any]]:
        """Read a blog entry by a given column value"""
        stmt = f"""
SELECT rowid AS id,{','.join(columns) if columns else '*'}
FROM blog_entries
WHERE {column} = ?
"""
        args = (value,)

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            row = await cur.fetchone()
            if row is None:
                return None
            result = _make_unpacker(cur)(row)
            return result

    async def read_between(
            self,
            start_value: Any,
            end_value: Any,
            columns: Optional[List[str]],
            order_by: str,
            limit: int
    ) -> List[Dict[str, Any]]:
        """Read blog entries between two dates"""
        stmt = f"""
SELECT rowid AS id,{','.join(columns) if columns else '*'}
FROM blog_entries
WHERE created BETWEEN ? AND ?
ORDER BY {order_by}
LIMIT ?
"""
        args = (start_value, end_value, limit)

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            unpack = _make_unpacker(cur)
            values = [unpack(row) async for row in cur]
            return values

    async def read_many(
            self,
            columns: Optional[List[str]],
            order_by_column: str,
            order_by_ascending: bool,
            limit: int
    ) -> List[Dict[str, Any]]:
        """Read many blog entries"""
        stmt = f"""
SELECT rowid AS id,{','.join(columns) if columns else '*'}
FROM blog_entries
ORDER BY {order_by_column} {'ASC' if order_by_ascending else 'DESC'}
LIMIT ?
"""
        args = (limit,)

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            unpack = _make_unpacker(cur)
            values = [unpack(row) async for row in cur]
            return values

    async def update(self, id_: int, **kwargs) -> bool:
        """Update a blog entry"""
        updates = {
            'updated': datetime.utcnow()
        }
        updates.update(kwargs)
        stmt = f"""
UPDATE blog_entries
SET {','.join(f'{key}=?' for key in updates)}
WHERE rowid=?
"""
        args = *updates.values(), id_
        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            await self._conn.commit()
            return cur.rowcount == 1

    async def delete(self, id_: int) -> bool:
        """Delete a blog entry"""
        stmt = f"""
DELETE FROM blog_entries
WHERE rowid=?
"""
        args = (id_,)
        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            await self._conn.commit()
            return cur.rowcount == 1

    async def initialise(self) -> None:
        """Initialise the repository"""
        await self._conn.execute("""
CREATE TABLE IF NOT EXISTS blog_entries
(
    title TEXT NOT NULL,
    description TEXT NULL,
    content TEXT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,

    PRIMARY KEY(title)
)
""")
        await self._conn.commit()
