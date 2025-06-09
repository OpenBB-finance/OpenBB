"""Port information and metadata."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class PortInfoQueryParams(QueryParams):
    """Port Information Query."""


class PortInfoData(Data):
    """Port Information Data."""

    port_code: str = Field(description="Unique ID assigned to the port by the source.")
