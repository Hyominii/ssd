
import os

OUTPUT_FILE = '../ssd_output.txt'
TARGET_FILE = '../ssd_nand.txt'
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

    def write(self, address: int, value: str) -> None:
        if not (isinstance(address, int)):
            with open(OUTPUT_FILE, 'w') as f:
                f.write('ERROR')

        if address == 0:
            with open(TARGET_FILE, 'w') as f:
                f.write(value)

        with open(TARGET_FILE, 'r') as f:
            lines = [line.rstrip('\n') for line in f]

        lines[19] = '0x00000001'

        with open(TARGET_FILE, 'w') as f:
            for line in lines:
                f.write(line + '\n')



