"""Yahoo Finance Asset Performance Growth Tech Equities Model."""

# pylint: disable=unused-argument

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


class YFGrowthTechEquitiesQueryParams(EquityPerformanceQueryParams):
    """Yahoo Finance Asset Performance Growth Tech Equities Query.

    Source: https://finance.yahoo.com/screener/predefined/growth_technology_stocks
    """


class YFGrowthTechEquitiesData(EquityPerformanceData):
    """Yahoo Finance Asset Performance Growth Tech Equities Data."""

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


class YFGrowthTechEquitiesFetcher(
    Fetcher[YFGrowthTechEquitiesQueryParams, List[YFGrowthTechEquitiesData]]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFGrowthTechEquitiesQueryParams:
        """Transform query params."""
        return YFGrowthTechEquitiesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFGrowthTechEquitiesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Get data from YF."""
        headers = {"user_agent": "Mozilla/5.0"}
        html = requests.get(
            "https://finance.yahoo.com/screener/predefined/growth_technology_stocks",
            headers=headers,
            timeout=10,
        ).text
        html_clean = re.sub(r"(<span class=\"Fz\(0\)\">).*?(</span>)", "", html)
        df = pd.read_html(html_clean, header=None)[0].dropna(how="all", axis=1)
        return df

    @staticmethod
    def transform_data(
        query: EquityPerformanceQueryParams,
        data: pd.DataFrame,
        **kwargs: Any,
    ) -> List[YFGrowthTechEquitiesData]:
        """Transform data."""

        def df_apply(data):
            """Replace abbreviations"""
            multipliers = {"M": 1e6, "B": 1e9, "T": 1e12}

            def replace_suffix(x, suffix, multiplier):
                return (
                    float(str(x).replace(suffix, "")) * multiplier
                    if suffix in str(x)
                    else x
                )

            for col in ["Market Cap", "Avg Vol (3 month)", "Volume", "% Change"]:
                if col == "% Change":
                    data[col] = data[col].astype(str).str.replace("%", "").astype(float)
                else:
                    for suffix, multiplier in multipliers.items():
                        data[col] = data[col].apply(
                            replace_suffix, args=(suffix, multiplier)
                        )
            return data

        data = df_apply(data)
        data = data.fillna("N/A").replace("N/A", None)
        return [
            YFGrowthTechEquitiesData.model_validate(d) for d in data.to_dict("records")
        ]
