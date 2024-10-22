import re
from typing import Any, Callable, Optional, Tuple

import click


class ParameterPair(click.ParamType):
    def __init__(
        self,
        value_types: Tuple[Callable, Callable] = (str, str),
        validator: Optional[Callable] = None,
    ) -> None:
        self.value_types = value_types
        self.validator = validator
        self.name = "PARAMETER_PAIR"

        # Build the complete regex
        self.pattern = re.compile(r"(?P<id>\w+)=((?P<value1>\w+),(?P<value2>\w+))")

    def convert(
        self, value: str, param: Any, ctx: click.Context
    ) -> Tuple[str, Any, Any]:
        if value is None:
            return None

        match = self.pattern.match(value)
        if not match:
            self.fail(
                f"Invalid pair format. Expected 'id=value,value2'",
                param,
                ctx,
            )

        id_part = match.group("id")
        val1 = match.group("value1")
        val2 = match.group("value2")

        try:
            # Convert values to specified types
            converted_val1 = self.value_types[0](val1.strip())
            converted_val2 = self.value_types[1](val2.strip())
        except (ValueError, TypeError):
            self.fail(
                f"Type conversion error: Expected {self.value_types[0].__name__} and "
                f"{self.value_types[1].__name__}. Got '{val1}' and '{val2}'",
                param,
                ctx,
            )

        # Run custom validator if provided
        if self.validator:
            try:
                self.validator(id_part, converted_val1, converted_val2)
            except Exception as e:
                self.fail(str(e), param, ctx)

        return (id_part, converted_val1, converted_val2)
