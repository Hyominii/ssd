import tempfile
import pytest
from pytest_mock import MockerFixture
from shell import *
from shell_cmd_checker import COMMAND_DESCRIPTION


@pytest.fixture
def shell_app(mocker):
    ssd_driver = SSDDriver()
    test_shell_app = TestShellApp(ssd_driver)

    return test_shell_app


@pytest.mark.parametrize("wrong_cmd", ["exi", "rea", "wri", "hel", " ", "0_", "*"])
def test_shell_wrong_cmd(shell_app, mocker: MockerFixture, wrong_cmd, capsys):
    # Arrange
    cmd = [f"{wrong_cmd}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert 'INVALID COMMAND' in captured.out


@pytest.mark.parametrize("wrong_cmd_args", ["write", "read 1 2", "fullwrite", "fullread 0000", "exit 3", "help -", \
                                            "1_ 02", "2_ s", "2_ a", "4_ *", "flush 0"])
def test_shell_wrong_cmd_args(shell_app, mocker: MockerFixture, wrong_cmd_args, capsys):
    # Arrange
    cmd = [f"{wrong_cmd_args}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert 'INVALID COMMAND' in captured.out


def test_shell_cmd_exit_success(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    cmd = ["exit"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    with pytest.raises(SystemExit) as e:
        shell_app.run_shell(cmd_len)

    captured = capsys.readouterr()

    # Assert
    assert e.value.code == 0
    assert 'INVALID COMMAND' not in captured.out


def test_shell_cmd_help_success(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    cmd = ["help"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert 'INVALID COMMAND' not in captured.out
    for line in COMMAND_DESCRIPTION:
        assert line in captured.out


def test_shell_cmd_flush_success(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    cmd = ["flush"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    shell_app.run_shell(cmd_len)

    captured = capsys.readouterr()

    # Assert
    buffer_files = ["1_empty", "2_empty", "3_empty", "4_empty", "5_empty"]
    assert 'INVALID COMMAND' not in captured.out
    assert '[Flush] Done' in captured.out
    for buffer_file in buffer_files:
        full_buffer_file = os.path.join(f"{ROOT_DIR}/buffer", buffer_file)
        assert os.path.exists(full_buffer_file)


def test_shell_write(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    cmd = ["write 0 0x00000001"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Write] Done' in captured.out
    assert 'INVALID COMMAND' not in captured.out


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


@pytest.mark.parametrize("valid_value", ["0xa", "0xab", "0xabc", "0xabcd", "0xabcde", "0xabcdef", "0xabcdeff",
                                         "0x00000000000000000001"])
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


@pytest.mark.parametrize("wrong_value",
                         ["AA", "0xHELLO", "ox11", "0xaaaaaaaaaa", "-0xa", "1234", ";", " ", "0xA00000000000000001"])
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


def test_shell_read(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    cmd = ["write 00 0x00000000", "read 0"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Write] Done' in captured.out
    assert '[Read] LBA 00 : 0x00000000' in captured.out
    assert 'INVALID COMMAND' not in captured.out


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


@pytest.mark.parametrize("valid_value", ["0xa", "0xab", "0xabc", "0xabcd", "0xabcde", "0xabcdef", "0xabcdeff",
                                         "0x00000000000000000001"])
def test_shell_read_valid_value(shell_app, valid_value, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"write 00 {valid_value}", f"read 00"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    int_value = int(valid_value, 16)
    assert '[Write] Done' in captured.out
    assert f'[Read] LBA 00 : 0x{int_value:08X}' in captured.out
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


@pytest.mark.parametrize("wrong_value",
                         ["AA", "0xHELLO", "ox11", "0xaaaaaaaaaa", "-0xa", "1234", ";", " ", "0xA00000000000000001"])
def test_shell_read_after_write_wrong_value(shell_app, wrong_value, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"write 00 {wrong_value}", f"read 00"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Write] Done' not in captured.out
    assert 'INVALID COMMAND' in captured.out


def test_shell_erase(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    cmd = ["erase 0 1"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Erase] Done' in captured.out
    assert 'INVALID COMMAND' not in captured.out


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


@pytest.mark.skip
@pytest.mark.parametrize("valid_address", [str(x) for x in range(100)])
@pytest.mark.parametrize("valid_size", ["1", "100", "4294967295", "0", "-1", "-100", "-4294967295"])
def test_shell_erase_with_valid_size(shell_app, valid_address, valid_size, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"erase {valid_address} {valid_size}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Erase] Done' in captured.out
    assert 'INVALID COMMAND' not in captured.out


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


def test_shell_erase_range(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    cmd = ["erase_range 0 1", "erase_range 1 0"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Erase_range] Done' in captured.out
    assert 'INVALID COMMAND' not in captured.out


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


def test_shell_cmd_fullwrite(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    cmd = ["fullwrite 0x00000001"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert 'INVALID COMMAND' not in captured.out


def test_shell_cmd_fullread(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    cmd = ["fullwrite 0x00000001", "fullread"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert 'INVALID COMMAND' not in captured.out
    for address in range(100):
        assert f'[Read] LBA {address:02} : 0x00000001' in captured.out


@pytest.mark.skip
@pytest.mark.parametrize("valid_value", ["0xa", "0xab", "0xabc", "0xabcd", "0xabcde", "0xabcdef", "0xabcdeff",
                                         "0x00000000000000000001"])
def test_shell_cmd_fullwrite_with_valid_value(shell_app, valid_value, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"fullwrite {valid_value}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert 'INVALID COMMAND' not in captured.out


@pytest.mark.parametrize("wrong_value",
                         ["AA", "0xHELLO", "ox11", "0xaaaaaaaaaa", "-0xa", "1234", ";", " ", "0xA00000000000000001"])
def test_shell_cmd_fullwrite_with_wrong_value(shell_app, wrong_value, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"fullwrite {wrong_value}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert 'INVALID COMMAND' in captured.out


@pytest.mark.skip
@pytest.mark.parametrize("wrong_value",
                         ["AA", "0xHELLO", "ox11", "0xaaaaaaaaaa", "-0xa", "1234", ";", " ", "0xA00000000000000001"])
def test_shell_cmd_fullread_after_write_wrong_value(shell_app, wrong_value, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"fullwrite 0x00000001", f"fullwrite {wrong_value}", "fullread"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert 'INVALID COMMAND' in captured.out
    for address in range(100):
        assert f'[Read] LBA {address:02} : 0x00000001' in captured.out


def test_shell_full_write_and_read_compare(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"1_FullWriteAndReadCompare", f"1_"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert 'INVALID COMMAND' not in captured.out
    assert 'Pass' in captured.out
    for address in range(100):
        assert f'[Read] LBA {address:02} : 0x12345678' in captured.out


def test_shell_partial_lba_write(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"2_PartialLBAWrite", f"2_"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert 'INVALID COMMAND' not in captured.out
    assert 'Pass' in captured.out
    for address in range(5):
        assert f'[Read] LBA {address:02} : 0x12345678' in captured.out  # ToDo: check iterations are 30


@pytest.mark.skip
def test_shell_write_read_aging_with_real(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"3_WriteReadAging", f"3_"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert 'INVALID COMMAND' not in captured.out
    assert 'Pass' in captured.out
    # ToDo: check read value


@pytest.mark.skip
def test_shell_erase_write_aging(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"4_EraseAndWriteAging", f"4_"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert 'INVALID COMMAND' not in captured.out
    assert 'Pass' in captured.out
    # ToDo: check read value


@pytest.mark.skip
@pytest.mark.parametrize("valid_cmd", ["1_", "2_", "3_", "4_", "1_FullWriteAndReadCompare",
                                       "2_PartialLBAWrite", "3_WriteReadAging", "4_EraseAndWriteAging"])
def test_shell_runner_with_testfile_valid_cmd(shell_app, valid_cmd, mocker: MockerFixture, capsys):
    # Arrange
    shell_app = TestShellApp()
    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_file:
        temp_file.write(f"{valid_cmd}\n")
        temp_file_path = temp_file.name

    # Act
    try:
        shell_app.run_runner(temp_file_path)
    finally:
        # 테스트 후 파일 삭제
        os.remove(temp_file_path)
    # Assert
    test_case = valid_cmd[:2]
    assert f"{test_case}  ___  RUN...Pass" in capsys.readouterr().out


@pytest.mark.parametrize("invalid_cmd", ["1_2", "he", " ", "None", "-",
                                         "0_", "5_", "-1_"])
def test_shell_runner_with_testfile_incorrect_cmd(shell_app, invalid_cmd, mocker: MockerFixture, capsys):
    # Arrange
    shell_app = TestShellApp()
    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_file:
        temp_file.write(f"{invalid_cmd}\n")
        temp_file_path = temp_file.name

    # Act
    try:
        shell_app.run_runner(temp_file_path)
    finally:
        # 테스트 후 파일 삭제
        os.remove(temp_file_path)

    # Assert
    assert "INVALID COMMAND" in capsys.readouterr().out


@pytest.mark.parametrize("invalid_file", [" ", f"{ROOT_DIR}\shell_scripts_.txt", f"shell_scripts.txt"])
def test_shell_runner_with_invalid_testfile(shell_app, invalid_file, mocker: MockerFixture, capsys):
    # Arrange
    shell_app = TestShellApp()

    # Act
    shell_app.run_runner(invalid_file)

    # Assert
    assert "INVALID COMMAND" in capsys.readouterr().out
