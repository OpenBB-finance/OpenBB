"""Field validators"""

from typing import Any, Callable, Optional, TypeVar

V = TypeVar("V", Callable[[str, Any], Any])


def check_single(field: str, value: Optional[str]) -> Optional[str]:
    """Check that string is a single value."""
    if value and ("," in value or ";" in value):
        raise ValueError(f"multiple values not allowed for field '{field}'")
    return value
