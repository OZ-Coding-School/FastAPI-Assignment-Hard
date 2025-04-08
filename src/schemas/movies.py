from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field


class CreateMovieRequest(BaseModel):
    title: str
    overview: str
    cast: str
    genre_ids: list[int]
    runtime: int
    release_date: date


class MovieResponse(BaseModel):
    id: int
    title: str
    overview: str
    cast: str
    genres: list[int]
    runtime: int
    release_date: date
    poster_image_url: str | None = None


class MovieSearchParams(BaseModel):
    title: str | None = None
    genre_ids: list[int] | None = None


class MovieUpdateRequest(BaseModel):
    title: str | None = None
    overview: str | None = None
    cast: str | None = None
    genre_ids: list[int] | None = None
    runtime: Annotated[int, Field(gt=0)] | None = None
    release_date: date | None = None
