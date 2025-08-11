import glob
import os
import sys
from pathlib import Path
import re

from abc import ABC, abstractmethod
from file_handler import SimpleFileHandler, MultilineFileWriter

from policy import ignore_cmd_policy, merge_erase_policy
from ssd_validator import is_valid_address, is_valid_size, is_valid_value
from command import Command, ReadCommand, WriteCommand, EraseCommand

# ssd.py 파일이 있는 디렉토리 내 (프로젝트 루트) 절대 경로
_PROJECT_ROOT = Path(__file__).resolve().parent
BUFFER_DIR = str(_PROJECT_ROOT / "buffer")
OUTPUT_FILE = str(_PROJECT_ROOT / "ssd_output.txt")
TARGET_FILE = str(_PROJECT_ROOT / "ssd_nand.txt")

BLANK_STRING = "0x00000000"
ERROR_STRING = 'ERROR'
SSD_SIZE = 100
MIN_VALUE = 0x00000000
MAX_VALUE = 0xFFFFFFFF
MAX_COMMANDS = 5


class SSD:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._target_file_handler = MultilineFileWriter(SimpleFileHandler(TARGET_FILE))
            self._output_file_handler = SimpleFileHandler(OUTPUT_FILE)
            self.init_target_file()
            self.init_command_buffer()

    def init_command_buffer(self):
        buffer_dir = BUFFER_DIR
        os.makedirs(buffer_dir, exist_ok=True)

        for i in range(1, 6):
            exists = any(
                filename.startswith(f"{i}_")
                for filename in os.listdir(buffer_dir)
            )

            if not exists:
                file_path = os.path.join(buffer_dir, f"{i}_empty")
                with open(file_path, "w") as f:
                    f.write("")

    def init_target_file(self):
        if os.path.exists(TARGET_FILE) and self._target_validation():
            return
        self._target_file_handler.write_lines([BLANK_STRING for _ in range(SSD_SIZE)])
        return

    def read(self, address: int) -> int:
        if not self._check_lda_validation(address):
            return 1

        read_value = self._target_file_handler.read_specific_line(address)
        if not self._value_validation(read_value):
            return 1
        self._output_file_handler.write(read_value)
        return 0

    def _target_validation(self, filename=TARGET_FILE) -> bool:
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
                sanitized_lines = [line.rstrip('\n') for line in lines if line.strip()]

                if len(sanitized_lines) != SSD_SIZE:
                    return False

                for line in sanitized_lines:
                    if not self._value_validation(line):
                        return False
        except IOError:
            return False
        return True

    def _value_validation(self, read_value):
        if not read_value.startswith(('0x', '0X')) or len(read_value) != 10:
            self._output_file_handler.write(ERROR_STRING)
            return False
        try:
            read_value_hex = int(read_value, 16)
        except ValueError:
            self._output_file_handler.write(ERROR_STRING)
            return False
        if read_value_hex < MIN_VALUE or read_value_hex > MAX_VALUE:
            self._output_file_handler.write(ERROR_STRING)
            return False
        return True

    def _check_lda_validation(self, address) -> bool:
        if not isinstance(address, int) or not (0 <= address < SSD_SIZE):
            self._output_file_handler.write(ERROR_STRING)
            return False
        if (address < 0 or address >= SSD_SIZE):
            self._output_file_handler.write(ERROR_STRING)
            return False
        return True

    def write(self, address: int, value: str) -> None:
        if not isinstance(address, int) or not (0 <= address < SSD_SIZE):
            self._output_file_handler.write(ERROR_STRING)
            return
        lines = self._target_file_handler.read_all_lines()
        lines[address] = value  # 실제 업데이트 추가
        self._target_file_handler.write_lines(lines)

    def erase(self, address: int, size: int) -> None:  # erase 메서드 추가 (old 기반)
        if not isinstance(address, int) or not isinstance(size, int) or size > 10:
            self._output_file_handler.write(ERROR_STRING)
            return

        if not (0 <= address < SSD_SIZE) or size < 0 or (address + size > SSD_SIZE):
            self._output_file_handler.write(ERROR_STRING)
            return

        if size == 0:
            return

        lines = self._target_file_handler.read_all_lines()
        for i in range(address, address + size):
            lines[i] = BLANK_STRING
        self._target_file_handler.write_lines(lines)

    def _read_from_nand(self, lba: int) -> str:
        if not os.path.exists(TARGET_FILE):
            self._initialize_nand()

        with open(TARGET_FILE, 'r') as f:
            lines = f.readlines()

        if len(lines) < SSD_SIZE:
            lines += [BLANK_STRING + '\n'] * (SSD_SIZE - len(lines))

        if 0 <= lba < SSD_SIZE:
            value = lines[lba].strip()
            if re.match(r'^0x[0-9A-F]{8}$', value):
                return value
        return BLANK_STRING

    def _initialize_nand(self):
        with open(TARGET_FILE, 'w') as f:
            for _ in range(SSD_SIZE):
                f.write(BLANK_STRING + '\n')


class CommandInvoker:
    def __init__(self, ssd: SSD):
        self._commands = []
        self._ssd = ssd

        if not os.path.isdir(BUFFER_DIR):
            self.init_command_buffer()
            return

        def _slot_num(name: str) -> int:
            try:
                return int(name.split("_", 1)[0])
            except Exception:
                return 10**9  # 이상치 맨 뒤로

        for filename in sorted(os.listdir(BUFFER_DIR), key=_slot_num):
            parts = filename.split('_')
            if len(parts) < 2:
                continue  # 형식 불량 스킵

            # parts 예:
            #  ["1","empty"]
            #  ["1","W","0","0x00000001"]
            #  ["2","E","10","3"]

            kind = parts[1]
            if kind == 'empty':
                continue  # ✅ empty는 건너뛰고 계속 (예전엔 break라 문제였음)

            # 안전 파싱
            try:
                if kind == "W" and len(parts) >= 4:
                    addr = int(parts[2])
                    val  = parts[3]
                    self.add_command(WriteCommand(ssd, addr, val))
                elif kind == "E" and len(parts) >= 4:
                    addr = int(parts[2])
                    size = int(parts[3])
                    self.add_command(EraseCommand(ssd, addr, size))
                elif kind == "F":
                    self.flush()
                else:
                    # 모르는 포맷은 스킵 (테스트 안정성)
                    continue
            except Exception:
                # 파싱 실패 시 스킵 (로그 넣고 싶으면 여기서)
                continue

    def _sync_buffer_files(self) -> None:
        os.makedirs(BUFFER_DIR, exist_ok=True)

        # init
        for f in os.listdir(BUFFER_DIR):
            os.remove(os.path.join(BUFFER_DIR, f))
        for i in range(1, 6):
            open(os.path.join(BUFFER_DIR, f"{i}_empty"), "w").close()

        # cmd queue <-> filename 동기화
        for idx, cmd in enumerate(self._commands, 1):
            if isinstance(cmd, WriteCommand):
                fname = f"{idx}_W_{cmd._address}_{cmd._value}"
            elif isinstance(cmd, EraseCommand):
                fname = f"{idx}_E_{cmd._address}_{cmd._size}"
            else:
                continue

            old_path = os.path.join(BUFFER_DIR, f"{idx}_empty")
            new_path = os.path.join(BUFFER_DIR, fname)
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
            else:
                open(new_path, "w").close()

    def add_command(self, cmd: Command) -> None:
        # Read는 즉시 실행
        if isinstance(cmd, ReadCommand):
            cmd.execute()
            return

        # 1) 정책 적용 - 무효/중복 제거 및 기본 정리
        make_erase = lambda a, s: EraseCommand(self._ssd, a, s)

        new_queue = ignore_cmd_policy(
            queue=self._commands,
            incoming=cmd,
            WriteCls=WriteCommand,
            EraseCls=EraseCommand,
            make_erase=make_erase,
        )

        self._commands = new_queue

        # 용량 체크(정책 적용 후 길이 기준) - 넘치면 flush
        if len(self._commands) >= MAX_COMMANDS:
            self.flush()

        # 2) Erase면 병합 정책 적용, Write면 그대로 append
        if isinstance(cmd, EraseCommand):
            self._commands = merge_erase_policy(
                queue=self._commands,
                incoming_erase=cmd,
                EraseCls=EraseCommand,
                make_erase=make_erase,
                chunk_size=10,  # 기존 정책 유지
            )
        else:
            self._commands.append(cmd)

        # 3) 버퍼 파일과 동기화
        self._sync_buffer_files()

    def flush(self):
        for cmd in self._commands:
            cmd.execute()
        self._commands.clear()
        self.init_command_buffer()

    def num_commands(self):
        return len(self._commands)

    def init_command_buffer(self):
        buffer_dir = BUFFER_DIR
        os.makedirs(buffer_dir, exist_ok=True)

        for i in range(1, 6):
            prefix_pattern = os.path.join(buffer_dir, f"{i}_*")
            matched_files = glob.glob(prefix_pattern)

            target_path = os.path.join(buffer_dir, f"{i}_empty")

            if matched_files:
                os.rename(matched_files[0], target_path)
            else:
                with open(target_path, "w") as f:
                    f.write("")

    def get_buffer(self):
        return self._commands

    def fast_read(self, lba: int) -> str:
        for cmd in reversed(self._commands):
            if isinstance(cmd, WriteCommand) and cmd._address == lba:
                return cmd._value
            if isinstance(cmd, EraseCommand):
                if cmd._address <= lba < cmd._address + cmd._size:
                    return BLANK_STRING
        return self._ssd._read_from_nand(lba)


def main():
    if len(sys.argv) < 1:
        print("Usage: ssd.py <command> <arg1> [arg2]")
        sys.exit(1)

    cmd = sys.argv[1].upper()
    arg1 = sys.argv[2] if len(sys.argv) > 2 else None
    arg2 = sys.argv[3] if len(sys.argv) > 3 else None

    ssd = SSD()
    invoker = CommandInvoker(ssd)

    if cmd == "R":
        val = invoker.fast_read(int(arg1))
        ssd._output_file_handler.write(val)

    elif cmd == "W":
        if not is_valid_address(arg1) or not is_valid_value(arg2):
            ssd._output_file_handler.write("ERROR")
            print("ERROR W arguments are not valid")
            return

        invoker.add_command(WriteCommand(ssd, int(arg1), arg2))

    elif cmd == "E":
        if not is_valid_address(arg1) or not is_valid_size(arg1, arg2):
            ssd._output_file_handler.write("ERROR")
            print("ERROR E arguments are not valid")
            return

        invoker.add_command(EraseCommand(ssd, int(arg1), int(arg2)))

    elif cmd == "F":
        invoker.flush()

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
