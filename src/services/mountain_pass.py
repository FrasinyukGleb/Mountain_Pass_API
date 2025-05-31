import logging
from datetime import datetime
from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, update, delete

from src.db.db import db_dependency
from src.exceptions import PassUpdateError
from src.models import Coord, Image, Level, PassAdded, User
from src.schemas import (
    CoordsSchema,
    ImageSchema,
    LevelSchema,
    PassAddSchema,
    UserSchema,
    PassShowSchema,
    PassUpdateSchema,
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

    async def get_mountain_passes_by_user_id(self, user_id: int, session: db_dependency) -> List[PassShowSchema]:
        _mountain_passes = await session.execute(select(PassAdded).where(PassAdded.user_id == user_id))
        mountain_passes = _mountain_passes.scalars().all()
        return [await self.get_info_mountain_pass(mountain_pass, session) for mountain_pass in mountain_passes]

    async def get_info_mountain_pass(self, mountain_pass: PassAdded, session: db_dependency) -> PassShowSchema:
        user = await self._get_user_by_id(mountain_pass.user_id, session)
        coord = await self._get_coord_by_id(mountain_pass.coord_id, session)
        level = await self._get_level_by_id(mountain_pass.level_id, session)
        images = await self._get_images_by_mountain_pass_id(mountain_pass.id, session)
        return PassShowSchema(
            beauty_title=mountain_pass.beauty_title,
            title=mountain_pass.title,
            other_titles=mountain_pass.other_titles,
            connect=mountain_pass.connect,
            add_time=str(mountain_pass.add_time),
            user=UserSchema(**jsonable_encoder(user)),
            coords=CoordsSchema(**jsonable_encoder(coord)),
            level=LevelSchema(**jsonable_encoder(level)),
            images=[ImageSchema(**jsonable_encoder(image)) for image in images],
            status=mountain_pass.status,
        )

    async def _get_user_by_id(self, user_id: int, session: db_dependency) -> User:
        user = await session.execute(select(User).where(User.id == user_id))
        return user.scalar()

    async def _get_coord_by_id(self, coords_id: int, session: db_dependency) -> Coord:
        coord = await session.execute(select(Coord).where(Coord.id == coords_id))
        return coord.scalar()

    async def _get_level_by_id(self, level_id: int, session: db_dependency) -> Level:
        level = await session.execute(select(Level).where(Level.id == level_id))
        return level.scalar()

    async def _get_images_by_mountain_pass_id(self, mountain_pass_id: int, session: db_dependency) -> List[Image]:
        images = await session.execute(select(Image).where(Image.mountain_pass_id == mountain_pass_id))
        return images.scalars().all()

    async def get_mountain_pass_by_id(self, mountain_pass_id: int, session: db_dependency) -> Optional[PassAdded]:
        mountain_pass = await session.execute(select(PassAdded).where(PassAdded.id == mountain_pass_id))
        return mountain_pass.scalar_one_or_none()

    async def update_mountain_pass(
        self,
        db_mountain_pass: PassAdded,
        data_update: PassUpdateSchema,
        session: db_dependency,
    ) -> bool:
        mountain_pass_data = data_update.model_dump()
        try:
            mountain_pass_data['add_time'] = datetime.strptime(data_update.add_time, '%Y-%m-%d %H:%M:%S')
            coords = mountain_pass_data.pop('coords')
            level = mountain_pass_data.pop('level')
            mountain_pass_data.pop('images')
            await session.execute(update(Coord).where(Coord.id == db_mountain_pass.coord_id).values(coords))
            await session.execute(update(Level).where(Level.id == db_mountain_pass.level_id).values(level))
            await session.execute(delete(Image).where(Image.mountain_pass_id == db_mountain_pass.id))
            if data_update.images:
                await self._add_images(db_mountain_pass.id, data_update.images, session)
            else:
                await session.execute(delete(Image).where(Image.mountain_pass_id == db_mountain_pass.id))
            await session.execute(update(PassAdded).where(PassAdded.id == db_mountain_pass.id).values(mountain_pass_data))
            await session.commit()
        except Exception as e:
            # Перезаписываем на первоначальное значение
            self.logger.warning(f'Error the update mountain_pass "{db_mountain_pass.id}". Delete data')
            info_mountain_pass = await self.get_info_mountain_pass(db_mountain_pass, session)
            await self._delete_mountain_pass(db_mountain_pass, session)
            await self.add_mountain_pass(info_mountain_pass, session)
            self.logger.warning('Adding the original mountain_pass. Success')
            raise PassUpdateError(e)
        return True

    async def _delete_mountain_pass(self, mountain_pass: PassAdded, session: db_dependency) -> None:
        await session.execute(delete(Image).where(Image.mountain_pass_id == mountain_pass.id))
        await session.execute(delete(PassAdded).where(PassAdded.id == mountain_pass.id))
        await session.execute(delete(Coord).where(Coord.id == mountain_pass.coord_id))
        await session.execute(delete(Level).where(Level.id == mountain_pass.level_id))
        await session.commit()