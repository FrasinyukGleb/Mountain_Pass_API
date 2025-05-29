from typing import List

from fastapi import APIRouter, status, Query
from starlette.responses import JSONResponse

from src.db.db import db_dependency
from src.exceptions import PassNotFoundError, UserNotFoundByEmailError, IncorrectPassStatus, PassUpdateError
from src.models import StatusEnum
from src.schemas import PassAddSchema, PassShowSchema, PassUpdateSchema
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
        raise PassNotFoundError(mountain_pass_id)
    return await db.get_info_mountain_pass(db_mountain_pass, session)


@mountain_pass_router.get('/')
async def get_mountain_pass_by_user_email(
    session: db_dependency,
    user__email: str = Query(pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
) -> List[PassShowSchema]:
    if not (user := await db.get_user_by_email(user__email, session)):
        raise UserNotFoundByEmailError(user__email)
    return await db.get_mountain_passes_by_user_id(user.id, session)


@mountain_pass_router.patch('/{mountain_pass_id}')
async def update_mountain_pass_by_id(
    mountain_pass_id: int,
    data_to_update: PassUpdateSchema,
    session: db_dependency,
) -> JSONResponse:
    try:
        if not (db_mountain_pass := await db.get_mountain_pass_by_id(mountain_pass_id, session)):
            raise PassNotFoundError(mountain_pass_id)

        if db_mountain_pass.status.value != StatusEnum.new.value:
            raise IncorrectPassStatus(db_mountain_pass.status.value)
        await db.update_mountain_pass(db_mountain_pass, data_to_update, session)
    except (PassNotFoundError, PassUpdateError, IncorrectPassStatus) as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                'state': 0,
                'message': e.detail,
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'state': 0,
                'message': str(e),
            },
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'state': 1,
            'message': None,
        },
    )