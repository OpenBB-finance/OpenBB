"""ETF Equity Exposure Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class EtfEquityExposureQueryParams(QueryParams):
    """ETF Equity Exposure Query Params."""

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "") + " (underlying equity)"
    )

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class EtfEquityExposureData(Data):
    """ETF Equity Exposure Data."""

    equity_symbol: str = Field(description="The symbol of the equity requested.")
    etf_symbol: str = Field(
        description="The symbol of the ETF with exposure to the requested equity."
    )
    weight: float | None = Field(
        default=None,
        description="The weight of the equity in the ETF, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    market_value: int | float | None = Field(
        default=None,
        description="The market value of the equity position in the ETF.",
    )
    shares: int | float | None = Field(
        default=None,
        description="Number of reported shares controlled by the ETF.",
    )
