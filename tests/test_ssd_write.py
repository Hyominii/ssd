import pytest
from ssd import SSD, OUTPUT_FILE, TARGET_FILE, ERROR_STRING


def read_output() -> str:
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        return f.readline().strip()


def read_target() -> list[str]:
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f]


@pytest.fixture
def ssd():
    return SSD()


def test_write_invalid_address_non_integer(ssd):
    # arrange and act
    addr, value = 'A', '0x00000001'
    ssd.write(addr, value)

    # assert
    assert read_output() == ERROR_STRING


def test_write_valid_address_zero(ssd):
    # arrange and act
    addr, value = 0, '0x00000001'
    ssd.write(addr, value)

    # assert
    assert read_target()[addr] == value


@pytest.mark.parametrize("addr", [0, 10, 19, 50, 99])
def test_write_valid_address(ssd, addr):
    # arrange and act
    value = '0x00000001'
    ssd.write(addr, value)

    # assert
    assert read_target()[addr] == value


@pytest.mark.parametrize("value", [
    '0x00000001',
    '0x12345678',
    '0x7FFFFFFF',
    '0xFFFFFFFF',
])
def test_write_valid_values(ssd, value):
    # arrange and act
    addr = 19
    ssd.write(addr, value)

    # assert
    assert read_target()[addr] == value
