import tempfile
import pytest
from pytest_mock import MockerFixture
from shell import *

@pytest.fixture
def shell_app(mocker):
    ssd_driver = SSDDriver()
    test_shell_app = TestShellApp(ssd_driver)

    return test_shell_app

@pytest.mark.parametrize("valid_address", [str(x) for x in range(100)])
def test_shell_write_test_valid_address(shell_app, valid_address, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"write {valid_address} 0x00000001"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Write] Done' in captured.out
    assert 'INVALID COMMAND' not in captured.out

@pytest.mark.parametrize("valid_value", ["0xa", "0xab", "0xabc", "0xabcd", "0xabcde", "0xabcdef", "0xabcdeff", "0x00000000000000000001"])
def test_shell_write_valid_value(shell_app, valid_value, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"write 00 {valid_value}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Write] Done' in captured.out
    assert 'INVALID COMMAND' not in captured.out

@pytest.mark.parametrize("wrong_address", ["-1", "100", "hello", "0.5", "-0.5", "123", ";", " ", "0x00"])
def test_shell_write_wrong_address(shell_app, wrong_address, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"write {wrong_address} 0x12345678"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Write] Done' not in captured.out
    assert 'INVALID COMMAND' in captured.out

@pytest.mark.parametrize("wrong_value", ["AA", "0xHELLO", "ox11", "0xaaaaaaaaaa", "-0xa", "1234", ";", " ", "0xA00000000000000001"])
def test_shell_write_wrong_value(shell_app, wrong_value, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"write 00 {wrong_value}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Write] Done' not in captured.out
    assert 'INVALID COMMAND' in captured.out

@pytest.mark.parametrize("valid_address", [str(x) for x in range(100)])
def test_shell_read_test_valid_address(shell_app, valid_address, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"write {valid_address} 0x00000001", f"read {valid_address}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Write] Done' in captured.out
    assert f'[Read] LBA {int(valid_address):02} : 0x00000001' in captured.out
    assert 'INVALID COMMAND' not in captured.out

@pytest.mark.parametrize("wrong_address", ["-1", "100", "hello", "0.5", "-0.5", "123", ";", " ", "0x00"])
def test_shell_read_wrong_address(shell_app, wrong_address, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"write {wrong_address} 0x12345678", f"read {wrong_address}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Write] Done' not in captured.out
    assert 'INVALID COMMAND' in captured.out


@pytest.mark.parametrize("valid_address", [str(x) for x in range(100)])
def test_shell_erase_with_valid_address(shell_app, valid_address, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"erase {valid_address} 1"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Erase] Done' in captured.out
    assert 'INVALID COMMAND' not in captured.out

@pytest.mark.parametrize("wrong_address", ["-1", "100", "hello", "0.5", "-0.5", "123", ";", " ", "0x00"])
def test_shell_erase_with_wrong_address(shell_app, wrong_address, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"erase {wrong_address} 1"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Erase] Done' not in captured.out
    assert 'INVALID COMMAND' in captured.out

@pytest.mark.parametrize("invalid_size", ["0.5", "-1.5", "0xa", "-0x1", "0xF", "-", " ", "null", "A"])
def test_shell_erase_with_invalid_size(shell_app, invalid_size, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"erase 00 {invalid_size}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Erase] Done' not in captured.out
    assert 'INVALID COMMAND' in captured.out

@pytest.mark.parametrize("valid_range", [("0", "0"), ("99", "99"), ("0", "99"), ("99", "0")])
def test_shell_erase_range_with_valid_range(shell_app, valid_range, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"erase_range {valid_range[0]} {valid_range[1]}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Erase_range] Done' in captured.out
    assert 'INVALID COMMAND' not in captured.out

@pytest.mark.parametrize("invalid_range", [("-1", "10"), ("1", "100"), ("1.5", "10"), ("10", "10.5")
                                           , ("a", "10.5"), ("10", ".5")])
def test_shell_erase_range_invalid_range(shell_app, invalid_range, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"erase_range {invalid_range[0]} {invalid_range[1]}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Erase_range] Done' not in captured.out
    assert 'INVALID COMMAND' in captured.out