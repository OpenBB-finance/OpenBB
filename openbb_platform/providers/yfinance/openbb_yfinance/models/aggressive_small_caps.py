"""Yahoo Finance Aggressive Small Caps Model."""

# pylint: disable=unused-argument

import re
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_performance import (
    EquityPerformanceData,
    EquityPerformanceQueryParams,
)
from openbb_core.provider.utils.helpers import make_request
from openbb_yfinance.utils.helpers import df_transform_numbers
from pydantic import Field


class YFAggressiveSmallCapsQueryParams(EquityPerformanceQueryParams):
    """Yahoo Finance Aggressive Small Caps Query.

    Source: https://finance.yahoo.com/screener/predefined/aggressive_small_caps
    """


class YFAggressiveSmallCapsData(EquityPerformanceData):
    """Yahoo Finance Aggressive Small Caps Data."""

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
        default=None,
        description="Market Cap.",
    )
    avg_volume_3_months: Optional[float] = Field(
        default=None,
        description="Average volume over the last 3 months in millions.",
    )
    pe_ratio_ttm: Optional[float] = Field(
        description="PE Ratio (TTM).",
        default=None,
    )


class YFAggressiveSmallCapsFetcher(
    Fetcher[YFAggressiveSmallCapsQueryParams, List[YFAggressiveSmallCapsData]]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFAggressiveSmallCapsQueryParams:
        """Transform query params."""
        return YFAggressiveSmallCapsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFAggressiveSmallCapsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Get data from YF."""
        headers = {"user_agent": "Mozilla/5.0"}
        html = make_request(
            "https://finance.yahoo.com/screener/predefined/aggressive_small_caps",
            headers=headers,
        ).text
        html_clean = re.sub(r"(<span class=\"Fz\(0\)\">).*?(</span>)", "", html)
        df = pd.read_html(html_clean, header=None)[0].dropna(how="all", axis=1)
        return df

    @staticmethod
    def transform_data(
        query: EquityPerformanceQueryParams,
        data: pd.DataFrame,
        **kwargs: Any,
    ) -> List[YFAggressiveSmallCapsData]:
        """Transform data."""

        columns = ["Market Cap", "Avg Vol (3 month)", "Volume", "% Change"]

        data = df_transform_numbers(data=data, columns=columns)
        data = data.fillna("N/A").replace("N/A", None)
        return [
            YFAggressiveSmallCapsData.model_validate(d) for d in data.to_dict("records")
        ]
