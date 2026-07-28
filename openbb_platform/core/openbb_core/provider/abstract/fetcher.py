"""Abstract class for the fetcher."""

# ruff: noqa: S101, E501

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
    """Class property decorator."""

    def __init__(self, f):
        """Initialize decorator."""
        self.f = f

    def __get__(self, obj, owner):
        """Get the property."""
        return self.f(owner)


class Fetcher(Generic[Q, R]):
    """Abstract class for the fetcher."""

    # Tell query executor if credentials are required. Can be overridden by subclasses.
    require_credentials = True

    @staticmethod
    def transform_query(params: dict[str, Any]) -> Q:
        """Transform the params to the provider-specific query."""
        raise NotImplementedError

    @staticmethod
    async def aextract_data(query: Q, credentials: dict[str, str] | None) -> Any:
        """Asynchronously extract the data from the provider."""

    @staticmethod
    def extract_data(query: Q, credentials: dict[str, str] | None) -> Any:
        """Extract the data from the provider."""

    @staticmethod
    def transform_data(query: Q, data: Any, **kwargs) -> R | AnnotatedResult[R]:
        """Transform the provider-specific data."""
        raise NotImplementedError

    @staticmethod
    def stream_data(query: Q, data: Any, **kwargs) -> R:
        """Transform a stream of extracted items into typed data.

        Override with an ``async def`` generator for streaming fetchers; ``data``
        is the async iterator returned by ``extract_data``.

        Parameters
        ----------
        query : Q
            The validated query.
        data : Any
            Async iterator of raw items from ``extract_data``.

        Returns
        -------
        R
            Async iterator of typed data rows.
        """
        raise NotImplementedError

    def __init_subclass__(cls, *args, **kwargs):
        """Initialize the subclass."""
        super().__init_subclass__(*args, **kwargs)

        if cls.aextract_data != Fetcher.aextract_data:
            cls.extract_data = cls.aextract_data  # type: ignore[method-assign]  # ty: ignore[invalid-assignment]
        elif cls.extract_data == Fetcher.extract_data:
            raise NotImplementedError(
                "Fetcher subclass must implement either extract_data or aextract_data"
                " method. If both are implemented, aextract_data will be used as the"
                " default."
            )

    @classmethod
    async def fetch_data(
        cls,
        params: dict[str, Any],
        credentials: dict[str, str] | None = None,
        **kwargs,
    ) -> R | AnnotatedResult[R]:
        """Fetch data from a provider."""
        query = cls.transform_query(params=params)
        data = await maybe_coroutine(
            cls.extract_data, query=query, credentials=credentials, **kwargs
        )
        if cls.is_streaming:
            return cls.stream_data(query=query, data=data, **kwargs)
        return cls.transform_data(query=query, data=data, **kwargs)

    @classproperty
    def is_streaming(self) -> bool:
        """Whether this fetcher streams its results via ``stream_data``."""
        return self.stream_data is not Fetcher.stream_data

    @classproperty
    def query_params_type(self) -> Q:
        """Get the type of query."""
        return self.__orig_bases__[0].__args__[0]  # type: ignore

    @classproperty
    def return_type(self) -> R:
        """Get the type of return."""
        return_type = self.__orig_bases__[0].__args__[1]  # type: ignore
        if get_origin(return_type) is AnnotatedResult:  # pragma: no cover
            return_type = get_args(return_type)[0]
        return return_type

    @classproperty
    def data_type(self) -> D:
        """Get the type data."""
        return self._get_data_type(self.__orig_bases__[0].__args__[1])  # type: ignore

    @staticmethod
    def _get_data_type(data: Any) -> D:
        """Get the type of the data.

        Parameters
        ----------
        data : Any
            The fetcher return annotation, possibly a container of the row type.

        Returns
        -------
        D
            The row data type, unwrapped from list or async-iterator containers.
        """
        from collections.abc import (
            AsyncGenerator,
            AsyncIterable,
            AsyncIterator,
            Iterable,
            Iterator,
        )

        containers = (
            list,
            AsyncIterator,
            AsyncIterable,
            AsyncGenerator,
            Iterator,
            Iterable,
        )
        if get_origin(data) in containers:
            args = get_args(data)
            if args:
                data = args[0]
        return data

    @classmethod
    def test(
        cls,
        params: dict[str, Any],
        credentials: dict[str, str] | None = None,
        **kwargs,
    ) -> None:
        """Test the fetcher.

        This method will test each stage of the fetcher TET (Transform, Extract, Transform).

        Parameters
        ----------
        params : Dict[str, Any]
            The params to test the fetcher with.
        credentials : Optional[Dict[str, str]], optional
            The credentials to test the fetcher with, by default None.

        Raises
        ------
        AssertionError
            If any of the tests fail.
        """
        from openbb_core.app.utils_optional import require_optional

        DataFrame = require_optional("pandas").DataFrame  # type: ignore[union-attr]

        query = cls.transform_query(params=params)

        # Class Assertions
        assert isinstance(cls.require_credentials, bool), (
            "require_credentials must be a boolean."
        )

        # Query Assertions
        assert query, "Query must not be None."
        assert issubclass(type(query), cls.query_params_type), (
            f"Query type mismatch. Expected: {cls.query_params_type} Got: {type(query)}"
        )
        assert all(getattr(query, key) == value for key, value in params.items()), (
            f"Query must have the correct values. Expected: {params} Got: {query.__dict__}"
        )

        if cls.is_streaming:
            cls._test_stream(query, credentials, **kwargs)
            return

        data = run_async(
            cls.extract_data, query=query, credentials=credentials, **kwargs
        )
        result = cls.transform_data(query=query, data=data, **kwargs)
        data_type_fields = cls.data_type.model_fields

        # Data Assertions
        if not isinstance(data, DataFrame):
            assert data, "Data must not be None."
        else:
            assert not data.empty, "Data must not be empty."
        is_list = isinstance(data, list)
        if is_list:
            assert all(
                field in data[0] for field in data_type_fields if field in data[0]
            ), (
                f"Data must have the correct fields. Expected: {data_type_fields} Got: {data[0].__dict__}"
            )
            # This makes sure that the data is not transformed yet so that the
            # pipeline is implemented correctly. We can remove this assertion if we
            # want to be less strict.
            assert issubclass(type(data[0]), cls.data_type) is False, (
                f"Data must not be transformed yet. Expected: {cls.data_type} Got: {type(data[0])}"
            )
        else:
            assert all(field in data for field in data_type_fields if field in data), (
                f"Data must have the correct fields. Expected: {data_type_fields} Got: {data.__dict__}"
            )
            assert issubclass(type(data), cls.data_type) is False, (
                f"Data must not be transformed yet. Expected: {cls.data_type} Got: {type(data)}"
            )

        assert len(data) > 0, "Data must not be empty."

        # Transformed Data Assertions
        transformed_data = (
            result.result if isinstance(result, AnnotatedResult) else result
        )

        assert transformed_data, "Transformed data must not be None."

        if isinstance(transformed_data, list):
            return_type_args = cls.return_type.__args__[0]
            return_type_is_dict = (
                hasattr(return_type_args, "__origin__")
                and return_type_args.__origin__ is dict
            )
            if return_type_is_dict:  # pragma: no cover
                return_type_fields = (
                    return_type_args.__args__[1].__args__[0].model_fields
                )
                return_type = return_type_args.__args__[1].__args__[0]
            else:
                return_type_fields = (
                    return_type_args
                    if isinstance(return_type_args, type)
                    else type(return_type_args)
                ).model_fields
                return_type = return_type_args

            assert len(transformed_data) > 0, "Transformed data must not be empty."
            assert all(
                field in transformed_data[0].__dict__ for field in return_type_fields
            ), (
                f"Transformed data must have the correct fields. Expected: {return_type_fields} Got: {transformed_data[0].__dict__}"
            )
            assert issubclass(
                type(transformed_data[0]),
                cls.data_type,
            ), (
                f"Transformed data must be of the correct type. Expected: {cls.data_type} Got: {type(transformed_data[0])}"
            )
            assert issubclass(
                type(transformed_data[0]),
                return_type,
            ), (
                f"Transformed data must be of the correct type. Expected: {return_type} Got: {type(transformed_data[0])}"
            )
        else:
            return_type_fields = cls.return_type.model_fields
            assert all(
                field in transformed_data.__dict__ for field in return_type_fields
            ), (
                f"Transformed data must have the correct fields. Expected: {return_type_fields} Got: {transformed_data.__dict__}"
            )
            assert issubclass(type(transformed_data), cls.data_type), (
                f"Transformed data must be of the correct type. Expected: {cls.data_type} Got: {type(transformed_data)}"
            )
            assert issubclass(type(transformed_data), cls.return_type), (
                f"Transformed data must be of the correct type. Expected: {cls.return_type} Got: {type(transformed_data)}"
            )

    @classmethod
    def _test_stream(
        cls,
        query: Q,
        credentials: dict[str, str] | None = None,
        max_items: int = 1,
        **kwargs,
    ) -> None:
        """Test a streaming fetcher by consuming and validating stream items.

        Parameters
        ----------
        query : Q
            The validated query.
        credentials : dict[str, str] or None
            The credentials to test the fetcher with.
        max_items : int
            Number of items to consume before stopping.

        Raises
        ------
        AssertionError
            If any of the streaming tests fail.
        """
        data_type = cls.data_type
        data_type_fields = data_type.model_fields

        async def _run() -> None:
            from collections.abc import AsyncIterator
            from typing import cast

            raw = await maybe_coroutine(
                cls.extract_data, query=query, credentials=credentials, **kwargs
            )
            assert hasattr(raw, "__aiter__"), (
                "extract_data must return an async iterable for a streaming fetcher."
            )
            stream = cls.stream_data(query=query, data=raw, **kwargs)
            assert hasattr(stream, "__aiter__"), (
                "stream_data must return an async iterable for a streaming fetcher."
            )
            iterator = cast("AsyncIterator[Any]", stream).__aiter__()
            count = 0
            try:
                while count < max_items:
                    item = await iterator.__anext__()
                    assert issubclass(type(item), data_type), (
                        f"Streamed item type mismatch. Expected: {data_type} Got: {type(item)}"
                    )
                    assert all(field in item.__dict__ for field in data_type_fields), (
                        f"Streamed item must have the correct fields. Expected: {data_type_fields} Got: {item.__dict__}"
                    )
                    count += 1
            except StopAsyncIteration:
                pass
            finally:
                aclose = getattr(iterator, "aclose", None)
                if aclose is not None:
                    await aclose()
            assert count > 0, "Stream must yield at least one item."

        run_async(_run)
