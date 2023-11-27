"""Discovery Filings Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional

from pydantic import Field, NonNegativeInt

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class DiscoveryFilingsQueryParams(QueryParams):
    """Discovery Filings Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["start_date"],
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["end_date"],
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


class DiscoveryFilingsData(Data):
    """Discovery Filings Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    cik: str = Field(description=DATA_DESCRIPTIONS.get("cik", ""))
    title: str = Field(description="Title of the filing.")
    date: datetime = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    form_type: str = Field(description="The form type of the filing")
    link: str = Field(description="URL to the filing page on the SEC site.")
