from enum import StrEnum

from pydantic import BaseModel as PydanticBaseModel
from tortoise import Model, fields

from src.models.base import BaseModel
from src.models.users import GenderEnum


class GenreEnum(StrEnum):
    SF = "SF"
    ADVENTURE = "Adventure"
    ROMANCE = "Romance"
    COMIC = "Comic"
    FANTASY = "Fantasy"
    SCIENCE = "Science"
    MYSTERY = "Mystery"
    ACTION = "Action"
    HORROR = "Horror"


class CastModel(PydanticBaseModel):
    name: str
    age: int
    agency: str
    gender: GenderEnum


class Movie(BaseModel, Model):
    title = fields.CharField(max_length=255)
    plot = fields.TextField()
    cast: list[CastModel] = fields.JSONField(field_type=list[CastModel])
    playtime = fields.IntField()
    genre = fields.CharEnumField(GenreEnum)

    class Meta:
        table = "movies"
