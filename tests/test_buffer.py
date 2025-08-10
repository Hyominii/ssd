import pytest
import shutil
import os

from unittest.mock import Mock  # Mock 객체를 만들기 위해 import

# 테스트할 클래스들을 import
from ssd import (
    CommandInvoker,
    ReadCommand,
    WriteCommand,
    EraseCommand,
    SSD,
    BUFFER_DIR,
)

TEST_VALUE = "0x01234567"

# --- Fixtures: 테스트 환경 준비 ---

@pytest.fixture
def mock_ssd():
    """실제 SSD 로직과 분리하기 위한 가짜(Mock) SSD 객체를 생성합니다."""
    # Mock 객체는 어떤 메서드를 호출해도 에러 없이 동작합니다.
    return Mock(spec=SSD)

@pytest.fixture(autouse=True)
def clean_buffer_dir():
    # 각 테스트 전 BUFFER_DIR 클린업
    if os.path.exists(BUFFER_DIR):
        shutil.rmtree(BUFFER_DIR, ignore_errors=True)
    os.makedirs(BUFFER_DIR)
    yield


# @pytest.fixture
# def invoker():
#     """모든 테스트에서 새로운 CommandInvoker 인스턴스를 사용하도록 합니다."""
#     return CommandInvoker(Mock(spec=SSD))


# --- Test Cases (TC) ---

def test_invoker_initialization(mock_ssd):
    """TC1: Invoker가 처음 생성되었을 때 버퍼는 비어있어야 한다."""
    invoker = CommandInvoker(mock_ssd)
    assert invoker.num_commands() == 0
    assert len(invoker.get_buffer()) == 0


def test_add_one_write_command(mock_ssd):
    """TC2: WriteCommand를 하나 추가했을 때 버퍼가 올바르게 구성되는가?"""
    # ARRANGE: 테스트 준비
    invoker = CommandInvoker(mock_ssd)
    cmd = WriteCommand(mock_ssd, 10, TEST_VALUE, 1)

    # ACT: 테스트할 동작 실행
    invoker.add_command(cmd)

    # ASSERT: 결과 검증
    assert invoker.num_commands() == 1

    buffered_cmd = invoker.get_buffer()[0]
    assert isinstance(buffered_cmd, WriteCommand)
    assert buffered_cmd._address == 10
    assert buffered_cmd._value == TEST_VALUE
    # assert buffered_cmd.seq == 1

def test_add_one_erase_command(mock_ssd):
    """TC3: ReadCommand를 하나 추가했을 때 버퍼가 올바르게 구성되는가?"""
    # ARRANGE
    invoker = CommandInvoker(mock_ssd)
    cmd = EraseCommand(mock_ssd, 5, 5, 1)

    # ACT
    invoker.add_command(cmd)

    # ASSERT
    assert invoker.num_commands() == 1
    buffered_cmd = invoker.get_buffer()[0]
    assert isinstance(buffered_cmd, EraseCommand)

def test_add_one_read_command(mock_ssd):
    """TC3: ReadCommand를 하나 추가했을 때 버퍼가 올바르게 구성되는가?"""
    # ARRANGE
    invoker = CommandInvoker(mock_ssd)
    cmd = ReadCommand(mock_ssd, 5)
    cmd.execute = Mock()

    # ACT
    invoker.add_command(cmd)

    # ASSERT
    assert invoker.num_commands() == 0
    # buffered_cmd = invoker.get_buffer()[0]
    # assert isinstance(buffered_cmd, ReadCommand)
    assert len(invoker.get_buffer()) == 0  # 버퍼 빈 상태 확인
    cmd.execute.assert_called_once()  # 즉시 실행 확인


# def test_add_one_read_command(invoker, mock_ssd):
#     # Arrange
#     assert invoker.num_commands() == 0
#
#     # Act
#     invoker.add_command(ReadCommand(mock_ssd, 0))
#
#     # Assert
#     assert invoker.num_commands() == 1
#     assert isinstance(invoker.get_buffer()[0], ReadCommand)



def test_add_multiple_commands(mock_ssd):
    """TC4: 여러 개의 커맨드를 순차적으로 추가했을 때 버퍼가 올바르게 쌓이는가?"""
    # ARRANGE & ACT
    invoker = CommandInvoker(mock_ssd)
    invoker.add_command(WriteCommand(mock_ssd, 0, "0x11112222", 1))
    invoker.add_command(WriteCommand(mock_ssd, 1, "0x22221111", 2))
    invoker.add_command(EraseCommand(mock_ssd, 5, 10, 3))

    # ASSERT
    assert invoker.num_commands() == 3

    buffer = invoker.get_buffer()
    assert isinstance(buffer[0], WriteCommand)
    assert isinstance(buffer[1], WriteCommand)
    assert isinstance(buffer[2], EraseCommand)

    assert buffer[1]._address == 1
    assert buffer[2]._address == 5


# def test_flush_executes_and_clears_buffer(mocker, mock_ssd):
def test_flush_executes_and_clears_buffer(mock_ssd):
    """TC5: flush()가 버퍼의 모든 커맨드를 실행하고 버퍼를 비우는가?"""
    # ARRANGE
    # 각 커맨드 객체의 execute 메서드를 Mocking(감시)합니다.
    invoker = CommandInvoker(mock_ssd)
    mock_write_cmd = WriteCommand(mock_ssd, 0, "0x11112222", 1)
    mock_erase_cmd = EraseCommand(mock_ssd, 5, 10, 2)
    # mocker.spy(mock_write_cmd, "execute")
    # mocker.spy(mock_erase_cmd, "execute")

    mock_write_cmd.execute = Mock()
    mock_erase_cmd.execute = Mock()

    invoker.add_command(mock_write_cmd)
    invoker.add_command(mock_erase_cmd)

    assert invoker.num_commands() == 2  # Flush 전 버퍼 확인

    # ACT
    invoker.flush()

    # ASSERT
    # 각 커맨드의 execute 메서드가 정확히 한 번씩 호출되었는지 확인
    mock_write_cmd.execute.assert_called_once()
    mock_erase_cmd.execute.assert_called_once()

    # Flush 후 버퍼가 비워졌는지 확인
    assert invoker.num_commands() == 0


# def test_ignore_overwrite_command(mock_ssd):
#     """TC7: 같은 LBA에 Write Overwrite 시 이전 명령 무시."""
#     invoker = CommandInvoker(mock_ssd)
#     invoker.add_command(WriteCommand(mock_ssd, 10, "0xOLDVALUE", 1))
#     invoker.add_command(WriteCommand(mock_ssd, 10, "0xNEWVALUE", 2))  # Overwrite
#
#     buffer = invoker.get_buffer()
#     assert len(buffer) == 1  # 이전 무시, 마지막만 남음
#     assert buffer[0]._value == "0xNEWVALUE"