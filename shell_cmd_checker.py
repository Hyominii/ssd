import shlex
import subprocess

from logger import Logger
from decorators import trace
from utils import get_class_and_method_name

logger = Logger()

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

COMMAND_DESCRIPTION = [
    "팀명: BestReviewer",
    "팀장: 이장희 / 팀원: 김대용, 최도현, 박윤상, 최동희, 안효민, 김동훈",
    "",
    "사용 가능한 명령어:",
    "  write <LBA> <Value>                : 특정 LBA에 값 저장",
    "  read <LBA>                         : 특정 LBA 값 읽기",
    "  erase <Start_LBA> <Size>           : Start_LBA부터 Size만큼 값 초기화",
    "  erase_range <Start_LBA> <End_LBA>  : Start_LBA부터 End_LBA까지 값 초기화 ",
    "  fullwrite <Value>                  : 전체 LBA에 동일 값 저장",
    "  fullread                           : 전체 LBA 읽기 및 출력",
    "  1_FullWriteAndReadCompare          : 전체 LBA 쓰기 및 비교",
    "  2_PartialLBAWrite                  : LBA 0 ~ 4 쓰기 및 읽기 30회",
    "  3_WriteReadAging                   : LBA 0, 99 랜덤 값 쓰기 및 읽기 200회",
    "  4_EraseAndWriteAging               : LBA 짝수번호에 값을 두번 쓰고 및 size 3 만큼 지우기를 30회 반복함",
    "  help                               : 도움말 출력",
    "  exit                               : 종료"
]


def print_invalid_command():
    print("INVALID COMMAND")


def is_valid_command(command):
    parts = shlex.split(command)
    if not parts:
        logger.print(get_class_and_method_name(), "empty command")
        return False

    cmd_name, *cmd_args = parts
    spec = COMMAND_SPEC.get(cmd_name)
    if not spec:
        logger.print(get_class_and_method_name(), f"entered invalid command => '{cmd_name}'")
        return False

    expected_arg_count, _, _ = spec

    if len(cmd_args) != expected_arg_count:
        logger.print(get_class_and_method_name(),
                     f"the number of args({cmd_args}) is not same as {expected_arg_count}")
    return len(cmd_args) == expected_arg_count


def is_valid_address(address: str):
    try:
        address_int = int(address)
    except ValueError:
        logger.print(get_class_and_method_name(), "정수형으로 변환할 수 없는 경우 (예: '0.5')")
        return False  # 정수형으로 변환할 수 없는 경우 (예: "0.5")

    if 0 <= address_int <= 99:
        return True
    else:
        logger.print(get_class_and_method_name(), "유효한 범위(0~99)를 벗어난 경우")
        return False  # 유효한 범위(0~99)를 벗어난 경우


def is_valid_size(lba_size):
    try:
        lba_size = int(lba_size)
        return True
    except ValueError:
        logger.print(get_class_and_method_name(), "정수형으로 변환할 수 없는 경우 (예: '0.5')")
        return False  # 정수형으로 변환할 수 없는 경우 (예: "0.5")


def format_hex_value(value: str) -> str | None:
    if not value.startswith('0x'):  # str 시작이 0x로 시작되어야함
        return None

    # 값의 범위를 체크함
    hex_str = value[2:]

    try:
        int_value = int(hex_str, 16)
    except ValueError:
        logger.print(get_class_and_method_name(), "Value error 발생")
        return None

    if not (0 <= int_value <= 0xFFFFFFFF):
        logger.print(get_class_and_method_name(), "유효한 범위(0 ~ 0xFFFFFFFF)를 벗어난 경우")
        return None

    return f'0x{int_value:08X}'
