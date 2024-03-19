"""FMP Equity Profile Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
)
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_info import (
    EquityInfoData,
    EquityInfoQueryParams,
)
from openbb_core.provider.utils.helpers import amake_requests
from pydantic import Field, field_validator, model_validator


class FMPEquityProfileQueryParams(EquityInfoQueryParams):
    """FMP Equity Profile Query.

    Source: https://site.financialmodelingprep.com/developer/docs/companies-key-stats-free-api/
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class FMPEquityProfileData(EquityInfoData):
    """FMP Equity Profile Data."""

    __alias_dict__ = {
        "name": "companyName",
        "stock_exchange": "exchange",
        "company_url": "website",
        "hq_address1": "address",
        "hq_address_city": "city",
        "hq_address_postal_code": "zip",
        "hq_state": "state",
        "hq_country": "country",
        "business_phone_no": "phone",
        "industry_category": "industry",
        "employees": "fullTimeEmployees",
        "long_description": "description",
        "first_stock_price_date": "ipoDate",
    }
    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    is_etf: bool = Field(description="If the symbol is an ETF.")
    is_actively_trading: bool = Field(description="If the company is actively trading.")
    is_adr: bool = Field(description="If the stock is an ADR.")
    is_fund: bool = Field(description="If the company is a fund.")
    image: Optional[str] = Field(default=None, description="Image of the company.")
    currency: Optional[str] = Field(
        default=None, description="Currency in which the stock is traded."
    )
    market_cap: Optional[ForceInt] = Field(
        default=None,
        description="Market capitalization of the company.",
        alias="mktCap",
    )
    last_price: Optional[float] = Field(
        default=None,
        description="The last traded price.",
        alias="price",
    )
    year_high: Optional[float] = Field(
        default=None, description="The one-year high of the price."
    )
    year_low: Optional[float] = Field(
        default=None, description="The one-year low of the price."
    )
    volume_avg: Optional[ForceInt] = Field(
        default=None,
        description="Average daily trading volume.",
        alias="volAvg",
    )
    annualized_dividend_amount: Optional[float] = Field(
        default=None,
        description="The annualized dividend payment based on the most recent regular dividend payment.",
        alias="lastDiv",
    )
    beta: Optional[float] = Field(
        default=None, description="Beta of the stock relative to the market."
    )

    @field_validator("first_stock_price_date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        if isinstance(v, dateType) or v is None:
            return v
        return dateType.fromisoformat(v) if v else None

    @model_validator(mode="before")
    @classmethod
    def replace_empty_strings(cls, values):
        """Check for empty strings and replace with None."""
        return (
            {k: None if v in ("", "NA") else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class FMPEquityProfileFetcher(
    Fetcher[
        FMPEquityProfileQueryParams,
        List[FMPEquityProfileData],
    ]
):
    """FMP Equity Profile Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEquityProfileQueryParams:
        """Transform the query params."""
        return FMPEquityProfileQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEquityProfileQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = query.symbol.split(",")
        base_url = "https://financialmodelingprep.com/api/v3"
        urls = [f"{base_url}/profile/{symbol}?apikey={api_key}" for symbol in symbols]

        return await amake_requests(urls, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEquityProfileQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FMPEquityProfileData]:
        """Return the transformed data."""
        results: List[FMPEquityProfileData] = []
        for d in data:
            d["year_low"], d["year_high"] = d.get("range", "-").split("-")

            # Clear out fields that don't belong and can be had elsewhere.
            entries_to_remove = (
                "exchangeShortName",
                "defaultImage",
                "dcf",
                "dcfDiff",
                "changes",
                "range",
            )
            for key in entries_to_remove:
                d.pop(key, None)

            results.append(FMPEquityProfileData.model_validate(d))
        return results
