"""Yahoo Finance Aggressive Small Caps Model."""

import re
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_performance import (
    EquityPerformanceData,
    EquityPerformanceQueryParams,
)
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

    market_cap: str = Field(
        description="Market Cap.",
    )
    avg_volume_3_months: float = Field(
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
        html = requests.get(
            "https://finance.yahoo.com/screener/predefined/aggressive_small_caps",
            headers=headers,
            timeout=10,
        ).text
        html_clean = re.sub(r"(<span class=\"Fz\(0\)\">).*?(</span>)", "", html)
        df = (
            pd.read_html(html_clean, header=None)[0]
            .dropna(how="all", axis=1)
            .fillna("-")
            .replace("-", None)
        )
        return df

    @staticmethod
    def transform_data(
        query: EquityPerformanceQueryParams,
        data: pd.DataFrame,
        **kwargs: Any,
    ) -> List[YFAggressiveSmallCapsData]:
        """Transform data."""
        data["% Change"] = data["% Change"].str.replace("%", "")
        data["Volume"] = data["Volume"].str.replace("M", "").astype(float) * 1000000
        data["Avg Vol (3 month)"] = (
            data["Avg Vol (3 month)"].str.replace("M", "").astype(float) * 1000000
        )
        data = data.to_dict(orient="records")
        data = sorted(data, key=lambda d: d["% Change"], reverse=query.sort == "desc")
        return [YFAggressiveSmallCapsData.model_validate(d) for d in data]
