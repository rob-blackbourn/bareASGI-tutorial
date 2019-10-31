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
        super().__init__(conn, 'blog_entry')

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
            limit
        )

    async def initialise(self) -> None:
        """Initialise the repository"""
        await self._conn.execute("""
CREATE TABLE IF NOT EXISTS blog_entry
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

# async def main():
#     conn = await aiosqlite.connect(
#           ':memory:',
#           detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
#       )
#     repo = BlogRepository(conn)
#     await repo.initialise()
#     now = datetime.now()
#     id_ = await repo.create(
#           title='Test',
#           description='Testing',
#           content='This is not a test',
#           created=now, updated=now
#        )
#     blog_entry = await repo.read_by_id(id_)
#     print(blog_entry)
#     await repo.update(id_, title='Test0', description='Testing0')
#     blog_entry = await repo.read_by_id(id_)
#     print(blog_entry)
#     await repo.delete(id_)
#     blog_entry = await repo.read_by_id(id_)
#     print(blog_entry)

#     now = datetime.now()
#     await repo.create(title='Test1', description='Testing1', content='This is not a test1', created=now, updated=now)
#     now = datetime.now()
#     await repo.create(title='Test2', description='Testing2', content='This is not a test2', created=now, updated=now)
#     now = datetime.now()
#     await repo.create(title='Test3', description='Testing3', content='This is not a test3', created=now, updated=now)
#     now = datetime.now()
#     blog_entries = await repo.read_between(now - timedelta(1), now + timedelta(1))
#     print(blog_entries)
#     await conn.close()



# if __name__ == '__main__':
#     import asyncio
#     asyncio.run(main())
