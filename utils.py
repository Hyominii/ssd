import inspect
from pathlib import Path
from typing import List, Union


def find_files_by_pattern(
        directory: Union[str, Path],
        pattern: str = "*"
) -> List[Path]:
    """
    주어진 디렉토리에서 특정 패턴에 해당하는 파일들을 반환합니다.

    Args:
        directory (str or Path): 검색할 디렉토리 경로
        pattern (str): glob 패턴 (예: "rotate_*.log", "*.zip")

    Returns:
        List[Path]: 일치하는 파일들의 경로 리스트
    """
    dir_path = Path(directory)
    return sorted(dir_path.glob(pattern))


def get_class_and_method_name():
    frame = inspect.currentframe()
    outer_frame = frame.f_back  # 현재 함수(get_class_and_method_name)를 호출한 프레임
    code = outer_frame.f_code
    func_name = code.co_name

    # 인스턴스 메서드인지 확인 (locals에 'self'가 있으면 클래스 메서드)
    instance = outer_frame.f_locals.get('self', None)
    if instance:
        class_name = instance.__class__.__name__
        return f"{class_name}.{func_name}()"

    # 클래스 메서드 (classmethod)인 경우
    cls = outer_frame.f_locals.get('cls', None)
    if cls:
        return f"{cls.__name__}.{func_name}()"

    # 일반 함수인 경우
    return f"{func_name}()"
