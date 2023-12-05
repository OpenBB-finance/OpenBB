"""Financial Statements Notes Tags Standard Model."""

from datetime import date as dateType
from typing import Literal, Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class FinancialStatementsNotesTagsQueryParams(QueryParams):
    """Financial Statements Notes Tags Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol"))
    period: Optional[Literal["annual", "quarter"]] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period")
    )
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class FinancialStatementsNotesTagsData(Data):
    """Financial Statements Notes Tags Data."""

    period_ending: Optional[dateType] = Field(
        default=None, description="The date of the period ending the report."
    )
    filing_date: dateType = Field(description="The date of the filing")
    cik: Optional[str] = Field(default=None, description=DATA_DESCRIPTIONS.get("cik"))
    xbrl_tag: Optional[str] = Field(
        default=None, description="The XBRL tag for the note."
    )
