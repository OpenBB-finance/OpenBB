"""Tests for the packaged Workspace app definitions."""

import asyncio
import json
from pathlib import Path

import pytest
import openbb_government_us

from openbb_government_us.congress.congress_router import get_congress_gov_apps_json
from openbb_government_us.treasury.treasury_router import get_us_treasury_apps_json
from openbb_government_us.usda.usda_router import get_usda_apps_json

PACKAGE_ROOT = Path(openbb_government_us.__file__).parent

APPS = {
    "congress": (
        get_congress_gov_apps_json,
        PACKAGE_ROOT / "congress/assets/apps.json",
    ),
    "treasury": (
        get_us_treasury_apps_json,
        PACKAGE_ROOT / "treasury/assets/apps.json",
    ),
    "usda": (
        get_usda_apps_json,
        PACKAGE_ROOT / "usda/assets/apps.json",
    ),
}


class TestAppsJsonAssets:
    """Tests for the packaged app definition files."""

    @pytest.mark.parametrize("agency", sorted(APPS))
    def test_asset_exists_and_parses(self, agency):
        """Each agency ships a parseable app definition."""
        _, path = APPS[agency]
        assert path.exists(), f"{agency} is missing its apps.json asset"
        apps = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(apps, list)
        assert len(apps) == 1

    @pytest.mark.parametrize("agency", sorted(APPS))
    def test_required_keys(self, agency):
        """Each app carries the keys Workspace requires."""
        _, path = APPS[agency]
        app = json.loads(path.read_text(encoding="utf-8"))[0]
        for key in ("name", "img", "img_dark", "img_light", "description", "tabs"):
            assert key in app, f"{agency} app is missing {key}"
        assert app["tabs"], f"{agency} app has no tabs"

    @pytest.mark.parametrize("agency", sorted(APPS))
    def test_tab_ids_match_their_keys(self, agency):
        """Each tab's id matches the key it is stored under."""
        _, path = APPS[agency]
        app = json.loads(path.read_text(encoding="utf-8"))[0]
        for key, tab in app["tabs"].items():
            assert tab["id"] == key
            assert tab["name"]
            assert tab["layout"]

    @pytest.mark.parametrize("agency", sorted(APPS))
    def test_layout_entries_are_well_formed(self, agency):
        """Every widget in a layout carries an id and a grid position."""
        _, path = APPS[agency]
        app = json.loads(path.read_text(encoding="utf-8"))[0]
        for tab in app["tabs"].values():
            for widget in tab["layout"]:
                for key in ("i", "x", "y", "w", "h"):
                    assert key in widget, f"{agency} widget missing {key}"
                assert widget["w"] > 0
                assert widget["h"] > 0

    @pytest.mark.parametrize("agency", sorted(APPS))
    def test_widget_ids_are_namespaced(self, agency):
        """Widget ids follow the router's generated naming."""
        prefix = {
            "congress": "uscongress_",
            "treasury": "ustreasury_",
            "usda": "usda_",
        }[agency]
        _, path = APPS[agency]
        app = json.loads(path.read_text(encoding="utf-8"))[0]
        for tab in app["tabs"].values():
            for widget in tab["layout"]:
                assert widget["i"].startswith(prefix)
                assert widget["i"].endswith("_obb")


class TestWidgetConfigs:
    """Tests for the generated Workspace widget configs."""

    @staticmethod
    def _widgets():
        """Build the widget configs the Workspace consumes."""
        import os

        os.environ["OPENBB_API_AUTH"] = "false"
        from openbb_core.api.rest_api import app
        from openbb_platform_api.utils.widgets import build_json

        return build_json(app.openapi(), [])

    def test_multiple_is_only_set_on_text_params(self):
        """Workspace rejects 'multiple' on any param that is not text.

        The platform sets multiple only after forcing a param's type to
        text, so a widget_config that overrides the type must not leave
        the flag behind.
        """
        offenders = [
            f"{widget_id}[{param.get('paramName')}] type={param.get('type')!r}"
            for widget_id, config in self._widgets().items()
            for param in config.get("params") or []
            if param.get("multiple") is True and param.get("type") != "text"
        ]
        assert not offenders

    def test_bell_report_commodity_is_an_endpoint_multiselect(self):
        """The Bell Report commodity picker is a multi-select endpoint param."""
        params = {
            p.get("paramName"): p
            for p in self._widgets()["usda_bell_report_custom_obb"]["params"]
        }
        commodity = params["commodity_code"]
        assert commodity["type"] == "endpoint"
        assert commodity["multiSelect"] is True
        assert "multiple" not in commodity
        assert commodity["optionsEndpoint"].endswith("/usda/bell_report_commodities")
        assert params["week_ending"]["optionsEndpoint"].endswith(
            "/usda/bell_report_weeks"
        )

    @pytest.mark.parametrize("agency", sorted(APPS))
    def test_saved_state_params_exist_on_the_widget(self, agency):
        """A tab's saved params must all exist on the widget it configures."""
        widgets = self._widgets()
        _, path = APPS[agency]
        app = json.loads(path.read_text(encoding="utf-8"))[0]
        offenders = [
            f"{tab['id']}: {item['i']}[{name}]"
            for tab in app["tabs"].values()
            for item in tab["layout"]
            for name in ((item.get("state") or {}).get("params") or {})
            if name
            not in {
                param.get("paramName")
                for param in (widgets.get(item["i"]) or {}).get("params") or []
            }
        ]
        assert not offenders

    def test_multi_file_viewers_declare_a_file_selector(self):
        """Workspace requires an endpoint param with the fileSelector role."""
        offenders = [
            widget_id
            for widget_id, config in self._widgets().items()
            if config.get("type") == "multi_file_viewer"
            and not any(
                param.get("type") == "endpoint"
                and "fileSelector" in (param.get("roles") or [])
                for param in config.get("params") or []
            )
        ]
        assert not offenders

    def test_bell_report_file_selector_cascades_from_the_pickers(self):
        """The file selector's options follow the commodity and week pickers."""
        params = {
            p.get("paramName"): p
            for p in self._widgets()["usda_bell_report_custom_obb"]["params"]
        }
        urls = params["urls"]
        assert urls["roles"] == ["fileSelector"]
        assert urls["show"] is False
        assert urls["multiSelect"] is True
        assert urls["optionsEndpoint"].endswith("/usda/bell_report_urls")
        assert urls["optionsParams"] == {
            "commodity_code": "$commodity_code",
            "week_ending": "$week_ending",
        }


class TestAppsJsonEndpoints:
    """Tests for the endpoints that serve the app definitions."""

    @pytest.mark.parametrize("agency", sorted(APPS))
    def test_endpoint_returns_the_asset(self, agency):
        """The endpoint serves the packaged file verbatim."""
        endpoint, path = APPS[agency]
        served = asyncio.run(endpoint())
        assert served == json.loads(path.read_text(encoding="utf-8"))

    @pytest.mark.parametrize("agency", sorted(APPS))
    def test_endpoint_returns_empty_when_the_asset_is_unreadable(
        self, agency, monkeypatch
    ):
        """An unreadable asset yields an empty list rather than an error."""
        endpoint, _ = APPS[agency]

        def _raise(*args, **kwargs):
            raise OSError("unreadable")

        monkeypatch.setattr(Path, "open", _raise)
        assert asyncio.run(endpoint()) == []
