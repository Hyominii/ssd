import re
from typing import Optional, Union

# 0x######## (대/소문자 모두 허용)
HEX_RE = re.compile(r'^(0x|0X)[0-9A-Fa-f]{8}$')
_INT_RE = re.compile(r'^[+-]?\d+$')

MIN_VALUE = 0x00000000
MAX_VALUE = 0xFFFFFFFF

def _as_int(x: Union[int, str]) -> Optional[int]:
    """str/int 모두 받아 정수로 변환. 실패 시 None."""
    if isinstance(x, int):
        return x
    if isinstance(x, str):
        s = x.strip()
        if _INT_RE.match(s):
            try:
                return int(s, 10)
            except ValueError:
                return None
    return None

def is_valid_address(address: Union[int, str], ssd_size: int = 100) -> bool:
    """0 <= address < ssd_size"""
    a = _as_int(address)
    return a is not None and 0 <= a < ssd_size

def is_valid_size(address: Union[int, str],
                  lba_size: Union[int, str],
                  ssd_size: int = 100,
                  max_chunk: int = 10) -> bool:
    """
    Erase 인자 검증:
    - address, size 모두 정수여야 함
    - 0 <= size <= max_chunk
    - 0 <= address < ssd_size
    - address + size <= ssd_size
    """
    a = _as_int(address)
    s = _as_int(lba_size)
    if a is None or s is None:
        return False
    if s < 0 or s > max_chunk:
        return False
    if a < 0 or a >= ssd_size:
        return False
    if a + s > ssd_size:
        return False
    return True

def is_valid_value(value: str) -> bool:
    """
    값은 '0x########' 정확히 10글자의 16진 문자열이어야 함.
    (파일 포맷 일관성을 위해 int는 허용하지 않음)
    """
    if not isinstance(value, str) or len(value) != 10 or not HEX_RE.match(value):
        return False
    try:
        v = int(value, 16)
    except ValueError:
        return False
    return MIN_VALUE <= v <= MAX_VALUE