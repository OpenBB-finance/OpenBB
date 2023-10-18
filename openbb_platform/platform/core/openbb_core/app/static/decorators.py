from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, overload

from pydantic.validate_call import validate_call
from typing_extensions import ParamSpec

from inspect import signature

P = ParamSpec("P")
R = TypeVar("R")


def listify(f_sig, f_args, f_kwargs, listify_params) -> Dict[str, Any]:
    """Converts function arguments to list if they are in listify_params."""

    # remove the self argument
    f_args = list(f_args[1:])
    f_kwargs = dict(f_kwargs)
    f_args.extend(f_kwargs.values())

    # get the function parameters
    params = f_sig.parameters
    params = {name: param for name, param in params.items() if name != "self"}

    # convert the function arguments into a dictionary
    f_args_dict = dict(zip(params.keys(), f_args))
    f_kwargs_dict = dict(zip(params.keys(), f_kwargs.values()))

    # merge the two dictionaries
    kwargs = {**f_args_dict, **f_kwargs_dict}

    for param in listify_params:
        if param in kwargs and not isinstance(kwargs[param], list):
            kwargs[param] = [kwargs[param]]

    return kwargs


@overload
def validate(func: Callable[P, R]) -> Callable[P, R]:
    pass


@overload
def validate(**dec_kwargs) -> Callable[P, R]:
    pass


def validate(func: Optional[Callable[P, R]] = None, **dec_kwargs) -> Any:
    """Validate function calls. This decorator avoids Pydantic ValidateCallWrapper to pollute the methods docstring."""
    listify_params = dec_kwargs.pop("listify_params", [])

    def decorated(f: Callable[P, R]):
        """Decorated function."""

        @wraps(f)
        def wrapper(*args, **kwargs):
            """Wrapper function."""
            if listify_params:
                f_sig = signature(f)
                kwargs = listify(f_sig, args, kwargs, listify_params)
                # args should be only the self argument
                args = tuple(args[:1])
            return validate_call(f, **dec_kwargs)(*args, **kwargs)

        return wrapper

    return decorated if func is None else decorated(func)
