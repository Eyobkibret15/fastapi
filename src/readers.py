import logging

from fastapi import APIRouter
from pydantic import BaseModel

from . import db


log = logging.getLogger(__name__)
router = APIRouter()


class Reader(BaseModel):
    name: str


@router.post("/v1/readers")
async def add_reader(reader: Reader):
    reader_id = (await db.connection.execute_insert(
        """
        INSERT INTO readers
            (name)
        VALUES (?)
        """,
        (reader.name,),
    ))[0]
    log.debug(f"Reader added {reader.name}")
    return {"reader_id": reader_id}


@router.get("/v1/readers")
async def get_readers():
    async with db.connection.execute(
        """
        SELECT
            id,
            name
        FROM
            readers
        """
    ) as cursor:
        rows = await cursor.fetchall()

    return {"readers": [{"id": item[0], "name": item[1]} for item in rows]}
