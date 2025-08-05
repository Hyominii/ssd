import pytest
from pytest_mock import MockerFixture

from ssd import SSD
import os

BLANK_VALUE = "0x00000000"
TEST_VALUE = "0x01234567"
ERROR_VALUE = "ERROR"
TARGET_FILE = 'ssd_output.txt'
WRITE_FILE = 'ssd_nand.txt'

def get_output_file():
    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        content_string = f.read()
    return content_string

def write_output_file(content: str):
    with open(TARGET_FILE, "w") as f:
        f.write(content + "\n")

def test_read_file_exist():
    ssd = SSD()
    if os.path.exists(TARGET_FILE):
        os.remove(TARGET_FILE)
    assert not os.path.exists(TARGET_FILE)
    ssd.read(0)
    assert os.path.exists(TARGET_FILE)
    os.remove(TARGET_FILE)

def test_write_file_exist():
    ssd = SSD()
    if os.path.exists(WRITE_FILE):
        os.remove(WRITE_FILE)
    assert not os.path.exists(WRITE_FILE)
    ssd.write(0,"00")
    assert os.path.exists(WRITE_FILE)
    os.remove(WRITE_FILE)


def test_read_success():
    ssd = SSD()
    write_output_file(TEST_VALUE)
    ssd.read(0)
    assert get_output_file() == TEST_VALUE

def test_read_blank_success():
    ssd = SSD()
    if os.path.exists(TARGET_FILE):
        os.remove(TARGET_FILE)
    ssd.read(0)
    assert get_output_file() == BLANK_VALUE

def test_read_lba_error():
    ssd = SSD()
    ssd.read(-1)
    assert get_output_file() == ERROR_VALUE

def test_read_invalid_lba_error():
    ssd = SSD()
    ssd.read('A')
    assert get_output_file() == ERROR_VALUE