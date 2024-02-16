"""YFinance Price Target Model"""

# pylint: disable=unused-argument
import asyncio
import warnings
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.price_target import (
    PriceTargetData,
    PriceTargetQueryParams,
)
from pydantic import Field
from yfinance import Ticker

_warn = warnings.warn


class YFinancePriceTargetQueryParams(PriceTargetQueryParams):
    """YFinance Price Target query params."""


class YFinancePriceTargetData(PriceTargetData):
    """YFinance Price Target Data."""

    __alias_dict__ = {
        "published_date": "GradeDate",
        "analyst_company": "Firm",
    }
    new_grade: Optional[str] = Field(
        default=None,
        description="The updated grade.",
        alias="ToGrade",
    )
    old_grade: Optional[str] = Field(
        default=None,
        description="The original grade.",
        alias="FromGrade",
    )
    action: Optional[str] = Field(
        default=None,
        description="The action taken.",
        alias="Action",
    )


class YFinancePriceTargetFetcher(
    Fetcher[YFinancePriceTargetQueryParams, List[YFinancePriceTargetData]]
):
    """YFinance Price Target fetcher."""

    @staticmethod
    async def aextract_data(
        query: YFinancePriceTargetQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from YFinance"""

        symbols = query.symbol.split(",")
        results = []

        async def get_one(symbol):
            """Get the data for one ticker symbol."""
            _ticker = Ticker(symbol)
            ticker = _ticker.get_upgrades_downgrades()
            if not ticker.empty:  # type: ignore
                ticker["symbol"] = symbol
                results.extend(ticker.reset_index().to_dict(orient="records"))  # type: ignore

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        return results

    @staticmethod
    def transform_data(
        query: YFinancePriceTargetQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinancePriceTargetData]:
        """Transform the data."""
        return [YFinancePriceTargetData.model_validate(d) for d in data]
