"""OpenBB 标准化 QueryParams 模型，保存查询输入参数。"""

from typing import Any

from pydantic import BaseModel, ConfigDict


class QueryParams(BaseModel):
    """OpenBB 标准化 QueryParams 模型。

    `QueryParams` 类旨在保存查询参数，将由
    提供者扩展，并在进行数据提供者请求时供 fetcher 使用。

    Key Features:
    - 别名处理：利用别名机制来保持与不同命名的兼容性
        跨各种数据格式的约定。仅在运行 `model_dump` 时应用别名。
    - Json schema extra merging：

        合并不同的 json schema extra，由提供者标识。
        Example:
            FMP fetcher:
                __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}
            Intrinio fetcher
                __json_schema_extra__ = {"symbol": {"multiple_items_allowed": False}}

            在 `symbol` 架构中创建新字段：
            {
                "type": "string",
                "description": "Symbol to get data for.",
                "fmp": {"multiple_items_allowed": True},
                "intrinio": {"multiple_items_allowed": False}
                ...,
            }

        可以使用相同或多个属性标记多个字段。
        Example:
        __json_schema_extra__ = {
            "<field_name_A>": {"foo": 123, "bar": 456},
            "<field_name_B>": {"foo": 789}
        }

    Attributes:
    __alias_dict__ (Dict[str, str]):
        将字段名称映射到其别名的字典，
        便于使用不同的命名约定。
    __json_schema_extra__ (Dict[str, List[str]]):
        要包含在 json schema extra 中的属性。
    model_config (ConfigDict):
        定义模型行为的配置字典，
        例如接受额外字段、按名称填充和别名
        生成。
    """

    __alias_dict__: dict[str, str] = {}
    __json_schema_extra__: dict[str, Any] = {}

    def __repr__(self):
        """返回 QueryParams 对象的字符串表示形式。"""
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in self.model_dump().items()])})"

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    def model_dump(self, *args, **kwargs):
        """转储模型。"""
        original = super().model_dump(*args, **kwargs)
        if self.__alias_dict__:
            return {
                self.__alias_dict__.get(key, key): value
                for key, value in original.items()
            }
        return original
