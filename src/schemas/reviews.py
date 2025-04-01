from pydantic import BaseModel


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    title: str
    content: str
    review_image_url: str | None = None
