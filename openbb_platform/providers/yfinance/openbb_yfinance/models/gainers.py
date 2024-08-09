"""Yahoo Finance Asset Performance Gainers Model."""

# pylint: disable=unused-argument

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_performance import (
    EquityPerformanceData,
    EquityPerformanceQueryParams,
)
from pydantic import Field

if TYPE_CHECKING:
    from pandas import DataFrame


class YFGainersQueryParams(EquityPerformanceQueryParams):
    """Yahoo Finance Asset Performance Gainers Query.

    Source: https://finance.yahoo.com/screener/predefined/day_gainers
    """


class YFGainersData(EquityPerformanceData):
    """Yahoo Finance Asset Performance Gainers Data."""

    __alias_dict__ = {
        "symbol": "Symbol",
        "name": "Name",
        "volume": "Volume",
        "change": "Change",
        "price": "Price (Intraday)",
        "percent_change": "% Change",
        "market_cap": "Market Cap",
        "avg_volume_3_months": "Avg Vol (3 month)",
        "pe_ratio_ttm": "PE Ratio (TTM)",
    }

    avg_volume_3_months: Optional[float] = Field(
        default=None,
        description="Average volume over the last 3 months in millions.",
    )
    market_cap: Optional[float] = Field(
        default=None,
        description="Market Cap.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    pe_ratio_ttm: Optional[float] = Field(
        default=None,
        description="PE Ratio (TTM).",
    )


class YFGainersFetcher(Fetcher[YFGainersQueryParams, List[YFGainersData]]):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFGainersQueryParams:
        """Transform query params."""
        return YFGainersQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFGainersQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> "DataFrame":
        """Get data from YF."""
        # pylint: disable=import-outside-toplevel
        import io  # noqa
        import re  # noqa
        from openbb_core.provider.utils.helpers import make_request  # noqa
        from pandas import read_html  # noqa

        headers = {"user_agent": "Mozilla/5.0"}
        html = make_request(
            "https://finance.yahoo.com/screener/predefined/day_gainers",
            headers=headers,
        ).text
        html_clean = re.sub(r"(<span class=\"Fz\(0\)\">).*?(</span>)", "", html)
        df = read_html(io.StringIO(html_clean), header=None)[0].dropna(
            how="all", axis=1
        )

        return df

    @staticmethod
    def transform_data(
        query: EquityPerformanceQueryParams,
        data: "DataFrame",
        **kwargs: Any,
    ) -> List[YFGainersData]:
        """Transform data."""
        # pylint: disable=import-outside-toplevel
        from openbb_yfinance.utils.helpers import df_transform_numbers

        columns = ["Market Cap", "Avg Vol (3 month)", "Volume", "% Change"]

        data = df_transform_numbers(data=data, columns=columns)
        data = data.fillna("N/A").replace("N/A", None)
        data["Name"] = data["Name"].fillna(data["Symbol"])

        return [
            YFGainersData.model_validate(d)
            for d in data.sort_values("% Change", ascending=False).to_dict(
                orient="records"
            )
        ]
