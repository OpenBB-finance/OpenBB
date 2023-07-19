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
        query: ProviderQueryParamsType, api_key: Optional[str]
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
        api_key: Optional[str],
    ) -> UDataType:
        """Fetch data from a provider by using the OpenBB standard."""
        provider_query = cls.transform_query(query=query, extra_params=extra_params)
        provider_data = cls.extract_data(query=provider_query, api_key=api_key)
        data = cls.transform_data(data=provider_data)
        return data

    @classmethod
    def fetch_provider_data(
        cls,
        query: QueryParamsType,
        extra_params: Optional[Dict],
        api_key: Optional[str],
    ) -> ReturnType:
        """Fetch data from a provider and return raw data from the provider."""
        provider_query = cls.transform_query(query=query, extra_params=extra_params)
        provider_data = cls.extract_data(query=provider_query, api_key=api_key)
        return provider_data

    @classmethod
    def standardized(
        cls, query: ProviderQueryParamsType, api_key: Optional[str]
    ) -> UDataType:
        """Use a provider-specific query to obtain standardized data."""
        provider_data = cls.extract_data(query=query, api_key=api_key)
        data = cls.transform_data(data=provider_data)
        return data

    @classmethod
    def simple(
        cls, query: ProviderQueryParamsType, api_key: Optional[str]
    ) -> ReturnType:
        """Use a provider-specific query to obtain raw data from the provider."""
        provider_data = cls.extract_data(query=query, api_key=api_key)
        return provider_data

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
