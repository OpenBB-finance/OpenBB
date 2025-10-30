"""FMP Institutional Ownership Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.institutional_ownership import (
    InstitutionalOwnershipData,
    InstitutionalOwnershipQueryParams,
)
from openbb_fmp.utils.helpers import get_data_urls
from pydantic import Field, field_validator


class FMPInstitutionalOwnershipQueryParams(InstitutionalOwnershipQueryParams):
    """FMP Institutional Ownership Query.

    Source: https://site.financialmodelingprep.com/developer/docs#positions-summary
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

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


class FMPInstitutionalOwnershipData(InstitutionalOwnershipData):
    """FMP Institutional Ownership Data."""

    __alias_dict__ = {
        "number_of_13f_shares": "numberOf13Fshares",
        "last_number_of_13f_shares": "lastNumberOf13Fshares",
        "number_of_13f_shares_change": "numberOf13FsharesChange",
        "ownership_percent_change": "changeInOwnershipPercentage",
    }

    investors_holding: int = Field(description="Number of investors holding the stock.")
    last_investors_holding: int = Field(
        description="Number of investors holding the stock in the last quarter."
    )
    investors_holding_change: int = Field(
        description="Change in the number of investors holding the stock."
    )
    number_of_13f_shares: int | None = Field(
        default=None,
        description="Number of 13F shares.",
    )
    last_number_of_13f_shares: int | None = Field(
        default=None,
        description="Number of 13F shares in the last quarter.",
    )
    number_of_13f_shares_change: int | None = Field(
        default=None,
        description="Change in the number of 13F shares.",
    )
    total_invested: float = Field(description="Total amount invested.")
    last_total_invested: float = Field(
        description="Total amount invested in the last quarter."
    )
    total_invested_change: float = Field(
        description="Change in the total amount invested."
    )
    ownership_percent: float = Field(
        description="Ownership percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    last_ownership_percent: float = Field(
        description="Ownership percent in the last quarter.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ownership_percent_change: float = Field(
        description="Change in the ownership percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    new_positions: int = Field(description="Number of new positions.")
    last_new_positions: int = Field(
        description="Number of new positions in the last quarter."
    )
    new_positions_change: int = Field(
        description="Change in the number of new positions."
    )
    increased_positions: int = Field(description="Number of increased positions.")
    last_increased_positions: int = Field(
        description="Number of increased positions in the last quarter."
    )
    increased_positions_change: int = Field(
        description="Change in the number of increased positions."
    )
    closed_positions: int = Field(description="Number of closed positions.")
    last_closed_positions: int = Field(
        description="Number of closed positions in the last quarter."
    )
    closed_positions_change: int = Field(
        description="Change in the number of closed positions."
    )
    reduced_positions: int = Field(description="Number of reduced positions.")
    last_reduced_positions: int = Field(
        description="Number of reduced positions in the last quarter."
    )
    reduced_positions_change: int = Field(
        description="Change in the number of reduced positions."
    )
    total_calls: int = Field(
        description="Total number of call options contracts traded for Apple Inc. on the specified date."
    )
    last_total_calls: int = Field(
        description="Total number of call options contracts traded for Apple Inc. on the previous reporting date."
    )
    total_calls_change: int = Field(
        description="Change in the total number of call options contracts traded between "
        "the current and previous reporting dates."
    )
    total_puts: int = Field(
        description="Total number of put options contracts traded for Apple Inc. on the specified date."
    )
    last_total_puts: int = Field(
        description="Total number of put options contracts traded for Apple Inc. on the previous reporting date."
    )
    total_puts_change: int = Field(
        description="Change in the total number of put "
        "options contracts traded between the current and previous reporting dates."
    )
    put_call_ratio: float = Field(
        description="Put-call ratio, which is the ratio of the total number of "
        "put options to call options traded on the specified date."
    )
    last_put_call_ratio: float = Field(
        description="Put-call ratio on the previous reporting date."
    )
    put_call_ratio_change: float = Field(
        description="Change in the put-call ratio between the current and previous reporting dates."
    )

    @field_validator(
        "ownership_percent",
        "last_ownership_percent",
        "ownership_percent_change",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def _normalize_percent(cls, v):
        """Normalize percent fields to be in decimal form."""
        return v / 100 if v else None


class FMPInstitutionalOwnershipFetcher(
    Fetcher[
        FMPInstitutionalOwnershipQueryParams,
        list[FMPInstitutionalOwnershipData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPInstitutionalOwnershipQueryParams:
        """Transform the query params."""
        return FMPInstitutionalOwnershipQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPInstitutionalOwnershipQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from pandas import Timestamp, offsets

        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = query.symbol.split(",")
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

        urls: list[str] = [
            "https://financialmodelingprep.com/stable/institutional-ownership/symbol-positions-summary"
            + f"?symbol={symbol}&year={year}&quarter={quarter}&apikey={api_key}"
            for symbol in symbols
        ]

        return await get_data_urls(urls, **kwargs)  # type: ignore

    @staticmethod
    def transform_data(
        query: FMPInstitutionalOwnershipQueryParams, data: list, **kwargs: Any
    ) -> list[FMPInstitutionalOwnershipData]:
        """Return the transformed data."""
        return [FMPInstitutionalOwnershipData.model_validate(d) for d in data]
