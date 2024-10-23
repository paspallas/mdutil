from typing import Any, Dict, List

from .property import CustomProperty


class Object:
    def __init__(
        self,
        name: str,
        id_: int,
        width: int,
        height: int,
        x: float,
        y: float,
        properties: List[CustomProperty] = None,
    ) -> None:
        self.name = name
        self.id = id_
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.properties = properties or []

    def add_property(self, property: CustomProperty) -> None:
        self.properties.append(property)

    def __repr__(self) -> str:
        description = [
            f"Object(name={self.name}, id={self.id}, x={self.x}, y={self.y})"
        ]
        for prop in self.properties:
            description.append(f"     *{str(prop)}")

        return "\n".join(description)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Object":
        properties = [
            CustomProperty.from_dict(prop) for prop in data.get("properties", [])
        ]

        return cls(
            name=data.get("name", ""),
            id_=data.get("id", 0),
            width=data.get("width", 0),
            height=data.get("height", 0),
            x=data.get("x", 0),
            y=data.get("y", 0),
            properties=properties,
        )
