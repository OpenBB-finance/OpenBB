from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, overload

from pydantic.validate_call import validate_call
from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


def listify(f_args, f_kwargs, listify_params) -> Tuple[List[Any], Dict[str, Any]]:
    """Converts function arguments to list if they are in listify_params."""
    args = list(f_args)
    for _, v in listify_params.items():
        if v < len(args) and not isinstance(args[v], list):
            args[v] = [args[v]]
    kwargs = {
        k: [v] if k in listify_params and not isinstance(v, list) else v
        for k, v in f_kwargs.items()
    }
    return args, kwargs


@overload
def validate(func: Callable[P, R]) -> Callable[P, R]:
    pass


@overload
def validate(**dec_kwargs) -> Callable[P, R]:
    pass


def validate(func: Optional[Callable[P, R]] = None, **dec_kwargs) -> Any:
    """Validate function calls. This decorator avoids Pydantic ValidateCallWrapper to pollute the methods docstring."""
    listify_params = dec_kwargs.pop("listify_params", {})

    def decorated(f: Callable[P, R]):
        """Decorated function."""

        @wraps(f)
        def wrapper(*args, **kwargs):
            """Wrapper function."""
            if listify_params:
                args, kwargs = listify(args, kwargs, listify_params)
            return validate_call(f, **dec_kwargs)(*args, **kwargs)

        return wrapper

    return decorated if func is None else decorated(func)
