from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from abc import ABC, abstractmethod


class StorageBackend(Protocol):
    """SSD가 만족해야 하는 최소 인터페이스(순환참조 방지)."""

    def read(self, address: int) -> int: ...

    def write(self, address: int, value: str) -> None: ...

    def erase(self, address: int, size: int) -> None: ...


class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...


@dataclass(frozen=True, slots=True)
class ReadCommand(Command):
    ssd: StorageBackend
    _address: int

    def execute(self) -> None:
        self.ssd.read(self._address)


@dataclass(frozen=True, slots=True)
class WriteCommand(Command):
    ssd: StorageBackend
    _address: int
    _value: str

    def execute(self) -> None:
        self.ssd.write(self._address, self._value)


@dataclass(frozen=True, slots=True)
class EraseCommand(Command):
    ssd: StorageBackend
    _address: int
    _size: int

    def execute(self) -> None:
        self.ssd.erase(self._address, self._size)
