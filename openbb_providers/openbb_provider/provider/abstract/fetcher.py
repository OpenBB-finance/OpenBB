"""Abstract class for the fetcher."""

# IMPORT STANDARD
from typing import Dict, Generic, List, Optional, TypeVar, Union

# IMPORT THIRD-PARTY
# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.abstract.provider_data import (
    ProviderData,
    ProviderQueryParams,
)

QueryParamsType = TypeVar("QueryParamsType", bound=QueryParams)
DataType = TypeVar("DataType", bound=Data)
ProviderQueryParamsType = TypeVar("ProviderQueryParamsType", bound=ProviderQueryParams)
ProviderDataType = TypeVar("ProviderDataType", bound=ProviderData)
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
    @staticmethod
    def transform_query(
        query: QueryParamsType,
        extra_params: Optional[Dict] = None,
    ) -> ProviderQueryParamsType:
        raise NotImplementedError("Method `transform_query` not implemented.")

    @staticmethod
    def extract_data(query: ProviderQueryParamsType, api_key: str) -> ReturnType:
        raise NotImplementedError("Method `extract_data` not implemented.")

    @staticmethod
    def transform_data(data: ReturnType) -> UDataType:
        raise NotImplementedError("Method `transform_query` not implemented.")

    @classmethod
    def fetch_data(
        cls, query: QueryParamsType, extra_params: Optional[Dict], api_key: str
    ) -> UDataType:
        provider_query = cls.transform_query(query=query, extra_params=extra_params)
        provider_data = cls.extract_data(query=provider_query, api_key=api_key)
        data = cls.transform_data(data=provider_data)
        return data

    @classmethod
    def fetch_provider_data(
        cls, query: QueryParamsType, extra_params: Optional[Dict], api_key: str
    ) -> ReturnType:
        provider_query = cls.transform_query(query=query, extra_params=extra_params)
        provider_data = cls.extract_data(query=provider_query, api_key=api_key)
        return provider_data

    @classmethod
    def standardized(cls, query: ProviderQueryParamsType, api_key: str) -> UDataType:
        provider_data = cls.extract_data(query=query, api_key=api_key)
        data = cls.transform_data(data=provider_data)
        return data

    @classmethod
    def simple(cls, query: ProviderQueryParamsType, api_key: str) -> ReturnType:
        provider_data = cls.extract_data(query=query, api_key=api_key)
        return provider_data

    @classmethod
    def get_query_type(cls):
        return cls.transform_query.__annotations__["query"]

    @classmethod
    def get_data_type(cls):
        return cls.transform_data.__annotations__["return"]

    @classmethod
    def get_provider_query_type(cls):
        return cls.extract_data.__annotations__["query"]

    @classmethod
    def get_provider_data_type(cls):
        return cls.extract_data.__annotations__["return"]
