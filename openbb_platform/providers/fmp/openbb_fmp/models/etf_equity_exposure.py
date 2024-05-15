"""FMP ETF Equity Exposure Model."""

# pylint: disable=unused-argument

import asyncio
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_equity_exposure import (
    EtfEquityExposureData,
    EtfEquityExposureQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_fmp.utils.helpers import response_callback
from pydantic import field_validator


class FMPEtfEquityExposureQueryParams(EtfEquityExposureQueryParams):
    """
    FMP ETF Equity Exposure Query Params.

    Source: https://site.financialmodelingprep.com/developer/docs/etf-stock-exposure-api/
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class FMPEtfEquityExposureData(EtfEquityExposureData):
    """FMP ETF Equity Exposure Data."""

    __alias_dict__ = {
        "equity_symbol": "assetExposure",
        "etf_symbol": "etfSymbol",
        "shares": "sharesNumber",
        "weight": "weightPercentage",
        "market_value": "marketValue",
    }

    @field_validator("weight", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize percent values."""
        return float(v) / 100 if v else None


class FMPEtfEquityExposureFetcher(
    Fetcher[FMPEtfEquityExposureQueryParams, List[FMPEtfEquityExposureData]]
):
    """FMP ETF Equity Exposure Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEtfEquityExposureQueryParams:
        """Transform the query."""
        return FMPEtfEquityExposureQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEtfEquityExposureQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = query.symbol.split(",")
        results: List[dict] = []

        async def get_one(symbol):
            """Get one symbol."""
            url = f"https://financialmodelingprep.com/api/v3/etf-stock-exposure/{symbol}?apikey={api_key}"
            response = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if not response:
                warn(f"No results found for {symbol}.")
            if response:
                results.extend(response)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No data was found for the given symbols.")

        return results

    @staticmethod
    def transform_data(
        query: FMPEtfEquityExposureQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FMPEtfEquityExposureData]:
        """Return the transformed data."""
        return [
            FMPEtfEquityExposureData.model_validate(d)
            for d in sorted(data, key=lambda x: x["marketValue"], reverse=True)
        ]
