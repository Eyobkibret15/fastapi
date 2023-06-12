import logging

from fastapi import APIRouter
from pydantic import BaseModel

from . import db


log = logging.getLogger(__name__)
router = APIRouter()


class Book(BaseModel):
    author_id: int
    title: str


@router.post("/v1/books")
async def add_book(book: Book):
    book_id = (await db.connection.execute_insert(
        """
        INSERT INTO books
            (author_id, title)
        VALUES (?, ?)
        """,
        (book.author_id, book.title),
    ))[0]

    log.debug(f"Book added {book.title}")

    return {"book_id": book_id}


@router.get("/v1/books")
async def get_books():
    async with db.connection.execute(
        """
        SELECT
            books.id,
            books.title,
            authors.name
        FROM
            books
        JOIN
            authors ON authors.id = books.author_id
        """
    ) as cursor:
        rows = await cursor.fetchall()

    return {"books": [{"id": item[0], "title": item[1], "author": item[2]} for item in rows]}
