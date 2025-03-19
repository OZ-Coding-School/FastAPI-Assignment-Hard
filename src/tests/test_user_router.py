import httpx
from fastapi import status

from main import app
from src.models.users import UserModel
from src.schemas.users import GenderEnum


async def test_api_create_user() -> None:
    # given
    data = {"username": "testuser", "password": "password1234", "age": 20, "gender": GenderEnum.male}

    # when
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(url="/users", json=data)

    # then
    assert response.status_code == status.HTTP_200_OK
    created_user_id = response.json()
    created_user = UserModel.filter(id=created_user_id)[0]
    assert created_user
    assert created_user.username == data["username"]
    assert created_user.age == data["age"]
    assert created_user.gender == data["gender"]


async def test_api_login_user() -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # given
        create_response = await client.post(
            url="/users", json={"username": "testuser", "password": "password123", "age": 20, "gender": GenderEnum.male}
        )
        user_id = create_response.json()
        user = UserModel.get(id=user_id)

        assert isinstance(user, UserModel)
        # when
        response = await client.post(url="/users/login", json={"username": user.username, "password": "password123"})

        # then
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.cookies.get("access_token") is not None
        assert response.cookies.get("refresh_token") is not None


async def test_api_login_user_when_use_invalid_user_data() -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # when
        response = await client.post(url="/users/login", json={"username": "invalid", "password": "password12123"})

        # then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_api_get_all_users() -> None:
    # given
    UserModel.create_dummy()

    # when
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(url="/users")

    # then
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == len(UserModel._data)
    assert response_data[0]["id"] == UserModel._data[0].id
    assert response_data[0]["username"] == UserModel._data[0].username
    assert response_data[0]["age"] == UserModel._data[0].age
    assert response_data[0]["gender"] == UserModel._data[0].gender


async def test_api_get_all_users_when_user_not_found() -> None:
    # when
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(url="/users")

    # then
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_api_get_user() -> None:
    # given
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            url="/users", json={"username": "testuser", "password": "password123", "age": 20, "gender": GenderEnum.male}
        )
        user_id = create_response.json()
        user = UserModel.get(id=user_id)

        assert isinstance(user, UserModel)

        await client.post(url="/users/login", json={"username": user.username, "password": "password123"})
        # when
        response = await client.get(url="/users/me")

    # then
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert user.id == response_data["id"]
    assert user.username == response_data["username"]
    assert user.age == response_data["age"]
    assert user.gender == response_data["gender"]


async def test_api_get_user_when_user_is_not_logged_in() -> None:
    # when
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(url="/users/me")

    # then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_api_update_user() -> None:
    # given
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            url="/users", json={"username": "testuser", "password": "password123", "age": 20, "gender": GenderEnum.male}
        )
        user_id = create_response.json()
        user = UserModel.get(id=user_id)
        assert isinstance(user, UserModel)

        await client.post(url="/users/login", json={"username": user.username, "password": "password123"})

        # when
        response = await client.patch(
            url="/users/me",
            json={"username": (updated_username := "updated_username"), "age": (updated_age := 30)},
        )

    # then
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["username"] == updated_username
    assert response_data["age"] == updated_age
    assert user.username == response_data["username"]
    assert user.age == response_data["age"]


async def test_api_update_user_when_user_is_not_logged_in() -> None:
    # when
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.patch(url="/users/me", json={"username": "updated_user"})

    # then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_api_delete_user() -> None:
    # given
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            url="/users", json={"username": "testuser", "password": "password123", "age": 20, "gender": GenderEnum.male}
        )
        user_id = create_response.json()
        user = UserModel.get(id=user_id)
        assert isinstance(user, UserModel)

        await client.post(url="/users/login", json={"username": user.username, "password": "password123"})

        # when
        response = await client.delete(url="/users/me")

    # then
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["detail"] == "Successfully Deleted."


async def test_api_delete_user_when_user_is_not_logged_in() -> None:
    # when
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete(url="/users/me")

    # then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_api_search_user() -> None:
    # given
    UserModel.create_dummy()

    # when
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(url="/users/search", params={"username": (username := "dummy1")})

    # then
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data[0]["username"] == username


async def test_api_search_user_when_user_not_found() -> None:
    # when
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(url="/users/search?username=dasdad")

    # then
    assert response.status_code == status.HTTP_404_NOT_FOUND
