from functools import wraps
from typing import Any, Callable, Optional, TypeVar, overload

from pkg_resources import parse_version
from pydantic import VERSION
from typing_extensions import ParamSpec


def get_validate_call() -> Callable:
    """Pydantic 2.5.0 changed location of validate_call, so we check and import"""
    if parse_version(VERSION) < parse_version("2.5.0"):
        from pydantic.validate_call import validate_call
    else:
        from pydantic import validate_call
    return validate_call


validate_call = get_validate_call()

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
