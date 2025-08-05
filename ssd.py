
import os

READ_FILE = 'ssd_output.txt'
WRITE_FILE = 'ssd_nand.txt'

class SSD:
    def __init__(self):
        pass

    def get_file(filename: str):
        # 파일이 없으면 새로 생성
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write("")  # 빈 파일로 생성

        # 존재하는 파일을 열어서 반환 (쓰기 모드가 아니므로 변경 없음)
        return open(filename, "r")  # 또는 "r+", "a+" 등 필요에 따라 변경 가능

    def read(self, address: int) -> int:

        f = self.get_file(READ_FILE)

        return 0


    def write(self, address: int, value: str) -> int:

        f = self.get_file(WRITE_FILE)
        return 0
