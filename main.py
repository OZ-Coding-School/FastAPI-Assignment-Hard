from fastapi import FastAPI

from src.configs.database import initialize_tortoise
from src.middleware.auth import AuthMiddleware
from src.routers.movie_router import movie_router
from src.routers.user_router import user_router

app = FastAPI()

# include custom middleware
app.add_middleware(AuthMiddleware)

# include router in app
app.include_router(user_router)
app.include_router(movie_router)

# initialize_tortoise-orm
initialize_tortoise(app=app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
