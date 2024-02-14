"""Field validators"""

from typing import Optional

from openbb_core.app.model.abstract.error import OpenBBError


def check_single_value(
    value: Optional[str], message: Optional[str] = None
) -> Optional[str]:
    """Check that string is a single value."""
    if value and ("," in value or ";" in value):
        raise OpenBBError(message if message else "multiple values not allowed")
    return value
