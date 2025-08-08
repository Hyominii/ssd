import tempfile

import pytest
from pytest_mock import MockerFixture
from shell import *


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
                                            "1_ 02", "2_ s", "2_ a", "4_ *"])
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
    expected_lines = [
        "팀명: BestReviewer",
        "팀장: 이장희 / 팀원: 김대용, 최도현, 박윤상, 최동희, 안효민, 김동훈",
        "",
        "사용 가능한 명령어:",
        "  write <LBA> <Value>                : 특정 LBA에 값 저장",
        "  read <LBA>                         : 특정 LBA 값 읽기",
        "  erase <Start_LBA> <Size>           : Start_LBA부터 Size만큼 값 초기화",
        "  erase_range <Start_LBA> <End_LBA>  : Start_LBA부터 End_LBA까지 값 초기화 ",
        "  fullwrite <Value>                  : 전체 LBA에 동일 값 저장",
        "  fullread                           : 전체 LBA 읽기 및 출력",
        "  1_FullWriteAndReadCompare          : 전체 LBA 쓰기 및 비교",
        "  2_PartialLBAWrite                  : LBA 0 ~ 4 쓰기 및 읽기 30회",
        "  3_WriteReadAging                   : LBA 0, 99 랜덤 값 쓰기 및 읽기 200회",
        "  4_EraseAndWriteAging               : LBA 짝수번호에 값을 두번 쓰고 및 size 3 만큼 지우기를 30회 반복함",
        "  help                               : 도움말 출력",
        "  exit                               : 종료"
    ]
    for line in expected_lines:
        assert line in captured.out

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
    cmd = [f"{wrong_address} 0x12345678"]
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
    cmd = [f"00 {wrong_value}"]
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

@pytest.mark.parametrize("valid_value", ["0xa", "0xab", "0xabc", "0xabcd", "0xabcde", "0xabcdef", "0xabcdeff", "0x00000000000000000001"])
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
    cmd = [f"{wrong_address} 0x12345678", f"read {wrong_address}"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Write] Done' not in captured.out
    assert 'INVALID COMMAND' in captured.out

@pytest.mark.parametrize("wrong_value", ["AA", "0xHELLO", "ox11", "0xaaaaaaaaaa", "-0xa", "1234", ";", " ", "0xA00000000000000001"])
def test_shell_read_after_write_wrong_value(shell_app, wrong_value, mocker: MockerFixture, capsys):
    # Arrange
    cmd = [f"00 {wrong_value}", f"read 00"]
    cmd_len = len(cmd)
    mocker.patch("builtins.input", side_effect=cmd)

    # Act
    ret = shell_app.run_shell(cmd_len)
    captured = capsys.readouterr()

    # Assert
    assert '[Write] Done' not in captured.out
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

@pytest.mark.parametrize("valid_value", ["0xa", "0xab", "0xabc", "0xabcd", "0xabcde", "0xabcdef", "0xabcdeff", "0x00000000000000000001"])
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

@pytest.mark.parametrize("wrong_value", ["AA", "0xHELLO", "ox11", "0xaaaaaaaaaa", "-0xa", "1234", ";", " ", "0xA00000000000000001"])
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

@pytest.mark.parametrize("wrong_value", ["AA", "0xHELLO", "ox11", "0xaaaaaaaaaa", "-0xa", "1234", ";", " ", "0xA00000000000000001"])
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




def test_shell_full_write_wrong_format():
    pass


def test_shell_full_write_and_read_compare(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    shell_app._ssd_driver.run_ssd_write.side_effect = [WRITE_SUCCESS] * 100
    shell_app._ssd_driver.run_ssd_read.side_effect = [READ_SUCCESS] * 100
    shell_app._ssd_driver.get_ssd_output.return_value = "0x12345678"
    # Act
    shell_app.process_cmd("1_FullWriteAndReadCompare")

    # Assert
    assert "Pass" in capsys.readouterr().out

    assert shell_app._ssd_driver.run_ssd_write.call_count == 100
    assert shell_app._ssd_driver.run_ssd_read.call_count == 100


def test_shell_partial_lba_write(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    shell_app._ssd_driver.run_ssd_write.side_effect = [WRITE_SUCCESS] * 150
    shell_app._ssd_driver.run_ssd_read.side_effect = [READ_SUCCESS] * 150
    shell_app._ssd_driver.get_ssd_output.return_value = "0x12345678"

    # Act
    shell_app.process_cmd("2_PartialLBAWrite")

    # Assert
    assert "Pass" in capsys.readouterr().out

    assert shell_app._ssd_driver.run_ssd_write.call_count == 150
    assert shell_app._ssd_driver.run_ssd_read.call_count == 150


def test_shell_write_read_aging_with_real(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    shell_app = TestShellApp()

    # Act
    shell_app.process_cmd("3_WriteReadAging")

    # Assert
    assert "Pass" in capsys.readouterr().out


def test_shell_runner_with_testfile_correct_cmd(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    shell_app = TestShellApp()
    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_file:
        temp_file.write("1_\n")
        temp_file_path = temp_file.name

    # Act
    try:
        shell_app.run_runner(temp_file_path)
    finally:
        # 테스트 후 파일 삭제
        os.remove(temp_file_path)
    # Assert
    assert "1_  ___  RUN...Pass" in capsys.readouterr().out


def test_shell_runner_with_testfile_incorrect_cmd(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    shell_app = TestShellApp()
    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_file:
        temp_file.write("Hello\n")
        temp_file_path = temp_file.name

    # Act
    try:
        shell_app.run_runner(temp_file_path)
    finally:
        # 테스트 후 파일 삭제
        os.remove(temp_file_path)

    # Assert
    assert "INVALID COMMAND" in capsys.readouterr().out


def test_shell_runner_without_testfile(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    shell_app = TestShellApp()

    # Act
    shell_app.run_runner()

    # Assert
    assert "INVALID COMMAND" in capsys.readouterr().out


def test_shell_runner_with_wrong_testfile(shell_app, mocker: MockerFixture, capsys):
    # Arrange
    shell_app = TestShellApp()

    # Act
    scipt_file = f"{ROOT_DIR}\shell_scripts_.txt"
    shell_app.run_runner(scipt_file)

    # Assert
    assert "INVALID COMMAND" in capsys.readouterr().out


@pytest.mark.parametrize("size", ["0.5", "-1.5", "0xa", "-0x1"])
def test_shell_erase_invalid_size(shell_app, size):
    # Arrange
    shell_app._ssd_driver.run_ssd_erase.return_value = ERASE_SUCCESS

    # Act
    ret_fail = shell_app.erase(address="0", lba_size=size)

    # Assert
    assert ERASE_ERROR == ret_fail


def test_shell_erase(shell_app):
    # Arrange
    shell_app._ssd_driver.run_ssd_erase.return_value = ERASE_SUCCESS

    # Act
    ret_pass = shell_app.erase(address="0", lba_size="1")

    # Assert
    assert ERASE_SUCCESS == ret_pass


def test_shell_erase_resize(shell_app, mocker):
    # Arrange
    shell_app._ssd_driver.run_ssd_erase.return_value = ERASE_SUCCESS
    mocker.patch.object(shell_app, "_erase_in_chunks", return_value=ERASE_SUCCESS, )

    # Act
    ret_pass = shell_app.erase(address="0", lba_size="1000")

    # Assert
    assert ERASE_SUCCESS == ret_pass
    shell_app._erase_in_chunks.assert_called_once_with(start_lba=0, size=100)


def test_shell_erase_resize_minus(shell_app, mocker):
    # Arrange
    shell_app._ssd_driver.run_ssd_erase.return_value = ERASE_SUCCESS
    mocker.patch.object(shell_app, "_erase_in_chunks", return_value=ERASE_SUCCESS, )

    # Act
    ret_pass = shell_app.erase(address="30", lba_size="-20")

    # Assert
    assert ERASE_SUCCESS == ret_pass
    shell_app._erase_in_chunks.assert_called_once_with(start_lba=11, size=20)


def test_shell_erase_range(shell_app, mocker):
    # Arrange
    shell_app._ssd_driver.run_ssd_erase.return_value = ERASE_SUCCESS
    mocker.patch.object(shell_app, "_erase_in_chunks", return_value=ERASE_SUCCESS, )

    # Act
    ret_pass = shell_app.erase_range(start_lba="31", end_lba="60")

    # Assert
    assert ERASE_SUCCESS == ret_pass
    shell_app._erase_in_chunks.assert_called_once_with(start_lba=31, size=30)


def test_shell_erase_range_reverse(shell_app, mocker):
    # Arrange
    shell_app._ssd_driver.run_ssd_erase.return_value = ERASE_SUCCESS
    mocker.patch.object(shell_app, "_erase_in_chunks", return_value=ERASE_SUCCESS, )

    # Act
    ret_pass = shell_app.erase_range(start_lba="60", end_lba="31")

    # Assert
    assert ERASE_SUCCESS == ret_pass
    shell_app._erase_in_chunks.assert_called_once_with(start_lba=31, size=30)


@pytest.mark.parametrize("range", [("-1", "10"), ("1", "100"), ("1.5", "10"), ("10", "10.5")])
def test_shell_erase_invalid_range(shell_app, mocker, range):
    # Arrange
    shell_app._ssd_driver.run_ssd_erase.return_value = ERASE_SUCCESS
    mocker.patch.object(shell_app, "_erase_in_chunks", return_value=ERASE_SUCCESS, )

    # Act
    ret_pass = shell_app.erase_range(start_lba=range[0], end_lba=range[1])

    # Assert
    assert ERASE_ERROR == ret_pass
