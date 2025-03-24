from typing import Annotated

from pydantic import BaseModel, Field

from src.models.movies import CastModel, GenreEnum


class CreateMovieRequest(BaseModel):
    title: str
    plot: str
    cast: list[CastModel]
    playtime: int
    genre: GenreEnum


class MovieResponse(BaseModel):
    id: int
    title: str
    plot: str
    cast: list[CastModel]
    playtime: int
    genre: GenreEnum


class MovieSearchParams(BaseModel):
    title: str | None = None
    genre: GenreEnum | None = None


class MovieUpdateRequest(BaseModel):
    title: str | None = None
    plot: str | None = None
    cast: list[CastModel] | None = None
    playtime: Annotated[int, Field(gt=0)] | None = None
    genre: GenreEnum | None = None
