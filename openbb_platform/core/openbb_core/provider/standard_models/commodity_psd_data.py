"""Commodity Production Supply & Demand Data Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class CommodityPsdDataQueryParams(QueryParams):
    """Commodity Production Supply & Demand Data Query."""


class CommodityPsdData(Data):
    """Commodity Production Supply & Demand Data."""

    region: str | None = Field(default=None, description="Region group category.")
    country: str | None = Field(
        default=None,
        description="Country or area name.",
    )
    commodity: str | None = Field(
        default=None,
        description="Commodity name.",
    )
    attribute: str | None = Field(
        default=None,
        description="Name of the row value.",
    )
    marketing_year: str | None = Field(
        default=None,
        description="Marketing year for the commodity.",
    )
    value: float | int | None = Field(
        default=None,
        description="Value for the commodity attribute in the given marketing year.",
    )
    unit: str | None = Field(
        default=None,
        description="Unit of measurement for the value.",
    )
