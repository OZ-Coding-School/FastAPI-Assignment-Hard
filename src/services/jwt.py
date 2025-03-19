from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import jwt
from fastapi import HTTPException, Response, status

SECRET_KEY = "asdasdasd1231asd12eadsd12easddasdqlkjlads"


class JWTService:
    def __init__(self) -> None:
        self.algorithm = "HS256"
        self.access_token_expires_in = 300
        self.refresh_token_expires_in = 3600 * 24
        self._secret_key = SECRET_KEY

    def _encode(self, data: dict[str, Any], expires_in: int) -> str:
        payload = data.copy()
        expire = datetime.now(ZoneInfo("Asia/Seoul")) + timedelta(seconds=expires_in)
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
            expires=self.access_token_expires_in,
            httponly=False,
            secure=False,
            samesite="lax",
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            expires=self.refresh_token_expires_in,
            httponly=False,
            secure=False,
            samesite="lax",
        )
        return response
