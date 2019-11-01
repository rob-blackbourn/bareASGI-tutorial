"""Blog Repository"""

from datetime import datetime
from typing import (
    Any,
    Dict,
    List,
    Optional
)

import aiosqlite

from bareasgi_blog.repository import Repository

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
        await self._conn.execute("""
CREATE TABLE IF NOT EXISTS blog_entries
(
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NULL,
    content TEXT NULL,
    created timestamp NOT NULL,
    updated timestamp NOT NULL,

    PRIMARY KEY(title)
)
""")
        await self._conn.commit()
