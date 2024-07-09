"""Store Model for OpenBB Obbject Callbacks."""

# pylint: disable=too-many-branches,too-many-return-statements,inconsistent-return-type

import hashlib
import lzma
import pickle
import pickletools
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from openbb_core.app.model.obbject import OBBject
from openbb_core.provider.abstract.data import Data
from pydantic import Field

if TYPE_CHECKING:
    from pandas import DataFrame


@lru_cache(maxsize=128)
class Store(Data):
    """The Store class is a data model for storing, organizing, and retrieving OBBjects or other Python objects.

    The class provides methods to add, retrieve, and save groups of data objects
    to memory or file as a transportable, compressed, SHA1 signed pickle.

    It is a shared resource across the Python session,
    when initialized globally within the OpenBB Platform as an OBBject extension.

    **Note**: The OpenBB user preference, 'output_type', must be set to 'OBBject' for this extension to work.

    Parameters
    ----------
    filename : Optional[str]
        Initialize the class with a previously exported file.
        Use the full path to the file without the '.xz' extension.
    names : Optional[str]
        A comma-separated list of names to load from the file.
        If None, all stored data objects are loaded.

    Properties
    ----------
    user_data_directory : str
        The read/write directory. The parent path is resolved by the OpenBB User Preference, 'data_directory'.
        This is overridden by entering the complete path to the file for IO operations.
    verbose : bool
        Set as False to silence IO operation confirmation messages.
    list_stores : List
        List of stored data object keys.
    directory : Dict
        Directory of stored data objects. Each entry contains a name, description, and a preview of the schema.

    Methods
    -------
    add_store(
        name: str,
        data: Union[OBBject, Data, DataFrame, Dict, List, str],
        description: Optional[str] = None
    ):

        Add a stored data object with a unique name, data, and optional description.

    get_store(
        name: str = "",
        element: Literal["OBBject", "dataframe", "dict", "llm", "chart"] = "dataframe",
        pd_query: Optional[str] = None,
        dict_orient: str = "list",
        chart_params: Optional[Dict[str, Any]] = None
    ):

        Get a stored data object by name. When only one object is stored, the name parameter is optional.
        The element parameter specifies the return type, and is only valid for OBBjects.

        A DataFrame is returned when element is set to 'dataframe', and a Pandas query string can be applied.

    get_schema(name: str):

        Get the schema for a stored data object by name.

    update_store(
        name: str,
        data: Union[OBBject, Data, DataFrame, Dict, List, str],
        description: Optional[str] = None
    ):

        Overwrite an existing stored data object with a new data object.

    remove_store(name: str):

        Remove a stored data object by name.

    clear_stores():

        Clear all stored data objects from memory.

    save_store_to_file(filename: str, names: Optional[List[str]] = None):

        Save the Store object, or a list of store names, to a compressed shelf file.

    load_store_from_file(filename: str, names: Optional[str] = None):

        Load an exported Store from file.
    """

    user_data_directory: Optional[str] = Field(
        description="The read/write directory."
        + " When initialized by OBBject, the parent path is resolved by the OpenBB User Preference, 'data_directory'."
        + " This is overridden by entering the complete path to the file for IO operations.",
        default="",
    )
    verbose: bool = Field(
        default=True,
        description="Set as False to silence IO operation confirmation messages.",
    )
    directory: Dict[str, Any] = Field(
        default_factory=dict,
        description="Directory of stored data objects."
        + " Each entry contains a name, description, and a preview of the schema.",
    )
    archives: Dict[str, Any] = Field(
        default_factory=dict,
        description="Compressed stored data objects.",
    )
    schemas: Dict[str, Any] = Field(
        default_factory=dict,
        description="Compressed schema for each stored data object. This field is not meant to be accessed directly."
        + " Use 'directory' to describle all entries,"
        + " or the 'get_schema' method to retrieve the schema for a stored data object.",
    )

    def __init__(
        self, filename: Optional[str] = None, names: Optional[List[str]] = None, **data
    ):
        super().__init__(**data)
        if filename:
            self.load_store_from_file(filename, names)

    @property
    def list_stores(self) -> list:
        """List all keys to stored data objects."""
        return list(self.directory)

    def add_store(
        self,
        name: str,
        data: Union[OBBject, Data, "DataFrame", Dict, List, str],
        description: Optional[str] = None,
    ):
        """Add a stored data object."""
        if name in self.directory:
            raise ValueError(
                f"Data store '{name}' already exists."
                + " Use 'update_store' to overwrite the existing data."
            )

        data_class = data.__class__.__name__
        schema = None
        schema_repr = ""

        if data_class == "OBBject":
            fields_set = data.to_df(index=None).columns.to_list()  # type: ignore
            length = len(data.results) if isinstance(data.results, list) else 1  # type: ignore
            if fields_set[0] == 0:
                fields_set = data.to_df(index=None).iloc[:, 0].to_list()  # type: ignore
            schema = {
                "length": length,
                "fields_set": fields_set,
                "data_model": (
                    data.results.model_copy()  # type: ignore
                    if length == 1
                    else data.results[0].model_copy()  # type: ignore
                ),
                "created_at": str(data.extra["metadata"].timestamp),  # type: ignore
                "uid": data.id,  # type: ignore
            }
            schema_repr = str(schema)[:80]
        elif data_class == "Data" or (
            data_class == "list"
            and len(data) == 1  # type: ignore
            and data[0].__class__.__name__ == "Data"  # type: ignore
        ):
            schema = data.model_copy()  # type: ignore
            schema_repr = schema.__repr__()[:80]
        elif data_class == "dict":
            schema = {
                "length": len(data),  # type: ignore
                "keys": list(data.keys()),  # type: ignore
                "types": list(set([d.__class__.__name__ for d in data.values()])),  # type: ignore
                "types_map": {k: v.__class__.__name__ for k, v in data.items()},  # type: ignore
            }
            schema_repr = str(schema)[:80]
        elif data_class == "list":
            schema = {
                "length": len(data),  # type: ignore
                "types": list(set([d.__class__.__name__ for d in data])),
                "first_value": data[0],  # type: ignore
            }
            schema_repr = str(schema)[:80]
        elif data_class == "DataFrame":
            schema = {
                "length": len(data.index),  # type: ignore
                "width": len(data.columns),  # type: ignore
                "columns": data.columns,  # type: ignore
                "index": data.index,  # type: ignore
                "types_map": data.dtypes,  # type: ignore
            }
            schema_repr = str(schema)[:80]
        elif data_class == "str":
            schema = {
                "length": len(data),  # type: ignore
                "first_80_chars": data[:80],  # type: ignore
            }
            schema_repr = str(schema)
        else:
            raise ValueError(f"Data type, {data_class}, not supported.")

        schema_repr = schema_repr + "..." if len(schema_repr) >= 80 else schema_repr
        compressed_schema = self._compress_store(schema)
        self.schemas.update({name: compressed_schema})
        directory_entry = {
            name: {
                "description": description,
                "data_class": data_class,
                "schema_preview": schema_repr,
            },
        }
        compressed_store = self._compress_store(data)
        self.archives.update({name: compressed_store})
        self.directory.update(directory_entry)
        if self.verbose:
            return f"Data store '{name}' added successfully."

    def get_store(
        self,
        name: str = "",
        element: Literal["OBBject", "dataframe", "dict", "llm", "chart"] = "dataframe",
        pd_query: Optional[str] = None,
        dict_orient: str = "list",
        chart_params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Get a stored data object.

        Parameters
        ----------
        name: str
            The name of the stored object.
        element: Literal["OBBject", "dataframe", "dict", "llm", "chart"]
            The element to retrieve. Ignored if the stored object is not an instance of "OBBject".
        pd_query: Optional[str]
            A Pandas query string to pass before output.
        dict_orient: Optional[str]
            The orientation of the dictionary.
        chart_params: Optional[Dict[str, Any]]
            Dictionary of `chart_params` to pass to `to_chart`.
            Ignored if the stored object is not an instance of "OBBject".
        """
        if not name:
            name = self.list_stores[0] if self.list_stores else ""  # type: ignore
        if name not in self.directory:
            raise ValueError(f"Data store '{name}' does not exist.")
        decompressed_data = self._decompress_store(self.archives[name])
        data_class = self.directory[name]["data_class"]
        if data_class == "OBBject":
            obbject = OBBject.model_validate(decompressed_data)
            if element == "OBBject":
                return obbject
            if element == "llm":
                obbject.to_llm()
            if element == "chart":
                if not hasattr(obbject, "charting"):
                    raise ValueError(
                        "Charting extension is not installed. Install with `pip install openbb-charting`."
                    )
                if hasattr(obbject.chart, "content") and not chart_params:
                    return obbject.chart.content  # type: ignore
                chart_params = chart_params or {}
                chart_params["render"] = False
                _ = obbject.charting.to_chart(data=obbject.results, **chart_params)  # type: ignore
                return obbject.chart.fig  # type: ignore
            df = obbject.to_df()
            if pd_query:
                df = df.query(pd_query)
            if element == "dataframe":
                return df.convert_dtypes()
            if element == "dict":
                return df.to_dict(orient=dict_orient)  # type: ignore
            raise ValueError(
                "Invalid element type. Use: 'OBBject', 'dataframe', 'dict', 'llm', or 'chart'."
            )
        if data_class == "DataFrame":
            df = DataFrame(decompressed_data)
            schema = self.get_schema(name)
            df.columns = schema["columns"]
            df.index = schema["index"]
            df = df.astype(schema["types_map"], errors="ignore")
            return (
                df.query(pd_query).convert_dtypes() if pd_query else df.convert_dtypes()
            )
        return decompressed_data

    def get_schema(self, name: str):
        """Get the schema for a stored data object."""
        if name not in self.directory:
            raise ValueError(f"Data store '{name}' does not exist.")
        compressed_schema = self.schemas[name]
        decompressed_schema = self._decompress_store(compressed_schema)

        if "data_model" in decompressed_schema:
            decompressed_schema["data_model"] = decompressed_schema[
                "data_model"
            ].schema(by_alias=False)

        return decompressed_schema

    def save_store_to_file(self, filename, names: Optional[List[str]] = None):
        """Save the Store object, or a list of store names, to a compressed shelf file."""
        names = names or self.list_stores
        temp = {
            "archives": {name: self.archives[name] for name in names},
            "schemas": {name: self.schemas[name] for name in names},
            "directory": {name: self.directory[name] for name in names},
        }
        # Pickle the data and generate a signature
        pickled_data = pickle.dumps(temp, protocol=pickle.HIGHEST_PROTOCOL)
        signature = hashlib.sha1(pickled_data).hexdigest()  # noqa
        # Store the data and the signature.
        filename = (
            filename + ".xz"
            if filename.startswith("/")
            else self.user_data_directory + filename + ".xz"
        )
        with lzma.open(filename, "wb") as f:
            f.write(pickle.dumps({"signature": signature, "data": pickled_data}))

        if self.verbose:
            return f"{filename} saved successfully."

    def load_store_from_file(self, filename, names: Optional[List[str]] = None):
        """Load the Store object from a file."""
        filename = (
            filename + ".xz"
            if filename.startswith("/")
            else self.user_data_directory + filename + ".xz"
        )
        pickled_data = None
        signature = None
        with lzma.open(filename, "rb") as f:
            file = pickle.load(f)  # noqa
            if (
                not isinstance(file, dict)
                or "signature" not in file
                or "data" not in file
            ):
                raise ValueError("Data integrity check failed")
            pickled_data = file["data"]
            signature = file["signature"]

        # Verify the signature
        if hashlib.sha1(pickled_data).hexdigest() != signature:  # noqa
            raise ValueError("Data integrity check failed")

        # Load the data
        temp = pickle.loads(pickled_data)  # noqa

        if names:
            names = names.split(",")  # type: ignore
            for name in temp["directory"].copy():
                if name not in names:
                    temp["directory"].pop(name)
                    temp["archives"].pop(name)
                    temp["schemas"].pop(name)

        self.archives.update(temp["archives"])
        self.schemas.update(temp["schemas"])
        self.directory.update(temp["directory"])

        if self.verbose:
            return f"{filename} loaded successfully."

    def update_store(
        self,
        name: str,
        data: Union[OBBject, Data, "DataFrame", Dict, List, str],
        description: Optional[str] = None,
    ):
        """Overwrite an existing stored data object."""
        if name not in self.directory:
            raise ValueError(f"Data store '{name}' does not exist.")
        self.remove_store(name, verbose=False)  # type: ignore
        self.add_store(
            name=name,
            data=data,
            description=description,
            verbose=False,  # type: ignore
        )
        if self.verbose:
            return f"Data store '{name}' updated successfully."

    def remove_store(self, name: str):
        """Remove a stored data object by name."""
        if name not in self.directory:
            raise ValueError(f"Data store '{name}' does not exist.")
        self.directory.pop(name)
        self.archives.pop(name)
        self.schemas.pop(name)
        if self.verbose:
            return f"Data store '{name}' removed successfully."

    def clear_stores(self):
        """Clear all stored data objects from memory."""
        self.directory = {}
        self.archives = {}
        self.schemas = {}
        if self.verbose:
            return "All data stores cleared."

    def _compress_store(self, data):
        """Compress a stored data object."""
        pickled_data = pickletools.optimize(pickle.dumps(data))
        signature = hashlib.sha1(pickled_data).hexdigest()  # noqa
        return {"archive": lzma.compress(pickled_data), "signature": signature}

    def _decompress_store(self, data):
        """Decompress a stored data object."""
        decompressed_data = lzma.decompress(data["archive"])
        signature = data["signature"]
        if hashlib.sha1(decompressed_data).hexdigest() != signature:  # noqa
            raise ValueError("Data signature does not match!")
        return pickle.loads(decompressed_data)  # noqa

    def __repr__(self):
        """Return a string representation of the object."""
        names = self.list_stores  # type: ignore
        if names == [""]:
            return f"{self.__class__.__name__}\n\nNo archives added."
        stores: List = []
        for name in names:
            string = (
                f"\n\n    {name}:\n        Data Class: {self.directory[name]['data_class']}"
                + f"\n        Description: {self.directory[name].get('description')}"
                + f"\n        Schema Preview: {self.directory[name].get('schema_preview')}"
            )
            stores.append(string)
        return f"\n{self.__class__.__name__} Archive {''.join(stores) if stores else 'No stores added.'}"
