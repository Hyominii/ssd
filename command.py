from abc import ABC, abstractmethod

MAX_COMMANDS = 5
# 추상 Command 클래스
class Command(ABC):
    @abstractmethod
    def execute(self):
        pass
    # 구체적인 Command들


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
