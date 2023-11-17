import warnings
from typing import Callable, List, Optional


class Extension:
    """Serves as extension entry point and must be created by each extension package.

    See README.md for more information on how to create an extension.
    """

    def __init__(
        self,
        name: str,
        credentials: Optional[List[str]] = None,
    ) -> None:
        """Initialize the extension.

        Parameters
        ----------
        name : str
            Name of the extension.
        credentials : Optional[List[str]], optional
            List of required credentials, by default None
        """
        self.name = name
        self.credentials = credentials or []

    @property
    def obbject_accessor(self) -> Callable:
        """Extend an OBBject, inspired by pandas."""
        # pylint: disable=import-outside-toplevel
        # Avoid circular imports

        from openbb_core.app.model.obbject import OBBject

        return self.register_accessor(self.name, OBBject)

    @staticmethod
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
