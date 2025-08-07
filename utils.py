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
