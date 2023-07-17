from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel

from openbb_core.app.model.abstract.error import Error


class ChartFormat(str, Enum):
    plotly = "plotly"


class Chart(BaseModel):
    content: Dict[str, Any]
    format: Optional[ChartFormat] = ChartFormat.plotly
    error: Optional[Error] = None

    class Config:
        validate_assignment = True

    def show(self):
        """Shows the chart in PyWry, browser or notebook."""

        #pylint: disable=import-outside-toplevel
        if self.format == ChartFormat.plotly:
            from openbb_charting.backend.plotly_helper import (
                OpenBBFigure,
            )

            chart = OpenBBFigure()

            chart.update(self.content)

            chart.show()

        else:
            raise ValueError(f"Chart format {self.format} not supported.")
