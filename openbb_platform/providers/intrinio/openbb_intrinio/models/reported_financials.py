"""Intrinio Reported Financials Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.reported_financials import (
    ReportedFinancialsData,
    ReportedFinancialsQueryParams,
)
from pydantic import Field

STATEMENT_DICT = {
    "balance": "balance_sheet_statement",
    "income": "income_statement",
    "cash": "cash_flow_statement",
}


class IntrinioReportedFinancialsQueryParams(ReportedFinancialsQueryParams):
    """Intrinio Reported Financials Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_fundamentals_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_reported_financials_v2
    """

    statement_type: Literal["balance", "income", "cash"] = Field(
        default="income",
        description="Cash flow statements are reported as YTD, Q4 is the same as FY.",
    )
    period: Literal["annual", "quarter"] = Field(default="annual")
    fiscal_year: Optional[int] = Field(
        default=None,
        description="The specific fiscal year.  Reports do not go beyond 2008.",
    )


class IntrinioReportedFinancialsData(ReportedFinancialsData):
    """
    Intrinio Reported Financials Data.

    The fields for this model are generated dynamically from the XBRL tags in the Intrinio response.
    """


class IntrinioReportedFinancialsFetcher(
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
    async def aextract_data(
        query: IntrinioReportedFinancialsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import (
            ClientResponse,
            amake_requests,
        )
        from openbb_intrinio.utils.helpers import get_data_one
        from pandas import DataFrame

        period_type = ""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        statement_code = STATEMENT_DICT[query.statement_type]
        period_type = "FY" if query.period == "annual" else "Q"
        ids = []
        ids_url = f"https://api-v2.intrinio.com/companies/{query.symbol}/fundamentals?reported_only=true&statement_code={statement_code}"
        if query.fiscal_year is not None:
            if query.fiscal_year < 2008:
                warn("Financials data is only available from 2008 and later.")
                query.fiscal_year = 2008
            ids_url = ids_url + f"&fiscal_year={query.fiscal_year}"
        ids_url = ids_url + f"&page_size=10000&api_key={api_key}"

        fundamentals_ids = await get_data_one(ids_url, **kwargs)
        filings = DataFrame(fundamentals_ids["fundamentals"])

        _period = "" if query.period is None else period_type
        _statement = "" if statement_code is None else statement_code
        if len(filings) > 0:
            filings = filings[filings["statement_code"].str.contains(_statement)]
            if query.period == "annual":
                filings = filings[filings["fiscal_period"].str.contains(_period)]
            ids = filings.iloc[: query.limit]["id"].to_list()

        if ids == []:
            raise OpenBBError("No reports found.")

        async def callback(response: ClientResponse, _: Any) -> Dict:
            """Return the response."""
            statement_data = await response.json()
            return {
                "period_ending": statement_data["fundamental"]["end_date"],  # type: ignore
                "fiscal_year": statement_data["fundamental"]["fiscal_year"],  # type: ignore
                "fiscal_period": statement_data["fundamental"]["fiscal_period"],  # type: ignore
                "financials": statement_data["reported_financials"],  # type: ignore
            }

        urls = [
            f"https://api-v2.intrinio.com/fundamentals/{id}/reported_financials?api_key={api_key}"
            for id in ids
        ]

        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioReportedFinancialsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioReportedFinancialsData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import to_snake_case

        transformed_data: List[IntrinioReportedFinancialsData] = []
        data_tag = "xbrl_tag"
        for item in data:
            sub_dict: Dict[str, Any] = {}

            for sub_item in item["financials"]:
                field_name = to_snake_case(sub_item[data_tag]["tag"])
                if sub_item["value"] and sub_item["value"] != 0:
                    sub_dict[field_name] = float(sub_item["value"])

            sub_dict["period_ending"] = item["period_ending"]
            sub_dict["fiscal_year"] = item["fiscal_year"]
            sub_dict["fiscal_period"] = item["fiscal_period"]

            transformed_data.append(IntrinioReportedFinancialsData(**sub_dict))

        return transformed_data
