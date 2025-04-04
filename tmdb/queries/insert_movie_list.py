from typing import Any

from src.models.movies import Movie


async def insert_movie_list_to_mysql(movie_list: list[dict[str, Any]]) -> None:
	movie_list_orm_model = [
		Movie(
			external_id=movie["id"],
			title=movie["title"],
			overview=movie["overview"],
			cast=movie["cast"],
			runtime=movie["runtime"],
			release_date=movie["release_date"],
			poster_image_url=movie["poster_image_url"],
		) for movie in movie_list
	]
	try:
		await Movie.bulk_create(movie_list_orm_model)
		print("Movie list DB Insert Completed.")

	except Exception as e:
		print(f"영화 데이터 삽입중 에러 발생: {str(e)}")
