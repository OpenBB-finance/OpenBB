"""OBBject。"""

# pylint: disable=too-many-branches, too-many-locals, too-many-statements

from collections.abc import Callable, Hashable
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    Literal,
    TypeVar,
)

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.abstract.tagged import Tagged
from openbb_core.app.model.abstract.warning import Warning_
from openbb_core.app.model.charts.chart import Chart
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from pydantic import BaseModel, Field, PrivateAttr

if TYPE_CHECKING:
    from numpy import ndarray  # noqa
    from pandas import DataFrame  # noqa
    from openbb_core.app.query import Query  # noqa

    try:
        from polars import DataFrame as PolarsDataFrame  # type: ignore
    except ImportError:
        PolarsDataFrame = None

T = TypeVar("T")


class OBBject(Tagged, Generic[T]):
    """OpenBB 对象。"""

    accessors: ClassVar[set[str]] = set()
    _user_settings: ClassVar[BaseModel | None] = None
    _system_settings: ClassVar[BaseModel | None] = None

    results: T | None = Field(
        default=None,
        description="可序列化的结果。",
    )
    provider: str | None = Field(  # type: ignore
        default=None,
        description="提供者名称。",
    )
    warnings: list[Warning_] | None = Field(
        default=None,
        description="警告列表。",
    )
    chart: Chart | None = Field(
        default=None,
        description="图表对象。",
    )
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="额外信息。",
    )
    _route: str | None = PrivateAttr(
        default=None,
    )
    _standard_params: dict[str, Any] | None = PrivateAttr(
        default_factory=dict,
    )
    _extra_params: dict[str, Any] | None = PrivateAttr(
        default_factory=dict,
    )

    def __repr__(self) -> str:
        """对象的人类可读表示。"""
        items = [
            f"{k}: {v}"[:83] + ("..." if len(f"{k}: {v}") > 83 else "")
            for k, v in self.model_dump().items()
        ]
        return f"{self.__class__.__name__}\n\n" + "\n".join(items)

    def to_df(
        self,
        index: str | None | None = "date",
        sort_by: str | None = None,
        ascending: bool | None = None,
    ) -> "DataFrame":
        """`to_dataframe` 的别名。

        支持从以下可序列化数据格式创建 Pandas DataFrame：

        - List[BaseModel]
        - List[Dict]
        - List[List]
        - List[str]
        - List[int]
        - List[float]
        - Dict[str, Dict]
        - Dict[str, List]
        - Dict[str, BaseModel]

        其他支持的格式：
        - str

        Parameters
        ----------
        index : Optional[str]
            用作索引的列名。
        sort_by : Optional[str]
            要排序的列名。
        ascending: Optional[bool]
            按 `sort_by` 中指定的每一列升序或降序排序。

        Returns
        -------
        DataFrame
            Pandas DataFrame 数据框。
        """
        return self.to_dataframe(index=index, sort_by=sort_by, ascending=ascending)

    def to_dataframe(  # noqa: PLR0912
        self,
        index: str | None | None = "date",
        sort_by: str | None = None,
        ascending: bool | None = None,
    ) -> "DataFrame":
        """将结果字段转换为 Pandas DataFrame。

        支持从以下可序列化数据格式创建 Pandas DataFrame：

        - List[BaseModel]
        - List[Dict]
        - List[List]
        - List[str]
        - List[int]
        - List[float]
        - Dict[str, Dict]
        - Dict[str, List]
        - Dict[str, BaseModel]

        其他支持的格式：
        - str

        Parameters
        ----------
        index : Optional[str]
            用作索引的列名。
        sort_by : Optional[str]
            要排序的列名。
        ascending: Optional[bool]
            按 `sort_by` 中指定的每一列升序排序。

        Returns
        -------
        DataFrame
            Pandas DataFrame。
        """
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame, Series, concat  # noqa
        from openbb_core.app.utils import basemodel_to_df  # noqa

        def is_list_of_basemodel(items: list[T] | T) -> bool:
            return isinstance(items, list) and all(
                isinstance(item, BaseModel) for item in items
            )

        if self.results is None or not self.results:
            raise OpenBBError("未找到结果。")

        if isinstance(self.results, DataFrame):
            return self.results

        try:
            res = self.results
            df = None
            sort_columns = True

            # BaseModel
            if isinstance(res, BaseModel):
                res_dict = res.model_dump(  # pylint: disable=no-member
                    exclude_unset=True, exclude_none=True
                )
                # Model is serialized as a dict[str, list] or list[dict]
                if (
                    (
                        isinstance(res_dict, dict)
                        and res_dict
                        and all(isinstance(v, list) for v in res_dict.values())
                    )
                    or isinstance(res_dict, list)
                    and all(isinstance(item, dict) for item in res_dict)
                ):
                    df = DataFrame(res_dict)
                    sort_columns = False
                else:
                    series = Series(res_dict, name=res.__class__.__name__)
                    df = series.to_frame().reset_index()
                    sort_columns = False

            # Dict[str, Any]
            elif isinstance(res, dict):
                try:
                    df = DataFrame.from_dict(res).T
                except ValueError:
                    try:
                        df = DataFrame.from_dict(res, orient="index")
                    except ValueError:
                        series = Series(res, name="values")
                        df = series.to_frame().reset_index()
                sort_columns = False

            # List[Dict]
            elif isinstance(res, list) and len(res) == 1 and isinstance(res[0], dict):
                r = res[0]
                dict_of_df = {}

                for k, v in r.items():
                    # Dict[str, List[BaseModel]]
                    if is_list_of_basemodel(v):
                        dict_of_df[k] = basemodel_to_df(v, index)
                        sort_columns = False
                    # Dict[str, Any]
                    else:
                        dict_of_df[k] = DataFrame(v)

                df = concat(dict_of_df, axis=1)

            # List[BaseModel]
            elif is_list_of_basemodel(res):
                dt: list[Data] | Data = res  # type: ignore
                r = dt[0] if isinstance(dt, list) and len(dt) == 1 else None  # type: ignore
                if r and all(
                    prop.get("type") == "array" for prop in r.model_json_schema()["properties"].values()  # type: ignore
                ):
                    sort_columns = False
                    df = DataFrame(r.model_dump(exclude_unset=True, exclude_none=True))  # type: ignore
                else:
                    df = basemodel_to_df(dt, index)
                    sort_columns = False
            # str
            elif isinstance(res, str):
                df = DataFrame([res])
            # List[List | str | int | float] | Dict[str, Dict | List | BaseModel]
            else:
                try:
                    df = DataFrame(res)  # type: ignore[call-overload]
                except ValueError:
                    if isinstance(res, dict):
                        df = DataFrame([res])

            if df is None:
                raise OpenBBError("不支持的数据格式。")

            # Set index, if any
            if index is not None and index in df.columns:
                df.set_index(index, inplace=True)

            # Drop columns that are all NaN, but don't rearrange columns
            if sort_columns:
                df.sort_index(axis=1, inplace=True)
            df = df.dropna(axis=1, how="all")

            # Sort by specified column
            if sort_by:
                df.sort_values(
                    by=sort_by,
                    ascending=ascending if ascending is not None else True,
                    inplace=True,
                )

        except OpenBBError as e:
            raise e
        except ValueError as ve:
            raise OpenBBError(
                f"ValueError: {ve}。请确保数据格式符合预期格式。"
            ) from ve
        except TypeError as te:
            raise OpenBBError(
                f"TypeError: {te}。请检查结果中的数据类型。"
            ) from te
        except Exception as ex:
            raise OpenBBError(f"发生意外错误: {ex}") from ex

        return df

    def to_polars(self) -> "PolarsDataFrame":  # type: ignore
        """将结果字段转换为 polars dataframe。"""
        try:
            from polars import from_pandas  # type: ignore # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(
                "请安装 polars: `pip install polars pyarrow` 以使用此方法。"
            ) from exc

        return from_pandas(self.to_dataframe(index=None))

    def to_numpy(self) -> "ndarray":
        """将结果字段转换为 numpy array。"""
        return self.to_dataframe(index=None).to_numpy()

    def to_dict(
        self,
        orient: Literal[
            "dict", "list", "series", "split", "tight", "records", "index"
        ] = "list",
    ) -> dict[Hashable, Any] | list[dict[Hashable, Any]]:
        """使用 Pandas `to_dict` 选项将结果字段转换为字典。

        Parameters
        ----------
        orient : Literal["dict", "list", "series", "split", "tight", "records", "index"]
            传递给 `.to_dict()` 方法的值

        Returns
        -------
        Union[Dict[Hashable, Any], List[Dict[Hashable, Any]]]
            如果 orient 为 "records"，则为列表字典或字典列表。
        """
        df = self.to_dataframe(index=None)
        if (
            orient == "list"
            and isinstance(self.results, dict)
            and all(
                isinstance(value, dict)
                for value in self.results.values()  # pylint: disable=no-member
            )
        ):
            df = df.T
        results: dict | list = df.to_dict(orient=orient)

        if isinstance(results, dict) and orient == "list" and "index" in results:
            del results["index"]

        return results

    def to_llm(self) -> dict[Hashable, Any] | list[dict[Hashable, Any]]:
        """将结果字段转换为 LLM 兼容的输出。

        Returns
        -------
        Union[Dict[Hashable, Any], List[Dict[Hashable, Any]]]
            如果 orient 为 "records"，则为列表字典或字典列表。
        """
        df = self.to_dataframe(index=None)

        results = df.to_json(
            orient="records",
            date_format="iso",
            date_unit="s",
        )

        return results  # type: ignore

    def show(self, **kwargs: Any) -> None:
        """显示图表。"""
        # pylint: disable=no-member
        if not self.chart or not self.chart.fig:
            raise OpenBBError("未找到图表。")
        show_function: Callable = getattr(self.chart.fig, "show")
        show_function(**kwargs)

    @classmethod
    async def from_query(cls, query: "Query") -> "OBBject":
        """从查询创建 OBBject。

        Parameters
        ----------
        query : Query
            初始化的查询对象。

        Returns
        -------
        OBBject[ResultsType]
            带有结果的 OBBject。
        """
        results = await query.execute()
        if isinstance(results, AnnotatedResult):
            return cls(
                results=results.result, extra={"results_metadata": results.metadata}
            )
        return cls(results=results)
