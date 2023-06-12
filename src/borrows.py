import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from . import db


log = logging.getLogger(__name__)
router = APIRouter()


class Borrow(BaseModel):
    reader_id: int
    book_id: int


@router.post("/v1/borrows")
async def add_borrow(borrow: Borrow):
    await db.connection.execute(
        """
        INSERT INTO borrows
            (reader_id, book_id, borrow_time, return_time)
        VALUES
            (?, ?, DATE('now'), NULL)
        """,
        (borrow.reader_id, borrow.book_id),
    )
    log.debug(f"New borrow from reader id {borrow.reader_id}")


@router.delete("/v1/borrows/{book_id}")
async def del_borrow(book_id: int):
    await db.connection.execute(
        """
        UPDATE
            borrows
        SET
            return_time = DATE('now')
        WHERE
            book_id = ?
            AND return_time IS NULL;
        """,
        (book_id,),
    )
    log.debug(f"Book {book_id} returned.")


@router.get("/v1/borrows")
async def get_borrows():
    async with db.connection.execute(
        """
        SELECT
            readers.name,
            books.title,
            authors.name,
            borrows.borrow_time
        FROM
            borrows
        LEFT JOIN
            books ON books.id = borrows.book_id
        LEFT JOIN
            authors ON authors.id = books.author_id
        LEFT JOIN
            readers ON readers.id = borrows.reader_id
        WHERE
            borrows.return_time IS NULL
        """
    ) as cursor:
        rows = await cursor.fetchall()

    return {
        "borrows": [{"reader": item[0], "title": item[1], "author": item[2], "borrow_time": item[3]} for item in rows]
    }
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from . import db

log = logging.getLogger(__name__)
router = APIRouter()


class Borrow(BaseModel):
    reader_id: int
    book_id: int


@router.post("/v1/borrows")
async def add_borrow(borrow: Borrow):
    book_exists = await check_book_exists(borrow.book_id)
    reader_exists = await check_reader_exists(borrow.reader_id)
    if not reader_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reader_id")
    if not book_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid book_id")

    is_already_borrowed = await check_book_borrowed_by_reader(borrow.reader_id, borrow.book_id)
    if is_already_borrowed:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="The book is already borrowed by the same reader")

    is_borrowed = await check_book_borrowed(borrow.book_id)
    if is_borrowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="The book is already borrowed by someone else"
        )

    await db.connection.execute(
        """
        INSERT INTO borrows
            (reader_id, book_id, borrow_time, return_time)
        VALUES
            (?, ?, DATE('now'), NULL)
        """,
        (borrow.reader_id, borrow.book_id),
    )
    log.debug(f"New borrow from reader id {borrow.reader_id}")

    return {"message": "Borrow added successfully", "borrow": borrow.dict()}


async def check_book_exists(book_id: int) -> bool:
    book = await db.connection.execute("SELECT id FROM books WHERE id = ?", (book_id,))
    return bool(await book.fetchone())


async def check_reader_exists(reader_id: int) -> bool:
    reader = await db.connection.execute("SELECT id FROM readers WHERE id = ?", (reader_id,))
    return bool(await reader.fetchone())


async def check_book_borrowed(book_id: int) -> bool:
    borrow = await db.connection.execute("SELECT id FROM borrows WHERE book_id = ? AND return_time IS NULL", (book_id,))
    return bool(await borrow.fetchone())


async def check_book_borrowed_by_reader(reader_id: int, book_id: int) -> bool:
    borrow = await db.connection.execute(
        "SELECT id FROM borrows WHERE reader_id = ? AND book_id = ? AND return_time IS NULL", (reader_id, book_id))
    return bool(await borrow.fetchone())


@router.delete("/v1/borrows/{book_id}")
async def del_borrow(book_id: int):
    await db.connection.execute(
        """
        UPDATE
            borrows
        SET
            return_time = DATE('now')
        WHERE
            book_id = ?
            AND return_time IS NULL;
        """,
        (book_id,),
    )
    log.debug(f"Book {book_id} returned.")


@router.get("/v1/borrows")
async def get_borrows():
    async with db.connection.execute(
        """
        SELECT
            readers.name,
            books.title,
            authors.name,
            borrows.borrow_time
        FROM
            borrows
        LEFT JOIN
            books ON books.id = borrows.book_id
        LEFT JOIN
            authors ON authors.id = books.author_id
        LEFT JOIN
            readers ON readers.id = borrows.reader_id
        WHERE
            borrows.return_time IS NULL
        """
    ) as cursor:
        rows = await cursor.fetchall()

    return {
        "borrows": [{"reader": item[0], "title": item[1], "author": item[2], "borrow_time": item[3]} for item in rows]
    }
