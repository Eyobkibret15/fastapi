import logging

from fastapi import APIRouter
from pydantic import BaseModel

from . import db


log = logging.getLogger(__name__)
router = APIRouter()


class Author(BaseModel):
    name: str


@router.post("/v1/authors")
async def add_author(author: Author):
    author_id = (await db.connection.execute_insert(
        """
        INSERT INTO authors (name) VALUES (?)
        """,
        (author.name,),
    ))[0]
    log.debug(f"Author added {author.name}")

    return {"author_id": author_id}


@router.get("/v1/authors")
async def get_authors():
    async with db.connection.execute(
        """
        SELECT
            id, name
        FROM
            authors
        ORDER BY id ASC
        """
    ) as cursor:
        rows = await cursor.fetchall()

    return {"authors": [{"id": item[0], "name": item[1]} for item in rows]}
