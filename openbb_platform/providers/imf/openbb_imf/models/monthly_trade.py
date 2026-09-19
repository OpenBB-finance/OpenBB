"""IMF Monthly TradeNow Model."""

from typing import Any, Literal

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field

api_prefix = SystemService().system_settings.api_settings.prefix


class ImfMonthlyTradeQueryParams(QueryParams):
    """IMF Monthly TradeNow Query Parameters."""

    __json_schema_extra__ = {
        "code": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/imf/portwatch/list_tradenow_region_choices",
                "style": {"popupWidth": 600},
            }
        },
        "metric": {
            "x-widget_config": {
                "type": "text",
                "options": [
                    {"label": "Trade Value Index (2019=100)", "value": "trade_value"},
                    {"label": "Trade Volume Index (2019=100)", "value": "trade_volume"},
                    {"label": "AIS Port Calls", "value": "portcalls"},
                ],
            }
        },
        "start_date": {"x-widget_config": {"type": "date"}},
        "end_date": {"x-widget_config": {"type": "date"}},
        "theme": {"x-widget_config": {"show": False}},
    }

    code: str = Field(
        default="USA",
        description="ISO3 country code or IMF region code (e.g. 'USA', 'ASEAN-5').",
        title="Country / Region",
    )
    metric: Literal["trade_value", "trade_volume", "portcalls"] = Field(
        default="trade_value",
        description="TradeNow metric: 'trade_value', 'trade_volume', or 'portcalls'.",
        title="Metric",
    )
    start_date: str | None = Field(
        default=None,
        description="ISO date (YYYY-MM-DD) lower bound for the monthly series.",
        title="Start Date",
    )
    end_date: str | None = Field(
        default=None,
        description="ISO date (YYYY-MM-DD) upper bound for the monthly series.",
        title="End Date",
    )
    theme: Literal["dark", "light"] | None = Field(
        default=None,
        description="Theme for the chart. Only used when ``chart=True``.",
        title="Theme",
    )


class ImfMonthlyTradeData(Data):
    """IMF Monthly TradeNow Data."""

    model_config = ConfigDict(
        extra="ignore",
        validate_by_alias=True,
        validate_by_name=True,
        populate_by_name=True,
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Monthly Trade (TradeNow)",
                "$.description": (
                    "Monthly TradeNow nowcasts of merchandise trade for a country or"
                    " IMF regional aggregate. Source: IMF Port Watch."
                ),
                "$.gridData": {"w": 40, "h": 14},
                "$.refetchInterval": False,
                "$.category": "IMF Utilities",
                "$.subCategory": "Port Watch",
                "$.source": ["UN Global Platform; IMF PortWatch"],
            }
        },
    )

    __alias_dict__ = {"country_code": "ISO3"}

    date: str = Field(description="Observation month (YYYY-MM-DD).", title="Date")
    country_code: str = Field(
        description="ISO3 country or IMF region code.", title="Country Code"
    )
    region: str | None = Field(
        default=None, description="IMF region label.", title="Region"
    )

    trade_value: float | None = Field(
        default=None,
        description="Trade value nowcast index (2019 = 100).",
        title="Trade Value Index",
    )
    trade_volume: float | None = Field(
        default=None,
        description="Trade volume nowcast index (2019 = 100).",
        title="Trade Volume Index",
    )
    value_import_total: float | None = Field(
        default=None,
        description="Imports component of the trade value index.",
        title="Value Imports",
    )
    value_export_total: float | None = Field(
        default=None,
        description="Exports component of the trade value index.",
        title="Value Exports",
    )
    volume_import_total: float | None = Field(
        default=None,
        description="Imports component of the trade volume index.",
        title="Volume Imports",
    )
    volume_export_total: float | None = Field(
        default=None,
        description="Exports component of the trade volume index.",
        title="Volume Exports",
    )

    ais_portcalls_container: int | None = Field(
        default=None,
        description="Monthly AIS port calls by container ships.",
        title="AIS Container Port Calls",
    )
    ais_portcalls_dry_bulk: int | None = Field(
        default=None,
        description="Monthly AIS port calls by dry-bulk carriers.",
        title="AIS Dry Bulk Port Calls",
    )
    ais_portcalls_general_cargo: int | None = Field(
        default=None,
        description="Monthly AIS port calls by general-cargo ships.",
        title="AIS General Cargo Port Calls",
    )
    ais_portcalls_roro: int | None = Field(
        default=None,
        description="Monthly AIS port calls by Ro-Ro ships.",
        title="AIS Ro-Ro Port Calls",
    )
    ais_portcalls_tanker: int | None = Field(
        default=None,
        description="Monthly AIS port calls by tankers.",
        title="AIS Tanker Port Calls",
    )

    ais_import_container: int | None = Field(
        default=None,
        description="Monthly AIS import volume by container ships.",
        title="AIS Container Imports",
    )
    ais_import_dry_bulk: int | None = Field(
        default=None,
        description="Monthly AIS import volume by dry-bulk carriers.",
        title="AIS Dry Bulk Imports",
    )
    ais_import_general_cargo: int | None = Field(
        default=None,
        description="Monthly AIS import volume by general-cargo ships.",
        title="AIS General Cargo Imports",
    )
    ais_import_roro: int | None = Field(
        default=None,
        description="Monthly AIS import volume by Ro-Ro ships.",
        title="AIS Ro-Ro Imports",
    )
    ais_import_tanker: int | None = Field(
        default=None,
        description="Monthly AIS import volume by tankers.",
        title="AIS Tanker Imports",
    )

    ais_export_container: int | None = Field(
        default=None,
        description="Monthly AIS export volume by container ships.",
        title="AIS Container Exports",
    )
    ais_export_dry_bulk: int | None = Field(
        default=None,
        description="Monthly AIS export volume by dry-bulk carriers.",
        title="AIS Dry Bulk Exports",
    )
    ais_export_general_cargo: int | None = Field(
        default=None,
        description="Monthly AIS export volume by general-cargo ships.",
        title="AIS General Cargo Exports",
    )
    ais_export_roro: int | None = Field(
        default=None,
        description="Monthly AIS export volume by Ro-Ro ships.",
        title="AIS Ro-Ro Exports",
    )
    ais_export_tanker: int | None = Field(
        default=None,
        description="Monthly AIS export volume by tankers.",
        title="AIS Tanker Exports",
    )


class ImfMonthlyTradeFetcher(
    Fetcher[ImfMonthlyTradeQueryParams, list[ImfMonthlyTradeData]]
):
    """IMF Monthly TradeNow Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ImfMonthlyTradeQueryParams:
        """Validate and coerce request params."""
        return ImfMonthlyTradeQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ImfMonthlyTradeQueryParams,
        credentials: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Fetch the monthly TradeNow rows for the requested country / region."""
        from openbb_imf.utils.port_watch_helpers import get_monthly_trade

        return await get_monthly_trade(query.code, query.start_date, query.end_date)

    @staticmethod
    def transform_data(
        query: ImfMonthlyTradeQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[ImfMonthlyTradeData]:
        """Coerce raw rows into ``ImfMonthlyTradeData`` instances."""
        return [ImfMonthlyTradeData.model_validate(row) for row in data]
