"""Yahoo Finance Income Statement Model."""

import json
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import to_snake_case
from pydantic import Field, field_validator
from yfinance import Ticker


class YFinanceIncomeStatementQueryParams(IncomeStatementQueryParams):
    """Yahoo Finance Income Statement Query.

    Source: https://finance.yahoo.com/
    """

    period: Optional[Literal["annual", "quarter"]] = Field(default="annual")


class YFinanceIncomeStatementData(IncomeStatementData):
    """Yahoo Finance Income Statement Data."""

    __alias_dict__ = {
        "selling_general_and_admin_expense": "selling_general_and_administration",
        "research_and_development_expense": "research_and_development",
        "total_pre_tax_income": "pretax_income",
        "net_income_attributable_to_common_shareholders": "net_income_common_stockholders",
        "weighted_average_basic_shares_outstanding": "basic_average_shares",
        "weighted_average_diluted_shares_outstanding": "diluted_average_shares",
        "basic_earnings_per_share": "basic_eps",
        "diluted_earnings_per_share": "diluted_eps",
    }

    @field_validator("period_ending", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Validate the date field."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
        return v


class YFinanceIncomeStatementFetcher(
    Fetcher[
        YFinanceIncomeStatementQueryParams,
        List[YFinanceIncomeStatementData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceIncomeStatementQueryParams:
        """Transform the query parameters."""
        return YFinanceIncomeStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        # pylint: disable=unused-argument
        query: YFinanceIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[YFinanceIncomeStatementData]:
        """Extract the data from the Yahoo Finance endpoints."""
        period = "yearly" if query.period == "annual" else "quarterly"
        data = Ticker(query.symbol).get_income_stmt(
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
        query: YFinanceIncomeStatementQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceIncomeStatementData]:
        """Transform the data."""
        return [YFinanceIncomeStatementData.model_validate(d) for d in data]
