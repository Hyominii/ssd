import subprocess
import os
from logger import Logger
from utils import get_class_and_method_name

logger = Logger()

ROOT_DIR = os.path.dirname(__file__)
SUCCESS = 0
ERROR = -1


class SSDDriver:
    def run_cmd_to_ssd(self, command):
        result = subprocess.run(command, cwd=ROOT_DIR, capture_output=True, text=True)
        if result.returncode == 0:
            return SUCCESS
        else:
            logger.print(get_class_and_method_name(), f"subprocess returned {result.returncode}")
            return ERROR

    def run_ssd_write(self, address: str, value: str):
        command = ['python', 'ssd.py', 'W', str(address), str(value)]
        return self.run_cmd_to_ssd(command)

    def run_ssd_erase(self, address: str, lba_size: str):
        command = ['python', 'ssd.py', 'E', str(address), str(lba_size)]
        return self.run_cmd_to_ssd(command)

    def run_ssd_read(self, address: str):
        command = ['python', 'ssd.py', 'R', str(address)]
        return self.run_cmd_to_ssd(command)

    def run_ssd_flush(self):
        command = ['python', 'ssd.py', 'F']
        return self.run_cmd_to_ssd(command)

    def get_ssd_output(self, file_path: str = ROOT_DIR + "/ssd_output.txt"):
        with open(file_path, 'r', encoding='utf-8') as f:
            line = f.readline().rstrip("\n")

        if len(line) != 10:
            raise ValueError(f"Error, value Length: {len(line)})")
        return line
