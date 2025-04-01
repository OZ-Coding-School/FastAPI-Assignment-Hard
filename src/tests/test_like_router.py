import httpx
from httpx import AsyncClient
from tortoise.contrib.test import TestCase

from main import app
from src.models.likes import ReviewLike
from src.models.movies import Movie
from src.models.reviews import Review
from src.models.users import GenderEnum, User
from src.services.auth import AuthService


class LikeRouterTestCase(TestCase):
    async def create_user(self, username: str, password: str) -> User:
        user = await User.create(
            username=username,
            hashed_password=AuthService().hash_password(password),
            age=25,
            gender=GenderEnum.MALE,
        )
        return user

    async def create_movie(self) -> Movie:
        movie = await Movie.create(
            title="test",
            plot="Testing...",
            cast=[
                {"name": "lee", "age": 23, "agency": "A actors", "gender": "male"},
                {"name": "lee2", "age": 24, "agency": "B actors", "gender": "male"},
            ],
            playtime=240,
            genre="SF",
        )
        return movie

    async def create_review(self, movie_id: int, user_id: int) -> Review:
        review = await Review.create(user_id=user_id, movie_id=movie_id, title="test review", content="test review...")
        return review

    async def user_login(self, client: AsyncClient, username: str, password: str) -> None:
        await client.post("/users/login", json={"username": username, "password": password})

    async def test_api_review_like(self) -> None:
        # given
        user = await self.create_user(username="testuser", password="password1234")
        movie = await self.create_movie()
        review = await self.create_review(movie_id=movie.id, user_id=user.id)

        other_user = await self.create_user(username=(username := "other_user"), password=(password := "password1234"))

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            await client.post(url="/users/login", json={"username": username, "password": password})

            # when
            response = await client.post(url=f"/likes/reviews/{review.id}/like")

            # then
            assert response.status_code == 200
            response_json = response.json()

            assert response_json["user_id"] == other_user.id
            assert response_json["review_id"] == review.id
            assert response_json["is_liked"]

    async def test_api_review_unlike(self) -> None:
        # given
        user = await self.create_user(username="testuser", password="password1234")
        movie = await self.create_movie()
        review = await self.create_review(movie_id=movie.id, user_id=user.id)

        other_user = await self.create_user(username=(username := "other_user"), password=(password := "password1234"))

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            await client.post(url="/users/login", json={"username": username, "password": password})

            like_response = await client.post(url=f"/likes/reviews/{review.id}/like")
            like_response_json = like_response.json()

            response = await client.post(url=f"/likes/reviews/{review.id}/unlike")
            # then
            assert response.status_code == 200
            response_json = response.json()

            assert response_json["id"] == like_response_json["id"]
            assert response_json["user_id"] == other_user.id
            assert response_json["review_id"] == review.id
            assert response_json["is_liked"] is False

    async def test_api_review_unlike_when_review_like_object_is_none(self) -> None:
        # given
        user = await self.create_user(username="testuser", password="password1234")
        movie = await self.create_movie()
        review = await self.create_review(movie_id=movie.id, user_id=user.id)

        other_user = await self.create_user(username=(username := "other_user"), password=(password := "password1234"))

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            await client.post(url="/users/login", json={"username": username, "password": password})

            # when
            response = await client.post(url=f"/likes/reviews/{review.id}/unlike")

            # then
            assert response.status_code == 200
            response_json = response.json()

            assert response_json["id"] is None
            assert response_json["user_id"] == other_user.id
            assert response_json["review_id"] == review.id
            assert response_json["is_liked"] is False

    async def test_api_review_like_when_review_status_is_false(self) -> None:
        # given
        user = await self.create_user(username="testuser", password="password1234")
        movie = await self.create_movie()
        review = await self.create_review(movie_id=movie.id, user_id=user.id)
        other_user = await self.create_user(username=(username := "other_user"), password=(password := "password1234"))

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            await client.post(url="/users/login", json={"username": username, "password": password})

            like_response = await client.post(url=f"/likes/reviews/{review.id}/like")
            like_response_json = like_response.json()

            await client.post(url=f"/likes/reviews/{review.id}/unlike")

            response = await client.post(url=f"/likes/reviews/{review.id}/like")

            assert response.status_code == 200
            response_json = response.json()

            assert response_json["id"] == like_response_json["id"]
            assert response_json["user_id"] == other_user.id
            assert response_json["review_id"] == review.id
            assert response_json["is_liked"]

    async def test_api_get_review_like_count(self) -> None:
        # given
        await User.bulk_create(
            [
                User(
                    username=f"testuser{i}",
                    hashed_password=AuthService().hash_password("password1234"),
                    age=25 + i,
                    gender=GenderEnum.MALE,
                )
                for i in range(1, 4)
            ]
        )
        users = await User.filter().all()
        movie = await self.create_movie()

        review = await self.create_review(movie_id=movie.id, user_id=users[0].id)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            review_like_responses = []
            for _ in users:
                response = await client.post(f"/likes/reviews/{review.id}/like")
                response_json = response.json()
                review_like_responses.append(response_json)

            response = await client.get(f"/reviews/{review.id}/like_count")

            assert response.status_code == 200
            response_json = response.json()

            assert response_json["review_id"] == review.id
            assert response_json["like_count"] == await ReviewLike.filter(review_id=review.id).count()

    async def test_api_get_whether_user_liked_the_review_when_user_not_like_review(self) -> None:
        # given
        user = await self.create_user(username=(username := "testuser"), password=(password := "password1234"))
        movie = await self.create_movie()
        review = await self.create_review(movie_id=movie.id, user_id=user.id)

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            await client.post(url="/users/login", json={"username": username, "password": password})

            response = await client.get(url=f"/reviews/{review.id}/is_liked")

            assert response.status_code == 200
            response_json = response.json()

            assert response_json["review_id"] == review.id
            assert response_json["is_liked"] is False

    async def test_api_get_whether_user_liked_the_review_when_user_like_review(self) -> None:
        # given
        user = await self.create_user(username=(username := "testuser"), password=(password := "password1234"))
        movie = await self.create_movie()
        review = await self.create_review(movie_id=movie.id, user_id=user.id)

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            await client.post(url="/users/login", json={"username": username, "password": password})
            await client.post(url=f"/likes/reviews/{review.id}/like")

            response = await client.get(url=f"/reviews/{review.id}/is_liked")

            assert response.status_code == 200
            response_json = response.json()

            assert response_json["review_id"] == review.id
            assert response_json["is_liked"]
