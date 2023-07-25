from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

import pandas as pd
from pydantic import Field
from pydantic.generics import GenericModel

from openbb_core.app.charting_manager import ChartingManager
from openbb_core.app.model.abstract.error import Error
from openbb_core.app.model.abstract.tagged import Tagged
from openbb_core.app.model.abstract.warning import Warning_
from openbb_core.app.model.charts.chart import Chart, ChartFormat
from openbb_core.app.provider_interface import get_provider_interface
from openbb_core.app.utils import basemodel_to_df

T = TypeVar("T")
PROVIDERS = get_provider_interface().providers_literal


class OpenBBError(Exception):
    pass


class CommandOutput(GenericModel, Generic[T], Tagged):
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
    error: Optional[Error] = Field(
        default=None,
        description="Exception caught.",
    )
    chart: Optional[Chart] = Field(
        default=None,
        description="Chart object.",
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
        if self.results is None:
            raise OpenBBError("Results not found.")

        try:
            if isinstance(self.results, dict) and all(
                isinstance(v, list) for v in self.results.values()
            ):
                dict_of_df = {
                    k: basemodel_to_df(v, "date") for k, v in self.results.items()
                }
                df = pd.concat(dict_of_df, axis=1) if concat else dict_of_df

            elif isinstance(self.results, list):
                df = basemodel_to_df(self.results, "date")
            else:
                df = basemodel_to_df(self.results, "date")
        except Exception as e:
            raise OpenBBError("Failed to convert results to DataFrame.") from e

        if df.index.name == "date":
            df.index = pd.to_datetime(df.index)
            df.sort_index(axis=0, inplace=True)

        return df

    def to_dict(self) -> Dict[str, List]:
        """Converts results field to list of values.

        Returns
        -------
        Dict[str, List]
            Dictionary of lists.
        """
        df = self.to_dataframe().reset_index()
        results = {}
        for field in df.columns:
            results[field] = df[field].tolist()

        return results

    def to_plotly_json(
        self, create_chart: bool = True, **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Returns the plotly json representation of the chart.
        If the chart was already computed it return the plotly json representation of the chart.
        Otherwise it computes the chart based on the available data and provided kwargs.

        Parameters
        ----------
        create_chart : bool, optional
            If True, it creates the chart object and populates the respective field on the object, by default True.
        **kwargs
            Keyword arguments to be passed to the charting extension.
            This implies that the user has to know the charting extension API; this is the case
            because the charting extension may vary on user settings.
        """

        if self.chart and not kwargs:
            plotly_json = self.chart.content
        else:
            cm = ChartingManager()
            kwargs["data"] = self.to_dataframe()
            plotly_json = cm.to_plotly_json(**kwargs)

            if create_chart:
                try:
                    self.chart = Chart(content=plotly_json, format=ChartFormat.plotly)
                except Exception as e:
                    self.chart = Chart(error=Error(message=str(e)))

        return plotly_json

    def show(self):
        """Displays chart."""
        if not self.chart:
            raise OpenBBError("Chart not found.")
        self.chart.show()
