class Formatter:
    def __init__(self, fmt=None):
        pass


class BaseHandler:
    def emit(self, formatted_message):
        raise NotImplementedError


class StreamHandler(BaseHandler):
    def __init__(self):
        pass

    def emit(self, formatted_message):
        pass


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

    def _log(self, level, message):
        pass

    def info(self, message):
        self._log("INFO", message)

    def warn(self, message):
        self._log("WARN", message)

    def error(self, message):
        self._log("ERROR", message)

    def debug(self, message):
        self._log("DEBUG", message)

    def print(self, class_method_name: str, message: str):
        pass
