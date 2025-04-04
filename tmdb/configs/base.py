import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")
	TMDB_API_KEY: str
	
	START_SEARCH_PAGE: int = 58
	MAX_SEARCH_PAGE: int = 60
	BASE_API_URL: str = "https://api.themoviedb.org"
	BASE_IMAGE_URL: str = "https://image.tmdb.org/t/p/w500"
	
	BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
	MEDIA_DIR: str = os.path.join(BASE_DIR, "media")
	
	MYSQL_HOST: str = "localhost"
	MYSQL_PORT: int = 3306
	MYSQL_USER: str = "root"
	MYSQL_PASSWORD: str = "1234"
	MYSQL_DB: str = "fastapi_assignment"
	MYSQL_CONNECT_TIMEOUT: int = 5
	CONNECTION_POOL_MAXSIZE: int = 10
