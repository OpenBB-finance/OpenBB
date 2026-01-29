"""用于表示端点示例的示例类。"""

from abc import abstractmethod
from datetime import date, datetime, timedelta
from typing import Any, Literal, _GenericAlias  # type: ignore

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    model_validator,
)

QUOTE_TYPES = {str, date}


class Example(BaseModel):
    """示例模型。"""

    scope: str

    model_config = ConfigDict(validate_assignment=True)

    @abstractmethod
    def to_python(self, **kwargs) -> str:
        """返回示例的 Python 代码表示。"""


class APIEx(Example):
    """API 示例模型。"""

    scope: Literal["api"] = "api"
    description: str | None = Field(
        default=None, description="可选描述，除非参数超过 3 个"
    )
    parameters: dict[str, str | int | float | bool | list[str] | list[dict[str, Any]]]

    @computed_field  # type: ignore[misc]
    @property
    def provider(self) -> str | None:
        """从参数中返回提供者。"""
        return self.parameters.get("provider")  # type: ignore

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, values: dict) -> dict:
        """验证模型。"""
        parameters = values.get("parameters", {})
        provider = parameters.pop("provider", None)

        if provider and not isinstance(provider, str):
            raise ValueError("提供者必须是字符串。")

        if len(parameters) > 3 and not values.get("description"):
            raise ValueError(
                "当参数超过 3 个时，描述是必需的。"
            )

        return values

    @staticmethod
    def _unpack_type(type_: type) -> set:
        """从 types 中解包类型，例如 Union[List[str], int] -> {typing._GenericAlias, int}。"""
        if (
            hasattr(type_, "__args__")
            and type(type_) is not _GenericAlias  # pylint: disable=C0123
        ):
            return set().union(*map(APIEx._unpack_type, type_.__args__))  # type: ignore
        return {type_} if isinstance(type_, type) else {type(type_)}

    @staticmethod
    def _shift(i: int) -> float:
        """返回整数的变换。"""
        return 2 * (i + 1) / (2 * i) % 1 + 1

    @staticmethod
    def mock_data(
        dataset: Literal["timeseries", "panel"],
        size: int = 5,
        sample: dict[str, Any] | None = None,
        multiindex: dict[str, Any] | None = None,
    ) -> list[dict]:
        """从样本生成模拟数据。

        Parameters
        ----------
        dataset : str
            要返回的数据类型：
            - 'timeseries': 时间序列数据
            - 'panel': 面板数据（多级索引）

        size : int
            要返回的数据大小，默认为 5。
        sample : Optional[Dict[str, Any]], optional
            要返回的数据样本，默认为 None。
        multiindex_names : Optional[List[str]], optional
            多级索引的名称，默认为 None。

        Timeseries 默认样本:
        {
            "date": "2023-01-01",
            "open": 110.0,
            "high": 120.0,
            "low": 100.0,
            "close": 115.0,
            "volume": 10000,
        }

        Panel 默认样本:
        {
            "portfolio_value": 100000,
            "risk_free_rate": 0.02,
        }
        multiindex: {"asset_manager": "AM", "time": 0}

        Returns
        -------
        List[Dict]
            包含模拟数据的字典列表。
        """
        if dataset == "timeseries":
            sample = sample or {
                "date": "2023-01-01",
                "open": 110.0,
                "high": 120.0,
                "low": 100.0,
                "close": 115.0,
                "volume": 10000,
            }
            result = []
            for i in range(1, size + 1):
                s = APIEx._shift(i)
                obs = {}
                for k, v in sample.items():
                    if k == "date":
                        obs[k] = (
                            datetime.strptime(v, "%Y-%m-%d") + timedelta(days=i)
                        ).strftime("%Y-%m-%d")
                    else:
                        obs[k] = round(v * s, 2)
                result.append(obs)
            return result
        if dataset == "panel":
            sample = sample or {
                "portfolio_value": 100000.0,
                "risk_free_rate": 0.02,
            }
            multiindex = multiindex or {"asset_manager": "AM", "time": 0}
            multiindex_names = list(multiindex.keys())
            idx_1 = multiindex_names[0]
            idx_2 = multiindex_names[1]
            items_per_idx = 2
            item: dict[str, Any] = {
                "is_multiindex": True,
                "multiindex_names": str(multiindex_names),
            }
            # 迭代要创建的项目数并将它们添加到结果中
            result = []
            for i in range(1, size + 1):
                item[idx_1] = f"{idx_1}_{i}"
                for j in range(items_per_idx):
                    item[idx_2] = j
                    for k, v in sample.items():
                        if isinstance(v, str):
                            item[k] = f"{v}_{j}"
                        else:
                            item[k] = round(v * APIEx._shift(i + j), 2)
                    result.append(item.copy())
            return result
        raise ValueError(f"未找到数据集 '{dataset}'。")

    def to_python(self, **kwargs) -> str:
        """返回示例的 Python 代码表示。"""
        indentation = kwargs.get("indentation", "")
        func_path = kwargs.get("func_path", ".func_router.func_name")
        param_types: dict[str, type] = kwargs.get("param_types", {})
        prompt = kwargs.get("prompt", "")

        eg = ""
        if self.description:
            eg += f"{indentation}{prompt}# {self.description}\n"

        eg += f"{indentation}{prompt}obb{func_path}("
        for k, v in self.parameters.items():
            if k in param_types and (type_ := param_types.get(k)):
                if QUOTE_TYPES.intersection(self._unpack_type(type_)):
                    eg += f"{k}='{v}', "
                else:
                    eg += f"{k}={v}, "
            else:
                eg += f"{k}={v}, "

        eg = indentation + eg.strip(", ") + ")\n"

        return eg


class PythonEx(Example):
    """Python 示例模型。"""

    scope: Literal["python"] = "python"
    description: str
    code: list[str]

    def to_python(self, **kwargs) -> str:
        """返回示例的 Python 代码表示。"""
        indentation = kwargs.get("indentation", "")
        prompt = kwargs.get("prompt", "")

        eg = ""
        if self.description:
            eg += f"{indentation}{prompt}# {self.description}\n"

        for line in self.code:
            eg += f"{indentation}{prompt}{line}\n"

        return eg


def filter_list(
    examples: list[Example],
    providers: list[str],
) -> list[Example]:
    """过滤示例列表。"""
    return [
        e
        for e in examples
        if (isinstance(e, APIEx) and (not e.provider or e.provider in providers))
        or e.scope != "api"
    ]
