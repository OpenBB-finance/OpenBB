"""Latest Attributes Standard Model."""

from typing import Optional, Union

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class LatestAttributesQueryParams(QueryParams):
    """Latest Attributes Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol"))
    tag: str = Field(description="Intrinio data tag ID or code.")


class LatestAttributesData(Data):
    """Latest Attributes Data."""

    value: Optional[Union[str, float]] = Field(
        default=None, description="The value of the data."
    )
