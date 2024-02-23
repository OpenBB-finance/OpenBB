"""Decorators for the OpenBB Platform static assets."""

from functools import wraps
from typing import Any, Callable, Optional, TypeVar, overload

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.env import Env
from pydantic import validate_call
from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


@overload
def validate(func: Callable[P, R]) -> Callable[P, R]:
    pass


@overload
def validate(**dec_kwargs) -> Callable[P, R]:
    pass


def validate(
    func: Optional[Callable[P, R]] = None,
    **dec_kwargs,
) -> Any:
    """Validate function calls."""

    def decorated(f: Callable[P, R]):
        """Decorated function."""

        @wraps(f)
        def wrapper(*f_args, **f_kwargs):
            return validate_call(f, **dec_kwargs)(*f_args, **f_kwargs)

        return wrapper

    return decorated if func is None else decorated(func)


def exception_handler(func: Callable[P, R]) -> Callable[P, R]:
    """Handle exceptions, attempting to focus on the last call from the traceback."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if Env().DEBUG_MODE:
                raise
            raise OpenBBError(
                f"\nType -> {e.__class__.__name__}\n\nDetail -> {str(e)}"
            ) from None

    return wrapper
