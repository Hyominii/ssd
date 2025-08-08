import shlex
import subprocess
import random
import os
import sys

from shell_cmd_checker import COMMAND_SPEC
from ssd_driver import SSDDriver
import shell_cmd_checker as checker

ROOT_DIR = os.path.dirname(__file__)

SUCCESS = 0
ERROR = -1
WRITE_SUCCESS = SUCCESS
WRITE_ERROR = ERROR
READ_SUCCESS = SUCCESS
READ_ERROR = ERROR

ERASE_SUCCESS = SUCCESS
ERASE_ERROR = ERROR
MAX_ERASE_SIZE = 10


class TestShellApp:
    def __init__(self, ssd_driver=None):
        if ssd_driver == None:
            ssd_driver = SSDDriver()

        self._ssd_driver = ssd_driver
        self._ssd_output_cache = None
        self._is_runner = False

    def read(self, address: str):
        if not checker.is_valid_address(address):
            return READ_ERROR

        status = self._ssd_driver.run_ssd_read(address=address)
        if status == READ_ERROR:
            return status
        self._ssd_output_cache = self._ssd_driver.get_ssd_output()
        read_result = f'[Read] LBA {address.zfill(2)} : {self._ssd_output_cache}'
        if not self._is_runner:
            print(read_result)
        return status

    def full_read(self):
        for address in range(0, 100):
            if self.read(address=str(address)) == READ_ERROR:
                return READ_ERROR
        return READ_SUCCESS

    def write(self, address: str, value: str):
        formatted_value = checker.format_hex_value(value)
        if formatted_value == None or not checker.is_valid_address(address):
            return WRITE_ERROR

        ret = self._ssd_driver.run_ssd_write(address=address, value=formatted_value)
        return ret

    def full_write(self, value: str):
        formatted_value = checker.format_hex_value(value)
        if formatted_value == None:
            return WRITE_ERROR

        for address in range(0, 100):
            if self._ssd_driver.run_ssd_write(address=str(address), value=formatted_value) == WRITE_ERROR:
                return WRITE_ERROR
        return WRITE_SUCCESS

    def erase(self, address: str, lba_size: str):
        if not checker.is_valid_address(address) or not checker.is_valid_size(lba_size):
            return ERASE_ERROR

        start_lba, size = self.range_resize(address, lba_size)
        status = self._erase_in_chunks(start_lba=start_lba, size=size)
        return status

    def erase_range(self, start_lba: str, end_lba: str):
        if not checker.is_valid_address(start_lba) or not checker.is_valid_address(end_lba):
            return ERASE_ERROR

        low, high = sorted((int(start_lba), int(end_lba)))

        low = max(0, low)
        high = min(99, high)

        # Erase size 계산
        size = high - low + 1
        if size <= 0: return ERASE_ERROR

        status = self._erase_in_chunks(start_lba=low, size=size)
        return status

    def _erase_chunk(self, start_lba: int, size: int):
        status = self._ssd_driver.run_ssd_erase(address=str(start_lba), lba_size=str(size))
        # end = start + size - 1
        # print(f'[Erase] LBA {start:02d} ~ {end:02d}')
        return status

    def _erase_in_chunks(self, start_lba: int, size: int):
        """MAX_ERASE_SIZE 단위로 잘라서 _erase_chunk 호출."""
        for offset in range(0, size, MAX_ERASE_SIZE):
            chunk_size = min(MAX_ERASE_SIZE, size - offset)
            chunk_start = start_lba + offset
            status = self._erase_chunk(chunk_start, chunk_size)
            if status == ERROR:
                return ERASE_ERROR
        return ERASE_SUCCESS

    def _read_and_compare(self, address: str, written_value: str):
        read_status = self.read(address)
        if read_status != READ_SUCCESS:
            return False

        read_value = self._ssd_driver.get_ssd_output()
        if read_value != written_value:
            return False

        return True

    def full_write_and_read_compare(self):
        for block in range(0, 100, 5):
            write_value = "0x12345678"
            for address in range(block, block + 5):
                self.write(str(address), write_value)
            for address in range(block, block + 5):
                if self._read_and_compare(str(address), write_value) == False:
                    return ERROR
        return SUCCESS

    def partial_lba_write(self):
        for iter in range(30):
            self.write("4", "0x12345678")
            self.write("0", "0x12345678")
            self.write("3", "0x12345678")
            self.write("1", "0x12345678")
            self.write("2", "0x12345678")
            for address in range(0, 5):
                if self._read_and_compare(str(address), "0x12345678") == False:
                    return ERROR
        return SUCCESS

    def write_read_aging(self):
        for iter in range(200):
            value = random.randint(0, 0xFFFFFFFF)
            write_value = f"0x{value:08X}"
            self.write("0", write_value)
            self.write("99", write_value)

            if self._read_and_compare("0", write_value) == False:
                return ERROR
            if self._read_and_compare("99", write_value) == False:
                return ERROR
        return SUCCESS

    def erase_write_test(self):
        self.erase_range("0", "3")
        for x in range(2, 97, 2):
            self.write(str(x), "0x12345678")
            self.write(str(x), "0xaabbccdd")

            self.erase_range(str(x), "3")

            for i in range(3):
                if not self._read_and_compare(str(x + i), "0x00000000"):
                    return ERROR

    def erase_write_aging(self):
        for iter in range(30):
            ret = self.erase_write_test()
            if ret == ERROR:
                print("FAIL")
                return ERROR
        print("PASS")
        return SUCCESS

    def exit(self):
        raise SystemExit(0)

    def help(self):
        print("팀명: BestReviewer")
        print("팀장: 이장희 / 팀원: 김대용, 최도현, 박윤상, 최동희, 안효민, 김동훈")
        print("사용 가능한 명령어:")
        print("  write <LBA> <Value>                : 특정 LBA에 값 저장")
        print("  read <LBA>                         : 특정 LBA 값 읽기")
        print("  erase <Start_LBA> <Size>           : Start_LBA부터 Size만큼 값 초기화")
        print("  erase_range <Start_LBA> <End_LBA>  : Start_LBA부터 End_LBA까지 값 초기화 ")
        print("  fullwrite <Value>                  : 전체 LBA에 동일 값 저장")
        print("  fullread                           : 전체 LBA 읽기 및 출력")
        print("  1_FullWriteAndReadCompare          : 전체 LBA 쓰기 및 비교")
        print("  2_PartialLBAWrite                  : LBA 0 ~ 4 쓰기 및 읽기 30회")
        print("  3_WriteReadAging                   : LBA 0, 99 랜덤 값 쓰기 및 읽기 200회")
        print("  4_EraseAndWriteAging               : LBA 짝수번호에 값을 두번 쓰고 및 size 3 만큼 지우기를 30회 반복함")
        print("  help                               : 도움말 출력")
        print("  exit                               : 종료")
        return SUCCESS

    def run(self):
        if len(sys.argv) > 1:
            script_file = sys.argv[1]
            self.run_runner(script_file)
        else:
            self.run_shell()
        return

    def run_shell(self, max_iterations: int = None):
        self._is_runner = False
        print(f"안녕하세요, SSD 검증용 Test Shell App을 시작합니다.\n")

        while True:
            if max_iterations is not None:
                if max_iterations <= 0:
                    break
                max_iterations -= 1
            command = input("Shell > ").strip()
            if checker.is_valid_command(command) == False:
                checker.print_invalid_command()
                continue

            self.process_cmd(command)

    def run_runner(self, script_file: str = ""):
        self._is_runner = True
        if not os.path.exists(script_file):
            checker.print_invalid_command()
            return

        with open(script_file, 'r') as f:
            commands = [line.strip() for line in f if line.strip()]

        if not commands:
            checker.print_invalid_command()
            return

        for command in commands:
            if checker.is_valid_command(command) == False:
                checker.print_invalid_command()
                return
            if self.process_cmd(command) == False:
                return

    def process_cmd(self, command):
        parts = shlex.split(command)
        if not parts:
            checker.print_invalid_command()
            return

        cmd_name, *cmd_args = parts
        spec = COMMAND_SPEC.get(cmd_name)
        if not spec:
            checker.print_invalid_command()
            return

        expected_arg_count, method_name, tags = spec
        handler = getattr(self, method_name)

        if len(cmd_args) != expected_arg_count:
            checker.print_invalid_command()
            return

        if self._is_runner:
            if tags != "scripts":
                checker.print_invalid_command()
                return

        try:
            if cmd_name in ["write", "erase", "erase_range"]:
                ret = handler(cmd_args)
                if ret == SUCCESS:
                    print(f"[{cmd_name.capitalize()}] Done")
            else:
                if self._is_runner:
                    print(f"{cmd_name}  ___  RUN...", flush=True, end="")
                ret = handler(cmd_args) if expected_arg_count else handler()
                if tags == "scripts":
                    if ret == SUCCESS:
                        print("Pass")
                    else:
                        print("FAIL!")
                        return False

        except Exception:
            ret = ERROR

        if ret != SUCCESS:
            checker.print_invalid_command()

    def range_resize(self, address: str, lba_size: str):
        start, size = int(address), int(lba_size)
        if size > 0:
            max_blocks = 100 - start
            block_count = min(size, max_blocks)
            erase_start = start

        else:  # 음수 방향: 뒤로 abs(cnt) 블록
            max_blocks = start + 1
            block_count = min(-size, max_blocks)
            # 음수 방향이므로 작은 주소부터 시작
            erase_start = start - (block_count - 1)
        return (erase_start, block_count)


if __name__ == "__main__":
    app = TestShellApp()
    app.run()
