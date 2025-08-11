import os
import shutil
import pytest
from ssd import *


# ───────────────────────── 세션 단위 초기화 ──────────────────────────
@pytest.fixture(scope="session")
def ctx():
    """
    기존 buffer/, nand.txt, output.txt 삭제
    SSD Invoker 생성 후 곧바로 flush() -> buffer 슬롯을 1_empty~5_empty 로 맞춤
    세션 동안 같은 객체·상태를 공유
    """
    if os.path.isdir(BUFFER_DIR):
        shutil.rmtree(BUFFER_DIR)
    for f in (TARGET_FILE, OUTPUT_FILE):
        if os.path.exists(f):
            os.remove(f)

    SSD._instance = None  # 싱글턴
    ssd_inst = SSD()
    invoker = CommandInvoker(ssd_inst)
    invoker.flush()  # empty 상태

    return ssd_inst, invoker


# ──────────────────────────────────────────────────────────────────


# 1) 버퍼가 제대로 초기화됐는지
def test_01_buffer_initialized(ctx):
    expected = {f"{i}_empty" for i in range(1, 6)}
    assert set(os.listdir(BUFFER_DIR)) == expected


# 2) 명령 추가 시 파일명이 변경되는지
def test_02_buffer_renamed(ctx):
    ssd_inst, invoker = ctx

    invoker.add_command(
        WriteCommand(ssd_inst, 10, "0xAAAABBBB")
    )
    invoker.add_command(
        EraseCommand(ssd_inst, 20, 5)
    )

    files = set(os.listdir(BUFFER_DIR))
    assert "1_W_10_0xAAAABBBB" in files
    assert "2_E_20_5" in files


# 3) flush() 후 다시 *_empty 로 복원되는지
def test_03_flush_resets_buffer(ctx):
    _, invoker = ctx
    invoker.flush()

    expected = {f"{i}_empty" for i in range(1, 6)}
    assert set(os.listdir(BUFFER_DIR)) == expected


def test_04_ignore_write_overwrite(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    # W 20 → W 21 → W 20(덮어쓰기)
    invoker.add_command(
        WriteCommand(ssd_inst, 20, "0xABCDABCD")
    )
    invoker.add_command(
        WriteCommand(ssd_inst, 21, "0x12341234")
    )
    invoker.add_command(
        WriteCommand(ssd_inst, 20, "0xEEEEFFFF")
    )

    # 버퍼에는 두 개만 남아야 함 (W 21 / W 20-최근)
    assert invoker.num_commands() == 2
    buf = invoker.get_buffer()
    assert buf[0].address == 21 and buf[1].address == 20

    # 실제 파일 이름도 1_W_21_… , 2_W_20_… 이어야 함
    files = set(os.listdir(BUFFER_DIR))
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
        EraseCommand(ssd_inst, 18, 3)
    )
    invoker.add_command(
        WriteCommand(ssd_inst, 21, "0x12341234")
    )
    invoker.add_command(
        EraseCommand(ssd_inst, 18, 5)
    )

    # 버퍼에는 최종 Erase 하나만 남아야 함
    assert invoker.num_commands() == 1
    cmd = invoker.get_buffer()[0]
    assert isinstance(cmd, EraseCommand)
    assert cmd.address == 18 and cmd.size == 5

    # 파일도 1_E_18_5 하나 + 2~5_empty 네 개
    files = set(os.listdir(BUFFER_DIR))
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
        EraseCommand(ssd_inst, 1, 4)
    )
    invoker.add_command(
        WriteCommand(ssd_inst, 0, "0x12341234")
    )
    invoker.add_command(
        EraseCommand(ssd_inst, 0, 5)
    )

    # 버퍼에는 최종 Erase 하나만 남아야 함
    assert invoker.num_commands() == 1
    cmd = invoker.get_buffer()[0]
    assert isinstance(cmd, EraseCommand)
    assert cmd.address == 0 and cmd.size == 5

    # 파일도 1_E_0_5 하나 + 2~5_empty 네 개
    files = set(os.listdir(BUFFER_DIR))
    assert files == {
        "1_E_0_5",
        "2_empty",
        "3_empty",
        "4_empty",
        "5_empty",
    }


def test_07_ignore_erase(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    # E 1 4  →  W 0 …  →  E 0 5 (상위범위)
    invoker.add_command(
        EraseCommand(ssd_inst, 0, 1)
    )
    invoker.add_command(
        WriteCommand(ssd_inst, 0, "0x12341234")
    )

    # 버퍼에는 최종 Erase 하나만 남아야 함
    assert invoker.num_commands() == 1
    cmd = invoker.get_buffer()[0]
    assert isinstance(cmd, WriteCommand)

    # 파일도 1_E_0_5 하나 + 2~5_empty 네 개
    files = set(os.listdir(BUFFER_DIR))
    assert files == {
        "1_W_0_0x12341234",
        "2_empty",
        "3_empty",
        "4_empty",
        "5_empty",
    }


def test_my1(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    invoker.add_command(
        EraseCommand(ssd_inst, 20, 5)
    )

    invoker.add_command(
        WriteCommand(ssd_inst, 30, "0xAAAABBBB")
    )
    invoker.add_command(
        WriteCommand(ssd_inst, 30, "0x12345678")
    )

    invoker.add_command(
        EraseCommand(ssd_inst, 20, 10)
    )

    invoker.add_command(
        EraseCommand(ssd_inst, 25, 10)
    )

    files = set(os.listdir(BUFFER_DIR))
    assert "1_E_20_10" in files
    assert "2_E_30_5" in files


def test_my2(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    invoker.add_command(
        EraseCommand(ssd_inst, 0, 8)
    )

    invoker.add_command(
        WriteCommand(ssd_inst, 30, "0xAAAABBBB")
    )
    invoker.add_command(
        WriteCommand(ssd_inst, 30, "0x12345678")
    )

    invoker.add_command(
        EraseCommand(ssd_inst, 7, 8)
    )

    invoker.add_command(
        EraseCommand(ssd_inst, 14, 10)
    )

    files = set(os.listdir(BUFFER_DIR))
    assert "1_W_30_0x12345678" in files
    assert "2_E_0_10" in files
    assert "3_E_10_10" in files
    assert "4_E_20_4" in files


def test_my3(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    invoker.add_command(
        ssd.EraseCommand(ssd_inst, 0, 8, invoker.num_commands() + 1)
    )

    invoker.add_command(
        WriteCommand(ssd_inst, 30, "0xAAAABBBB")
    )
    invoker.add_command(
        WriteCommand(ssd_inst, 30, "0x12345678")
    )

    invoker.add_command(
        ssd.EraseCommand(ssd_inst, 7, 8, invoker.num_commands() + 1)
    )

    invoker.add_command(
        EraseCommand(ssd_inst, 14, 10)
    )

    files = set(os.listdir(BUFFER_DIR))
    assert "1_W_30_0x12345678" in files
    assert "2_E_0_10" in files
    assert "3_E_10_10" in files
    assert "4_E_20_4" in files


def test_my4(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    invoker.add_command(
        WriteCommand(ssd_inst, 0, "0x0000000a")
    )
    invoker.add_command(
        WriteCommand(ssd_inst, 1, "0x0000000b")
    )
    invoker.add_command(
        WriteCommand(ssd_inst, 2, "0x0000000c")
    )
    invoker.add_command(
        EraseCommand(ssd_inst, 0, 3)
    )

    files = set(os.listdir(BUFFER_DIR))
    assert "1_E_0_3" in files


def test_my5(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    invoker.add_command(
        ssd.WriteCommand(ssd_inst, 0, "0x0000000a", invoker.num_commands() + 1)
    )
    invoker.add_command(
        ssd.WriteCommand(ssd_inst, 1, "0x0000000b", invoker.num_commands() + 1)
    )
    invoker.add_command(
        ssd.WriteCommand(ssd_inst, 2, "0x0000000c", invoker.num_commands() + 1)
    )
    invoker.add_command(
        EraseCommand(ssd_inst, 0, 3)
    )

    files = set(os.listdir(ssd.BUFFER_DIR))
    assert "1_E_0_3" in files


def test_my6(ctx):
    ssd_inst, invoker = ctx
    invoker.flush()

    invoker.add_command(
        WriteCommand(ssd_inst, 10, "0x0000000a")
    )
    invoker.add_command(
        ssd.EraseCommand(ssd_inst, 11, 2, invoker.num_commands() + 1)
    )
    invoker.add_command(
        ssd.WriteCommand(ssd_inst, 11, "0x0000000b", invoker.num_commands() + 1)
    )
    invoker.add_command(
        ssd.EraseCommand(ssd_inst, 12, 2, invoker.num_commands() + 1)
    )

    files = set(os.listdir(BUFFER_DIR))
    assert "1_W_10_0x0000000a" in files
    assert "2_W_11_0x0000000b" in files
    assert "3_E_12_2" in files


@pytest.mark.parametrize("input", [
    {
        "original": {
            "1": "1_W_0_0x00000000",
            "2": "2_empty",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "W_1_0x00000001",
        "changed": [
            "1_W_0_0x00000000",
            "2_W_1_0x00000001",
            "3_empty",
            "4_empty",
            "5_empty",
        ],
    },
    {
        "original": {
            "1": "1_E_0_1",
            "2": "2_empty",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "W_1_0x00000001",
        "changed": [
            "1_E_0_1",
            "2_W_1_0x00000001",
            "3_empty",
            "4_empty",
            "5_empty",
        ],
    }
])
def test_08_pass_ignore_write(ctx, input):
    ssd_inst, invoker = ctx
    invoker.flush()

    # 기존 입력
    for num in input["original"]:
        if "empty" in input["original"][num]:
            continue
        _, cmd, addr, value = input["original"][num].split("_")
        if cmd == "W":
            invoker.add_command(WriteCommand(ssd_inst, addr, value))
        elif cmd == "E":
            invoker.add_command(EraseCommand(ssd_inst, int(addr), int(value)))

    # 새로운 입력
    cmd, addr, value = input["new_input"].split("_")
    if cmd == "W":
        invoker.add_command(WriteCommand(ssd_inst, int(addr), value))
    elif cmd == "E":
        invoker.add_command(EraseCommand(ssd_inst, int(addr), int(value)))

    expected_num_commands = 0
    for i in input["changed"]:
        if "empty" not in i:
            expected_num_commands += 1

    assert invoker.num_commands() == expected_num_commands
    files = set(os.listdir(BUFFER_DIR))
    assert files == set(input["changed"])


@pytest.mark.parametrize("input", [
    {
        "original": {
            "1": "1_W_0_0x00000000",
            "2": "2_empty",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "W_0_0x00000001",
        "changed": [
            "1_W_0_0x00000001",
            "2_empty",
            "3_empty",
            "4_empty",
            "5_empty",
        ],
    },
    {
        "original": {
            "1": "1_E_0_1",
            "2": "2_empty",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "W_0_0x00000001",
        "changed": [
            "1_W_0_0x00000001",
            "2_empty",
            "3_empty",
            "4_empty",
            "5_empty",
        ],
    }
])
def test_09_ignore_write(ctx, input):
    ssd_inst, invoker = ctx
    invoker.flush()

    # 기존 입력
    for num in input["original"]:
        if "empty" in input["original"][num]:
            continue
        _, cmd, addr, value = input["original"][num].split("_")
        add_command_by_signature(addr, cmd, invoker, ssd_inst, value)

    # 새로운 입력
    cmd, addr, value = input["new_input"].split("_")
    add_command_by_signature(addr, cmd, invoker, ssd_inst, value)

    expected_num_commands = 0
    for i in input["changed"]:
        if "empty" not in i:
            expected_num_commands += 1

    assert invoker.num_commands() == expected_num_commands
    files = set(os.listdir(BUFFER_DIR))
    assert files == set(input["changed"])


def add_command_by_signature(addr, cmd, invoker, ssd_inst, value):
    if cmd == "W":
        invoker.add_command(WriteCommand(ssd_inst, int(addr), value))
    elif cmd == "E":
        invoker.add_command(EraseCommand(ssd_inst, int(addr), int(value)))


@pytest.mark.parametrize("input", [
    {
        "original": {
            "1": "1_W_0_0x00000005",
            "2": "2_empty",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_1_3",
        "changed": [
            "1_W_0_0x00000005",
            "2_E_1_3",
            "3_empty",
            "4_empty",
            "5_empty",
        ],
    },
    {
        "original": {
            "1": "1_E_0_2",
            "2": "2_W_5_0x00001234",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_6_3",
        "changed": [
            "1_E_0_2",
            "2_W_5_0x00001234",
            "3_E_6_3",
            "4_empty",
            "5_empty",
        ],
    },
    {
        "original": {
            "1": "1_E_0_2",
            "2": "2_W_0_0x00001234",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_3_3",
        "changed": [
            "1_E_1_1",
            "2_W_0_0x00001234",
            "3_E_3_3",
            "4_empty",
            "5_empty"
        ],
    },
])
def test_10_pass_ignore_command_erase(ctx, input):
    ssd_inst, invoker = ctx
    invoker.flush()

    # 기존 입력
    for num in input["original"]:
        if "empty" in input["original"][num]:
            continue
        _, cmd, addr, value = input["original"][num].split("_")
        add_command_by_signature(addr, cmd, invoker, ssd_inst, value)

    # 새로운 입력
    cmd, addr, value = input["new_input"].split("_")
    add_command_by_signature(int(addr), cmd, invoker, ssd_inst, int(value))

    expected_num_commands = 0
    for i in input["changed"]:
        if "empty" not in i:
            expected_num_commands += 1

    assert invoker.num_commands() == expected_num_commands
    files = set(os.listdir(BUFFER_DIR))
    assert files == set(input["changed"])


@pytest.mark.parametrize("input", [
    {
        "original": {
            "1": "1_W_0_0x00000005",
            "2": "2_empty",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_0_3",
        "changed": [
            "1_E_0_3", "2_empty", "3_empty", "4_empty", "5_empty"
        ],
    },
    {
        "original": {
            "1": "1_E_0_2",
            "2": "2_W_5_0x00001234",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_0_3",
        "changed": [
            "1_W_5_0x00001234", "2_E_0_3", "3_empty", "4_empty", "5_empty"
        ],
    },
    {
        "original": {
            "1": "1_E_0_2",
            "2": "2_W_0_0x00001234",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_0_3",
        "changed": [
            "1_E_0_3", "2_empty", "3_empty", "4_empty", "5_empty"
        ],
    },
])
def test_11_ignore_command_erase(ctx, input):
    ssd_inst, invoker = ctx
    invoker.flush()

    # 기존 입력
    for num in input["original"]:
        if "empty" in input["original"][num]:
            continue
        _, cmd, addr, value = input["original"][num].split("_")
        add_command_by_signature(addr, cmd, invoker, ssd_inst, value)

    # 새로운 입력
    cmd, addr, value = input["new_input"].split("_")
    add_command_by_signature(int(addr), cmd, invoker, ssd_inst, int(value))

    expected_num_commands = 0
    for i in input["changed"]:
        if "empty" not in i:
            expected_num_commands += 1

    assert invoker.num_commands() == expected_num_commands
    files = set(os.listdir(BUFFER_DIR))
    assert files == set(input["changed"])


@pytest.mark.parametrize("input", [
    {
        "original": {
            "1": "1_E_0_3",
            "2": "2_empty",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_4_3",
        "changed": [
            "1_E_0_3", "2_E_4_3", "3_empty", "4_empty", "5_empty"
        ],
    },
])
def test_12_pass_merge_erase(ctx, input):
    ssd_inst, invoker = ctx
    invoker.flush()

    # 기존 입력
    for num in input["original"]:
        if "empty" in input["original"][num]:
            continue
        _, cmd, addr, value = input["original"][num].split("_")
        add_command_by_signature(addr, cmd, invoker, ssd_inst, value)

    # 새로운 입력
    cmd, addr, value = input["new_input"].split("_")
    add_command_by_signature(int(addr), cmd, invoker, ssd_inst, int(value))

    expected_num_commands = 0
    for i in input["changed"]:
        if "empty" not in i:
            expected_num_commands += 1

    assert invoker.num_commands() == expected_num_commands
    files = set(os.listdir(BUFFER_DIR))
    assert files == set(input["changed"])


@pytest.mark.parametrize("input", [
    {
        "original": {
            "1": "1_E_0_0",
            "2": "2_empty",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_0_3",
        "changed": [
            "1_E_0_3", "2_empty", "3_empty", "4_empty", "5_empty"
        ],
    },
    {
        "original": {
            "1": "1_E_0_1",
            "2": "2_empty",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_0_3",
        "changed": [
            "1_E_0_3", "2_empty", "3_empty", "4_empty", "5_empty"
        ],
    },
    {
        "original": {
            "1": "1_E_0_3",
            "2": "2_empty",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_0_3",
        "changed": [
            "1_E_0_3", "2_empty", "3_empty", "4_empty", "5_empty"
        ],
    },
    {
        "original": {
            "1": "1_E_0_5",
            "2": "2_empty",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_0_3",
        "changed": [
            "1_E_0_5", "2_empty", "3_empty", "4_empty", "5_empty"
        ],
    },
    {
        "original": {
            "1": "1_E_0_5",
            "2": "2_empty",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_4_3",
        "changed": [
            "1_E_0_7", "2_empty", "3_empty", "4_empty", "5_empty"
        ],
    },
    {
        "original": {
            "1": "1_E_0_5",
            "2": "2_empty",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_5_3",
        "changed": [
            "1_E_0_8", "2_empty", "3_empty", "4_empty", "5_empty"
        ],
    },
    {
        "original": {
            "1": "1_E_0_5",
            "2": "2_W_5_0x00001234",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_5_3",
        "changed": [
            "1_E_0_8", "2_empty", "3_empty", "4_empty", "5_empty"
        ],
    },
    {
        "original": {
            "1": "1_E_0_5",
            "2": "2_empty",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_4_10",
        "changed": [
            "1_E_0_10", "2_E_10_4", "3_empty", "4_empty", "5_empty"
        ],
    },
    {
        "original": {
            "1": "1_E_0_5",
            "2": "2_empty",
            "3": "3_empty",
            "4": "4_empty",
            "5": "5_empty",
        },
        "new_input": "E_5_10",
        "changed": [
            "1_E_0_10", "2_E_10_5", "3_empty", "4_empty", "5_empty"
        ],
    },
])
def test_13_merge_erase(ctx, input):
    ssd_inst, invoker = ctx
    invoker.flush()

    # 기존 입력
    for num in input["original"]:
        if "empty" in input["original"][num]:
            continue
        _, cmd, addr, value = input["original"][num].split("_")
        add_command_by_signature(addr, cmd, invoker, ssd_inst, value)

    # 새로운 입력
    cmd, addr, value = input["new_input"].split("_")
    add_command_by_signature(int(addr), cmd, invoker, ssd_inst, int(value))

    expected_num_commands = 0
    for i in input["changed"]:
        if "empty" not in i:
            expected_num_commands += 1

    assert invoker.num_commands() == expected_num_commands
    files = set(os.listdir(BUFFER_DIR))
    assert files == set(input["changed"])
