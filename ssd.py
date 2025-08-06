import os
import sys

from abc import ABC, abstractmethod

OUTPUT_FILE = 'ssd_output.txt'
TARGET_FILE = 'ssd_nand.txt'
BLANK_STRING = "0x00000000"
ERROR_STRING = 'ERROR'


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
        if (address < 0 or address >= 100):
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

    def write(self, address: str, value: str) -> None:
        if not address.isdigit():
            with open(OUTPUT_FILE, 'w') as f:
                f.write('ERROR')
        return


def main():
    if len(sys.argv) < 3:
        print("Usage: ssd.py <command> <arg1> [arg2]")
        sys.exit(1)

    command = sys.argv[1]
    arg1 = sys.argv[2]
    arg2 = sys.argv[3] if len(sys.argv) > 3 else None

    ssd = SSD()

    if command == "R":
        ssd.read(arg1)
    elif command == "W":
        if arg2 is None:
            print("Missing value for write")
            sys.exit(1)
        ssd.write(arg1, arg2)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
