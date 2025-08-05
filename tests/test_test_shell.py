import pytest
from pytest_mock import MockerFixture
from test_shell import TestShellApp


@pytest.fixture
def shell_app():
    test_shell_app = TestShellApp()
    return test_shell_app


@pytest.mark.skip
def test_shell_write():
    pass


@pytest.mark.skip
def test_shell_write_subprocess():
    pass


@pytest.mark.skip
def test_shell_write_wrong_address():
    pass


@pytest.mark.skip
def test_shell_write_wrong_data_format():
    pass


@pytest.mark.skip
def test_shell_write_short_number():
    pass


@pytest.mark.skip
def test_shell_read():
    pass


@pytest.mark.skip
def test_shell_read_wrong_address():
    pass


@pytest.mark.skip
def test_shell_read_output_file():
    pass


@pytest.mark.skip
def test_shell_read_after_write():
    pass


@pytest.mark.skip
def test_shell_read_after_read():
    pass


@pytest.mark.parametrize("input", ["exi", "rea", "wri", "hel"])
def test_shell_wrong_cmd(shell_app, mocker: MockerFixture, input, capsys):
    mocker.patch("builtins.input", side_effect=[input])

    shell_app.run(1)
    captured = capsys.readouterr()

    assert 'INVALID COMMAND' in captured.out


@pytest.mark.skip
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


@pytest.mark.skip
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


@pytest.mark.skip
def test_shell_help(shell_app, mocker: MockerFixture, capsys):
    mocker.patch("builtins.input", side_effect=["help"])

    shell_app.run()
    captured = capsys.readouterr()

    assert "종료합니다." in captured.out


@pytest.mark.skip
def test_shell_full_read():
    pass


@pytest.mark.skip
def test_shell_full_write():
    pass


@pytest.mark.skip
def test_shell_full_write_wrong_format():
    pass
