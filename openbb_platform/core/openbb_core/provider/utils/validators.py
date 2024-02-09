"""Field validators"""

from typing import Optional


def check_single(v: Optional[str]) -> Optional[str]:
    """Check that string is not comma-separated string"""
    if v and "," in v:
        raise ValueError("comma-separated values are not allowed")
    return v


VALIDATORS = {"check_single": check_single}
