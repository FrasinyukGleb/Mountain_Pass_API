import multiprocessing
from typing import Optional

from dotenv import load_dotenv, find_dotenv
import os
from pydantic import model_validator, PostgresDsn
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

load_dotenv(find_dotenv())


class AppSettings(BaseSettings):
    fstr_db_login: str = os.getenv('FSTR_DB_LOGIN')
    fstr_db_pass: str = os.getenv('FSTR_DB_PASS')
    fstr_db_name: str = os.getenv('FSTR_DB_NAME')
    fstr_db_host: str = os.getenv('FSTR_DB_HOST')
    fstr_db_port: int = os.getenv('FSTR_DB_PORT')
    app_port: int = 8080
    app_host: str = 'localhost'
    reload: bool = True
    cpu_count: int | None = None
    postgres_dsn: PostgresDsn = MultiHostUrl(
            f'postgresql+asyncpg://{fstr_db_login}'
            f':{fstr_db_pass}@{fstr_db_host}'
            f':{fstr_db_port}/{fstr_db_name}')

    class Config:
        _env_file = ".env"
        _extra = 'allow'



app_settings = AppSettings()

uvicorn_options = {
    'host': app_settings.app_host,
    'port': app_settings.app_port,
    'workers': app_settings.cpu_count or multiprocessing.cpu_count(),
    'reload': app_settings.reload,
}