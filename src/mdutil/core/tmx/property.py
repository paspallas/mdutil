from typing import Any, Dict

from mdutil.core.exceptions import PropertyError


class CustomProperty:
    def __init__(self, name: str, value: Any, value_type: str) -> None:
        self.name = name
        self.value = self._convert_value(value, value_type)
        self.value_type = value_type

    def _convert_value(self, value: Any, value_type: str) -> Any:
        if value_type in ["int", "object"]:
            return int(value)
        elif value_type == "float":
            return float(value)
        elif value_type == "bool":
            return bool(value)
        elif value_type in ["string", "file"]:
            return str(value)
        elif value_type == "color":
            return int(value.lstrip("#"), 16)
        else:
            raise PropertyError(f"Unsupported property type: {value_type}")

    def __repr__(self) -> str:
        val = self.value if self.value_type != "color" else hex(self.value)
        return f" Property(name={self.name}, type={self.value_type}, val={val})"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CustomProperty":
        return cls(
            name=data.get("name", ""),
            value=data.get("value", 0),
            value_type=data.get("type", "int"),
        )
