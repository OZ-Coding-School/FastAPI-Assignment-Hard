from typing import Any

from src.models.movies import Movie


async def validate_not_exist_movie_in_db(movie_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    movie_ids = [movie["id"] for movie in movie_list]

    exist_movie_ids = await Movie.filter(external_id__in=movie_ids).values_list("external_id", flat=True)

    return [movie for movie in movie_list if movie["id"] not in exist_movie_ids]
