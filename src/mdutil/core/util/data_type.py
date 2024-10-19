from dataclasses import astuple, dataclass
from typing import Tuple


@dataclass
class Size:
    height: int
    width: int

    def __mul__(self, other):
        if isinstance(other, Size):
            return Size(self.height * other.height, self.width * other.width)
        return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, Size):
            return Size(self.height // other.height, self.width // other.width)
        return NotImplemented

    def __iter__(self) -> Tuple[int, int]:
        return iter(astuple(self))

    def to_tuple(self) -> Tuple[int, int]:
        return astuple(self)


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Rect:
    x: int
    y: int
    width: int
    height: int
