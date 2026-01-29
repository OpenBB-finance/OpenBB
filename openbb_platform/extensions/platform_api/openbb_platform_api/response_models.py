"""OpenBB Workspace 响应模型。"""

from typing import Any

from openbb_core.provider.abstract.data import Data
from pydantic import ConfigDict, Field, model_validator


class MetricResponseModel(Data):
    """
    指标挂件响应模型。

    提供标签、值和可选的 delta。

    Fields
    ------
    label : str
        在指标挂件中显示的标签。
    value : int, float, or str
        在指标挂件中显示的值。
    delta : int, float, or str
        在指标挂件中显示的（可选）delta 值。

    Returns
    -------
    object
        具有标签、值和可选 delta 值的对象。
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
    value: int | float | str = Field(
        description="The value to display in the metric widget.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    delta: int | float | str | None = Field(
        default=None,
        description="The delta value to display in the metric widget.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )


class PdfResponseModel(Data):
    """
    PDF 挂件响应模型。

    提供 url 或内容，以及可选的文件名。

    Fields
    ------
    filename : str
        PDF 内容的文件名。
    content : bytes
        在 PDF 挂件中显示的 PDF 内容。
    url : str
        PDF 的 URL 引用

    Returns
    -------
    object
        具有序列化为 Base64 编码字符串的 PDF 内容的对象。

    Raises
    ------
    ValueError
        如果未提供 'content' 或 'url_reference'，或者提供了无效的 URL 引用。
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

    filename: str | None = Field(
        default="",
        description="The filename of the PDF content.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    content: str | bytes | None = Field(
        default=None,
        description="The PDF content to display in the PDF widget.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    url: str | None = Field(
        default=None,
        description="The URL reference to the PDF content.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    data_format: dict | None = Field(
        default=None,
        description="Leave this field empty. This is populated by the model_validator.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )

    @model_validator(mode="after")
    @classmethod
    def validate_model(cls, values) -> "PdfResponseModel":
        """验证 PDF 内容。"""
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
    """Omni 挂件响应模型。

    提供内容，以及可选的 `parse_as` 字段。

    Fields
    ------
    content : Any
        在 Omni 挂件中显示的内容。
    parse_as : Optional[str]
        要解析为的内容类型。 "table"、"chart" 或 "text" 之一。
        尝试根据内容类型自动设置此属性，但可以覆盖。

    Returns
    -------
    object
        符合 API 验证输出要求的对象。

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
    parse_as: str | None = Field(
        default=None,
        description="The type of content to parse as. One of 'table', 'chart', or 'text'.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    data_format: dict | None = Field(
        default=None,
        description="Leave this field empty. This is populated by the model_validator.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )

    @model_validator(mode="after")
    @classmethod
    def validate_model(cls, values) -> "OmniWidgetResponseModel":
        """验证 Omni 挂件内容。"""
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
