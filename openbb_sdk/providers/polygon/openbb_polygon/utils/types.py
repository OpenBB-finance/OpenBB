"""Polygon types helpers."""


from datetime import date, datetime, timedelta
from enum import Enum
from typing import Literal, Optional, Union

# IMPORT INTERNAL
from openbb_provider.abstract.data import Data, QueryParams

# IMPORT THIRD-PARTY
from pydantic import Field, PositiveFloat, PositiveInt, validator


class Timespan(str, Enum):
    minute = "minute"
    hour = "hour"
    day = "day"
    week = "week"
    month = "month"
    quarter = "quarter"
    year = "year"


class PolygonFundamentalQueryParams(QueryParams):
    """Polygon Fundamental QueryParams.

    Source: https://polygon.io/docs/stocks#!/get_vx_reference_financials

    Parameter
    ---------
    symbol : Optional[str]
        The symbol of the company if no CIK is provided.
    cik : Optional[str]
        The CIK of the company if no symbol is provided.
    company_name : Optional[str]
        The name of the company.
    company_name_search : Optional[str]
        The name of the company to search.
    sic : Optional[str]
        The Standard Industrial Classification (SIC) of the company.
    filing_date : Optional[date]
        The filing date of the financial statement.
    filing_date_lt : Optional[date]
        The filing date less than the given date.
    filing_date_lte : Optional[date]
        The filing date less than or equal to the given date.
    filing_date_gt : Optional[date]
        The filing date greater than the given date.
    filing_date_gte : Optional[date]
        The filing date greater than or equal to the given date.
    period_of_report_date : Optional[date]
        The period of report date of the financial statement.
    period_of_report_date_lt : Optional[date]
        The period of report date less than the given date.
    period_of_report_date_lte : Optional[date]
        The period of report date less than or equal to the given date.
    period_of_report_date_gt : Optional[date]
        The period of report date greater than the given date.
    period_of_report_date_gte : Optional[date]
        The period of report date greater than or equal to the given date.
    timeframe : Optional[Literal["annual", "quarterly", "ttm"]]
        The timeframe of the financial statement.
    include_sources : Optional[bool]
        Whether to include the sources of the financial statement.
    order : Optional[Literal["asc", "desc"]]
        The order of the financial statement.
    limit : Optional[PositiveInt]
        The limit of the financial statement.
    sort : Optional[Literal["filing_date", "period_of_report_date"]]
        The sort of the financial statement.
    """

    ticker: Optional[str] = Field(alias="symbol")
    cik: Optional[str]
    company_name: Optional[str]
    company_name_search: Optional[str] = Field(alias="company_name.search")
    sic: Optional[str]
    filing_date: Optional[date]
    filing_date_lt: Optional[date] = Field(alias="filing_date.lt")
    filing_date_lte: Optional[date] = Field(alias="filing_date.lte")
    filing_date_gt: Optional[date] = Field(alias="filing_date.gt")
    filing_date_gte: Optional[date] = Field(alias="filing_date.gte")
    period_of_report_date: Optional[date]
    period_of_report_date_lt: Optional[date] = Field(alias="period_of_report_date.lt")
    period_of_report_date_lte: Optional[date] = Field(alias="period_of_report_date.lte")
    period_of_report_date_gt: Optional[date] = Field(alias="period_of_report_date.gt")
    period_of_report_date_gte: Optional[date] = Field(alias="period_of_report_date.gte")
    timeframe: Optional[Literal["annual", "quarterly", "ttm"]] = Field(alias="period")
    include_sources: Optional[bool]
    order: Optional[Literal["asc", "desc"]]
    limit: Optional[PositiveInt] = 100
    sort: Optional[Literal["filing_date", "period_of_report_date"]]


class BaseStockQueryParams(QueryParams):
    stocksTicker: str = Field(alias="symbol")
    start_date: Union[date, datetime] = Field(
        default=datetime.now().date() - timedelta(days=8)
    )
    end_date: Union[date, datetime] = Field(
        default=datetime.now().date() - timedelta(days=1)
    )
    timespan: Timespan = Field(default=Timespan.day)
    sort: Literal["asc", "desc"] = Field(default="desc")
    limit: PositiveInt = Field(default=49999)
    adjusted: bool = Field(default=True)
    multiplier: PositiveInt = Field(default=1)


class BaseStockData(Data):
    c: PositiveFloat = Field(alias="close")
    o: PositiveFloat = Field(alias="open")
    h: PositiveFloat = Field(alias="high")
    l: PositiveFloat = Field(alias="low")  # noqa: E741
    t: datetime = Field(alias="date")

    @validator("t", pre=True)
    def time_validate(cls, v):  # pylint: disable=E0213
        return datetime.fromtimestamp(v / 1000)
