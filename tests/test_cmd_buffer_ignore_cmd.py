import os
import shutil
import pytest
import ssd


# ───────────────────────── 세션 단위 초기화 ──────────────────────────
@pytest.fixture(scope="session")
def ctx():
    """
    기존 buffer/, nand.txt, output.txt 삭제
    SSD Invoker 생성 후 곧바로 flush() -> buffer 슬롯을 1_empty~5_empty 로 맞춤
    세션 동안 같은 객체·상태를 공유
    """
    if os.path.isdir(ssd.BUFFER_DIR):
        shutil.rmtree(ssd.BUFFER_DIR)
    for f in (ssd.TARGET_FILE, ssd.OUTPUT_FILE):
        if os.path.exists(f):
            os.remove(f)

    ssd.SSD._instance = None  # 싱글턴
    ssd_inst = ssd.SSD()
    invoker = ssd.CommandInvoker(ssd_inst)
    invoker.flush()  # empty 상태

    return ssd_inst, invoker


# ──────────────────────────────────────────────────────────────────


# 1) 버퍼가 제대로 초기화됐는지
def test_01_buffer_initialized(ctx):
    expected = {f"{i}_empty" for i in range(1, 6)}
    assert set(os.listdir(ssd.BUFFER_DIR)) == expected


# 2) 명령 추가 시 파일명이 변경되는지
def test_02_buffer_renamed(ctx):
    ssd_inst, invoker = ctx

    invoker.add_command(
        ssd.WriteCommand(ssd_inst, 10, "0xAAAABBBB", invoker.num_commands() + 1)
    )
    invoker.add_command(
        ssd.EraseCommand(ssd_inst, 20, 5, invoker.num_commands() + 1)
    )

    files = set(os.listdir(ssd.BUFFER_DIR))
    assert "1_W_10_0xAAAABBBB" in files
    assert "2_E_20_5" in files


# 3) flush() 후 다시 *_empty 로 복원되는지
def test_03_flush_resets_buffer(ctx):
    _, invoker = ctx
    invoker.flush()

    expected = {f"{i}_empty" for i in range(1, 6)}
    assert set(os.listdir(ssd.BUFFER_DIR)) == expected


def test_04_ignore_write_overwrite(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    # W 20 → W 21 → W 20(덮어쓰기)
    invoker.add_command(
        ssd.WriteCommand(ssd_inst, 20, "0xABCDABCD", invoker.num_commands() + 1)
    )
    invoker.add_command(
        ssd.WriteCommand(ssd_inst, 21, "0x12341234", invoker.num_commands() + 1)
    )
    invoker.add_command(
        ssd.WriteCommand(ssd_inst, 20, "0xEEEEFFFF", invoker.num_commands() + 1)
    )

    # 버퍼에는 두 개만 남아야 함 (W 21 / W 20-최근)
    assert invoker.num_commands() == 2
    buf = invoker.get_buffer()
    assert buf[0]._address == 21 and buf[1]._address == 20

    # 실제 파일 이름도 1_W_21_… , 2_W_20_… 이어야 함
    files = set(os.listdir(ssd.BUFFER_DIR))
    assert "1_W_21_0x12341234" in files
    assert "2_W_20_0xEEEEFFFF" in files
    # 불필요 파일이 더 있으면 실패
    assert len(files) == 5  # 3_empty~5_empty 포함 총 5개


# 5) 상위 Erase 범위가 이전 Write·Erase 를 모두 무효화 하는지 확인
def test_05_ignore_erase_supersedes(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    # E 18 3  →  W 21 …  →  E 18 5 (상위범위)
    invoker.add_command(
        ssd.EraseCommand(ssd_inst, 18, 3, invoker.num_commands() + 1)
    )
    invoker.add_command(
        ssd.WriteCommand(ssd_inst, 21, "0x12341234", invoker.num_commands() + 1)
    )
    invoker.add_command(
        ssd.EraseCommand(ssd_inst, 18, 5, invoker.num_commands() + 1)
    )

    # 버퍼에는 최종 Erase 하나만 남아야 함
    assert invoker.num_commands() == 1
    cmd = invoker.get_buffer()[0]
    assert isinstance(cmd, ssd.EraseCommand)
    assert cmd._address == 18 and cmd._size == 5

    # 파일도 1_E_18_5 하나 + 2~5_empty 네 개
    files = set(os.listdir(ssd.BUFFER_DIR))
    assert files == {
        "1_E_18_5",
        "2_empty",
        "3_empty",
        "4_empty",
        "5_empty",
    }


def test_06_merge_erase(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    # E 1 4  →  W 0 …  →  E 0 5 (상위범위)
    invoker.add_command(
        ssd.EraseCommand(ssd_inst, 1, 4, invoker.num_commands() + 1)
    )
    invoker.add_command(
        ssd.WriteCommand(ssd_inst, 0, "0x12341234", invoker.num_commands() + 1)
    )
    invoker.add_command(
        ssd.EraseCommand(ssd_inst, 0, 5, invoker.num_commands() + 1)
    )

    # 버퍼에는 최종 Erase 하나만 남아야 함
    assert invoker.num_commands() == 1
    cmd = invoker.get_buffer()[0]
    assert isinstance(cmd, ssd.EraseCommand)
    assert cmd._address == 0 and cmd._size == 5

    # 파일도 1_E_0_5 하나 + 2~5_empty 네 개
    files = set(os.listdir(ssd.BUFFER_DIR))
    assert files == {
        "1_E_0_5",
        "2_empty",
        "3_empty",
        "4_empty",
        "5_empty",
    }