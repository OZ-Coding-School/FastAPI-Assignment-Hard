from tortoise import Model, fields

from src.models.base import BaseModel


class Genre(BaseModel, Model):
    external_id = fields.IntField(unique=True)
    name = fields.CharField(max_length=255)

    class Meta:
        table = "genres"


class Movie(BaseModel, Model):
    external_id = fields.IntField(unique=True, null=True)
    title = fields.CharField(max_length=255)
    overview = fields.TextField()
    cast = fields.CharField(max_length=255)
    release_date = fields.DateField()
    runtime = fields.IntField()
    poster_image_url = fields.CharField(max_length=255, null=True)
    genres: fields.ManyToManyRelation[Genre] = fields.ManyToManyField("models.Genre", related_name="movies")

    class Meta:
        table = "movies"
