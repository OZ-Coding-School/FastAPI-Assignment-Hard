from typing import Annotated

from pydantic import BaseModel, Field


class CreateMovieRequest(BaseModel):
    title: str
    playtime: int
    genre: list[str]


class MovieResponse(BaseModel):
    id: int
    title: str
    playtime: int
    genre: list[str]


class MovieSearchParams(BaseModel):
    title: str | None = None
    genre: str | None = None


class MovieUpdateRequest(BaseModel):
    title: str | None = None
    playtime: Annotated[int, Field(gt=0)] | None = None
    genre: list[str] | None = None
