import shlex
import subprocess

from matplotlib.dates import TUESDAY

SUCCESS = 0
ERROR = -1
WRITE_SUCCESS = SUCCESS
WRITE_ERROR = ERROR
READ_SUCCESS = SUCCESS
READ_ERROR = ERROR


class SSDDriver:
    def run_ssd_write(self, address: str, value: str):
        command = ['python', 'ssd.py', 'W', str(address), str(value)]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            return WRITE_SUCCESS
        else:
            return WRITE_ERROR

    def run_ssd_read(self, address: str):
        command = ['python', 'ssd.py', 'R', str(address)]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            return READ_SUCCESS
        else:
            return READ_ERROR

    def get_ssd_output(self, file_path: str = "ssd_output.txt"):
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
            "exit": (0, lambda: self.exit()),
            "help": (0, lambda: self.help()),
            "fullread": (0, lambda: self.full_read()),
            "write": (2, lambda args: self.write(args[0], args[1])),
            "read": (1, lambda args: self.read(args[0])),
            "fullwrite": (1, lambda args: self.full_write(args[0])),
        }

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
                    print("FAIL")
                    raise SystemExit(1)
        print("PASS")

    def partial_lba_write(self):
        for iter in range(30):
            self.write("4", "0x12345678")
            self.write("0", "0x12345678")
            self.write("3", "0x12345678")
            self.write("1", "0x12345678")
            self.write("2", "0x12345678")
            for address in range(0, 5):
                if self._read_and_compare(str(address), "0x12345678") == False:
                    print("FAIL")
                    raise SystemExit(1)
        print("PASS")

    def write_read_aging(self):
        for iter in range(200):
            self.write("0", "0x12345678")
            self.write("99", "0x12345678")

            if self._read_and_compare("0", "0x12345678") == False:
                print("FAIL")
                raise SystemExit(1)
            if self._read_and_compare("99", "0x12345678") == False:
                print("FAIL")
                raise SystemExit(1)
        print("PASS")

    def exit(self):
        raise SystemExit(0)

    def help(self):
        print("팀명: BestReviewer")
        print("팀장: 이장희 / 팀원: 김대용, 최도현, 박윤상, 최동희, 안효민, 김동훈")
        print("사용 가능한 명령어:")
        print("  write <LBA> <Value>      : 특정 LBA에 값 저장")
        print("  read <LBA>               : 특정 LBA 값 읽기")
        print("  fullwrite <Value>        : 전체 LBA에 동일 값 저장")
        print("  fullread                 : 전체 LBA 읽기 및 출력")
        print("  help                     : 도움말 출력")
        print("  exit                     : 종료")
        return SUCCESS

    def run(self, max_iterations: int = None):
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

    def is_valid_command(self, command):
        parts = shlex.split(command)
        if not parts:
            return False

        cmd_name, *cmd_args = parts
        spec = self.command_specs.get(cmd_name)
        if not spec:
            return False

        expected_arg_count, _ = spec
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

        expected_arg_count, handler = spec
        if len(cmd_args) != expected_arg_count:
            self.print_invalid_command()
            return

        try:
            if cmd_name == "write":
                ret = handler(cmd_args)
                if ret == SUCCESS:
                    print("[Write] Done")
            else:
                ret = handler(cmd_args) if expected_arg_count else handler()
        except Exception:
            ret = ERROR

        if ret != SUCCESS:
            self.print_invalid_command()

    def print_invalid_command(self):
        print("INVALID COMMAND")


if __name__ == "__main__":
    app = TestShellApp()
    app.run()
    app.help()
