from enum import Enum
from typing import Any, Dict, Optional

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
