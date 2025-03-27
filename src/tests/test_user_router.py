import os

import httpx
from fastapi import status
from tortoise.contrib.test import TestCase

from main import app
from src.configs import config
from src.models.users import GenderEnum, User
from src.services.auth import AuthService
from src.services.jwt import JWTService
from src.tests.utils.fake_file import fake_image, fake_txt_file
from src.utils.file import IMAGE_EXTENSIONS


class TestUserRouter(TestCase):
    async def test_api_create_user(self) -> None:
        # given
        data = {"username": "testuser", "password": "password1234", "age": 20, "gender": GenderEnum.MALE}

        # when
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(url="/users", json=data)

        # then
        assert response.status_code == status.HTTP_200_OK
        created_user_id = response.json()
        created_user = await User.get(id=created_user_id)
        assert created_user
        assert created_user.username == data["username"]
        assert created_user.age == data["age"]
        assert created_user.gender == data["gender"]

    async def test_api_login_user(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # given
            create_response = await client.post(
                url="/users",
                json={
                    "username": "testuser",
                    "password": (password := "password123"),
                    "age": 20,
                    "gender": GenderEnum.MALE,
                },
            )
            user_id = create_response.json()
            user = await User.get(id=user_id)

            # when
            response = await client.post(url="/users/login", json={"username": user.username, "password": password})

            # then
            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert response.cookies.get("access_token") is not None
            assert response.cookies.get("refresh_token") is not None

    async def test_api_login_user_when_use_invalid_username(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # when
            response = await client.post(
                url="/users/login", json={"username": (username := "invalid"), "password": "password12123"}
            )

            # then
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["detail"] == f"username: {username} - not found."

    async def test_api_login_user_when_use_invalid_password(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # given
            await client.post(
                url="/users",
                json={
                    "username": (username := "testuser"),
                    "password": "password123",
                    "age": 20,
                    "gender": GenderEnum.MALE,
                },
            )
            # when
            response = await client.post(url="/users/login", json={"username": username, "password": "password12123"})

            # then
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["detail"] == "password incorrect."

    async def test_api_get_all_users(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            for i in range(3):
                await client.post(
                    url="/users",
                    json={
                        "username": f"testuser{i}",
                        "password": "password123",
                        "age": 20 + i,
                        "gender": GenderEnum.MALE,
                    },
                )

            # when
            response = await client.get(url="/users")

        # then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == await User.filter().count()
        created_users = await User.filter().order_by("id")
        assert response_data[0]["id"] == created_users[0].id
        assert response_data[0]["username"] == created_users[0].username
        assert response_data[0]["age"] == created_users[0].age
        assert response_data[0]["gender"] == created_users[0].gender

    async def test_api_get_all_users_when_user_not_found(self) -> None:
        # when
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(url="/users")

        # then
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_api_get_user(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                url="/users",
                json={
                    "username": "testuser",
                    "password": (password := "password123"),
                    "age": 20,
                    "gender": GenderEnum.MALE,
                },
            )
            user_id = create_response.json()
            user = await User.get(id=user_id)

            await client.post(url="/users/login", json={"username": user.username, "password": password})
            # when
            response = await client.get(url="/users/me")

        # then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert user.id == response_data["id"]
        assert user.username == response_data["username"]
        assert user.age == response_data["age"]
        assert user.gender == response_data["gender"]

    async def test_api_get_user_when_token_has_invalid_value(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(url="/users/me", cookies={"access_token": "invalid"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_api_get_user_when_token_encoded_using_invalid_user_id(self) -> None:
        access_token = JWTService().create_access_token({"user_id": 31241312312})
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(url="/users/me", cookies={"access_token": access_token})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid Access Token."

    async def test_api_get_user_when_user_is_not_logged_in(self) -> None:
        # when
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(url="/users/me")

        # then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_api_update_user(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                url="/users",
                json={
                    "username": "testuser",
                    "password": (password := "password123"),
                    "age": 20,
                    "gender": GenderEnum.MALE,
                },
            )
            user_id = create_response.json()
            user = await User.get(id=user_id)

            await client.post(url="/users/login", json={"username": user.username, "password": password})

            # when
            response = await client.patch(
                url="/users/me",
                json={
                    "username": (updated_username := "updated_username"),
                    "age": (updated_age := 30),
                    "password": (password := "updated_password123"),
                },
            )

        # then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        await user.refresh_from_db()
        assert response_data["username"] == updated_username
        assert response_data["age"] == updated_age
        assert user.username == response_data["username"]
        assert user.age == response_data["age"]
        assert AuthService().verify_password(plain_password=password, hashed_password=user.hashed_password)

    async def test_api_update_user_when_user_is_not_logged_in(self) -> None:
        # when
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(url="/users/me", json={"username": "updated_user"})

        # then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_api_delete_user(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                url="/users",
                json={
                    "username": "testuser",
                    "password": (password := "password123"),
                    "age": 20,
                    "gender": GenderEnum.MALE,
                },
            )
            user_id = create_response.json()
            user = await User.get(id=user_id)

            await client.post(url="/users/login", json={"username": user.username, "password": password})

            # when
            response = await client.delete(url="/users/me")

        # then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["detail"] == "Successfully Deleted."

    async def test_api_delete_user_when_user_is_not_logged_in(self) -> None:
        # when
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(url="/users/me")

        # then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_api_search_user(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            for i in range(3):
                await client.post(
                    url="/users",
                    json={
                        "username": f"testuser{i}",
                        "password": "password123",
                        "age": 20 + i,
                        "gender": GenderEnum.MALE,
                    },
                )
            # when
            response = await client.get(url="/users/search", params={"username": (username := "testuser1")})

        # then
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == 1
        assert response_data[0]["username"] == username

    async def test_api_search_user_when_user_not_found(self) -> None:
        # when
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(url="/users/search?username=dasdad")

        # then
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_api_register_user_profile_image(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                url="/users",
                json={
                    "username": "testuser",
                    "password": (password := "password123"),
                    "age": 20,
                    "gender": GenderEnum.MALE,
                },
            )
            user_id = create_response.json()
            user = await User.get(id=user_id)

            await client.post(url="/users/login", json={"username": user.username, "password": password})

            # when
            response = await client.post(
                "/users/me/profile_image", files={"image": ((image := "test_image.png"), fake_image(), "image/png")}
            )

        # then
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()

        assert f"users/profile_images/{image.rsplit(".")[0]}" in response_json["profile_image_url"]
        assert image.rsplit(".")[1] in response_json["profile_image_url"]

        await user.refresh_from_db()
        assert response_json["profile_image_url"] == user.profile_image_url

        saved_file_path = os.path.join(config.MEDIA_DIR, user.profile_image_url)
        # 파일이 저장되었는지 확인
        assert os.path.exists(saved_file_path)

        # 리소스 정리
        os.remove(saved_file_path)

    async def test_api_register_user_profile_image_when_file_has_unavailable_extension(self) -> None:
        # given
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                url="/users",
                json={
                    "username": "testuser",
                    "password": (password := "password123"),
                    "age": 20,
                    "gender": GenderEnum.MALE,
                },
            )
            user_id = create_response.json()
            user = await User.get(id=user_id)

            await client.post(url="/users/login", json={"username": user.username, "password": password})

            # when
            response = await client.post(
                "/users/me/profile_image", files={"image": ("test_file.txt", fake_txt_file(), "text/plain")}
            )

        # then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()

        assert response_json["detail"] == f"not allowed extension. available extensions: {IMAGE_EXTENSIONS}"
