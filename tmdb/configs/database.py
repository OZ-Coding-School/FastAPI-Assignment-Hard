from tortoise import Tortoise
from src.configs import config
from src.configs.database import TORTOISE_APP_MODELS


async def db_init():
    await Tortoise.init(
        db_url=f"mysql://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{config.MYSQL_DB}",
        modules={"models": TORTOISE_APP_MODELS}  # 네 모델이 정의된 경로
    )
    await Tortoise.generate_schemas()
