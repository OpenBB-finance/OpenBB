"""Tests for the IMF port-watch Fetcher models."""

# ruff: noqa: I001

from unittest.mock import AsyncMock, patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_imf.models.container_metrics import (
    ImfContainerMetricsData,
    ImfContainerMetricsFetcher,
)
from openbb_imf.models.country_activity import (
    ImfCountryActivityData,
    ImfCountryActivityFetcher,
    ImfCountryActivityQueryParams,
)
from openbb_imf.models.disruption_events import (
    ImfDisruptionEventsData,
    ImfDisruptionEventsFetcher,
)
from openbb_imf.models.disruption_sankey import (
    ImfDisruptionSankeyData,
    ImfDisruptionSankeyFetcher,
)
from openbb_imf.models.monthly_trade import (
    ImfMonthlyTradeData,
    ImfMonthlyTradeFetcher,
)


class TestCountryActivityFetcher:
    """Tests for ``ImfCountryActivityFetcher``."""

    def test_transform_query_defaults(self):
        """Default params survive ``transform_query``."""
        q = ImfCountryActivityFetcher.transform_query({})
        assert isinstance(q, ImfCountryActivityQueryParams)
        assert q.country_code == "USA"
        assert q.metric == "portcalls"

    @pytest.mark.asyncio
    async def test_aextract_data_delegates_to_helper(self):
        """``aextract_data`` calls the shared helper with the right args."""
        with patch(
            "openbb_imf.utils.port_watch_helpers.get_country_daily_activity",
            new=AsyncMock(return_value=[{"date": "2024-01-01"}]),
        ) as mocked:
            q = ImfCountryActivityFetcher.transform_query(
                {
                    "country_code": "JPN",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                }
            )
            rows = await ImfCountryActivityFetcher.aextract_data(q, None)
        mocked.assert_awaited_once_with("JPN", "2024-01-01", "2024-01-31")
        assert rows == [{"date": "2024-01-01"}]

    def test_transform_data_builds_typed_rows(self):
        """``transform_data`` validates each row through the Data model and applies aliases."""
        q = ImfCountryActivityFetcher.transform_query({})
        out = ImfCountryActivityFetcher.transform_data(
            q,
            [
                {
                    "date": "2024-01-01",
                    "ISO3": "USA",
                    "portcalls": 5,
                    "import": 10,
                    "export": 7,
                }
            ],
        )
        assert isinstance(out[0], ImfCountryActivityData)
        assert out[0].country_code == "USA"
        assert out[0].imports == 10
        assert out[0].exports == 7

    def test_data_coerces_string_30ma_to_float(self):
        """The ``*_30MA`` strings the API returns get coerced to floats."""
        row = ImfCountryActivityData.model_validate(
            {
                "date": "2024-01-01",
                "ISO3": "USA",
                "export_container_30MA": "345609.36",
                "shipment_30MA_yoy_doy": "0.03",
            }
        )
        assert row.exports_container_30ma == pytest.approx(345609.36)
        assert row.shipment_30ma_yoy_doy == pytest.approx(0.03)


class TestMonthlyTradeFetcher:
    """Tests for ``ImfMonthlyTradeFetcher``."""

    def test_transform_query_defaults(self):
        """Default code and metric are populated."""
        q = ImfMonthlyTradeFetcher.transform_query({})
        assert q.code == "USA"
        assert q.metric == "trade_value"

    @pytest.mark.asyncio
    async def test_aextract_data(self):
        """The helper is invoked with the resolved query params."""
        with patch(
            "openbb_imf.utils.port_watch_helpers.get_monthly_trade",
            new=AsyncMock(return_value=[{"date": "2024-01-01"}]),
        ) as mocked:
            q = ImfMonthlyTradeFetcher.transform_query({"code": "JPN"})
            rows = await ImfMonthlyTradeFetcher.aextract_data(q, None)
        mocked.assert_awaited_once_with("JPN", None, None)
        assert rows == [{"date": "2024-01-01"}]

    def test_transform_data(self):
        """Rows are validated through the Data model with ISO3 alias."""
        q = ImfMonthlyTradeFetcher.transform_query({})
        out = ImfMonthlyTradeFetcher.transform_data(
            q,
            [
                {
                    "date": "2024-01-01",
                    "ISO3": "USA",
                    "region": "United States",
                    "trade_value": 105.6,
                    "ais_portcalls_container": 240,
                }
            ],
        )
        assert isinstance(out[0], ImfMonthlyTradeData)
        assert out[0].country_code == "USA"
        assert out[0].region == "United States"
        assert out[0].trade_value == pytest.approx(105.6)


class TestContainerMetricsFetcher:
    """Tests for ``ImfContainerMetricsFetcher`` including TOP10 ranking."""

    def test_transform_query_defaults(self):
        """Defaults match the widget config."""
        q = ImfContainerMetricsFetcher.transform_query({})
        assert q.metric == "portcalls"
        assert q.port_ids == "TOP10"

    @pytest.mark.asyncio
    async def test_aextract_top10_picks_busiest_ports(self):
        """The TOP10 path keeps the 10 ports with the largest ``value`` totals."""
        rows = []
        for i in range(20):
            for j in range(3):
                rows.append(
                    {
                        "metric": "portcalls",
                        "portid": f"PORT{i}",
                        "date": f"2024-0{j + 1}-01",
                        "value": (i + 1) * 10 + j,
                    }
                )
        with patch(
            "openbb_imf.utils.port_watch_helpers.get_container_metrics",
            new=AsyncMock(return_value=rows),
        ):
            q = ImfContainerMetricsFetcher.transform_query({})
            out = await ImfContainerMetricsFetcher.aextract_data(q, None)
        kept = {r["portid"] for r in out}
        assert len(kept) == 10
        assert kept == {f"PORT{i}" for i in range(10, 20)}

    @pytest.mark.asyncio
    async def test_aextract_explicit_port_filter(self):
        """Explicit port ids filter directly without invoking the TOP10 ranking."""
        rows = [
            {"metric": "portcalls", "portid": "PORT1", "date": "2024-01", "value": 1},
            {"metric": "portcalls", "portid": "PORT2", "date": "2024-01", "value": 2},
        ]
        with patch(
            "openbb_imf.utils.port_watch_helpers.get_container_metrics",
            new=AsyncMock(return_value=rows),
        ):
            q = ImfContainerMetricsFetcher.transform_query({"port_ids": "PORT2+PORT99"})
            out = await ImfContainerMetricsFetcher.aextract_data(q, None)
        assert [r["portid"] for r in out] == ["PORT2"]

    @pytest.mark.asyncio
    async def test_aextract_top10_handles_missing_values(self):
        """Rows without a ``portid`` or numeric ``value`` are skipped during ranking."""
        rows = [
            {"metric": "portcalls", "portid": "PORT1", "date": "2024-01", "value": 5},
            {"metric": "portcalls", "portid": None, "date": "2024-01", "value": 99},
            {
                "metric": "portcalls",
                "portid": "PORT2",
                "date": "2024-01",
                "value": None,
            },
        ]
        with patch(
            "openbb_imf.utils.port_watch_helpers.get_container_metrics",
            new=AsyncMock(return_value=rows),
        ):
            q = ImfContainerMetricsFetcher.transform_query({})
            out = await ImfContainerMetricsFetcher.aextract_data(q, None)
        assert {r["portid"] for r in out} == {"PORT1", "PORT2"}

    def test_transform_data(self):
        """Rows survive the typed Data validation."""
        q = ImfContainerMetricsFetcher.transform_query({})
        out = ImfContainerMetricsFetcher.transform_data(
            q,
            [
                {
                    "metric": "portcalls",
                    "portid": "PORT1",
                    "date": "2024-01-01",
                    "value": 42,
                }
            ],
        )
        assert isinstance(out[0], ImfContainerMetricsData)
        assert out[0].value == 42


class TestDisruptionEventsFetcher:
    """Tests for ``ImfDisruptionEventsFetcher``."""

    def test_transform_query_defaults(self):
        """The default alert level is ``ALL`` and active-only is False."""
        q = ImfDisruptionEventsFetcher.transform_query({})
        assert q.alertlevel == "ALL"
        assert q.active_only is False

    @pytest.mark.asyncio
    async def test_aextract_data_converts_all_to_none(self):
        """An ``ALL`` alert level translates to ``None`` in the helper call."""
        with patch(
            "openbb_imf.utils.port_watch_helpers.get_disruption_events",
            new=AsyncMock(return_value=[]),
        ) as mocked:
            q = ImfDisruptionEventsFetcher.transform_query(
                {"country": "JPN", "alertlevel": "ALL"}
            )
            await ImfDisruptionEventsFetcher.aextract_data(q, None)
        mocked.assert_awaited_once_with("JPN", None, None, False, None, None)

    @pytest.mark.asyncio
    async def test_aextract_data_passes_specific_alert_level(self):
        """A specific alert level flows through to the helper unchanged."""
        with patch(
            "openbb_imf.utils.port_watch_helpers.get_disruption_events",
            new=AsyncMock(return_value=[]),
        ) as mocked:
            q = ImfDisruptionEventsFetcher.transform_query({"alertlevel": "RED"})
            await ImfDisruptionEventsFetcher.aextract_data(q, None)
        assert mocked.call_args.args[2] == "RED"

    def test_transform_data_aliases(self):
        """ArcGIS field names are mapped to snake_case via ``__alias_dict__``."""
        q = ImfDisruptionEventsFetcher.transform_query({})
        out = ImfDisruptionEventsFetcher.transform_data(
            q,
            [
                {
                    "eventid": 1,
                    "eventname": "Storm",
                    "alertlevel": "RED",
                    "lat": 12.5,
                    "long": -45.0,
                    "ObjectId": 7,
                    "htmlname": "<b>Storm</b>",
                    "pageid": "abc",
                }
            ],
        )
        row = out[0]
        assert isinstance(row, ImfDisruptionEventsData)
        assert row.latitude == 12.5
        assert row.longitude == -45.0
        assert row.object_id == 7
        assert row.html_name == "<b>Storm</b>"
        assert row.page_id == "abc"


class TestDisruptionSankeyFetcher:
    """Tests for ``ImfDisruptionSankeyFetcher``."""

    def test_transform_query_default_latest(self):
        """The default event id is ``LATEST``."""
        q = ImfDisruptionSankeyFetcher.transform_query({})
        assert q.event_id == "LATEST"

    @pytest.mark.asyncio
    async def test_aextract_latest_resolves_to_top_event(self):
        """``LATEST`` resolves to the first event returned by the disruptions helper."""
        with (
            patch(
                "openbb_imf.utils.port_watch_helpers.get_disruption_events",
                new=AsyncMock(return_value=[{"eventid": 42, "eventname": "Hurricane"}]),
            ),
            patch(
                "openbb_imf.utils.port_watch_helpers.get_disruption_sankey_edges",
                new=AsyncMock(return_value=[{"source": 1, "target": 2}]),
            ) as edges_mock,
        ):
            q = ImfDisruptionSankeyFetcher.transform_query({"event_id": "LATEST"})
            rows = await ImfDisruptionSankeyFetcher.aextract_data(q, None)
        edges_mock.assert_awaited_once_with(42)
        assert q._event_label == "Hurricane"
        assert rows == [{"source": 1, "target": 2}]

    @pytest.mark.asyncio
    async def test_aextract_explicit_event_id(self):
        """An explicit numeric event id is passed straight through."""
        with patch(
            "openbb_imf.utils.port_watch_helpers.get_disruption_sankey_edges",
            new=AsyncMock(return_value=[]),
        ) as edges_mock:
            q = ImfDisruptionSankeyFetcher.transform_query({"event_id": "100"})
            await ImfDisruptionSankeyFetcher.aextract_data(q, None)
        edges_mock.assert_awaited_once_with(100)
        assert q._event_label == "Event 100"

    @pytest.mark.asyncio
    async def test_aextract_latest_raises_when_no_events(self):
        """If there are no disruption events to choose from, raise ``OpenBBError``."""
        with patch(
            "openbb_imf.utils.port_watch_helpers.get_disruption_events",
            new=AsyncMock(return_value=[]),
        ):
            q = ImfDisruptionSankeyFetcher.transform_query({})
            with pytest.raises(OpenBBError):
                await ImfDisruptionSankeyFetcher.aextract_data(q, None)

    def test_transform_data_aliases_from_and_to(self):
        """The ArcGIS ``from_``/``to_`` keys are remapped to source/target ports."""
        q = ImfDisruptionSankeyFetcher.transform_query({})
        out = ImfDisruptionSankeyFetcher.transform_data(
            q,
            [
                {
                    "eventid": 1,
                    "source": 0,
                    "target": 1,
                    "from_": "Colombo",
                    "to_": "Chittagong",
                    "from_id": "port254",
                    "to_id": "port241",
                    "from_iso3": "LKA",
                    "to_iso3": "BGD",
                    "perc_disaster_capacity": 14.9,
                    "ObjectId": 1,
                }
            ],
        )
        edge = out[0]
        assert isinstance(edge, ImfDisruptionSankeyData)
        assert edge.source_port == "Colombo"
        assert edge.target_port == "Chittagong"
        assert edge.source_port_id == "port254"
        assert edge.target_country_code == "BGD"
        assert edge.perc_disaster_capacity == pytest.approx(14.9)
        assert edge.object_id == 1
