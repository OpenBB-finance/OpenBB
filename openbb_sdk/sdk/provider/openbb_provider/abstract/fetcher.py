"""Abstract class for the fetcher."""


from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

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
        """Transform the provider-specific data."""
        raise NotImplementedError

    @classmethod
    def fetch_data(
        cls,
        params: Dict[str, Any],
        credentials: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> GenericDataType:
        """Fetch data from a provider."""
        query = cls.transform_query(params=params)
        data = cls.extract_data(query=query, credentials=credentials, **kwargs)
        results = cls.transform_data(data=data)
        return results

    @property
    def query_params_type(self):
        """Get the type of the query."""
        # pylint: disable=E1101
        return self.__orig_bases__[0].__args__[0]

    @property
    def data_type(self):
        """Get the type of the data."""
        # pylint: disable=E1101
        return self.get_data_type(self.__orig_bases__[0].__args__[1])

    @property
    def provider_query_params_type(self):
        """Get the type of the provider query."""
        # pylint: disable=E1101
        return self.__orig_bases__[0].__args__[2]

    @property
    def provider_data_type(self):
        """Get the type of the provider data."""
        # pylint: disable=E1101
        return self.get_data_type(self.__orig_bases__[0].__args__[3])

    # TODO: Create abstract class attribute for generic return type
    @property
    def generic_return_type(self):
        """Get the type of the return."""
        # pylint: disable=E1101
        return self.__orig_bases__[0].__args__[1]

    @staticmethod
    def get_data_type(data: GenericDataType) -> DataType:
        """Get the type of the data."""
        if get_origin(data) == list:
            data = get_args(data)[0]
        return data
