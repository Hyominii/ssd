import pytest
from pytest_mock import MockerFixture
from shell import *


@pytest.fixture
def shell_app(mocker):
    ssd_driver_mock = mocker.Mock(spec=SSDDriver)
    test_shell_app = TestShellApp(ssd_driver_mock)

    return test_shell_app


def test_shell_write_subprocess(shell_app):
    # Arrange
    shell_app._ssd_driver.run_ssd_write.return_value = WRITE_SUCCESS

    # Act
    ret = shell_app.write(address="0", value="0x00000000")

    # Assert
    assert ret == WRITE_SUCCESS
    shell_app._ssd_driver.run_ssd_write.assert_called_once()
    shell_app._ssd_driver.run_ssd_write.assert_called_once_with(address="0", value="0x00000000")


@pytest.mark.parametrize("wrong_address", ["-1", "100", "hello", "0.5", "-0.5", "123", ";"])
def test_shell_write_wrong_address(shell_app, wrong_address):
    # Arrange
    shell_app._ssd_driver.run_ssd_write.return_value = WRITE_SUCCESS

    # Act
    ret = shell_app.write(address=wrong_address, value="0x00000000")

    # Assert
    assert ret == WRITE_ERROR


@pytest.mark.parametrize("wrong_value", ["AA", "0xHELLO", "ox11", "0xaaaaaaaaaa", "-0xa", "1234", ";"])
def test_shell_write_wrong_value(shell_app, wrong_value):
    # Arrange
    shell_app._ssd_driver.run_ssd_write.return_value = WRITE_SUCCESS

    # Act
    ret = shell_app.write(address="0", value=wrong_value)

    # Assert
    assert ret == WRITE_ERROR


def test_shell_write_short_number(shell_app):
    # Arrange
    shell_app._ssd_driver.run_ssd_write.return_value = WRITE_SUCCESS

    # Act
    ret = shell_app.write(address="0", value="0xAA")

    # Assert
    assert ret == WRITE_SUCCESS


def test_shell_read(shell_app, capsys):
    # Arrange
    shell_app._ssd_driver.run_ssd_read.return_value = 0
    shell_app._ssd_driver.get_ssd_output.return_value = "0x00000000"

    # Act
    ret = shell_app.read(address="0")
    captured = capsys.readouterr()

    # Assert
    assert ret == READ_SUCCESS
    assert '[Read] LBA 00 : 0x00000000' in captured.out
    shell_app._ssd_driver.run_ssd_read.assert_called_once_with(address="0")


def test_shell_read_after_write(shell_app, capsys):
    # Arrange
    shell_app._ssd_driver.run_ssd_write.return_value = WRITE_SUCCESS
    shell_app._ssd_driver.run_ssd_read.return_value = READ_SUCCESS
    shell_app._ssd_driver.get_ssd_output.return_value = "0x00000000"

    # Act
    ret_write = shell_app.write(address="0", value="0x00000000")
    ret_read = shell_app.read(address="0")
    captured = capsys.readouterr()

    # Assert
    assert ret_write == WRITE_SUCCESS
    assert ret_read == READ_SUCCESS
    assert '[Read] LBA 00 : 0x00000000' in captured.out

    shell_app._ssd_driver.run_ssd_write.assert_called_once_with(address="0", value="0x00000000")
    shell_app._ssd_driver.run_ssd_read.assert_called_once_with(address="0")


def test_shell_read_after_read(shell_app, capsys):
    # Arrange & Act
    shell_app._ssd_driver.run_ssd_read.return_value = READ_SUCCESS
    shell_app._ssd_driver.get_ssd_output.return_value = "0x00000000"
    ret0 = shell_app.read(address="0")

    shell_app._ssd_driver.run_ssd_read.return_value = READ_SUCCESS
    shell_app._ssd_driver.get_ssd_output.return_value = "0x00000010"
    ret1 = shell_app.read(address="1")

    captured = capsys.readouterr()

    # Assert
    assert ret0 == READ_SUCCESS
    assert ret1 == READ_SUCCESS
    assert '[Read] LBA 00 : 0x00000000' in captured.out
    assert '[Read] LBA 01 : 0x00000010' in captured.out


def test_shell_cmd_exit_success(shell_app, mocker: MockerFixture):
    mocker.patch("builtins.input", side_effect=["exit"])
    mock_method = mocker.patch("shell.TestShellApp.exit")

    shell_app.run(1)

    mock_method.assert_called_once()


def test_shell_cmd_read_success(shell_app, mocker: MockerFixture):
    mocker.patch("builtins.input", side_effect=["read 1"])
    mock_method = mocker.patch("shell.TestShellApp.read")

    shell_app.run(1)

    mock_method.assert_called_once()


def test_shell_cmd_write_success(shell_app, mocker: MockerFixture):
    mocker.patch("builtins.input", side_effect=["write 0 0x00000001"])
    mock_method = mocker.patch("shell.TestShellApp.write")

    shell_app.run(1)

    mock_method.assert_called_once()


def test_shell_cmd_help_success(shell_app, mocker: MockerFixture):
    mocker.patch("builtins.input", side_effect=["help"])
    mock_method = mocker.patch("shell.TestShellApp.help")

    shell_app.run(1)

    mock_method.assert_called_once()


def test_shell_cmd_fullread_success(shell_app, mocker: MockerFixture):
    mocker.patch("builtins.input", side_effect=["fullread"])
    mock_method = mocker.patch("shell.TestShellApp.full_read")

    shell_app.run(1)

    mock_method.assert_called_once()


def test_shell_cmd_fullwrite_success(shell_app, mocker: MockerFixture):
    mocker.patch("builtins.input", side_effect=["fullwrite 0x00010000"])
    mock_method = mocker.patch("shell.TestShellApp.full_write")

    shell_app.run(1)

    mock_method.assert_called_once()


@pytest.mark.parametrize("input", ["exi", "rea", "wri", "hel"])
def test_shell_wrong_cmd(shell_app, mocker: MockerFixture, input, capsys):
    mocker.patch("builtins.input", side_effect=[input])

    shell_app.run(1)
    captured = capsys.readouterr()

    assert 'INVALID COMMAND' in captured.out


def test_shell_wrong_cmd_empty(shell_app, mocker: MockerFixture, capsys):
    mocker.patch("builtins.input", side_effect=[""])

    shell_app.run(1)
    captured = capsys.readouterr()

    assert 'INVALID COMMAND' in captured.out


@pytest.mark.parametrize("input", ["read 1 2", "write", "fullwrite", "exit 3"])
def test_shell_wrong_cmd_args(shell_app, mocker: MockerFixture, input, capsys):
    mocker.patch("builtins.input", side_effect=["read 1 2"])

    shell_app.run(1)
    captured = capsys.readouterr()

    assert 'INVALID COMMAND' in captured.out


def test_shell_subprocess_cmd():
    pass


# @pytest.mark.skip
def test_shell_exit(shell_app, mocker: MockerFixture):
    mocker.patch("builtins.input", side_effect=["exit"])
    exit_mock = mocker.patch("shell.TestShellApp.exit", side_effect=SystemExit(0))

    with pytest.raises(SystemExit) as e:
        shell_app.run(1)

    exit_mock.assert_called_once()
    assert e.value.code == 0


def test_shell_help(capsys):
    test_shell_app = TestShellApp()
    test_shell_app.help()

    captured = capsys.readouterr()
    output_lines = captured.out.strip().splitlines()

    expected_lines = [
        "팀명: BestReviewer",
        "팀장: 이장희 / 팀원: 김대용, 최도현, 박윤상, 최동희, 안효민, 김동훈",
        "사용 가능한 명령어:",
        "  write <LBA> <Value>      : 특정 LBA에 값 저장",
        "  read <LBA>               : 특정 LBA 값 읽기",
        "  fullwrite <Value>        : 전체 LBA에 동일 값 저장",
        "  fullread                 : 전체 LBA 읽기 및 출력",
        "  help                     : 도움말 출력",
        "  exit                     : 종료",
    ]

    for line in expected_lines:
        assert line in output_lines


def test_shell_full_read(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    shell_app._ssd_driver.run_ssd_read.side_effect = [0] * 100
    shell_app._ssd_driver.get_ssd_output.side_effect = ["0x00000000"] * 100

    # Act
    ret = shell_app.full_read()
    captured = capsys.readouterr()
    assert ret == READ_SUCCESS
    assert shell_app._ssd_driver.run_ssd_read.call_count == 100


def test_shell_full_write(shell_app, mocker: MockerFixture):
    # Arrange
    shell_app._ssd_driver.run_ssd_write.side_effect = [WRITE_SUCCESS] * 100

    # Act
    ret = shell_app.full_write(value="0x12345678")

    # Assert
    assert ret == WRITE_SUCCESS
    assert shell_app._ssd_driver.run_ssd_write.call_count == 100

def test_shell_full_write_wrong_format():
    pass

def test_shell_full_write_and_read_compare(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    shell_app._ssd_driver.run_ssd_write.side_effect = [WRITE_SUCCESS] * 100
    shell_app._ssd_driver.run_ssd_read.side_effect = [READ_SUCCESS] * 100
    shell_app._ssd_driver.get_ssd_output.return_value = "0x12345678"
    # Act
    shell_app.full_write_and_read_compare()

    # Assert
    assert "PASS" in capsys.readouterr().out

    assert shell_app._ssd_driver.run_ssd_write.call_count == 100
    assert shell_app._ssd_driver.run_ssd_read.call_count == 100

def test_shell_partial_lba_write(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    shell_app._ssd_driver.run_ssd_write.side_effect = [WRITE_SUCCESS] * 150
    shell_app._ssd_driver.run_ssd_read.side_effect = [READ_SUCCESS] * 150
    shell_app._ssd_driver.get_ssd_output.return_value = "0x12345678"

    # Act
    shell_app.partial_lba_write()

    # Assert
    assert "PASS" in capsys.readouterr().out

    assert shell_app._ssd_driver.run_ssd_write.call_count == 150
    assert shell_app._ssd_driver.run_ssd_read.call_count == 150

def test_shell_write_read_aging(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    shell_app._ssd_driver.run_ssd_write.side_effect = [WRITE_SUCCESS] * 400
    shell_app._ssd_driver.run_ssd_read.side_effect = [READ_SUCCESS] * 400
    shell_app._ssd_driver.get_ssd_output.return_value = "0x12345678"

    # Act
    shell_app.write_read_aging()

    # Assert
    assert "PASS" in capsys.readouterr().out

    assert shell_app._ssd_driver.run_ssd_write.call_count == 400
    assert shell_app._ssd_driver.run_ssd_read.call_count == 400