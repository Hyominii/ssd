import shlex
import subprocess
import random
import os
import sys

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


class SSDDriver:
    def run_ssd_write(self, address: str, value: str):
        command = ['python', 'ssd.py', 'W', str(address), str(value)]
        result = subprocess.run(command, cwd=ROOT_DIR, capture_output=True, text=True)

        if result.returncode == 0:
            return WRITE_SUCCESS
        else:
            return WRITE_ERROR

    def run_ssd_erase(self, address: str, lba_size: str):
        command = ['python', 'ssd.py', 'E', str(address), str(lba_size)]
        result = subprocess.run(command, cwd=ROOT_DIR, capture_output=True, text=True)

        if result.returncode == 0:
            return ERASE_SUCCESS
        else:
            return ERASE_ERROR

    def run_ssd_read(self, address: str):
        command = ['python', 'ssd.py', 'R', str(address)]
        result = subprocess.run(command, cwd=ROOT_DIR, capture_output=True, text=True)
        if result.returncode == 0:
            return READ_SUCCESS
        else:
            return READ_ERROR

    def get_ssd_output(self, file_path: str = ROOT_DIR + "/ssd_output.txt"):
        with open(file_path, 'r', encoding='utf-8') as f:
            line = f.readline().rstrip("\n")

        if len(line) != 10:
            raise ValueError(f"Error, value Length: {len(line)})")
        return line


class TestShellApp:
    def __init__(self, ssd_driver=None):
        if ssd_driver == None:
            ssd_driver = SSDDriver()

        self._ssd_driver = ssd_driver
        self._ssd_output_cache = None

        self.command_specs = {
            "exit": {"args": 0, "func": lambda: self.exit(), "tags": ""},
            "help": {"args": 0, "func": lambda: self.help(), "tags": ""},
            "fullread": {"args": 0, "func": lambda: self.full_read(), "tags": ""},
            "write": {"args": 2, "func": lambda args: self.write(args[0], args[1]), "tags": ""},
            "read": {"args": 1, "func": lambda args: self.read(args[0]), "tags": ""},
            "erase": {"args": 2, "func": lambda args: self.erase(args[0], args[1]), "tags": ""},
            "erase_range": {"args": 2, "func": lambda args: self.erase_range(args[0], args[1]), "tags": ""},
            "fullwrite": {"args": 1, "func": lambda args: self.full_write(args[0]), "tags": ""},

            # scripts-tagged commands
            "1_": {"args": 0, "func": lambda: self.full_write_and_read_compare(), "tags": "scripts"},
            "1_FullWriteAndReadCompare": {"args": 0, "func": lambda: self.full_write_and_read_compare(),
                                          "tags": "scripts"},
            "2_": {"args": 0, "func": lambda: self.partial_lba_write(), "tags": "scripts"},
            "2_PartialLBAWrite": {"args": 0, "func": lambda: self.partial_lba_write(), "tags": "scripts"},
            "3_": {"args": 0, "func": lambda: self.write_read_aging(), "tags": "scripts"},
            "3_WriteReadAging": {"args": 0, "func": lambda: self.write_read_aging(), "tags": "scripts"},
            "4_": {"args": 0, "func": lambda: self.erase_write_aging(), "tags": "scripts"},
            "4_EraseAndWriteAging": {"args": 0, "func": lambda: self.erase_write_aging(), "tags": "scripts"},
        }
        self._is_runner = False

    def is_address_valid(self, address: str):
        try:
            address_int = int(address)
        except ValueError:
            return False  # 정수형으로 변환할 수 없는 경우 (예: "0.5")

        if 0 <= address_int <= 99:
            return True
        else:
            return False  # 유효한 범위(0~99)를 벗어난 경우

    def format_hex_value(self, value: str) -> str | None:
        if not value.startswith('0x'):  # str 시작이 0x로 시작되어야함
            return None

        # 값의 범위를 체크함
        hex_str = value[2:]

        try:
            int_value = int(hex_str, 16)
        except ValueError:
            return None

        if not (0 <= int_value <= 0xFFFFFFFF):
            return None

        return f'0x{int_value:08X}'

    def read(self, address: str):
        if not self.is_address_valid(address):
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
        formatted_value = self.format_hex_value(value)
        if formatted_value == None or not self.is_address_valid(address):
            return WRITE_ERROR

        ret = self._ssd_driver.run_ssd_write(address=address, value=formatted_value)
        return ret

    def full_write(self, value: str):
        formatted_value = self.format_hex_value(value)
        if formatted_value == None:
            return WRITE_ERROR

        for address in range(0, 100):
            if self._ssd_driver.run_ssd_write(address=str(address), value=formatted_value) == WRITE_ERROR:
                return WRITE_ERROR
        return WRITE_SUCCESS

    def erase(self, address: str, lba_size: str):
        if not self.is_address_valid(address) or not self.is_size_valid(lba_size):
            return ERASE_ERROR

        start_lba, size = self.range_resize(address, lba_size)
        status = self._erase_in_chunks(start_lba=start_lba, size=size)
        return status

    def erase_range(self, start_lba: str, end_lba: str):
        if not self.is_address_valid(start_lba) or not self.is_address_valid(end_lba):
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
        self.erase_range("0", "2")
        for x in range(2, 97, 2):
            self.write(str(x), "0x12345678")
            self.write(str(x), "0xaabbccdd")

            self.erase(str(x), "3")

            for i in range(3):
                if not self._read_and_compare(str(x + i), "0x00000000"):
                    return ERROR

    def erase_write_aging(self):
        for iter in range(30):
            ret = self.erase_write_test()
            if ret == ERROR:
                return ERROR
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
            if self.is_valid_command(command) == False:
                self.print_invalid_command()
                continue

            self.process_cmd(command)

    def run_runner(self, script_file: str = ""):
        self._is_runner = True
        if not os.path.exists(script_file):
            self.print_invalid_command()
            return

        with open(script_file, 'r') as f:
            commands = [line.strip() for line in f if line.strip()]

        if not commands:
            self.print_invalid_command()
            return

        for command in commands:
            if self.is_valid_command(command) == False:
                self.print_invalid_command()
                return
            if self.process_cmd(command) == False:
                return

    def is_valid_command(self, command):
        parts = shlex.split(command)
        if not parts:
            return False

        cmd_name, *cmd_args = parts
        spec = self.command_specs.get(cmd_name)
        if not spec:
            return False

        expected_arg_count = spec["args"]
        return len(cmd_args) == expected_arg_count

    def process_cmd(self, command):
        parts = shlex.split(command)
        if not parts:
            self.print_invalid_command()
            return

        cmd_name, *cmd_args = parts
        spec = self.command_specs.get(cmd_name)
        if not spec:
            self.print_invalid_command()
            return

        expected_arg_count = spec["args"]
        handler = spec["func"]
        tags = spec["tags"]
        if len(cmd_args) != expected_arg_count:
            self.print_invalid_command()
            return

        if self._is_runner:
            if tags != "scripts":
                self.print_invalid_command()
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
            self.print_invalid_command()

    def print_invalid_command(self):
        print("INVALID COMMAND")

    def is_size_valid(self, lba_size):
        try:
            lba_size = int(lba_size)
            return True
        except ValueError:
            return False  # 정수형으로 변환할 수 없는 경우 (예: "0.5")

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
