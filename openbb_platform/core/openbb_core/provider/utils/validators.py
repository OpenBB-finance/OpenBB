"""Field validators"""

from typing import Any, Callable, NewType, Optional

V = NewType("V", Callable[[str, Any], Any])


def check_single_value(value: Optional[str]) -> Optional[str]:
    """Check that string is a single value."""
    if value and ("," in value or ";" in value):
        raise ValueError("multiple values not allowed")
    return value
