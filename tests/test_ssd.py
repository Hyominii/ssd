import subprocess
import sys

import pytest
from pathlib import Path
from tests.test_read import get_output_file, TEST_VALUE
from tests.test_ssd_write import read_target

def test_main_write_called():
    addr, value = '0', TEST_VALUE

    ssd_path = str(Path(__file__).parent.parent / "ssd.py")

    result = subprocess.run(
        [sys.executable, ssd_path, 'W', addr, value],
        capture_output=False,
        text=True
    )

    print(result.stdout)

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
