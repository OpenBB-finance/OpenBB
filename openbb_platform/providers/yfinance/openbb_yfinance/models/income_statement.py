"""Yahoo Finance Income Statement Model."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from pydantic import field_validator
from yfinance import Ticker


class YFinanceIncomeStatementQueryParams(IncomeStatementQueryParams):
    """Yahoo Finance Income Statement Query.

    Source: https://finance.yahoo.com/
    """


class YFinanceIncomeStatementData(IncomeStatementData):
    """Yahoo Finance Income Statement Data."""

    # TODO: Standardize the fields
    @field_validator("date", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
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
        return YFinanceIncomeStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[YFinanceIncomeStatementData]:
        period = "yearly" if query.period == "annual" else "quarterly"
        data = Ticker(query.symbol).get_income_stmt(
            as_dict=False, pretty=False, freq=period
        )
        data = data.convert_dtypes().fillna(0).to_dict()
        data = [{"date": str(key), **value} for key, value in data.items()]
        # To match standardization
        for d in data:
            d["Symbol"] = query.symbol
        data = json.loads(json.dumps(data))

        return data

    @staticmethod
    def transform_data(
        query: YFinanceIncomeStatementQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceIncomeStatementData]:
        return [YFinanceIncomeStatementData.model_validate(d) for d in data]
