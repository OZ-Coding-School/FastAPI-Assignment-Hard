from typing import Any

from src.models.movies import Genre


async def insert_genres(genres: list[dict[str, Any]]) -> None:
    genre_models = [Genre(name=genre["name"], external_id=genre["id"]) for genre in genres]
    try:
        await Genre.bulk_create(genre_models)
        print("Genres DB Insert Completed.")
    except Exception as e:
        print(f"영화 데이터 삽입중 에러 발생: {str(e)}")
