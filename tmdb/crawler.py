import asyncio

from tmdb.api_requests.get_movie_cast import get_movie_cast
from tmdb.api_requests.get_movie_details import get_movie_details
from tmdb.api_requests.get_movie_genres import get_movie_genres
from tmdb.api_requests.get_movie_list import get_movie_list
from tmdb.configs import config
from tmdb.configs.database import db_init
from tmdb.configs.params import SearchParams
from tmdb.queries.insert_genres import insert_genres
from tmdb.queries.insert_movie_genres import insert_movie_genres
from tmdb.queries.insert_movie_list import insert_movie_list_to_mysql
from tmdb.utils.image import get_poster_image_by_path
from tmdb.utils.validate_not_exist_genre_in_db import validate_not_exist_genre_in_db
from tmdb.utils.validate_not_exist_movie_in_db import validate_not_exist_movie_in_db


async def main() -> None:
    await db_init()
    print("장르를 TMDB로 부터 가져오는 중..")
    genres = await get_movie_genres()
    if genres:
        print(f"장르 가져오기 성공!: {genres}")
        print("장르 데이터가 이미 db에 존재하는지 확인하는 중..")
        validated_genre = await validate_not_exist_genre_in_db(genres=genres)
        if validated_genre:
            print("가져온 장르를 DB에 삽입하는 중..")
            await insert_genres(genres=genres)

    movie_list = []
    for i in range(config.START_SEARCH_PAGE, config.MAX_SEARCH_PAGE + 1):
        print(f"TMDB로부터 영화 데이터 {i}페이지 가져오는 중..")
        movie_list_data = await get_movie_list(search_params=SearchParams(page=i).to_dict())
        print(f"영화 가져오기 성공!: {movie_list_data}")
        movie_list += movie_list_data

    if movie_list:
        print("영화 데이터가 이미 db에 존재하는지 확인하는 중..")
        validated_movie_list = await validate_not_exist_movie_in_db(movie_list=movie_list)

        for movie in validated_movie_list:
            print(f"{movie["title"]} 영화의 cast(출연진)를 TMDB를 통해 가져오는 중..")
            casts = await get_movie_cast(movie_id=movie["id"])
            movie["cast"] = ", ".join([cast["name"] for cast in casts])

            print(f"{movie["title"]} 영화의 details를 TMDB를 통해 가져오는 중..")
            details = await get_movie_details(movie_id=movie["id"])
            movie["runtime"] = details["runtime"]

            print(f"{movie["title"]} 영화의 poster_image 를 다운로드 하는 중..")
            uploaded_image_url = await get_poster_image_by_path(movie["poster_path"])
            movie["poster_image_url"] = uploaded_image_url

        if validated_movie_list:
            print("가져온 영화를 DB에 삽입하는 중..")
            await insert_movie_list_to_mysql(movie_list=validated_movie_list)

            print("가져온 영화에 해당하는 장르를 DB에 삽입하는 중..")
            await insert_movie_genres(movie_list=validated_movie_list)

    print("모든 작업이 완료되었습니다.")


if __name__ == "__main__":
    asyncio.run(main())
