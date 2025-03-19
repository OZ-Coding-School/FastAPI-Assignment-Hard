from fastapi import FastAPI

from src.middleware.auth import AuthMiddleware
from src.models.movies import MovieModel
from src.models.users import UserModel
from src.routers.movie_router import movie_router
from src.routers.user_router import user_router

app = FastAPI()

# include custom middleware
app.add_middleware(AuthMiddleware)
# include router in app
app.include_router(user_router)
app.include_router(movie_router)

# create dummy for test
UserModel.create_dummy()
MovieModel.create_dummy()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
