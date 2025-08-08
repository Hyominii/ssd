import os
import shutil
import pytest
import ssd                                       # ssd.py 모듈

# ───────────────────────── 세션 단위 초기화 ──────────────────────────
@pytest.fixture(scope="session")
def ctx():
    """
    • 기존 buffer/, nand.txt, output.txt 삭제
    • SSD·Invoker 생성 후 곧바로 flush() ⇒ buffer 슬롯을 1_empty~5_empty 로 맞춤
    • 세션 동안 같은 객체·상태를 공유
    """
    if os.path.isdir(ssd.BUFFER_DIR):
        shutil.rmtree(ssd.BUFFER_DIR)
    for f in (ssd.TARGET_FILE, ssd.OUTPUT_FILE):
        if os.path.exists(f):
            os.remove(f)

    ssd.SSD._instance = None           # 싱글턴 리셋
    ssd_inst = ssd.SSD()
    invoker  = ssd.CommandInvoker(ssd_inst)
    invoker.flush()                    # ⭐️ 항상 깨끗한 상태에서 시작

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
    invoker.flush()                    # 버퍼 비우기 + 슬롯 초기화

    expected = {f"{i}_empty" for i in range(1, 6)}
    assert set(os.listdir(ssd.BUFFER_DIR)) == expected