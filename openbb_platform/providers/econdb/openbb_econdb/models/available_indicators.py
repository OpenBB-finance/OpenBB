"""EconDB Available Indicators."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.available_indicators import (
    AvailableIndicatorsData,
    AvailableIndicesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class EconDbAvailableIndicatorsQueryParams(AvailableIndicesQueryParams):
    """EconDB Available Indicators Query Parameters."""

    use_cache: bool = Field(
        default=True,
        description="Whether to use cache or not, by default is True"
        + " The cache of indicator symbols will persist for one week.",
    )


class EconDbAvailableIndicatorsData(AvailableIndicatorsData):
    """EconDB Available Indicators Data."""

    __alias_dict__ = {
        "symbol": "short_ticker",
        "country": "entity",
    }
    currency: Optional[str] = Field(
        default=None,
        description="The currency, or unit, the data is based in.",
    )
    scale: Optional[str] = Field(
        default=None,
        description="The scale of the data.",
    )
    multiplier: Optional[int] = Field(
        description="The multiplier of the data to arrive at whole units.",
    )
    transformation: str = Field(
        description="Transformation type.",
    )
    source: Optional[str] = Field(
        default=None,
        description="The original source of the data.",
    )
    first_date: Optional[dateType] = Field(
        default=None,
        description="The first date of the data.",
    )
    last_date: Optional[dateType] = Field(
        default=None,
        description="The last date of the data.",
    )
    last_insert_timestamp: Optional[datetime] = Field(
        default=None,
        description="The time of the last update. Data is typically reported with a lag.",
    )


class EconDbAvailableIndicatorsFetcher(
    Fetcher[EconDbAvailableIndicatorsQueryParams, List[EconDbAvailableIndicatorsData]]
):
    """EconDB Available Indicators Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> EconDbAvailableIndicatorsQueryParams:
        """Transform query."""
        return EconDbAvailableIndicatorsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: EconDbAvailableIndicatorsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        from openbb_econdb.utils.helpers import download_indicators

        df = await download_indicators(query.use_cache)
        if df.empty:
            raise EmptyDataError("There was an error fetching the data.")
        return df.sort_values(by="last_date", ascending=False).to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: EconDbAvailableIndicatorsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[EconDbAvailableIndicatorsData]:
        """Transform data."""
        return [EconDbAvailableIndicatorsData.model_validate(d) for d in data]
