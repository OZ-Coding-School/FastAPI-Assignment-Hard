from fastapi import HTTPException, Request, Response
from passlib.context import CryptContext

from src.models.users import User
from src.services.jwt import JWTService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self) -> None:
        self.jwt_service = JWTService()

    async def login(self, username: str, password: str) -> Response:
        user = await self.authenticate(username, password)

        access_token = self.jwt_service.create_access_token(data={"user_id": user.id})
        refresh_token = self.jwt_service.create_refresh_token(data={"user_id": user.id})

        response = self._get_login_response(access_token, refresh_token)

        return response

    def _get_login_response(self, access_token: str, refresh_token: str) -> Response:
        response = Response(status_code=204)
        self.jwt_service.attach_jwt_token_in_response_cookie(access_token, refresh_token, response)
        return response

    async def get_current_user(self, request: Request) -> Request:
        access_token = request.cookies.get("access_token")
        if not access_token:
            raise HTTPException(status_code=401, detail="This Request requires an access token.")

        decoded = self.jwt_service._decode(access_token)

        user = await User.get_or_none(id=decoded["user_id"])
        if not user:
            raise HTTPException(status_code=401, detail="Invalid Access Token.")

        request.state.user = user

        return request

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def authenticate(self, username: str, password: str) -> User:
        user = await User.get_or_none(username=username)
        if user is None:
            raise HTTPException(status_code=401, detail=f"username: {username} - not found.")
        if not self.verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="password incorrect.")
        return user
