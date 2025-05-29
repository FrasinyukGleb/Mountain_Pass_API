from typing import List, Optional

from pydantic import Base64Bytes, BaseModel, EmailStr, Field, PositiveFloat, PositiveInt

from src.models import StatusEnum


class UserSchema(BaseModel):
    email: EmailStr
    surname: str = Field(max_length=150)
    name: str = Field(max_length=150)
    patronymic: Optional[str] = Field(max_length=150, default='')
    phone: Optional[str] = Field(max_length=15, default=None)


class CoordsSchema(BaseModel):
    latitude: PositiveFloat
    longitude: PositiveFloat
    height: PositiveInt


class LevelSchema(BaseModel):
    winter: str = Field(max_length=2, default='')
    summer: str = Field(max_length=2, default='')
    autumn: str = Field(max_length=2, default='')
    spring: str = Field(max_length=2, default='')


class ImageSchema(BaseModel):
    data: Base64Bytes
    title: str = Field(max_length=150)


class BaseMountainPass(BaseModel):
    beauty_title: str = Field(max_length=250)
    title: str = Field(max_length=250)
    other_titles: str = Field(max_length=250)
    connect: str = Field(default='')
    add_time: str
    coords: CoordsSchema = Field(default=CoordsSchema)
    level: LevelSchema = Field(default=LevelSchema)
    images: Optional[List[ImageSchema]] = Field(default=[])


class PassAddSchema(BaseMountainPass):
    user: UserSchema = Field(default=UserSchema)


class PassShowSchema(BaseMountainPass):
    user: UserSchema = Field(default=UserSchema)
    status: str = Field(default=StatusEnum.new.value)


class PassUpdateSchema(BaseMountainPass):
    pass
