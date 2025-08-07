import os
from abc import ABC, abstractmethod

BUFFER_DIR = 'buffer'

MAX_COMMANDS = 5
# 추상 Command 클래스
class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    def set_path(self, file_path: str):
        self.path = file_path

    def rename_buffer(self, buffer_num, cmd, address, size):
        path = f'{buffer_num}_{cmd}_{address}_{size}'
        self.set_path(path)
        for filename in os.listdir(BUFFER_DIR):
            if filename.startswith(f'{buffer_num}'):
                old_path = os.path.join(BUFFER_DIR, filename)
                new_path = os.path.join(BUFFER_DIR, path)
                os.rename(old_path, new_path)
                # print(f"Renamed {filename} -> {}2_string")
                break  # ✅ 하나만 처리하고 끝냄



class CommandInvoker:
    def __init__(self):
        self._commands = []

    def add_command(self, cmd: Command):
        if len(self._commands) >= MAX_COMMANDS:
            self.flush()
        self._commands.append(cmd)

    def flush(self):
        for cmd in self._commands:
            cmd.execute()
        self._commands.clear()

    def num_commands(self):
        return len(self._commands)
