import glob
import os
import sys
from pathlib import Path
import re

from abc import ABC, abstractmethod
from file_handler import SimpleFileHandler, MultilineFileWriter

# ssd.py 파일이 있는 디렉토리 내 (프로젝트 루트) 절대 경로
_PROJECT_ROOT = Path(__file__).resolve().parent
BUFFER_DIR   = str(_PROJECT_ROOT / "buffer")   # ← 여기만 변경
OUTPUT_FILE  = str(_PROJECT_ROOT / "ssd_output.txt")
TARGET_FILE  = str(_PROJECT_ROOT / "ssd_nand.txt")

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
        os.makedirs(buffer_dir, exist_ok=True)  # 이미 있어도 에러 안 나게

        # 2. 파일 생성
        for i in range(1, 6):
            # 해당 i로 시작하는 파일이 이미 존재하는지 확인
            exists = any(
                filename.startswith(f"{i}_")
                for filename in os.listdir(buffer_dir)
            )

            if not exists:
                file_path = os.path.join(buffer_dir, f"{i}_empty")
                with open(file_path, "w") as f:
                    f.write("")

    def init_target_file(self):
        # SSD init시에 nand.txt파일이 올바른 포멧인지 확인합니다
        if os.path.exists(TARGET_FILE) and self._target_validation():
            return
        # 파일이 없으면 100개의 BLANK VALUE 생성
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

                # 모든 라인에서 개행 문자를 제거한 후 유효한 라인만 필터링합니다.
                sanitized_lines = [line.rstrip('\n') for line in lines if line.strip()]

                # 개행 문자를 제거한 라인 수가 SSD_SIZE와 일치하는지 확인합니다.
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


class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    def set_path(self, file_path: str):
        self.path = file_path

    def rename_buffer(self, buffer_num, cmd, address, size):
        path = f'{buffer_num}_{cmd}_{address}_{size}'
        self.set_path(path)
        for filename in os.listdir(BUFFER_DIR):
            if filename.startswith(f'{buffer_num}'):
                old_path = os.path.join(BUFFER_DIR, filename)
                new_path = os.path.join(BUFFER_DIR, path)
                os.rename(old_path, new_path)
                # print(f"Renamed {filename} -> {}2_string")
                break  # ✅ 하나만 처리하고 끝냄


class ReadCommand(Command):
    def __init__(self, ssd: SSD, address: int):
        self.ssd = ssd
        self._address = address

    def execute(self):
        self.ssd.read(self._address)


class WriteCommand(Command):
    def __init__(self, ssd: SSD, address: int, value: str, buffer_num: int):
        self.ssd = ssd
        self._address = address
        self._value = value
        self.rename_buffer(buffer_num, 'W', address, value)

    def execute(self):
        self.ssd.write(self._address, self._value)


class EraseCommand(Command):
    def __init__(self, ssd: SSD, address: int, size: int, buffer_num: int):
        self.ssd = ssd
        self._address = address
        self._size = size  # 오타 수정
        self.rename_buffer(buffer_num, 'E', address, size)

    def execute(self):
        self.ssd.erase(self._address, self._size)  # 인자 전달 추가


class CommandInvoker:
    def __init__(self, ssd: SSD):
        self._commands = []
        self._ssd = ssd
        self.init_command_buffer()  # forced init buffer

        if not os.path.isdir(BUFFER_DIR):
            self.init_command_buffer()
            return

        for filename in os.listdir(BUFFER_DIR):
            # file_path = os.path.join(BUFFER_DIR, filename)
            cmd_arg = filename.split('_')
            cmd = cmd_arg[1]
            if cmd == 'empty':
                break

            arg1 = cmd_arg[2]
            arg2 = cmd_arg[3]

            if cmd_arg[1] == "W":
                self.add_command(WriteCommand(ssd, int(arg1), arg2, self.num_commands() + 1))
            elif cmd_arg[1] == "E":
                self.add_command(EraseCommand(ssd, int(arg1), int(arg2), self.num_commands() + 1))
            elif cmd_arg[1] == "F":
                self.flush()
            else:
                print(f"Unknown command: {cmd}")
                sys.exit(1)

    def _sync_buffer_files(self) -> None:
        os.makedirs(BUFFER_DIR, exist_ok=True)
        for f in os.listdir(BUFFER_DIR):
            os.remove(os.path.join(BUFFER_DIR, f))
        for i in range(1, 6):
            open(os.path.join(BUFFER_DIR, f"{i}_empty"), "w").close()
        for idx, cmd in enumerate(self._commands, 1):
            if isinstance(cmd, WriteCommand):
                cmd.rename_buffer(idx, 'W', cmd._address, cmd._value)
            elif isinstance(cmd, EraseCommand):
                cmd.rename_buffer(idx, 'E', cmd._address, cmd._size)

    def add_command(self, cmd: Command) -> None:
        self.ignore_cmd(cmd) #신규 커맨드 대비해 지울수 있는 기존 커맨드 제거

        if isinstance(cmd, ReadCommand):  # Read 즉시 실행
            cmd.execute()
            return  # 버퍼에 추가 안 함

        if len(self._commands) >= MAX_COMMANDS:
            self.flush()

        if isinstance(cmd, EraseCommand):
            merged = self._merge_erase_if_possible(cmd)
            if merged: self._commands.extend(merged)
            else : self._commands.append(cmd)
        else : self._commands.append(cmd)

        self._sync_buffer_files()

    def _merge_erase_if_possible(self, incoming_cmd: EraseCommand) -> list[EraseCommand] | None:
        # range of the new (incoming) erase request
        incoming_start_addr = incoming_cmd._address
        incoming_end_addr = incoming_start_addr + incoming_cmd._size

        # track commands that will be removed because they merge with the incoming one
        indices_to_remove: list[int] = []

        # running merged range (will expand if we find overlaps/adjacency)
        merged_start_addr = incoming_start_addr
        merged_end_addr = incoming_end_addr

        def _has_write_between(start_idx: int, union_start: int, union_end: int) -> bool:
            # 기존 Erase(start_idx) 이후 ~ 현재 버퍼 끝까지 사이에,
            # 합집합 범위[union_start, union_end) 를 쓰는 Write 가 있으면 True
            for j in range(start_idx + 1, len(self._commands)):
                mid = self._commands[j]
                if isinstance(mid, WriteCommand) and union_start <= mid._address < union_end:
                    return True
            return False

        for idx, queued_cmd in enumerate(self._commands):
            if not isinstance(queued_cmd, EraseCommand):
                continue

            queued_start_addr = queued_cmd._address
            queued_end_addr = queued_start_addr + queued_cmd._size

            # overlap or directly adjacent?
            has_overlap_or_adjacent = (
                    queued_end_addr == merged_start_addr
                    or merged_end_addr == queued_start_addr
                    or (queued_start_addr <= merged_start_addr < queued_end_addr)
                    or (merged_start_addr <= queued_start_addr < merged_end_addr)
            )

            # if has_overlap_or_adjacent:
            #     merged_start_addr = min(merged_start_addr, queued_start_addr)
            #     merged_end_addr = max(merged_end_addr, queued_end_addr)
            #     indices_to_remove.append(idx)

            if has_overlap_or_adjacent:
                # 중간에 해당 합집합 범위를 건드는 Write 가 있으면 merge 금지
                union_start = min(merged_start_addr, queued_start_addr)
                union_end   = max(merged_end_addr, queued_end_addr)
                if _has_write_between(idx, union_start, union_end):
                    continue
                merged_start_addr = union_start
                merged_end_addr   = union_end
                indices_to_remove.append(idx)

        # nothing merged → caller should append the incoming command as-is
        if not indices_to_remove:
            return None

        # drop all commands that we merged with
        for idx in reversed(indices_to_remove):
            del self._commands[idx]

        # create replacement commands (split into chunks ≤ 10 lines each)
        total_merged_size = merged_end_addr - merged_start_addr
        replacement_cmds: list[EraseCommand] = []
        current_addr = merged_start_addr
        remaining_size = total_merged_size

        while remaining_size > 0:
            chunk_size = min(10, remaining_size)
            replacement_cmds.append(
                EraseCommand(incoming_cmd.ssd, current_addr, chunk_size, 0)
            )
            current_addr += chunk_size
            remaining_size -= chunk_size

        return replacement_cmds

    def flush(self):
        for cmd in self._commands:
            cmd.execute()
        self._commands.clear()
        self.init_command_buffer()

    def num_commands(self):
        return len(self._commands)

    def init_command_buffer(self):
        buffer_dir = BUFFER_DIR
        os.makedirs(buffer_dir, exist_ok=True)  # 이미 있어도 에러 안 나게

        # 2. 파일 생성
        for i in range(1, 6):
            prefix_pattern = os.path.join(buffer_dir, f"{i}_*")
            matched_files = glob.glob(prefix_pattern)

            target_path = os.path.join(buffer_dir, f"{i}_empty")

            if matched_files:
                # 첫 번째로 매칭된 파일만 이름 변경
                os.rename(matched_files[0], target_path)
            else:
                # 파일 새로 생성
                with open(target_path, "w") as f:
                    f.write("")

    def get_buffer(self):
        return self._commands

    def ignore_cmd(self, new_cmd: Command):
        """
        버퍼에 이미 존재하는 불필요한 명령을 제거.
        - Write  : 같은 LBA에 대한 이전 Write 모두 제거
                   (추가) 같은 LBA의 단일 슬롯 Erase(size=1)도 불필요하므로 제거
        - Erase  : (a) 지우려는 범위에 포함된 모든 Write 제거
                   (b) 완전히 포함되는 이전 Erase 제거
        """
        def _erase_range(cmd):
            return range(cmd._address, cmd._address + cmd._size)

        removed_idx = []
        for idx, old in enumerate(self._commands):
            if isinstance(new_cmd, WriteCommand):
                # if isinstance(old, WriteCommand) and old._address == new_cmd._address:
                #     removed_idx.append(idx)

                # 같은 LBA의 이전 Write 제거
                if isinstance(old, WriteCommand) and old._address == new_cmd._address:
                    removed_idx.append(idx)
                # 같은 LBA의 단일 슬롯 Erase(size=1)는 Write로 덮이므로 제거
                elif isinstance(old, EraseCommand) and old._size == 1 and old._address == new_cmd._address:
                    removed_idx.append(idx)

            elif isinstance(new_cmd, EraseCommand):
                n_range = _erase_range(new_cmd)

                # (a) 기존 Write 가 지워질 범위에 포함
                if isinstance(old, WriteCommand) and old._address in n_range:
                    removed_idx.append(idx)

                # # (b) 기존 Erase 가 새 Erase 범위에 완전히 포함
                # elif isinstance(old, EraseCommand):
                #     o_range = _erase_range(old)
                #     if o_range.start >= n_range.start and o_range.stop <= n_range.stop:
                #         removed_idx.append(idx)

                # (b) 기존 Erase 가 새 Erase 범위에 완전히 포함
                elif isinstance(old, EraseCommand):
                    o_range = _erase_range(old)
                    if o_range.start >= n_range.start and o_range.stop <= n_range.stop:
                        removed_idx.append(idx)
                    else:
                        # (c) 기존 Erase 의 '실효 범위'가 신규 Erase 로 모두 대체되면 제거
                        #     실효 범위 = 기존 Erase 범위 - (그 이후~현재 사이 Write 가 쓴 주소)
                        writes_between = {
                            c._address for c in self._commands[idx+1:]
                            if isinstance(c, WriteCommand) and c._address in o_range
                        }
                        effective_after_writes = {a for a in o_range if a not in writes_between}
                        if not effective_after_writes:
                            # 전부 Write 로 가려져 더 이상 의미 없음
                            removed_idx.append(idx)
                        elif all(n_range.start <= a < n_range.stop for a in effective_after_writes):
                            # 남은 실효 범위가 모두 신규 Erase 로 커버되므로 제거
                            removed_idx.append(idx)

        for i in sorted(removed_idx, reverse=True):
            old = self._commands.pop(i)

    # def fast_read(self, lba: int) -> str:
    #     # 최근 명령어 우선으로 역순 스캔
    #     for cmd in reversed(self._commands):
    #         if cmd['type'] == 'W':
    #             if cmd['lba'] == lba:
    #                 return cmd['value']  # 최신 쓰기 값
    #         elif cmd['type'] == 'E':
    #             start = cmd['start_lba']
    #             end = start + cmd['size']
    #             if start <= lba < end:
    #                 return BLANK_STRING  # 삭제됨
    #
    #     return self._ssd._read_from_nand(lba)  # 실제 NAND 읽기로 후퇴

    def fast_read(self, lba: int) -> str:
        for cmd in reversed(self._commands):
            if isinstance(cmd, WriteCommand) and cmd._address == lba:
                return cmd._value
            if isinstance(cmd, EraseCommand):
                if cmd._address <= lba < cmd._address + cmd._size:
                    return BLANK_STRING
        return self._ssd._read_from_nand(lba)


    def fast_read(self, lba: int) -> str:
        # 최근 명령어 우선으로 역순 스캔
        for cmd in reversed(self._commands):
            if cmd['type'] == 'W':
                if cmd['lba'] == lba:
                    return cmd['value']  # 최신 쓰기 값
            elif cmd['type'] == 'E':
                start = cmd['start_lba']
                end = start + cmd['size']
                if start <= lba < end:
                    return BLANK_STRING  # 삭제됨

        return self._ssd._read_from_nand(lba)  # 실제 NAND 읽기로 후퇴


def main():
    if len(sys.argv) < 2:
        print("Usage: ssd.py <command> <arg1> [arg2]")
        sys.exit(1)

    cmd = sys.argv[1].upper()
    arg1 = sys.argv[2] if len(sys.argv) > 2 else None
    arg2 = sys.argv[3] if len(sys.argv) > 3 else None

    ssd = SSD()
    invoker = CommandInvoker(ssd)

    # if cmd == "R":
    #     # invoker.add_command(ReadCommand(ssd, int(arg1)))
    #     invoker.flush()
    #     ReadCommand(ssd, int(arg1)).execute()
    if cmd == "R":
        val = invoker.fast_read(int(arg1))
        ssd._output_file_handler.write(val)
    elif cmd == "W":
        invoker.add_command(WriteCommand(ssd, int(arg1), arg2, invoker.num_commands() + 1))
    elif cmd == "E":
        invoker.add_command(EraseCommand(ssd, int(arg1), int(arg2), invoker.num_commands() + 1))
    elif cmd == "F":
        invoker.flush()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

    # flush
    # invoker.flush()


if __name__ == "__main__":
    main()
