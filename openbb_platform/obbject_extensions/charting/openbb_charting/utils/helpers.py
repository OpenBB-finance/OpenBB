"""Helper functions for charting."""

from inspect import getmembers, getsource, isfunction
from typing import List

from openbb_charting import charting_router


def get_charting_functions() -> List[str]:
    """Discover charting functions."""
    implemented_functions = []

    for name, obj in getmembers(charting_router, isfunction):
        if (
            obj.__module__ == charting_router.__name__
            and not name.startswith("_")
            and "NotImplementedError" not in getsource(obj)
        ):
            implemented_functions.append(name)

    return implemented_functions
