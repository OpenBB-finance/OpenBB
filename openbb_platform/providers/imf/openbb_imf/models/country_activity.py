"""IMF Country Maritime Activity Model."""

from typing import Any, Literal

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field

api_prefix = SystemService().system_settings.api_settings.prefix


class ImfCountryActivityQueryParams(QueryParams):
    """IMF Country Maritime Activity Query Parameters."""

    __json_schema_extra__ = {
        "country_code": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/imf/portwatch/list_country_choices",
                "style": {"popupWidth": 350},
            }
        },
        "metric": {
            "x-widget_config": {
                "type": "text",
                "options": [
                    {"label": "Port Calls", "value": "portcalls"},
                    {"label": "Imports (mt)", "value": "import"},
                    {"label": "Exports (mt)", "value": "export"},
                ],
            }
        },
        "start_date": {"x-widget_config": {"type": "date"}},
        "end_date": {"x-widget_config": {"type": "date"}},
        "theme": {"x-widget_config": {"show": False}},
    }

    country_code: str = Field(
        default="USA",
        description="ISO3 country code to fetch daily activity for.",
        title="Country",
    )
    metric: Literal["portcalls", "import", "export"] = Field(
        default="portcalls",
        description="Activity metric to chart: 'portcalls', 'import', or 'export'.",
        title="Metric",
    )
    start_date: str | None = Field(
        default=None,
        description="ISO date (YYYY-MM-DD) lower bound for the activity window.",
        title="Start Date",
    )
    end_date: str | None = Field(
        default=None,
        description="ISO date (YYYY-MM-DD) upper bound for the activity window.",
        title="End Date",
    )
    theme: Literal["dark", "light"] | None = Field(
        default=None,
        description="Theme for the chart. Only used when ``chart=True``.",
        title="Theme",
    )


class ImfCountryActivityData(Data):
    """IMF Country Maritime Activity Data."""

    model_config = ConfigDict(
        extra="ignore",
        validate_by_alias=True,
        validate_by_name=True,
        populate_by_name=True,
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Daily Country Trade Activity",
                "$.description": (
                    "Daily country-level port calls, import volumes, and export"
                    " volumes from IMF Port Watch's Daily Trade Data (REG)."
                ),
                "$.gridData": {"w": 40, "h": 14},
                "$.refetchInterval": False,
                "$.category": "IMF Utilities",
                "$.subCategory": "Port Watch",
                "$.source": ["UN Global Platform; IMF PortWatch"],
            }
        },
    )

    __alias_dict__ = {
        "country_code": "ISO3",
        "imports": "import",
        "imports_cargo": "import_cargo",
        "imports_container": "import_container",
        "imports_container_30ma": "import_container_30MA",
        "imports_container_30ma_yoy_doy": "import_container_30MA_yoy_doy",
        "imports_dry_bulk": "import_dry_bulk",
        "imports_general_cargo": "import_general_cargo",
        "imports_roro": "import_roro",
        "imports_tanker": "import_tanker",
        "exports": "export",
        "exports_cargo": "export_cargo",
        "exports_container": "export_container",
        "exports_container_30ma": "export_container_30MA",
        "exports_container_30ma_yoy_doy": "export_container_30MA_yoy_doy",
        "exports_dry_bulk": "export_dry_bulk",
        "exports_general_cargo": "export_general_cargo",
        "exports_roro": "export_roro",
        "exports_tanker": "export_tanker",
        "portcalls_container_30ma": "portcalls_container_30MA",
        "portcalls_container_30ma_yoy_doy": "portcalls_container_30MA_yoy_doy",
        "shipment_30ma": "shipment_30MA",
        "shipment_30ma_yoy_doy": "shipment_30MA_yoy_doy",
    }

    date: str = Field(description="Observation date (YYYY-MM-DD).", title="Date")
    country_code: str = Field(description="ISO3 country code.", title="Country Code")
    country: str | None = Field(
        default=None, description="Country display name.", title="Country"
    )

    portcalls: int | None = Field(
        default=None,
        description="Total ships calling at the country's ports on this date.",
        title="Port Calls",
    )
    portcalls_cargo: int | None = Field(
        default=None,
        description="Total cargo ships (excluding tankers) calling on this date.",
        title="Cargo Port Calls",
    )
    portcalls_container: int | None = Field(
        default=None,
        description="Container-ship port calls on this date.",
        title="Container Port Calls",
    )
    portcalls_dry_bulk: int | None = Field(
        default=None,
        description="Dry-bulk-carrier port calls on this date.",
        title="Dry Bulk Port Calls",
    )
    portcalls_general_cargo: int | None = Field(
        default=None,
        description="General-cargo-ship port calls on this date.",
        title="General Cargo Port Calls",
    )
    portcalls_roro: int | None = Field(
        default=None,
        description="Ro-Ro-ship port calls on this date.",
        title="Ro-Ro Port Calls",
    )
    portcalls_tanker: int | None = Field(
        default=None,
        description="Tanker port calls on this date.",
        title="Tanker Port Calls",
    )
    portcalls_container_30ma: float | None = Field(
        default=None,
        description="30-day moving average of container port calls.",
        title="Container Port Calls (30d MA)",
    )
    portcalls_container_30ma_yoy_doy: float | None = Field(
        default=None,
        description=(
            "Year-over-year change in the 30-day MA of container port calls,"
            " keyed on day of year."
        ),
        title="Container Port Calls (30d MA YoY)",
    )

    imports: int | None = Field(
        default=None,
        description="Total import volume (mt) of all ships entering on this date.",
        title="Imports",
    )
    imports_cargo: int | None = Field(
        default=None,
        description="Total import volume (mt) of cargo ships (excluding tankers).",
        title="Cargo Imports",
    )
    imports_container: int | None = Field(
        default=None,
        description="Total import volume (mt) of container ships on this date.",
        title="Container Imports",
    )
    imports_dry_bulk: int | None = Field(
        default=None,
        description="Total import volume (mt) of dry-bulk carriers on this date.",
        title="Dry Bulk Imports",
    )
    imports_general_cargo: int | None = Field(
        default=None,
        description="Total import volume (mt) of general-cargo ships on this date.",
        title="General Cargo Imports",
    )
    imports_roro: int | None = Field(
        default=None,
        description="Total import volume (mt) of Ro-Ro ships on this date.",
        title="Ro-Ro Imports",
    )
    imports_tanker: int | None = Field(
        default=None,
        description="Total import volume (mt) of tankers on this date.",
        title="Tanker Imports",
    )
    imports_container_30ma: float | None = Field(
        default=None,
        description="30-day moving average of container import volume.",
        title="Container Imports (30d MA)",
    )
    imports_container_30ma_yoy_doy: float | None = Field(
        default=None,
        description=(
            "Year-over-year change in the 30-day MA of container import volume,"
            " keyed on day of year."
        ),
        title="Container Imports (30d MA YoY)",
    )

    exports: int | None = Field(
        default=None,
        description="Total export volume (mt) of all ships departing on this date.",
        title="Exports",
    )
    exports_cargo: int | None = Field(
        default=None,
        description="Total export volume (mt) of cargo ships (excluding tankers).",
        title="Cargo Exports",
    )
    exports_container: int | None = Field(
        default=None,
        description="Total export volume (mt) of container ships on this date.",
        title="Container Exports",
    )
    exports_dry_bulk: int | None = Field(
        default=None,
        description="Total export volume (mt) of dry-bulk carriers on this date.",
        title="Dry Bulk Exports",
    )
    exports_general_cargo: int | None = Field(
        default=None,
        description="Total export volume (mt) of general-cargo ships on this date.",
        title="General Cargo Exports",
    )
    exports_roro: int | None = Field(
        default=None,
        description="Total export volume (mt) of Ro-Ro ships on this date.",
        title="Ro-Ro Exports",
    )
    exports_tanker: int | None = Field(
        default=None,
        description="Total export volume (mt) of tankers on this date.",
        title="Tanker Exports",
    )
    exports_container_30ma: float | None = Field(
        default=None,
        description="30-day moving average of container export volume.",
        title="Container Exports (30d MA)",
    )
    exports_container_30ma_yoy_doy: float | None = Field(
        default=None,
        description=(
            "Year-over-year change in the 30-day MA of container export volume,"
            " keyed on day of year."
        ),
        title="Container Exports (30d MA YoY)",
    )

    shipment: int | None = Field(
        default=None,
        description="Total shipment volume (mt) crossing the country on this date.",
        title="Shipment",
    )
    shipment_30ma: float | None = Field(
        default=None,
        description="30-day moving average of total shipment volume.",
        title="Shipment (30d MA)",
    )
    shipment_30ma_yoy_doy: float | None = Field(
        default=None,
        description=(
            "Year-over-year change in the 30-day MA of total shipment volume,"
            " keyed on day of year."
        ),
        title="Shipment (30d MA YoY)",
    )


class ImfCountryActivityFetcher(
    Fetcher[ImfCountryActivityQueryParams, list[ImfCountryActivityData]]
):
    """IMF Country Maritime Activity Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ImfCountryActivityQueryParams:
        """Validate and coerce request params."""
        return ImfCountryActivityQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ImfCountryActivityQueryParams,
        credentials: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Fetch the daily activity rows for the requested country."""
        from openbb_imf.utils.port_watch_helpers import get_country_daily_activity

        return await get_country_daily_activity(
            query.country_code, query.start_date, query.end_date
        )

    @staticmethod
    def transform_data(
        query: ImfCountryActivityQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[ImfCountryActivityData]:
        """Coerce raw rows into ``ImfCountryActivityData`` instances."""
        return [ImfCountryActivityData.model_validate(row) for row in data]
