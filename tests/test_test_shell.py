import pytest

from ssd.test_shell import TestShellApp


def test_shell_write():
    pass


def test_shell_write_subprocess():
    pass


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


def test_shell_wrong_cmd():
    pass


def test_shell_wrong_cmd_format():
    pass


def test_shell_wrong_cmd_args():
    pass


def test_shell_subprocess_cmd():
    pass


def test_shell_exit():
    pass


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


def test_shell_full_write():
    pass


def test_shell_full_write_wrong_format():
    pass
