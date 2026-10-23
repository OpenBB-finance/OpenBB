"""IMF Container Metrics Model."""

from typing import Any, Literal

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field

api_prefix = SystemService().system_settings.api_settings.prefix

ContainerMetric = Literal[
    "portcalls",
    "import_container",
    "export_container",
    "incoming_cargo_container",
    "outgoing_cargo_container",
]


class ImfContainerMetricsQueryParams(QueryParams):
    """IMF Container Metrics Query Parameters."""

    __json_schema_extra__ = {
        "metric": {
            "x-widget_config": {
                "type": "text",
                "options": [
                    {"label": "Container Port Calls", "value": "portcalls"},
                    {"label": "Container Imports", "value": "import_container"},
                    {"label": "Container Exports", "value": "export_container"},
                    {
                        "label": "Incoming Container Cargo",
                        "value": "incoming_cargo_container",
                    },
                    {
                        "label": "Outgoing Container Cargo",
                        "value": "outgoing_cargo_container",
                    },
                ],
            }
        },
        "port_ids": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/imf/portwatch/list_container_port_choices",
                "multiSelect": True,
                "style": {"popupWidth": 350},
            },
        },
        "start_date": {"x-widget_config": {"type": "date"}},
        "end_date": {"x-widget_config": {"type": "date"}},
        "theme": {"x-widget_config": {"show": False}},
    }

    metric: ContainerMetric = Field(
        default="portcalls",
        description=(
            "Container metric to plot. Allowed: 'portcalls', 'import_container',"
            " 'export_container', 'incoming_cargo_container',"
            " 'outgoing_cargo_container'."
        ),
        title="Metric",
    )
    port_ids: str = Field(
        default="TOP10",
        description=(
            "Comma- or plus-separated port IDs to compare, or 'TOP10' to"
            " auto-select the busiest ports for the chosen metric."
        ),
        title="Port IDs",
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


class ImfContainerMetricsData(Data):
    """IMF Container Metrics Data (long format)."""

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Top Container Ports — Monthly Comparison",
                "$.description": (
                    "Monthly container metric at the world's largest container"
                    " ports. Source: IMF Port Watch."
                ),
                "$.gridData": {"w": 40, "h": 14},
                "$.refetchInterval": False,
                "$.category": "IMF Utilities",
                "$.subCategory": "Port Watch",
                "$.source": ["UN Global Platform; IMF PortWatch"],
            }
        },
    )

    metric: str = Field(description="Container metric name.", title="Metric")
    portid: str = Field(description="Port identifier (e.g. PORT23).", title="Port ID")
    date: str = Field(description="Observation month (YYYY-MM-DD).", title="Date")
    value: float | None = Field(
        default=None, description="Metric value.", title="Value"
    )


class ImfContainerMetricsFetcher(
    Fetcher[ImfContainerMetricsQueryParams, list[ImfContainerMetricsData]]
):
    """IMF Container Metrics Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ImfContainerMetricsQueryParams:
        """Validate and coerce request params."""
        return ImfContainerMetricsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ImfContainerMetricsQueryParams,
        credentials: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Fetch container-metric rows; resolves ``TOP10`` to the busiest ports."""
        from openbb_imf.utils.port_watch_helpers import get_container_metrics

        tokens = [
            p.strip().upper()
            for p in query.port_ids.replace("+", ",").split(",")
            if p.strip()
        ]
        use_top10 = not tokens or "TOP10" in tokens

        all_rows = await get_container_metrics(
            None, query.metric, query.start_date, query.end_date
        )
        if not use_top10:
            keep = set(tokens)
            return [r for r in all_rows if r.get("portid") in keep]

        totals: dict[str, float] = {}
        for r in all_rows:
            pid = r.get("portid")
            if not pid:
                continue
            totals[pid] = totals.get(pid, 0.0) + float(r.get("value") or 0)
        top10 = {
            pid
            for pid, _ in sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[
                :10
            ]
        }
        return [r for r in all_rows if r.get("portid") in top10]

    @staticmethod
    def transform_data(
        query: ImfContainerMetricsQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[ImfContainerMetricsData]:
        """Coerce raw rows into ``ImfContainerMetricsData`` instances."""
        return [ImfContainerMetricsData.model_validate(row) for row in data]
