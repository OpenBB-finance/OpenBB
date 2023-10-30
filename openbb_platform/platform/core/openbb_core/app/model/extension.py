import warnings
from typing import Callable, List, Optional


class Extension:
    """Serves as extension entry point and must be created by each extension package."""

    def __init__(
        self,
        name: str,
        required_credentials: Optional[List[str]] = None,
    ) -> None:
        """Initialize the extension.

        Parameters
        ----------
        name : str
            Name of the provider.
        required_credentials : Optional[List[str]], optional
            List of required credentials, by default None
        """
        self.name = name
        if required_credentials is None:
            self.required_credentials: List = []
        else:
            self.required_credentials = []
            for rq in required_credentials:
                self.required_credentials.append(f"{self.name.lower()}_{rq}")

    @property
    def accessor(self) -> Callable:
        """Extend an OBBject, inspired by pandas.

        Set the following as entry_point in your extension .toml file and install it:
        [tool.poetry.plugins."openbb_obbject_extension"]
        example = "openbb_example:entry_point"

        Extension code:
        ```python
        from openbb_core.app.model.extension import Extension

        entry_point = Extension(name="example", required_credentials=["api_key"])

        @entry_point.accessor
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

        return self.register_accessor(self.name, OBBject)

    @staticmethod
    def register_accessor(name, cls) -> Callable:
        """Register a custom accessor"""

        def decorator(accessor):
            # Here we need to prevent the user from using provider names as accessor names

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
