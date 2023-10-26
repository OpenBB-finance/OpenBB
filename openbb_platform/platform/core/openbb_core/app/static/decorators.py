import warnings
from functools import wraps
from typing import Any, Callable, List, Optional, TypeVar, overload

from pydantic.validate_call import validate_call
from typing_extensions import ParamSpec

from openbb_core.app.model.credentials import Credentials, format_map
from openbb_core.app.model.obbject import OBBject

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


class CachedAccessor:
    """CachedAccessor"""

    def __init__(self, name: str, accessor) -> None:
        self._name = name
        self._accessor = accessor

    def __get__(self, obj, cls):
        if obj is None:
            return self._accessor
        accessor_obj = self._accessor(obj)
        object.__setattr__(obj, self._name, accessor_obj)
        return accessor_obj


def _register_accessor(name, cls) -> Callable:
    """Register a custom accessor"""

    def decorator(accessor):
        if hasattr(cls, name):
            warnings.warn(
                f"registration of accessor '{repr(accessor)}' under name "
                f"'{repr(name)}' for type '{repr(cls)}' is overriding a preexisting "
                f"attribute with the same name.",
                UserWarning,
            )
        setattr(cls, name, CachedAccessor(name, accessor))
        # pylint: disable=protected-access
        cls._accessors.add(name)
        return accessor

    return decorator


def extend_obbject(name: str, required_credentials: List[str]) -> Callable:
    """Extend an OBBject, inspired by pandas.

    Parameters
    ----------
    name : str
        Name of the accessor.

    required_credentials : List[str]
        List of required credentials.

    Returns
    -------
    Callable
        Decorator for the extension.

    Example
    -------
    @extend_obbject(name="useless", required_credentials=["api_key"])
    class Useless:
        def __init__(self, obbject):
            self._obbject = obbject

        def hello(self) -> str:
            cred = self._obbject._credentials.model_dump(mode="json")["useless_api_key"]
            return f"Hi, I'm {self.__class__.__name__}, this is my credential: {cred}!"

    """
    formatted_creds = [f"{name}_{c}" for c in required_credentials]
    # pylint: disable=protected-access
    Credentials._add_fields(**format_map(formatted_creds))
    return _register_accessor(name, OBBject)
