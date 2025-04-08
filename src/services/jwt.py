from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import jwt
from fastapi import HTTPException, Response, status

from src.configs import config


class JWTService:
    def __init__(self) -> None:
        self.algorithm = config.JWT_ALGORITHM
        self.access_token_expires_in = config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expires_in = config.JWT_REFRESH_TOKEN_EXPIRE_MINUTES
        self._secret_key = config.SECRET_KEY

    def _encode(self, data: dict[str, Any], expires_in: int) -> str:
        payload = data.copy()
        expire = datetime.now(ZoneInfo("Asia/Seoul")) + timedelta(minutes=expires_in)
        payload.update({"exp": expire})
        return jwt.encode(payload, self._secret_key, algorithm=self.algorithm)

    def _decode(self, token: str) -> Any:
        try:
            return jwt.decode(token, self._secret_key, algorithms=self.algorithm)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    def _create_token(self, data: dict[str, Any], expires_in: int) -> str:
        return self._encode(data=data, expires_in=expires_in)

    def create_access_token(self, data: dict[str, Any]) -> str:
        return self._create_token(data, self.access_token_expires_in)

    def create_refresh_token(self, data: dict[str, Any]) -> str:
        return self._create_token(data, self.refresh_token_expires_in)

    def attach_jwt_token_in_response_cookie(
        self, access_token: str, refresh_token: str, response: Response
    ) -> Response:
        response.set_cookie(
            key="access_token",
            value=access_token,
            expires=self.access_token_expires_in * 60,
            httponly=False,
            secure=False,
            samesite="lax",
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            expires=self.refresh_token_expires_in * 60,
            httponly=False,
            secure=False,
            samesite="lax",
        )
        return response
