from dataclasses import astuple, dataclass
from typing import Dict, Tuple


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
    x: float
    y: float

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "Point":
        return cls(data["x"], data["y"])


@dataclass
class Rect:
    x: int
    y: int
    width: int
    height: int
