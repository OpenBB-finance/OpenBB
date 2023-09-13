"""The OBBject."""
from typing import Any, Dict, Generic, List, Literal, Optional, TypeVar

import pandas as pd
from numpy import ndarray
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from openbb_core.app.charting_service import ChartingService
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.abstract.tagged import Tagged
from openbb_core.app.model.abstract.warning import Warning_
from openbb_core.app.model.charts.chart import Chart
from openbb_core.app.model.metadata import Metadata
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.utils import basemodel_to_df

try:
    from polars import DataFrame as PolarsDataFrame
except ImportError:
    PolarsDataFrame = Any

T = TypeVar("T")
PROVIDERS = Literal[tuple(ProviderInterface().available_providers)]  # type: ignore


class OBBject(GenericModel, Generic[T], Tagged):
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
    metadata: Optional[Metadata] = Field(
        default=None,
        description="Metadata info about the command execution.",
    )

    def __repr__(self) -> str:
        """Human readable representation of the object."""
        return (
            self.__class__.__name__
            + "\n\n"
            + "\n".join(
                [
                    f"{k}: {v}"[:83]
                    + ("..." if len(f"{k}: {v}") > len(f"{k}: {v}"[:83]) else "")
                    for k, v in self.dict().items()
                ]
            )
        )

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
        if self.results is None or self.results == []:
            raise OpenBBError("Results not found.")

        if isinstance(self.results, pd.DataFrame):
            return self.results

        try:
            res = self.results

            df = None

            sort_columns = True
            if isinstance(res, list) and len(res) == 1 and isinstance(res[0], dict):
                for r in res:
                    dict_of_df = {}
                    for k, v in r.items():
                        if isinstance(v, list) and all(
                            isinstance(nv, BaseModel) for nv in v
                        ):
                            dict_of_df[k] = basemodel_to_df(v, "date")
                            sort_columns = False
                        else:
                            dict_of_df[k] = pd.DataFrame(v)
                    df = pd.concat(dict_of_df, axis=1)

            elif isinstance(res, list) and all(
                isinstance(item, BaseModel) for item in res
            ):
                df = basemodel_to_df(res, "date")
                sort_columns = False
            else:
                df = pd.DataFrame(res)

            if df is None:
                raise OpenBBError("Unsupported data format.")

            # Drop columns that are all NaN, but don't rearrange columns
            if sort_columns:
                df.sort_index(axis=1, inplace=True)
            df = df.dropna(axis=1, how="all")

        except Exception as e:
            raise OpenBBError("Failed to convert results to DataFrame.") from e

        return df

    def to_polars(self) -> PolarsDataFrame:
        """Convert results field to polars dataframe."""
        try:
            from polars import from_pandas
        except ImportError:
            raise ImportError(
                "Please install polars: `pip install polars`  to use this function."
            )

        return from_pandas(self.to_dataframe().reset_index())

    def to_numpy(self) -> ndarray:
        """Convert results field to numpy array."""
        return self.to_dataframe().reset_index().to_numpy()

    def to_dict(self) -> Dict[str, List]:
        """Convert results field to list of values.

        Returns
        -------
        Dict[str, List]
            Dictionary of lists.
        """
        if isinstance(self.results, dict) and all(
            isinstance(v, dict) for v in self.results.values()
        ):
            results: Dict[str, List] = {}
            for _, v in self.results.items():
                for kk, vv in v.items():
                    if kk not in results:
                        results[kk] = []
                    results[kk].append(vv)

            return results

        df = self.to_dataframe().reset_index()  # type: ignore
        results = {}
        for field in df.columns:
            results[field] = df[field].tolist()

        # remove index from results
        if "index" in results:
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
