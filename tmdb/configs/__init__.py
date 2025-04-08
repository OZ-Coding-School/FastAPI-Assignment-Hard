from tmdb.configs.base import Config


def get_config() -> Config:
    return Config()


config = get_config()
