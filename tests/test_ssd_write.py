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
    # Arrange
    addr, value = 'A', '0x00000001'

    # Act
    ssd.write(addr, value)

    # Assert
    assert read_output() == ERROR_STRING


def test_write_valid_address_zero(ssd):
    # Arrange
    addr, value = 0, '0x00000001'

    # Act
    ssd.write(addr, value)

    # Assert
    assert read_target()[addr] == value


def test_write_valid_address_nineteen(ssd):
    # Arrange
    addr, value = 19, '0x00000001'

    # Act
    ssd.write(addr, value)

    # Assert
    assert read_target()[addr] == value
