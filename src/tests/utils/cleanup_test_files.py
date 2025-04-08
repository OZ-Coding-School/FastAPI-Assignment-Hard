import glob
import os

from src.configs import config


def remove_test_files() -> None:
    pattern = os.path.join(config.MEDIA_DIR, "**", "*test*")  # MEDIA_DIR의 모든 하위 폴더의 test* 파일 검색
    files_to_delete = glob.glob(pattern, recursive=True)  # 해당 패턴과 매칭되는 파일 리스트 찾기

    # 순회하면서 삭제
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            print(f"삭제됨: {file_path}")
        except Exception as e:
            print(f"삭제 실패: {file_path}, 오류: {e}")
