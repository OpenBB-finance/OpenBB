"""OpenBB 标准化数据模型。"""

from typing import Annotated

from pydantic import (
    AliasGenerator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    alias_generators,
    model_validator,
)


def check_int(v: int) -> int:
    """检查该值是否为 int。"""
    try:
        return int(v)
    except ValueError as exc:
        raise TypeError("value must be an int") from exc


ForceInt = Annotated[int, BeforeValidator(check_int)]


class Data(BaseModel):
    """
    OpenBB 标准化数据模型。

    `Data` 类是一个灵活的 Pydantic 模型，旨在适应各种数据结构
    用于 OpenBB 的数据处理管道，因为它的结构是为了支持动态字段定义。

    该模型利用 Pydantic 强大的验证功能来确保数据完整性，同时
    提供处理模型中未明确定义的额外字段的灵活性
    架构。这使得 `Data` 类非常适合处理具有不同结构的数据集
    结构或来自异构来源。

    Key Features:
    - 动态字段支持：可以动态处理模型中未预定义的字段，
        允许在处理不同数据形状时具有极大的灵活性。
    - 别名处理：利用别名机制来保持与不同命名的兼容性
        跨各种数据格式的约定。

    Usage:
    `Data` 类可以使用与预期数据字段对应的关键字参数进行实例化。
    它还可以解析和验证来自 JSON 或其他可序列化格式的数据，并
    将它们转换为 `Data` 实例，以便于操作和访问。

    Example:
        # Direct instantiation
        data_record = Data(name="OpenBB", value=42)

        # Conversion from a dictionary
        data_dict = {"name": "OpenBB", "value": 42}
        data_record = Data(**data_dict)

    该类具有高度可扩展性，可以通过子类化来创建针对以下情况量身定制的更具体的模型
    特定数据集或领域，同时仍然受益于提供的基本功能
    `Data` 类。

    Attributes:
        __alias_dict__ (Dict[str, str]):
            将字段名称映射到其别名的字典，
            便于使用不同的命名约定。
        model_config (ConfigDict):
            定义模型行为的配置字典，
            例如接受额外字段、按名称填充和别名
            生成。
    """

    __alias_dict__: dict[str, str] = {}

    def __repr__(self):
        """返回对象的字符串表示形式。"""
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in super().model_dump().items()])})"

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        strict=False,
        alias_generator=AliasGenerator(
            validation_alias=alias_generators.to_camel,
            serialization_alias=alias_generators.to_snake,
        ),
    )

    @model_validator(mode="before")
    @classmethod
    def _use_alias(cls, values):
        """为错误 locs 使用别名。"""
        # set the alias dict values keys
        aliases = {orig: alias for alias, orig in cls.__alias_dict__.items()}
        if aliases and isinstance(values, dict):
            return {aliases.get(k, k): v for k, v in values.items()}

        return values
