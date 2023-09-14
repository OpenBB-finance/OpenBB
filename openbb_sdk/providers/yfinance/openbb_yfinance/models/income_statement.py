"""yfinance Income Statement Fetcher."""


import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from pydantic import validator
from yfinance import Ticker


class YFinanceIncomeStatementQueryParams(IncomeStatementQueryParams):
    """yfinance Income Statement QueryParams.

    Source: https://finance.yahoo.com/
    """


class YFinanceIncomeStatementData(IncomeStatementData):
    """yfinance Income Statement Data."""

    # TODO: Standardize the fields

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()


class YFinanceIncomeStatementFetcher(
    Fetcher[
        YFinanceIncomeStatementQueryParams,
        List[YFinanceIncomeStatementData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceIncomeStatementQueryParams:
        return YFinanceIncomeStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[YFinanceIncomeStatementData]:
        query.period = "yearly" if query.period == "annual" else "quarterly"
        data = Ticker(query.symbol).get_income_stmt(
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
    ) -> List[YFinanceIncomeStatementData]:
        return [YFinanceIncomeStatementData.parse_obj(d) for d in data]
