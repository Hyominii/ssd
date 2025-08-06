import pytest
from pytest_mock import MockerFixture

from ssd import SSD, BLANK_STRING, ERROR_STRING, TARGET_FILE, OUTPUT_FILE
import os

TEST_VALUE = "0x01234567"


def get_output_file() -> str:
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        content_string = f.read()
    return content_string.rstrip("\n")


def write_file(address: int, value: str):
    ssd = SSD()
    if address < 0 or address > 100:
        with open(OUTPUT_FILE, "w") as f:
            f.write(ERROR_STRING + "\n")
    with open(TARGET_FILE, "r") as f:
        lines = f.readlines()
    # 줄이 address 줄보다 적으면 빈 줄로 채움
    while len(lines) < address:
        lines.append("\n")
    lines[address] = value + "\n"
    with open(TARGET_FILE, "w") as f:
        f.writelines(lines)
    return 0


def test_read_file_exist():
    if os.path.exists(TARGET_FILE):
        os.remove(TARGET_FILE)
    assert not os.path.exists(TARGET_FILE)
    ssd = SSD()
    ssd.read(0)
    #print(TARGET_FILE)
    assert os.path.exists(TARGET_FILE)
    os.remove(TARGET_FILE)


def test_write_file_exist(tmp_path):
    if os.path.exists(TARGET_FILE):
        os.remove(TARGET_FILE)
    assert not os.path.exists(TARGET_FILE)
    ssd = SSD()
    write_file(0, TEST_VALUE)
    assert os.path.exists(TARGET_FILE)
    os.remove(TARGET_FILE)


def test_read_success_lba0():
    ssd = SSD()
    write_file(0, TEST_VALUE)
    ssd.read(0)
    assert get_output_file() == TEST_VALUE


def test_read_success_lba99():
    ssd = SSD()
    write_file(99, TEST_VALUE)
    ssd.read(99)
    assert get_output_file() == TEST_VALUE


def test_read_blank_success():
    if os.path.exists(TARGET_FILE):
        os.remove(TARGET_FILE)
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    ssd = SSD()
    ssd.read(50)
    assert get_output_file() == BLANK_STRING


def test_read_lba_error():
    ssd = SSD()
    ssd.read(-1)
    assert get_output_file() == ERROR_STRING
    ssd.read(-15)
    assert get_output_file() == ERROR_STRING
    ssd.read(100)
    assert get_output_file() == ERROR_STRING
    ssd.read(150)
    assert get_output_file() == ERROR_STRING


def test_read_invalid_lba_error():
    ssd = SSD()
    ssd.read('A')
    assert get_output_file() == ERROR_STRING
