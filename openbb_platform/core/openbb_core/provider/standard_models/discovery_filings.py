"""Discovery Filings Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, NonNegativeInt


class DiscoveryFilingsQueryParams(QueryParams):
    """Discovery Filings Query."""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["start_date"],
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["end_date"],
    )
    form_type: str | None = Field(
        default=None,
        description=(
            "Filter by form type. Visit https://www.sec.gov/forms for a list of supported form types."
        ),
    )
    limit: NonNegativeInt | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("limit", "")
    )


class DiscoveryFilingsData(Data):
    """Discovery Filings Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    cik: str = Field(description=DATA_DESCRIPTIONS.get("cik", ""))
    filing_date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    accepted_date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("accepted_date", "")
    )
    form_type: str = Field(description="The form type of the filing")
    link: str = Field(description="URL to the filing page on the SEC site.")
