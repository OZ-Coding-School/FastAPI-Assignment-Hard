from typing import Any

from src.models.movies import Genre


async def validate_not_exist_genre_in_db(genres: list[dict[str, Any]]) -> list[dict[str, Any]]:
    genre_ids = [genre["id"] for genre in genres]

    exist_genre_ids = await Genre.filter(external_id__in=genre_ids).values_list("external_id", flat=True)

    return [genre for genre in genres if genre["id"] not in exist_genre_ids]
