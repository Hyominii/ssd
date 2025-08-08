"""
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

        if os.path.isdir(BUFFER_DIR):
            self.init_command_buffer()
            return

        for filename in os.listdir(BUFFER_DIR):
            #file_path = os.path.join(BUFFER_DIR, filename)
            cmd_arg = filename.split('_')

            if cmd_arg[1] == "W":
                self.
                self.add_command(WriteCommand(ssd, int(arg1), arg2, invoker.num_commands() + 1))
            elif cmd_arg[1] == "E":
                self.add_command(EraseCommand(ssd, int(arg1), int(arg2), invoker.num_commands() + 1))
            elif cmd_arg[1] == "F":
                invoker.flush()
            else:
                print(f"Unknown command: {cmd}")
                sys.exit(1)


    def add_command(self, cmd: Command):
        if len(self._commands) >= MAX_COMMANDS:
            self.flush()
        self._commands.append(cmd)

    def flush(self):
        for cmd in self._commands:
            cmd.execute()
        self._commands.clear()
        self.init_command_buffer()

    def num_commands(self):
        return len(self._commands)

    def init_command_buffer(self):
        buffer_dir = BUFFER_DIR
        os.makedirs(buffer_dir, exist_ok=True)  # 이미 있어도 에러 안 나게

        # 2. 파일 생성
        for i in range(1, 6):
            # 해당 i로 시작하는 파일이 이미 존재하는지 확인
            exists = any(
                filename.startswith(f"{i}_")
                for filename in os.listdir(buffer_dir)
            )

            if not exists:
                file_path = os.path.join(buffer_dir, f"{i}_empty")
                with open(file_path, "w") as f:
                    f.write("")
"""