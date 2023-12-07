"""The OBBject."""
from re import sub
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Set,
    TypeVar,
)

import pandas as pd
from numpy import ndarray
from pydantic import BaseModel, Field

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.abstract.tagged import Tagged
from openbb_core.app.model.abstract.warning import Warning_
from openbb_core.app.model.charts.chart import Chart
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.query import Query
from openbb_core.app.utils import basemodel_to_df

if TYPE_CHECKING:
    try:
        from polars import DataFrame as PolarsDataFrame  # type: ignore
    except ImportError:
        PolarsDataFrame = None

T = TypeVar("T")
PROVIDERS = Literal[tuple(ProviderInterface().available_providers)]  # type: ignore


class OBBject(Tagged, Generic[T]):
    """OpenBB object."""

    results: Optional[T] = Field(
        default=None,
        description="Serializable results.",
    )
    provider: Optional[PROVIDERS] = Field(  # type: ignore
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
    _credentials: ClassVar[Optional[BaseModel]] = None
    _accessors: ClassVar[Set[str]] = set()

    def __repr__(self) -> str:
        """Human readable representation of the object."""
        items = [
            f"{k}: {v}"[:83] + ("..." if len(f"{k}: {v}") > 83 else "")
            for k, v in self.model_dump().items()
        ]
        return f"{self.__class__.__name__}\n\n" + "\n".join(items)

    @classmethod
    def results_type_repr(cls, params: Optional[Any] = None) -> str:
        """Return the results type name."""
        type_ = params[0] if params else cls.model_fields["results"].annotation
        name = type_.__name__ if hasattr(type_, "__name__") else str(type_)
        if "typing." in str(type_):
            unpack_optional = sub(r"Optional\[(.*)\]", r"\1", str(type_))
            name = sub(
                r"(\w+\.)*(\w+)?(\, NoneType)?",
                r"\2",
                unpack_optional,
            )

        return name

    @classmethod
    def model_parametrized_name(cls, params: Any) -> str:
        """Return the model name with the parameters."""
        return f"OBBject[{cls.results_type_repr(params)}]"

    def to_df(self) -> pd.DataFrame:
        """Alias for `to_dataframe`."""
        return self.to_dataframe()

    def to_dataframe(self) -> pd.DataFrame:
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

        Returns
        -------
        pd.DataFrame
            Pandas dataframe.
        """

        def is_list_of_basemodel(items: List[Any]) -> bool:
            return isinstance(items, list) and all(
                isinstance(item, BaseModel) for item in items
            )

        if self.results is None or self.results == []:
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
                        dict_of_df[k] = basemodel_to_df(v, "date")
                        sort_columns = False
                    # Dict[str, Any]
                    else:
                        dict_of_df[k] = pd.DataFrame(v)

                df = pd.concat(dict_of_df, axis=1)

            # List[BaseModel]
            elif is_list_of_basemodel(res):
                df = basemodel_to_df(res, "date")
                sort_columns = False
            # List[List | str | int | float] | Dict[str, Dict | List | BaseModel]
            else:
                try:
                    df = pd.DataFrame(res)
                except ValueError:
                    if isinstance(res, dict):
                        df = pd.DataFrame([res])

            if df is None:
                raise OpenBBError("Unsupported data format.")

            # Drop columns that are all NaN, but don't rearrange columns
            if sort_columns:
                df.sort_index(axis=1, inplace=True)
            df = df.dropna(axis=1, how="all")

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

        return from_pandas(self.to_dataframe().reset_index())

    def to_numpy(self) -> ndarray:
        """Convert results field to numpy array."""
        return self.to_dataframe().reset_index().to_numpy()

    def to_dict(
        self,
        orient: Literal[
            "dict", "list", "series", "split", "tight", "records", "index"
        ] = "list",
    ) -> Dict[str, List]:
        """Convert results field to a dictionary using any of pandas to_dict options.

        Parameters
        ----------
        orient : Literal["dict", "list", "series", "split", "tight", "records", "index"]
            Value to pass to `.to_dict()` method


        Returns
        -------
        Dict[str, List]
            Dictionary of lists.
        """
        df = self.to_dataframe()  # type: ignore
        transpose = False
        if orient == "list":
            transpose = True
            if not isinstance(self.results, dict):
                transpose = False
            else:  # Only enter the loop if self.results is a dictionary
                for key, value in self.results.items():
                    if not isinstance(value, dict):
                        transpose = False
                        break
        if transpose:
            df = df.T
        results = df.to_dict(orient=orient)
        if orient == "list" and "index" in results:
            del results["index"]
        return results

    def to_chart(self, **kwargs):
        """
        Create or update the `Chart`.
        This function assumes that the provided data is a time series, if it's not, it will
        most likely result in an Exception.

        Note that the `chart` attribute is composed by: `content`, `format` and `fig`.

        Parameters
        ----------
        **kwargs
            Keyword arguments to be passed to the charting extension.
            This implies that the user has some knowledge on the charting extension API.
            This is the case because the charting extension may vary on user preferences.

        Returns
        -------
        chart.fig
            The chart figure.
        """
        #  pylint: disable=import-outside-toplevel
        # Avoids circular import
        from openbb_core.app.charting_service import ChartingService

        cs = ChartingService()
        kwargs["data"] = self.to_dataframe()

        self.chart = cs.to_chart(**kwargs)
        return self.chart.fig

    def show(self):
        """Display chart."""
        if not self.chart or not self.chart.fig:
            raise OpenBBError(
                "Chart not found. "
                "Please compute the chart first by using the `chart=True` argument."
            )
        self.chart.fig.show()

    @classmethod
    async def from_query(cls, query: Query) -> "OBBject":
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

        return cls(results=await query.execute())
