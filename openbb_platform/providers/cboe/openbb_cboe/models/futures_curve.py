"""CBOE Futures Curve Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_curve import (
    FuturesCurveData,
    FuturesCurveQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

SymbolChoices = Literal["VX_AM", "VX_EOD"]


class CboeFuturesCurveQueryParams(FuturesCurveQueryParams):
    """CBOE Futures Curve Query.

    Source: https://www.cboe.com/
    """

    __json_schema_extra__ = {"date": {"multiple_items_allowed": True}}

    symbol: SymbolChoices = Field(
        default="VX_EOD",
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + "Default is 'VX_EOD'. Entered dates return the data nearest to the entered date."
        + "\n    'VX_AM' = Mid-Morning TWAP Levels"
        + "\n    'VX_EOD' = 4PM Eastern Time Levels",
        json_schema_extra={"choices": ["VX_AM", "VX_EOD"]},
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def validate_symbol(cls, v):
        """Validate the symbol."""
        if not v or v.lower() in ["vx", "vix", "^vix", "vix_index"]:
            return "VX_EOD"
        return v.upper()


class CboeFuturesCurveData(FuturesCurveData):
    """CBOE Futures Curve Data."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )


class CboeFuturesCurveFetcher(
    Fetcher[
        CboeFuturesCurveQueryParams,
        List[CboeFuturesCurveData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeFuturesCurveQueryParams:
        """Transform the query."""
        return CboeFuturesCurveQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CboeFuturesCurveQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the CBOE endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_cboe.utils.vix import get_vx_by_date, get_vx_current

        symbol = "am" if query.symbol == "VX_AM" else "eod"
        if query.date is not None:
            data = await get_vx_by_date(
                date=query.date,  # type: ignore
                vx_type=symbol,
                use_cache=False,
            )
        else:
            data = await get_vx_current(vx_type=symbol, use_cache=False)

        if data.empty:
            raise EmptyDataError("The response was returned empty.")

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        query: CboeFuturesCurveQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[CboeFuturesCurveData]:
        """Transform data."""
        return [CboeFuturesCurveData.model_validate(d) for d in data]
