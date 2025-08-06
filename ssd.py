
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
        # BLANK_VALUE = "0x00000000"
        # 파일이 없으면 새로 생성
        # 100칸이 있어야 하므로 100개의 BLANCK VALUE 생성
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                [f.write("0x00000000"+"\n") for _ in range(100)]
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

    def write(self, address: str, value: str) -> None:
        if not address.isdigit():
            with open(OUTPUT_FILE, 'w') as f:
                f.write('ERROR')
        return


