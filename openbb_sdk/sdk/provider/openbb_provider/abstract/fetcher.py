"""Abstract class for the fetcher."""


from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams

QueryParamsType = TypeVar("QueryParamsType", bound=QueryParams)
DataType = TypeVar("DataType", bound=Data)
ProviderQueryParamsType = TypeVar("ProviderQueryParamsType", bound=QueryParams)
ProviderDataType = TypeVar("ProviderDataType", bound=Data)
ReturnType = Union[List[ProviderDataType], ProviderDataType]
GenericDataType = Union[DataType, List[DataType], Dict[str, DataType]]


class Fetcher(
    Generic[
        QueryParamsType,
        DataType,
        ProviderQueryParamsType,
        ProviderDataType,
    ]
):
    """Abstract class for the fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> ProviderQueryParamsType:
        """Transform the params to the provider-specific query."""
        raise NotImplementedError

    @staticmethod
    def extract_data(
        query: ProviderQueryParamsType, credentials: Optional[Dict[str, str]]
    ) -> ReturnType:
        """Extract the data from the provider."""
        raise NotImplementedError

    @staticmethod
    def transform_data(data: ReturnType) -> GenericDataType:
        """Transform the provider-specific data to the standard data."""
        raise NotImplementedError

    @classmethod
    def fetch_data(
        cls,
        params: Dict[str, Any],
        credentials: Optional[Dict[str, str]] = None,
    ) -> GenericDataType:
        """Fetch data from a provider by using the OpenBB standard."""
        provider_query = cls.transform_query(params=params)
        provider_data = cls.extract_data(query=provider_query, credentials=credentials)
        data = cls.transform_data(data=provider_data)
        return data

    @property
    def query_params_type(self):
        """Get the type of the query."""
        # pylint: disable=E1101
        return self.__orig_bases__[0].__args__[0]

    @property
    def data_type(self):
        """Get the type of the data."""
        # pylint: disable=E1101
        return self.__orig_bases__[0].__args__[1]

    @property
    def provider_query_params_type(self):
        """Get the type of the provider query."""
        # pylint: disable=E1101
        return self.__orig_bases__[0].__args__[2]

    @property
    def provider_data_type(self):
        """Get the type of the provider data."""
        # pylint: disable=E1101
        return self.__orig_bases__[0].__args__[3]
