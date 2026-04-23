"""Commitment of Traders Reports Search Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class CotSearchQueryParams(QueryParams):
    """Commitment of Traders Reports Search Query."""

    code: str | None = Field(
        default=None,
        description="A string with the market contract code (can be partial).",
    )
    query: str = Field(description="Search query.", default="")


class CotSearchData(Data):
    """Commitment of Traders Reports Search Data."""

    code: str = Field(
        description="CFTC market contract code of the report.",
        json_schema_extra={
            "x-widget_config": {
                "renderFn": "cellOnClick",
                "renderFnParams": {
                    "actionType": "groupBy",
                    "groupByParamName": "code",
                },
            },
        },
    )
    name: str = Field(description="Name of the underlying asset.")
    category: str | None = Field(
        default=None, description="Category of the underlying asset."
    )
    subcategory: str | None = Field(
        default=None, description="Subcategory of the underlying asset."
    )
    units: str | None = Field(default=None, description="The units for one contract.")
    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
