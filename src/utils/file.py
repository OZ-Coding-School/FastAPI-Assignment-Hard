import os
import uuid
from pathlib import Path
from typing import Union

from fastapi import UploadFile

IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif"]


class FileExtensionError(Exception):
    def __init__(self, valid_extensions: list[str]):
        super().__init__(f"not allowed extension. available extensions: {valid_extensions}")


class FileDoesNotExist(Exception):
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(f"file does not exist: {file_path}")


async def upload_file(file: UploadFile, upload_dir_path: str) -> str:
    # 파일 확장자 분리
    assert file.filename
    filename, ext = file.filename.rsplit(".", 1) if "." in file.filename else (file.filename, "")

    # UUID가 추가된 유니크한 파일명 생성
    unique_filename = f"{filename}_{uuid.uuid4().hex}.{ext}" if ext else f"{filename}_{uuid.uuid4().hex}"

    os.makedirs(upload_dir_path, exist_ok=True)  # 업로드 폴더가 없으면 생성

    file_path = f"{upload_dir_path}/{unique_filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return file_path


def delete_file(file_path: str) -> None:
    if not os.path.exists(file_path):
        raise FileDoesNotExist(file_path)

    os.remove(file_path)


def validate_image_extension(file: UploadFile) -> str:
    assert file.filename
    filename, ext = file.filename.rsplit(".", 1) if "." in file.filename else (file.filename, "")
    if ext not in IMAGE_EXTENSIONS:
        raise FileExtensionError(IMAGE_EXTENSIONS)
    return ext
