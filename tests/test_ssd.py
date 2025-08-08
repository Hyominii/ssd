import os.path
import subprocess
import sys

import pytest
from pathlib import Path
from tests.test_read import get_output_file, TEST_VALUE
from tests.test_ssd_write_ import read_target

def buffer_flush():
    ssd_path = str(Path(__file__).parent.parent / "ssd.py")
    result = subprocess.run(
        [sys.executable, ssd_path, 'F'],
        capture_output=False,
        text=True
    )

def test_main_write_called():

    #arrange
    addr, value = '0', TEST_VALUE
    ssd_path = str(Path(__file__).parent.parent / "ssd.py")
    target_file_name = f'1_W_{addr}_{value}'
    file_path = os.path.join('buffer', target_file_name)
    buffer_flush()

    #action
    result = subprocess.run(
        [sys.executable, ssd_path, 'W', addr, value],
        capture_output=False,
        text=True
    )
    #assert
    assert os.path.isfile(file_path)

def test_main_write_and_flush_called():

    #arrange
    addr, value = '0', TEST_VALUE
    ssd_path = str(Path(__file__).parent.parent / "ssd.py")

    #action
    result = subprocess.run(
        [sys.executable, ssd_path, 'W', addr, value],
        capture_output=False,
        text=True
    )
    print(result.stdout)
    buffer_flush()

    #assert
    assert read_target()[int(addr)] == value



def test_main_read_called():
    addr, value = '0', TEST_VALUE

    ssd_path = str(Path(__file__).parent.parent / "ssd.py")
    result = subprocess.run(
        [sys.executable, ssd_path, "R", addr],
        capture_output=True,
        text=True
    )

    assert get_output_file() == TEST_VALUE

"""
def test_main_command_buffer_multiple_call():
    addr, value = '0', TEST_VALUE
    addrs = ["0", "1", "2"]
    commands = ["W", "E", "F", "R"]
    ssd_path = str(Path(__file__).parent.parent / "ssd.py")

    for cmd in commands:
        for addr in addrs:
            result = subprocess.run(
                [sys.executable, ssd_path, cmd, addr],
                capture_output=True,
                text=True
            )

    assert get_output_file() == TEST_VALUE
"""