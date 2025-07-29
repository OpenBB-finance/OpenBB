from typing import Any, Callable, Literal, Optional

from pydantic import BaseModel, Field, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema


class OptionsEndpoint:
    def __new__(cls, func: Callable[[], list[str]]):
        values = func()

        class DynamicOptions:
            @classmethod
            def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> CoreSchema:
                return core_schema.literal_schema(values)

            @classmethod
            def __get_pydantic_json_schema__(
                cls,
                _core_schema: CoreSchema,
                _handler: GetJsonSchemaHandler,
            ) -> JsonSchemaValue:
                return {
                    "type": "string",
                    "enum": values,
                }

        return DynamicOptions


class RenderFnParams(BaseModel):
    actionType: str = Field(..., description="Specifies the action type for the render function")


class ColumnDef(BaseModel):
    field: str = Field(..., description="The name of the field from the JSON data")
    headerName: str = Field(..., description="The display name of the column header")
    chartDataType: Optional[Literal["category", "series", "time", "excluded"]] = Field(
        None, description="Specifies how data is treated in a chart"
    )
    cellDataType: Optional[Literal["text", "number", "boolean", "date", "dateString", "object"]] = Field(
        None, description="Specifies the data type of the cell"
    )
    formatterFn: Optional[str] = Field(None, description="Specifies how to format the data")
    renderFn: Optional[Literal["greenRed", "cellOnClick", "titleCase"]] = Field(
        None, description="Specifies a rendering function for cell data"
    )
    renderFnParams: Optional[RenderFnParams] = Field(
        None, description="Required if renderFn cellOnClick is used. Specifies the parameters for the render function"
    )
    width: Optional[int] = Field(None, gt=0, description="Specifies the width of the column in pixels")
    maxWidth: Optional[int] = Field(None, gt=0, description="Specifies the maximum width of the column in pixels")
    minWidth: Optional[int] = Field(None, gt=0, description="Specifies the minimum width of the column in pixels")
    hide: Optional[bool] = Field(False, description="Hides the column from the table")
    pinned: Optional[Literal["left", "right"]] = Field(
        None, description="Pins the column to the left or right of the table"
    )
