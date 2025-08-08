import os
import zipfile
import sys

from datetime import datetime
from typing import Optional
from utils import find_files_by_pattern

DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FILE_NAME = "latest.log"
DEFAULT_MAX_BYTES = 10 * 1024
DEFAULT_LOG_TIMESTAMP_FORMAT = "%y.%m.%d %H:%M"
DEFAULT_LOG_FORMAT = "[{time}]{level} {class_method_name}: {message}"
DEFAULT_ROTATE_LOG_TIMESTAMP_FORMAT = "%y%m%d_%Hh_%Mm_%Ss"

INFO = "INFO"
WARN = "WARN"
ERROR = "ERROR"
DEBUG = "DEBUG"


class Formatter:
    def __init__(self, fmt=None):
        self.fmt = fmt or DEFAULT_LOG_FORMAT

    def format(self, class_method_name, message, level: Optional[str] = None):
        now = datetime.now().strftime(DEFAULT_LOG_TIMESTAMP_FORMAT)
        if not level:
            level = ""
        return self.fmt.format(time=now, class_method_name=class_method_name, message=message, level=level)


class BaseHandler:
    def emit(self, formatted_message):
        raise NotImplementedError


class StreamHandler(BaseHandler):
    def __init__(self, stream=sys.stdout):
        self.stream = stream

    def emit(self, formatted_message):
        self.stream.write(formatted_message + "\n")
        self.stream.flush()


class FileHandler(BaseHandler):
    def __init__(self, dirname=DEFAULT_LOG_DIR, filename: str = DEFAULT_LOG_FILE_NAME, max_bytes=DEFAULT_MAX_BYTES,
                 compress=True):
        self.dirname = dirname
        self.filename = filename
        self.log_path = f"{dirname}/{filename}"
        self.max_bytes = max_bytes
        self.compress = compress
        self._open_file()

    def _open_file(self):
        os.makedirs(self.dirname, exist_ok=True)
        self.file = open(self.log_path, "a", encoding="utf-8")

    def _rotate(self):
        self.file.close()

        self._compress_existing_rotate_log()

        timestamp = datetime.now().strftime(DEFAULT_ROTATE_LOG_TIMESTAMP_FORMAT)
        rotate_file_path = f"{self.dirname}/until_{timestamp}.log"
        os.rename(self.log_path, rotate_file_path)

        self._open_file()

    def _compress_existing_rotate_log(self):
        rotate_log_files = find_files_by_pattern(self.dirname, "until*log")
        if len(rotate_log_files) < 1:
            return

        for log_file in rotate_log_files:
            zip_path = log_file.with_name(f"{log_file.stem}.zip")

            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(log_file, arcname=log_file.name)

            os.remove(log_file)

    def _should_rotate(self):
        self.file.flush()
        self.file.seek(0, os.SEEK_END)
        return self.file.tell() >= self.max_bytes

    def emit(self, formatted_message):
        if self._should_rotate():
            self._rotate()
        self.file.write(formatted_message + "\n")
        self.file.flush()


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance


class Logger(Singleton):
    _instance = None

    def __init__(self):
        if self._initialized:
            return
        self.handlers = [FileHandler()]
        self.formatter = Formatter()
        self._initialized = True

    def set_formatter(self, formatter: Formatter):
        self.formatter = formatter

    def add_handler(self, handler: BaseHandler):
        self.handlers.append(handler)

    def _log(self, class_method_name, message, level: Optional[str] = None):
        formatted = self.formatter.format(class_method_name, message, level)
        for handler in self.handlers:
            handler.emit(formatted)

    def info(self, class_method_name: str, message: str):
        self._log(class_method_name, message, INFO)

    def warn(self, class_method_name: str, message: str):
        self._log(class_method_name, message, WARN)

    def error(self, class_method_name: str, message: str):
        self._log(class_method_name, message, ERROR)

    def debug(self, class_method_name: str, message: str):
        self._log(class_method_name, message, DEBUG)

    def print(self, class_method_name: str, message: str):
        self._log(class_method_name=class_method_name, message=message)

    def clear(self):
        self.handlers.clear()
