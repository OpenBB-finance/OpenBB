"""Field validators"""

from typing import Optional


def check_single(v: Optional[str]) -> Optional[str]:
    """Check that string is a single value."""
    if v:
        if "," in v:
            raise ValueError("comma-separated values are not allowed")
        if ";" in v:
            raise ValueError("semicolon-separated values are not allowed")
    return v


VALIDATORS = {"check_single": check_single}
