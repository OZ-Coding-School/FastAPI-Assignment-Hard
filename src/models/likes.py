from tortoise import fields
from tortoise.models import Model

from src.models.base import BaseModel
from src.models.reviews import Review
from src.models.users import User


class ReviewLike(BaseModel, Model):
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="review_likes", on_delete=fields.CASCADE
    )
    review: fields.ForeignKeyRelation[Review] = fields.ForeignKeyField(
        "models.Review", related_name="likes", on_delete=fields.CASCADE
    )
    is_liked = fields.BooleanField(default=True)

    class Meta:
        table = "review_likes"
        unique_together = (("user", "review"),)
