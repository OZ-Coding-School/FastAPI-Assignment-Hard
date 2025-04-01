from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Request,
    UploadFile,
)

from src.models.reviews import Review
from src.routers.movie_router import movie_router
from src.routers.user_router import user_router
from src.schemas.reviews import ReviewResponse
from src.services.file import FileUploadService

review_router = APIRouter(prefix="/reviews", tags=["reviews"])


@review_router.post("", status_code=201)
async def create_movie_review(
    request: Request,
    movie_id: int = Form(),
    title: str = Form(),
    content: str = Form(),
    review_image: UploadFile | None = File(None),
    file_service: FileUploadService = Depends(),
) -> ReviewResponse:
    data = {"user_id": request.state.user.id, "movie_id": movie_id, "title": title, "content": content}

    review = await Review(**data)

    if review_image:
        review = await file_service.review_image_upload(review, review_image)
    else:
        await review.save()

    assert hasattr(review, "user_id") and hasattr(review, "movie_id")

    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        movie_id=review.movie_id,
        title=review.title,
        content=review.content,
        review_image_url=review.review_image_url,
    )


@review_router.get("/{review_id}")
async def get_review(review_id: int = Path(gt=0)) -> ReviewResponse:
    review = await Review.get_or_none(id=review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review does not exist")

    assert hasattr(review, "user_id") and hasattr(review, "movie_id")

    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        movie_id=review.movie_id,
        title=review.title,
        content=review.content,
        review_image_url=review.review_image_url,
    )


@review_router.patch("/{review_id}")
async def update_review(
    request: Request,
    update_title: str | None = Form(None),
    update_content: str | None = Form(None),
    update_image: UploadFile | None = File(None),
    review_id: int = Path(gt=0),
    file_service: FileUploadService = Depends(),
) -> ReviewResponse:
    review = await Review.get_or_none(id=review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review does not exist")

    assert hasattr(review, "user_id") and hasattr(review, "movie_id")

    if review.user_id != request.state.user.id:
        raise HTTPException(status_code=403, detail="Only the review owner can update reviews")

    review.title = update_title if update_title is not None else review.title
    review.content = update_content if update_content is not None else review.content
    if update_image:
        review = await file_service.review_image_upload(review, update_image)
    else:
        await review.save()

    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        movie_id=review.movie_id,
        title=review.title,
        content=review.content,
        review_image_url=review.review_image_url,
    )


@review_router.delete("/{review_id}", status_code=204)
async def delete_review(request: Request, review_id: int = Path(gt=0)) -> None:
    review = await Review.filter(id=review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review does not exist")

    assert hasattr(review, "user_id")

    if review.user_id != request.state.user.id:
        raise HTTPException(status_code=403, detail="Only the review owner can delete review.")

    await review.delete()


@movie_router.get("/{movie_id}/reviews")
async def get_movie_reviews(movie_id: int = Path(gt=0)) -> list[ReviewResponse]:
    reviews = await Review.filter(movie_id=movie_id).all()
    result = []
    for review in reviews:
        assert hasattr(review, "user_id") and hasattr(review, "movie_id")

        result.append(
            ReviewResponse(
                id=review.id,
                user_id=review.user_id,
                movie_id=review.movie_id,
                title=review.title,
                content=review.content,
                review_image_url=review.review_image_url,
            )
        )

    return result


@user_router.get("/me/reviews")
async def get_my_reviews(request: Request) -> list[ReviewResponse]:
    reviews = await Review.filter(user_id=request.state.user.id).all()
    result = []
    for review in reviews:
        assert hasattr(review, "user_id") and hasattr(review, "movie_id")

        result.append(
            ReviewResponse(
                id=review.id,
                user_id=review.user_id,
                movie_id=review.movie_id,
                title=review.title,
                content=review.content,
                review_image_url=review.review_image_url,
            )
        )

    return result
