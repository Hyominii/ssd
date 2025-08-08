import pytest
import pytest_mock


def test_pass_ignore_command_write():
    cases = [
        {
            "original": {
                "1": "W_0_0x00000000",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "W_1_0x00000001",
            "changed": {
                "1": "W_0_0x00000001",
                "2": "W_1_0x00000001",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
        {
            "original": {
                "1": "E_0_1",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "W_1_0x00000001",
            "changed": {
                "1": "E_0_1",
                "2": "W_1_0x00000001",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        }
    ]


def test_ignore_command_write():
    cases = [
        {
            "original": {
                "1": "W_0_0x00000000",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "W_0_0x00000001",
            "changed": {
                "1": "W_0_0x00000001",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
        {
            "original": {
                "1": "E_0_1",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "W_0_0x00000001",
            "changed": {
                "1": "W_0_0x00000001",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        }
    ]


def test_pass_ignore_command_erase():
    cases = [
        {
            "original": {
                "1": "W_0_0x00000005",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_1_3",
            "changed": {
                "1": "W_0_0x00000005",
                "2": "E_1_3",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
        {
            "original": {
                "1": "E_0_2",
                "2": "W_5_0x00001234",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_6_3",
            "changed": {
                "1": "E_0_2",
                "2": "W_5_0x00001234",
                "3": "E_6_3",
                "4": "empty",
                "5": "empty",
            },
        },
        {
            "original": {
                "1": "E_0_2",
                "2": "W_0_0x00001234",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_3_3",
            "changed": {
                "1": "E_0_2",
                "2": "W_0_0x00001234",
                "3": "E_3_3",
                "4": "empty",
                "5": "empty",
            },
        },
    ]


def test_ignore_command_erase():
    cases = [
        {
            "original": {
                "1": "W_0_0x00000005",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_0_3",
            "changed": {
                "1": "E_0_3",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
        {
            "original": {
                "1": "E_0_2",
                "2": "W_5_0x00001234",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_0_3",
            "changed": {
                "1": "W_5_0x00001234",
                "2": "E_0_3",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
        {
            "original": {
                "1": "E_0_2",
                "2": "W_0_0x00001234",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_0_3",
            "changed": {
                "1": "E_0_3",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
    ]

def test_pass_merge_erase():
    cases = [
        {
            "original": {
                "1": "E_0_3",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_4_3",
            "changed": {
                "1": "E_0_3",
                "2": "E_4_3",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
    ]

def test_merge_erase():
    cases = [
        # 기존에 erase size가 0일 때
        {
            "original": {
                "1": "E_0_0",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_0_3",
            "changed": {
                "1": "E_0_3",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
        # 기존에 erase size가 새로운 input erase의 부분 집합일 때
        {
            "original": {
                "1": "E_0_1",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_0_3",
            "changed": {
                "1": "E_0_3",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
        # 기존에 erase size가 새로운 input erase과 동일할 때
        {
            "original": {
                "1": "E_0_3",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_0_3",
            "changed": {
                "1": "E_0_3",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
        # 새로운 input erase이 기존 erase 명령의 부분 집합일 때
        {
            "original": {
                "1": "E_0_5",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_0_3",
            "changed": {
                "1": "E_0_5",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
        # 기존 erase명령과 새로운 erase명령이 한 개 겹칠 때
        {
            "original": {
                "1": "E_0_5",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_4_3",
            "changed": {
                "1": "E_0_7",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
        # 기존 erase명령과 새로운 erase명령이 이어질 때
        {
            "original": {
                "1": "E_0_5",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_5_3",
            "changed": {
                "1": "E_0_8",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
        # 기존 erase명령과 새로운 erase명령이 이어지고 중간에 W명령이 새로운 erase에 ignore되는 경우
        {
            "original": {
                "1": "E_0_5",
                "2": "W_5_0x00001234",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_5_3",
            "changed": {
                "1": "E_0_8",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
        # 기존 erase명령과 새로운 erase명령이 겹치고 size가 10을 넘은 경우
        {
            "original": {
                "1": "E_0_5",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_4_10",
            "changed": {
                "1": "E_0_10",
                "2": "E_10_4",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
        # 기존 erase명령과 새로운 erase명령이 이어지고 size가 10을 넘은 경우
        {
            "original": {
                "1": "E_0_5",
                "2": "empty",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
            "new_input": "E_5_10",
            "changed": {
                "1": "E_0_10",
                "2": "E_10_5",
                "3": "empty",
                "4": "empty",
                "5": "empty",
            },
        },
    ]
