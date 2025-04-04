from dataclasses import dataclass, asdict
from typing import Any

from tmdb.configs import config


@dataclass
class SearchParams:
    sort_by: str = "vote_count.desc"
    with_original_language: str = ""  # 영화에서 사용하는 언어
    with_genres: str = ""
    without_genres: str = ""
    include_adult: bool = False
    include_video: bool = False
    language: str = "ko"  # 응답 데이터의 언어 지정
    page: int = 1
    api_key: str | None = config.TMDB_API_KEY
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
