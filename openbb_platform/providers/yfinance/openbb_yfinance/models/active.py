"""Yahoo Finance Asset Performance Active Model."""

# pylint: disable=unused-argument

import re
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_performance import (
    EquityPerformanceData,
    EquityPerformanceQueryParams,
)
from openbb_core.provider.utils.helpers import make_request
from openbb_yfinance.utils.helpers import df_transform_numbers
from pandas import DataFrame, read_html
from pydantic import Field


class YFActiveQueryParams(EquityPerformanceQueryParams):
    """Yahoo Finance Asset Performance Active Query.

    Source: https://finance.yahoo.com/screener/predefined/most_actives
    """


class YFActiveData(EquityPerformanceData):
    """Yahoo Finance Asset Performance Active Data."""

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

    market_cap: Optional[float] = Field(
        description="Market Cap displayed in billions.",
    )
    avg_volume_3_months: Optional[float] = Field(
        description="Average volume over the last 3 months in millions.",
    )
    pe_ratio_ttm: Optional[float] = Field(
        description="PE Ratio (TTM).",
        default=None,
    )


class YFActiveFetcher(Fetcher[YFActiveQueryParams, List[YFActiveData]]):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFActiveQueryParams:
        """Transform query params."""
        return YFActiveQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFActiveQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> DataFrame:
        """Get data from YF."""
        headers = {"user_agent": "Mozilla/5.0"}
        html = make_request(
            "https://finance.yahoo.com/screener/predefined/most_actives",
            headers=headers,
        ).text
        html_clean = re.sub(r"(<span class=\"Fz\(0\)\">).*?(</span>)", "", html)
        df = read_html(html_clean, header=None)[0].dropna(how="all", axis=1)
        return df

    @staticmethod
    def transform_data(
        query: EquityPerformanceQueryParams,
        data: DataFrame,
        **kwargs: Any,
    ) -> List[YFActiveData]:
        """Transform data."""

        columns = ["Market Cap", "Avg Vol (3 month)", "Volume", "% Change"]

        data = df_transform_numbers(data, columns)
        data = data.fillna("N/A").replace("N/A", None)

        return [
            YFActiveData.model_validate(d)
            for d in data.sort_values(by="Volume", ascending=False).to_dict("records")
        ]
