import glob
import os
import sys

from abc import ABC, abstractmethod
from file_handler import SimpleFileHandler, MultilineFileWriter

OUTPUT_FILE = 'ssd_output.txt'
TARGET_FILE = 'ssd_nand.txt'
BLANK_STRING = "0x00000000"
ERROR_STRING = 'ERROR'
SSD_SIZE = 100
MIN_VALUE = 0x00000000
MAX_VALUE = 0xFFFFFFFF
BUFFER_DIR = 'buffer'
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
        self.ssd.read(self._address)


class WriteCommand(Command):
    def __init__(self, ssd: SSD, address: int, value: str, buffer_num: int):
        self.ssd = ssd
        self._address = address
        self._value = value
        self.rename_buffer(buffer_num, 'W', address, value)

    def rename_buffer(self, buffer_num, cmd_type, address, value=None):  # 임시 구현 (실제 버퍼 로직 필요 시 확장)
        pass  # 버퍼 파일 rename 로직 미구현; 필요 시 추가

    def execute(self):
        self.ssd.write(self._address, self._value)


class EraseCommand(Command):
    def __init__(self, ssd: SSD, address: int, size: int, buffer_num: int):
        self.ssd = ssd
        self._address = address
        self._size = size  # 오타 수정
        self.rename_buffer(buffer_num, 'E', address, size)

    def rename_buffer(self, buffer_num, cmd_type, address, size=None):  # 임시 구현
        pass  # 버퍼 파일 rename 로직 미구현; 필요 시 추가

    def execute(self):
        self.ssd.erase(self._address, self._size)  # 인자 전달 추가


class CommandInvoker:
    def __init__(self, ssd: SSD):
        self._commands = []

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

    def add_command(self, cmd: Command):
        if len(self._commands) >= MAX_COMMANDS:
            self.flush()
        self._commands.append(cmd)

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

def main():
    if len(sys.argv) < 1:
        print("Usage: ssd.py <command> <arg1> [arg2]")
        sys.exit(1)

    cmd = sys.argv[1].upper()
    arg1 = sys.argv[2] if len(sys.argv) > 2 else None
    arg2 = sys.argv[3] if len(sys.argv) > 3 else None

    ssd = SSD()
    invoker = CommandInvoker(ssd)

    if cmd == "R":
        # invoker.add_command(ReadCommand(ssd, int(arg1)))
        invoker.flush()
        ReadCommand(ssd, int(arg1)).execute()
    elif cmd == "W":
        invoker.add_command(WriteCommand(ssd, int(arg1), arg2, invoker.num_commands() + 1))
    elif cmd == "E":
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
