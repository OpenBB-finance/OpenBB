"""ETF Search Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class EtfSearchQueryParams(QueryParams):
    """ETF Search Query."""

    query: str | None = Field(description="Search query.", default="")


class EtfSearchData(Data):
    """ETF Search Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", "") + "(ETF)")
    name: str | None = Field(description="Name of the ETF.", default=None)
