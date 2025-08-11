import glob
import os
import sys
from pathlib import Path
import re

from abc import ABC, abstractmethod
from file_handler import SimpleFileHandler, MultilineFileWriter

from policy import ignore_cmd_policy, merge_erase_policy

# ssd.py 파일이 있는 디렉토리 내 (프로젝트 루트) 절대 경로
_PROJECT_ROOT = Path(__file__).resolve().parent
BUFFER_DIR = str(_PROJECT_ROOT / "buffer")  # ← 여기만 변경
OUTPUT_FILE = str(_PROJECT_ROOT / "ssd_output.txt")
TARGET_FILE = str(_PROJECT_ROOT / "ssd_nand.txt")

BLANK_STRING = "0x00000000"
ERROR_STRING = 'ERROR'
SSD_SIZE = 100
MIN_VALUE = 0x00000000
MAX_VALUE = 0xFFFFFFFF
MAX_COMMANDS = 5


class SSD:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._target_file_handler = MultilineFileWriter(SimpleFileHandler(TARGET_FILE))
            self._output_file_handler = SimpleFileHandler(OUTPUT_FILE)
            self.init_target_file()
            self.init_command_buffer()

    def init_command_buffer(self):
        buffer_dir = BUFFER_DIR
        os.makedirs(buffer_dir, exist_ok=True)  # 이미 있어도 에러 안 나게

        # 2. 파일 생성
        for i in range(1, 6):
            # 해당 i로 시작하는 파일이 이미 존재하는지 확인
            exists = any(
                filename.startswith(f"{i}_")
                for filename in os.listdir(buffer_dir)
            )

            if not exists:
                file_path = os.path.join(buffer_dir, f"{i}_empty")
                with open(file_path, "w") as f:
                    f.write("")

    def init_target_file(self):
        # SSD init시에 nand.txt파일이 올바른 포멧인지 확인합니다
        if os.path.exists(TARGET_FILE) and self._target_validation():
            return
        # 파일이 없으면 100개의 BLANK VALUE 생성
        self._target_file_handler.write_lines([BLANK_STRING for _ in range(SSD_SIZE)])
        return

    def read(self, address: int) -> int:
        if not self._check_lda_validation(address):
            return 1

        read_value = self._target_file_handler.read_specific_line(address)
        if not self._value_validation(read_value):
            return 1
        self._output_file_handler.write(read_value)
        return 0

    def _target_validation(self, filename=TARGET_FILE) -> bool:
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()

                # 모든 라인에서 개행 문자를 제거한 후 유효한 라인만 필터링합니다.
                sanitized_lines = [line.rstrip('\n') for line in lines if line.strip()]

                # 개행 문자를 제거한 라인 수가 SSD_SIZE와 일치하는지 확인합니다.
                if len(sanitized_lines) != SSD_SIZE:
                    return False

                for line in sanitized_lines:
                    if not self._value_validation(line):
                        return False
        except IOError:
            return False
        return True

    def _value_validation(self, read_value):
        if not read_value.startswith(('0x', '0X')) or len(read_value) != 10:
            self._output_file_handler.write(ERROR_STRING)
            return False
        try:
            read_value_hex = int(read_value, 16)
        except ValueError:
            self._output_file_handler.write(ERROR_STRING)
            return False
        if read_value_hex < MIN_VALUE or read_value_hex > MAX_VALUE:
            self._output_file_handler.write(ERROR_STRING)
            return False
        return True

    def _check_lda_validation(self, address) -> bool:
        if not isinstance(address, int) or not (0 <= address < SSD_SIZE):
            self._output_file_handler.write(ERROR_STRING)
            return False
        if (address < 0 or address >= SSD_SIZE):
            self._output_file_handler.write(ERROR_STRING)
            return False
        return True

    def write(self, address: int, value: str) -> None:
        if not isinstance(address, int) or not (0 <= address < SSD_SIZE):
            self._output_file_handler.write(ERROR_STRING)
            return
        lines = self._target_file_handler.read_all_lines()
        lines[address] = value  # 실제 업데이트 추가
        self._target_file_handler.write_lines(lines)

    def erase(self, address: int, size: int) -> None:  # erase 메서드 추가 (old 기반)
        if not isinstance(address, int) or not isinstance(size, int) or size > 10:
            self._output_file_handler.write(ERROR_STRING)
            return

        if not (0 <= address < SSD_SIZE) or size < 0 or (address + size > SSD_SIZE):
            self._output_file_handler.write(ERROR_STRING)
            return

        if size == 0:
            return

        lines = self._target_file_handler.read_all_lines()
        for i in range(address, address + size):
            lines[i] = BLANK_STRING
        self._target_file_handler.write_lines(lines)

    def _read_from_nand(self, lba: int) -> str:
        if not os.path.exists(TARGET_FILE):
            self._initialize_nand()

        with open(TARGET_FILE, 'r') as f:
            lines = f.readlines()

        if len(lines) < SSD_SIZE:
            lines += [BLANK_STRING + '\n'] * (SSD_SIZE - len(lines))

        if 0 <= lba < SSD_SIZE:
            value = lines[lba].strip()
            if re.match(r'^0x[0-9A-F]{8}$', value):
                return value
        return BLANK_STRING

    def _initialize_nand(self):
        with open(TARGET_FILE, 'w') as f:
            for _ in range(SSD_SIZE):
                f.write(BLANK_STRING + '\n')


class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    def set_path(self, file_path: str):
        self.path = file_path

    def rename_buffer(self, buffer_num, cmd, address, size):
        path = f'{buffer_num}_{cmd}_{address}_{size}'
        self.set_path(path)
        for filename in os.listdir(BUFFER_DIR):
            if filename.startswith(f'{buffer_num}'):
                old_path = os.path.join(BUFFER_DIR, filename)
                new_path = os.path.join(BUFFER_DIR, path)
                os.rename(old_path, new_path)
                # print(f"Renamed {filename} -> {}2_string")
                break  # ✅ 하나만 처리하고 끝냄


class ReadCommand(Command):
    def __init__(self, ssd: SSD, address: int):
        self.ssd = ssd
        self._address = address

    def execute(self):
        self.ssd.read(self.address)

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
        self._address = address


class WriteCommand(Command):
    def __init__(self, ssd: SSD, address: int, value: str, buffer_num: int):
        self.ssd = ssd
        self._address = address
        self._value = value
        self.rename_buffer(buffer_num, 'W', address, value)

    def execute(self):
        self.ssd.write(self.address, self.value)

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
        self._address = address

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class EraseCommand(Command):
    def __init__(self, ssd: SSD, address: int, size: int, buffer_num: int):
        self.ssd = ssd
        self._address = address
        self._size = size  # 오타 수정
        self.rename_buffer(buffer_num, 'E', address, size)

    def execute(self):
        self.ssd.erase(self.address, self.size)  # 인자 전달 추가

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
        self._address = address

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size


class CommandInvoker:
    def __init__(self, ssd: SSD):
        self._commands = []
        self._ssd = ssd

        if not os.path.isdir(BUFFER_DIR):
            self.init_command_buffer()
            return

        for filename in os.listdir(BUFFER_DIR):
            # file_path = os.path.join(BUFFER_DIR, filename)
            cmd_arg = filename.split('_')
            cmd = cmd_arg[1]
            if cmd == 'empty':
                break

            arg1 = cmd_arg[2]
            arg2 = cmd_arg[3]

            if cmd_arg[1] == "W":
                self.add_command(WriteCommand(ssd, int(arg1), arg2, self.num_commands() + 1))
            elif cmd_arg[1] == "E":
                self.add_command(EraseCommand(ssd, int(arg1), int(arg2), self.num_commands() + 1))
            elif cmd_arg[1] == "F":
                self.flush()
            else:
                print(f"Unknown command: {cmd}")
                sys.exit(1)

    def _sync_buffer_files(self) -> None:
        os.makedirs(BUFFER_DIR, exist_ok=True)
        for f in os.listdir(BUFFER_DIR):
            os.remove(os.path.join(BUFFER_DIR, f))
        for i in range(1, 6):
            open(os.path.join(BUFFER_DIR, f"{i}_empty"), "w").close()
        for idx, cmd in enumerate(self._commands, 1):
            if isinstance(cmd, WriteCommand):
                cmd.rename_buffer(idx, 'W', cmd.address, cmd.value)
            elif isinstance(cmd, EraseCommand):
                cmd.rename_buffer(idx, 'E', cmd.address, cmd.size)

    def add_command(self, cmd: Command) -> None:
        # Read는 즉시 실행
        if isinstance(cmd, ReadCommand):
            cmd.execute()
            return

        # 1) 정책 적용 - 무효/중복 제거 및 기본 정리
        make_erase = lambda a, s: EraseCommand(self._ssd, a, s, 0)

        new_queue = ignore_cmd_policy(
            queue=self._commands,
            incoming=cmd,
            WriteCls=WriteCommand,
            EraseCls=EraseCommand,
            make_erase=make_erase,
        )

        self._commands = new_queue

        # 용량 체크(정책 적용 후 길이 기준) - 넘치면 flush
        if len(self._commands) >= MAX_COMMANDS:
            self.flush()

        # 2) Erase면 병합 정책 적용, Write면 그대로 append
        if isinstance(cmd, EraseCommand):
            self._commands = merge_erase_policy(
                queue=self._commands,
                incoming_erase=cmd,
                EraseCls=EraseCommand,
                make_erase=make_erase,
                chunk_size=10,   # 기존 정책 유지
            )
        else:
            self._commands.append(cmd)

        # 3) 버퍼 파일과 동기화
        self._sync_buffer_files()

    def flush(self):
        for cmd in self._commands:
            cmd.execute()
        self._commands.clear()
        self.init_command_buffer()

    def num_commands(self):
        return len(self._commands)

    def init_command_buffer(self):
        buffer_dir = BUFFER_DIR
        os.makedirs(buffer_dir, exist_ok=True)  # 이미 있어도 에러 안 나게

        # 2. 파일 생성
        for i in range(1, 6):
            prefix_pattern = os.path.join(buffer_dir, f"{i}_*")
            matched_files = glob.glob(prefix_pattern)

            target_path = os.path.join(buffer_dir, f"{i}_empty")

            if matched_files:
                # 첫 번째로 매칭된 파일만 이름 변경
                os.rename(matched_files[0], target_path)
            else:
                # 파일 새로 생성
                with open(target_path, "w") as f:
                    f.write("")

    def get_buffer(self):
        return self._commands

    def fast_read(self, lba: int) -> str:
        for cmd in reversed(self._commands):
            if isinstance(cmd, WriteCommand) and cmd._address == lba:
                return cmd._value
            if isinstance(cmd, EraseCommand):
                if cmd._address <= lba < cmd._address + cmd._size:
                    return BLANK_STRING
        return self._ssd._read_from_nand(lba)


def is_valid_size(address: str, lba_size: str):
    try:
        address = int(address)
        lba_size = int(lba_size)
        if address + lba_size <= 100:
            return True
        else:
            return False
    except ValueError:
        return False  # 정수형으로 변환할 수 없는 경우 (예: "0.5")


def is_valid_address(address: str):
    try:
        address_int = int(address)
    except ValueError:
        return False  # 정수형으로 변환할 수 없는 경우 (예: "0.5")

    if 0 <= address_int <= 99:
        return True
    else:
        return False  # 유효한 범위(0~99)를 벗어난 경우


def is_valid_value(value: str) -> str | None:
    if not value.startswith('0x') or not len(value) == 10:  # str 시작이 0x로 시작되어야함
        return False

    # 값의 범위를 체크함
    hex_str = value[2:]

    try:
        int_value = int(hex_str, 16)
    except ValueError:
        return False

    if not (0x0 <= int_value <= 0xFFFFFFFF):
        return False

    return True


def main():
    if len(sys.argv) < 1:
        print("Usage: ssd.py <command> <arg1> [arg2]")
        sys.exit(1)

    cmd = sys.argv[1].upper()
    arg1 = sys.argv[2] if len(sys.argv) > 2 else None
    arg2 = sys.argv[3] if len(sys.argv) > 3 else None

    ssd = SSD()
    invoker = CommandInvoker(ssd)

    # if cmd == "R":
    #     # invoker.add_command(ReadCommand(ssd, int(arg1)))
    #     invoker.flush()
    #     ReadCommand(ssd, int(arg1)).execute()
    if cmd == "R":
        val = invoker.fast_read(int(arg1))
        ssd._output_file_handler.write(val)

    elif cmd == "W":
        if not is_valid_address(arg1) or not is_valid_value(arg2):
            ssd._output_file_handler.write("ERROR")
            print("ERROR W arguments are not valid")
            return

        invoker.add_command(WriteCommand(ssd, int(arg1), arg2, invoker.num_commands() + 1))

    elif cmd == "E":
        if not is_valid_address(arg1) or not is_valid_size(arg1, arg2):
            ssd._output_file_handler.write("ERROR")
            print("ERROR E arguments are not valid")
            return

        invoker.add_command(EraseCommand(ssd, int(arg1), int(arg2), invoker.num_commands() + 1))

    elif cmd == "F":
        invoker.flush()

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

    # flush
    # invoker.flush()


if __name__ == "__main__":
    main()
