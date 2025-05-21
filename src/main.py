import uvicorn
from fastapi import FastAPI, APIRouter, HTTPException, Request, status
from starlette.responses import JSONResponse

import logging.config
import logging.handlers
import atexit
from contextlib import asynccontextmanager
from typing import AsyncContextManager

from core.logger import LOGGING_CONFIG
from src.api import api_router
from src.core.config import uvicorn_options


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncContextManager[None]:
    logging.config.dictConfig(LOGGING_CONFIG)
    # получаем обработчик очереди из корневого логгера
    queue_handler = logging.getHandlerByName("queue_handler")
    try:
        # если логгер есть
        if queue_handler is not None:
            # запускаем слушатель очереди
            queue_handler.listener.start()
            # регистрируем функцию, которая будет вызвана при завершении работы программы
            atexit.register(queue_handler.listener.stop)
        yield
    finally:
        # в случае ошибки выключаем слушатель
        if queue_handler is not None:
            queue_handler.listener.stop()

app = FastAPI(
    lifespan=lifespan,
    docs_url="/api/openapi"
)

logger = logging.getLogger("my_app")

router = APIRouter()

app.include_router(router)
app.include_router(api_router)


@app.middleware('http')
async def error_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as exc:
        logger.exception(exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                'status': exc.status_code,
                'message': exc.detail,
                'id': None,
            },
        )
    except Exception as e:
        logger.exception(f'{request.url} | Error in application: {e}')
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e),
                'id': None,
            },
        )

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        **uvicorn_options
    )