from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query

from src.models.movies import Movie
from src.schemas.movies import (
    CreateMovieRequest,
    MovieResponse,
    MovieSearchParams,
    MovieUpdateRequest,
)

movie_router = APIRouter(prefix="/movies", tags=["movies"])


@movie_router.post("", status_code=201)
async def create_movie(data: CreateMovieRequest) -> MovieResponse:
    movie = await Movie.create(**data.model_dump())
    return MovieResponse(
        id=movie.id, title=movie.title, plot=movie.plot, cast=movie.cast, playtime=movie.playtime, genre=movie.genre
    )


@movie_router.get("", status_code=200)
async def get_movies(query_params: Annotated[MovieSearchParams, Query()]) -> list[MovieResponse]:
    valid_query = {key: value for key, value in query_params.model_dump().items() if value is not None}
    return [
        MovieResponse(
            id=movie.id, title=movie.title, plot=movie.plot, cast=movie.cast, playtime=movie.playtime, genre=movie.genre
        )
        for movie in await Movie.filter(**valid_query).all()
    ]


@movie_router.get("/{movie_id}", status_code=200)
async def get_movie(movie_id: int = Path(gt=0)) -> MovieResponse:
    movie = await Movie.get_or_none(id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404)
    return MovieResponse(
        id=movie.id, title=movie.title, plot=movie.plot, cast=movie.cast, playtime=movie.playtime, genre=movie.genre
    )


@movie_router.patch("/{movie_id}", status_code=200)
async def update_movie(data: MovieUpdateRequest, movie_id: int = Path(gt=0)) -> MovieResponse:
    movie = await Movie.get_or_none(id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404)
    update_data = {key: value for key, value in data.model_dump().items() if value is not None}
    await movie.update_from_dict(update_data)
    await movie.save()
    return MovieResponse(
        id=movie.id, title=movie.title, plot=movie.plot, cast=movie.cast, playtime=movie.playtime, genre=movie.genre
    )


@movie_router.delete("/{movie_id}", status_code=204)
async def delete_movie(movie_id: int = Path(gt=0)) -> None:
    movie = await Movie.get_or_none(id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404)
    await movie.delete()
