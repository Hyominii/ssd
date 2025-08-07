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
    log_path = tmp_path / "latest.log"

    handler = FileHandler(dirname=tmp_path, filename="latest.log")  # 1KB 용량 제한
    logger.add_handler(handler)
    logger.print(CLASS_METHOD_NAME, MESSAGE)

    content = log_path.read_text()
    assert log_path.exists()
    assert "class.method(): Hi" in content


def test_log_rotate(tmp_path, logger):
    log_path = tmp_path / "latest.log"

    handler = FileHandler(dirname=tmp_path, filename="latest.log", max_bytes=100)

    for _ in range(10):
        handler.emit("A" * 20)
    rotated_logs = list(log_path.parent.glob("until*.log"))

    assert len(rotated_logs) == 1
    assert rotated_logs[0].is_file()


def test_log_zip_after_second_rotate(tmp_path, logger):
    log_path = tmp_path / "latest.log"
    handler = FileHandler(dirname=tmp_path, filename="latest.log", max_bytes=100)

    # First rotate
    for _ in range(10):
        handler.emit("A" * 20)

    rotated_log = list(log_path.parent.glob("until*.log"))[0]
    assert rotated_log.exists()

    import time
    time.sleep(1)

    # Second rotate
    for _ in range(10):
        handler.emit("B" * 10)

    zip_files = list(log_path.parent.glob("until*.zip"))
    assert len(zip_files) > 0
    assert zip_files[0].is_file()
    assert not rotated_log.exists()

