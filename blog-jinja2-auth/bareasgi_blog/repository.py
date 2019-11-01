"""Repository"""

from abc import ABCMeta, abstractmethod
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple
)

import aiosqlite


def make_unpacker(cur: aiosqlite.Cursor) -> Callable[[Tuple], Dict[str, Any]]:
    """Make an unpacker"""
    columns = [name for name, *_ in cur.description]
    return lambda row: dict(zip(columns, row))


class Repository(metaclass=ABCMeta):
    """"Repository"""

    def __init__(self, conn: aiosqlite.Connection, table: str) -> None:
        self._conn = conn
        self.table = table

    async def create(self, **kwargs) -> int:
        """Create a record"""
        stmt = f"""
INSERT INTO {self.table}({','.join(kwargs.keys())})
VALUES ({','.join('?' for _ in range(len(kwargs)))})
"""
        args = tuple(kwargs.values())

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            await self._conn.commit()
            return cur.lastrowid

    async def read_by_id(
            self,
            id_: int,
            columns: Optional[List[str]]
    ) -> Optional[Dict[str, Any]]:
        """Read a record by it's id"""
        return await self.read_by_column('id', id_, columns)

    async def read_by_column(
            self,
            column: str,
            value: Any,
            columns: Optional[List[str]]
    ) -> Optional[Dict[str, Any]]:
        """Read a record by a column value"""
        stmt = f"""
SELECT {','.join(columns) if columns else '*'}
FROM {self.table}
WHERE {column} = ?
"""
        args = (value,)

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            row = await cur.fetchone()
            if row is None:
                return None
            result = make_unpacker(cur)(row)
            return result

    async def read_between_column(
            self,
            column: str,
            start_value: Any,
            end_value: Any,
            columns: Optional[List[str]],
            order_by_column: str,
            order_by_ascending: bool,
            limit: int
    ) -> List[Dict[str, Any]]:
        """Read records for a column between values"""
        stmt = f"""
SELECT {','.join(columns) if columns else '*'}
FROM {self.table}
WHERE {column} BETWEEN ? AND ?
ORDER BY {order_by_column} {'ASC' if order_by_ascending else 'DESC'}
LIMIT ?
"""
        args = (start_value, end_value, limit)

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            unpack = make_unpacker(cur)
            values = [unpack(row) async for row in cur]
            return values

    async def read_many(
            self,
            columns: Optional[List[str]],
            order_by_column: str,
            order_by_ascending: bool,
            limit: int
    ) -> List[Dict[str, Any]]:
        """Read many records"""
        stmt = f"""
SELECT {','.join(columns) if columns else '*'}
FROM {self.table}
ORDER BY {order_by_column} {'ASC' if order_by_ascending else 'DESC'}
LIMIT ?
"""
        args = (limit,)

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            unpack = make_unpacker(cur)
            values = [unpack(row) async for row in cur]
            return values

    async def read_many_by_column(
            self,
            column: str,
            value: Any,
            columns: Optional[List[str]],
            order_by_column: str,
            order_by_ascending: bool,
            limit: int
    ) -> List[Dict[str, Any]]:
        """Read many records"""
        stmt = f"""
SELECT {','.join(columns) if columns else '*'}
FROM {self.table}
WHERE {column} = ?
ORDER BY {order_by_column} {'ASC' if order_by_ascending else 'DESC'}
LIMIT ?
"""
        args = (value, limit)

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            unpack = make_unpacker(cur)
            values = [unpack(row) async for row in cur]
            return values

    async def update(
            self, id_: int,
            **kwargs
    ) -> bool:
        """Update a record"""
        stmt = f"""UPDATE {self.table}
SET {','.join(f'{key}=?' for key in kwargs)}
WHERE id=?"""
        args = *kwargs.values(), id_
        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            await self._conn.commit()
            return cur.rowcount == 1

    async def delete(
            self, id_: int
    ) -> bool:
        """Delete a record"""
        stmt = f"""
DELETE FROM {self.table}
WHERE id=?
"""
        args = (id_,)
        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            await self._conn.commit()
            return cur.rowcount == 1

    @abstractmethod
    async def initialise(self) -> None:
        """Initialise the repository"""
