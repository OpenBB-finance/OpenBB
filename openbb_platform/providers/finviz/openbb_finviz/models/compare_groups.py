"""Finviz Compare Groups Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional, Union

from finvizfinance.group.overview import Overview
from finvizfinance.group.performance import Performance
from finvizfinance.group.valuation import Valuation
from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.compare_groups import (
    CompareGroupsData,
    CompareGroupsQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_finviz.utils.definitions import GROUPS, GROUPS_DICT, METRICS
from pandas import DataFrame
from pydantic import Field, field_validator


class FinvizCompareGroupsQueryParams(CompareGroupsQueryParams):
    """Finviz Compare Groups Query Params."""

    group: Union[GROUPS, None] = Field(
        default="sector",
        description="US-listed stocks only."
        + " When a sector is selected, it is broken down by industry."
        + " The default is sector.",
    )
    metric: Union[METRICS, None] = Field(
        default="performance",
        description="Select from: performance, valuation, overview."
        + " The default is performance.",
    )


class FinvizCompareGroupsData(CompareGroupsData):
    """Finviz Compare Groups Data."""

    __alias_dict__ = {
        "name": "Name",
        "stocks": "Number of Stocks",
        "market_cap": "Market Cap",
        "performance_1D": "Change",
        "performance_1W": "Perf Week",
        "performance_1M": "Perf Month",
        "performance_3M": "Perf Quart",
        "performance_6M": "Perf Half",
        "performance_1Y": "Perf Year",
        "performance_YTD": "Perf YTD",
        "volume": "Volume",
        "volume_average": "Avg Volume",
        "volume_relative": "Rel Volume",
        "pe": "P/E",
        "forward_pe": "Fwd P/E",
        "pe_growth": "PEG",
        "eps_growth_past_5_years": "EPS past 5Y",
        "eps_growth_next_5_years": "EPS next 5Y",
        "sales_growth_past_5_years": "Sales past 5Y",
        "price_to_sales": "P/S",
        "price_to_book": "P/B",
        "price_to_cash": "P/C",
        "price_to_free_cash_flow": "P/FCF",
        "dividend_yield": "Dividend",
        "float_short": "Float Short",
        "analyst_recommendation": "Recom",
    }

    stocks: Optional[int] = Field(
        default=None,
        description="The number of stocks in the group.",
        alias="Stocks",
    )
    market_cap: Optional[ForceInt] = Field(
        default=None,
        description="The market cap of the group.",
    )
    performance_1D: Optional[float] = Field(
        default=None,
        description="The performance in the last day, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    performance_1W: Optional[float] = Field(
        default=None,
        description="The performance in the last week, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    performance_1M: Optional[float] = Field(
        default=None,
        description="The performance in the last month, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    performance_3M: Optional[float] = Field(
        default=None,
        description="The performance in the last quarter, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    performance_6M: Optional[float] = Field(
        default=None,
        description="The performance in the last half year, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    performance_1Y: Optional[float] = Field(
        default=None,
        description="The performance in the last year, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    performance_YTD: Optional[float] = Field(
        default=None,
        description="The performance in the year to date, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    dividend_yield: Optional[float] = Field(
        default=None,
        description="The dividend yield of the group, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    pe: Optional[float] = Field(
        default=None,
        description="The P/E ratio of the group.",
    )
    forward_pe: Optional[float] = Field(
        default=None,
        description="The forward P/E ratio of the group.",
    )
    peg: Optional[float] = Field(
        default=None,
        description="The PEG ratio of the group.",
        alias="pe_growth",
    )
    eps_growth_past_5_years: Optional[float] = Field(
        default=None,
        description="The EPS growth of the group for the past 5 years, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    eps_growth_next_5_years: Optional[float] = Field(
        default=None,
        description="The estimated EPS growth of the groupo for the next 5 years,"
        + " as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    sales_growth_past_5_years: Optional[float] = Field(
        default=None,
        description="The sales growth of the group for the past 5 years, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    float_short: Optional[float] = Field(
        default=None,
        description="The percent of the float shorted for the group, as a normalized value.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    analyst_recommendation: Optional[float] = Field(
        default=None,
        description="The analyst consensus, on a scale of 1-5 where 1 is a buy and 5 is a sell.",
    )
    volume: Optional[ForceInt] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
    )
    volume_average: Optional[ForceInt] = Field(
        default=None,
        description="The 3-month average volume of the group.",
    )
    volume_relative: Optional[float] = Field(
        default=None,
        description="The relative volume compared to the 3-month average volume.",
    )

    @field_validator(
        "performance_1W",
        "performance_1M",
        "performance_3M",
        "performance_6M",
        "performance_1Y",
        "performance_YTD",
        "dividend_yield",
        "eps_growth_past_5_years",
        "eps_growth_next_5_years",
        "sales_growth_past_5_years",
        "float_short",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_percent_values(cls, v):
        """Check fields for the presence of a % character."""
        if v is not None and "%" in str(v):
            return float(v.replace("%", "")) / 100
        return v if v else None

    @field_validator("market_cap", "volume", mode="before", check_fields=False)
    @classmethod
    def validate_abbreviated_numbers(cls, v):
        """Checks for abbreviated string values."""
        if v is not None and isinstance(v, str):
            v = (
                v.replace("M", "e+6")
                .replace("B", "e+9")
                .replace("T", "e+12")
                .replace("K", "e+3")
            )
            return int(float(v))
        return v if v else None


class FinvizCompareGroupsFetcher(
    Fetcher[FinvizCompareGroupsQueryParams, List[FinvizCompareGroupsData]]
):
    """Finviz Compare Groups Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FinvizCompareGroupsQueryParams:
        """Transform the query params."""
        if params.get("group") is None:
            params["group"] = "sector"
        if params.get("metric") is None:
            params["metric"] = "performance"
        return FinvizCompareGroupsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FinvizCompareGroupsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from Finviz."""
        results = []
        data = DataFrame()
        if query.metric == "performance":
            data = Performance().screener_view(
                group=GROUPS_DICT[query.group],  # type: ignore
                order="Performance (Week)",
            )
        if query.metric == "valuation":
            data = Valuation().screener_view(
                group=GROUPS_DICT[query.group],  # type: ignore
                order="Forward Price/Earnings",
            )
        if query.metric == "overview":
            data = Overview().screener_view(
                group=GROUPS_DICT[query.group],  # type: ignore
                order="Change",
            )
        if not data.empty:
            results = data.fillna("N/A").replace("N/A", None).to_dict(orient="records")
        return results

    @staticmethod
    def transform_data(
        query: FinvizCompareGroupsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FinvizCompareGroupsData]:
        """Transform the raw data."""
        return [FinvizCompareGroupsData.model_validate(d) for d in data]
