from enum import Enum
from typing import Any, Dict, Optional, Type

from openbb_core.app.model.abstract.error import Error
from pydantic import BaseModel, Field


class ChartFormat(str, Enum):
    plotly = "plotly"


class Chart(BaseModel):
    content: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw textual representation of the chart.",
    )
    format: Optional[ChartFormat] = Field(
        default=ChartFormat.plotly,
        description="Complementary attribute to the `content` attribute. It specifies the format of the chart.",
    )
    error: Optional[Error] = Field(
        default=None,
        description="Exception caught during the computation of the `Chart`.",
    )
    fig: Optional[Any] = Field(
        default=None,
        description="The figure object.",
    )

    class Config:
        validate_assignment = True

    def show(self):
        """Shows the chart in PyWry, browser or notebook."""

        # TODO : this method should be handled by the ChartingManager so that
        # this model class doesn't have specific knowledge on the charting extension

        # pylint: disable=import-outside-toplevel
        if self.format == ChartFormat.plotly:
            from openbb_charting.core.openbb_figure import OpenBBFigure

            chart = OpenBBFigure()

            chart.update(self.content)

            chart.show()

        else:
            raise ValueError(f"Chart format {self.format} not supported.")
