"""FMP Equity Ownership Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_ownership import (
    EquityOwnershipData,
    EquityOwnershipQueryParams,
)
from pydantic import Field, field_validator


class FMPEquityOwnershipQueryParams(EquityOwnershipQueryParams):
    """FMP Equity Ownership Query.

    Source: https://site.financialmodelingprep.com/developer/docs#filings-extract-with-analytics-by-holder
    """

    year: int | None = Field(
        default=None,
        description="Calendar year for the data. If not provided, the latest year is used.",
    )
    quarter: int | None = Field(
        default=None,
        description="Calendar quarter for the data. Valid values are 1, 2, 3, or 4."
        + " If not provided, the quarter previous to the current quarter is used.",
        ge=1,
        le=4,
    )
    page: int | None = Field(
        default=None,
        description="Page number, used in conjunction with the limit. The default is 0.",
    )
    limit: int | None = Field(
        default=None,
        description="Number of items to return per page. The default is 100, which is the maximum.",
    )


class FMPEquityOwnershipData(EquityOwnershipData):
    """FMP Equity Ownership Data."""

    __alias_dict__ = {
        "security_type": "typeOfSecurity",
        "sic_industry": "industryTitle",
        "weight_previous": "lastWeight",
        "weight_change": "changeInWeight",
        "weight_change_percent": "changeInWeightPercentage",
        "market_value_previous": "lastMarketValue",
        "market_value_change": "changeInMarketValue",
        "market_value_change_percent": "changeInMarketValuePercentage",
        "shares_previous": "lastSharesNumber",
        "shares_change": "changeInSharesNumber",
        "shares_change_percent": "changeInSharesNumberPercentage",
        "ownership_previous": "lastOwnership",
        "ownership_change": "changeInOwnership",
        "ownership_change_percent": "changeInOwnershipPercentage",
        "performance_percent": "performancePercentage",
        "performance_previous": "lastPerformance",
        "performance_change": "changeInPerformance",
    }

    security_name: str = Field(
        description="Security name.",
    )
    security_type: str = Field(
        description="Type or class of security.",
    )
    security_cusip: str = Field(
        description="CUSIP of the security.",
    )
    shares_type: str = Field(description="Shares type.")
    put_call_share: str = Field(
        description="Whether the share represents a put, call, or share.",
    )
    investment_discretion: str = Field(
        description="Investment discretion of reporting entity.",
    )
    sic_industry: str = Field(
        description="SIC classification industry.",
    )
    weight: float = Field(
        description="Weight relative to the total reported portfolio.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    weight_previous: float = Field(
        description="Weight from the previous quarter.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    weight_change: float = Field(
        description="Change in the weight from the previous quarter.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    weight_change_percent: float = Field(
        description="Change in weight as a percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    market_value: int = Field(description="Market value of the stock ownership.")
    market_value_previous: int = Field(
        description="Market value from the previous quarter.",
    )
    market_value_change: int = Field(
        description="Change in market value from the previous quarter.",
    )
    market_value_change_percent: float = Field(
        description="Change in market value from the previous quarter, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    shares_number: int = Field(
        description="Number of controlled shares.",
    )
    shares_previous: int = Field(
        description="Number of controlled shares from the previous quarter.",
    )
    shares_change: float = Field(
        description="Change in shares number from the previous quarter.",
    )
    shares_change_percent: float = Field(
        description="Change in shares number from the previous quarter, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    quarter_end_price: float = Field(
        description="Market price of the security at the end of the quarter.",
    )
    avg_price_paid: float = Field(
        description="Average price paid for the shares.",
    )
    is_new: bool = Field(description="If the security was newly added this quarter.")
    is_sold_out: bool = Field(description="If the security was sold out this quarter.")
    ownership: float | None = Field(
        default=None,
        description="Ownership stake in the security, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ownership_previous: float | None = Field(
        default=None,
        description="Ownership stake in the security from the previous quarter, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ownership_change: float | None = Field(
        default=None,
        description="Change in ownership stake from the previous quarter.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ownership_change_percent: float | None = Field(
        default=None,
        description="Change in ownership stake from the previous quarter, as a percent.",
    )
    holding_period: int = Field(
        description="Holding period of the security.",
    )
    first_added: dateType = Field(
        description="When the security was first reported as held.",
    )
    performance: float | None = Field(
        default=None, description="Performance value of the security holding."
    )
    performance_percent: float | None = Field(
        default=None,
        description="Performance of the security holding, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    performance_previous: float | None = Field(
        default=None,
        description="Performance value of the security holding from the previous quarter.",
    )
    performance_change: float | None = Field(
        default=None,
        description="Change in value of the security holding's performance.",
    )
    is_counted_for_performance: bool = Field(
        description="If the security is counted for the performance measurement.",
    )

    @field_validator(
        "weight",
        "weight_previous",
        "weight_change",
        "weight_change_percent",
        "market_value_change_percent",
        "shares_change_percent",
        "ownership",
        "ownership_previous",
        "ownership_change",
        "ownership_change_percent",
        "performance_percent",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def _normalize_percent(cls, v):
        """Normalize percent values."""
        return v / 100 if v else None


class FMPEquityOwnershipFetcher(
    Fetcher[
        FMPEquityOwnershipQueryParams,
        list[FMPEquityOwnershipData],
    ]
):
    """FMP Equity Ownership Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPEquityOwnershipQueryParams:
        """Transform the query params."""
        return FMPEquityOwnershipQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEquityOwnershipQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many
        from pandas import Timestamp, offsets

        api_key = credentials.get("fmp_api_key") if credentials else ""

        year = query.year if query.year else None
        quarter = query.quarter if query.quarter else None

        if year is None and quarter is None:
            current = (Timestamp("now") + offsets.QuarterEnd()) - offsets.QuarterEnd()
            quarter = current.quarter
            year = current.year
        elif year is None and quarter is not None:
            year = Timestamp("now").year
        elif year is not None and quarter is None:
            current = Timestamp("now")
            quarter = (
                4
                if year < current.year
                else current.quarter - 1 if current.quarter > 1 else 1
            )

        url = (
            "https://financialmodelingprep.com/stable/institutional-ownership/extract-analytics/holder"
            + f"?symbol={query.symbol}&year={year}&quarter={quarter}&page={query.page or 0}"
            + f"&limit={query.limit or 100}&apikey={api_key}"
        )

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEquityOwnershipQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPEquityOwnershipData]:
        """Return the transformed data."""
        return [FMPEquityOwnershipData.model_validate(d) for d in data]
