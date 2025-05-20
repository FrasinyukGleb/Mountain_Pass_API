from fastapi import APIRouter

from src.api.v1.mountain_pass import mountain_pass_router

api_router = APIRouter()

api_router.include_router(mountain_pass_router)