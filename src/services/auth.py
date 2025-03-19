from fastapi import HTTPException, Request, Response, status

from src.models.users import UserModel
from src.services.jwt import JWTService


class AuthService:
    def __init__(self) -> None:
        self.jwt_service = JWTService()

    def login(self, username: str, password: str) -> Response:
        user = UserModel.authenticate(username, password)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

        access_token = self.jwt_service.create_access_token(data={"user_id": user.id})
        refresh_token = self.jwt_service.create_refresh_token(data={"user_id": user.id})

        response = self._get_login_response(access_token, refresh_token)

        return response

    def _get_login_response(self, access_token: str, refresh_token: str) -> Response:
        response = Response(status_code=204)
        self.jwt_service.attach_jwt_token_in_response_cookie(access_token, refresh_token, response)
        return response

    def get_current_user(self, request: Request) -> Request:
        access_token = request.cookies.get("access_token")
        if not access_token:
            raise HTTPException(status_code=401, detail="Unauthorized.")

        decoded = self.jwt_service._decode(access_token)

        user = UserModel.get(id=decoded["user_id"])
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized.")

        request.state.user = user

        return request
