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
            "Filter by form type. Check the data provider for available types."
        ),
    )
    limit: NonNegativeInt = Field(
        default=100, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: Union[str, List[str], Set[str]]):
        """Convert field to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)]) if v else None


class CompanyFilingsData(Data):
    """Company Filings Data."""

    filing_date: dateType = Field(description="The date of the filing.")
    accepted_date: Optional[datetime] = Field(
        default=None, description="Accepted date of the filing."
    )
    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    cik: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("cik", "")
    )
    report_type: Optional[str] = Field(default=None, description="Type of filing.")
    filing_url: Optional[str] = Field(
        default=None, description="URL to the filing page."
    )
    report_url: str = Field(description="URL to the actual report.")

    @field_validator("filing_date", "accepted_date", mode="before", check_fields=False)
    @classmethod
    def convert_date(cls, v: str):
        """Convert date to date type."""
        return parser.parse(str(v)).date() if v else None
