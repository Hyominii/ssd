import os
import sys

from abc import ABC, abstractmethod
from file_handler_ import SimpleFileHandler, MultilineFileWriter
from command import CommandInvoker, Command

OUTPUT_FILE = 'ssd_output.txt'
TARGET_FILE = 'ssd_nand.txt'
BLANK_STRING = "0x00000000"
ERROR_STRING = 'ERROR'
SSD_SIZE = 100
MIN_VALUE = 0x00000000
MAX_VALUE = 0xFFFFFFFF
BUFFER_DIR = 'buffer'


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
        # 파일이 없으면 새로 생성
        # 100칸이 있어야 하므로 100개의 BLANK VALUE 생성
        if os.path.exists(TARGET_FILE):
            return
        self._target_file_handler.write_lines([BLANK_STRING for _ in range(100)])
        return

    def read(self, address: int) -> int:
        if not self._check_lda_validation(address):
            return 1

        read_value = self._target_file_handler.read_specific_line(address)
        if not self._value_validation(read_value):
            return 1
        self._output_file_handler.write(read_value)
        return 0

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
        if (address < 0 or address >= 100):
            self._output_file_handler.write(ERROR_STRING)
            return False
        return True

    def write(self, address: int, value: str) -> None:
        if not isinstance(address, int) or not (0 <= address < SSD_SIZE):
            self._output_file_handler.write(ERROR_STRING)
            return
        lines = self._target_file_handler.read_all_lines()
        lines[address] = value
        self._target_file_handler.write_lines(lines)

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

    def execute(self):
        self.ssd.write(self._address, self._value)


class EraseCommand(Command):
    def __init__(self, ssd: SSD, address: int, size: int, buffer_num: int):
        self.ssd = ssd
        self._address = address
        self._sise = size
        self.rename_buffer(buffer_num, 'E', address, size)

    def execute(self):
        self.ssd.erase()


def main():
    if len(sys.argv) < 3:
        print("Usage: ssd.py <command> <arg1> [arg2]")
        sys.exit(1)

    cmd = sys.argv[1].upper()
    arg1 = sys.argv[2]
    arg2 = sys.argv[3] if len(sys.argv) > 3 else None

    ssd = SSD()
    invoker = CommandInvoker()

    if cmd == "R":
        invoker.add_command(ReadCommand(ssd, int(arg1)))
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
    invoker.flush()


if __name__ == "__main__":
    main()
