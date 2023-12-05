"""Financial Statements Notes Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
)


class FinancialStatementsNotesQueryParams(QueryParams):
    """Financial Statements Notes Query."""

    tag: str = Field(
        description="The data tag for the note."
        + " Use `financial_statements_notes_tags()` to get a list of tags."
        + " For Intrinio, use the associated 'intrinio_id'."
    )


class FinancialStatementsNotesData(Data):
    """Financial Statements Notes Data."""

    content: str = Field(description="The contents of the note.")
    period_ending: Optional[dateType] = Field(
        default=None, description="The date of the period ending the report."
    )
    filing_date: Optional[dateType] = Field(
        description="The date of the filing", default=None
    )
    cik: Optional[str] = Field(default=None, description=DATA_DESCRIPTIONS.get("cik"))
    xbrl_tag: Optional[str] = Field(
        default=None, description="The XBRL tag for the note."
    )
