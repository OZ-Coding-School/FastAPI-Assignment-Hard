import httpx
from fastapi import status

from main import app
from src.models.movies import MovieModel


async def test_api_create_movie() -> None:
    # when
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/movies",
            json={
                "title": (title := "test"),
                "playtime": (playtime := 240),
                "genre": (genre := ["SF", "Romance", "Action"]),
            },
        )

    # then
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json["title"] == title
    assert response_json["playtime"] == playtime
    assert response_json["genre"] == genre


async def test_api_get_movies_when_query_param_is_nothing() -> None:
    # given
    MovieModel.create_dummy()

    # when
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/movies")

    # then
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 10
    assert response_json[0]["id"] == MovieModel._data[0].id
    assert response_json[0]["title"] == MovieModel._data[0].title
    assert response_json[0]["playtime"] == MovieModel._data[0].playtime
    assert response_json[0]["genre"] == MovieModel._data[0].genre


async def test_api_get_movies_when_query_param_is_not_none() -> None:
    # given
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            "/movies",
            json={"title": (title := "test"), "playtime": 240, "genre": (genre := ["SF", "Romance", "Action"])},
        )

        # when
        response = await client.get("/movies", params={"title": title, "genre": genre[0]})

    # then
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]["title"] == title
    assert response_json[0]["genre"] == genre


async def test_api_get_movie() -> None:
    # given
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            "/movies",
            json={
                "title": (title := "test"),
                "playtime": (playtime := 240),
                "genre": (genre := ["SF", "Romance", "Action"]),
            },
        )
        movie_id = create_response.json()["id"]
        # when
        response = await client.get(f"/movies/{movie_id}")

    # then
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["title"] == title
    assert response_json["playtime"] == playtime
    assert response_json["genre"] == genre


async def test_api_get_movie_when_movie_id_is_invalid() -> None:
    # when
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/movies/1232131311")

    # then
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_api_update_movie() -> None:
    # when
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            "/movies", json={"title": "test", "playtime": 240, "genre": ["SF", "Romance", "Action"]}
        )
        movie_id = create_response.json()["id"]

        # when
        response = await client.patch(
            f"/movies/{movie_id}",
            json={
                "title": (updated_title := "updated_title"),
                "playtime": (updated_playtime := 180),
                "genre": (updated_genre := ["Fantasy", "Romance", "Adventure"]),
            },
        )

    # then
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["title"] == updated_title
    assert response_json["playtime"] == updated_playtime
    assert response_json["genre"] == updated_genre


async def test_api_update_movie_when_movie_id_is_invalid() -> None:
    # when
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.patch(
            "/movies/1232131311",
            json={"title": "updated_title", "playtime": 180, "genre": ["Fantasy", "Romance", "Adventure"]},
        )

    # then
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_api_delete_movie() -> None:
    # when
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            "/movies", json={"title": "test", "playtime": 240, "genre": ["SF", "Romance", "Action"]}
        )
        movie_id = create_response.json()["id"]

        # when
        response = await client.delete(f"/movies/{movie_id}")

    # then
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_api_delete_movie_when_movie_id_is_invalid() -> None:
    # when
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete("/movies/1232131311")

    # then
    assert response.status_code == status.HTTP_404_NOT_FOUND
