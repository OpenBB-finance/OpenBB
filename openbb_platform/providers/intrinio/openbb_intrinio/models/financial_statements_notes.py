"""Intrinio Financial Statements Notes Model."""

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.financial_statements_notes import (
    FinancialStatementsNotesData,
    FinancialStatementsNotesQueryParams,
)
from openbb_intrinio.utils.helpers import get_data_one
from pydantic import Field


class IntrinioFinancialStatementsNotesQueryParams(FinancialStatementsNotesQueryParams):
    """Intrinio Financial Statements Notes Query."""

    content_format: Literal["text", "html"] = Field(
        default="text", description="Format of the content, either text or html."
    )


class IntrinioFinancialStatementsNotesData(FinancialStatementsNotesData):
    """Intrinio Financial Statements Notes Data."""

    report_type: Optional[str] = Field(
        default=None, description="The type of report the note is from."
    )
    intrinio_id: Optional[str] = Field(
        default=None, description="The Intrinio ID for the note."
    )


class IntrinioFinancialStatementsNotesFetcher(
    Fetcher[
        IntrinioFinancialStatementsNotesQueryParams,
        IntrinioFinancialStatementsNotesData,
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> IntrinioFinancialStatementsNotesQueryParams:
        """Transform the query params."""
        return IntrinioFinancialStatementsNotesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: IntrinioFinancialStatementsNotesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        data: Dict = {}

        url = f"https://api-v2.intrinio.com/filings/notes/{query.tag}?content_format={query.content_format}&api_key={api_key}"

        data = get_data_one(url)

        return data

    @staticmethod
    def transform_data(
        query: IntrinioFinancialStatementsNotesQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> IntrinioFinancialStatementsNotesData:
        """Return the transformed data."""
        results = {
            "cik": data["filing"].get("cik", None),
            "filing_date": data["filing"].get("filing_date", None),
            "period_ending": data["filing"].get("period_end_date", None),
            "report_type": data["filing"].get("report_type", None),
            "xbrl_tag": data.get("xbrl_tag", None),
            "intrinio_id": data.get("id", None),
            "content": data.get("content", None),
        }
        return IntrinioFinancialStatementsNotesData.model_validate(results)
