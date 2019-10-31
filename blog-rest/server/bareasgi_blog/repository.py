"""Repository"""

from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
import sqlite3
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

class Repository:
    """"Repository"""

    def __init__(self, conn: aiosqlite.Connection, table: str) -> None:
        self._conn = conn
        self._table = table

    async def create(self, **kwargs) -> int:
        stmt = f"""INSERT INTO {self._table}({','.join(kwargs.keys())})
VALUES ({','.join('?' for _ in range(len(kwargs)))})"""
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
        return await self.read_by_column('rowid', id_, columns)


    async def read_by_column(
            self,
            column: str,
            value: Any,
            columns: Optional[List[str]]
    ) -> Optional[Dict[str, Any]]:
        stmt = f"""SELECT rowid AS id,{','.join(columns) if columns else '*'}
FROM {self._table}
WHERE {column} = ?"""
        args = (value,)

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            row = await cur.fetchone()
            if row is None:
                return None
            result = _make_unpacker(cur)(row)
            return result

    async def read_between_column(
            self,
            column: str,
            start_value: Any,
            end_value: Any,
            columns: Optional[List[str]],
            order_by: str,
            limit: int
    ) -> List[Dict[str, Any]]:
        stmt = f"""SELECT rowid AS id,{','.join(columns) if columns else '*'}
FROM {self._table}
WHERE {column} BETWEEN ? AND ?
ORDER BY {order_by}
LIMIT ?"""
        args = (start_value, end_value, limit)

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            unpack = _make_unpacker(cur)
            values = [unpack(row) async for row in cur]
            return values

    async def read_many(self, columns: Optional[List[str]], order_by: str, limit: int) -> List[Dict[str, Any]]:
        stmt = f"""SELECT rowid AS id,{','.join(columns) if columns else '*'}
FROM {self._table}
ORDER BY {order_by}
LIMIT ?"""
        args = (limit,)

        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            unpack = _make_unpacker(cur)
            values = [unpack(row) async for row in cur]
            return values

    async def update(self, id_: int, **kwargs) -> bool:
        updates = {
            'updated': datetime.utcnow()
        }
        updates.update(kwargs)
        stmt = f"""UPDATE {self._table}
SET {','.join(f'{key}=?' for key in updates)}
WHERE rowid=?"""
        args = *updates.values(), id_
        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            await self._conn.commit()
            return cur.rowcount == 1

    async def delete(self, id_: int) -> bool:
        stmt = f"""DELETE FROM {self._table} WHERE rowid=?"""
        args = (id_,)
        async with self._conn.cursor() as cur:
            await cur.execute(stmt, args)
            await self._conn.commit()
            return cur.rowcount == 1

    @abstractmethod
    async def initialise(self) -> None:
        pass
