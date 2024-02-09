"""Field validators"""


def check_single(v: str) -> str:
    """Check that string is not comma-separated string"""
    if "," in v:
        raise ValueError("multiple values are not allowed")
    return v
