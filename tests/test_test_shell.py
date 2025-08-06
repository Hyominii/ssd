import pytest
from pytest_mock import MockerFixture
from test_shell import TestShellApp, SSDDriver


@pytest.fixture
def shell_app(mocker):
    ssd_driver_mock = mocker.Mock(spec=SSDDriver)
    test_shell_app = TestShellApp(ssd_driver_mock)

    return test_shell_app


def test_shell_write(mocker):
    # Arrange
    ssd_driver_mock = mocker.Mock(spec=SSDDriver)
    test_shell_app = TestShellApp(ssd_driver_mock)

    test_shell_app._ssd_driver.run_ssd_write.return_value = TestShellApp.WRITE_SUCCESS

    # Act
    ret = test_shell_app.write(address=0, value=0)

    # Assert
    assert ret == TestShellApp.WRITE_SUCCESS
    test_shell_app._ssd_driver.run_ssd_write.assert_called_once()


def test_shell_write_subprocess(mocker):
    # Arrange
    ssd_driver_mock = mocker.Mock(spec=SSDDriver)
    test_shell_app = TestShellApp(ssd_driver_mock)

    test_shell_app._ssd_driver.run_ssd_write.return_value = TestShellApp.WRITE_SUCCESS

    # Act
    ret = test_shell_app.write(address=0, value=0)

    # Assert
    assert ret == TestShellApp.WRITE_SUCCESS
    test_shell_app._ssd_driver.run_ssd_write.assert_called_once_with(address=0, value=0)


def test_shell_write_wrong_address():
    pass


def test_shell_write_wrong_data_format():
    pass


def test_shell_write_short_number():
    pass


def test_shell_read():
    pass


def test_shell_read_wrong_address():
    pass


def test_shell_read_output_file():
    pass


def test_shell_read_after_write():
    pass


def test_shell_read_after_read():
    pass


def test_shell_cmd_exit_success(shell_app, mocker: MockerFixture):
    mocker.patch("builtins.input", side_effect=["exit"])
    mock_method = mocker.patch("test_shell.TestShellApp.exit")

    shell_app.run(1)

    mock_method.assert_called_once()


def test_shell_cmd_read_success(shell_app, mocker: MockerFixture):
    mocker.patch("builtins.input", side_effect=["read 1"])
    mock_method = mocker.patch("test_shell.TestShellApp.read")

    shell_app.run(1)

    mock_method.assert_called_once()


def test_shell_cmd_write_success(shell_app, mocker: MockerFixture):
    mocker.patch("builtins.input", side_effect=["write 0 0x00000001"])
    mock_method = mocker.patch("test_shell.TestShellApp.write")

    shell_app.run(1)

    mock_method.assert_called_once()


def test_shell_cmd_help_success(shell_app, mocker: MockerFixture):
    mocker.patch("builtins.input", side_effect=["help"])
    mock_method = mocker.patch("test_shell.TestShellApp.help")

    shell_app.run(1)

    mock_method.assert_called_once()


def test_shell_cmd_fullread_success(shell_app, mocker: MockerFixture):
    mocker.patch("builtins.input", side_effect=["fullread"])
    mock_method = mocker.patch("test_shell.TestShellApp.full_read")

    shell_app.run(1)

    mock_method.assert_called_once()


def test_shell_cmd_fullwrite_success(shell_app, mocker: MockerFixture):
    mocker.patch("builtins.input", side_effect=["fullwrite 0x00010000"])
    mock_method = mocker.patch("test_shell.TestShellApp.full_write")

    shell_app.run(1)

    mock_method.assert_called_once()


@pytest.mark.parametrize("input", ["exi", "rea", "wri", "hel"])
def test_shell_wrong_cmd(shell_app, mocker: MockerFixture, input, capsys):
    mocker.patch("builtins.input", side_effect=[input])

    shell_app.run(1)
    captured = capsys.readouterr()

    assert 'INVALID COMMAND' in captured.out


# @pytest.mark.skip
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
    exit_mock = mocker.patch("test_shell.TestShellApp.exit", side_effect=SystemExit(0))

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


def test_shell_full_read():
    pass


def test_shell_full_write(shell_app, mocker: MockerFixture):
    # Arrange
    ssd_driver_mock = mocker.Mock(spec=SSDDriver)
    test_shell_app = TestShellApp(ssd_driver_mock)

    test_shell_app._ssd_driver.run_ssd_write.side_effect = [TestShellApp.WRITE_SUCCESS] * 100

    # Act
    ret = test_shell_app.full_write(value=0)

    # Assert
    assert ret == TestShellApp.WRITE_SUCCESS

    assert test_shell_app._ssd_driver.run_ssd_write.call_count == 100


def test_shell_full_write_wrong_format():
    pass
