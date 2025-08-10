import pytest
from pytest_mock import MockerFixture
import os
import shutil

from shell import *

# # buffer 초기화
# @pytest.fixture(autouse=True)
# def clean_buffer():
#     buffer_path = os.path.join(ROOT_DIR, "buffer")
#     if os.path.exists(buffer_path):
#         shutil.rmtree(buffer_path)
#     os.makedirs(buffer_path, exist_ok=True)
#     yield


@pytest.fixture
def shell_app(mocker):
    ssd_driver = SSDDriver()
    test_shell_app = TestShellApp(ssd_driver)

    return test_shell_app

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("read", "00", "",           ["1_W_0_0x00000001"], "[Read] LBA 00 : 0x00000001"),
    ]
)
def test_buffer_fastread_1(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"{cmd} {arg1} {arg2}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert check_print in captured.out
    assert 'INVALID COMMAND' not in captured.out
    for buffer_file in buffer_files:
        full_buffer_file = os.path.join(f"{ROOT_DIR}/buffer", buffer_file)
        assert os.path.exists(full_buffer_file)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("read", "00", "",           ["1_empty"], "[Read] LBA 00 : 0x00000001"),
    ]
)
def test_buffer_fastread_2(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"{cmd} {arg1} {arg2}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert check_print in captured.out
    assert 'INVALID COMMAND' not in captured.out
    for buffer_file in buffer_files:
        full_buffer_file = os.path.join(f"{ROOT_DIR}/buffer", buffer_file)
        assert os.path.exists(full_buffer_file)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("erase", "00", "01", ["1_E_0_1"], "[Erase] Done"),
        ("read", "00", "",           ["1_E_0_1"], "[Read] LBA 00 : 0x00000000"),
    ]
)
def test_buffer_fastread_3(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"{cmd} {arg1} {arg2}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert check_print in captured.out
    assert 'INVALID COMMAND' not in captured.out
    for buffer_file in buffer_files:
        full_buffer_file = os.path.join(f"{ROOT_DIR}/buffer", buffer_file)
        assert os.path.exists(full_buffer_file)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("erase", "00", "01", ["1_E_0_1"], "[Erase] Done"),
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("read", "00", "",           ["2_empty"], "[Read] LBA 00 : 0x00000000"),
    ]
)
def test_buffer_fastread_4(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"{cmd} {arg1} {arg2}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert check_print in captured.out
    assert 'INVALID COMMAND' not in captured.out
    for buffer_file in buffer_files:
        full_buffer_file = os.path.join(f"{ROOT_DIR}/buffer", buffer_file)
        assert os.path.exists(full_buffer_file)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("erase", "00", "01", ["1_E_0_1"], "[Erase] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("read", "00", "",           ["1_W_0_0x00000001"], "[Read] LBA 00 : 0x00000001"),
    ]
)
def test_buffer_fastread_5(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"{cmd} {arg1} {arg2}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert check_print in captured.out
    assert 'INVALID COMMAND' not in captured.out
    for buffer_file in buffer_files:
        full_buffer_file = os.path.join(f"{ROOT_DIR}/buffer", buffer_file)
        assert os.path.exists(full_buffer_file)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("erase", "00", "01", ["1_E_0_1"], "[Erase] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("flush", "", "", ["2_empty"], "[Flush] Done"),
        ("read", "00", "",           ["1_empty"], "[Read] LBA 00 : 0x00000001"),
    ]
)
def test_buffer_fastread_6(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"{cmd} {arg1} {arg2}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert check_print in captured.out
    assert 'INVALID COMMAND' not in captured.out
    for buffer_file in buffer_files:
        full_buffer_file = os.path.join(f"{ROOT_DIR}/buffer", buffer_file)
        assert os.path.exists(full_buffer_file)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "00", "0x00000002", ["1_W_0_0x00000002"], "[Write] Done"),
        ("read", "00", "",           ["1_W_0_0x00000002"], "[Read] LBA 00 : 0x00000002"),
        # ("read", "00", "",           ["1_empty"], "[Read] LBA 00 : 0x00000002"),
    ]
)
def test_buffer_fastread_7(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"{cmd} {arg1} {arg2}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert check_print in captured.out
    assert 'INVALID COMMAND' not in captured.out
    for buffer_file in buffer_files:
        full_buffer_file = os.path.join(f"{ROOT_DIR}/buffer", buffer_file)
        assert os.path.exists(full_buffer_file)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "00", "0x00000002", ["1_W_0_0x00000002"], "[Write] Done"),
        ("flush", "", "", ["2_empty"], "[Flush] Done"),
        ("read", "00", "",           ["1_empty"], "[Read] LBA 00 : 0x00000002"),
    ]
)
def test_buffer_fastread_8(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"{cmd} {arg1} {arg2}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert check_print in captured.out
    assert 'INVALID COMMAND' not in captured.out
    for buffer_file in buffer_files:
        full_buffer_file = os.path.join(f"{ROOT_DIR}/buffer", buffer_file)
        assert os.path.exists(full_buffer_file)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "00", "0x00000002", ["1_W_0_0x00000002"], "[Write] Done"),
        ("write", "00", "0x00000003", ["1_W_0_0x00000003"], "[Write] Done"),
        ("write", "00", "0x00000004", ["1_W_0_0x00000004"], "[Write] Done"),
        ("write", "00", "0x00000005", ["1_W_0_0x00000005"], "[Write] Done"),
        ("read", "00", "",           ["1_empty"], "[Read] LBA 00 : 0x00000005"),
    ]
)
def test_buffer_fastread_9(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"{cmd} {arg1} {arg2}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert check_print in captured.out
    assert 'INVALID COMMAND' not in captured.out
    for buffer_file in buffer_files:
        full_buffer_file = os.path.join(f"{ROOT_DIR}/buffer", buffer_file)
        assert os.path.exists(full_buffer_file)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "00", "0x00000002", ["1_W_0_0x00000002"], "[Write] Done"),
        ("write", "00", "0x00000003", ["1_W_0_0x00000003"], "[Write] Done"),
        ("write", "00", "0x00000004", ["1_W_0_0x00000004"], "[Write] Done"),
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000005", ["1_W_0_0x00000005"], "[Write] Done"),
        ("read", "00", "",           ["1_empty"], "[Read] LBA 00 : 0x00000005"),
    ]
)
def test_buffer_fastread_10(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"{cmd} {arg1} {arg2}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert check_print in captured.out
    assert 'INVALID COMMAND' not in captured.out
    for buffer_file in buffer_files:
        full_buffer_file = os.path.join(f"{ROOT_DIR}/buffer", buffer_file)
        assert os.path.exists(full_buffer_file)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "01", "0x00000002", ["2_W_1_0x00000002"], "[Write] Done"),
        ("write", "02", "0x00000003", ["3_W_2_0x00000003"], "[Write] Done"),
        ("erase", "00", "01", ["3_E_0_1"], "[Erase] Done"),
        ("read", "00", "",           ["1_empty"], "[Read] LBA 00 : 0x00000000"),
        ("read", "01", "",           ["1_empty"], "[Read] LBA 01 : 0x00000002"),
        ("read", "02", "",           ["1_empty"], "[Read] LBA 02 : 0x00000003")
    ]
)
def test_buffer_fastread_11(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"{cmd} {arg1} {arg2}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert check_print in captured.out
    assert 'INVALID COMMAND' not in captured.out
    for buffer_file in buffer_files:
        full_buffer_file = os.path.join(f"{ROOT_DIR}/buffer", buffer_file)
        assert os.path.exists(full_buffer_file)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "01", "0x00000002", ["2_W_1_0x00000002"], "[Write] Done"),
        ("write", "02", "0x00000003", ["3_W_2_0x00000003"], "[Write] Done"),
        ("erase_range", "0", "1", ["2_E_0_2"], "[Erase_range] Done"),
        ("read", "00", "",           ["1_empty"], "[Read] LBA 00 : 0x00000000"),
        ("read", "01", "",           ["1_empty"], "[Read] LBA 01 : 0x00000000"),
        ("read", "02", "",           ["1_empty"], "[Read] LBA 02 : 0x00000003")
    ]
)
def test_buffer_fastread_12(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"{cmd} {arg1} {arg2}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert check_print in captured.out
    assert 'INVALID COMMAND' not in captured.out
    for buffer_file in buffer_files:
        full_buffer_file = os.path.join(f"{ROOT_DIR}/buffer", buffer_file)
        assert os.path.exists(full_buffer_file)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("write", "10", "0x00000001", ["1_W_10_0x00000001"], "[Write] Done"),
        ("erase", "11", "2", ["2_E_11_2"], "[Erase] Done"),
        ("write", "12", "0x00000001", ["3_W_12_0x00000001"], "[Write] Done"),
        ("erase", "13", "2", ["4_E_13_2"], "[Erase] Done"),
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("read", "10", "",           ["1_empty"], "[Read] LBA 10 : 0x00000001"),
    ]
)
def test_buffer_fastread_13(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"{cmd} {arg1} {arg2}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert check_print in captured.out
    assert 'INVALID COMMAND' not in captured.out
    for buffer_file in buffer_files:
        full_buffer_file = os.path.join(f"{ROOT_DIR}/buffer", buffer_file)
        assert os.path.exists(full_buffer_file)