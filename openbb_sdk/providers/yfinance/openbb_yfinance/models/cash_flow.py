"""yfinance Cash Flow Statement Fetcher."""


import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from pydantic import validator
from yfinance import Ticker


class YFinanceCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """yfinance Cash Flow Statement QueryParams.

    Source: https://finance.yahoo.com/
    """


class YFinanceCashFlowStatementData(CashFlowStatementData):
    """yfinance Cash Flow Statement Data."""

    # TODO: Standardize the fields

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()


class YFinanceCashFlowStatementFetcher(
    Fetcher[
        YFinanceCashFlowStatementQueryParams,
        List[YFinanceCashFlowStatementData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceCashFlowStatementQueryParams:
        return YFinanceCashFlowStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[YFinanceCashFlowStatementData]:
        query.period = "yearly" if query.period == "annual" else "quarterly"  # type: ignore
        data = Ticker(query.symbol).get_cash_flow(
            as_dict=True, pretty=False, freq=query.period
        )
        data = [{"date": str(key), **value} for key, value in data.items()]
        # To match standardization
        for d in data:
            d["Symbol"] = query.symbol
        data = json.loads(json.dumps(data))

        return data

    @staticmethod
    def transform_data(
        data: List[Dict],
    ) -> List[YFinanceCashFlowStatementData]:
        return [YFinanceCashFlowStatementData.parse_obj(d) for d in data]
