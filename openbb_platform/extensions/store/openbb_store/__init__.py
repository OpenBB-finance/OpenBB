"""OBBject Store Extension."""

import importlib
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.app.model.extension import Extension
from openbb_core.app.model.obbject import OBBject
from openbb_core.provider.abstract.data import Data
from pandas import DataFrame

ext = Extension(name="store")

store_module = importlib.import_module("openbb_store.store")

@ext.obbject_accessor
class Store:
    """OBBject Store Extension."""

    # Initialize the Store class as global.
    _store = store_module.Store()

    def __init__(self, obbject):
        """Initialize the Store extension."""
        self._store.user_data_directory = (
            obbject._user_settings.preferences.data_directory
            + "/stores/"
        )
        self.__doc__ = self._store.__doc__

    @property
    def user_data_directory(self) -> str:
        """Return the user data directory."""
        return self._store.user_data_directory

    @user_data_directory.setter
    def user_data_directory(self, directory: str):
        """Set the user data directory."""
        self._store.user_data_directory = directory

    @property
    def verbose(self) -> bool:
        """Return the verbose setting."""
        return self._store.verbose

    @verbose.setter
    def verbose(self, verbose: bool):
        """Set the verbose setting."""
        self._store.verbose = verbose

    @property
    def list_stores(self) -> list:
        """List all keys to stored data objects."""
        return self._store.list_stores()

    @property
    def directory(self) -> dict:
        """Return the store directory."""
        return self._store.directory

    @classmethod
    def add_store(
        cls,
        name: str,
        data: Union[OBBject, Data, DataFrame, Dict, List, str],
        description: Optional[str] = None
    ):
        """Add a stored data object."""
        return cls._store.add_store(name, data, description)

    @classmethod
    def update_store(
        cls,
        name: str,
        data: Union[OBBject, Data, DataFrame, Dict, List, str],
        description: Optional[str] = None
    ):
        """Update a stored data object."""
        return cls._store.update_store(name, data, description)

    @classmethod
    def remove_store(cls, name: str):
        """Remove a stored data object."""
        return cls._store.remove_store(name)

    @classmethod
    def clear_stores(cls):
        """Clear all stored data objects."""
        return cls._store.clear_stores()

    @classmethod
    def get_schema(cls, name: str):
        """Get the schema of a stored data object."""
        return cls._store.get_schema(name)

    @classmethod
    def get_store(
        cls,
        name: str = "",
        element: Literal["OBBject", "dataframe", "dict", "llm", "chart"] = "dataframe",
        pd_query: Optional[str] = None,
        dict_orient: str = "list",
        chart_params: Optional[Dict[str, Any]] = None,
    ):
        """Get a stored data object."""
        return cls._store.get_store(name, element, pd_query, dict_orient, chart_params)

    @classmethod
    def load_store_from_file(
        cls,
        filename: str,
        names: Optional[List[str]] = None,
    ):
        """Load a Store from a file."""
        return cls._store.load_store_from_file(filename, names)

    @classmethod
    def save_store_to_file(
        cls,
        filename: str,
        names: Optional[List[str]] = None,
    ):
        """Save a Store to a file."""
        return cls._store.save_store_to_file(filename, names)

    def __repr__(self):
        """Return a string representation of the object."""
        return f"{self._store.__repr__()}\n\n"
