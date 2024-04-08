"""Yahoo Finance Asset Undervalued Growth Tech Equities Model."""

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


class YFUndervaluedGrowthEquitiesQueryParams(EquityPerformanceQueryParams):
    """Yahoo Finance Asset Undervalued Growth Tech Equities Query.

    Source: https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks
    """


class YFUndervaluedGrowthEquitiesData(EquityPerformanceData):
    """Yahoo Finance Asset Undervalued Growth Tech Equities Data."""

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


class YFUndervaluedGrowthEquitiesFetcher(
    Fetcher[
        YFUndervaluedGrowthEquitiesQueryParams, List[YFUndervaluedGrowthEquitiesData]
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> YFUndervaluedGrowthEquitiesQueryParams:
        """Transform query params."""
        return YFUndervaluedGrowthEquitiesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFUndervaluedGrowthEquitiesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Get data from YF."""
        headers = {"user_agent": "Mozilla/5.0"}
        html = make_request(
            "https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks",
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
    ) -> List[YFUndervaluedGrowthEquitiesData]:
        """Transform data."""

        columns = ["Market Cap", "Avg Vol (3 month)", "Volume", "% Change"]

        data = df_transform_numbers(data, columns)
        data = data.fillna("N/A").replace("N/A", None)

        return [
            YFUndervaluedGrowthEquitiesData.model_validate(d)
            for d in data.sort_values(by="Market Cap", ascending=False).to_dict(
                "records"
            )
        ]
