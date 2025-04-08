from typing import Any

import httpx

from tmdb.configs import config


async def get_movie_genres() -> Any:
    async with httpx.AsyncClient() as client:
        url = f"{config.BASE_API_URL}/3/genre/movie/list"

        headers = {
            "accept": "application/json",
        }

        params = {"language": "en-US", "api_key": config.TMDB_API_KEY}

        response = await client.get(url=url, headers=headers, params=params)
        response_json = response.json()

    if response.status_code != 200:
        print(f"장르를 가져오는 중 에러 발생: {response.text}")
        return []

    return response_json["genres"]
