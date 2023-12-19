"""Yahoo Finance Cash Flow Statement Model."""

import json
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import to_snake_case
from pydantic import Field, field_validator
from yfinance import Ticker


class YFinanceCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """Yahoo Finance Cash Flow Statement Query.

    Source: https://finance.yahoo.com/
    """

    period: Optional[Literal["annual", "quarter"]] = Field(default="annual")


class YFinanceCashFlowStatementData(CashFlowStatementData):
    """Yahoo Finance Cash Flow Statement Data."""

    __alias_dict__ = {
        "investments_in_property_plant_and_equipment": "purchase_of_ppe",
        "issuance_of_common_equity": "common_stock_issuance",
        "repurchase_of_common_equity": "common_stock_payments",
        "cash_dividends_paid": "payment_of_dividends",
        "net_change_in_cash_and_equivalents": "changes_in_cash",
    }

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return datetime object from string."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
        return v


class YFinanceCashFlowStatementFetcher(
    Fetcher[
        YFinanceCashFlowStatementQueryParams,
        List[YFinanceCashFlowStatementData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceCashFlowStatementQueryParams:
        """Transform the query parameters."""
        return YFinanceCashFlowStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        # pylint: disable=unused-argument
        query: YFinanceCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[YFinanceCashFlowStatementData]:
        """Extract the data from the Yahoo Finance endpoints."""
        period = "yearly" if query.period == "annual" else "quarterly"  # type: ignore
        data = Ticker(query.symbol).get_cash_flow(
            as_dict=False, pretty=False, freq=period
        )

        if data is None:
            raise EmptyDataError()

        data.index = [to_snake_case(i) for i in data.index]
        data = data.reset_index().sort_index(ascending=False).set_index("index")
        data = data.convert_dtypes().fillna(0).replace(0, None).to_dict()
        data = [{"period_ending": str(key), **value} for key, value in data.items()]

        data = json.loads(json.dumps(data))

        return data

    @staticmethod
    def transform_data(
        # pylint: disable=unused-argument
        query: YFinanceCashFlowStatementQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceCashFlowStatementData]:
        """Transform the data."""
        return [YFinanceCashFlowStatementData.model_validate(d) for d in data]
