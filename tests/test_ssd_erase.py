import pytest
import random
from ssd import SSD, OUTPUT_FILE, TARGET_FILE, ERROR_STRING, BLANK_STRING, MIN_VALUE, MAX_VALUE


def read_output() -> str:
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        return f.readline().strip()


def read_target() -> list[str]:
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f]  # 변경: strip() → rstrip('\n') for consistency with file_handler


def generate_random_hex():
    rand_int = random.randint(MIN_VALUE, MAX_VALUE)
    return f"0x{rand_int:08X}"


@pytest.fixture
def ssd():
    ssd_instance = SSD()  # 싱글톤 인스턴스 사용 (최신 SSD 클래스 반영)
    # 각 테스트 전에 target 파일 초기화 (싱글톤 상태 공유 방지)
    ssd_instance._target_file_handler.write_lines([generate_random_hex() for _ in range(100)])
    ssd_instance._output_file_handler.write("")  # output 파일 초기화
    return ssd_instance


def test_erase_valid_range(ssd):
    addr, size = 10, 3
    ssd.erase(addr, size)
    lines = read_target()
    for i in range(addr, addr + size):
        assert lines[i] == BLANK_STRING


def test_erase_zero_size(ssd):
    addr = 20
    value = '0x12345678'
    ssd.write(addr, value)

    output_before = read_output()
    ssd.erase(addr, 0)
    output_after = read_output()

    # check no changes
    lines = read_target()
    assert lines[addr] == value
    assert output_after == output_before


def test_erase_at_upper_boundary(ssd):
    addr, size = 90, 10     # uppper boundary
    ssd.erase(addr, size)
    lines = read_target()
    for i in range(addr, addr + size):
        assert lines[i] == BLANK_STRING


def test_erase_exact_size_limit(ssd):
    addr, size = 0, 10      # lower boundary
    ssd.erase(addr, size)
    lines = read_target()
    for i in range(addr, addr + size):
        assert lines[i] == BLANK_STRING


@pytest.mark.parametrize("addr,size", [
    (95, 10),   # 범위 초과 (95~104)
    (100, 1),   # 존재하지 않는 인덱스
    (0, 11),    # size 10 초과
    (-1, 5),    # 음수 주소
    (10, -1),   # 음수 size
])
def test_erase_invalid_range(ssd, addr, size):
    ssd.erase(addr, size)
    assert read_output() == ERROR_STRING


@pytest.mark.parametrize("addr,size", [
    ("A", 5),
    (10, "B"),
    ("0", "3"),
    (None, 3),
    (5, None),
])
def test_erase_invalid_type(ssd, addr, size):
    ssd.erase(addr, size)
    assert read_output() == ERROR_STRING
