from enum import Enum, auto
from typing import Any, Dict, List

from mdutil.core.util import Point, smart_repr

from .property import CustomProperty


class ObjectType(Enum):
    RECT = auto()
    ELLIPSE = auto()
    POLYLINE = auto()


class Object:
    def __init__(
        self,
        name: str,
        id_: int,
        class_: str,
        width: int,
        height: int,
        x: float,
        y: float,
        type_: ObjectType,
        properties: List[CustomProperty] = None,
        polyline: List[Point] = None,
    ) -> None:
        self.name = name
        self.id = id_
        self.class_ = class_
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.type = type_
        self.properties = properties or []
        self.polyline = polyline or []

    def add_property(self, property: CustomProperty) -> None:
        self.properties.append(property)

    def __repr__(self) -> str:
        description = [smart_repr(self, exclude=("properties", "polyline"))]
        for prop in self.properties:
            description.append(f"     *{str(prop)}")

        return "\n".join(description)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Object":
        properties = [
            CustomProperty.from_dict(prop) for prop in data.get("properties", [])
        ]

        polyline = [Point.from_dict(point) for point in data.get("polyline", [])]

        if "polyline" in data:
            objtype = ObjectType.POLYLINE
        elif "ellipse" in data:
            objtype = ObjectType.ELLIPSE
        else:
            objtype = ObjectType.RECT

        return cls(
            name=data.get("name", ""),
            id_=data.get("id", 0),
            class_=data.get("type", ""),
            width=data.get("width", 0),
            height=data.get("height", 0),
            x=data.get("x", 0),
            y=data.get("y", 0),
            type_=objtype,
            properties=properties,
            polyline=polyline,
        )
