import pytest
from pytest_mock import MockerFixture
from shell import *

@pytest.fixture
def shell_app(mocker):
    ssd_driver = SSDDriver()
    test_shell_app = TestShellApp(ssd_driver)

    return test_shell_app

def fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app, invalid_command=False):
    # Arrange
    cmd = [f"{cmd} {arg1} {arg2}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)
    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()
    # Assert
    assert check_print in captured.out
    if not invalid_command:
        assert 'INVALID COMMAND' not in captured.out
    for buffer_file in buffer_files:
        full_buffer_file = os.path.join(f"{ROOT_DIR}/buffer", buffer_file)
        assert os.path.exists(full_buffer_file)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("read", "00", "",           ["1_W_0_0x00000001"], "[Read] LBA 00 : 0x00000001"),
    ]
)
def test_buffer_fastread_1(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("read", "00", "",           ["1_empty"], "[Read] LBA 00 : 0x00000001"),
    ]
)
def test_buffer_fastread_2(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("erase", "00", "01", ["1_E_0_1"], "[Erase] Done"),
        ("read", "00", "",           ["1_E_0_1"], "[Read] LBA 00 : 0x00000000"),
    ]
)
def test_buffer_fastread_3(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("erase", "00", "01", ["1_E_0_1"], "[Erase] Done"),
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("read", "00", "",           ["2_empty"], "[Read] LBA 00 : 0x00000000"),
    ]
)
def test_buffer_fastread_4(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("erase", "00", "01", ["1_E_0_1"], "[Erase] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("read", "00", "",           ["1_W_0_0x00000001"], "[Read] LBA 00 : 0x00000001"),
    ]
)
def test_buffer_fastread_5(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("erase", "00", "01", ["1_E_0_1"], "[Erase] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("flush", "", "", ["2_empty"], "[Flush] Done"),
        ("read", "00", "",           ["1_empty"], "[Read] LBA 00 : 0x00000001"),
    ]
)
def test_buffer_fastread_6(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "00", "0x00000002", ["1_W_0_0x00000002"], "[Write] Done"),
        ("read", "00", "",           ["1_W_0_0x00000002"], "[Read] LBA 00 : 0x00000002"),
    ]
)
def test_buffer_fastread_7(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "00", "0x00000002", ["1_W_0_0x00000002"], "[Write] Done"),
        ("flush", "", "", ["2_empty"], "[Flush] Done"),
        ("read", "00", "",           ["1_empty"], "[Read] LBA 00 : 0x00000002"),
    ]
)
def test_buffer_fastread_8(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "00", "0x00000002", ["1_W_0_0x00000002"], "[Write] Done"),
        ("write", "00", "0x00000003", ["1_W_0_0x00000003"], "[Write] Done"),
        ("write", "00", "0x00000004", ["1_W_0_0x00000004"], "[Write] Done"),
        ("write", "00", "0x00000005", ["1_W_0_0x00000005"], "[Write] Done"),
        ("read", "00", "",           ["1_W_0_0x00000005"], "[Read] LBA 00 : 0x00000005"),
    ]
)
def test_buffer_fastread_9(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "00", "0x00000002", ["1_W_0_0x00000002"], "[Write] Done"),
        ("write", "00", "0x00000003", ["1_W_0_0x00000003"], "[Write] Done"),
        ("write", "00", "0x00000004", ["1_W_0_0x00000004"], "[Write] Done"),
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000005", ["1_W_0_0x00000005"], "[Write] Done"),
        ("read", "00", "",           ["1_W_0_0x00000005"], "[Read] LBA 00 : 0x00000005"),
    ]
)
def test_buffer_fastread_10(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "01", "0x00000002", ["2_W_1_0x00000002"], "[Write] Done"),
        ("write", "02", "0x00000003", ["3_W_2_0x00000003"], "[Write] Done"),
        ("erase", "00", "01", ["3_E_0_1"], "[Erase] Done"),
        ("read", "00", "",           ["1_W_1_0x00000002"], "[Read] LBA 00 : 0x00000000"),
        ("read", "01", "",           ["2_W_2_0x00000003"], "[Read] LBA 01 : 0x00000002"),
        ("read", "02", "",           ["3_E_0_1"], "[Read] LBA 02 : 0x00000003")
    ]
)
def test_buffer_fastread_11(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "01", "0x00000002", ["2_W_1_0x00000002"], "[Write] Done"),
        ("write", "02", "0x00000003", ["3_W_2_0x00000003"], "[Write] Done"),
        ("erase_range", "0", "1", ["2_E_0_2"], "[Erase_range] Done"),
        ("read", "00", "",           ["1_W_2_0x00000003"], "[Read] LBA 00 : 0x00000000"),
        ("read", "01", "",           ["2_E_0_2"], "[Read] LBA 01 : 0x00000000"),
        ("read", "02", "",           ["3_empty"], "[Read] LBA 02 : 0x00000003")
    ]
)
def test_buffer_fastread_12(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "10", "0x00000001", ["1_W_10_0x00000001"], "[Write] Done"),
        ("erase", "11", "2", ["2_E_11_2"], "[Erase] Done"),
        ("write", "11", "0x00000001", ["3_W_11_0x00000001"], "[Write] Done"),
        ("erase", "12", "2", ["3_E_12_2"], "[Erase] Done"),
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("read", "10", "",           ["1_empty"], "[Read] LBA 10 : 0x00000001"),
    ]
)
def test_buffer_fastread_13(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "01", "0x00000002", ["2_W_1_0x00000002"], "[Write] Done"),
        ("write", "02", "0x00000003", ["3_W_2_0x00000003"], "[Write] Done"),
        ("write", "03", "0x00000004", ["4_W_3_0x00000004"], "[Write] Done"),
        ("write", "04", "0x00000005", ["5_W_4_0x00000005"], "[Write] Done"),
        ("read", "00", "",           ["1_W_0_0x00000001"], "[Read] LBA 00 : 0x00000001"),
        ("read", "01", "",           ["2_W_1_0x00000002"], "[Read] LBA 01 : 0x00000002"),
        ("read", "02", "",           ["3_W_2_0x00000003"], "[Read] LBA 02 : 0x00000003"),
        ("read", "03", "",           ["4_W_3_0x00000004"], "[Read] LBA 03 : 0x00000004"),
        ("read", "04", "",           ["5_W_4_0x00000005"], "[Read] LBA 04 : 0x00000005"),
        ("write", "06", "0x00000001", ["1_W_6_0x00000001"], "[Write] Done"),
    ]
)
def test_buffer_fastread_14(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "01", "0x00000002", ["2_W_1_0x00000002"], "[Write] Done"),
        ("write", "02", "0x00000003", ["3_W_2_0x00000003"], "[Write] Done"),
        ("write", "03", "0x00000004", ["4_W_3_0x00000004"], "[Write] Done"),
        ("write", "04", "0x00000005", ["5_W_4_0x00000005"], "[Write] Done"),
        ("read", "00", "",           ["1_W_0_0x00000001"], "[Read] LBA 00 : 0x00000001"),
        ("read", "01", "",           ["2_W_1_0x00000002"], "[Read] LBA 01 : 0x00000002"),
        ("read", "02", "",           ["3_W_2_0x00000003"], "[Read] LBA 02 : 0x00000003"),
        ("read", "03", "",           ["4_W_3_0x00000004"], "[Read] LBA 03 : 0x00000004"),
        ("read", "04", "",           ["5_W_4_0x00000005"], "[Read] LBA 04 : 0x00000005"),
        ("write", "00", "0x00000001", ["5_W_0_0x00000001"], "[Write] Done"),
    ]
)
def test_buffer_fastread_15(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "01", "0x00000002", ["2_W_1_0x00000002"], "[Write] Done"),
        ("write", "02", "0x00000003", ["3_W_2_0x00000003"], "[Write] Done"),
        ("write", "03", "0x00000004", ["4_W_3_0x00000004"], "[Write] Done"),
        ("write", "04", "0x00000005", ["5_W_4_0x00000005"], "[Write] Done"),
        ("erase", "00", "05",           ["1_E_0_5"], "[Erase] Done"),
        ("read", "00", "",           ["1_E_0_5"], "[Read] LBA 00 : 0x00000000"),
        ("read", "01", "",           ["1_E_0_5"], "[Read] LBA 01 : 0x00000000"),
        ("read", "02", "",           ["1_E_0_5"], "[Read] LBA 02 : 0x00000000"),
        ("read", "03", "",           ["1_E_0_5"], "[Read] LBA 03 : 0x00000000"),
        ("read", "04", "",           ["1_E_0_5"], "[Read] LBA 04 : 0x00000000"),
    ]
)
def test_buffer_fastread_16(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "01", "0x00000002", ["2_W_1_0x00000002"], "[Write] Done"),
        ("write", "02", "0x00000003", ["3_W_2_0x00000003"], "[Write] Done"),
        ("write", "03", "0x00000004", ["4_W_3_0x00000004"], "[Write] Done"),
        ("write", "04", "0x00000005", ["5_W_4_0x00000005"], "[Write] Done"),
        ("erase_range", "04", "00",           ["1_E_0_5"], "[Erase_range] Done"),
        ("read", "00", "",           ["1_E_0_5"], "[Read] LBA 00 : 0x00000000"),
        ("read", "01", "",           ["1_E_0_5"], "[Read] LBA 01 : 0x00000000"),
        ("read", "02", "",           ["1_E_0_5"], "[Read] LBA 02 : 0x00000000"),
        ("read", "03", "",           ["1_E_0_5"], "[Read] LBA 03 : 0x00000000"),
        ("read", "04", "",           ["1_E_0_5"], "[Read] LBA 04 : 0x00000000"),
    ]
)
def test_buffer_fastread_17(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "01", "0x00000002", ["2_W_1_0x00000002"], "[Write] Done"),
        ("write", "02", "0x00000003", ["3_W_2_0x00000003"], "[Write] Done"),
        ("write", "03", "0x00000004", ["4_W_3_0x00000004"], "[Write] Done"),
        ("write", "04", "0x00000005", ["5_W_4_0x00000005"], "[Write] Done"),
        ("erase", "04", "-5",           ["1_E_0_5"], "[Erase] Done"),
        ("read", "00", "",           ["1_E_0_5"], "[Read] LBA 00 : 0x00000000"),
        ("read", "01", "",           ["1_E_0_5"], "[Read] LBA 01 : 0x00000000"),
        ("read", "02", "",           ["1_E_0_5"], "[Read] LBA 02 : 0x00000000"),
        ("read", "03", "",           ["1_E_0_5"], "[Read] LBA 03 : 0x00000000"),
        ("read", "04", "",           ["1_E_0_5"], "[Read] LBA 04 : 0x00000000")
    ]
)
def test_buffer_fastread_18(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "01", "0x00000002", ["2_W_1_0x00000002"], "[Write] Done"),
        ("write", "02", "0x00000003", ["3_W_2_0x00000003"], "[Write] Done"),
        ("erase", "0", "100", ["1_E_50_10"], "[Erase] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "01", "0x00000002", ["2_W_1_0x00000002"], "[Write] Done"),
        ("write", "02", "0x00000003", ["3_W_2_0x00000003"], "[Write] Done"),
        ("erase", "0", "-1000", ["3_E_0_1"], "[Erase] Done"),
        ("erase", "99", "-1000", ["1_E_50_10"], "[Erase] Done"),
    ]
)
def test_buffer_fastread_19(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "01", "0x00000002", ["2_W_1_0x00000002"], "[Write] Done"),
        ("write", "02", "0x00000003", ["3_W_2_0x00000003"], "[Write] Done"),
        ("erase", "0", "1", ["3_E_0_1"], "[Erase] Done"),
        ("write", "03", "0x00000003", ["4_W_3_0x00000003"], "[Write] Done"),
        ("read", "00", "",           ["3_E_0_1"], "[Read] LBA 00 : 0x00000000"),
        ("erase", "0", "-1", ["4_E_0_1"], "[Erase] Done"),
        ("erase_range", "2", "0", ["2_E_0_3"], "[Erase_range] Done"),
    ]
)
def test_buffer_fastread_20(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "", ["1_empty"], "[Flush] Done"),
        ("write", "0", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("write", "00", "0x00000001", ["1_W_0_0x00000001"], "[Write] Done"),
        ("read", "0", "", ["1_W_0_0x00000001"], "[Read] LBA 00 : 0x00000001"),
        ("read", "00", "", ["1_W_0_0x00000001"], "[Read] LBA 00 : 0x00000001"),
        ("erase", "0", "1", ["1_E_0_1"], "[Erase] Done"),
        ("read", "00", "", ["1_E_0_1"], "[Read] LBA 00 : 0x00000000"),
        ("erase", "00", "1", ["1_E_0_1"], "[Erase] Done"),
    ]
)
def test_buffer_fastread_21(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app)

@pytest.mark.parametrize(
    "cmd, arg1, arg2, buffer_files, check_print",
    [
        ("flush", "", "",        ["1_empty"], "[Flush] Done"),
        ("flush", "0", "",       ["1_empty"], "INVALID COMMAND"),
        ("write", "00", "0x",    ["1_empty"], "INVALID COMMAND"),
        ("write", "00", "-",     ["1_empty"], "INVALID COMMAND"),
        ("write", "00", "None",  ["1_empty"], "INVALID COMMAND"),
        ("write", "00", "-1",    ["1_empty"], "INVALID COMMAND"),
        ("write", "00", "A",     ["1_empty"], "INVALID COMMAND"),
        ("write", "00", "1.5",     ["1_empty"], "INVALID COMMAND"),
        ("write", "-1", "0",     ["1_empty"], "INVALID COMMAND"),
        ("write", "100", "0",     ["1_empty"], "INVALID COMMAND"),
        ("write", "a", "0",     ["1_empty"], "INVALID COMMAND"),
        ("write", "0x0", "0",     ["1_empty"], "INVALID COMMAND"),
        ("write", "1.5", "0",     ["1_empty"], "INVALID COMMAND"),
        ("erase", "-1", "1",     ["1_empty"], "INVALID COMMAND"),
        ("erase", "100", "1",     ["1_empty"], "INVALID COMMAND"),
        ("erase", "a", "1",     ["1_empty"], "INVALID COMMAND"),
        ("erase", "0x0", "1",     ["1_empty"], "INVALID COMMAND"),
        ("erase", "0", "-1.5",     ["1_empty"], "INVALID COMMAND"),
        ("erase", "0", "0xa",     ["1_empty"], "INVALID COMMAND"),
        ("erase", "0", "None",     ["1_empty"], "INVALID COMMAND"),
        ("erase", "0", "A",     ["1_empty"], "INVALID COMMAND"),
        ("erase_range", "0", "-1",     ["1_empty"], "INVALID COMMAND"),
        ("erase_range", "-2", "-1",     ["1_empty"], "INVALID COMMAND"),
        ("erase_range", "0", "1.5",     ["1_empty"], "INVALID COMMAND"),
        ("erase_range", "0", "a",     ["1_empty"], "INVALID COMMAND"),
        ("erase_range", "100", "0",     ["1_empty"], "INVALID COMMAND"),
        ("erase_range", "99", "-1",     ["1_empty"], "INVALID COMMAND"),
        ("read", "-1", "",       ["1_empty"], "INVALID COMMAND"),
        ("read", "100", "",       ["1_empty"], "INVALID COMMAND"),
        ("read", "a", "",       ["1_empty"], "INVALID COMMAND"),
        ("read", "None", "",       ["1_empty"], "INVALID COMMAND"),
        ("read", "1.5", "",       ["1_empty"], "INVALID COMMAND")
    ]
)
def test_buffer_fastread_22(shell_app, cmd, arg1, arg2, buffer_files, check_print, mocker: MockerFixture, capsys):
    fast_read(arg1, arg2, buffer_files, capsys, check_print, cmd, mocker, shell_app, invalid_command=True)
