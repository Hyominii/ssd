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

    def init_target_file(self):
        # 파일이 없으면 새로 생성
        # 100칸이 있어야 하므로 100개의 BLANK VALUE 생성
        if os.path.exists(TARGET_FILE):
            return
        self._target_file_handler.write_lines([(BLANK_STRING) for _ in range(100)])
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

        lines = self._target_file_handler.real_all_lines()
        self._target_file_handler.write_lines(lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: ssd.py <command> <arg1> [arg2]")
        sys.exit(1)

    command = sys.argv[1]
    arg1 = sys.argv[2]
    arg2 = sys.argv[3] if len(sys.argv) > 3 else None

    ssd = SSD()

    if command == "R":
        ssd.read(int(arg1))
    elif command == "W":
        if arg2 is None:
            print("Missing value for write")
            sys.exit(1)
        ssd.write(int(arg1), arg2)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
