import warnings
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, overload

from pydantic.validate_call import validate_call
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


def register_accessor(name, cls) -> Callable:
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


def extend_obbject(name: str) -> Callable:
    """Extend an OBBject, inspired by pandas.

    Set the following as entry_point in your extension .toml file:
    [tool.poetry.plugins."openbb_obbject_extension"]
    useless = "openbb_useless:entry_point"

    Extension code:
    ```python
    from openbb_core.app.model.extension import Extension
    from openbb_core.app.static.decorators import extend_obbject

    entry_point = Extension(name="example", required_credentials=["api_key"])
    @extend_obbject(name="example")
    class Example:
        def __init__(self, obbject):
            self._obbject = obbject
        def hello(self):
            api_key = self._obbject._credentials.example_api_key
            print(f"Hello, this is my credential: {api_key}!")
    ```

    Usage:
    >>> from openbb import obb
    >>> obbject = obb.stock.load("AAPL")
    >>> obbject.example.hello()
    Hello, this is my credential: None!
    """
    # pylint: disable=import-outside-toplevel
    # Avoid circular imports
    from openbb_core.app.model.obbject import OBBject

    return register_accessor(name, OBBject)
