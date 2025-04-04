from typing import Any

import httpx

from tmdb.configs import config


async def get_movie_cast(movie_id: int) -> Any:
    """ 특정 영화의 출연진 정보 가져오기 """
    async with httpx.AsyncClient() as client:
        url = f"{config.BASE_API_URL}/3/movie/{movie_id}/credits"
        params = {
            "api_key": config.TMDB_API_KEY,
            "language": "ko"
        }
        response = await client.get(url, params=params)
    if response.status_code != 200:
        return []
    
    data = response.json()
    return data["cast"][:5]
