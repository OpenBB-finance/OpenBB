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
        return YFinanceCashFlowStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[YFinanceCashFlowStatementData]:
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
        query: YFinanceCashFlowStatementQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceCashFlowStatementData]:
        return [YFinanceCashFlowStatementData.model_validate(d) for d in data]
