from typing import Any, Tuple


def smart_repr(obj: Any, exclude: Tuple[str] = ()) -> str:
    """Create a string representation of an object, including only attributes
    that have actual values (not None, empty strings, empty lists,...)

    Args:
        obj (Any): The object to create a representation for
        exclude (Tuple[str]): Tuple of attributes to exclude by name

    Returns:
        str: A string representation of the object
    """

    # Get all public attributes
    attributes = {
        name: getattr(obj, name) for name in dir(obj) if not name.startswith("_")
    }

    # Perform filtering
    valid_attrs = []
    for name, val in attributes.items():
        # Skip methods and properties
        if callable(val) or isinstance(val, property):
            continue

        # Skip empty values
        if name in exclude:
            continue
        if val is None:
            continue
        if isinstance(val, (list, dict, set, tuple, str, int, float, bool)) and not val:
            continue

        # Format the value
        if isinstance(val, str):
            formatted_val = f"{val}"
        else:
            formatted_val = str(val)

        valid_attrs.append(f"{name}={formatted_val}")

    attrs_str = ", ".join(valid_attrs)
    return f"{obj.__class__.__name__}({attrs_str})"
