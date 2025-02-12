from typing import Any, Callable

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
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
