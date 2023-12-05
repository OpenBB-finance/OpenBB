"""Intrinio Financial Statements Notes Tags Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.financial_statements_notes_tags import (
    FinancialStatementsNotesTagsData,
    FinancialStatementsNotesTagsQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_intrinio.utils.helpers import get_data_many
from pandas import DataFrame
from pydantic import Field


class IntrinioFinancialStatementsNotesTagsQueryParams(
    FinancialStatementsNotesTagsQueryParams
):
    """Intrinio Financial Attributes Query."""

    __alias_dict__ = {"limit": "page_size"}

    limit: Optional[int] = Field(
        default=1000, description=QUERY_DESCRIPTIONS.get("limit")
    )


class IntrinioFinancialStatementsNotesTagsData(FinancialStatementsNotesTagsData):
    """Intrinio Financial Attributes Data."""


class IntrinioFinancialStatementsNotesTagsFetcher(
    Fetcher[
        IntrinioFinancialStatementsNotesTagsQueryParams,
        List[IntrinioFinancialStatementsNotesTagsData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> IntrinioFinancialStatementsNotesTagsQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=5)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return IntrinioFinancialStatementsNotesTagsQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: IntrinioFinancialStatementsNotesTagsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        data: List[Dict] = []
        report_type = "10-K" if query.period == "annual" else "10-Q"
        base_url = f"https://api-v2.intrinio.com/filings/notes?company={query.symbol}&report_type={report_type}&"
        url = (
            f"{base_url}period_ended_start_date={query.start_date}"
            f"&period_ended_end_date={query.end_date}&page_size={query.limit}"
            f"&api_key={api_key}"
        )

        data = get_data_many(url, "filing_notes")

        return data

    @staticmethod
    def transform_data(
        query: IntrinioFinancialStatementsNotesTagsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioFinancialStatementsNotesTagsData]:
        """Return the transformed data."""
        results = {
            "filing_date": [d["filing"]["filing_date"] for d in data],
            "period_ending": [d["filing"]["period_end_date"] for d in data],
            "report_type": [d["filing"]["report_type"] for d in data],
            "xbrl_tag": [d["xbrl_tag"] for d in data],
            "intrinio_id": [d["id"] for d in data],
        }
        output = DataFrame(results).to_dict(orient="records")
        return [
            IntrinioFinancialStatementsNotesTagsData.model_validate(item)
            for item in output
        ]
