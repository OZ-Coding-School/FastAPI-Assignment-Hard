import httpx
from fastapi import status
from tortoise.contrib.test import TestCase

from main import app
from src.models.movies import Movie
from src.models.users import GenderEnum, User
from src.services.auth import AuthService
from src.tests.utils.cleanup_test_files import remove_test_files
from src.tests.utils.fake_file import fake_image


class TestReviewRouter(TestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.movies = [
            await Movie.create(
                title=f"test{i}",
                overview="test 중 입니다.",
                cast="lee byeong heon, choi min sik",
                runtime=240,
                genre_ids=[1, 2],
                release_date="2021-02-01",
            )
            for i in range(1, 4)
        ]
        self.user = await User.create(
            username="testuser",
            hashed_password=AuthService().hash_password((plain_password := "password1234")),
            age=25,
            gender=GenderEnum.MALE,
        )
        self.user_plain_password = plain_password

    async def asyncTearDown(self) -> None:
        remove_test_files()
        await super().asyncTearDown()

    async def _test_user_login(self, client: httpx.AsyncClient) -> None:
        await client.post(
            url="/users/login", json={"username": self.user.username, "password": self.user_plain_password}
        )

    async def test_create_review(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 유저 로그인
            await self._test_user_login(client=client)

            # when
            response = await client.post(
                "/reviews",
                data={
                    "movie_id": self.movies[0].id,
                    "title": (review_title := "test review"),
                    "content": (review_content := "test review content"),
                },
                files={"review_image": ((review_image := "test_image.png"), fake_image(), "image/png")},
            )

        assert response.status_code == status.HTTP_201_CREATED
        response_json = response.json()
        assert response_json["user_id"] == self.user.id
        assert response_json["movie_id"] == self.movies[0].id
        assert response_json["title"] == review_title
        assert response_json["content"] == review_content
        assert f"reviews/images/{review_image.rsplit(".")[0]}" in response_json["review_image_url"]
        assert review_image.rsplit(".")[1] in response_json["review_image_url"]

    async def test_get_review(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 유저 로그인
            await self._test_user_login(client=client)

            create_response = await client.post(
                "/reviews",
                data={
                    "movie_id": self.movies[0].id,
                    "title": (review_title := "test review"),
                    "content": (review_content := "test review content"),
                },
                files={"review_image": ((review_image := "test_image.png"), fake_image(), "image/png")},
            )
            review_id = create_response.json()["id"]

            # when
            response = await client.get(f"/reviews/{review_id}")

            assert response.status_code == status.HTTP_200_OK
            response_json = response.json()
            assert response_json["movie_id"] == self.movies[0].id
            assert response_json["user_id"] == self.user.id
            assert response_json["title"] == review_title
            assert response_json["content"] == review_content
            assert f"reviews/images/{review_image.rsplit(".")[0]}" in response_json["review_image_url"]
            assert review_image.rsplit(".")[1] in response_json["review_image_url"]

    async def test_get_review_when_review_does_not_exist(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 유저 로그인
            await client.post(
                url="/users/login", json={"username": self.user.username, "password": self.user_plain_password}
            )
            response = await client.get("/reviews/378912739121")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_review(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 유저 로그인
            await self._test_user_login(client=client)

            create_response = await client.post(
                "/reviews",
                data={
                    "movie_id": self.movies[0].id,
                    "title": "test review",
                    "content": "test review content",
                },
                files={"review_image": ("test_image.png", fake_image(), "image/png")},
            )

            create_response_json = create_response.json()
            review_id = create_response_json["id"]

            update_response = await client.patch(
                f"/reviews/{review_id}",
                data={
                    "update_title": (updated_title := "updated title"),
                    "update_content": (updated_content := "updated content"),
                },
                files={"update_image": ((updated_image := "updated_test_image.png"), fake_image(), "image/png")},
            )

        assert update_response.status_code == status.HTTP_200_OK
        response_json = update_response.json()
        assert response_json["id"] == review_id
        assert response_json["user_id"] == self.user.id
        assert response_json["movie_id"] == self.movies[0].id
        assert response_json["title"] == updated_title
        assert response_json["content"] == updated_content
        assert f"reviews/images/{updated_image.rsplit(".")[0]}" in response_json["review_image_url"]
        assert updated_image.rsplit(".")[1] in response_json["review_image_url"]

    async def test_update_review_when_review_does_not_exist(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 유저 로그인
            await self._test_user_login(client=client)

            response = await client.patch("/reviews/378912739121", data={"update_title": "updated title"})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_review(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 유저 로그인
            await self._test_user_login(client=client)

            create_response = await client.post(
                "/reviews",
                data={
                    "movie_id": self.movies[0].id,
                    "title": "test review",
                    "content": "test review content",
                },
                files={"review_image": ("test_image.png", fake_image(), "image/png")},
            )

            create_response_json = create_response.json()
            review_id = create_response_json["id"]

            delete_response = await client.delete(f"/reviews/{review_id}")

        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_review_when_review_does_not_exist(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 유저 로그인
            await self._test_user_login(client=client)

            response = await client.delete("/reviews/378912739121")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_movie_reviews(self) -> None:
        # given
        users = [
            await User.create(
                username=f"testuser{i}",
                hashed_password=AuthService().hash_password("password1234"),
                age=25 + i,
                gender=GenderEnum.MALE,
            )
            for i in range(1, 4)
        ]

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 유저 로그인
            reviews = []
            for i, user in enumerate(users):
                await client.post("/users/login", json={"username": user.username, "password": "password1234"})

                create_reponse = await client.post(
                    "/reviews",
                    data={
                        "movie_id": self.movies[0].id,
                        "title": f"test review {i}",
                        "content": f"test review content {i}",
                    },
                    files={"review_image": (f"test_image {i}.png", fake_image(), "image/png")},
                )
                reviews.append(create_reponse.json())

            # when
            response = await client.get(f"/movies/{self.movies[0].id}/reviews")

            assert response.status_code == status.HTTP_200_OK
            response_json = response.json()
            for i, review in enumerate(response_json):
                assert review["movie_id"] == self.movies[0].id
                assert review["user_id"] == users[i].id
                assert review["title"] == reviews[i]["title"]
                assert review["content"] == reviews[i]["content"]
                assert reviews[i]["review_image_url"] == review["review_image_url"]

    async def test_get_my_reviews(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # 유저 로그인
            await self._test_user_login(client=client)

            reviews = []
            for i, movie in enumerate(self.movies):
                create_reponse = await client.post(
                    "/reviews",
                    data={
                        "movie_id": movie.id,
                        "title": f"test review {i}",
                        "content": f"test review content {i}",
                    },
                    files={"review_image": (f"test_image {i}.png", fake_image(), "image/png")},
                )
                reviews.append(create_reponse.json())

            # when
            response = await client.get("/users/me/reviews")

            assert response.status_code == status.HTTP_200_OK
            response_json = response.json()
            for i, review in enumerate(response_json):
                assert review["movie_id"] == self.movies[i].id
                assert review["user_id"] == self.user.id
                assert review["title"] == reviews[i]["title"]
                assert review["content"] == reviews[i]["content"]
                assert review["review_image_url"] == reviews[i]["review_image_url"]
