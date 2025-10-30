"""FMP Price Performance Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.recent_performance import (
    RecentPerformanceData,
    RecentPerformanceQueryParams,
)
from pydantic import model_validator


class FMPPricePerformanceQueryParams(RecentPerformanceQueryParams):
    """FMP Price Performance Query.

    Source: https://site.financialmodelingprep.com/developer/docs#quote-change
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class FMPPricePerformanceData(RecentPerformanceData):
    """FMP Price Performance Data."""

    __alias_dict__ = {
        "one_day": "1D",
        "one_week": "5D",
        "one_month": "1M",
        "three_month": "3M",
        "six_month": "6M",
        "one_year": "1Y",
        "three_year": "3Y",
        "five_year": "5Y",
        "ten_year": "10Y",
    }

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Replace zero with None and convert percents to normalized values."""
        if isinstance(values, dict):
            for k, v in values.items():
                if k != "symbol":
                    values[k] = None if v == 0 else float(v) / 100
        return values


class FMPPricePerformanceFetcher(
    Fetcher[
        FMPPricePerformanceQueryParams,
        list[FMPPricePerformanceData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPPricePerformanceQueryParams:
        """Transform the query params."""
        return FMPPricePerformanceQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPPricePerformanceQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_urls

        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = query.symbol.upper().split(",")
        chunk_size = 200
        chunks = [
            symbols[i : i + chunk_size] for i in range(0, len(symbols), chunk_size)
        ]
        base_url = "https://financialmodelingprep.com/stable/stock-price-change?symbol="
        urls = [f"{base_url}{','.join(chunk)}&apikey={api_key}" for chunk in chunks]

        return await get_data_urls(urls, **kwargs)  # type: ignore

    @staticmethod
    def transform_data(
        query: FMPPricePerformanceQueryParams,
        data: list,
        **kwargs: Any,
    ) -> list[FMPPricePerformanceData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        import warnings

        symbols = query.symbol.upper().split(",")
        symbols = list(dict.fromkeys(symbols))
        if len(data) != len(symbols):
            data_symbols = [d["symbol"] for d in data]
            missing_symbols = [
                symbol for symbol in symbols if symbol not in data_symbols
            ]
            warnings.warn(f"Missing data for symbols: {missing_symbols}")

        return [FMPPricePerformanceData.model_validate(i) for i in data]
