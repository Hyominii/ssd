from typing import Any, Callable, List, Type

MakeErase = Callable[[int, int], Any]

def ignore_cmd_policy(
    queue: List[Any],
    incoming: Any,
    WriteCls: Type[Any],
    EraseCls: Type[Any],
    make_erase: MakeErase,
) -> List[Any]:
    """
    새 명령(incoming) 추가 전에, 무효/중복 명령을 제거하거나(Write),
    이전 Erase를 적절히 제거(완전 포함)(Erase)

    - Write:
        * 같은 LBA의 이전 Write 제거
        * Write가 기존 Erase의 시작/끝과 맞닿으면 해당 Erase를 축소
          (가운데에 박히는 케이스는 기존 정책대로 유지)
    - Erase:
        * 범위에 포함된 Write 제거
        * 자신이 완전히 감싸는 이전 Erase 제거
    """
    new_q: List[Any] = []
    # Write Cmd 추가시
    if isinstance(incoming, WriteCls):
        w_addr = getattr(incoming, "_address")
        for cmd in queue:
            if isinstance(cmd, WriteCls):
                if getattr(cmd, "_address") == w_addr:
                    continue
                new_q.append(cmd)
            elif isinstance(cmd, EraseCls):
                s = getattr(cmd, "_address")
                sz = getattr(cmd, "_size")
                e = s + sz

                if s <= w_addr < e:
                    if w_addr == s:
                        s2 = s + 1
                        sz2 = e - s2
                        if sz2 > 0:
                            new_q.append(make_erase(s2, sz2))
                    elif w_addr == e - 1:
                        sz2 = (e - 1) - s
                        if sz2 > 0:
                            new_q.append(make_erase(s, sz2))
                    else:
                        new_q.append(cmd)
                else:
                    new_q.append(cmd)
            else:
                new_q.append(cmd)
        return new_q

    # Erase cmd 추가 시
    if isinstance(incoming, EraseCls):
        s_new = getattr(incoming, "_address")
        e_new = s_new + getattr(incoming, "_size")
        for cmd in queue:
            if isinstance(cmd, WriteCls):
                w_addr = getattr(cmd, "_address")
                if s_new <= w_addr < e_new:
                    continue
                new_q.append(cmd)
            elif isinstance(cmd, EraseCls):
                s = getattr(cmd, "_address")
                e = s + getattr(cmd, "_size")
                if s_new <= s and e <= e_new:
                    continue
                new_q.append(cmd)
            else:
                new_q.append(cmd)
        return new_q

    return list(queue)


def merge_erase_policy(
    queue: List[Any],
    incoming_erase: Any,
    EraseCls: Type[Any],
    make_erase: MakeErase,
    chunk_size: int,
) -> List[Any]:
    """
    새 Erase를 큐에 넣기 전에, 기존의 겹치거나 인접한 Erase들과 하나로 합친 뒤
    chunk_size 단위로 쪼개서 재배치.
    """
    s = getattr(incoming_erase, "_address")
    e = s + getattr(incoming_erase, "_size")

    survived: List[Any] = []

    def overlap_or_adjacent(a1: int, a2: int, b1: int, b2: int) -> bool:
        return not (a2 < b1 or b2 < a1) or a2 == b1 or b2 == a1

    for cmd in queue:
        if isinstance(cmd, EraseCls):
            s2 = getattr(cmd, "_address")
            e2 = s2 + getattr(cmd, "_size")
            if overlap_or_adjacent(s, e, s2, e2):
                s = min(s, s2)
                e = max(e, e2)
            else:
                survived.append(cmd)
        else:
            survived.append(cmd)

    cur = s
    while cur < e:
        chunk = min(chunk_size, e - cur)
        survived.append(make_erase(cur, chunk))
        cur += chunk

    return survived