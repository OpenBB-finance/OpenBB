"""Maritime chokepoint information and metadata."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class MaritimeChokePointInfoQueryParams(QueryParams):
    """MaritimeChokepointInfo Query."""


class MaritimeChokePointInfoData(Data):
    """MaritimeChokepointInfo Data."""

    chokepoint_code: str = Field(
        description="Unique ID assigned to the chokepoint by the source."
    )
