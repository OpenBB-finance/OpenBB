"""Field validators"""

from typing import Optional


def check_single(field: str, value: Optional[str]) -> Optional[str]:
    """Check that string is a single value."""
    if value:
        if "," in value or ";" in value:
            raise ValueError(f"multiple values not allowed for field '{field}'")
    return value


VALIDATORS = {"check_single": check_single}
