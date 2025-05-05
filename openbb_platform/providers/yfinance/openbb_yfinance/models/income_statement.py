"""Yahoo Finance Income Statement Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class YFinanceIncomeStatementQueryParams(IncomeStatementQueryParams):
    """Yahoo Finance Income Statement Query.

    Source: https://finance.yahoo.com/
    """

    __json_schema_extra__ = {
        "period": {
            "choices": ["annual", "quarter"],
        }
    }

    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    limit: Optional[int] = Field(
        default=5,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
        le=5,
    )


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
    @classmethod
    def date_validate(cls, v):
        """Validate the date field."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
        return v


class YFinanceIncomeStatementFetcher(
    Fetcher[
        YFinanceIncomeStatementQueryParams,
        list[YFinanceIncomeStatementData],
    ]
):
    """Yahoo Finance Income Statement Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFinanceIncomeStatementQueryParams:
        """Transform the query parameters."""
        return YFinanceIncomeStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceIncomeStatementQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[YFinanceIncomeStatementData]:
        """Extract the data from the Yahoo Finance endpoints."""
        # pylint: disable=import-outside-toplevel
        import json  # noqa
        from curl_adapter import CurlCffiAdapter
        from numpy import nan
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_core.provider.utils.helpers import (
            get_requests_session,
            to_snake_case,
        )
        from yfinance import Ticker

        period = "yearly" if query.period == "annual" else "quarterly"
        session = get_requests_session()
        session.mount("https://", CurlCffiAdapter())
        session.mount("http://", CurlCffiAdapter())

        data = Ticker(
            query.symbol,
            session=session,
        ).get_income_stmt(as_dict=False, pretty=False, freq=period)

        if data is None:
            raise EmptyDataError()

        if query.limit:
            data = data.iloc[:, : query.limit]

        data.index = [to_snake_case(i) for i in data.index]
        data = data.reset_index().sort_index(ascending=False).set_index("index")
        data = data.replace({nan: None}).to_dict()
        data = [{"period_ending": str(key), **value} for key, value in data.items()]
        data = json.loads(json.dumps(data))

        return data

    @staticmethod
    def transform_data(
        query: YFinanceIncomeStatementQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[YFinanceIncomeStatementData]:
        """Transform the data."""
        return [YFinanceIncomeStatementData.model_validate(d) for d in data]
