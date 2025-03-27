import os.path

import httpx
from fastapi import status
from tortoise.contrib.test import TestCase

from main import app
from src.configs import config
from src.models.movies import Movie
from src.tests.utils.fake_file import fake_image


class TestMovieRouter(TestCase):
    async def test_api_create_movie(self) -> None:
        # when
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/movies",
                json={
                    "title": (title := "test"),
                    "plot": (plot := "test 중 입니다."),
                    "cast": (
                        cast := [
                            {"name": "lee2", "age": 23, "agency": "A actors", "gender": "male"},
                            {"name": "lee3", "age": 24, "agency": "B actors", "gender": "male"},
                        ]
                    ),
                    "playtime": (playtime := 240),
                    "genre": (genre := "SF"),
                },
            )

        # then
        assert response.status_code == status.HTTP_201_CREATED
        response_json = response.json()
        assert response_json["title"] == title
        assert response_json["plot"] == plot
        assert response_json["cast"] == cast
        assert response_json["playtime"] == playtime
        assert response_json["genre"] == genre

    async def test_api_get_movies_when_query_param_is_nothing(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            for i in range(3):
                await client.post(
                    "/movies",
                    json={
                        "title": f"test{i}",
                        "plot": "test 중 입니다.",
                        "cast": [
                            {"name": "lee2", "age": 23, "agency": "A actors", "gender": "male"},
                            {"name": "lee3", "age": 24, "agency": "B actors", "gender": "male"},
                        ],
                        "playtime": 240,
                        "genre": "SF",
                    },
                )

            # when
            response = await client.get("/movies")

        # then
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert len(response_json) == await Movie.filter().count()
        movies = await Movie.filter().order_by("id")
        assert response_json[0]["id"] == movies[0].id
        assert response_json[0]["title"] == movies[0].title

    async def test_api_get_movies_when_query_param_is_not_none(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            await client.post(
                "/movies",
                json={
                    "title": (title := "test"),
                    "plot": (plot := "test 중 입니다."),
                    "cast": (
                        cast := [
                            {"name": "lee2", "age": 23, "agency": "A actors", "gender": "male"},
                            {"name": "lee3", "age": 24, "agency": "B actors", "gender": "male"},
                        ]
                    ),
                    "playtime": (playtime := 240),
                    "genre": (genre := "SF"),
                },
            )

            # when
            response = await client.get("/movies", params={"title": title, "genre": genre})

        # then
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert len(response_json) == 1
        assert response_json[0]["title"] == title
        assert response_json[0]["plot"] == plot
        assert response_json[0]["cast"] == cast
        assert response_json[0]["genre"] == genre
        assert response_json[0]["playtime"] == playtime

    async def test_api_get_movie(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                "/movies",
                json={
                    "title": (title := "test"),
                    "plot": (plot := "test 중 입니다."),
                    "cast": (
                        cast := [
                            {"name": "lee2", "age": 23, "agency": "A actors", "gender": "male"},
                            {"name": "lee3", "age": 24, "agency": "B actors", "gender": "male"},
                        ]
                    ),
                    "playtime": (playtime := 240),
                    "genre": (genre := "SF"),
                },
            )
            movie_id = create_response.json()["id"]
            # when
            response = await client.get(f"/movies/{movie_id}")

        # then
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json["title"] == title
        assert response_json["plot"] == plot
        assert response_json["cast"] == cast
        assert response_json["playtime"] == playtime
        assert response_json["genre"] == genre

    async def test_api_get_movie_when_movie_id_is_invalid(self) -> None:
        # when
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/movies/1232131311")

        # then
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_api_update_movie(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                "/movies",
                json={
                    "title": "test",
                    "plot": "test 중 입니다.",
                    "cast": [
                        {"name": "lee2", "age": 23, "agency": "A actors", "gender": "male"},
                        {"name": "lee3", "age": 24, "agency": "B actors", "gender": "male"},
                    ],
                    "playtime": 240,
                    "genre": "SF",
                },
            )
            movie_id = create_response.json()["id"]

            # when
            response = await client.patch(
                f"/movies/{movie_id}",
                json={
                    "title": (updated_title := "updated_title"),
                    "playtime": (updated_playtime := 180),
                    "genre": (updated_genre := "Fantasy"),
                },
            )

        # then
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json["title"] == updated_title
        assert response_json["playtime"] == updated_playtime
        assert response_json["genre"] == updated_genre

    async def test_api_update_movie_when_movie_id_is_invalid(self) -> None:
        # when
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(
                "/movies/1232131311",
                json={"title": "updated_title", "playtime": 180, "genre": "Fantasy"},
            )

        # then
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_api_delete_movie(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                "/movies",
                json={
                    "title": "test",
                    "plot": "test 중 입니다.",
                    "cast": [
                        {"name": "lee2", "age": 23, "agency": "A actors", "gender": "male"},
                        {"name": "lee3", "age": 24, "agency": "B actors", "gender": "male"},
                    ],
                    "playtime": 240,
                    "genre": "SF",
                },
            )
            movie_id = create_response.json()["id"]

            # when
            response = await client.delete(f"/movies/{movie_id}")

        # then
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_api_delete_movie_when_movie_id_is_invalid(self) -> None:
        # when
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete("/movies/1232131311")

        # then
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_api_register_movie_poster_image(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                "/movies",
                json={
                    "title": "test",
                    "plot": "test 중 입니다.",
                    "cast": [
                        {"name": "lee2", "age": 23, "agency": "A actors", "gender": "male"},
                        {"name": "lee3", "age": 24, "agency": "B actors", "gender": "male"},
                    ],
                    "playtime": 240,
                    "genre": "SF",
                },
            )
            movie_id = create_response.json()["id"]

            # when
            response = await client.post(
                f"/movies/{movie_id}/poster_image",
                files={"image": ((image := "test_image.png"), fake_image(), "image/png")},
            )

        # then
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()

        assert f"movies/poster_images/{image.rsplit(".")[0]}" in response_json["poster_image_url"]
        assert image.rsplit(".")[1] in response_json["poster_image_url"]

        movie = await Movie.get(id=movie_id)
        assert response_json["poster_image_url"] == movie.poster_image_url

        saved_file_path = os.path.join(config.MEDIA_DIR, movie.poster_image_url)
        # 파일이 저장되었는지 확인
        assert os.path.exists(saved_file_path)

        # 리소스 정리
        os.remove(saved_file_path)

    async def test_api_register_movie_poster_image_when_movie_has_profile_image_url(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                "/movies",
                json={
                    "title": "test",
                    "plot": "test 중 입니다.",
                    "cast": [
                        {"name": "lee2", "age": 23, "agency": "A actors", "gender": "male"},
                        {"name": "lee3", "age": 24, "agency": "B actors", "gender": "male"},
                    ],
                    "playtime": 240,
                    "genre": "SF",
                },
            )
            movie_id = create_response.json()["id"]

            await client.post(
                f"/movies/{movie_id}/poster_image",
                files={"image": ("test_image.png", fake_image(), "image/png")},
            )

            movie = await Movie.get(id=movie_id)
            prev_image_url = movie.poster_image_url

            # 첫번째 파일이 저장되었는지 확인
            first_file_path = os.path.join(config.MEDIA_DIR, prev_image_url)
            assert os.path.exists(first_file_path)

            # when
            response = await client.post(
                f"/movies/{movie_id}/poster_image",
                files={"image": ((second_image := "test_image2.png"), fake_image(), "image/png")},
            )
        # then
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()

        # 파일경로와 확장자가 응답으로 반환된 poster_image_url에 포함되어 있는지 확인
        assert f"movies/poster_images/{second_image.rsplit(".")[0]}" in response_json["poster_image_url"]
        assert second_image.rsplit(".")[1] in response_json["poster_image_url"]

        await movie.refresh_from_db()
        # 응답과 Movie객체에 저장된 profile_image_url이 같은지 확인
        assert response_json["poster_image_url"] == movie.poster_image_url

        # 두번째로 등록한 파일이 저장되었는지 확인
        second_file_path = os.path.join(config.MEDIA_DIR, movie.poster_image_url)
        assert os.path.exists(second_file_path)

        # 첫번째로 등록한 파일이 삭제가 되었는지 확인
        assert not os.path.exists(first_file_path)

        # 리소스 정리
        os.remove(second_file_path)
