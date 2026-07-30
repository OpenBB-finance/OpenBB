"""Cboe Futures Instruments Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_instruments import (
    FuturesInstrumentsData,
    FuturesInstrumentsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class CboeFuturesInstrumentsQueryParams(FuturesInstrumentsQueryParams):
    """Cboe Futures Instruments Query.

    Source: https://www.cboe.com/
    """


class CboeFuturesInstrumentsData(FuturesInstrumentsData):
    """Cboe Futures Instruments Data."""

    future_root: str = Field(description="The root symbol of the futures product.")
    name: str | None = Field(
        default=None, description="The name of the futures product."
    )
    family: str | None = Field(default=None, description="The product family.")
    underlying: str | None = Field(
        default=None, description="The underlying symbol of the futures product."
    )


class CboeFuturesInstrumentsFetcher(
    Fetcher[
        CboeFuturesInstrumentsQueryParams,
        list[CboeFuturesInstrumentsData],
    ]
):
    """Transform the query, extract and transform the data from the Cboe endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CboeFuturesInstrumentsQueryParams:
        """Transform the query."""
        return CboeFuturesInstrumentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CboeFuturesInstrumentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Cboe endpoint.

        Raises
        ------
        EmptyDataError
            If the futures roots directory returned empty.
        """
        from openbb_cboe.utils.helpers import list_futures

        data = await list_futures()

        if not data:
            raise EmptyDataError("The futures roots directory returned empty.")

        return data

    @staticmethod
    def transform_data(
        query: CboeFuturesInstrumentsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CboeFuturesInstrumentsData]:
        """Transform the data to the model."""
        return [CboeFuturesInstrumentsData.model_validate(record) for record in data]
