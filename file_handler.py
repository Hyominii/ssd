from abc import ABC, abstractmethod
import os


class FileHandler(ABC):
    @abstractmethod
    def write(self, data: str):
        pass

    @abstractmethod
    def read(self) -> str:
        pass


class SimpleFileHandler(FileHandler):
    def __init__(self, filename: str):
        self._filename = filename
        if not os.path.exists(filename):
            with open(self._filename, 'w', encoding='utf-8') as f:
                f.write("")

    def write(self, data: str):
        with open(self._filename, 'w', encoding='utf-8') as f:
            f.write(data)

    def read(self) -> str:
        with open(self._filename, 'r', encoding='utf-8') as f:
            line = f.readline().strip()
            return line


class FileDecorator(FileHandler):
    def __init__(self, handler: FileHandler):
        self._wrapped_handler = handler

    def write(self, data: str):
        self._wrapped_handler.write(data)

    def read(self) -> str:
        return self._wrapped_handler.read()


class MultilineFileWriter(FileDecorator):
    def write_lines(self, lines: list):
        lines_with_newlines = [str(line) + '\n' for line in lines]
        with open(self._wrapped_handler._filename, 'w', encoding='utf-8') as f:
            f.writelines(lines_with_newlines)

    def read_all_lines(self) -> list:
        with open(self._wrapped_handler._filename, 'r', encoding='utf-8') as f:
            lines = f.read().split("\n")
            return lines

    def read_specific_line(self, line_number: int) -> str:
        return self.read_all_lines()[line_number].strip()