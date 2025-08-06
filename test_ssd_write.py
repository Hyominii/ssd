import pytest
import pytest_mock

from ssd import SSD
from ssd import OUTPUT_FILE, TARGET_FILE, ERROR_STRING


def read_ssd_output_txt() -> str:
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        return f.readline().strip()


def test_write_invalid_address_A():
    # arrange
    ssd = SSD()
    addr, value = 'A', '0x00000001'

    # act
    ssd.write(addr, value)
    result = read_ssd_output_txt()

    # assert
    assert result == 'ERROR'







