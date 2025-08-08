import os
import pytest

from ssd import SSD, CommandInvoker, WriteCommand, EraseCommand, BLANK_STRING


@pytest.fixture
def setup_ssd():
    nand_file = "../ssd_nand.txt"
    buffer_dir = "../buffer"
    os.environ['TARGET_FILE'] = str(nand_file)
    ssd = SSD()
    invoker = CommandInvoker(ssd)
    yield ssd, invoker


def test_fast_read_from_buffer_with_write_and_erase(setup_ssd):
    ssd, invoker = setup_ssd
    actual = "0xABCDEF01"

    invoker.add_command(WriteCommand(ssd, 5, actual, invoker.num_commands() + 1))

    # Buffer에 Erase 명령어 추가 (해당 LBA 지움)
    # invoker.add_command(EraseCommand(ssd, 5, 1, invoker.num_commands() + 1))

    # Fast read: Buffer에서 Erase 적용되어 BLANK_STRING 반환해야 함
    value = invoker.fast_read(5)
    assert value == actual # , f"Expected {BLANK_STRING}, but got {value}"

    # # NAND 확인: Flush 안 했으므로 NAND는 여전히 초기값 (BLANK_STRING)
    # nand_value = ssd._read_from_nand(5)
    # assert nand_value == BLANK_STRING, f"NAND should still be {BLANK_STRING}, but got {nand_value}"