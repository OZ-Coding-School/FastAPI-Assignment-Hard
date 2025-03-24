from enum import StrEnum

from tortoise import Model, fields

from src.models.base import BaseModel


class GenderEnum(StrEnum):
    MALE = "male"
    FEMALE = "female"


class User(BaseModel, Model):
    username = fields.CharField(unique=True, max_length=50, index=True)
    hashed_password = fields.CharField(max_length=128)
    age = fields.IntField()
    gender = fields.CharEnumField(GenderEnum)
    last_login = fields.DatetimeField(null=True)

    class Meta:
        table = "users"
