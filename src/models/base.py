from tortoise import fields


class BaseModel:
    id = fields.BigIntField(primary_key=True, autoincrement=True)
    created_at = fields.DatetimeField(auto_now_add=True)
