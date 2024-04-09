"""Decorators for the OpenBB Platform static assets."""

from functools import wraps
from typing import Any, Callable, Optional, TypeVar, overload

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.env import Env
from pydantic import ValidationError, validate_call
from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


@overload
def validate(func: Callable[P, R]) -> Callable[P, R]:
    pass


@overload
def validate(**dec_kwargs) -> Callable[[Callable[P, R]], Callable[P, R]]:
    pass


def validate(
    func: Optional[Callable[P, R]] = None,
    **dec_kwargs,
) -> Any:
    """Validate function calls."""

    def decorated(f: Callable[P, R]):
        """Use for decorating functions."""

        @wraps(f)
        def wrapper(*f_args, **f_kwargs):
            return validate_call(f, **dec_kwargs)(*f_args, **f_kwargs)

        return wrapper

    return decorated if func is None else decorated(func)


def exception_handler(func: Callable[P, R]) -> Callable[P, R]:
    """Handle exceptions, attempting to focus on the last call from the traceback."""

    @wraps(func)
    def wrapper(*f_args, **f_kwargs):
        try:
            return func(*f_args, **f_kwargs)
        except (ValidationError, Exception) as e:
            # If the DEBUG_MODE is enabled, raise the exception with complete traceback
            if Env().DEBUG_MODE:
                raise

            # Get the last traceback object from the exception
            tb = e.__traceback__
            if tb:
                while tb.tb_next is not None:
                    tb = tb.tb_next

            if isinstance(e, ValidationError):
                error_list = []

                validation_error = f"{e.error_count()} validations errors in {e.title}"
                for error in e.errors():
                    arg = ".".join(map(str, error["loc"]))
                    arg_error = f"Arg {arg} ->\n"
                    error_details = (
                        f"{error['msg']} "
                        f"[validation_error_type={error['type']}, "
                        f"input_type={type(error['input']).__name__}, "
                        f"input_value={error['input']}]\n"
                    )
                    url = error.get("url")
                    error_info = (
                        f"    For further information visit {url}\n" if url else ""
                    )
                    error_list.append(arg_error + error_details + error_info)

                error_list.insert(0, validation_error)
                error_str = "\n".join(error_list)

                raise OpenBBError(
                    f"\nType -> ValidationError \n\nDetails -> {error_str}"
                ).with_traceback(tb) from None

            # If the error is not a ValidationError, then it is a generic exception
            error_type = getattr(e, "original", e).__class__.__name__
            raise OpenBBError(
                f"\nType -> {error_type}\n\nDetail -> {str(e)}"
            ).with_traceback(tb) from None

    return wrapper
