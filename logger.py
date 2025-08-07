import sys

from datetime import datetime
from typing import Optional


class Formatter:
    def __init__(self, fmt=None):
        self.fmt = fmt or "[{time}]{level} {class_method_name}: {message}"

    def format(self, class_method_name, message, level: Optional[str] = None):
        now = datetime.now().strftime("%y.%m.%d %H:%M")
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
    def __init__(self):
        pass

    def emit(self, formatted_message):
        pass


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
        self.handlers = [StreamHandler()]
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
        self._log(class_method_name, message, "INFO")

    def warn(self, class_method_name: str, message: str):
        self._log(class_method_name, message, "WARN")

    def error(self, class_method_name: str, message: str):
        self._log(class_method_name, message, "ERROR")

    def debug(self, class_method_name: str, message: str):
        self._log(class_method_name, message, "DEBUG")

    def print(self, class_method_name: str, message: str):
        self._log(class_method_name=class_method_name, message=message)

    def clear(self):
        self.handlers.clear()
