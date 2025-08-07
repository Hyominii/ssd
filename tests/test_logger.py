import sys

import pytest
from logger import Logger, StreamHandler, FileHandler

CLASS_METHOD_NAME = "class.method()"
MESSAGE = "Hi"


@pytest.fixture
def logger():
    logger = Logger()
    logger.clear()  # clear handlers

    return logger


def test_logger_print_success(logger, capsys):
    logger.add_handler(StreamHandler(sys.stdout))
    logger.print(CLASS_METHOD_NAME, MESSAGE)

    captured = capsys.readouterr()
    print(f"captured.out: {captured.out}")

    assert f"{CLASS_METHOD_NAME}: {MESSAGE}" in captured.out


def test_logger_info_success(logger, capsys):
    logger.add_handler(StreamHandler(sys.stdout))
    logger.info(CLASS_METHOD_NAME, MESSAGE)

    captured = capsys.readouterr()
    print(f"captured.out: {captured.out}")

    assert f"INFO {CLASS_METHOD_NAME}: {MESSAGE}" in captured.out


def test_logger_warn_success(logger, capsys):
    logger.add_handler(StreamHandler(sys.stdout))
    logger.warn(CLASS_METHOD_NAME, MESSAGE)

    captured = capsys.readouterr()
    print(f"captured.out: {captured.out}")

    assert f"WARN {CLASS_METHOD_NAME}: {MESSAGE}" in captured.out


def test_logger_error_success(logger, capsys):
    logger.add_handler(StreamHandler(sys.stdout))
    logger.error(CLASS_METHOD_NAME, MESSAGE)

    captured = capsys.readouterr()
    print(f"captured.out: {captured.out}")

    assert f"ERROR {CLASS_METHOD_NAME}: {MESSAGE}" in captured.out


def test_logger_debug_success(logger, capsys):
    logger.add_handler(StreamHandler(sys.stdout))
    logger.debug(CLASS_METHOD_NAME, MESSAGE)

    captured = capsys.readouterr()
    print(f"captured.out: {captured.out}")

    assert f"DEBUG {CLASS_METHOD_NAME}: {MESSAGE}" in captured.out


def test_file_handler_writes_to_file(tmp_path, logger):
    log_path = tmp_path / "test.log"

    handler = FileHandler(dirname=tmp_path, filename="test.log")  # 1KB 용량 제한
    logger.add_handler(handler)
    logger.print(CLASS_METHOD_NAME, MESSAGE)

    content = log_path.read_text()
    assert log_path.exists()
    assert "class.method(): Hi" in content
