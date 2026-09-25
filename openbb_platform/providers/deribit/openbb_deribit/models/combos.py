"""Deribit Combos Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_deribit.utils.constants import (
    COMBO_CHOICES_ENDPOINT,
    SYMBOL_STYLE,
    AnyListingCurrencies,
)


class DeribitCombosQueryParams(QueryParams):
    """Deribit Combos Query.

    Source: https://docs.deribit.com/api-reference/combo-books/public-get_combos
    """

    __json_schema_extra__ = {
        "combo_id": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": COMBO_CHOICES_ENDPOINT,
                "style": SYMBOL_STYLE,
            },
        }
    }

    currency: AnyListingCurrencies = Field(
        default="BTC", description="The currency the combos settle in."
    )
    combo_id: str | None = Field(
        default=None,
        description="One or more combo identifiers. When given, the currency is"
        + " ignored.",
    )


class DeribitCombosData(Data):
    """Deribit Combos Data."""

    combo_id: str = Field(
        description="The identifier of the combo.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Combo ID",
                "chartDataType": "category",
                "pinned": "left",
            }
        },
    )
    instrument_id: int | None = Field(
        default=None,
        description="The numeric identifier of the combo.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Instrument ID",
                "cellDataType": "text",
                "chartDataType": "excluded",
                "hide": True,
            }
        },
    )
    state: str | None = Field(
        default=None,
        description="Whether the combo is still tradeable.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    leg: str = Field(
        description="The instrument the leg trades.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    amount: float | None = Field(
        default=None,
        description="The size of the leg. A negative amount is a sold leg.",
        json_schema_extra={"x-widget_config": {"chartDataType": "series"}},
    )
    creation_timestamp: datetime | None = Field(
        default=None,
        description="When the combo was listed.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    state_timestamp: datetime | None = Field(
        default=None,
        description="When the combo last changed state.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )

    @field_validator(
        "creation_timestamp", "state_timestamp", mode="before", check_fields=False
    )
    @classmethod
    def validate_timestamp(cls, v):
        """Read the timestamp as a datetime."""
        from openbb_deribit.utils.helpers import from_timestamp

        return from_timestamp(v) if v else None


class DeribitCombosFetcher(Fetcher[DeribitCombosQueryParams, list[DeribitCombosData]]):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitCombosQueryParams:
        """Transform the query."""
        return DeribitCombosQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitCombosQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If the exchange lists no matching combo.
        """
        from openbb_deribit.utils.client import gather, request
        from openbb_deribit.utils.helpers import normalize_currency

        if query.combo_id:
            ids = [c.strip() for c in query.combo_id.split(",") if c.strip()]
            results = await gather(
                [("get_combo_details", {"combo_id": c}) for c in ids]
            )
            data = [result for result in results if isinstance(result, dict) and result]
        else:
            data = await request(
                "get_combos", {"currency": normalize_currency(query.currency)}
            )

        if not data:
            raise EmptyDataError("Deribit lists no combo matching the query.")

        return data

    @staticmethod
    def transform_data(
        query: DeribitCombosQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitCombosData]:
        """Transform the data to the model."""
        records: list[dict] = []

        for combo in data:
            for leg in combo.get("legs") or []:
                records.append(
                    {
                        "combo_id": combo.get("id"),
                        "instrument_id": combo.get("instrument_id"),
                        "state": combo.get("state"),
                        "leg": leg.get("instrument_name"),
                        "amount": leg.get("amount"),
                        "creation_timestamp": combo.get("creation_timestamp"),
                        "state_timestamp": combo.get("state_timestamp"),
                    }
                )

        return [
            DeribitCombosData.model_validate(record)
            for record in sorted(records, key=lambda d: (d["combo_id"], d["leg"]))
        ]
