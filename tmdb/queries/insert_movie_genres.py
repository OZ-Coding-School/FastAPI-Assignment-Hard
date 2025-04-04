from typing import Any

from src.models.movies import Movie, Genre


async def insert_movie_genres(movie_list: list[dict[str, Any]]) -> None:
	for movie_data in movie_list:
		movie = await Movie.filter(external_id=movie_data["id"]).first()
		genres = await Genre.filter(external_id__in=movie_data["genre_ids"])
		try:
			await movie.genres.add(*genres)
		except Exception as e:
			print(f"영화의 장르 데이터 삽입중 에러 발생: {str(e)}")
	print("MovieGenre DB Insert Completed.")
