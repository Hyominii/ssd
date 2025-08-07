import sys

import pytest
from logger import Logger, StreamHandler


@pytest.fixture
def logger():
    logger = Logger()
    logger.clear() # clear handlers

    return logger


def test_logger_print_success(logger, capsys):
    class_method_name = "class.method()"
    message = "Hi"
    logger.add_handler(StreamHandler(sys.stdout))
    logger.print(class_method_name, message)

    captured = capsys.readouterr()
    print(f"captured.out: {captured.out}")

    assert f"{class_method_name}: {message}" in captured.out


def test_logger_info_success(logger, capsys):
    class_method_name = "class.method()"
    message = "Hi"
    logger.add_handler(StreamHandler(sys.stdout))
    logger.info(class_method_name, message)

    captured = capsys.readouterr()
    print(f"captured.out: {captured.out}")

    assert f"INFO {class_method_name}: {message}" in captured.out


def test_logger_warn_success(logger, capsys):
    class_method_name = "class.method()"
    message = "Hi"
    logger.add_handler(StreamHandler(sys.stdout))
    logger.warn(class_method_name, message)

    captured = capsys.readouterr()
    print(f"captured.out: {captured.out}")

    assert f"WARN {class_method_name}: {message}" in captured.out


def test_logger_error_success(logger, capsys):
    class_method_name = "class.method()"
    message = "Hi"
    logger.add_handler(StreamHandler(sys.stdout))
    logger.error(class_method_name, message)

    captured = capsys.readouterr()
    print(f"captured.out: {captured.out}")

    assert f"ERROR {class_method_name}: {message}" in captured.out


def test_logger_debug_success(logger, capsys):
    class_method_name = "class.method()"
    message = "Hi"
    logger.add_handler(StreamHandler(sys.stdout))
    logger.debug(class_method_name, message)

    captured = capsys.readouterr()
    print(f"captured.out: {captured.out}")

    assert f"DEBUG {class_method_name}: {message}" in captured.out
