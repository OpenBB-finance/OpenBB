"""ETF Holdings data model."""


from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class EtfHoldingsQueryParams(QueryParams):
    """ETF Holdings Query Params"""

    symbol: str = Field(description="The exchange ticker symbol for the ETF.")

class EtfHoldingsData(Data):
    """ETF Holdings Data."""
