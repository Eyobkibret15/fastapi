import logging
import os

import aiosqlite


log = logging.getLogger(__name__)
connection = None


async def initialize():
    global connection

    log.debug("Initializing database...")
    log.info("what is happinging here")
    connection = await aiosqlite.connect(f"{os.getcwd()}/app.db")

    await connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            author_id INTEGER NOT NULL,
            title TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS readers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS borrows (
            id INTEGER PRIMARY KEY,
            reader_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_time TEXT NOT NULL,
            return_time TEXT
        );
        """
    )

    log.debug("Database ready.")
