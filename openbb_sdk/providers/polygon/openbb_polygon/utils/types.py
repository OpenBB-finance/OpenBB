"""Polygon types helpers."""


from datetime import date
from typing import Literal, Optional

from openbb_provider.standard_models.income_statement import IncomeStatementQueryParams
from pydantic import Field


class PolygonFundamentalQueryParams(IncomeStatementQueryParams):
    """Polygon Fundamental QueryParams.

    Source: https://polygon.io/docs/stocks#!/get_vx_reference_financials
    """

    __alias_dict__ = {
        "symbol": "ticker",
        "period": "timeframe",
    }

    company_name: Optional[str] = Field(
        default=None, description="Name of the company."
    )
    company_name_search: Optional[str] = Field(
        default=None, description="Name of the company to search."
    )
    sic: Optional[str] = Field(
        default=None,
        description="The Standard Industrial Classification (SIC) of the company.",
    )
    filing_date: Optional[date] = Field(
        default=None, description="Filing date of the financial statement."
    )
    filing_date_lt: Optional[date] = Field(
        default=None, description="Filing date less than the given date."
    )
    filing_date_lte: Optional[date] = Field(
        default=None,
        description="Filing date less than or equal to the given date.",
    )
    filing_date_gt: Optional[date] = Field(
        default=None,
        description="Filing date greater than the given date.",
    )
    filing_date_gte: Optional[date] = Field(
        default=None,
        description="Filing date greater than or equal to the given date.",
    )
    period_of_report_date: Optional[date] = Field(
        default=None, description="Period of report date of the financial statement."
    )
    period_of_report_date_lt: Optional[date] = Field(
        default=None,
        description="Period of report date less than the given date.",
    )
    period_of_report_date_lte: Optional[date] = Field(
        default=None,
        description="Period of report date less than or equal to the given date.",
    )
    period_of_report_date_gt: Optional[date] = Field(
        default=None,
        description="Period of report date greater than the given date.",
    )
    period_of_report_date_gte: Optional[date] = Field(
        default=None,
        description="Period of report date greater than or equal to the given date.",
    )
    include_sources: Optional[bool] = Field(
        default=None,
        description="Whether to include the sources of the financial statement.",
    )
    order: Optional[Literal["asc", "desc"]] = Field(
        default=None, description="Order of the financial statement."
    )
    sort: Optional[Literal["filing_date", "period_of_report_date"]] = Field(
        default=None, description="Sort of the financial statement."
    )
