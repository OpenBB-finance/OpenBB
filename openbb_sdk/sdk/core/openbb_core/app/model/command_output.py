from typing import Any, Dict, Generic, List, Optional, TypeVar

import pandas as pd
from pydantic import Field
from pydantic.generics import GenericModel

from openbb_core.app.model.abstract.error import Error
from openbb_core.app.model.abstract.tagged import Tagged
from openbb_core.app.model.abstract.warning import Warning_
from openbb_core.app.model.chart import Chart
from openbb_core.app.provider_interface import get_provider_interface

T = TypeVar("T")
PROVIDERS = get_provider_interface().providers_literal


class CommandOutput(GenericModel, Generic[T], Tagged):
    results: Optional[T] = Field(
        default=None,
        description="Serializable results.",
    )
    provider: Optional[PROVIDERS] = Field(  # type: ignore
        default=None,
        description="Provider name.",
    )
    warnings: Optional[List[Warning_]] = None
    error: Optional[Error] = None
    chart: Optional[Chart] = None

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + "\n\n"
            + "\n".join([f"{k}: {v}" for k, v in self.dict().items()])
        )

    def to_dataframe(self) -> pd.DataFrame:
        """Converts results field to pandas dataframe.

        Returns
        -------
        pd.DataFrame
            Pandas dataframe.
        """
        if self.results is None:
            raise ValueError("Results not found.")

        try:
            df = pd.DataFrame(self.dict()["results"])
            if "date" in df.columns:
                df = df.set_index("date")
                df.index = pd.to_datetime(df.index)
        except ValueError:
            df = pd.DataFrame(self.dict()["results"], index=["values"]).T

        return df

    def to_dict(self) -> Dict[str, List]:
        """Converts results field to list of values.

        Returns
        -------
        Dict[str, List]
            Dictionary of lists.
        """
        df = self.to_dataframe()
        results = {}
        for field in df.columns:
            results[field] = df[field].tolist()

        return results

    def to_plotly_json(self) -> Optional[Dict[str, Any]]:
        """
        Outputs the plotly json.
        It is a proxy to the `chart.content` attribute that contains it already.
        Returns
        -------
        Dict[str, Any]
            Plotly json.
        """
        if not self.chart:
            raise ValueError("Chart not found.")
        if not self.chart.format == "plotly":
            raise ValueError("Chart is not in plotly format.")
        return self.chart.content

    def show(self):
        """Displays chart."""
        if not self.chart:
            raise ValueError("Chart not found.")
        self.chart.show()
