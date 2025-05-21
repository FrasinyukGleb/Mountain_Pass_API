import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select

from src.db.db import db_dependency
from src.models import Coord, Image, Level, PassAdded, User
from src.schemas import (
    CoordsSchema,
    ImageSchema,
    LevelSchema,
    PassAddSchema,
    UserSchema,
)


class Mountain_Pass:
    def __init__(self):
        self.logger = logging.getLogger('mountain_pass')

    async def add_mountain_pass(
        self,
        mountain_pass: PassAddSchema,
        session: db_dependency,
    ) -> int:
        """
        Добавление перевала
        :param db: сессия
        :param mountain_pass: данные с post запроса
        :return: id записи
        """
        user_id = await self._add_user(mountain_pass.user, session)
        coords_id = await self._add_coords(mountain_pass.coords, session)
        level_id = await self._add_levels(mountain_pass.level, session)
        db_mountain_pass = PassAdded(
            beauty_title=mountain_pass.beauty_title,
            title=mountain_pass.title,
            other_titles=mountain_pass.other_titles,
            connect=mountain_pass.connect,
            add_time=datetime.strptime(mountain_pass.add_time, '%Y-%m-%d %H:%M:%S'),
            user_id=user_id,
            coord_id=coords_id,
            level_id=level_id,
        )
        session.add(db_mountain_pass)
        await session.commit()

        if mountain_pass.images:
            await self._add_images(db_mountain_pass.id, mountain_pass.images, session)
        return db_mountain_pass.id

    async def _add_images(self, mountain_pass_id: int, images: List[ImageSchema], session: db_dependency) -> None:
        list_img = [Image(**image.model_dump(), mountain_pass_id=mountain_pass_id) for image in images]
        session.add_all(list_img)
        await session.commit()

    async def _add_coords(self, coords: CoordsSchema, session: db_dependency) -> int:
        coords_db = Coord(**coords.model_dump())
        session.add(coords_db)
        await session.commit()
        return coords_db.id

    async def _add_user(self, user: UserSchema, session: db_dependency) -> int:
        if not (user_db := await self.get_user_by_email(user.email, session)):
            user_db = User(**user.model_dump())
            session.add(user_db)
            await session.commit()
        return user_db.id

    async def _add_levels(self, levels: LevelSchema, session: db_dependency) -> int:
        levels_db = Level(**levels.model_dump())
        session.add(levels_db)
        await session.commit()
        return levels_db.id

    async def get_user_by_email(self, email: str, session: db_dependency) -> Optional[User]:
        user = await session.execute(select(User).filter(User.email == email))
        return user.scalar_one_or_none()

