"""Yahoo Finance Balance Sheet Model."""

import json
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import to_snake_case
from pydantic import Field, field_validator
from yfinance import Ticker


class YFinanceBalanceSheetQueryParams(BalanceSheetQueryParams):
    """Yahoo Finance Balance Sheet Query.

    Source: https://finance.yahoo.com/
    """

    period: Optional[Literal["annual", "quarter"]] = Field(default="annual")


class YFinanceBalanceSheetData(BalanceSheetData):
    """Yahoo Finance Balance Sheet Data."""

    __alias_dict__ = {
        "short_term_investments": "other_short_term_investments",
        "net_receivables": "receivables",
        "inventories": "inventory",
        "total_current_assets": "current_assets",
        "plant_property_equipment_gross": "gross_ppe",
        "plant_property_equipment_net": "net_ppe",
        "total_common_equity": "stockholders_equity",
        "total_equity_non_controlling_interests": "total_equity_gross_minority_interest",
    }

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return datetime object from string."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
        return v


class YFinanceBalanceSheetFetcher(
    Fetcher[
        YFinanceBalanceSheetQueryParams,
        List[YFinanceBalanceSheetData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceBalanceSheetQueryParams:
        """Transform the query parameters."""
        return YFinanceBalanceSheetQueryParams(**params)

    @staticmethod
    def extract_data(
        # pylint: disable=unused-argument
        query: YFinanceBalanceSheetQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data from the Yahoo Finance endpoints."""
        period = "yearly" if query.period == "annual" else "quarterly"  # type: ignore
        data = Ticker(query.symbol).get_balance_sheet(
            as_dict=False, pretty=False, freq=period
        )
        if data is None:
            raise EmptyDataError()
        data.index = [to_snake_case(i) for i in data.index]
        data = data.reset_index().sort_index(ascending=False).set_index("index")
        data = data.fillna("N/A").replace("N/A", None).to_dict()
        data = [{"period_ending": str(key), **value} for key, value in data.items()]

        data = json.loads(json.dumps(data))

        return data

    @staticmethod
    def transform_data(
        query: YFinanceBalanceSheetQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceBalanceSheetData]:
        """Transform the data."""
        return [YFinanceBalanceSheetData.model_validate(d) for d in data]
