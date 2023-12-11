"""Intrinio Reported Financials Model."""


from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.financial_statements import (
    CashFlowStatementData,
    FinancialStatementsQueryParams,
)
from openbb_intrinio.utils.helpers import (
    async_get_all_fundamentals_ids,
    async_get_data_one,
    generate_fundamentals_url,
)
from pydantic import Field

STATEMENT_DICT = {
    "balance": "balance_sheet_statement",
    "income": "income_statement",
    "cash": "cash_flow_statement",
}


class IntrinioReportedFinancialsQueryParams(FinancialStatementsQueryParams):
    """Intrinio Reported Financials Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_fundamentals_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2
    """

    statement: Literal["balance", "income", "cash"] = Field(
        default="income",
        description="The type of financial statement.",
    )
    period: Literal["annual", "quarter", "ttm", "ytd"] = Field(default="annual")
    use_cache: Optional[bool] = Field(
        default=True,
        description="Whether to use cached data or not.",
    )


class IntrinioReportedFinancialsData(CashFlowStatementData):
    """Intrinio Reported Financials Data."""

    __alias_dict__ = {}


class IntrinioCashFlowStatementFetcher(
    Fetcher[
        IntrinioReportedFinancialsQueryParams,
        List[IntrinioReportedFinancialsData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> IntrinioReportedFinancialsQueryParams:
        """Transform the query params."""
        return IntrinioReportedFinancialsQueryParams(**params)

    @staticmethod
    async def extract_data(
        query: IntrinioReportedFinancialsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""

        api_key = credentials.get("intrinio_api_key") if credentials else ""
        statement_code = STATEMENT_DICT[query.statement]
        if query.period in ["quarter", "annual"]:
            period_type = "FY" if query.period == "annual" else "Q"
        if query.period in ["ttm", "ytd"]:
            period_type = query.period.upper()

        data: List[Dict] = []

        fundamentals_ids = await async_get_all_fundamentals_ids(
            symbol=query.symbol,
            api_key=api_key,
            period=period_type,
            statement=statement_code,
            use_cache=query.use_cache,
        )

        if len(fundamentals_ids) > 0:
            ids = fundamentals_ids.iloc[: query.limit]["id"].to_list()

        urls = [generate_fundamentals_url(id, api_key, as_reported=True) for id in ids]

        async def async_get_financial_statement_data(url, data: List[Dict]):
            statement_data: Dict = {}
            statement_data = await async_get_data_one(url, **kwargs)

            data.append(
                {
                    "period_ending": statement_data["fundamental"]["end_date"],
                    "fiscal_year": statement_data["fundamental"]["fiscal_year"],
                    "fiscal_period": statement_data["fundamental"]["fiscal_period"],
                    "financials": statement_data[f"{report_type}_financials"],
                }
            )

        for i in range(0, len(urls)):
            await async_get_financial_statement_data(urls[i], data)

        return sorted(data, key=lambda x: x["period_ending"], reverse=True)

    @staticmethod
    def transform_data(
        query: IntrinioCashFlowStatementQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioReportedFinancialsData]:
        """Return the transformed data."""
        transformed_data: List[IntrinioReportedFinancialsData] = []
        data_tag = "xbrl_tag"
        for item in data:
            sub_dict: Dict[str, Any] = {}

            for sub_item in item["financials"]:
                field_name = sub_item[data_tag]["tag"]
                sub_dict[field_name] = float(sub_item["value"])

            sub_dict["period_ending"] = item["period_ending"]
            sub_dict["fiscal_year"] = item["fiscal_year"]
            sub_dict["fiscal_period"] = item["fiscal_period"]

            transformed_data.append(IntrinioReportedFinancialsData(**sub_dict))

        return transformed_data
