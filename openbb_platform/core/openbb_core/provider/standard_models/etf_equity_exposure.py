"""ETF Equity Exposure Standard Model."""

from typing import Optional, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class EtfEquityExposureQueryParams(QueryParams):
    """ETF Equity Exposure Query Params."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", "") + " (Stock)")

    @field_validator("symbol")
    @classmethod
    def upper_symbol(cls, v: str) -> str:
        """Convert symbol to uppercase."""
        return v.upper()


class EtfEquityExposureData(Data):
    """ETF Equity Exposure Data."""

    equity_symbol: str = Field(description="The symbol of the equity requested.")
    etf_symbol: str = Field(
        description="The symbol of the ETF with exposure to the requested equity."
    )
    shares: Optional[int] = Field(
        default=None,
        description="The number of shares held in the ETF.",
    )
    weight: Optional[float] = Field(
        default=None,
        description="The weight of the equity in the ETF, as a normalized percent.",
        json_schema_extra={"units_measurement": "percent", "frontend_multiply": 100},
    )
    market_value: Optional[Union[int, float]] = Field(
        default=None,
        description="The market value of the equity position in the ETF.",
    )
