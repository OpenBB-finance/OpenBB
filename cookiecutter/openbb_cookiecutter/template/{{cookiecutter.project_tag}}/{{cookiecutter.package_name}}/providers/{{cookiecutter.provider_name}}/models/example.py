"""Example model with custom query parameters and data."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class ExampleQueryParams(QueryParams):
    """Example query parameters."""

    symbol: str = Field(description="Symbol to query.")


class ExampleData(Data):
    """Example data."""

    __alias_dict__ = {
        "date": "d",
        "open": "o",
        "high": "h",
        "low": "l",
        "close": "c",
        "volume": "v",
    }

    symbol: str = Field(description="Symbol of the row.")
    date: str = Field(description="Date of the row.")
    open: float = Field(description="Open price.")
    high: float = Field(description="High price.")
    low: float = Field(description="Low price.")
    close: float = Field(description="Close price.")
    volume: float = Field(description="Volume.")


class ExampleFetcher(Fetcher[ExampleQueryParams, list[ExampleData]]):
    """Example fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ExampleQueryParams:
        """Transform the query parameters.

        Parameters
        ----------
        params : dict[str, Any]
            The raw query parameters.

        Returns
        -------
        ExampleQueryParams
            The validated query.
        """
        return ExampleQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ExampleQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw rows for the query.

        Parameters
        ----------
        query : ExampleQueryParams
            The validated query.
        credentials : dict[str, str] | None
            The provider credentials.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        list[dict]
            The raw rows.
        """
        return [
            {
                "symbol": query.symbol,
                "d": "2023-08-23",
                "o": 2,
                "h": 5,
                "l": 1,
                "c": 4,
                "v": 5,
            },
            {
                "symbol": query.symbol,
                "d": "2023-08-24",
                "o": 4,
                "h": 7,
                "l": 3,
                "c": 6,
                "v": 10,
            },
        ]

    @staticmethod
    def transform_data(
        query: ExampleQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[ExampleData]:
        """Validate the raw rows into the data model.

        Parameters
        ----------
        query : ExampleQueryParams
            The validated query.
        data : list[dict]
            The raw rows.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        list[ExampleData]
            The validated rows.
        """
        return [ExampleData.model_validate(row) for row in data]
