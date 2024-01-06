"""ESG Sector Standard Model."""

from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams


class ESGSectorQueryParams(QueryParams):
    """ESG Sector Query."""

    year: Optional[int] = Field(default=None, description="The year to get data for.")


class ESGSectorData(Data):
    """ESG Sector Data."""

    sector: Optional[str] = Field(default=None, description="The sector")
    environmental_score: Optional[float] = Field(
        default=None, description="Environmental score of the company."
    )
    social_score: Optional[float] = Field(
        default=None, description="Social score of the company."
    )
    governance_score: Optional[float] = Field(
        default=None, description="Governance score of the company."
    )
    esg_score: Optional[float] = Field(
        default=None, description="ESG score of the company."
    )
