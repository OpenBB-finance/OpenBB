"""Deribit Trade Volumes Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

DAY_VOLUMES = ("futures_volume", "calls_volume", "puts_volume", "spot_volume")


def _traded(record: dict) -> float:
    """Return everything that traded in one currency over the last day."""
    return sum(float(record.get(field) or 0) for field in DAY_VOLUMES)


class DeribitTradeVolumesQueryParams(QueryParams):
    """Deribit Trade Volumes Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_trade_volumes
    """

    extended: bool = Field(
        default=True,
        description="When True, adds the seven and thirty day volumes to the"
        + " trailing twenty-four hours.",
    )


class DeribitTradeVolumesData(Data):
    """Deribit Trade Volumes Data."""

    currency: str = Field(
        description="The currency the volume was traded in.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "category", "pinned": "left"}
        },
    )
    currency_pair: str | None = Field(
        default=None,
        description="The index the currency is priced against.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    futures_volume: float | None = Field(
        default=None,
        description="The futures volume of the last 24 hours.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Futures Volume",
                "chartDataType": "series",
            }
        },
    )
    calls_volume: float | None = Field(
        default=None,
        description="The call volume of the last 24 hours.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Calls Volume",
                "chartDataType": "excluded",
            }
        },
    )
    puts_volume: float | None = Field(
        default=None,
        description="The put volume of the last 24 hours.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Puts Volume",
                "chartDataType": "excluded",
            }
        },
    )
    spot_volume: float | None = Field(
        default=None,
        description="The spot volume of the last 24 hours.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Spot Volume",
                "chartDataType": "excluded",
            }
        },
    )
    futures_volume_7d: float | None = Field(
        default=None,
        description="The futures volume of the last seven days.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Futures Volume 7D",
                "chartDataType": "excluded",
            }
        },
    )
    calls_volume_7d: float | None = Field(
        default=None,
        description="The call volume of the last seven days.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Calls Volume 7D",
                "chartDataType": "excluded",
            }
        },
    )
    puts_volume_7d: float | None = Field(
        default=None,
        description="The put volume of the last seven days.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Puts Volume 7D",
                "chartDataType": "excluded",
            }
        },
    )
    spot_volume_7d: float | None = Field(
        default=None,
        description="The spot volume of the last seven days.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Spot Volume 7D",
                "chartDataType": "excluded",
            }
        },
    )
    futures_volume_30d: float | None = Field(
        default=None,
        description="The futures volume of the last thirty days.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Futures Volume 30D",
                "chartDataType": "excluded",
            }
        },
    )
    calls_volume_30d: float | None = Field(
        default=None,
        description="The call volume of the last thirty days.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Calls Volume 30D",
                "chartDataType": "excluded",
            }
        },
    )
    puts_volume_30d: float | None = Field(
        default=None,
        description="The put volume of the last thirty days.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Puts Volume 30D",
                "chartDataType": "excluded",
            }
        },
    )
    spot_volume_30d: float | None = Field(
        default=None,
        description="The spot volume of the last thirty days.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Spot Volume 30D",
                "chartDataType": "excluded",
            }
        },
    )


class DeribitTradeVolumesFetcher(
    Fetcher[DeribitTradeVolumesQueryParams, list[DeribitTradeVolumesData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitTradeVolumesQueryParams:
        """Transform the query."""
        return DeribitTradeVolumesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitTradeVolumesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If the exchange published no volumes.
        """
        from openbb_deribit.utils.client import request

        data = await request("get_trade_volumes", {"extended": query.extended})

        if not data:
            raise EmptyDataError("Deribit published no trade volumes.")

        return data

    @staticmethod
    def transform_data(
        query: DeribitTradeVolumesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitTradeVolumesData]:
        """Transform the data to the model.

        The busiest currencies come first. Most of the currencies the exchange
        lists trade nothing on a given day, and ordering them by name buries the
        handful that did under the ones that did not. Volumes are counted in
        each currency's own units, so the ranking is by activity rather than by
        value.
        """
        return [
            DeribitTradeVolumesData.model_validate(record)
            for record in sorted(
                data,
                key=lambda d: (-_traded(d), str(d.get("currency"))),
            )
        ]
