"""IMF Direction Of Trade Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.direction_of_trade import (
    DirectionOfTradeData,
    DirectionOfTradeQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_imf.utils.dot_helpers import (
    get_label_to_code_map,
    resolve_country_input,
)
from pydantic import ConfigDict, Field, field_validator

dot_indicators_dict = {
    "exports": "XG_FOB_USD",
    "imports": "MG_CIF_USD",
    "balance": "TBG_USD",
    "all": "*",
}


class ImfDirectionOfTradeQueryParams(DirectionOfTradeQueryParams):
    """IMF Direction Of Trade Query Parameters."""

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": list(get_label_to_code_map()),
            "x-widget_config": {"value": "united_states", "style": {"popupWidth": 600}},
        },
        "counterpart": {
            "multiple_items_allowed": True,
            "choices": ["all"] + list(get_label_to_code_map()),
            "x-widget_config": {"value": "world", "style": {"popupWidth": 600}},
        },
    }

    limit: int | None = Field(
        default=None,
        description="Limit the number of results returned, the most recent data points first.",
    )

    @field_validator("country", "counterpart", mode="before")
    @classmethod
    def _validate_country_fields(cls, v):
        """Validate country and counterpart fields.

        Accepts both ISO3 codes (e.g., 'USA') and snake_case country names
        (e.g., 'united_states'). Converts names to ISO3 codes.
        """
        if not v:
            raise ValueError("Required parameter for IMF provider not supplied.")

        if isinstance(v, str) and v.lower() in ["all", "*"]:
            return "*"

        # Split by comma if string
        values = (
            v.split(",")
            if isinstance(v, str) and "," in v
            else [v] if isinstance(v, str) else v
        )

        result: list[str] = []
        for item in values:
            item_stripped = item.strip()
            if item_stripped.lower() in ["all", "*"]:
                if len(values) > 1:
                    raise ValueError(
                        "'all' cannot be used with other country codes in a list."
                    )
                return "*"
            # Resolve the country input (handles both codes and names)
            resolved = resolve_country_input(item_stripped)
            result.append(resolved)

        return ",".join(result)


class ImfDirectionOfTradeData(DirectionOfTradeData):
    """IMF Direction Of Trade Data."""

    model_config = ConfigDict(extra="ignore")
    __alias_dict__ = {
        "date": "TIME_PERIOD",
        "symbol": "series_id",
        "country": "COUNTRY",
        "counterpart": "COUNTERPART_COUNTRY",
        "counterpart_code": "counterpart_country_code",
        "value": "OBS_VALUE",
        "scale": "SCALE",
        "frequency": "FREQUENCY",
    }

    date: dateType | int = Field(description="The date of the data.")
    country: str = Field(description="The country or region to the trade.")
    unit: str | None = Field(default=None, description="Unit of the value.")
    country_code: str = Field(description="IMF country code.")
    counterpart: str = Field(description="Counterpart country or region to the trade.")
    counterpart_code: str = Field(description="IMF counterpart country code.")
    symbol: str | None = Field(
        default=None,
        description="Symbol representing the entity requested in the data. Concatenated series identifier.",
    )
    title: str | None = Field(
        default=None, description="Title corresponding to the symbol."
    )
    value: float = Field(description="Trade value.")
    scale: str | None = Field(default=None, description="Scale of the value.")
    unit_multiplier: int | None = Field(
        default=None, description="Unit multiplier of the value."
    )

    @field_validator("symbol", mode="before")
    @classmethod
    def _validate_symbol(cls, v):
        """Format symbol to indicators format."""
        symbol = v.split("IMTS_")[-1]
        return f"IMTS::{symbol}"


class ImfDirectionOfTradeFetcher(
    Fetcher[ImfDirectionOfTradeQueryParams, list[ImfDirectionOfTradeData]]
):
    """IMF Direction Of Trade Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ImfDirectionOfTradeQueryParams:
        """Transform query parameters."""
        return ImfDirectionOfTradeQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ImfDirectionOfTradeQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the IMF API."""
        # pylint: disable=import-outside-toplevel
        from openbb_imf.utils.dot_helpers import imts_query

        if query.limit:
            kwargs = {"lastNObservations": query.limit}

        try:
            return imts_query(
                country=query.country or "",
                counterpart=query.counterpart or "",
                indicator=dot_indicators_dict.get(query.direction, "*"),
                freq=query.frequency[0].upper(),
                start_date=(
                    query.start_date.strftime("%Y-%m-%d") if query.start_date else None
                ),
                end_date=(
                    query.end_date.strftime("%Y-%m-%d") if query.end_date else None
                ),
                **kwargs,
            )
        except (ValueError, OpenBBError) as e:
            raise OpenBBError(e) from e

    @staticmethod
    def transform_data(
        query: ImfDirectionOfTradeQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> AnnotatedResult[list[ImfDirectionOfTradeData]]:
        """Transform the data."""
        meta = data.get("metadata", {})
        records = data.get("data", [])

        if not records:
            raise EmptyDataError("No data found for the given query parameters.")

        return AnnotatedResult(
            result=[
                ImfDirectionOfTradeData.model_validate(record) for record in records
            ],
            metadata=meta,
        )
