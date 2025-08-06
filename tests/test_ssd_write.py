import pytest
import pytest_mock

from ssd import SSD
from ssd import OUTPUT_FILE, TARGET_FILE, ERROR_STRING


def read_ssd_output_txt() -> str:
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        return f.readline().strip()


def read_ssd_target_txt() -> list[str]:
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f]
    return lines


def test_write_invalid_address_A():
    # arrange
    ssd = SSD()
    addr, value = 'A', '0x00000001'

    # act
    ssd.write(addr, value)
    result = read_ssd_output_txt()

    # assert
    assert result == 'ERROR'


def test_write_valid_address_valid_value():
    # arrange
    ssd = SSD()
    addr, value = 0, '0x00000001'

    # act
    ssd.write(addr, value)
    result = read_ssd_output_txt()

    # assert
    assert result == value


def test_write_another_valid_address_valid_value():
    # arrange
    ssd = SSD()
    addr, value = 19, '0x00000001'

    # act
    ssd.write(addr, value)
    result = read_ssd_target_txt()[addr]

    # assert
    assert result == value






