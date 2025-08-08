import shlex
import subprocess
import random
import os
import sys

from ssd_driver import SSDDriver
from logger import Logger
from decorators import trace
from utils import get_class_and_method_name
import shell_cmd_checker as checker

ROOT_DIR = os.path.dirname(__file__)

logger = Logger()

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

    @trace(logger)
    def read(self, address: str):
        if not checker.is_valid_address(address):
            return READ_ERROR

        status = self._ssd_driver.run_ssd_read(address=address)
        if status == READ_ERROR:
            logger.print(get_class_and_method_name(), "read error while run_ssd_read.")
            return status
        self._ssd_output_cache = self._ssd_driver.get_ssd_output()
        read_result = f'[Read] LBA {address.zfill(2)} : {self._ssd_output_cache}'
        if not self._is_runner:
            print(read_result)
        return status

    @trace(logger)
    def full_read(self):
        for address in range(0, 100):
            if self.read(address=str(address)) == READ_ERROR:
                return READ_ERROR
        return READ_SUCCESS

    @trace(logger)
    def write(self, address: str, value: str):
        formatted_value = checker.format_hex_value(value)
        if formatted_value == None or not checker.is_valid_address(address):
            return WRITE_ERROR

        ret = self._ssd_driver.run_ssd_write(address=address, value=formatted_value)
        return ret

    @trace(logger)
    def full_write(self, value: str):
        formatted_value = checker.format_hex_value(value)
        if formatted_value == None:
            return WRITE_ERROR

        for address in range(0, 100):
            if self._ssd_driver.run_ssd_write(address=str(address), value=formatted_value) == WRITE_ERROR:
                return WRITE_ERROR
        return WRITE_SUCCESS

    @trace(logger)
    def erase(self, address: str, lba_size: str):
        if not checker.is_valid_address(address) or not checker.is_valid_size(lba_size):
            return ERASE_ERROR

        start_lba, size = self.range_resize(address, lba_size)
        status = self._erase_in_chunks(start_lba=start_lba, size=size)
        return status

    @trace(logger)
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

    @trace(logger)
    def _erase_chunk(self, start_lba: int, size: int):
        status = self._ssd_driver.run_ssd_erase(address=str(start_lba), lba_size=str(size))
        # end = start + size - 1
        # print(f'[Erase] LBA {start:02d} ~ {end:02d}')
        return status

    @trace(logger)
    def _erase_in_chunks(self, start_lba: int, size: int):
        """MAX_ERASE_SIZE 단위로 잘라서 _erase_chunk 호출."""
        for offset in range(0, size, MAX_ERASE_SIZE):
            chunk_size = min(MAX_ERASE_SIZE, size - offset)
            chunk_start = start_lba + offset
            status = self._erase_chunk(chunk_start, chunk_size)
            if status == ERROR:
                return ERASE_ERROR
        return ERASE_SUCCESS

    @trace(logger)
    def _read_and_compare(self, address: str, written_value: str):
        read_status = self.read(address)
        if read_status != READ_SUCCESS:
            return False

        read_value = self._ssd_driver.get_ssd_output()
        if read_value != written_value:
            return False

        return True

    @trace(logger)
    def full_write_and_read_compare(self):
        for block in range(0, 100, 5):
            write_value = "0x12345678"
            for address in range(block, block + 5):
                self.write(str(address), write_value)
            for address in range(block, block + 5):
                if self._read_and_compare(str(address), write_value) == False:
                    return ERROR
        return SUCCESS

    @trace(logger)
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

    @trace(logger)
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

    @trace(logger)
    def erase_write_test(self):
        self.erase_range("0", "2")
        for x in range(2, 97, 2):
            self.write(str(x), "0x12345678")
            self.write(str(x), "0xaabbccdd")

            self.erase(str(x), "3")

            for i in range(3):
                if not self._read_and_compare(str(x + i), "0x00000000"):
                    return ERROR

    @trace(logger)
    def erase_write_aging(self):
        for iter in range(30):
            ret = self.erase_write_test()
            if ret == ERROR:
                return ERROR
        return SUCCESS

    @trace(logger)
    def flush(self):
        ret = self._ssd_driver.run_ssd_flush()
        return ret

    @trace(logger)
    def exit(self):
        raise SystemExit(0)

    @trace(logger)
    def help(self):
        print("\n".join(checker.COMMAND_DESCRIPTION))
        return SUCCESS

    @trace(logger)
    def run(self):
        if len(sys.argv) > 1:
            script_file = sys.argv[1]
            self.run_runner(script_file)
        else:
            self.run_shell()
        return

    @trace(logger)
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

    @trace(logger)
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
            if not checker.is_valid_command(command):
                checker.print_invalid_command()
                return
            if self.process_cmd(command) == False:
                return

    @trace(logger)
    def process_cmd(self, command):
        parts = shlex.split(command)
        if not parts:
            checker.print_invalid_command()
            return

        cmd_name, *cmd_args = parts
        spec = checker.COMMAND_SPEC.get(cmd_name)
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
            if cmd_name in ["write", "erase", "erase_range", "flush"]:
                ret = handler(*cmd_args)
                if ret == SUCCESS:
                    print(f"[{cmd_name.capitalize()}] Done")
            else:
                if self._is_runner:
                    print(f"{cmd_name}  ___  RUN...", flush=True, end="")
                ret = handler(*cmd_args) if expected_arg_count else handler()
                if tags == "scripts":
                    if ret == SUCCESS:
                        print("Pass")
                    else:
                        print("FAIL!")
                        return False

        except Exception as e:
            logger.print(get_class_and_method_name(), str(e))
            ret = ERROR

        if ret != SUCCESS:
            checker.print_invalid_command()

    @trace(logger)
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
