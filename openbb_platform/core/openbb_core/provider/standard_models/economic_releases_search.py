"""Economic Releases Search Model."""

from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams


class EconomicReleasesSearchQueryParams(QueryParams):
    """Economic Releases Query Params."""

    query: str = Field(description="Term to search the releases for.")


class EconomicReleasesSearchData(Data):
    """Economic Releases Search Data."""

    id: int = Field(description="The release ID for FRED queries.")
    name: str = Field(description="The name of the release.")
    press_release: Optional[bool] = Field(
        description="If the release is a press release.",
        default=None,
    )
    url: Optional[str] = Field(default=None, description="URL to the release.")
    notes: Optional[str] = Field(
        default=None, description="Description of the release."
    )
