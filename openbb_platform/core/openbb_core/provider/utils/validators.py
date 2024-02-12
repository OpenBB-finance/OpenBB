"""Field validators"""

from typing import Any, Callable, NewType, Optional

V = NewType("V", Callable[[str, Any], Any])


def check_singles(field: str, value: Optional[str]) -> Optional[str]:
    """Check that string is a single value."""
    if value and ("," in value or ";" in value):
        raise ValueError(f"multiple values not allowed for field '{field}'")
    return value
