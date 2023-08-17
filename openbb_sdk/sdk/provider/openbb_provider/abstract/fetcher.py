"""Abstract class for the fetcher."""


from typing import Any, Dict, Generic, Optional, TypeVar, get_args, get_origin

from openbb_provider.abstract.query_params import QueryParams

Q = TypeVar("Q", bound=QueryParams)
D = TypeVar("D")  # Data
R = TypeVar("R")  # Return, usually the same as Data but can be List[Data] for example


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
    def provider_query_params_type(self) -> Q:
        """Get the type of the provider query."""
        # pylint: disable=E1101
        return self.__orig_bases__[0].__args__[0]  # type: ignore

    @property
    def generic_return_type(self) -> R:
        """Get the type of the return."""
        # pylint: disable=E1101
        return self.__orig_bases__[0].__args__[1]  # type: ignore

    @property
    def provider_data_type(self) -> D:  # type: ignore
        """Get the type of the provider data."""
        # pylint: disable=E1101
        return self.get_data_type(self.__orig_bases__[0].__args__[1])  # type: ignore

    @staticmethod
    def get_data_type(data: Any) -> D:  # type: ignore
        """Get the type of the data."""
        if get_origin(data) == list:
            data = get_args(data)[0]
        return data
