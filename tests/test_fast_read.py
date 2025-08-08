import os
import shutil
import pytest

from ssd import SSD, CommandInvoker, WriteCommand, EraseCommand, BLANK_STRING

dir_buffer = "C:/tmp_yp/ssd/buffer"
file_nand = "C:/tmp_y/ssd/ssd_nand.txt"
file_output = "C:/tmp_yp/ssd/ssd_output.txt"


@pytest.fixture(scope="session")
def ctx():
    """
    기존 buffer/, nand.txt, output.txt 삭제
    SSD Invoker 생성 후 곧바로 flush() -> buffer 슬롯을 1_empty~5_empty 로 맞춤
    세션 동안 같은 객체·상태를 공유
    """
    # if os.path.isdir(SSD.BUFFER_DIR):
    #     shutil.rmtree(SSD.BUFFER_DIR)
    # for f in (SSD.TARGET_FILE, SSD.OUTPUT_FILE):
    #     if os.path.exists(f):
    #         os.remove(f)

    if os.path.isdir(dir_buffer):
        shutil.rmtree(dir_buffer)
    for f in (file_nand, file_output):
        if os.path.exists(f):
            os.remove(f)

    SSD._instance = None  # 싱글턴
    ssd_inst = SSD()
    invoker = CommandInvoker(ssd_inst)
    invoker.flush()  # empty 상태

    return ssd_inst, invoker


# 1. Buffer가 비어 있을 때 NAND에서 읽음 (초기 BLANK_STRING)
def test_fast_read_empty_buffer(ctx):
    _, invoker = ctx
    invoker.flush()

    value = invoker.fast_read(0)
    assert value == BLANK_STRING


# 2. Buffer에 Write 후 fast_read: Buffer 값 반환, NAND는 아직 변하지 않음
def test_fast_read_after_write(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    actual = "0xABCDEF01"
    invoker.add_command(WriteCommand(ssd_inst, 5, actual, invoker.num_commands() + 1))

    value = invoker.fast_read(5)
    assert value == actual

    # NAND 확인: Flush 전이므로 BLANK_STRING
    nand_value = ssd_inst._read_from_nand(5)
    assert nand_value == BLANK_STRING


# 3. Buffer에 Erase 후 fast_read: 범위 내 BLANK_STRING 반환
def test_fast_read_after_erase(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    # 먼저 Write (Buffer에)
    invoker.add_command(WriteCommand(ssd_inst, 10, "0x12345678", invoker.num_commands() + 1))
    # Erase (같은 Buffer)
    invoker.add_command(EraseCommand(ssd_inst, 10, 1, invoker.num_commands() + 1))

    value = invoker.fast_read(10)
    assert value == BLANK_STRING


# 4. PDF 예시: W 10 → E 10 2 → W 11 → R 10=BLANK, R 11=Write 값
def test_fast_read_mixed_commands(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    invoker.add_command(WriteCommand(ssd_inst, 10, "0xABCDABCD", invoker.num_commands() + 1))
    invoker.add_command(EraseCommand(ssd_inst, 10, 2, invoker.num_commands() + 1))
    invoker.add_command(WriteCommand(ssd_inst, 11, "0xABCDABCD", invoker.num_commands() + 1))

    assert invoker.fast_read(10) == BLANK_STRING
    assert invoker.fast_read(11) == "0xABCDABCD"


# 5. Ignore Command 적용: Overwrite Write → 최신 값만 반환
def test_fast_read_with_ignore_write(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    invoker.add_command(WriteCommand(ssd_inst, 20, "0xAAAAAAAA", invoker.num_commands() + 1))
    invoker.add_command(WriteCommand(ssd_inst, 20, "0xBBBBBBBB", invoker.num_commands() + 1))

    assert invoker.fast_read(20) == "0xBBBBBBBB"


# 6. Ignore Command 적용: Erase가 이전 Write/Erase 무시 → BLANK 반환
def test_fast_read_with_ignore_erase(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    invoker.add_command(EraseCommand(ssd_inst, 18, 3, invoker.num_commands() + 1))
    invoker.add_command(WriteCommand(ssd_inst, 21, "0x12341234", invoker.num_commands() + 1))
    invoker.add_command(EraseCommand(ssd_inst, 18, 5, invoker.num_commands() + 1))  # 18~22 Erase

    for lba in range(18, 23):
        assert invoker.fast_read(lba) == BLANK_STRING


# 7. Merge Erase 적용: 연속 Erase 병합 후 범위 내 BLANK 반환
def test_fast_read_with_merge_erase(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    invoker.add_command(EraseCommand(ssd_inst, 10, 4, invoker.num_commands() + 1))  # 10~13
    invoker.add_command(EraseCommand(ssd_inst, 12, 3, invoker.num_commands() + 1))  # 12~14 → merge to 10~14

    for lba in range(10, 15):
        assert invoker.fast_read(lba) == BLANK_STRING

    # 범위 밖
    assert invoker.fast_read(15) == BLANK_STRING  # NAND 초기값


# 8. Buffer Full 직전 추가: Flush 없이 fast_read 정상
def test_fast_read_near_full_buffer(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    for i in range(1, 5):  # 4개 Write
        invoker.add_command(WriteCommand(ssd_inst, i, f"0x0000000{i}", invoker.num_commands() + 1))

    for i in range(1, 5):
        assert invoker.fast_read(i) == f"0x0000000{i}"




# import os
# import pytest
#
# from ssd import SSD, CommandInvoker, WriteCommand, EraseCommand, BLANK_STRING
#
#
# @pytest.fixture
# def setup_ssd():
#     nand_file = "../ssd_nand.txt"
#     buffer_dir = "../buffer"
#     os.environ['TARGET_FILE'] = str(nand_file)
#     ssd = SSD()
#     invoker = CommandInvoker(ssd)
#     yield ssd, invoker
#
#
# def test_fast_read_from_buffer_with_write_and_erase(setup_ssd):
#     ssd, invoker = setup_ssd
#     actual = "0xABCDEF01"
#
#     invoker.add_command(WriteCommand(ssd, 5, actual, invoker.num_commands() + 1))
#
#     # Buffer에 Erase 명령어 추가 (해당 LBA 지움)
#     # invoker.add_command(EraseCommand(ssd, 5, 1, invoker.num_commands() + 1))
#
#     # Fast read: Buffer에서 Erase 적용되어 BLANK_STRING 반환해야 함
#     value = invoker.fast_read(5)
#     assert value == actual # , f"Expected {BLANK_STRING}, but got {value}"
#
#     # # NAND 확인: Flush 안 했으므로 NAND는 여전히 초기값 (BLANK_STRING)
#     # nand_value = ssd._read_from_nand(5)
#     # assert nand_value == BLANK_STRING, f"NAND should still be {BLANK_STRING}, but got {nand_value}"