"""FMP Equity Profile Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
)
from typing import Any

from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_info import (
    EquityInfoData,
    EquityInfoQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator, model_validator


class FMPEquityProfileQueryParams(EquityInfoQueryParams):
    """FMP Equity Profile Query.

    Source: https://site.financialmodelingprep.com/developer/docs#profile-symbol
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


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
        "last_price": "price",
        "volume_avg": "averageVolume",
        "annualized_dividend_amount": "lastDividend",
    }
    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}
    model_config = ConfigDict(extra="ignore")

    is_etf: bool = Field(description="If the symbol is an ETF.")
    is_actively_trading: bool = Field(description="If the company is actively trading.")
    is_adr: bool = Field(description="If the stock is an ADR.")
    is_fund: bool = Field(description="If the company is a fund.")
    image: str | None = Field(default=None, description="Image of the company.")
    currency: str | None = Field(
        default=None, description="Currency in which the stock is traded."
    )
    market_cap: ForceInt | None = Field(
        default=None,
        description="Market capitalization of the company.",
    )
    last_price: float | None = Field(
        default=None,
        description="The last traded price.",
    )
    year_high: float | None = Field(
        default=None, description="The one-year high of the price."
    )
    year_low: float | None = Field(
        default=None, description="The one-year low of the price."
    )
    volume_avg: ForceInt | None = Field(
        default=None,
        description="Average daily trading volume.",
    )
    annualized_dividend_amount: float | None = Field(
        default=None,
        description="The annualized dividend payment based on the most recent regular dividend payment.",
    )
    beta: float | None = Field(
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
        list[FMPEquityProfileData],
    ]
):
    """FMP Equity Profile Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPEquityProfileQueryParams:
        """Transform the query params."""
        return FMPEquityProfileQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEquityProfileQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import warnings
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_fmp.utils.helpers import response_callback

        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = query.symbol.split(",")
        base_url = "https://financialmodelingprep.com/stable/"

        results: list = []

        async def get_one(symbol):
            """Get data for one symbol."""
            url = f"{base_url}profile?symbol={symbol}&apikey={api_key}"
            result = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if not result:
                warnings.warn(f"Symbol Error: No data found for {symbol}")

            if result:
                results.append(result[0])

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No data found for the given symbols.")

        return sorted(
            results,
            key=(lambda item: (symbols.index(item.get("symbol", len(symbols))))),
        )

    @staticmethod
    def transform_data(
        query: FMPEquityProfileQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FMPEquityProfileData]:
        """Return the transformed data."""
        results: list[FMPEquityProfileData] = []

        for d in data:
            d["year_low"], d["year_high"] = (
                d.pop("range", "-").split("-") if d.get("range") else (None, None)
            )
            results.append(FMPEquityProfileData.model_validate(d))

        return results
