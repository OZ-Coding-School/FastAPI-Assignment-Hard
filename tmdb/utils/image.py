import os

import httpx

from tmdb.configs import config


async def get_poster_image_by_path(path: str) -> str:
    """TMDB에서 포스터 이미지를 다운로드하고 저장하는 함수"""
    # TMDB 이미지 URL
    image_url = config.BASE_IMAGE_URL + path
    upload_dir = "movies/poster_images"
    # 저장할 디렉터리를 설정
    save_dir = os.path.join(config.MEDIA_DIR, upload_dir)
    # 디렉터리 경로에 폴더가 존재하지 않으면 생성하기
    os.makedirs(save_dir, exist_ok=True)

    # 저장할 파일 경로 설정
    filename = os.path.basename(path)  # URL에서 파일명 추출
    save_path = os.path.join(save_dir, filename)

    # 이미지 다운로드
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(image_url)
            response.raise_for_status()
            # 파일 저장
            with open(save_path, "wb") as file:
                file.write(response.content)

            print(f"이미지 다운로드 및 업로드 완료: {save_path}")
            return upload_dir + path

        except httpx.HTTPStatusError as e:
            print(f"이미지 다운로드 중 HTTP 오류 발생: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"이미지 다운로드 요청 오류 발생: {str(e)}")

    return ""
