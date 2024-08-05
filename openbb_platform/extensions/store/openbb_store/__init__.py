"""OBBject Store Extension."""

import importlib
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union
from warnings import warn

from openbb_core.app.model.extension import Extension
from openbb_core.app.model.obbject import OBBject

if TYPE_CHECKING:
    from openbb_core.provider.abstract.data import Data
    from pandas import DataFrame, ExcelFile

ext = Extension(name="store")

store_module = importlib.import_module("openbb_store.store")


@ext.obbject_accessor
class Store:
    """OBBject Store Extension."""

    # Initialize the Store class as global.
    _store = store_module.Store()
    __doc__ = _store.__doc__

    def __init__(self, obbject):
        """Initialize the Store extension."""
        self._store.user_data_directory = (
            obbject._user_settings.preferences.data_directory + "/stores/"
        )
        self.__doc__ = self._store.__doc__
        self._load_defaults()

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
        return self._store.list_stores

    @property
    def directory(self) -> dict:
        """Return the store directory."""
        return self._store.directory

    @property
    def defaults(self) -> list:
        """Return the list of stores loaded by default."""
        return self._store._defaults

    @classmethod
    def add_store(
        cls,
        name: str,
        data: Union[OBBject, "Data", "DataFrame", "ExcelFile", Dict, List, str],
        description: Optional[str] = None,
    ):
        """Add a stored data object."""
        return cls._store.add_store(name, data, description)

    @classmethod
    def update_store(
        cls,
        name: str,
        data: Union[OBBject, "Data", "DataFrame", Dict, List, str],
        description: Optional[str] = None,
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
        sheet_name: Optional[str] = None,
        pd_query: Optional[str] = None,
        dict_orient: str = "list",
        chart_params: Optional[Dict[str, Any]] = None,
        **excel_kwargs,
    ) -> Any:
        """Get a stored data object.

        Parameters
        ----------
        name: str
            The name of the stored object.
        element: Literal["OBBject", "dataframe", "dict", "llm", "chart"]
            The element to retrieve. Ignored if the stored object is not an instance of "OBBject".
        sheet_name: Optional[str]
            The name of the Excel worksheet to return from the ExcelFile object.
            Ignored if the stored object is not an instance of "ExcelFile".
        pd_query: Optional[str]
            A Pandas query string to pass before output.
            Valid only when the expected output is passed through a DataFrame.
        dict_orient: Optional[str]
            The orientation of the dictionary.
        chart_params: Optional[Dict[str, Any]]
            Dictionary of `chart_params` to pass to `to_chart`.
            Ignored if the stored object is not an instance of "OBBject".
        **excel_kwargs
            Additional keyword arguments for the `read_excel` method.
            Ignored if the stored object is not an instance of "ExcelFile".

        Returns
        -------
        Any
            The stored data object or requested element.
        """
        return cls._store.get_store(
            name,
            element,
            sheet_name,
            pd_query,
            dict_orient,
            chart_params,
            **excel_kwargs,
        )

    @classmethod
    def load_store_from_file(
        cls,
        filename: str,
        names: Optional[List[str]] = None,
    ):
        """Load a Store from a file."""
        return cls._store.load_store_from_file(filename, names)

    @classmethod
    def load_from_excel(
        cls,
        file: Union[bytes, str],
        name: str,
        description: Optional[str] = None,
        **excel_file_kwargs,
    ) -> "ExcelFile":
        """Load an Excel spreadsheet from a file, adds it as a stored data object, and returns the ExcelFile object.

        Parameters
        ----------
        file : Union[bytes, str]
            The file path, url, or bytes object. If the file is a path-like, it must include the file extension.
        name : str
            The name to assign to the stored object.
        description : Optional[str]
            A description of the stored object.
        **excel_file_kwargs
            Additional keyword arguments for the ExcelFile constructor.

        Returns
        -------
        ExcelFile
            The ExcelFile object.
        """
        return cls._store.load_from_excel(file, name, description, **excel_file_kwargs)

    def load_defaults(self):
        """Clear all stores and load the defaults."""
        self._load_defaults()
        if self.verbose:
            return (
                "Defaults loaded."
                if self.defaults and len(self.defaults) > 0
                else "No defaults saved."
            )

    @classmethod
    def save_store_to_file(
        cls,
        filename: str,
        names: Optional[List[str]] = None,
    ):
        """Save a Store to a file."""
        return cls._store.save_store_to_file(filename, names)

    def add_to_defaults(
        self,
        name: str,
    ) -> Union[str, None]:
        """Add a stored data object to load by default."""
        verbose_setting = bool(self.verbose)
        defaults = self.defaults
        if name in defaults and verbose_setting:
            warn(f"{name} is already in the defaults, overwriting.")

        if name not in self.list_stores:
            raise KeyError(f"{name} is not a stored object.")

        if name not in defaults:
            defaults.append(name)

        self._store._defaults = defaults
        self.verbose = False
        try:
            self.save_store_to_file("defaults", defaults)
        except Exception as e:
            self.verbose = verbose_setting
            raise Exception from e
        self.verbose = verbose_setting
        if self.verbose:
            return f"{name} added to defaults."
        return None

    def remove_from_defaults(
        self,
        name: str,
    ) -> Union[str, None]:
        """Remove an entry from the default stores."""
        verbose_setting = bool(self.verbose)
        defaults = self.defaults
        if name not in defaults:
            raise KeyError(f"{name} is not a default store.")
        defaults.remove(name)
        self._store._defaults = defaults
        self.verbose = False
        try:
            self.save_store_to_file("defaults", defaults)
        except Exception as e:
            self.verbose = verbose_setting
            raise e from e
        self.verbose = verbose_setting
        if self.verbose:
            return f"{name} removed from defaults."
        return None

    def _load_defaults(self):
        """Load the default stores."""
        verbose_setting = bool(self.verbose)
        self.verbose = False
        loaded_stores = self.list_stores
        self.clear_stores()
        self.load_store_from_file("defaults")
        defaults = self.list_stores
        if not defaults:
            for store in loaded_stores:
                self.add_store(store, self.get_store(store))
            self.verbose = verbose_setting
            return None
        for store in defaults:
            self._store._defaults.append(store)
        self.verbose = verbose_setting

    def __repr__(self):
        """Return a string representation of the Store class."""
        return f"{self._store.__repr__()}\n"
