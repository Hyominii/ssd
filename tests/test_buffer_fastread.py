import pytest
from pytest_mock import MockerFixture
from shell import *

@pytest.fixture
def shell_app(mocker):
    ssd_driver = SSDDriver()
    test_shell_app = TestShellApp(ssd_driver)

    return test_shell_app

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "01", "0x00000001", ["2_W_1_0x00000001"], "[Write] Done"),
        ("read", "00", "",           ["1_empty", "2_empty"], "[Read] LBA 00 : 0x00000001"),
    ]
)
def test_buffer_fastread_with_write(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
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
