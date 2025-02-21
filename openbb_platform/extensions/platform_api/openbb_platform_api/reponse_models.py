"""OpenBB Workspace Reponse Models."""

import base64
from typing import Optional, Union

from openbb_core.provider.abstract.data import Data
from pydantic import ConfigDict, Field, model_serializer, model_validator


class MetricResponseModel(Data):
    """Metric Widget Response Model. Supply a label, value, and optional delta."""

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "title": "Metric Widget Response Model",
            "x-widget_config": {
                "$.type": "metric",
            },
        },
    )

    label: str = Field(
        description="The label to display in the metric widget.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    value: Union[int, float, str] = Field(
        description="The value to display in the metric widget.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    delta: Optional[Union[int, float, str]] = Field(
        default=None,
        description="The delta value to display in the metric widget.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )


class PdfResponseModel(Data):
    """PDF Widget Response Model. Supply either, a URL reference or content, and an optional filename."""

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "title": "PDF Widget Response Model",
            "x-widget_config": {
                "$.type": "pdf",
                "refetchInterval": False,
            },
        },
    )

    filename: Optional[str] = Field(
        default="",
        description="The filename of the PDF content.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    content: Optional[Union[str, bytes]] = Field(
        default=None,
        description="The PDF content to display in the PDF widget.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    url_reference: Optional[str] = Field(
        default=None,
        description="The URL reference to the PDF content.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, values):
        """Validate the PDF content."""

        if not values.get("content") and not values.get("url_reference"):
            raise ValueError("Either 'content' or 'url_reference' must be provided.")

        if values.get("url_reference") and "://" not in values.get("url_reference"):
            raise ValueError("Invalid URL reference provided")

        return values

    @model_serializer
    def model_serialize(self) -> dict:
        """Serialize the PDF content."""

        file_reference = None
        pdf = None

        if self.content:
            pdf = base64.b64encode(self.content).decode("utf-8")
        elif self.url_reference:
            file_reference = self.url_reference

        output = {
            "data_format": {"data_type": "pdf"},
            "content": pdf,
            "url_reference": file_reference,
            "filename": self.filename,
        }

        return {k: v for k, v in output.items() if v is not None}
