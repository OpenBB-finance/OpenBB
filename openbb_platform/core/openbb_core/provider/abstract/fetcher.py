"""Fetcher 抽象类。"""

# ruff: noqa: S101, E501
# pylint: disable=E1101, C0301

from typing import (
    Any,
    Generic,
    TypeVar,
    get_args,
    get_origin,
)

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.helpers import maybe_coroutine, run_async

Q = TypeVar("Q", bound=QueryParams)
D = TypeVar("D", bound=Data)
R = TypeVar("R")  # Return, usually List[D], but can be just D for example


class classproperty:
    """类属性装饰器。"""

    def __init__(self, f):
        """初始化装饰器。"""
        self.f = f

    def __get__(self, obj, owner):
        """获取属性。"""
        return self.f(owner)


class Fetcher(Generic[Q, R]):
    """Fetcher 抽象类。"""

    # 告诉查询执行器是否需要凭据。可以被子类覆盖。
    require_credentials = True

    @staticmethod
    def transform_query(params: dict[str, Any]) -> Q:
        """将 params 转换为特定于提供者的查询。"""
        raise NotImplementedError

    @staticmethod
    async def aextract_data(query: Q, credentials: dict[str, str] | None) -> Any:
        """从提供者异步提取数据。"""

    @staticmethod
    def extract_data(query: Q, credentials: dict[str, str] | None) -> Any:
        """从提供者提取数据。"""

    @staticmethod
    def transform_data(query: Q, data: Any, **kwargs) -> R | AnnotatedResult[R]:
        """转换特定于提供者的数据。"""
        raise NotImplementedError

    def __init_subclass__(cls, *args, **kwargs):
        """初始化子类。"""
        super().__init_subclass__(*args, **kwargs)

        if cls.aextract_data != Fetcher.aextract_data:
            cls.extract_data = cls.aextract_data  # type: ignore[method-assign]
        elif cls.extract_data == Fetcher.extract_data:
            raise NotImplementedError(
                "Fetcher 子类必须实现 extract_data 或 aextract_data"
                " 方法。如果两者都实现，将使用 aextract_data 作为"
                " 默认值。"
            )

    @classmethod
    async def fetch_data(
        cls,
        params: dict[str, Any],
        credentials: dict[str, str] | None = None,
        **kwargs,
    ) -> R | AnnotatedResult[R]:
        """从提供者获取数据。"""
        query = cls.transform_query(params=params)
        data = await maybe_coroutine(
            cls.extract_data, query=query, credentials=credentials, **kwargs
        )
        return cls.transform_data(query=query, data=data, **kwargs)

    @classproperty
    def query_params_type(self) -> Q:
        """获取查询类型。"""
        # pylint: disable=E1101
        return self.__orig_bases__[0].__args__[0]  # type: ignore

    @classproperty
    def return_type(self) -> R:
        """获取返回类型。"""
        # pylint: disable=E1101
        return_type = self.__orig_bases__[0].__args__[1]  # type: ignore
        if get_origin(return_type) is AnnotatedResult:
            return_type = get_args(return_type)[0]
        return return_type

    @classproperty
    def data_type(self) -> D:  # type: ignore
        """获取类型数据。"""
        # pylint: disable=E1101
        return self._get_data_type(self.__orig_bases__[0].__args__[1])  # type: ignore

    @staticmethod
    def _get_data_type(data: Any) -> D:  # type: ignore
        """获取数据类型。"""
        if get_origin(data) is list:
            data = get_args(data)[0]
        return data

    @classmethod
    def test(
        cls,
        params: dict[str, Any],
        credentials: dict[str, str] | None = None,
        **kwargs,
    ) -> None:
        """测试 fetcher。

        此方法将测试 fetcher TET（转换、提取、转换）的每个阶段。

        Parameters
        ----------
        params : Dict[str, Any]
            用于测试 fetcher 的参数。
        credentials : Optional[Dict[str, str]], optional
            用于测试 fetcher 的凭据，默认为 None。

        Raises
        ------
        AssertionError
            如果任何测试失败。
        """
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        query = cls.transform_query(params=params)
        data = run_async(
            cls.extract_data, query=query, credentials=credentials, **kwargs
        )
        result = cls.transform_data(query=query, data=data, **kwargs)

        # 类断言
        assert isinstance(
            cls.require_credentials, bool
        ), "require_credentials 必须是布尔值。"

        # 查询断言
        assert query, "查询不能为 None。"
        assert issubclass(
            type(query), cls.query_params_type
        ), f"查询类型不匹配。预期：{cls.query_params_type} 得到：{type(query)}"
        assert all(
            getattr(query, key) == value for key, value in params.items()
        ), f"查询必须具有正确的值。预期：{params} 得到：{query.__dict__}"

        # 数据断言
        if not isinstance(data, DataFrame):
            assert data, "数据不能为 None。"
        else:
            assert not data.empty, "数据不能为空。"
        is_list = isinstance(data, list)
        if is_list:
            assert all(
                field in data[0]
                for field in cls.data_type.model_fields
                if field in data[0]
            ), f"数据必须具有正确的字段。预期：{cls.data_type.model_fields} 得到：{data[0].__dict__}"
            # 确保数据尚未转换，以便
            # 管道正确实现。如果我们
            # 想要不那么严格，我们可以删除此断言。
            assert (
                issubclass(type(data[0]), cls.data_type) is False
            ), f"数据目前不应转换。预期：{cls.data_type} 得到：{type(data[0])}"
        else:
            assert all(
                field in data for field in cls.data_type.model_fields if field in data
            ), f"数据必须具有正确的字段。预期：{cls.data_type.model_fields} 得到：{data.__dict__}"
            assert (
                issubclass(type(data), cls.data_type) is False
            ), f"数据目前不应转换。预期：{cls.data_type} 得到：{type(data)}"

        assert len(data) > 0, "数据不能为空。"

        # 转换数据断言
        transformed_data = (
            result.result if isinstance(result, AnnotatedResult) else result
        )

        assert transformed_data, "转换的数据不能为 None。"

        if isinstance(transformed_data, list):
            return_type_args = cls.return_type.__args__[0]
            return_type_is_dict = (
                hasattr(return_type_args, "__origin__")
                and return_type_args.__origin__ is dict
            )
            if return_type_is_dict:
                return_type_fields = (
                    return_type_args.__args__[1].__args__[0].model_fields
                )
                return_type = return_type_args.__args__[1].__args__[0]
            else:
                return_type_fields = return_type_args.model_fields
                return_type = return_type_args

            assert len(transformed_data) > 0, "转换的数据不能为空。"  # type: ignore
            assert all(
                field in transformed_data[0].__dict__ for field in return_type_fields  # type: ignore
            ), f"转换的数据必须具有正确的字段。预期：{return_type_fields} 得到：{transformed_data[0].__dict__}"  # type: ignore
            assert issubclass(
                type(transformed_data[0]),
                cls.data_type,  # type: ignore
            ), f"转换的数据必须是正确的类型。预期：{cls.data_type} 得到：{type(transformed_data[0])}"  # type: ignore
            assert issubclass(  # type: ignore
                type(transformed_data[0]),  # type: ignore
                return_type,
            ), f"转换的数据必须是正确的类型。预期：{return_type} 得到：{type(transformed_data[0])}"  # type: ignore
        else:
            assert all(
                field in transformed_data.__dict__
                for field in cls.return_type.model_fields
            ), f"转换的数据必须具有正确的字段。预期：{cls.return_type.model_fields} 得到：{transformed_data.__dict__}"
            assert issubclass(
                type(transformed_data), cls.data_type
            ), f"转换的数据必须是正确的类型。预期：{cls.data_type} 得到：{type(transformed_data)}"
            assert issubclass(
                type(transformed_data), cls.return_type
            ), f"转换的数据必须是正确的类型。预期：{cls.return_type} 得到：{type(transformed_data)}"
