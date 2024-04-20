"""The OBBject."""

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Hashable,
    List,
    Literal,
    Optional,
    Set,
    TypeVar,
    Union,
)

import pandas as pd
from numpy import ndarray
from pydantic import BaseModel, Field, PrivateAttr

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.abstract.tagged import Tagged
from openbb_core.app.model.abstract.warning import Warning_
from openbb_core.app.model.charts.chart import Chart
from openbb_core.app.utils import basemodel_to_df
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data

if TYPE_CHECKING:
    from openbb_core.app.query import Query

    try:
        from polars import DataFrame as PolarsDataFrame  # type: ignore
    except ImportError:
        PolarsDataFrame = None

T = TypeVar("T")


class OBBject(Tagged, Generic[T]):
    """OpenBB object."""

    accessors: ClassVar[Set[str]] = set()
    _user_settings: ClassVar[Optional[BaseModel]] = None
    _system_settings: ClassVar[Optional[BaseModel]] = None

    results: Optional[T] = Field(
        default=None,
        description="Serializable results.",
    )
    provider: Optional[str] = Field(  # type: ignore
        default=None,
        description="Provider name.",
    )
    warnings: Optional[List[Warning_]] = Field(
        default=None,
        description="List of warnings.",
    )
    chart: Optional[Chart] = Field(
        default=None,
        description="Chart object.",
    )
    extra: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extra info.",
    )
    _route: str = PrivateAttr(
        default=None,
    )
    _standard_params: Optional[Dict[str, Any]] = PrivateAttr(
        default_factory=dict,
    )

    def __repr__(self) -> str:
        """Human readable representation of the object."""
        items = [
            f"{k}: {v}"[:83] + ("..." if len(f"{k}: {v}") > 83 else "")
            for k, v in self.model_dump().items()
        ]
        return f"{self.__class__.__name__}\n\n" + "\n".join(items)

    def to_df(
        self, index: Optional[Union[str, None]] = "date", sort_by: Optional[str] = None
    ) -> pd.DataFrame:
        """Alias for `to_dataframe`."""
        return self.to_dataframe(index=index, sort_by=sort_by)

    def to_dataframe(
        self, index: Optional[Union[str, None]] = "date", sort_by: Optional[str] = None
    ) -> pd.DataFrame:
        """Convert results field to pandas dataframe.

        Supports converting creating pandas DataFrames from the following
        serializable data formats:

        - List[BaseModel]
        - List[Dict]
        - List[List]
        - List[str]
        - List[int]
        - List[float]
        - Dict[str, Dict]
        - Dict[str, List]
        - Dict[str, BaseModel]

        Parameters
        ----------
        index : Optional[str]
            Column name to use as index.
        sort_by : Optional[str]
            Column name to sort by.

        Returns
        -------
        pd.DataFrame
            Pandas dataframe.
        """

        def is_list_of_basemodel(items: Union[List[T], T]) -> bool:
            return isinstance(items, list) and all(
                isinstance(item, BaseModel) for item in items
            )

        if self.results is None or not self.results:
            raise OpenBBError("Results not found.")

        if isinstance(self.results, pd.DataFrame):
            return self.results

        try:
            res = self.results
            df = None
            sort_columns = True

            # List[Dict]
            if isinstance(res, list) and len(res) == 1 and isinstance(res[0], dict):
                r = res[0]
                dict_of_df = {}

                for k, v in r.items():
                    # Dict[str, List[BaseModel]]
                    if is_list_of_basemodel(v):
                        dict_of_df[k] = basemodel_to_df(v, index)
                        sort_columns = False
                    # Dict[str, Any]
                    else:
                        dict_of_df[k] = pd.DataFrame(v)

                df = pd.concat(dict_of_df, axis=1)

            # List[BaseModel]
            elif is_list_of_basemodel(res):
                dt: Union[List[Data], Data] = res  # type: ignore
                df = basemodel_to_df(dt, index)
                sort_columns = False
            # List[List | str | int | float] | Dict[str, Dict | List | BaseModel]
            else:
                try:
                    df = pd.DataFrame(res)  # type: ignore[call-overload]
                    # Set index, if any
                    if df is not None and index is not None and index in df.columns:
                        df.set_index(index, inplace=True)

                except ValueError:
                    if isinstance(res, dict):
                        df = pd.DataFrame([res])

            if df is None:
                raise OpenBBError("Unsupported data format.")

            # Drop columns that are all NaN, but don't rearrange columns
            if sort_columns:
                df.sort_index(axis=1, inplace=True)
            df = df.dropna(axis=1, how="all")

            # Sort by specified column
            if sort_by:
                df.sort_values(by=sort_by, inplace=True)

        except OpenBBError as e:
            raise e
        except ValueError as ve:
            raise OpenBBError(
                f"ValueError: {ve}. Ensure the data format matches the expected format."
            ) from ve
        except TypeError as te:
            raise OpenBBError(
                f"TypeError: {te}. Check the data types in your results."
            ) from te
        except Exception as ex:
            raise OpenBBError(f"An unexpected error occurred: {ex}") from ex

        return df

    def to_polars(self) -> "PolarsDataFrame":
        """Convert results field to polars dataframe."""
        try:
            from polars import from_pandas  # type: ignore # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(
                "Please install polars: `pip install polars pyarrow`  to use this method."
            ) from exc

        return from_pandas(self.to_dataframe(index=None))

    def to_numpy(self) -> ndarray:
        """Convert results field to numpy array."""
        return self.to_dataframe(index=None).to_numpy()

    def to_dict(
        self,
        orient: Literal[
            "dict", "list", "series", "split", "tight", "records", "index"
        ] = "list",
    ) -> Union[Dict[Hashable, Any], List[Dict[Hashable, Any]]]:
        """Convert results field to a dictionary using any of pandas to_dict options.

        Parameters
        ----------
        orient : Literal["dict", "list", "series", "split", "tight", "records", "index"]
            Value to pass to `.to_dict()` method


        Returns
        -------
        Union[Dict[Hashable, Any], List[Dict[Hashable, Any]]]
            Dictionary of lists or list of dictionaries if orient is "records".
        """
        df = self.to_dataframe(index=None)
        if (
            orient == "list"
            and isinstance(self.results, dict)
            and all(
                isinstance(value, dict)
                for value in self.results.values()  # pylint: disable=no-member
            )
        ):
            df = df.T
        results = df.to_dict(orient=orient)
        if isinstance(results, dict) and orient == "list" and "index" in results:
            del results["index"]
        return results

    def to_llm(self) -> Union[Dict[Hashable, Any], List[Dict[Hashable, Any]]]:
        """Convert results field to an LLM compatible output.

        Returns
        -------
        Union[Dict[Hashable, Any], List[Dict[Hashable, Any]]]
            Dictionary of lists or list of dictionaries if orient is "records".
        """
        df = self.to_dataframe(index=None)

        results = df.to_json(
            orient="records",
            date_format="iso",
            date_unit="s",
        )

        return results

    def show(self, **kwargs: Any) -> None:
        """Display chart."""
        # pylint: disable=no-member
        if not self.chart or not self.chart.fig:
            raise OpenBBError("Chart not found.")
        show_function: Callable = getattr(self.chart.fig, "show")
        show_function(**kwargs)

    @classmethod
    async def from_query(cls, query: "Query") -> "OBBject":
        """Create OBBject from query.

        Parameters
        ----------
        query : Query
            Initialized query object.

        Returns
        -------
        OBBject[ResultsType]
            OBBject with results.
        """
        results = await query.execute()
        if isinstance(results, AnnotatedResult):
            return cls(
                results=results.result, extra={"results_metadata": results.metadata}
            )
        return cls(results=results)
