from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.services.auth import AuthService


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            if request.url.path.startswith("/users"):
                if request.url.path not in ["/users/login", "/users", "/users/search"]:
                    request = await AuthService().get_current_user(request)
            response: Response = await call_next(request)
            return response
        except HTTPException as e:
            return JSONResponse({"detail": e.detail}, status_code=e.status_code)
        except Exception as e:
            return JSONResponse({"detail": str(e)}, status_code=500)
