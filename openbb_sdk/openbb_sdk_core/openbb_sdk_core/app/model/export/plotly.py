from typing import Any, Dict

from openbb_sdk_core.app.model.abstract.export import Export, ExportFormat
from pydantic import Field


class Plotly(Export):
    content: Dict[Any, Any]  # type: ignore
    export_format: ExportFormat = Field(default=ExportFormat.plotly, const=True)

    class Config:
        validate_assignment = True
