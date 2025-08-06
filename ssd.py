
import os
from abc import ABC, abstractmethod

OUTPUT_FILE = 'ssd_output.txt'
TARGET_FILE = 'ssd_nand.txt'
BLANK_STRING = "0x00000000"
ERROR_STRING = 'ERROR'
SSD_SIZE = 100


class SSD:
    def __init__(self):
        self.init_output_file(OUTPUT_FILE)
        self.init_target_file(TARGET_FILE)

    def init_target_file(self, filename: str):
        # 파일이 없으면 새로 생성
        # 100칸이 있어야 하므로 100개의 BLANK VALUE 생성
        if os.path.exists(filename):
            os.remove(filename)
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
        if not isinstance(address, (int, float)):
            with open(OUTPUT_FILE, "w") as f:
                f.write(ERROR_STRING)
            return 1
        if (address<0  or address >=100):
            with open(OUTPUT_FILE, "w") as f:
                f.write(ERROR_STRING)
            return 1

        with open(TARGET_FILE, "r") as f:
            lines = f.readlines()

        if len(lines) >= address:
            with open(OUTPUT_FILE, "w") as f:
                f.write(lines[address].rstrip("\n"))
        else:
            with open(OUTPUT_FILE, "w") as f:
                f.write(ERROR_STRING)
        return 0

      
    def _write_output(self, content: str):
        with open(OUTPUT_FILE, 'w') as f:
            f.write(content)


    def _read_lines(self) -> list[str]:
        with open(TARGET_FILE, 'r') as f:
            return [line.rstrip('\n') for line in f]


    def _write_lines(self, lines: list[str]):
        with open(TARGET_FILE, 'w') as f:
            f.writelines(line + '\n' for line in lines)


    def write(self, address: int, value: str) -> None:
        if not isinstance(address, int) or not (0 <= address < SSD_SIZE):
            self._write_output(ERROR_STRING)
            return

        lines = self._read_lines()
        lines[address] = value
        self._write_lines(lines)

        with open(TARGET_FILE, 'r') as f:
            lines = [line.rstrip('\n') for line in f]

        lines[19] = '0x00000001'

        with open(TARGET_FILE, 'w') as f:
            for line in lines:
                f.write(line + '\n')

