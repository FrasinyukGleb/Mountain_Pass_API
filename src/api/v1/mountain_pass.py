from typing import List

from fastapi import APIRouter, Query, status
from starlette.responses import JSONResponse

from src.db.db import db_dependency
from src.models import StatusEnum
from src.schemas import PassAddSchema
from src.services.mountain_pass import Mountain_Pass

mountain_pass_router = APIRouter(prefix='/submitData', tags=['mountain_pass'])
db = Mountain_Pass()


@mountain_pass_router.post('/')
async def add_mountain_pass(mountain_pass: PassAddSchema, session: db_dependency) -> JSONResponse:
    mountain_pass_id = await db.add_mountain_pass(mountain_pass=mountain_pass, session=session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'status': status.HTTP_200_OK,
            'id': mountain_pass_id,
            'message': None,
        },
    )
