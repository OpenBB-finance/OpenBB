"""Abstract class for the fetcher."""


from typing import Any, Dict, Generic, Optional, TypeVar, get_args, get_origin

from openbb_provider.abstract.query_params import QueryParams

Q = TypeVar("Q", bound=QueryParams)
D = TypeVar("D")  # Data
R = TypeVar("R")  # Return, usually List[D], but can be just D for example


class Fetcher(Generic[Q, R]):
    """Abstract class for the fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> Q:
        """Transform the params to the provider-specific query."""
        raise NotImplementedError

    @staticmethod
    def extract_data(query: Q, credentials: Optional[Dict[str, str]]) -> Any:
        """Extract the data from the provider."""
        raise NotImplementedError

    @staticmethod
    def transform_data(data: Any) -> R:
        """Transform the provider-specific data."""
        raise NotImplementedError

    @classmethod
    def fetch_data(
        cls,
        params: Dict[str, Any],
        credentials: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> R:
        """Fetch data from a provider."""
        query = cls.transform_query(params=params)
        data = cls.extract_data(query=query, credentials=credentials, **kwargs)
        return cls.transform_data(data=data)

    @property
    def query_params(self) -> Q:
        """Get the type of query."""
        # pylint: disable=E1101
        return self.__orig_bases__[0].__args__[0]  # type: ignore

    @property
    def return_type(self) -> R:
        """Get the type of return."""
        # pylint: disable=E1101
        return self.__orig_bases__[0].__args__[1]  # type: ignore

    @property
    def data(self) -> D:  # type: ignore
        """Get the type data."""
        # pylint: disable=E1101
        return self._get_data_type(self.__orig_bases__[0].__args__[1])  # type: ignore

    @staticmethod
    def _get_data_type(data: Any) -> D:  # type: ignore
        """Get the type of the data."""
        if get_origin(data) == list:
            data = get_args(data)[0]
        return data
