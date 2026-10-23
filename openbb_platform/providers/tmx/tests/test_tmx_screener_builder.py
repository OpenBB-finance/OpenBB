"""Tests for the screener builder catalog, page, and presets."""

from datetime import date

import pytest

from openbb_tmx.utils import screener_presets
from openbb_tmx.utils.screener_catalog import build_screener_catalog, query_from_config
from openbb_tmx.utils.screener_iframe import (
    COLUMNS,
    build_screener_builder_html,
    prune_empty_columns,
)


class TestCatalog:
    """The catalog the builder renders."""

    def test_the_catalog_carries_every_surface(self):
        catalog = build_screener_catalog("CA")

        assert catalog["country"] == "CA"
        assert catalog["asset_types"]
        assert catalog["fields"]
        assert catalog["sort_fields"]
        assert catalog["sort_types"]

    def test_every_field_names_a_screener_parameter(self):
        from openbb_tmx.models.equity_screener import TmxEquityScreenerQueryParams

        accepted = set(TmxEquityScreenerQueryParams.model_fields)

        for field in build_screener_catalog("CA")["fields"]:
            param = field["param"]

            assert (
                param in accepted
                or f"{param}_min" in accepted
                and f"{param}_max" in accepted
            ), param

    def test_every_field_carries_a_category_and_operators(self):
        for field in build_screener_catalog("CA")["fields"]:
            assert field["category"] and field["category_label"]
            assert field["operators"]

    def test_a_field_is_declared_once(self):
        params = [f["param"] for f in build_screener_catalog("CA")["fields"]]

        assert len(params) == len(set(params))

    def test_the_sector_tree_cascades(self):
        tree = next(
            f for f in build_screener_catalog("CA")["fields"] if f["type"] == "tree"
        )
        energy = next(s for s in tree["options"] if s["value"] == "energy")

        assert energy["label"] == "Energy"
        assert energy["children"]
        assert all(child["children"] for child in energy["children"])

    def test_an_unknown_country_falls_back(self):
        assert build_screener_catalog("ZZ")["country"] == "CA"

    def test_the_us_catalog_is_served(self):
        assert build_screener_catalog("US")["country"] == "US"


class TestConfigTranslation:
    """A builder configuration becomes screener query parameters."""

    def test_the_shell_of_a_configuration_is_kept(self):
        params = query_from_config(
            {"asset_type": "ETF", "sort_by": "market_cap", "limit": 25}
        )

        assert params == {
            "symbol_type": "ETF",
            "sort_by": "market_cap",
            "limit": 25,
        }

    def test_a_between_condition_sets_both_bounds(self):
        params = query_from_config(
            {
                "conditions": [
                    {"param": "market_cap", "operator": "between", "value": [1e9, 5e9]}
                ]
            }
        )

        assert params == {"market_cap_min": 1e9, "market_cap_max": 5e9}

    def test_an_at_least_condition_sets_only_the_floor(self):
        params = query_from_config(
            {"conditions": [{"param": "beta", "operator": "gte", "value": [0.5, None]}]}
        )

        assert params == {"beta_min": 0.5}

    def test_an_at_most_condition_sets_only_the_ceiling(self):
        params = query_from_config(
            {"conditions": [{"param": "beta", "operator": "lte", "value": [None, 1.5]}]}
        )

        assert params == {"beta_max": 1.5}

    def test_a_boolean_condition_is_kept(self):
        params = query_from_config(
            {"conditions": [{"param": "optionable", "operator": "is", "value": True}]}
        )

        assert params == {"optionable": True}

    def test_a_sector_condition_is_kept(self):
        params = query_from_config(
            {"conditions": [{"param": "sector", "operator": "is", "value": "energy"}]}
        )

        assert params == {"sector": "energy"}

    def test_an_unknown_sector_is_dropped(self):
        params = query_from_config(
            {"conditions": [{"param": "sector", "operator": "is", "value": "atlantis"}]}
        )

        assert params == {}

    def test_an_empty_condition_is_dropped(self):
        params = query_from_config(
            {"conditions": [{"param": "beta", "operator": "gte", "value": None}]}
        )

        assert params == {}

    def test_an_empty_configuration_is_accepted(self):
        assert query_from_config({}) == {}
        assert query_from_config(None) == {}


class TestColumns:
    """The result columns follow the rows."""

    def test_empty_columns_are_pruned(self):
        rows = [{"symbol": "AC", "pe_ratio": None, "market_cap": 1}]
        kept = [c["field"] for c in prune_empty_columns(rows, COLUMNS)]

        assert "symbol" in kept
        assert "market_cap" in kept
        assert "pe_ratio" not in kept

    def test_no_rows_keeps_every_column(self):
        """An empty result still renders its headers."""
        assert prune_empty_columns([], COLUMNS) == COLUMNS

    def test_required_columns_survive_a_blank_value(self):
        kept = [
            c["field"]
            for c in prune_empty_columns([{"symbol": "AC", "name": ""}], COLUMNS)
        ]

        assert "name" in kept


class TestBuilderPage:
    """The page the iframe loads."""

    def test_the_page_carries_its_grid_and_components(self):
        html = build_screener_builder_html("dark")

        assert "tmx-results-grid" in html
        assert "screener:apply" in html and "screener:add-filter" in html
        assert "json_data" in html

    def test_the_theme_is_applied(self):
        assert "pywry-theme-light" in build_screener_builder_html("light")
        assert "pywry-theme-dark" in build_screener_builder_html("dark")

    def test_the_iframe_transport_is_declared(self):
        assert '"transport": "iframe"' in build_screener_builder_html("dark").replace(
            "&quot;", '"'
        )


class TestPresets:
    """Saved configurations round-trip."""

    @pytest.fixture(autouse=True)
    def store(self, tmp_path, monkeypatch):
        """Keep the presets out of the user's home directory."""
        monkeypatch.setattr(
            screener_presets, "_STORE", tmp_path / "presets.json", raising=False
        )

    def test_the_shipped_presets_are_always_listed(self):
        listed = [p["name"] for p in screener_presets.list_presets()]

        assert listed == list(screener_presets.DEFAULTS)

    def test_a_shipped_preset_is_loaded(self):
        config = screener_presets.load_preset("Value")

        assert config["asset_type"] == "Equity"
        assert config["conditions"]

    def test_a_preset_round_trips(self):
        screener_presets.save_preset("Income", {"dividend_yield_min": 4})
        listed = [p["name"] for p in screener_presets.list_presets()]

        assert listed[-1] == "Income"
        assert screener_presets.load_preset("Income") == {"dividend_yield_min": 4}

    def test_a_missing_preset_is_reported(self):
        with pytest.raises(FileNotFoundError):
            screener_presets.load_preset("nope")

    def test_an_unusable_name_is_rejected(self):
        with pytest.raises(ValueError, match="letters, digits"):
            screener_presets.save_preset("../escape", {})

    def test_a_preset_is_deleted(self):
        screener_presets.save_preset("Income", {})
        remaining = [p["name"] for p in screener_presets.delete_preset("Income")]

        assert "Income" not in remaining

    def test_deleting_an_absent_preset_is_accepted(self):
        remaining = [p["name"] for p in screener_presets.delete_preset("ghost")]

        assert remaining == list(screener_presets.DEFAULTS)

    def test_an_unreadable_store_reads_as_empty(self, tmp_path, monkeypatch):
        broken = tmp_path / "broken.json"
        broken.write_text("{not json", encoding="utf-8")
        monkeypatch.setattr(screener_presets, "_STORE", broken, raising=False)
        listed = [p["name"] for p in screener_presets.list_presets()]

        assert listed == list(screener_presets.DEFAULTS)


class TestBuilderEndpoints:
    """The routes the iframe calls."""

    @pytest.fixture
    def client(self):
        """Serve the TMX router."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from openbb_tmx.routers.equity import router

        app = FastAPI()
        app.include_router(router.api_router, prefix="/tmx")

        return TestClient(app)

    def test_the_page_is_served(self, client):
        response = client.get("/tmx/equity/screener_builder/view")

        assert response.status_code == 200
        assert "tmx-results-grid" in response.text

    def test_the_catalog_is_served(self, client):
        payload = client.get("/tmx/equity/screener_builder/catalog").json()

        assert payload["fields"]
        assert payload["asset_types"]

    def test_an_invalid_configuration_is_rejected(self, client):
        response = client.get(
            "/tmx/equity/screener_builder/run", params={"config": "{not json"}
        )

        assert response.status_code == 400
        assert response.json()["rows"] == []

    def test_a_non_mapping_configuration_returns_nothing(self, client):
        payload = client.get(
            "/tmx/equity/screener_builder/run", params={"config": "[1, 2]"}
        ).json()

        assert payload == {"rows": [], "columns": []}

    def test_a_failed_screen_is_reported(self, client, monkeypatch):
        from openbb_core.provider.utils.errors import EmptyDataError

        async def empty(*args, **kwargs):
            raise EmptyDataError("No instruments matched the screen.")

        monkeypatch.setattr(
            "openbb_tmx.models.equity_screener.TmxEquityScreenerFetcher.fetch_data",
            empty,
        )
        payload = client.get(
            "/tmx/equity/screener_builder/run", params={"config": "{}"}
        ).json()

        assert payload["rows"] == []
        assert "No instruments matched" in payload["error"]

    def test_a_broken_screen_reports_a_fixed_message(self, client, monkeypatch):
        from openbb_core.app.model.abstract.error import OpenBBError

        async def broken(*args, **kwargs):
            raise OpenBBError("postgres://tmx:hunter2@10.0.0.4/quotes is unreachable")

        monkeypatch.setattr(
            "openbb_tmx.models.equity_screener.TmxEquityScreenerFetcher.fetch_data",
            broken,
        )
        payload = client.get(
            "/tmx/equity/screener_builder/run", params={"config": "{}"}
        ).json()

        assert payload == {
            "error": "The screen could not be run.",
            "rows": [],
            "columns": [],
        }

    def test_an_unwritable_preset_store_reports_a_fixed_message(
        self, client, monkeypatch
    ):
        from openbb_tmx.utils import screener_presets

        def refuse(presets):
            raise OSError("[Errno 13] Permission denied: '/root/.openbb_platform'")

        monkeypatch.setattr(screener_presets, "_write", refuse)
        response = client.post(
            "/tmx/equity/screener_builder/presets/save",
            params={"name": "Income", "config": "{}"},
        )

        assert response.status_code == 400
        assert response.json() == {"error": "The preset could not be saved."}

    def test_an_invalid_preset_configuration_is_rejected(self, client):
        response = client.post(
            "/tmx/equity/screener_builder/presets/save",
            params={"name": "Income", "config": "{not json"},
        )

        assert response.status_code == 400
        assert response.json() == {"error": "The configuration is not valid JSON."}

    def test_rows_and_columns_are_returned(self, client, monkeypatch):
        from openbb_tmx.models.equity_screener import TmxEquityScreenerData

        async def rows(*args, **kwargs):
            return [
                TmxEquityScreenerData(symbol="AC", name="Air Canada", market_cap=8.0e9)
            ]

        monkeypatch.setattr(
            "openbb_tmx.models.equity_screener.TmxEquityScreenerFetcher.fetch_data",
            rows,
        )
        payload = client.get(
            "/tmx/equity/screener_builder/run", params={"config": "{}"}
        ).json()

        assert payload["rows"][0]["symbol"] == "AC"
        assert [c["field"] for c in payload["columns"]] == [
            "symbol",
            "name",
            "market_cap",
        ]

    def test_presets_round_trip_over_http(self, client, tmp_path, monkeypatch):
        from openbb_tmx.utils import screener_presets

        monkeypatch.setattr(
            screener_presets, "_STORE", tmp_path / "presets.json", raising=False
        )
        base = "/tmx/equity/screener_builder/presets"

        saved = client.post(
            f"{base}/save", params={"name": "Income", "config": "{}"}
        ).json()

        assert saved["presets"][-1] == {"name": "Income", "label": "Income"}
        assert client.get(base).json() == saved
        assert client.get(f"{base}/load", params={"name": "Income"}).json() == {
            "config": {}
        }
        assert client.get(f"{base}/load", params={"name": "Value"}).json()["config"]
        assert client.get(f"{base}/load", params={"name": "gone"}).status_code == 404
        assert (
            client.post(
                f"{base}/save", params={"name": "../x", "config": "{}"}
            ).status_code
            == 400
        )
        remaining = client.post(f"{base}/delete", params={"name": "Income"}).json()

        assert "Income" not in [p["name"] for p in remaining["presets"]]


class TestNativeBuilder:
    """The desktop surface and its bridge callbacks."""

    def test_a_headless_host_is_given_the_iframe(self, monkeypatch):
        from openbb_core.provider.utils.helpers import run_async

        from openbb_tmx.routers import equity

        monkeypatch.setattr(equity, "_gui_available", lambda: False)
        result = run_async(equity.screener_builder, "light")

        assert "screener_builder/view?theme=light" in result.results["endpoint"]

    def test_a_desktop_host_opens_a_window(self, monkeypatch):
        from openbb_core.provider.utils.helpers import run_async

        from openbb_tmx.routers import equity
        from openbb_tmx.utils import screener_native

        opened: dict = {}

        def launch(theme):
            opened["theme"] = theme
            return {"window": "tmx_screener_builder"}

        monkeypatch.setattr(equity, "_gui_available", lambda: True)
        monkeypatch.setattr(screener_native, "launch_screener_builder", launch)
        result = run_async(equity.screener_builder, "dark")

        assert opened["theme"] == "dark"
        assert result.results == {"window": "tmx_screener_builder"}

    def test_the_bridge_answers_a_run(self, monkeypatch):
        import json

        from openbb_tmx.utils import screener_native

        emitted: list = []

        class App:
            def emit(self, event, payload):
                emitted.append((event, payload))

        monkeypatch.setattr(
            screener_native,
            "_run_screen",
            lambda config, limit: [{"symbol": "AC", "name": "Air Canada"}],
        )
        callbacks = screener_native.make_screener_callbacks(App())
        callbacks["screener:run"](
            {"config": json.dumps({"asset_type": "Equity"}), "limit": 5}
        )

        assert emitted[0][0] == "screener:results"
        assert emitted[0][1]["rows"][0]["symbol"] == "AC"
        assert emitted[0][1]["columns"]

    def test_a_failed_bridge_run_is_reported(self, monkeypatch):
        from openbb_tmx.utils import screener_native

        emitted: list = []

        class App:
            def emit(self, event, payload):
                emitted.append(payload)

        def boom(config, limit):
            raise RuntimeError("no")

        monkeypatch.setattr(screener_native, "_run_screen", boom)
        callbacks = screener_native.make_screener_callbacks(App())
        callbacks["screener:run"]({"config": "{}", "limit": 1})

        assert emitted[0]["rows"] == []
        assert "could not be run" in emitted[0]["error"]

    def test_the_bridge_serves_presets(self, monkeypatch, tmp_path):
        from openbb_tmx.utils import screener_native, screener_presets

        monkeypatch.setattr(
            screener_presets, "_STORE", tmp_path / "presets.json", raising=False
        )
        emitted: list = []

        class App:
            def emit(self, event, payload):
                emitted.append((event, payload))

        callbacks = screener_native.make_screener_callbacks(App())
        callbacks["screener:preset-save"]({"name": "Income", "config": "{}"})
        callbacks["screener:presets-list"]({})
        callbacks["screener:preset-load"]({"name": "Income"})
        callbacks["screener:preset-delete"]({"name": "Income"})

        assert emitted[0][1]["presets"][-1] == {"name": "Income", "label": "Income"}
        assert emitted[2][1]["config"] == {}
        assert "Income" not in [p["name"] for p in emitted[3][1]["presets"]]

    def test_a_missing_preset_is_reported_over_the_bridge(self, monkeypatch, tmp_path):
        from openbb_tmx.utils import screener_native, screener_presets

        monkeypatch.setattr(
            screener_presets, "_STORE", tmp_path / "presets.json", raising=False
        )
        emitted: list = []

        class App:
            def emit(self, event, payload):
                emitted.append(payload)

        callbacks = screener_native.make_screener_callbacks(App())
        callbacks["screener:preset-load"]({"name": "ghost"})

        assert emitted[0]["error"] == "Preset not found."

    def test_the_bridge_content_declares_its_transport(self):
        from openbb_tmx.utils.screener_iframe import build_screener_content

        content, toolbars, modals, theme = build_screener_content("dark", "bridge")

        assert content.json_data["transport"] == "bridge"
        assert len(toolbars) == 2
        assert len(modals) == 3
        assert theme == "dark"


class TestNativeInternals:
    """The pieces the desktop surface is built from."""

    def test_the_screen_runs_on_its_own_loop(self, monkeypatch):
        from openbb_tmx.models.equity_screener import TmxEquityScreenerData
        from openbb_tmx.utils import screener_native

        seen: dict = {}

        async def fetch(params, credentials):
            seen.update(params)
            return [TmxEquityScreenerData(symbol="AC", name="Air Canada")]

        monkeypatch.setattr(
            "openbb_tmx.models.equity_screener.TmxEquityScreenerFetcher.fetch_data",
            fetch,
        )
        rows = screener_native._run_screen({"asset_type": "ETF"}, 25)

        assert rows == [{"symbol": "AC", "name": "Air Canada"}]
        assert seen["symbol_type"] == "ETF"
        assert seen["limit"] == 25

    def test_an_empty_screen_returns_no_rows(self, monkeypatch):
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_tmx.utils import screener_native

        async def fetch(params, credentials):
            raise EmptyDataError("nothing matched")

        monkeypatch.setattr(
            "openbb_tmx.models.equity_screener.TmxEquityScreenerFetcher.fetch_data",
            fetch,
        )

        assert screener_native._run_screen({}, None) == []

    def test_an_unparsable_configuration_screens_on_nothing(self, monkeypatch):
        from openbb_tmx.utils import screener_native

        seen: list = []

        class App:
            def emit(self, event, payload):
                seen.append(payload)

        monkeypatch.setattr(
            screener_native, "_run_screen", lambda config, limit: [{"symbol": "AC"}]
        )
        callbacks = screener_native.make_screener_callbacks(App())
        callbacks["screener:run"]({"config": "{not json", "limit": 1})

        assert seen[0]["rows"] == [{"symbol": "AC"}]

    def test_the_theme_follows_the_window(self):
        from pywry import ThemeMode

        from openbb_tmx.utils import screener_native

        class App:
            theme = None

            def emit(self, event, payload):
                """Emit nothing."""

        app = App()
        callbacks = screener_native.make_screener_callbacks(app)
        callbacks["pywry:update-theme"]({"theme": "light"})

        assert app.theme == ThemeMode.LIGHT

        callbacks["pywry:update-theme"]({"theme": "dark"})

        assert app.theme == ThemeMode.DARK

    def test_an_unusable_preset_name_is_reported(self, monkeypatch, tmp_path):
        from openbb_tmx.utils import screener_native, screener_presets

        monkeypatch.setattr(
            screener_presets, "_STORE", tmp_path / "presets.json", raising=False
        )
        seen: list = []

        class App:
            def emit(self, event, payload):
                seen.append(payload)

        callbacks = screener_native.make_screener_callbacks(App())
        callbacks["screener:preset-save"]({"name": "../escape", "config": "{}"})

        assert seen[0]["error"] == "The preset could not be saved."

    def test_the_application_is_created_once(self, monkeypatch):
        from openbb_tmx.utils import screener_native

        built: list = []

        class FakePyWry:
            def __init__(self, theme=None):
                built.append(theme)
                self.theme = theme

        monkeypatch.setattr(screener_native, "_APP", None, raising=False)
        monkeypatch.setitem(
            __import__("sys").modules["pywry"].__dict__, "PyWry", FakePyWry
        )
        first = screener_native._get_app("dark")
        second = screener_native._get_app("light")

        assert first is second
        assert built == ["dark"]
        assert second.theme == "light"

        monkeypatch.setattr(screener_native, "_APP", None, raising=False)

    def test_the_window_opens_with_the_bridge_content(self, monkeypatch):
        from openbb_tmx.utils import screener_native

        shown: dict = {}

        class App:
            def show(self, content, **kwargs):
                shown.update(kwargs)
                shown["content"] = content
                return {"window": "tmx_screener_builder"}

        monkeypatch.setattr(screener_native, "_get_app", lambda theme: App())
        handle = screener_native.launch_screener_builder("light", width=100, height=200)

        assert handle == {"window": "tmx_screener_builder"}
        assert shown["width"] == 100 and shown["height"] == 200
        assert shown["aggrid_theme"] == "balham"
        assert len(shown["toolbars"]) == 2 and len(shown["modals"]) == 3
        assert "screener:run" in shown["callbacks"]
        assert shown["content"].json_data["transport"] == "bridge"


class TestAssetInfo:
    """The asset overview page."""

    def test_a_missing_value_renders_no_row(self):
        from openbb_tmx.utils.asset_info import _stat

        assert _stat("Beta", "-") == ""
        assert _stat("Beta", "") == ""
        assert "Beta" in _stat("Beta", "1.05")

    def test_a_range_needs_both_ends(self):
        from openbb_tmx.utils.asset_info import _range

        assert _range("Day Range", None, 5, 3) == ""
        assert _range("Day Range", 1, None, 3) == ""
        assert "Day Range" in _range("Day Range", 1, 5, 3)

    def test_a_range_marks_where_the_last_level_sits(self):
        from openbb_tmx.utils.asset_info import _range

        rendered = _range("Day Range", 0, 10, 5)

        assert "ai-bar" in rendered
        assert "left:50.0%" in rendered

    def test_a_range_without_a_last_level_has_no_marker(self):
        from openbb_tmx.utils.asset_info import _range

        assert "ai-bar" not in _range("Day Range", 1, 5, None)

    def test_a_card_with_no_rows_is_dropped(self):
        from openbb_tmx.utils.asset_info import _card

        assert _card("Valuation", "") == ""
        assert "Valuation" in _card("Valuation", "<div></div>")

    @pytest.mark.parametrize(
        ("value", "expected"),
        [(None, "-"), (1_500_000_000_000, "1.50T"), (2.5e9, "2.50B"), (900, "900")],
    )
    def test_large_numbers_are_compact(self, value, expected):
        from openbb_tmx.utils.asset_info import _compact

        assert _compact(value) == expected

    def test_returns_need_two_observations(self):
        from openbb_tmx.utils.asset_info import _returns

        assert _returns([]) == ""
        assert _returns([{"date": date(2026, 7, 24), "close": 1.0}]) == ""

    def test_returns_are_computed_from_the_history(self):
        from openbb_tmx.utils.asset_info import _returns

        history = [
            {"date": date(2025, 7, 24), "close": 100.0},
            {"date": date(2026, 6, 24), "close": 110.0},
            {"date": date(2026, 7, 24), "close": 120.0},
        ]
        rendered = _returns(history)

        assert "1 Month" in rendered
        assert "1 Year" in rendered
        assert "20.00%" in rendered

    async def test_an_unknown_symbol_says_so(self, monkeypatch):
        from openbb_tmx.utils import asset_info

        async def nothing(symbol):
            return asset_info._empty_payload()

        monkeypatch.setattr(asset_info, "_gather", nothing)
        html = await asset_info.asset_info_html("ZZZZ")

        assert "Nothing is published" in html

    async def test_a_company_page_carries_its_cards(self, monkeypatch):
        from openbb_tmx.utils import asset_info

        async def payload(symbol):
            return {
                "quote": {
                    "name": "Air Canada",
                    "last_price": 23.27,
                    "change": 0.62,
                    "change_percent": 0.0274,
                    "exchange": "TSX",
                    "currency": "CAD",
                    "MarketCap": 8e9,
                    "pe": 6.1,
                },
                "profile": {"long_description": "An airline.", "sector": "Industrials"},
                "history": [],
                "targets": {"consensus_action": "Buy", "target_consensus": 30.0},
                "insiders": [{"period": "3_months", "net_activity": 100}],
                "shorts": {},
                "dividends": [],
                "earnings": [],
                "fund": {},
                "holdings": [],
                "sectors": [],
                "countries": [],
            }

        monkeypatch.setattr(asset_info, "_gather", payload)
        html = await asset_info.asset_info_html("AC", "light")

        assert 'data-theme="light"' in html
        assert "Air Canada" in html
        assert "Analyst Coverage" in html
        assert "An airline." in html
        assert "Fund Facts" not in html

    async def test_a_fund_page_carries_its_weightings(self, monkeypatch):
        from openbb_tmx.utils import asset_info

        async def payload(symbol):
            return {
                "quote": {"name": "iShares", "last_price": 52.74},
                "profile": {},
                "history": [],
                "targets": {},
                "insiders": [],
                "shorts": {},
                "dividends": [],
                "earnings": [],
                "fund": {"aum": 1.2e10, "description": "Tracks the index."},
                "holdings": [{"symbol": "RY", "share_percentage": 8.1}],
                "sectors": [{"sector": "Financials", "weight": 35.0}],
                "countries": [{"country": "Canada", "weight": 98.0}],
            }

        monkeypatch.setattr(asset_info, "_gather", payload)
        html = await asset_info.asset_info_html("XIU")

        assert "Fund Facts" in html
        assert "Top Holdings" in html and "RY" in html
        assert "Sector Weightings" in html and "Financials" in html
        assert "Countries" in html and "Canada" in html
        assert "Analyst Coverage" not in html

    def test_the_widget_groups_on_the_symbol(self):
        import warnings

        warnings.filterwarnings("ignore")
        from openbb_core.api.rest_api import app
        from openbb_platform_api.utils.widgets import build_json

        widget = build_json(app.openapi(), [])["tmx_equity_asset_info_obb"]
        params = {p["paramName"]: p for p in widget["params"]}

        assert widget["type"] == "iframe"
        assert params["symbol"]["value"] == "AC"
        assert params["theme"]["show"] is False


class TestAppLayout:
    """The tabs the app lays out."""

    @pytest.fixture(scope="class")
    def app(self):
        """Read the packaged layout."""
        import json
        import pathlib

        return json.loads(
            pathlib.Path("openbb_tmx/assets/apps.json").read_text(encoding="utf-8")
        )[0]

    @pytest.fixture(scope="class")
    def registry(self):
        """Build the widget registry the layout refers to."""
        import warnings

        warnings.filterwarnings("ignore")
        from openbb_core.api.rest_api import app as api
        from openbb_platform_api.utils.widgets import build_json

        return build_json(api.openapi(), [])

    def test_the_tabs_read_as_one_flow(self, app):
        assert [tab["name"] for tab in app["tabs"].values()] == [
            "Market Overview",
            "Screener",
            "Company",
            "Financials",
            "Options",
            "Futures & FX",
            "Fixed Income",
            "ETFs",
            "Indices",
            "News",
        ]

    def test_the_screener_tab_carries_the_builder_alone(self, app):
        layout = app["tabs"]["screener"]["layout"]

        assert [cell["i"] for cell in layout] == ["tmx_equity_screener_builder_obb"]

    def test_filings_and_ownership_sit_under_the_company(self, app):
        placed = [cell["i"] for cell in app["tabs"]["company"]["layout"]]

        assert "tmx_equity_filings_viewer_obb" in placed
        assert "tmx_equity_ownership_insider_transactions_tmx_obb" in placed

    def test_nothing_the_overview_page_renders_is_laid_out_again(self, app):
        """The overview page already carries the quote, profile, and calendar."""
        placed = {cell["i"] for tab in app["tabs"].values() for cell in tab["layout"]}

        assert placed.isdisjoint(
            {
                "tmx_equity_quote_tmx_obb",
                "tmx_equity_profile_tmx_obb",
                "tmx_equity_calendar_earnings_tmx_obb",
                "tmx_equity_estimates_consensus_tmx_obb",
                "tmx_markets_short_interest_tmx_obb",
                "tmx_equity_ownership_insider_trading_tmx_obb",
                "tmx_etf_info_tmx_obb",
                "tmx_etf_holdings_tmx_obb",
                "tmx_etf_sectors_tmx_obb",
                "tmx_etf_countries_tmx_obb",
            }
        )

    def test_no_two_widgets_share_a_cell(self, app):
        for tab in app["tabs"].values():
            occupied: dict = {}

            for cell in tab["layout"]:
                assert cell["x"] + cell["w"] <= 40, (tab["id"], cell["i"])

                for x in range(cell["x"], cell["x"] + cell["w"]):
                    for y in range(cell["y"], cell["y"] + cell["h"]):
                        assert (x, y) not in occupied, (tab["id"], cell["i"])
                        occupied[x, y] = cell["i"]

    def test_every_placement_is_served_by_the_api(self, app, registry):
        for tab in app["tabs"].values():
            for cell in tab["layout"]:
                assert cell["i"] in registry, cell["i"]

    def test_groups_are_declared_once_at_the_app_level(self, app):
        assert app["groups"]

        for tab in app["tabs"].values():
            assert "groups" not in tab

    def test_every_group_member_takes_the_parameter(self, app, registry):
        for group in app["groups"]:
            assert group["widgetIds"]

            for widget in group["widgetIds"]:
                assert any(
                    param["paramName"] == group["paramName"]
                    for param in registry[widget]["params"]
                ), (group["name"], widget)

    def test_every_group_lives_on_one_tab(self, app):
        for group in app["groups"]:
            members = set(group["widgetIds"])

            assert any(
                members <= {cell["i"] for cell in tab["layout"]}
                for tab in app["tabs"].values()
            ), group["name"]

    def test_every_click_column_writes_to_a_grouped_parameter(self, app, registry):
        """A click has nowhere to write without a group on the parameter."""
        clicked = set()
        placed = {cell["i"] for tab in app["tabs"].values() for cell in tab["layout"]}

        for widget_id in placed:
            table = (registry[widget_id].get("data") or {}).get("table") or {}

            for column in table.get("columnsDefs") or []:
                if column.get("renderFn") != "cellOnClick":
                    continue

                params = column["renderFnParams"]

                assert params["actionType"] == "groupBy"

                name = params["groupBy"]["paramName"]

                assert name == column["field"]
                assert any(
                    group["paramName"] == name and widget_id in group["widgetIds"]
                    for group in app["groups"]
                ), (widget_id, column["field"])

                clicked.add(widget_id)

        assert clicked == {
            "tmx_equity_search_tmx_obb",
            "tmx_etf_search_tmx_obb",
            "tmx_index_available_tmx_obb",
            "tmx_derivatives_futures_instruments_tmx_obb",
            "tmx_fixedincome_prices_tmx_obb",
        }

    def test_every_click_source_hides_the_grouped_parameter(self, app, registry):
        """The source carries the parameter without offering it as an input."""
        for widget_id in (
            "tmx_equity_search_tmx_obb",
            "tmx_etf_search_tmx_obb",
            "tmx_index_available_tmx_obb",
            "tmx_derivatives_futures_instruments_tmx_obb",
            "tmx_fixedincome_prices_tmx_obb",
        ):
            table = registry[widget_id]["data"]["table"]
            field = next(
                column["field"]
                for column in table["columnsDefs"]
                if column.get("renderFn") == "cellOnClick"
            )
            params = {p["paramName"]: p for p in registry[widget_id]["params"]}

            assert params[field]["show"] is False


class TestAssetInfoSections:
    """The sections the overview page is assembled from."""

    def test_a_target_range_is_rendered(self):
        from openbb_tmx.utils.asset_info import _range_row

        assert _range_row("Target Range", None, 5) == ""
        assert "24.00 – 32.00" in _range_row("Target Range", 24.0, 32.0)

    def test_the_short_position_is_rendered(self):
        from openbb_tmx.utils.asset_info import _ownership

        rendered = _ownership(
            [{"period": "3_months", "net_activity": 1000}],
            {"short_interest": 6443193, "change": -12000, "days_to_cover": 2.44},
        )

        assert "Shares Short" in rendered
        assert "Days to Cover" in rendered
        assert "6.44M" in rendered

    def test_the_calendar_carries_earnings_and_dividends(self):
        from openbb_tmx.utils.asset_info import _calendar

        rendered = _calendar(
            [{"report_date": date(2026, 8, 1), "eps_consensus": 0.42}],
            [{"ex_dividend_date": date(2026, 8, 15), "amount": 0.2125}],
        )

        assert "0.42 est" in rendered
        assert "Ex-Dividend 2026-08-15" in rendered
        assert "0.2125" in rendered

    def test_a_symbol_with_no_description_has_no_about(self):
        from openbb_tmx.utils.asset_info import _about

        assert _about({}, {}) == ""

    def test_the_issuer_links_are_rendered(self):
        from openbb_tmx.utils.asset_info import _about

        rendered = _about(
            {
                "long_description": "An airline.",
                "company_url": "https://aircanada.com",
                "email": "ir@aircanada.ca",
            },
            {},
        )

        assert 'href="https://aircanada.com"' in rendered
        assert 'href="mailto:ir@aircanada.ca"' in rendered

    async def test_every_dataset_is_read_at_once(self, monkeypatch):
        from openbb_tmx.utils import asset_info

        asked: list = []

        class Row:
            def __init__(self, **fields):
                self._fields = fields

            def model_dump(self, **kwargs):
                return self._fields

        def answer(name, payload):
            class Fetcher:
                @staticmethod
                async def fetch_data(params, credentials):
                    asked.append(name)

                    if payload is None:
                        raise RuntimeError(f"{name} publishes nothing")

                    return payload

            return Fetcher

        for name, payload in (
            ("equity_quote.TmxEquityQuoteFetcher", [Row(name="Air Canada")]),
            ("equity_profile.TmxEquityProfileFetcher", Row(sector="Industrials")),
            ("equity_historical.TmxEquityHistoricalFetcher", [Row(close=23.27)]),
            ("price_target_consensus.TmxPriceTargetConsensusFetcher", [Row(pt=30.0)]),
            ("insider_trading.TmxInsiderTradingFetcher", [Row(period="3_months")]),
            ("equity_short_interest.TmxShortInterestFetcher", None),
            ("historical_dividends.TmxHistoricalDividendsFetcher", [Row(amount=0.2)]),
            (
                "calendar_earnings.TmxCalendarEarningsFetcher",
                [Row(symbol="AC"), Row(symbol="BCE")],
            ),
            ("etf_info.TmxEtfInfoFetcher", []),
            ("etf_holdings.TmxEtfHoldingsFetcher", []),
            ("etf_sectors.TmxEtfSectorsFetcher", []),
            ("etf_countries.TmxEtfCountriesFetcher", []),
        ):
            module, fetcher = name.split(".")
            monkeypatch.setattr(
                f"openbb_tmx.models.{module}.{fetcher}", answer(name, payload)
            )

        payload = await asset_info._gather("AC")

        assert len(asked) == 12
        assert payload["quote"] == {"name": "Air Canada"}
        assert payload["profile"] == {"sector": "Industrials"}
        assert payload["shorts"] == {}
        assert payload["earnings"] == [{"symbol": "AC"}]
        assert payload["fund"] == {}

    def test_the_page_is_served_over_http(self, monkeypatch):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from openbb_tmx.utils import asset_info

        async def payload(symbol):
            return {**asset_info._empty_payload(), "quote": {"name": "Air Canada"}}

        monkeypatch.setattr(asset_info, "_gather", payload)

        from openbb_tmx.routers.equity import router

        app = FastAPI()
        app.include_router(router.api_router, prefix="/tmx")
        response = TestClient(app).get(
            "/tmx/equity/asset_info/view", params={"symbol": "AC", "theme": "light"}
        )

        assert response.status_code == 200
        assert "Air Canada" in response.text
        assert 'data-theme="light"' in response.text


class TestWorkspaceHandshake:
    """The page negotiates its theme with the Workspace that embeds it."""

    @pytest.fixture(scope="class")
    def script(self):
        """Read the shared connect script."""
        import pathlib

        return pathlib.Path("openbb_tmx/assets/openbb_connect.js").read_text(
            encoding="utf-8"
        )

    def test_the_asset_info_page_announces_itself(self, script):
        assert "openbb-connect" in script
        assert "openbb-params-update" in script
        assert "openbb:widget-params:update" in script

    def test_the_page_repaints_on_a_theme_push(self, script):
        assert 'root.setAttribute("data-theme", theme)' in script
        assert "MutationObserver" in script

    def test_the_theme_is_read_from_the_query_string(self, script):
        """The Workspace serves the page with ?theme=, which is authoritative."""
        assert "/[?&]theme=(light|dark)/i" in script

    async def test_the_script_ships_with_the_page(self, monkeypatch):
        from openbb_tmx.utils import asset_info

        async def payload(symbol):
            return {**asset_info._empty_payload(), "quote": {"name": "Air Canada"}}

        monkeypatch.setattr(asset_info, "_gather", payload)
        html = await asset_info.asset_info_html("AC")

        assert "openbb-connect" in html
        assert html.rstrip().endswith("</body></html>")

    def test_the_builder_announces_itself_and_its_results(self):
        html = build_screener_builder_html("dark")

        assert "openbb-connect" in html
        assert "tmx-screener-results" in html
        assert "openbb-request" in html

    def test_the_builder_repaints_on_a_theme_push(self):
        html = build_screener_builder_html("dark")

        assert "pywry:update-theme" in html
        assert "ag-theme-balham-dark" in html

    def test_the_builder_opens_on_a_screen(self):
        """An empty grid on load reads as broken, so the default screen runs."""
        import pathlib

        script = pathlib.Path("openbb_tmx/assets/screener_builder.js").read_text(
            encoding="utf-8"
        )
        tail = script.rsplit("renderConditions();", 1)[-1]

        assert "apply();" in tail
