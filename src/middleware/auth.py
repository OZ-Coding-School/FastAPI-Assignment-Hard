import re

from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.services.auth import AuthService

NEED_AUTH_REGEX_URL = [
    r"^/users/me$",
    r"^/users/me/profile_image$",
    r"^/users/me/reviews$",
    r"^/reviews$",
    r"^/reviews/\d+$",
    r"^/reviews/\d+/is_liked$",
    r"^/likes/reviews/\d+/like$",
    r"^/likes/reviews/\d+/unlike$",
]


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            for url in NEED_AUTH_REGEX_URL:
                if re.match(url, request.url.path):
                    request = await AuthService().get_current_user(request)
                    break
            response: Response = await call_next(request)
            return response
        except HTTPException as e:
            return JSONResponse({"detail": e.detail}, status_code=e.status_code)
        except Exception as e:
            return JSONResponse({"detail": str(e)}, status_code=500)
