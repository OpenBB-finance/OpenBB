"""Field validators"""

from typing import Optional


def check_single(v: Optional[str]) -> Optional[str]:
    """Check that string is a single value."""
    if v:
        if "," in v or ";" in v:
            raise ValueError("multiple values not allowed")
    return v


VALIDATORS = {"check_single": check_single}
