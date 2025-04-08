from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
)

from src.models.users import User
from src.schemas.users import (
    UserCreateRequest,
    UserLoginRequest,
    UserResponse,
    UserSearchParams,
    UserUpdateRequest,
)
from src.services.auth import AuthService
from src.services.file import FileUploadService

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("")
async def create_user(data: UserCreateRequest, auth_service: AuthService = Depends()) -> int:
    request_data = data.model_dump()
    request_data["hashed_password"] = auth_service.hash_password(request_data.pop("password"))
    user = await User.create(**request_data)
    return user.id


@user_router.get("")
async def get_all_users() -> list[UserResponse]:
    result = await User.filter().all()
    if not result:
        raise HTTPException(status_code=404)
    return [UserResponse(id=user.id, username=user.username, age=user.age, gender=user.gender) for user in result]


@user_router.post("/login", status_code=204)
async def login(data: UserLoginRequest, auth_service: AuthService = Depends()) -> Response:
    return await auth_service.login(data.username, data.password)


@user_router.get("/search")
async def search_users(query_params: Annotated[UserSearchParams, Query()]) -> list[UserResponse]:
    valid_query = {key: value for key, value in query_params.model_dump().items() if value is not None}
    filtered_users = await User.filter(**valid_query).all()
    if not filtered_users:
        raise HTTPException(status_code=404)
    return [
        UserResponse(id=user.id, username=user.username, age=user.age, gender=user.gender) for user in filtered_users
    ]


@user_router.get("/me")
async def get_user(request: Request) -> UserResponse:
    user = request.state.user
    return UserResponse(id=user.id, username=user.username, age=user.age, gender=user.gender)


@user_router.patch("/me")
async def update_user(data: UserUpdateRequest, request: Request, auth_service: AuthService = Depends()) -> UserResponse:
    user = request.state.user
    update_data = {key: value for key, value in data.model_dump().items() if value is not None}
    if "password" in update_data.keys():
        update_data["hashed_password"] = auth_service.hash_password(update_data.pop("password"))
    await user.update_from_dict(update_data)
    await user.save()
    return UserResponse(id=user.id, username=user.username, age=user.age, gender=user.gender)


@user_router.delete("/me")
async def delete_user(request: Request) -> dict[str, str]:
    user = request.state.user
    await user.delete()

    return {"detail": "Successfully Deleted."}


@user_router.post("/me/profile_image")
async def register_profile_image(
    request: Request, image: UploadFile, file_service: FileUploadService = Depends()
) -> UserResponse:
    updated_user = await file_service.user_profile_image_upload(request.state.user, image)

    return UserResponse(
        id=updated_user.id,
        username=updated_user.username,
        age=updated_user.age,
        gender=updated_user.gender,
        profile_image_url=updated_user.profile_image_url,
    )
