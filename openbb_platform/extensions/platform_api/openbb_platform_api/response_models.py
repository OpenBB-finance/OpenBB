"""OpenBB Workspace Response Models."""

from typing import Optional, Union

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

    Supply the url_reference or content, and an optional filename.

    Fields
    ------
    filename : str
        The filename of the PDF content.
    content : bytes
        The PDF content to display in the PDF widget.
    url_reference : str
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
    url_reference: Optional[str] = Field(
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
        file_reference = getattr(values, "url_reference", None)
        filename = getattr(values, "filename", "")

        if not content and not file_reference:
            raise ValueError("Either 'content' or 'url_reference' must be provided.")

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
            values.url_reference = file_reference
        elif hasattr(values, "url_reference"):
            del values.url_reference
        values.data_format = {"data_type": "pdf", "filename": filename}

        return values
