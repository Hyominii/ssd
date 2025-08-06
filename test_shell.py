import shlex
import subprocess


class SSDDriver:
    def run_ssd_write(self, address: int, value: str):
        command = ['python', 'ssd.py', 'W', str(address), str(value)]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            return self.WRITE_SUCCESS
        else:
            return self.WRITE_ERROR


class TestShellApp:
    SUCCESS = 0
    WRITE_SUCCESS = SUCCESS
    WRITE_ERROR = -1

    def __init__(self, ssd_driver = None):
        if ssd_driver == None:
            ssd_driver = SSDDriver()

        self._ssd_driver = ssd_driver

    def read(self, address: int):
        pass

    def full_read(self):
        pass

    def write(self, address: int, value: str):
        ret = self._ssd_driver.run_ssd_write(address = address, value = value)
        return ret

    def full_write(self, value: str):
        for address in range(0, 100):
            if self._ssd_driver.run_ssd_write(address=address, value=value) == self.WRITE_ERROR:
                return self.WRITE_ERROR
        return self.WRITE_SUCCESS

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

    def run(self, max_iterations: int = None):
        print(f"안녕하세요, SSD 검증용 Test Shell App을 시작합니다.\n")

        while True:
            if max_iterations is not None:
                if max_iterations <= 0:
                    break
                max_iterations -= 1
            command = input("Shell > ").strip()
            if not command:
                self.print_invalid_command()
                continue
            parts = shlex.split(command)  # 공백을 기준으로 파싱하되 인용된 문자열도 처리
            cmd_name, *cmd_args = parts
            if self.is_validate_command(cmd_name, cmd_args):
                if cmd_name == "exit":
                    self.exit()
                elif cmd_name == "help":
                    self.help()
                elif cmd_name == "write":
                    self.write(cmd_args[0], cmd_args[1])
                elif cmd_name == "read":
                    self.read(cmd_args[0])
                elif cmd_name == "fullwrite":
                    self.full_write(cmd_args[0])
                elif cmd_name == "fullread":
                    self.full_read()
                else:
                    self.print_invalid_command()

    def is_validate_command(self, cmd_name, cmd_args):
        if cmd_name == "exit" or cmd_name == "help" or cmd_name == "fullread":
            if len(cmd_args) > 0:
                self.print_invalid_command()
                return False
        elif cmd_name == "write":
            if len(cmd_args) != 2:
                self.print_invalid_command()
                return False
        elif cmd_name == "read":
            if len(cmd_args) != 1:
                self.print_invalid_command()
                return False
        elif cmd_name == "fullwrite":
            if len(cmd_args) != 1:
                self.print_invalid_command()
                return False

        return True

    def print_invalid_command(self):
        print("INVALID COMMAND")


if __name__ == "__main__":
    app = TestShellApp()
    app.run()
    app.help()
