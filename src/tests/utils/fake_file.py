import io

from PIL import Image


def fake_image() -> io.BytesIO:
    """가짜 이미지 파일을 생성"""
    image_bytes = io.BytesIO()
    image = Image.new("RGB", (100, 100), color=(255, 0, 0))  # 빨간색 이미지 생성
    image.save(image_bytes, format="PNG")  # PNG 형식으로 저장
    image_bytes.seek(0)  # 파일 포인터를 처음으로 이동
    return image_bytes


def fake_txt_file() -> io.BytesIO:
    """가짜 텍스트 파일을 생성"""
    file = io.BytesIO()
    file.write(b"fake txt file!")
    file.seek(0)
    return file
