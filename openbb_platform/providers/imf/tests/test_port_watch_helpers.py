"""Tests for the port-watch FS helpers."""

# ruff: noqa: I001

from unittest.mock import AsyncMock, patch

import pytest

from openbb_imf.utils.port_watch_helpers import (
    _arcgis_query,
    _date_where_clause,
    _epoch_to_iso_date,
    _normalize_ymd,
    get_container_metrics,
    get_container_port_choices,
    get_country_daily_activity,
    get_disruption_events,
    get_disruption_sankey_edges,
    get_monthly_trade,
    get_sankey_event_choices,
    get_tradenow_region_choices,
)


class _FakeResponse:
    """Mimic ``aiohttp`` response context manager for tests."""

    def __init__(self, payload: dict, status: int = 200):
        self.status = status
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def json(self):
        return self._payload


class _FakeSession:
    """Fake aiohttp session yielding pre-baked responses keyed by call order."""

    def __init__(self, responses: list[dict]):
        self._responses = list(responses)
        self.urls: list[str] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def get(self, url: str):
        self.urls.append(url)
        payload = self._responses.pop(0) if self._responses else {"features": []}
        return _AwaitableContext(_FakeResponse(payload))


class _AwaitableContext:
    """Wrap a context manager so ``await session.get(url)`` works in our async helper."""

    def __init__(self, ctx):
        self._ctx = ctx

    def __await__(self):
        async def _do():
            return self._ctx

        return _do().__await__()


def _patch_session(*payloads: dict):
    """Return a context manager that swaps in a fake aiohttp session."""
    fake = _FakeSession(list(payloads))

    class _Factory:
        async def __aenter__(self_):
            return fake

        async def __aexit__(self_, *args):
            return False

    async def _factory(*args, **kwargs):
        return _Factory()

    return patch(
        "openbb_core.provider.utils.helpers.get_async_requests_session",
        side_effect=_factory,
    ), fake


class TestArcgisQuery:
    """Tests for the generic ``_arcgis_query`` paginator."""

    @pytest.mark.asyncio
    async def test_single_page(self):
        """Single-page response returns attribute dicts."""
        patcher, fake = _patch_session(
            {
                "features": [
                    {"attributes": {"a": 1, "b": 2}},
                    {"attributes": {"a": 3, "b": 4}},
                ]
            }
        )
        with patcher:
            rows = await _arcgis_query("https://x/", where="a > 0")
        assert rows == [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        assert "where=a%20%3E%200" in fake.urls[0]

    @pytest.mark.asyncio
    async def test_paginates_on_exceeded_transfer_limit(self):
        """Follows ``exceededTransferLimit`` until the server stops paging."""
        patcher, fake = _patch_session(
            {
                "features": [{"attributes": {"i": 1}}],
                "exceededTransferLimit": True,
            },
            {"features": [{"attributes": {"i": 2}}]},
        )
        with patcher:
            rows = await _arcgis_query("https://x/", where="1=1", page_size=1)
        assert [r["i"] for r in rows] == [1, 2]
        assert "resultOffset=0" in fake.urls[0]
        assert "resultOffset=1" in fake.urls[1]

    @pytest.mark.asyncio
    async def test_order_by_and_extra_params_appended(self):
        """``order_by`` and ``extra_params`` end up in the query string."""
        patcher, fake = _patch_session({"features": []})
        with patcher:
            await _arcgis_query(
                "https://x/",
                where="1=1",
                order_by="date DESC",
                extra_params="&returnDistinctValues=true",
            )
        url = fake.urls[0]
        assert "orderByFields=date%20DESC" in url
        assert "&returnDistinctValues=true" in url

    @pytest.mark.asyncio
    async def test_non_200_raises_openbb_error(self):
        """A non-200 status surfaces as ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError

        bad_response = _FakeResponse({}, status=500)
        fake = _FakeSession([])
        fake.get = lambda url: _AwaitableContext(bad_response)  # type: ignore

        class _Factory:
            async def __aenter__(self_):
                return fake

            async def __aexit__(self_, *args):
                return False

        async def _factory(*args, **kwargs):
            return _Factory()

        with patch(
            "openbb_core.provider.utils.helpers.get_async_requests_session",
            side_effect=_factory,
        ):
            with pytest.raises(OpenBBError):
                await _arcgis_query("https://x/", where="1=1")

    @pytest.mark.asyncio
    async def test_empty_features_terminates_pagination(self):
        """An empty ``features`` array stops the loop even with the limit flag."""
        patcher, _ = _patch_session({"features": [], "exceededTransferLimit": True})
        with patcher:
            rows = await _arcgis_query("https://x/", where="1=1")
        assert rows == []

    @pytest.mark.asyncio
    async def test_attributes_missing_or_empty_are_skipped(self):
        """Features without ``attributes`` (or with empty ones) are dropped."""
        patcher, _ = _patch_session(
            {
                "features": [
                    {"attributes": {"a": 1}},
                    {},
                    {"attributes": {}},
                ]
            }
        )
        with patcher:
            rows = await _arcgis_query("https://x/", where="1=1")
        assert rows == [{"a": 1}]


class TestEpochToIsoDate:
    """Tests for ``_epoch_to_iso_date``."""

    def test_none_returns_none(self):
        """``None`` passes through."""
        assert _epoch_to_iso_date(None) is None

    def test_string_input_trims_to_date(self):
        """String inputs are truncated to the first 10 chars."""
        assert _epoch_to_iso_date("2024-05-01T12:34:56Z") == "2024-05-01"

    def test_epoch_millis_returns_iso(self):
        """A millisecond epoch integer is rendered as YYYY-MM-DD."""
        millis = 1_704_067_200_000
        assert _epoch_to_iso_date(millis) == "2024-01-01"

    def test_small_int_passes_through_as_str(self):
        """A small integer (clearly not an epoch) is returned as ``str``."""
        assert _epoch_to_iso_date(42) == "42"


class TestNormalizeYmd:
    """Tests for ``_normalize_ymd``."""

    def test_ymd_triple_collapses_to_date(self):
        """``year``/``month``/``day`` get rewritten to ``date`` and removed."""
        row = {"year": 2024, "month": 5, "day": 9, "value": 12}
        out = _normalize_ymd(row)
        assert out == {"date": "2024-05-09", "value": 12}

    def test_invalid_ymd_is_silently_ignored(self):
        """Bad ymd values leave ``date`` unset but still drop the triple."""
        out = _normalize_ymd({"year": "not-a-year", "month": 5, "day": 1, "v": 1})
        assert "date" not in out
        assert out == {"v": 1}

    def test_internal_arcgis_fields_dropped(self):
        """``ObjectId`` and ``GlobalID`` are stripped from the output."""
        out = _normalize_ymd({"ObjectId": 7, "GlobalID": "g", "x": 1})
        assert out == {"x": 1}


class TestDateWhereClause:
    """Tests for ``_date_where_clause``."""

    def test_no_dates_returns_one_eq_one(self):
        """With neither bound supplied, the helper returns the SQL-true filter."""
        assert _date_where_clause("date", None, None) == "1=1"

    def test_start_only(self):
        """Lower bound produces a ``>=`` clause."""
        assert _date_where_clause("date", "2024-01-01", None) == (
            "date >= TIMESTAMP '2024-01-01 00:00:00'"
        )

    def test_end_only(self):
        """Upper bound produces a ``<=`` clause."""
        assert _date_where_clause("date", None, "2024-12-31") == (
            "date <= TIMESTAMP '2024-12-31 23:59:59'"
        )

    def test_both_bounds_joined_with_and(self):
        """Both bounds get joined with ``AND``."""
        clause = _date_where_clause("date", "2024-01-01", "2024-12-31")
        assert "AND" in clause
        assert ">=" in clause
        assert "<=" in clause


class TestFetchHelpers:
    """Tests for the dataset-specific fetcher helpers."""

    @pytest.mark.asyncio
    async def test_country_daily_activity(self):
        """``get_country_daily_activity`` builds the right WHERE and normalises rows."""
        get_country_daily_activity.cache_clear()
        with patch(
            "openbb_imf.utils.port_watch_helpers._arcgis_query",
            new=AsyncMock(
                return_value=[{"year": 2024, "month": 1, "day": 1, "portcalls": 5}]
            ),
        ) as mocked:
            rows = await get_country_daily_activity("usa", "2024-01-01", "2024-01-31")
        called_where = mocked.call_args.kwargs["where"]
        assert "ISO3 = 'USA'" in called_where
        assert "TIMESTAMP '2024-01-01" in called_where
        assert rows == [{"date": "2024-01-01", "portcalls": 5}]

    @pytest.mark.asyncio
    async def test_monthly_trade(self):
        """``get_monthly_trade`` normalises the date column from an epoch."""
        get_monthly_trade.cache_clear()
        with patch(
            "openbb_imf.utils.port_watch_helpers._arcgis_query",
            new=AsyncMock(
                return_value=[{"date": 1_704_067_200_000, "trade_value": 100.0}]
            ),
        ):
            rows = await get_monthly_trade("USA", None, None)
        assert rows == [{"date": "2024-01-01", "trade_value": 100.0}]

    @pytest.mark.asyncio
    async def test_container_metrics_melts_wide_rows(self):
        """Wide container-metric rows are melted to long format and filtered."""
        get_container_metrics.cache_clear()
        wide_rows = [
            {
                "metric": "portcalls",
                "date_in": 1_704_067_200_000,
                "port23": 50,
                "port99": 12,
                "ObjectId": 1,
            }
        ]
        with patch(
            "openbb_imf.utils.port_watch_helpers._arcgis_query",
            new=AsyncMock(return_value=wide_rows),
        ):
            rows = await get_container_metrics(("PORT23",), "portcalls", None, None)
        assert rows == [
            {
                "metric": "portcalls",
                "portid": "PORT23",
                "date": "2024-01-01",
                "value": 50,
            }
        ]

    @pytest.mark.asyncio
    async def test_container_metrics_no_filter_emits_all_ports(self):
        """With ``port_ids=None`` every port column is emitted."""
        get_container_metrics.cache_clear()
        wide_rows = [{"metric": "portcalls", "date_in": 0, "port1": 1, "port2": 2}]
        with patch(
            "openbb_imf.utils.port_watch_helpers._arcgis_query",
            new=AsyncMock(return_value=wide_rows),
        ):
            rows = await get_container_metrics(None, "portcalls", None, None)
        ids = sorted(r["portid"] for r in rows)
        assert ids == ["PORT1", "PORT2"]

    @pytest.mark.asyncio
    async def test_disruption_events_filters_and_normalises_dates(self):
        """``get_disruption_events`` composes filters and rewrites date fields."""
        get_disruption_events.cache_clear()
        with patch(
            "openbb_imf.utils.port_watch_helpers._arcgis_query",
            new=AsyncMock(
                return_value=[
                    {
                        "eventid": 1,
                        "fromdate": 1_704_067_200_000,
                        "todate": None,
                        "editdate": 1_704_067_200_000,
                    }
                ]
            ),
        ) as mocked:
            rows = await get_disruption_events(
                "usa", "Storm", "red", True, "2024-01-01", None
            )
        where = mocked.call_args.kwargs["where"]
        assert "country = 'USA'" in where
        assert "eventtype = 'Storm'" in where
        assert "alertlevel = 'RED'" in where
        assert "todate IS NULL" in where
        assert "fromdate >= TIMESTAMP" in where
        assert rows[0]["fromdate"] == "2024-01-01"
        assert rows[0]["todate"] is None
        assert rows[0]["editdate"] == "2024-01-01"

    @pytest.mark.asyncio
    async def test_disruption_events_defaults_to_one_eq_one(self):
        """With no filters at all the WHERE clause is ``1=1``."""
        get_disruption_events.cache_clear()
        with patch(
            "openbb_imf.utils.port_watch_helpers._arcgis_query",
            new=AsyncMock(return_value=[]),
        ) as mocked:
            await get_disruption_events()
        assert mocked.call_args.kwargs["where"] == "1=1"

    @pytest.mark.asyncio
    async def test_disruption_sankey(self):
        """``get_disruption_sankey_edges`` passes the integer event id."""
        get_disruption_sankey_edges.cache_clear()
        with patch(
            "openbb_imf.utils.port_watch_helpers._arcgis_query",
            new=AsyncMock(return_value=[{"source": 1, "target": 2}]),
        ) as mocked:
            rows = await get_disruption_sankey_edges(42)
        assert mocked.call_args.kwargs["where"] == "eventid = 42"
        assert rows == [{"source": 1, "target": 2}]

    @pytest.mark.asyncio
    async def test_tradenow_region_choices_dedupes_and_sorts(self):
        """Distinct ISO3+region tuples become sorted ``[{label, value}]`` entries."""
        with patch(
            "openbb_imf.utils.port_watch_helpers._arcgis_query",
            new=AsyncMock(
                return_value=[
                    {"ISO3": "USA", "region": "United States"},
                    {"ISO3": "USA", "region": "United States"},
                    {"ISO3": "JPN", "region": "Japan"},
                    {"ISO3": None, "region": "Nowhere"},
                ]
            ),
        ):
            choices = await get_tradenow_region_choices()
        assert choices == [
            {"label": "Japan", "value": "JPN"},
            {"label": "United States", "value": "USA"},
        ]

    @pytest.mark.asyncio
    async def test_container_port_choices(self):
        """Port columns from a sample row become friendly-named choices."""
        from openbb_imf.utils import port_watch_helpers as pwh

        async def _name_map() -> dict[str, str]:
            return {"PORT1": "Singapore, Singapore", "PORT23": "Rotterdam"}

        with (
            patch(
                "openbb_imf.utils.port_watch_helpers._arcgis_query",
                new=AsyncMock(
                    return_value=[
                        {
                            "metric": "portcalls",
                            "date": 0,
                            "port23": 5,
                            "port1": 1,
                            "ObjectId": 1,
                        }
                    ]
                ),
            ),
            patch.object(pwh, "get_container_port_name_map", _name_map),
        ):
            choices = await get_container_port_choices()
        assert choices == [
            {"label": "Singapore, Singapore", "value": "PORT1"},
            {"label": "Rotterdam", "value": "PORT23"},
        ]

    @pytest.mark.asyncio
    async def test_container_port_choices_empty_rows(self):
        """An empty response returns no choices."""
        with patch(
            "openbb_imf.utils.port_watch_helpers._arcgis_query",
            new=AsyncMock(return_value=[]),
        ):
            assert await get_container_port_choices() == []

    @pytest.mark.asyncio
    async def test_container_port_name_map(self):
        """``list_ports`` rows are folded into ``{portid: fullname or portname}``."""
        from openbb_imf.utils import port_watch_helpers as pwh

        async def _ports() -> list[dict]:
            return [
                {"portid": "port1", "portname": "Busan", "fullname": "Busan, Korea"},
                {"portid": "PORT2", "portname": "Hamburg", "fullname": ""},
                {"portname": "Skipped — no portid"},
            ]

        with patch.object(pwh, "list_ports", _ports):
            out = await pwh.get_container_port_name_map()
        assert out == {"PORT1": "Busan, Korea", "PORT2": "Hamburg"}

    @pytest.mark.asyncio
    async def test_sankey_event_choices(self):
        """Event rows with date and name get a ``Name (date)`` label."""
        with patch(
            "openbb_imf.utils.port_watch_helpers._arcgis_query",
            new=AsyncMock(
                return_value=[
                    {
                        "eventid": 1,
                        "eventname": "Suez Block",
                        "fromdate": 1_704_067_200_000,
                    },
                    {"eventid": 2, "eventname": None, "fromdate": None},
                    {"eventid": None, "eventname": "junk"},
                ]
            ),
        ):
            choices = await get_sankey_event_choices()
        assert choices == [
            {"label": "Suez Block (2024-01-01)", "value": "1"},
            {"label": "event 2", "value": "2"},
        ]


_PORTS_FIXTURE = [
    {
        "portid": "PORT1",
        "portname": "Port One",
        "ISO3": "USA",
        "countrynoaccents": "United States",
    },
    {
        "portid": "PORT2",
        "portname": "Port Two",
        "ISO3": "USA",
        "countrynoaccents": "United States",
    },
    {
        "portid": "PORT3",
        "portname": "Port Three",
        "ISO3": "CAN",
        "countrynoaccents": "Canada",
    },
]


class TestListCountries:
    """Tests for ``list_countries``."""

    def test_dedupes_by_iso3(self):
        """Each ISO3 is emitted exactly once with its country name."""
        from openbb_imf.utils import port_watch_helpers as pwh

        with patch.object(pwh, "get_ports", return_value=_PORTS_FIXTURE):
            choices = pwh.list_countries()
        assert choices == [
            {"label": "United States", "value": "USA"},
            {"label": "Canada", "value": "CAN"},
        ]


class TestMapPortCountryCode:
    """Tests for ``map_port_country_code``."""

    def test_maps_known_code(self):
        """A known code resolves to the country name (lowercase coerced)."""
        from openbb_imf.utils import port_watch_helpers as pwh

        with patch.object(pwh, "get_ports", return_value=_PORTS_FIXTURE):
            assert pwh.map_port_country_code("usa") == "United States"

    def test_unknown_code_raises(self):
        """An unknown ISO3 raises ``ValueError``."""
        from openbb_imf.utils import port_watch_helpers as pwh

        with patch.object(pwh, "get_ports", return_value=_PORTS_FIXTURE):
            with pytest.raises(ValueError):
                pwh.map_port_country_code("ZZZ")


class TestGetPortIdsByCountry:
    """Tests for ``get_port_ids_by_country``."""

    def test_filters_by_country_code(self):
        """Only ports for the requested country are returned, comma-joined."""
        from openbb_imf.utils import port_watch_helpers as pwh

        with patch.object(pwh, "get_ports", return_value=_PORTS_FIXTURE):
            assert pwh.get_port_ids_by_country("usa") == "PORT1,PORT2"
            assert pwh.get_port_ids_by_country("CAN") == "PORT3"
            assert pwh.get_port_ids_by_country("ZZZ") == ""


class TestGetPortIdChoices:
    """Tests for ``get_port_id_choices``."""

    def test_label_value_pairs(self):
        """Every port yields a ``{label, value}`` entry."""
        from openbb_imf.utils import port_watch_helpers as pwh

        with patch.object(pwh, "get_ports", return_value=_PORTS_FIXTURE):
            choices = pwh.get_port_id_choices()
        assert len(choices) == 3
        assert choices[0] == {"label": "Port One", "value": "PORT1"}


class TestGetPortsSyncBridge:
    """Tests for ``_run_list_ports_sync`` and ``get_ports``."""

    def test_get_ports_returns_async_payload(self):
        """``get_ports`` runs ``list_ports`` through a thread pool."""
        from openbb_imf.utils import port_watch_helpers as pwh

        async def _fake_list_ports():
            return [{"portid": "P", "portname": "Name", "ISO3": "USA"}]

        with patch.object(pwh, "list_ports", side_effect=_fake_list_ports):
            assert pwh.get_ports() == [
                {"portid": "P", "portname": "Name", "ISO3": "USA"}
            ]

    def test_run_list_ports_sync_uses_asyncio_run(self):
        """``_run_list_ports_sync`` drops into ``asyncio.run`` directly."""
        from openbb_imf.utils import port_watch_helpers as pwh

        async def _fake():
            return ["ok"]

        with patch.object(pwh, "list_ports", side_effect=_fake):
            assert pwh._run_list_ports_sync() == ["ok"]


class TestListPortsAsync:
    """Tests for the async ``list_ports`` fetcher."""

    @pytest.mark.asyncio
    async def test_returns_attributes(self):
        """A 200 response yields the ``features.attributes`` payload."""
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.list_ports.cache_clear()
        patcher, _ = _patch_session(
            {
                "features": [
                    {"attributes": {"portid": "P1", "portname": "Port"}},
                ]
            }
        )
        with patcher:
            ports = await pwh.list_ports()
        assert ports == [{"portid": "P1", "portname": "Port"}]
        pwh.list_ports.cache_clear()

    @pytest.mark.asyncio
    async def test_non_200_raises(self):
        """A non-200 response surfaces as ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.list_ports.cache_clear()
        bad = _FakeResponse({}, status=500)
        bad.reason = "Bad"
        fake = _FakeSession([])
        fake.get = lambda url: _AwaitableContext(bad)  # type: ignore

        class _Factory:
            async def __aenter__(self_):
                return fake

            async def __aexit__(self_, *args):
                return False

        async def _factory(*args, **kwargs):
            return _Factory()

        with patch(
            "openbb_core.provider.utils.helpers.get_async_requests_session",
            side_effect=_factory,
        ):
            with pytest.raises(OpenBBError):
                await pwh.list_ports()
        pwh.list_ports.cache_clear()


class TestDailyChokepointData:
    """Tests for ``get_daily_chokepoint_data`` and the bulk aggregator."""

    @pytest.mark.asyncio
    async def test_dated_paginates_and_normalises(self):
        """A dated query paginates and turns ``year/month/day`` into ``date``."""
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_daily_chokepoint_data.cache_clear()
        patcher, fake = _patch_session(
            {
                "features": [
                    {"attributes": {"year": 2024, "month": 1, "day": 1, "v": 1}}
                ],
                "exceededTransferLimit": True,
            },
            {
                "features": [
                    {"attributes": {"year": 2024, "month": 1, "day": 2, "v": 2}}
                ],
            },
        )
        with patcher:
            rows = await pwh.get_daily_chokepoint_data(
                "chokepoint1", "2024-01-01", "2024-01-31"
            )
        assert [r["date"] for r in rows] == ["2024-01-01", "2024-01-02"]
        assert all("year" not in r for r in rows)
        assert "TIMESTAMP" in fake.urls[0]
        pwh.get_daily_chokepoint_data.cache_clear()

    @pytest.mark.asyncio
    async def test_no_dates_uses_undated_url(self):
        """When no date range is supplied, the un-dated URL form is used."""
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_daily_chokepoint_data.cache_clear()
        patcher, fake = _patch_session(
            {"features": [{"attributes": {"year": 2024, "month": 1, "day": 1}}]}
        )
        with patcher:
            await pwh.get_daily_chokepoint_data("chokepoint2")
        assert "TIMESTAMP" not in fake.urls[0]
        pwh.get_daily_chokepoint_data.cache_clear()

    @pytest.mark.asyncio
    async def test_only_start_date_defaults_end(self):
        """A start_date alone makes the helper supply ``today`` as the end."""
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_daily_chokepoint_data.cache_clear()
        patcher, fake = _patch_session({"features": []})
        with patcher:
            await pwh.get_daily_chokepoint_data("chokepoint3", start_date="2024-01-01")
        assert "TIMESTAMP" in fake.urls[0]
        pwh.get_daily_chokepoint_data.cache_clear()

    @pytest.mark.asyncio
    async def test_only_end_date_defaults_start(self):
        """An end_date alone defaults the start to ``2019-01-01``."""
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_daily_chokepoint_data.cache_clear()
        patcher, fake = _patch_session({"features": []})
        with patcher:
            await pwh.get_daily_chokepoint_data("chokepoint4", end_date="2024-01-01")
        assert "2019-01-01" in fake.urls[0]
        pwh.get_daily_chokepoint_data.cache_clear()

    @pytest.mark.asyncio
    async def test_non_200_initial_raises(self):
        """A non-200 on the initial fetch raises ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_daily_chokepoint_data.cache_clear()
        bad = _FakeResponse({}, status=500)
        fake = _FakeSession([])
        fake.get = lambda url: _AwaitableContext(bad)  # type: ignore

        class _Factory:
            async def __aenter__(self_):
                return fake

            async def __aexit__(self_, *args):
                return False

        async def _factory(*args, **kwargs):
            return _Factory()

        with patch(
            "openbb_core.provider.utils.helpers.get_async_requests_session",
            side_effect=_factory,
        ):
            with pytest.raises(OpenBBError):
                await pwh.get_daily_chokepoint_data("chokepoint5")
        pwh.get_daily_chokepoint_data.cache_clear()

    @pytest.mark.asyncio
    async def test_non_200_on_followup_raises(self):
        """A non-200 on a follow-up page raises ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_daily_chokepoint_data.cache_clear()
        ok = _FakeResponse(
            {
                "features": [
                    {"attributes": {"year": 2024, "month": 1, "day": 1, "v": 1}}
                ],
                "exceededTransferLimit": True,
            }
        )
        bad = _FakeResponse({}, status=500)

        calls = {"n": 0}

        def _get(url):
            calls["n"] += 1
            return _AwaitableContext(ok if calls["n"] == 1 else bad)

        fake = _FakeSession([])
        fake.get = _get  # type: ignore

        class _Factory:
            async def __aenter__(self_):
                return fake

            async def __aexit__(self_, *args):
                return False

        async def _factory(*args, **kwargs):
            return _Factory()

        with patch(
            "openbb_core.provider.utils.helpers.get_async_requests_session",
            side_effect=_factory,
        ):
            with pytest.raises(OpenBBError):
                await pwh.get_daily_chokepoint_data("chokepoint6")
        pwh.get_daily_chokepoint_data.cache_clear()

    @pytest.mark.asyncio
    async def test_all_daily_chokepoint_activity_data_combines(self):
        """``get_all_daily_chokepoint_activity_data`` gathers all 24 chokepoints."""
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_all_daily_chokepoint_activity_data.cache_clear()

        async def _fake(_, *args, **kwargs):
            return [{"date": "2024-01-01", "v": 1}]

        with patch.object(pwh, "get_daily_chokepoint_data", side_effect=_fake):
            rows = await pwh.get_all_daily_chokepoint_activity_data()
        assert len(rows) == 24
        pwh.get_all_daily_chokepoint_activity_data.cache_clear()

    @pytest.mark.asyncio
    async def test_all_daily_chokepoint_activity_propagates_errors(self):
        """A single-chokepoint failure surfaces from the gather."""
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_all_daily_chokepoint_activity_data.cache_clear()

        async def _boom(*_, **__):
            raise OpenBBError("nope")

        with patch.object(pwh, "get_daily_chokepoint_data", side_effect=_boom):
            with pytest.raises(OpenBBError):
                await pwh.get_all_daily_chokepoint_activity_data()
        pwh.get_all_daily_chokepoint_activity_data.cache_clear()

    @pytest.mark.asyncio
    async def test_all_daily_chokepoint_activity_empty_raises(self):
        """If every chokepoint returns nothing, raise the empty-results error."""
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_all_daily_chokepoint_activity_data.cache_clear()

        async def _empty(*_, **__):
            return []

        with patch.object(pwh, "get_daily_chokepoint_data", side_effect=_empty):
            with pytest.raises(OpenBBError):
                await pwh.get_all_daily_chokepoint_activity_data()
        pwh.get_all_daily_chokepoint_activity_data.cache_clear()


class TestDailyPortActivity:
    """Tests for ``get_daily_port_activity_data`` and the bulk CSV variant."""

    @pytest.mark.asyncio
    async def test_dated_paginates(self):
        """A dated query paginates and normalises the ``year/month/day`` triplet."""
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_daily_port_activity_data.cache_clear()
        patcher, fake = _patch_session(
            {
                "features": [
                    {"attributes": {"year": 2024, "month": 1, "day": 1, "v": 1}}
                ],
                "exceededTransferLimit": True,
            },
            {
                "features": [
                    {"attributes": {"year": 2024, "month": 1, "day": 2, "v": 2}}
                ]
            },
        )
        with patcher:
            rows = await pwh.get_daily_port_activity_data(
                "p1", "2024-01-01", "2024-01-31"
            )
        assert [r["date"] for r in rows] == ["2024-01-01", "2024-01-02"]
        assert "TIMESTAMP" in fake.urls[0]
        pwh.get_daily_port_activity_data.cache_clear()

    @pytest.mark.asyncio
    async def test_no_dates_undated_url(self):
        """Without dates the un-dated URL form is used."""
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_daily_port_activity_data.cache_clear()
        patcher, fake = _patch_session(
            {"features": [{"attributes": {"year": 2024, "month": 1, "day": 1}}]}
        )
        with patcher:
            await pwh.get_daily_port_activity_data("p2")
        assert "TIMESTAMP" not in fake.urls[0]
        pwh.get_daily_port_activity_data.cache_clear()

    @pytest.mark.asyncio
    async def test_only_start_date(self):
        """A start_date alone backfills ``end_date`` with today."""
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_daily_port_activity_data.cache_clear()
        patcher, fake = _patch_session({"features": []})
        with patcher:
            await pwh.get_daily_port_activity_data("p3", start_date="2024-01-01")
        assert "TIMESTAMP" in fake.urls[0]
        pwh.get_daily_port_activity_data.cache_clear()

    @pytest.mark.asyncio
    async def test_only_end_date(self):
        """An end_date alone backfills ``start_date`` with 2019-01-01."""
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_daily_port_activity_data.cache_clear()
        patcher, fake = _patch_session({"features": []})
        with patcher:
            await pwh.get_daily_port_activity_data("p4", end_date="2024-01-01")
        assert "2019-01-01" in fake.urls[0]
        pwh.get_daily_port_activity_data.cache_clear()

    @pytest.mark.asyncio
    async def test_missing_port_id_raises(self):
        """A ``None`` port_id raises ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_daily_port_activity_data.cache_clear()
        with pytest.raises(OpenBBError):
            await pwh.get_daily_port_activity_data(None)
        pwh.get_daily_port_activity_data.cache_clear()

    @pytest.mark.asyncio
    async def test_non_200_initial_raises(self):
        """A non-200 on the initial response raises."""
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_daily_port_activity_data.cache_clear()
        bad = _FakeResponse({}, status=500)
        fake = _FakeSession([])
        fake.get = lambda url: _AwaitableContext(bad)  # type: ignore

        class _Factory:
            async def __aenter__(self_):
                return fake

            async def __aexit__(self_, *args):
                return False

        async def _factory(*args, **kwargs):
            return _Factory()

        with patch(
            "openbb_core.provider.utils.helpers.get_async_requests_session",
            side_effect=_factory,
        ):
            with pytest.raises(OpenBBError):
                await pwh.get_daily_port_activity_data("px")
        pwh.get_daily_port_activity_data.cache_clear()

    @pytest.mark.asyncio
    async def test_non_200_on_followup_raises(self):
        """A non-200 on the second page raises."""
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_daily_port_activity_data.cache_clear()
        ok = _FakeResponse(
            {
                "features": [
                    {"attributes": {"year": 2024, "month": 1, "day": 1, "v": 1}}
                ],
                "exceededTransferLimit": True,
            }
        )
        bad = _FakeResponse({}, status=500)

        calls = {"n": 0}

        def _get(url):
            calls["n"] += 1
            return _AwaitableContext(ok if calls["n"] == 1 else bad)

        fake = _FakeSession([])
        fake.get = _get  # type: ignore

        class _Factory:
            async def __aenter__(self_):
                return fake

            async def __aexit__(self_, *args):
                return False

        async def _factory(*args, **kwargs):
            return _Factory()

        with patch(
            "openbb_core.provider.utils.helpers.get_async_requests_session",
            side_effect=_factory,
        ):
            with pytest.raises(OpenBBError):
                await pwh.get_daily_port_activity_data("py")
        pwh.get_daily_port_activity_data.cache_clear()


class TestAllDailyPortActivityCsv:
    """Tests for the bulk CSV ``get_all_daily_port_activity_data`` helper."""

    @pytest.mark.asyncio
    async def test_returns_records(self):
        """A 200 CSV response is parsed into a list of dicts."""
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_all_daily_port_activity_data.cache_clear()

        csv_text = "date,portid,v,ObjectId,GlobalID,year,month,day\n2024-01-01,P1,5,1,g,2024,1,1\n"

        class _CsvResp:
            status = 200
            reason = "OK"
            content = b"x"

            async def __aenter__(self):
                return self

            async def __aexit__(self, *_):
                return False

            async def text(self):
                return csv_text

        fake = _FakeSession([])
        fake.get = lambda url: _AwaitableContext(_CsvResp())  # type: ignore

        class _Factory:
            async def __aenter__(self_):
                return fake

            async def __aexit__(self_, *args):
                return False

        async def _factory(*args, **kwargs):
            return _Factory()

        with patch(
            "openbb_core.provider.utils.helpers.get_async_requests_session",
            side_effect=_factory,
        ):
            rows = await pwh.get_all_daily_port_activity_data()
        assert rows[0]["portid"] == "P1"
        assert "ObjectId" not in rows[0]
        assert "year" not in rows[0]
        pwh.get_all_daily_port_activity_data.cache_clear()

    @pytest.mark.asyncio
    async def test_non_200_raises(self):
        """A non-200 CSV response raises ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_all_daily_port_activity_data.cache_clear()

        class _CsvResp:
            status = 500
            reason = "Down"
            content = b""

            async def __aenter__(self):
                return self

            async def __aexit__(self, *_):
                return False

            async def text(self):
                return ""

        fake = _FakeSession([])
        fake.get = lambda url: _AwaitableContext(_CsvResp())  # type: ignore

        class _Factory:
            async def __aenter__(self_):
                return fake

            async def __aexit__(self_, *args):
                return False

        async def _factory(*args, **kwargs):
            return _Factory()

        with patch(
            "openbb_core.provider.utils.helpers.get_async_requests_session",
            side_effect=_factory,
        ):
            with pytest.raises(OpenBBError):
                await pwh.get_all_daily_port_activity_data()
        pwh.get_all_daily_port_activity_data.cache_clear()

    @pytest.mark.asyncio
    async def test_empty_content_raises(self):
        """A response with ``content=None`` raises."""
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_all_daily_port_activity_data.cache_clear()

        class _CsvResp:
            status = 200
            reason = "OK"
            content = None

            async def __aenter__(self):
                return self

            async def __aexit__(self, *_):
                return False

            async def text(self):
                return ""

        fake = _FakeSession([])
        fake.get = lambda url: _AwaitableContext(_CsvResp())  # type: ignore

        class _Factory:
            async def __aenter__(self_):
                return fake

            async def __aexit__(self_, *args):
                return False

        async def _factory(*args, **kwargs):
            return _Factory()

        with patch(
            "openbb_core.provider.utils.helpers.get_async_requests_session",
            side_effect=_factory,
        ):
            with pytest.raises(OpenBBError):
                await pwh.get_all_daily_port_activity_data()
        pwh.get_all_daily_port_activity_data.cache_clear()


class TestContainerMetricsSkipsNoneValues:
    """Edge test for the ``val is None`` continue inside ``get_container_metrics``."""

    @pytest.mark.asyncio
    async def test_none_port_values_skipped(self):
        """A row where a port column is ``None`` produces no entry for that port."""
        from openbb_imf.utils import port_watch_helpers as pwh

        pwh.get_container_metrics.cache_clear()
        rows_payload = [
            {
                "metric": "portcalls",
                "date_in": 1_704_067_200_000,
                "PORTA": 5,
                "PORTB": None,
            }
        ]
        with patch(
            "openbb_imf.utils.port_watch_helpers._arcgis_query",
            new=AsyncMock(return_value=rows_payload),
        ):
            out = await pwh.get_container_metrics(None, "portcalls")
        ports = {r["portid"] for r in out}
        assert ports == {"PORTA"}
        pwh.get_container_metrics.cache_clear()
