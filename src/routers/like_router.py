from fastapi import APIRouter, Path, Request

from src.models.likes import ReviewLike
from src.routers.review_router import review_router
from src.schemas.likes import (
    ReviewIsLikedResponse,
    ReviewLikeCountResponse,
    ReviewLikeResponse,
)

like_router = APIRouter(prefix="/likes", tags=["likes"])


@like_router.post("/reviews/{review_id}/like", status_code=200)
async def like_review(request: Request, review_id: int = Path(gt=0)) -> ReviewLikeResponse:
    review_like, _ = await ReviewLike.get_or_create(user_id=request.state.user.id, review_id=review_id)

    if not review_like.is_liked:
        review_like.is_liked = True
        await review_like.save()

    assert hasattr(review_like, "user_id") and hasattr(review_like, "review_id")

    return ReviewLikeResponse(
        id=review_like.id, user_id=review_like.user_id, review_id=review_like.review_id, is_liked=review_like.is_liked
    )


@like_router.post("/reviews/{review_id}/unlike", status_code=200)
async def unlike_review(request: Request, review_id: int = Path(gt=0)) -> ReviewLikeResponse:
    review_like = await ReviewLike.get_or_none(user_id=request.state.user.id, review_id=review_id)

    if review_like is None:
        return ReviewLikeResponse(user_id=request.state.user.id, review_id=review_id, is_liked=False)

    if review_like.is_liked:
        review_like.is_liked = False
        await review_like.save()

    assert hasattr(review_like, "user_id") and hasattr(review_like, "review_id")

    return ReviewLikeResponse(
        id=review_like.id, user_id=review_like.user_id, review_id=review_like.review_id, is_liked=review_like.is_liked
    )


@review_router.get("/{review_id}/like_count", status_code=200)
async def get_review_like_count(review_id: int = Path(gt=0)) -> ReviewLikeCountResponse:
    like_count = await ReviewLike.filter(review_id=review_id).count()
    return ReviewLikeCountResponse(review_id=review_id, like_count=like_count)


@review_router.get("/{review_id}/is_liked", status_code=200)
async def get_user_review_is_liked(request: Request, review_id: int = Path(gt=0)) -> ReviewIsLikedResponse:
    like = await ReviewLike.get_or_none(review_id=review_id, user_id=request.state.user.id)
    if like is None:
        return ReviewIsLikedResponse(review_id=review_id, is_liked=False)

    assert hasattr(like, "review_id")

    return ReviewIsLikedResponse(review_id=like.review_id, is_liked=like.is_liked)
