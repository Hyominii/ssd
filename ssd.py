import os
import sys

from abc import ABC, abstractmethod

from command import CommandInvoker, Command

OUTPUT_FILE = 'ssd_output.txt'
TARGET_FILE = 'ssd_nand.txt'
BLANK_STRING = "0x00000000"
ERROR_STRING = 'ERROR'
SSD_SIZE = 100
MIN_VALUE = 0x00000000
MAX_VALUE = 0xFFFFFFFF


class SSD:
    def __init__(self):
        self.init_output_file(OUTPUT_FILE)
        self.init_target_file(TARGET_FILE)

    def init_target_file(self, filename: str):
        # 파일이 없으면 새로 생성
        # 100칸이 있어야 하므로 100개의 BLANK VALUE 생성
        if os.path.exists(filename):
            return
        with open(filename, "w") as f:
            [f.write(BLANK_STRING + "\n") for _ in range(100)]
        return

    def init_output_file(self, filename: str):
        # 파일이 없으면 새로 생성
        if os.path.exists(filename):
            os.remove(filename)
        with open(filename, "w") as f:
            f.write("")
        return

    def read(self, address: int) -> int:
        if not self._check_lda_validation(address):
            return 1

        with open(TARGET_FILE, "r") as f:
            lines = f.readlines()

        read_value = lines[address].rstrip("\n")
        if not self._value_validation(address, lines, read_value):
            return 1
        with open(OUTPUT_FILE, "w") as f:
            f.write(read_value)
        return 0

    def write(self, address: int, value: str) -> None:
        if not isinstance(address, int) or not (0 <= address < SSD_SIZE):
            self._write_output(ERROR_STRING)
            return

        lines = self._read_lines()
        lines[address] = value
        self._write_lines(lines)

    def erase(self, address: int, size: int) -> None:
        if not isinstance(address, int) or not isinstance(size, int) or size > 10:
            self._write_output(ERROR_STRING)
            return

        if not (0 <= address < SSD_SIZE) or size < 0 or (address + size > SSD_SIZE):
            self._write_output(ERROR_STRING)
            return

        if size == 0:
            return

        lines = self._read_lines()
        for i in range(address, address + size):
            lines[i] = BLANK_STRING
        self._write_lines(lines)


    def _value_validation(self, address, lines, read_value):
        if not read_value.startswith(('0x', '0X')) or len(read_value) != 10:
            self._write_error_output()
            return False
        try:
            read_value_hex = int(read_value, 16)
        except ValueError:
            self._write_error_output()
            return False
        if read_value_hex < MIN_VALUE or read_value_hex > MAX_VALUE:
            self._write_error_output()
            return False
        if len(lines) < address:
            self._write_error_output()
            return False
        return True

    def _write_error_output(self):
        with open(OUTPUT_FILE, "w") as f:
            f.write(ERROR_STRING)

    def _check_lda_validation(self, address) -> bool:
        if not isinstance(address, int) or not (0 <= address < SSD_SIZE):
            with open(OUTPUT_FILE, "w") as f:
                f.write(ERROR_STRING)
                return False
        if (address < 0 or address >= 100):
            with open(OUTPUT_FILE, "w") as f:
                f.write(ERROR_STRING)
                return False
        return True

    def _write_output(self, content: str):
        with open(OUTPUT_FILE, 'w') as f:
            f.write(content)

    def _read_lines(self) -> list[str]:
        with open(TARGET_FILE, 'r') as f:
            return [line.rstrip('\n') for line in f]

    def _write_lines(self, lines: list[str]):
        with open(TARGET_FILE, 'w') as f:
            f.writelines(line + '\n' for line in lines)



class ReadCommand(Command):
    def __init__(self, ssd: SSD, address: int):
        self.ssd = ssd
        self._address = address

    def execute(self):
        self.ssd.read(self._address)


class WriteCommand(Command):
    def __init__(self, ssd: SSD, address: int, value: str):
        self.ssd = ssd
        self._address = address
        self._value = value

    def execute(self):
        self.ssd.write(self._address, self._value)


class EraseCommand(Command):
    def __init__(self, ssd: SSD, address: int, size: int):
        self.ssd = ssd
        self._address = address
        self._size = size

    def execute(self):
        self.ssd.erase(self._address, self._size)


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
        invoker.add_command(WriteCommand(ssd, int(arg1), arg2))
    elif cmd == "E":
        invoker.add_command(EraseCommand(ssd, int(arg1), int(arg2)))
    elif cmd == "F":
        invoker.flush()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

    # flush
    invoker.flush()


if __name__ == "__main__":
    main()
