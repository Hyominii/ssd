import pytest
from pytest_mock import MockerFixture

from ssd import SSD, BLANK_STRING, ERROR_STRING, TARGET_FILE, OUTPUT_FILE
import os

TEST_VALUE = "0x01234567"

def get_output_file() -> str:
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        content_string = f.read()
    return content_string.rstrip("\n")

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


def test_read_success_lba0():
    ssd = SSD()
    ssd.write(0, TEST_VALUE)
    ssd.read(0)
    assert get_output_file() == TEST_VALUE

def test_read_success_lba99():
    ssd = SSD()
    ssd.write(99, TEST_VALUE)
    ssd.read(99)
    assert get_output_file() == TEST_VALUE

def test_read_blank_success():
    if os.path.exists(TARGET_FILE):
        os.remove(TARGET_FILE)
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    ssd = SSD()
    ssd.read(0)
    assert get_output_file() == BLANK_STRING

def test_read_lba_error():
    ssd = SSD()
    ssd.read(-1)
    assert get_output_file() == ERROR_VALUE

def test_read_invalid_lba_error():
    ssd = SSD()
    ssd.read('A')
    assert get_output_file() == ERROR_VALUE