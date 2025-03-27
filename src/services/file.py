import os

from fastapi import HTTPException, UploadFile

from src.configs import config
from src.models.movies import Movie
from src.models.users import User
from src.utils.file import (
    FileDoesNotExist,
    FileExtensionError,
    delete_file,
    upload_file,
    validate_image_extension,
)


class FileUploadService:
    def __init__(self) -> None:
        self.save_dir_path = config.MEDIA_DIR

    async def _image_upload(self, file: UploadFile, upload_dir: str, prev_image_url: str | None = None) -> str:
        """파일을 업로드하는 서비스 로직"""
        try:
            validate_image_extension(file)
            saved_path = await upload_file(file, os.path.join(self.save_dir_path, upload_dir))
            file_url = os.path.relpath(saved_path, self.save_dir_path)
        except FileExtensionError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        try:
            if prev_image_url:
                delete_file(os.path.join(self.save_dir_path, prev_image_url))
        except FileDoesNotExist:
            return file_url

        return saved_path

    async def user_profile_image_upload(self, user: User, file: UploadFile) -> User:
        upload_dir = "users/profile_images"
        saved_image_url = await self._image_upload(file, upload_dir, user.profile_image_url)
        user.profile_image_url = saved_image_url
        await user.save()

        return user

    async def movie_poster_image_upload(self, movie: Movie, file: UploadFile) -> Movie:
        upload_dir = "movies/poster_images"
        saved_image_url = await self._image_upload(file, upload_dir, movie.poster_image_url)
        movie.poster_image_url = saved_image_url
        await movie.save()

        return movie
