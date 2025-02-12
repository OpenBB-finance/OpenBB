"""FMP Equity Screener Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_screener import (
    EquityScreenerData,
    EquityScreenerQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_fmp.utils.definitions import EXCHANGES, SECTORS, Exchanges, Sectors
from pydantic import Field


class FMPEquityScreenerQueryParams(EquityScreenerQueryParams):
    """FMP Equity Screener Query."""

    __alias_dict__ = {
        "mktcap_min": "marketCapMoreThan",
        "mktcap_max": "marketCapLowerThan",
        "price_min": "priceMoreThan",
        "price_max": "priceLowerThan",
        "beta_min": "betaMoreThan",
        "beta_max": "betaLowerThan",
        "volume_min": "volumeMoreThan",
        "volume_max": "volumeLowerThan",
        "dividend_min": "dividendMoreThan",
        "dividend_max": "dividendLowerThan",
        "is_active": "isActivelyTrading",
        "is_etf": "isEtf",
    }

    __json_schema_extra__ = {
        "exchange": {
            "multiple_items_allowed": False,
            "choices": EXCHANGES,
        },
        "sector": {
            "multiple_items_allowed": False,
            "choices": SECTORS,
        },
    }

    mktcap_min: Optional[int] = Field(
        default=None, description="Filter by market cap greater than this value."
    )
    mktcap_max: Optional[int] = Field(
        default=None,
        description="Filter by market cap less than this value.",
    )
    price_min: Optional[float] = Field(
        default=None,
        description="Filter by price greater than this value.",
    )
    price_max: Optional[float] = Field(
        default=None,
        description="Filter by price less than this value.",
    )
    beta_min: Optional[float] = Field(
        default=None,
        description="Filter by a beta greater than this value.",
    )
    beta_max: Optional[float] = Field(
        default=None,
        description="Filter by a beta less than this value.",
    )
    volume_min: Optional[int] = Field(
        default=None,
        description="Filter by volume greater than this value.",
    )
    volume_max: Optional[int] = Field(
        default=None,
        description="Filter by volume less than this value.",
    )
    dividend_min: Optional[float] = Field(
        default=None,
        description="Filter by dividend amount greater than this value.",
    )
    dividend_max: Optional[float] = Field(
        default=None,
        description="Filter by dividend amount less than this value.",
    )
    is_etf: Optional[bool] = Field(
        default=False,
        description="If true, returns only ETFs.",
    )
    is_active: Optional[bool] = Field(
        default=True,
        description="If false, returns only inactive tickers.",
    )
    sector: Optional[Sectors] = Field(default=None, description="Filter by sector.")
    industry: Optional[str] = Field(default=None, description="Filter by industry.")
    country: Optional[str] = Field(
        default=None, description="Filter by country, as a two-letter country code."
    )
    exchange: Optional[Exchanges] = Field(
        default=None, description="Filter by exchange."
    )
    limit: Optional[int] = Field(
        default=50000, description="Limit the number of results to return."
    )


class FMPEquityScreenerData(EquityScreenerData):
    """FMP Equity Screener Data."""

    __alias_dict__ = {
        "name": "companyName",
        "market_cap": "marketCap",
        "last_annual_dividend": "lastAnnualDividend",
        "exchange": "exchangeShortName",
        "exchange_name": "exchange",
        "is_etf": "isEtf",
        "actively_trading": "isActivelyTrading",
    }

    market_cap: Optional[int] = Field(
        description="The market cap of ticker.", default=None
    )
    sector: Optional[str] = Field(
        description="The sector the ticker belongs to.", default=None
    )
    industry: Optional[str] = Field(
        description="The industry ticker belongs to.", default=None
    )
    beta: Optional[float] = Field(description="The beta of the ETF.", default=None)
    price: Optional[float] = Field(description="The current price.", default=None)
    last_annual_dividend: Optional[float] = Field(
        description="The last annual amount dividend paid.",
        default=None,
    )
    volume: Optional[int] = Field(
        description="The current trading volume.", default=None
    )
    exchange: Optional[str] = Field(
        description="The exchange code the asset trades on.",
        default=None,
    )
    exchange_name: Optional[str] = Field(
        description="The full name of the primary exchange.",
        default=None,
    )
    country: Optional[str] = Field(
        description="The two-letter country abbreviation where the head office is located.",
        default=None,
    )
    is_etf: Optional[Literal[True, False]] = Field(
        description="Whether the ticker is an ETF.", default=None
    )
    actively_trading: Optional[Literal[True, False]] = Field(
        description="Whether the ETF is actively trading.",
        default=None,
    )


class FMPEquityScreenerFetcher(
    Fetcher[
        FMPEquityScreenerQueryParams,
        List[FMPEquityScreenerData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEquityScreenerQueryParams:
        """Transform the query."""
        return FMPEquityScreenerQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEquityScreenerQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from copy import deepcopy  # noqa
        from openbb_fmp.utils.helpers import create_url, get_data  # noqa

        api_key = credentials.get("fmp_api_key") if credentials else ""
        _query = deepcopy(query)
        if _query.sector is not None:
            _query.sector = _query.sector.replace("_", " ").title()
        url = create_url(
            version=3,
            endpoint="stock-screener",
            api_key=api_key,
            query=_query,
            exclude=["query", "is_symbol", "industry"],
        ).replace(" ", "%20")

        return await get_data(url, **kwargs)  # type: ignore

    @staticmethod
    def transform_data(
        query: FMPEquityScreenerQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEquityScreenerData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        if not data:
            raise EmptyDataError("The request was returned empty.")
        results = DataFrame(data)
        if query.industry:
            results = results[
                results["sector"].str.contains(query.industry, case=False)
                | results["industry"].str.contains(query.industry, case=False)
            ]
        results["companyName"] = results["companyName"].fillna("-").replace("-", "")
        for col in results:
            if results[col].dtype in ("int", "float"):
                results[col] = results[col].fillna(0).replace(0, None)
        return [
            FMPEquityScreenerData.model_validate(d)
            for d in results.sort_values(by="marketCap", ascending=False).to_dict(
                "records"
            )
        ]
