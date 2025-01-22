"""Finviz Compare Groups Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.compare_groups import (
    CompareGroupsData,
    CompareGroupsQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_finviz.utils.definitions import GROUPS, GROUPS_DICT, METRICS
from pydantic import Field, field_validator

GROUPS_CHOICES = sorted(list(GROUPS_DICT))


class FinvizCompareGroupsQueryParams(CompareGroupsQueryParams):
    """Finviz Compare Groups Query Params."""

    __json_schema_extra__ = {
        "group": {
            "multiple_items_allowed": False,
            "choices": GROUPS_CHOICES,
        },
        "metric": {
            "multiple_items_allowed": False,
            "choices": ["performance", "valuation", "overview"],
        },
    }

    group: GROUPS = Field(
        default="sector",
        description="US-listed stocks only."
        + " When an individual sector is selected, it is broken down by industry."
        + " The default is 'sector'.",
    )
    metric: METRICS = Field(
        default="performance",
        description="Statistical metric to return. Select from: ['performance', 'valuation', 'overview']"
        + " The default is 'performance'.",
    )


class FinvizCompareGroupsData(CompareGroupsData):
    """Finviz Compare Groups Data."""

    __alias_dict__ = {
        "name": "Name",
        "stocks": "Number of Stocks",
        "market_cap": "Market Cap",
        "performance_1d": "Change",
        "performance_1w": "Perf Week",
        "performance_1m": "Perf Month",
        "performance_3m": "Perf Quart",
        "performance_6m": "Perf Half",
        "performance_1y": "Perf Year",
        "performance_ytd": "Perf YTD",
        "volume": "Volume",
        "volume_average": "Avg Volume",
        "volume_relative": "Rel Volume",
        "pe": "P/E",
        "forward_pe": "Fwd P/E",
        "peg": "PEG",
        "eps_growth_past_5y": "EPS past 5Y",
        "eps_growth_next_5y": "EPS next 5Y",
        "sales_growth_past_5_years": "Sales past 5Y",
        "price_to_sales": "P/S",
        "price_to_book": "P/B",
        "price_to_cash": "P/C",
        "price_to_free_cash_flow": "P/FCF",
        "dividend_yield": "Dividend",
        "float_short": "Float Short",
        "analyst_recommendation": "Recom",
    }

    name: str = Field(description="Name or label of the group.")

    stocks: Optional[int] = Field(
        default=None,
        description="The number of stocks in the group.",
    )
    market_cap: Optional[ForceInt] = Field(
        default=None,
        description="The market cap of the group.",
    )
    performance_1d: Optional[float] = Field(
        default=None,
        description="The performance in the last day, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    performance_1w: Optional[float] = Field(
        default=None,
        description="The performance in the last week, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    performance_1m: Optional[float] = Field(
        default=None,
        description="The performance in the last month, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    performance_3m: Optional[float] = Field(
        default=None,
        description="The performance in the last quarter, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    performance_6m: Optional[float] = Field(
        default=None,
        description="The performance in the last half year, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    performance_1y: Optional[float] = Field(
        default=None,
        description="The performance in the last year, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    performance_ytd: Optional[float] = Field(
        default=None,
        description="The performance in the year to date, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    dividend_yield: Optional[float] = Field(
        default=None,
        description="The dividend yield of the group, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
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
    )
    eps_growth_past_5y: Optional[float] = Field(
        default=None,
        description="The EPS growth of the group for the past 5 years, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    eps_growth_next_5y: Optional[float] = Field(
        default=None,
        description="The estimated EPS growth of the groupo for the next 5 years,"
        + " as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    sales_growth_past_5y: Optional[float] = Field(
        default=None,
        description="The sales growth of the group for the past 5 years, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    float_short: Optional[float] = Field(
        default=None,
        description="The percent of the float shorted for the group, as a normalized value.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
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
        "performance_1w",
        "performance_1m",
        "performance_3m",
        "performance_6m",
        "performance_1y",
        "performance_ytd",
        "dividend_yield",
        "eps_growth_past_5y",
        "eps_growth_next_5y",
        "sales_growth_past_5y",
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
        """Check for abbreviated string values."""
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
        # pylint: disable=import-outside-toplevel
        from finvizfinance import util
        from finvizfinance.group import Overview, Performance, Valuation
        from openbb_core.provider.utils.helpers import get_requests_session
        from pandas import DataFrame

        util.session = get_requests_session()
        results: List = []
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
