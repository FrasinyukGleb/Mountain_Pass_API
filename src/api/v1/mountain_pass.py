from fastapi import APIRouter, status
from starlette.responses import JSONResponse

from src.db.db import db_dependency
from src.schemas import PassAddSchema, PassShowSchema
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


@mountain_pass_router.get('/{mountain_pass_id}')
async def get_mountain_pass_by_id(mountain_pass_id: int, session: db_dependency) -> PassShowSchema:
    if not (db_mountain_pass := await db.get_mountain_pass_by_id(mountain_pass_id, session)):
        raise ValueError(f'Не удалось найти запись с id {mountain_pass_id}')
    return await db.get_info_mountain_pass(db_mountain_pass, session)