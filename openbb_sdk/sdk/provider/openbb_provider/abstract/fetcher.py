"""Abstract class for the fetcher."""


from typing import Dict, Generic, List, Optional, TypeVar, Union

from openbb_provider.abstract.data import Data, QueryParams

QueryParamsType = TypeVar("QueryParamsType", bound=QueryParams)
DataType = TypeVar("DataType", bound=Data)
ProviderQueryParamsType = TypeVar("ProviderQueryParamsType", bound=QueryParams)
ProviderDataType = TypeVar("ProviderDataType", bound=Data)
ReturnType = Union[List[ProviderDataType], ProviderDataType]
UDataType = Union[List[DataType], DataType]


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
    def transform_query(
        query: QueryParamsType,
        extra_params: Optional[Dict] = None,
    ) -> ProviderQueryParamsType:
        """Transform the standard query to the provider-specific query."""
        raise NotImplementedError("Method `transform_query` not implemented.")

    @staticmethod
    def extract_data(
        query: ProviderQueryParamsType, credentials: Optional[Dict[str, str]]
    ) -> ReturnType:
        """Extract the data from the provider."""
        raise NotImplementedError("Method `extract_data` not implemented.")

    @staticmethod
    def transform_data(data: ReturnType) -> UDataType:
        """Transform the provider-specific data to the standard data."""
        raise NotImplementedError("Method `transform_query` not implemented.")

    @classmethod
    def fetch_data(
        cls,
        query: QueryParamsType,
        extra_params: Optional[Dict],
        credentials: Optional[Dict[str, str]] = None,
    ) -> UDataType:
        """Fetch data from a provider by using the OpenBB standard."""
        provider_query = cls.transform_query(query=query, extra_params=extra_params)
        provider_data = cls.extract_data(query=provider_query, credentials=credentials)
        data = cls.transform_data(data=provider_data)
        return data

    @classmethod
    def get_query_type(cls):
        """Get the type of the query."""
        return cls.transform_query.__annotations__["query"]

    @classmethod
    def get_data_type(cls):
        """Get the type of the data."""
        return cls.transform_data.__annotations__["return"]

    @classmethod
    def get_provider_query_type(cls):
        """Get the type of the provider query."""
        return cls.extract_data.__annotations__["query"]

    @classmethod
    def get_provider_data_type(cls):
        """Get the type of the provider data."""
        return cls.extract_data.__annotations__["return"]
