import shlex
import subprocess

COMMAND_SPEC = {
    "exit": (0, "exit", ""),
    "help": (0, "help", ""),
    "fullread": (0, "full_read", ""),
    "write": (2, "write", ""),
    "read": (1, "read", ""),
    "erase": (2, "erase", ""),
    "erase_range": (2, "erase_range", ""),
    "fullwrite": (1, "full_write", ""),
    # scripts-tagged commands
    "1_": (0, "full_write_and_read_compare", "scripts"),
    "1_FullWriteAndReadCompare": (0, "full_write_and_read_compare", "scripts"),
    "2_": (0, "partial_lba_write", "scripts"),
    "2_PartialLBAWrite": (0, "partial_lba_write", "scripts"),
    "3_": (0, "write_read_aging", "scripts"),
    "3_WriteReadAging": (0, "write_read_aging", "scripts"),
    "4_": (0, "erase_write_aging", "scripts"),
    "4_EraseAndWriteAging": (0, "erase_write_aging", "scripts"),
}


def print_invalid_command():
    print("INVALID COMMAND")

def is_valid_command(command):
    parts = shlex.split(command)
    if not parts:
        return False

    cmd_name, *cmd_args = parts
    spec = COMMAND_SPEC.get(cmd_name)
    if not spec:
        return False

    expected_arg_count, _, _ = spec
    return len(cmd_args) == expected_arg_count


def is_valid_address(address: str):
    try:
        address_int = int(address)
    except ValueError:
        return False  # 정수형으로 변환할 수 없는 경우 (예: "0.5")

    if 0 <= address_int <= 99:
        return True
    else:
        return False  # 유효한 범위(0~99)를 벗어난 경우


def is_valid_size(lba_size):
    try:
        lba_size = int(lba_size)
        return True
    except ValueError:
        return False  # 정수형으로 변환할 수 없는 경우 (예: "0.5")


def format_hex_value(value: str) -> str | None:
    if not value.startswith('0x'):  # str 시작이 0x로 시작되어야함
        return None

    # 값의 범위를 체크함
    hex_str = value[2:]

    try:
        int_value = int(hex_str, 16)
    except ValueError:
        return None

    if not (0 <= int_value <= 0xFFFFFFFF):
        return None

    return f'0x{int_value:08X}'
