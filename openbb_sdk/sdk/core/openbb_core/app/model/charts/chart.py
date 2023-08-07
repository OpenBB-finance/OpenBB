from enum import Enum
from typing import Any, Dict, Optional

from openbb_core.app.model.abstract.error import Error
from pydantic import ConfigDict, BaseModel


class ChartFormat(str, Enum):
    plotly = "plotly"


class Chart(BaseModel):
    content: Optional[Dict[str, Any]] = None
    format: Optional[ChartFormat] = ChartFormat.plotly
    error: Optional[Error] = None
    model_config = ConfigDict(validate_assignment=True)

    def show(self):
        """Shows the chart in PyWry, browser or notebook."""

        if self.format != ChartFormat.plotly:
            raise ValueError(f"Chart format {self.format} not supported.")
        from openbb_charting.core.openbb_figure import OpenBBFigure

        chart = OpenBBFigure()

        chart.update(self.content)

        chart.show()
