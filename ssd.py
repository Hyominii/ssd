
import os

OUTPUT_FILE = 'ssd_output.txt'
TARGET_FILE = 'ssd_nand.txt'

ERROR_STRING = 'ERROR'

class SSD:
    def __init__(self):
        self.init_file(OUTPUT_FILE)
        self.init_file(TARGET_FILE)
        pass

    def init_file(self, filename: str):
        # 파일이 없으면 새로 생성
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write("")  # 빈 파일로 생성
        return

    def read(self, address: int) -> int:

        with open(TARGET_FILE, "r") as f:
            lines = f.readlines()

        if len(lines) >= address:
            return lines[address].rstrip("\n")  # 0-based index
        else:
            with open(OUTPUT_FILE, "w") as f:
                f.write(ERROR_STRING + "\n")
        return 0


    def write(self, address: int, value: str) -> int:

        if address < 0 or address > 100:
            with open(OUTPUT_FILE, "w") as f:
                f.write(ERROR_STRING + "\n")

        with open(TARGET_FILE, "r") as f:
            lines = f.readlines()

        # 줄이 address 줄보다 적으면 빈 줄로 채움
        while len(lines) < address:
            lines.append("\n")

        lines[address] = str + "\n"

        with open(TARGET_FILE, "w") as f:
            f.writelines(lines)
        return 0
