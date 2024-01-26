"""Compare Groups Model."""

from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams


class CompareGroupsQueryParams(QueryParams):
    """Compare Groups Query."""

    group: Optional[str] = Field(
        default=None,
        description="The group to compare - i.e., 'sector', 'industry', 'country'. Choices vary by provider.",
    )
    metric: Optional[str] = Field(
        default=None,
        description="The type of metrics to compare - i.e, 'valuation', 'performance'. Choices vary by provider.",
    )


class CompareGroupsData(Data):
    """Compare Groups Data."""

    name: str = Field(description="Name or label of the group.")
