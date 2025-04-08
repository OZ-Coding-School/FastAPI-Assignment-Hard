from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, UploadFile

from src.models.movies import Genre, Movie
from src.schemas.movies import (
    CreateMovieRequest,
    MovieResponse,
    MovieSearchParams,
    MovieUpdateRequest,
)
from src.services.file import FileUploadService

movie_router = APIRouter(prefix="/movies", tags=["movies"])


@movie_router.post("", status_code=201)
async def create_movie(data: CreateMovieRequest) -> MovieResponse:
    movie = await Movie.create(**data.model_dump(exclude={"genre_ids"}))

    # 요청에 포함된 장르를 가져오기
    genres = await Genre.filter(id__in=data.genre_ids)

    # 생성된 영화에 장르를 관계로 추가해주기
    await movie.genres.add(*genres)

    # fetch_related를 이용하여 장르를 미리 가져오기
    await movie.fetch_related("genres")

    return MovieResponse(
        id=movie.id,
        title=movie.title,
        overview=movie.overview,
        cast=movie.cast,
        runtime=movie.runtime,
        release_date=movie.release_date,
        genres=[genre.id for genre in movie.genres],
        genres_str=[genre.name for genre in movie.genres],
    )


@movie_router.get("", status_code=200)
async def get_movies(query_params: Annotated[MovieSearchParams, Query()]) -> list[MovieResponse]:
    movie_qs = Movie.filter().all()
    if query_params.genre_ids:
        movie_qs = movie_qs.filter(genres__id__in=query_params.genre_ids).distinct()

    if query_params.title:
        movie_qs = movie_qs.filter(title__icontains=query_params.title)

    movies = await movie_qs.prefetch_related("genres")

    return [
        MovieResponse(
            id=movie.id,
            title=movie.title,
            overview=movie.overview,
            cast=movie.cast,
            runtime=movie.runtime,
            release_date=movie.release_date,
            genres=[genre.id for genre in movie.genres],
            genres_str=[genre.name for genre in movie.genres],
        )
        for movie in movies
    ]


@movie_router.get("/{movie_id}", status_code=200)
async def get_movie(movie_id: int = Path(gt=0)) -> MovieResponse:
    movie = await Movie.get_or_none(id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404)
    await movie.fetch_related("genres")
    return MovieResponse(
        id=movie.id,
        title=movie.title,
        overview=movie.overview,
        cast=movie.cast,
        runtime=movie.runtime,
        release_date=movie.release_date,
        genres=[genre.id for genre in movie.genres],
        genres_str=[genre.name for genre in movie.genres],
    )


@movie_router.patch("/{movie_id}", status_code=200)
async def update_movie(data: MovieUpdateRequest, movie_id: int = Path(gt=0)) -> MovieResponse:
    movie = await Movie.get_or_none(id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    update_data = {key: value for key, value in data.model_dump(exclude={"genre_ids"}).items() if value is not None}
    for key, value in update_data.items():
        setattr(movie, key, value)
    await movie.save()

    if data.genre_ids is not None:
        genres = await Genre.filter(id__in=data.genre_ids)
        # 기존 장르 연결 제거
        await movie.genres.clear()
        # 새 장르 연결 추가
        await movie.genres.add(*genres)

    await movie.fetch_related("genres")

    return MovieResponse(
        id=movie.id,
        title=movie.title,
        overview=movie.overview,
        cast=movie.cast,
        runtime=movie.runtime,
        release_date=movie.release_date,
        genres=[genre.id for genre in movie.genres],
        genres_str=[genre.name for genre in movie.genres],
    )


@movie_router.delete("/{movie_id}", status_code=204)
async def delete_movie(movie_id: int = Path(gt=0)) -> None:
    movie = await Movie.get_or_none(id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404)
    await movie.genres.clear()
    await movie.delete()


@movie_router.post("/{movie_id}/poster_image")
async def register_poster_image(
    image: UploadFile, movie_id: int = Path(gt=0), file_service: FileUploadService = Depends()
) -> MovieResponse:
    movie = await Movie.get_or_none(id=movie_id)

    if movie is None:
        raise HTTPException(status_code=404)

    updated_movie = await file_service.movie_poster_image_upload(movie, image)
    await updated_movie.fetch_related("genres")

    return MovieResponse(
        id=updated_movie.id,
        title=updated_movie.title,
        overview=updated_movie.overview,
        cast=updated_movie.cast,
        runtime=updated_movie.runtime,
        genres=[genre.id for genre in updated_movie.genres],
        genres_str=[genre.name for genre in movie.genres],
        release_date=updated_movie.release_date,
        poster_image_url=updated_movie.poster_image_url,
    )
