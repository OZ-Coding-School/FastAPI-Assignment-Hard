import pytest

from src.models.movies import MovieModel
from src.models.users import UserModel

TEST_BASE_URL = "http://test"


@pytest.fixture(scope="function", autouse=True)
def user_model_clear() -> None:
    UserModel.clear()
    MovieModel.clear()
