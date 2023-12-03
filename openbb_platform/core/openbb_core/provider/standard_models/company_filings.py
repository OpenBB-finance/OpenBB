"""Company Filings Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import List, Optional, Set, Union

from dateutil import parser
from pydantic import Field, NonNegativeInt, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class CompanyFilingsQueryParams(QueryParams):
    """Company Filings Query."""

    symbol: Optional[str] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("symbol", "")
    )
    form_type: Optional[str] = Field(
        default=None,
        description=(
            "Filter by form type. Visit https://www.sec.gov/forms "
            "for a list of supported form types."
        ),
    )
    limit: NonNegativeInt = Field(
        default=100, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)]) if v else None


class CompanyFilingsData(Data):
    """Company Filings Data."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    cik: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("cik", "")
    )
    filing_date: dateType = Field(description="Filing date of the SEC report.")
    accepted_date: datetime = Field(description="Accepted date of the SEC report.")
    report_type: str = Field(description="Type of the SEC report.")
    filing_url: str = Field(description="URL to the filing page on the SEC site.")
    report_url: str = Field(description="URL to the actual report on the SEC site.")

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)]) if v else None

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def convert_date(cls, v: str):
        """Convert date to date type."""
        return parser.parse(str(v)).date()
