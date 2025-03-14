from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query

from src.models.users import UserModel
from src.schemas.users import (
    UserCreateRequest,
    UserResponse,
    UserSearchParams,
    UserUpdateRequest,
)

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("")
async def create_user(data: UserCreateRequest) -> int:
    user = UserModel.create(**data.model_dump())
    return user.id


@user_router.get("", response_model=list[UserResponse])
async def get_all_users() -> list[UserModel]:
    result = UserModel.all()
    if not result:
        raise HTTPException(status_code=404)
    return result


@user_router.get("/search", response_model=list[UserResponse])
async def search_users(query_params: Annotated[UserSearchParams, Query()]) -> list[UserModel]:
    valid_query = {key: value for key, value in query_params.model_dump().items() if value is not None}
    filtered_users = UserModel.filter(**valid_query)
    if not filtered_users:
        raise HTTPException(status_code=404)
    return filtered_users


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int = Path(gt=0)) -> UserModel:
    user = UserModel.get(id=user_id)
    if user is None:
        raise HTTPException(status_code=404)
    return user


@user_router.patch("/{user_id}", response_model=UserResponse)
async def update_user(data: UserUpdateRequest, user_id: int = Path(gt=0)) -> UserModel:
    user = UserModel.get(id=user_id)
    if user is None:
        raise HTTPException(status_code=404)
    user.update(**data.model_dump())
    return user


@user_router.delete("/{user_id}")
async def delete_user(user_id: int = Path(gt=0)) -> dict[str, str]:
    user = UserModel.get(id=user_id)
    if user is None:
        raise HTTPException(status_code=404)
    user.delete()

    return {"detail": f"User: {user_id}, Successfully Deleted."}
