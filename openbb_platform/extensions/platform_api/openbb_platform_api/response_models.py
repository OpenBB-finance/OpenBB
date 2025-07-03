"""OpenBB Workspace Response Models."""

from typing import Any, Optional, Union

from openbb_core.provider.abstract.data import Data
from pydantic import ConfigDict, Field, model_validator


class MetricResponseModel(Data):
    """
    Metric Widget Response Model.

    Supply a label, value, and optional delta.

    Fields
    ------
    label : str
        The label to display in the metric widget.
    value : int, float, or str
        The value to display in the metric widget.
    delta : int, float, or str
        The, optional, delta value to display in the metric widget.

    Returns
    -------
    object
        Object with the label, value, and optional delta value.
    """

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "title": "Metric Widget Response Model",
            "x-widget_config": {
                "$.type": "metric",
                "$.category": "Metric",
                "$.searchCategory": "Metric",
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
    """
    PDF Widget Response Model.

    Supply the url or content, and an optional filename.

    Fields
    ------
    filename : str
        The filename of the PDF content.
    content : bytes
        The PDF content to display in the PDF widget.
    url : str
        The URL reference to the PDF

    Returns
    -------
    object
        Object with the PDF content serialized as a Base64 encoded string.

    Raises
    ------
    ValueError
        If neither 'content' or 'url_reference' is provided, or an invalid URL reference is provided.
    """

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "x-widget_config": {
                "$.type": "pdf",
                "$.refetchInterval": False,
                "$.category": "File",
                "$.subCategory": "PDF",
                "$.searchCategory": "File",
            }
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
    url: Optional[str] = Field(
        default=None,
        description="The URL reference to the PDF content.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    data_format: Optional[dict] = Field(
        default=None,
        description="Leave this field empty. This is populated by the model_validator.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )

    @model_validator(mode="after")
    @classmethod
    def validate_model(cls, values) -> "PdfResponseModel":
        """Validate the PDF content."""
        # pylint: disable=import-outside-toplevel
        import base64  # noqa
        from io import BytesIO

        content = getattr(values, "content", None)
        file_reference = getattr(values, "url", None)
        filename = getattr(values, "filename", "")

        if not content and not file_reference:
            raise ValueError("Either 'content' or 'url' must be provided.")

        if file_reference and "://" not in file_reference:
            raise ValueError("Invalid URL reference provided")

        if content:
            pdf = (
                base64.b64encode(BytesIO(content).getvalue()).decode("utf-8")
                if isinstance(content, bytes)
                else content
            )

        values.content = pdf
        if file_reference:
            values.url = file_reference
        elif hasattr(values, "url"):
            del values.url
        values.data_format = {"data_type": "pdf", "filename": filename}

        return values


class OmniWidgetResponseModel(Data):
    """Omni Widget Response Model.

    Supply the content, and optionally the `parse_as` field.

    Fields
    ------
    content : Any
        The content to display in the Omni widget.
    parse_as : Optional[str]
        The type of content to parse as. One of "table", "chart", or "text".
        Attempts to set this automatically based on the content type, but can be overridden.

    Returns
    -------
    object
        Object that conforms to the validated output requirements of the API.

    Example
    -------
    >>> from openbb_platform_api.main import app
    >>> @app.get("/omni_widget", response_model=OmniWidgetResponseModel)
    >>> async def get_omni_widget():
    >>>     return {"content": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}
    """

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "x-widget_config": {
                "$.type": "omni",
            }
        },
    )

    content: Any = Field(
        description="The content to display in the Omni widget.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    parse_as: Optional[str] = Field(
        default=None,
        description="The type of content to parse as. One of 'table', 'chart', or 'text'.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    data_format: Optional[dict] = Field(
        default=None,
        description="Leave this field empty. This is populated by the model_validator.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )

    @model_validator(mode="after")
    @classmethod
    def validate_model(cls, values) -> "OmniWidgetResponseModel":
        """Validate the Omni widget content."""
        # pylint: disable=import-outside-toplevel
        import json  # noqa
        import re
        import pandas as pd

        content = getattr(values, "content", None)

        if content is None:
            raise ValueError("Content cannot be empty.")

        parse_as = getattr(values, "parse_as", None)

        if parse_as and parse_as not in ("table", "chart", "text"):
            raise ValueError(
                "Invalid parse_as value. Must be one of 'table', 'chart', or 'text'."
            )

        # If parameter was supplied, assume the data is formatted correctly.
        if content and parse_as:
            data_format = {
                "data_type": "object",
                "parse_as": parse_as,
            }
            values.data_format = data_format
            del values.parse_as

            return values

        if content.__class__.__name__ == "Figure":
            values.parse_as = "chart"
            try:
                content = content.to_json()
            except Exception as e:
                raise ValueError("Failed to convert chart to JSON") from e
            values.content = content
        elif isinstance(content, dict) and "layout" in content and "data" in content:
            values.parse_as = "chart"
        elif isinstance(content, list) and all(
            isinstance(item, dict) for item in content
        ):
            values.parse_as = "table"
        elif isinstance(content, pd.DataFrame):
            values.parse_as = "table"
            try:
                content = json.loads(content.to_json(orient="records"))
            except Exception as e:
                raise ValueError("Failed to convert DataFrame to JSON") from e
            values.content = content
        elif isinstance(content, dict) and all(
            isinstance(v, list) for v in content.values()
        ):
            values.parse_as = "table"
            try:
                df = pd.DataFrame(content)
                content = json.loads(df.to_json(orient="records"))
            except Exception as e:
                raise ValueError(
                    "Failed to convert dictionary of lists to list of records"
                ) from e
            values.content = content
        elif isinstance(content, str) and content.strip():  # pylint: disable=R0916
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                # Remove trailing commas in objects and arrays
                try:
                    cleaned_content = re.sub(r",(\s*[}\]])", r"\1", content)
                    content = json.loads(cleaned_content)
                except json.JSONDecodeError:
                    pass

            values.parse_as = "table" if isinstance(content, (list, dict)) else "text"
            values.content = content
        else:
            values.parse_as = "text"

        data_format = {
            "data_type": "object",
            "parse_as": parse_as if parse_as else values.parse_as,
        }
        values.data_format = data_format

        del values.parse_as

        return values
