import httpx
from typing import Any

from tmdb.configs import config


async def get_movie_list(search_params: dict[str, Any]) -> Any:
	url = f"{config.BASE_API_URL}/3/discover/movie"
	
	async with httpx.AsyncClient() as client:
		response = await client.get(
			url=url,
			headers={
				"accept": "application/json",
			},
			params=search_params
		)
	
	if response.status_code != 200:
		return []
	
	data = response.json()
	return data["results"]
