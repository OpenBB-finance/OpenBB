from typing import Dict, Generic, List, Optional, TypeVar, Union

import pandas as pd
from pydantic import Field
from pydantic.generics import GenericModel

from openbb_core.app.charting_manager import ChartingManager
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.abstract.tagged import Tagged
from openbb_core.app.model.abstract.warning import Warning_
from openbb_core.app.model.charts.chart import Chart
from openbb_core.app.model.metadata import Metadata
from openbb_core.app.provider_interface import get_provider_interface
from openbb_core.app.utils import basemodel_to_df

T = TypeVar("T")
PROVIDERS = get_provider_interface().providers_literal


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
        return (
            self.__class__.__name__
            + "\n\n"
            + "\n".join([f"{k}: {v}" for k, v in self.dict().items()])
        )

    def to_dataframe(
        self, concat: bool = True
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """Converts results field to pandas dataframe.

        Parameters
        ----------
        concat : bool, optional
            If True, it concatenates the dataframes, by default True.

        Returns
        -------
        Union[pd.DataFrame, Dict[str, pd.DataFrame]]
            Pandas dataframe or dictionary of dataframes.
        """
        if not self.results:
            raise OpenBBError("Results not found.")

        try:
            res = self.results
            if isinstance(res, list):
                if isinstance(res[0], dict):
                    for r in res:
                        dict_of_df = {
                            k: basemodel_to_df(v, "date") for k, v in r.items()
                        }
                        df = pd.concat(dict_of_df, axis=1) if concat else dict_of_df

                else:
                    df = basemodel_to_df(res, "date")  # type: ignore
            else:
                df = basemodel_to_df(res, "date")  # type: ignore

            # Improve output so that all columns that are None are not returned
            df = df.dropna(axis=1, how="all")

        except Exception as e:
            raise OpenBBError("Failed to convert results to DataFrame.") from e

        return df

    def to_dict(self) -> Dict[str, List]:
        """Converts results field to list of values.

        Returns
        -------
        Dict[str, List]
            Dictionary of lists.
        """
        df = self.to_dataframe().reset_index()  # type: ignore
        results = {}
        for field in df.columns:
            results[field] = df[field].tolist()

        return results

    def to_chart(self, **kwargs):
        """
        Create or update the `Chart`.
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
        cm = ChartingManager()
        kwargs["data"] = self.to_dataframe()

        self.chart = cm.to_chart(**kwargs)
        return self.chart.fig

    def show(self):
        """Displays chart."""

        if not self.chart or not self.chart.fig:
            raise OpenBBError("Chart not found.")
        self.chart.fig.show()
