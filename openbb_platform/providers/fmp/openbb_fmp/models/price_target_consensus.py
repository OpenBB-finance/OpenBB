"""FMP Price Target Consensus Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.price_target_consensus import (
    PriceTargetConsensusData,
    PriceTargetConsensusQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import field_validator


class FMPPriceTargetConsensusQueryParams(PriceTargetConsensusQueryParams):
    """FMP Price Target Consensus Query.

    Source: https://site.financialmodelingprep.com/developer/docs#price-target-consensus
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def check_symbol(cls, value):
        """Check the symbol."""
        if not value:
            raise OpenBBError("Symbol is a required field for FMP.")
        return value


class FMPPriceTargetConsensusData(PriceTargetConsensusData):
    """FMP Price Target Consensus Data."""


class FMPPriceTargetConsensusFetcher(
    Fetcher[
        FMPPriceTargetConsensusQueryParams,
        list[FMPPriceTargetConsensusData],
    ]
):
    """FMP Price Target Consensus Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPPriceTargetConsensusQueryParams:
        """Transform the query params."""
        return FMPPriceTargetConsensusQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPPriceTargetConsensusQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import warnings
        from openbb_fmp.utils.helpers import get_data_urls

        api_key = credentials.get("fmp_api_key") if credentials else ""

        symbols = query.symbol.split(",")  # type: ignore
        results: list[dict] = []

        async def get_one(symbol):
            """Get data for one symbol."""
            url = f"https://financialmodelingprep.com/stable/price-target-consensus?symbol={symbol}&apikey={api_key}"
            result = await get_data_urls([url], **kwargs)

            if not result or len(result) == 0:
                warnings.warn(f"Symbol Error: No data found for {symbol}")

            if result:
                results.extend(result)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No data returned for the given symbols.")

        return sorted(
            results,
            key=(lambda item: (symbols.index(item.get("symbol", len(symbols))))),
        )

    @staticmethod
    def transform_data(
        query: FMPPriceTargetConsensusQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FMPPriceTargetConsensusData]:
        """Return the transformed data."""
        return [FMPPriceTargetConsensusData.model_validate(d) for d in data]
