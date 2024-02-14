"""FMP ETF Equity Exposure Model."""

# pylint: disable=unsed-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_equity_exposure import (
    EtfEquityExposureData,
    EtfEquityExposureQueryParams,
)
from openbb_core.provider.utils.helpers import amake_requests
from pydantic import field_validator


class FMPEtfEquityExposureQueryParams(EtfEquityExposureQueryParams):
    """
    FMP ETF Equity Exposure Query Params.

    Source: https://site.financialmodelingprep.com/developer/docs/etf-stock-exposure-api/
    """


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

        urls = [
            f"https://financialmodelingprep.com/api/v3/etf-stock-exposure/{symbol}?apikey={api_key}"
            for symbol in symbols
        ]

        return await amake_requests(urls, **kwargs)

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
