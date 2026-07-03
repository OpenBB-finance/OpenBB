"""Tests for the per-district widgets.json / apps.json spec generation."""

import json
from pathlib import Path

import pytest

import openbb_federal_reserve
from openbb_federal_reserve.utils.widgets import build_apps, district_widgets

_PACKAGE = Path(openbb_federal_reserve.__file__).resolve().parent
_ASSETS = _PACKAGE / "assets" / "regional"
_FFIEC_WIDGETS = _PACKAGE / "assets" / "ffiec" / "widgets.json"
_SLUGS = [
    "atlanta",
    "boston",
    "chicago",
    "cleveland",
    "dallas",
    "kc",
    "minneapolis",
    "ny",
    "philadelphia",
    "richmond",
    "sf",
    "stl",
]


@pytest.fixture(scope="module", autouse=True)
def _generate_regional_specs():
    """Generate the per-district spec files on disk if they are absent."""
    if not _ASSETS.exists() or not any(_ASSETS.glob("*_widgets.json")):
        from openbb_federal_reserve.federal_reserve_router import _REGIONAL_DISTRICTS
        from openbb_federal_reserve.utils.widgets import write_specs

        write_specs(_REGIONAL_DISTRICTS)


class TestRegionalSpecs:
    """Tests for the generated per-district spec files."""

    @pytest.mark.parametrize("slug", _SLUGS)
    def test_widgets_valid_relative_and_configured(self, slug):
        """Each widget has a bare endpoint, real params, and table columnsDefs."""
        widgets = json.loads((_ASSETS / f"{slug}_widgets.json").read_text())
        assert widgets
        for widget_id, widget in widgets.items():
            endpoint = widget["endpoint"]
            assert widget_id.startswith(f"{slug}_")
            # Consistent browser grouping: category is always "Federal Reserve"
            # and the sub-category is the branch (never a per-widget theme).
            assert widget["category"] == "Federal Reserve"
            assert widget["subCategory"]
            # Endpoints are the bare command; ids are namespaced by district. The
            # shared publication download/choices endpoints are rebased to a bare
            # district-relative name too, so the merge step resolves them under the
            # district instead of stacking the district path on an absolute path.
            assert "/" not in endpoint
            for param in widget["params"]:
                options_endpoint = param.get("optionsEndpoint")
                if options_endpoint is not None:
                    assert "/" not in options_endpoint
            if widget.get("type") == "multi_file_viewer":
                assert endpoint == "regional_publications_download"
                file_param = next(
                    p for p in widget["params"] if p.get("roles") == ["fileSelector"]
                )
                assert file_param["optionsEndpoint"] == "regional_publications_choices"
                assert file_param["optionsParams"]["district"]
                continue
            # A populated data table carries real column definitions, and a
            # provider-backed command always carries the provider param.
            table = widget.get("data", {}).get("table", {})
            if "columnsDefs" in table:
                assert table["columnsDefs"]
                for column in table["columnsDefs"]:
                    assert column.get("field")
                    assert column.get("cellDataType")
                assert "provider" in {p["paramName"] for p in widget["params"]}

    def test_widget_ids_globally_unique(self):
        """No widget id repeats across any two districts."""
        owner: dict[str, str] = {}
        for slug in _SLUGS:
            widgets = json.loads((_ASSETS / f"{slug}_widgets.json").read_text())
            for widget_id in widgets:
                assert widget_id not in owner, (
                    f"{widget_id} is defined in both {owner.get(widget_id)} and {slug}"
                )
                owner[widget_id] = slug

    @pytest.mark.parametrize("slug", _SLUGS)
    def test_apps_themed_tabs_reference_known_widgets(self, slug):
        """Widgets are split across themed tabs and every one is a known widget."""
        apps = json.loads((_ASSETS / f"{slug}_apps.json").read_text())
        widgets = json.loads((_ASSETS / f"{slug}_widgets.json").read_text())
        assert isinstance(apps, list)
        assert len(apps) == 1
        tabs = apps[0]["tabs"]
        assert tabs
        placed = [w["i"] for tab in tabs.values() for w in tab["layout"]]
        assert placed
        for widget_id in placed:
            assert widget_id in widgets
        # every widget is placed exactly once, across one or more themed tabs.
        assert sorted(placed) == sorted(widgets)


class TestFfiecSpec:
    """Tests for the FFIEC subrouter spec generation and curated app."""

    def test_widgets_generated_with_bare_endpoints(self):
        """Every FFIEC command yields a widget namespaced ``ffiec_*``, bare endpoint."""
        widgets = district_widgets("ffiec")
        assert widgets
        for widget_id, widget in widgets.items():
            assert widget_id.startswith("ffiec_")
            assert "/" not in widget["endpoint"]
            for param in widget["params"]:
                options = param.get("optionsEndpoint")
                if options is not None:
                    assert "/" not in options

    def test_bhcpr_multi_file_viewer_claimed_by_id(self):
        """The BHCPR multi_file_viewer is claimed even with a bare model endpoint."""
        widgets = district_widgets("ffiec")
        bhcpr = widgets["ffiec_bhcpr_report_federal_reserve_obb"]
        assert bhcpr["type"] == "multi_file_viewer"
        assert bhcpr["endpoint"] == "bhcpr_report_download"
        file_param = next(p for p in bhcpr["params"] if p.get("optionsEndpoint"))
        assert file_param["optionsEndpoint"] == "bhcpr_report_choices"

    def test_curated_apps_served_verbatim(self):
        """The ``/ffiec/apps.json`` route serves the hand-curated multi-tab app."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from openbb_federal_reserve import federal_reserve_router

        app = FastAPI()
        app.include_router(federal_reserve_router.router.api_router)
        client = TestClient(app)

        response = client.get("/ffiec/apps.json")
        assert response.status_code == 200
        apps = response.json()
        assert isinstance(apps, list) and len(apps) == 1
        assert apps[0]["name"].startswith("FFIEC")
        # every placed widget id is namespaced to the ffiec subrouter and resolves
        # to a generated widget.
        widgets = json.loads(_FFIEC_WIDGETS.read_text())
        placed = {w["i"] for tab in apps[0]["tabs"].values() for w in tab["layout"]}
        assert placed
        for widget_id in placed:
            assert widget_id.startswith("ffiec_")
            assert widget_id in widgets

    def test_curated_widgets_served_from_ffiec_dir(self):
        """The ``/ffiec/widgets.json`` route serves the curated widget spec."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from openbb_federal_reserve import federal_reserve_router

        app = FastAPI()
        app.include_router(federal_reserve_router.router.api_router)
        client = TestClient(app)

        response = client.get("/ffiec/widgets.json")
        assert response.status_code == 200
        widgets = response.json()
        assert isinstance(widgets, dict)
        assert widgets == json.loads(_FFIEC_WIDGETS.read_text())
        assert len(widgets) == 18
        assert all(widget_id.startswith("ffiec_") for widget_id in widgets)

    @pytest.mark.asyncio
    async def test_curated_apps_fallback_when_missing(self, tmp_path, monkeypatch):
        """A missing curated apps.json yields the empty fallback list."""
        import openbb_federal_reserve.utils.widgets as widgets_module
        from openbb_federal_reserve.utils.widgets import register_spec_routes

        monkeypatch.setattr(
            widgets_module, "_curated_apps_path", lambda slug: tmp_path / "missing.json"
        )
        routes: dict = {}

        class _Api:
            """Capture the route functions the registrar attaches."""

            def add_api_route(self, path, endpoint, **_kwargs):
                """Record the endpoint keyed by its path."""
                routes[path] = endpoint

        class _Router:
            """Stand-in subrouter exposing the api_router."""

            api_router = _Api()

        register_spec_routes(_Router(), "ffiec", "FFIEC", curated_apps=True)
        assert await routes["/apps.json"]() == []


class TestWidgetBuilder:
    """Tests for the live spec builder and served endpoints."""

    def test_columns_and_params_from_official_builder(self):
        """The official build_json output carries real columnsDefs and params."""
        widgets = district_widgets("cleveland")
        components = next(
            w
            for k, w in widgets.items()
            if k.endswith("median_cpi_components") or "median_cpi_components" in k
        )
        fields = {c["field"] for c in components["data"]["table"]["columnsDefs"]}
        assert {"component", "change", "relative_importance"} <= fields
        median = next(
            w
            for k, w in widgets.items()
            if k.endswith("median_cpi_federal_reserve_obb")
        )
        param_names = {p["paramName"] for p in median["params"]}
        assert {"table", "start_date", "end_date"} <= param_names

    def test_endpoints_served(self):
        """The district router serves its widgets.json and apps.json."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from openbb_federal_reserve import federal_reserve_router

        app = FastAPI()
        app.include_router(federal_reserve_router.router.api_router)
        client = TestClient(app)

        widgets_response = client.get("/sf/widgets.json")
        assert widgets_response.status_code == 200
        assert isinstance(widgets_response.json(), dict)

        apps_response = client.get("/sf/apps.json")
        assert apps_response.status_code == 200
        assert isinstance(apps_response.json(), list)


class TestBuildApps:
    """Tests for the per-district app builder, themes, and banner images."""

    def test_uses_district_building_image_and_themes(self):
        """The app icon is the district's own HQ photo; tabs group by theme."""
        widgets = {
            "a_obb": {"subCategory": "Prices"},
            "b_obb": {"subCategory": "Prices"},
            "c_obb": {"subCategory": "Labor"},
        }
        app = build_apps(widgets, "New York", "ny")[0]
        assert app["name"] == "New York Fed"
        assert "Federal_Reserve_Bank_of_New_York" in app["img"]
        assert app["img"] == app["img_dark"] == app["img_light"]
        # the description names this district's signature products, not boilerplate
        assert "Global Supply Chain" in app["description"]
        themes = {
            tab["name"]: [w["i"] for w in tab["layout"]] for tab in app["tabs"].values()
        }
        assert themes == {"Prices": ["a_obb", "b_obb"], "Labor": ["c_obb"]}

    def test_unknown_slug_falls_back_to_system_seal(self):
        """An unknown slug uses the System seal; un-themed widgets go to Overview."""
        app = build_apps({"x_obb": {}}, "Nowhere", "nope")[0]
        assert "Federal_Reserve_System" in app["img"]
        assert "Indicators and surveys" in app["description"]
        assert app["tabs"]["overview"]["layout"][0]["i"] == "x_obb"

    def test_relabel_metadata_normalizes_browser_grouping(self):
        """Every widget gets category 'Federal Reserve' and the branch sub-category."""
        from openbb_federal_reserve.utils.widgets import _relabel_metadata

        widgets = {"a_obb": {"category": "Ny", "subCategory": "Rates & Markets"}}
        _relabel_metadata(widgets, "New York")
        assert widgets["a_obb"]["category"] == "Federal Reserve"
        assert widgets["a_obb"]["subCategory"] == "New York"

    def test_clashing_theme_names_get_unique_tab_ids(self):
        """Two themes that slugify to the same base get distinct tab ids."""
        app = build_apps(
            {"a_obb": {"subCategory": "Prices"}, "b_obb": {"subCategory": "Prices!"}},
            "Nowhere",
            "nope",
        )[0]
        assert set(app["tabs"]) == {"prices", "prices-2"}

    def test_every_widget_is_a_full_width_row_stacked_in_order(self):
        """Each widget claims its own w:40 row, x:0, stacked by widget order."""
        widgets = {
            "chart_obb": {"subCategory": "Rates"},
            "a_obb": {"subCategory": "Rates"},
            "b_obb": {"subCategory": "Rates"},
            "c_obb": {"subCategory": "Rates"},
        }
        layout = build_apps(widgets, "Nowhere", "nope")[0]["tabs"]["rates"]["layout"]
        # the widgets appear in order, one per full-width row, no two-per-row packing
        assert [item["i"] for item in layout] == [
            "chart_obb",
            "a_obb",
            "b_obb",
            "c_obb",
        ]
        for index, item in enumerate(layout):
            assert item["w"] == 40
            assert item["x"] == 0
            assert item["h"] == 18
            assert item["y"] == index * 18
            assert item["state"] == {"params": {}}


class TestDistrictWidgets:
    """Tests for filtering and rewriting the full widget set to one district."""

    def test_rewrites_prefixed_options_endpoint(self):
        """A param's district-prefixed optionsEndpoint is rebased to a bare path."""
        full = {
            "sf_demo_obb": {
                "endpoint": "/sf/demo",
                "params": [{"paramName": "x", "optionsEndpoint": "/sf/choices"}],
            },
            "ny_other_obb": {"endpoint": "/ny/other", "params": []},
        }
        widgets = district_widgets("sf", full)
        assert set(widgets) == {"sf_demo_obb"}
        assert widgets["sf_demo_obb"]["endpoint"] == "demo"
        assert widgets["sf_demo_obb"]["params"][0]["optionsEndpoint"] == "choices"

    def test_rebases_shared_publication_endpoints_to_bare(self):
        """A multi_file_viewer's absolute shared endpoints become bare names.

        The shared download/choices endpoints live on the main router by absolute
        path; rebasing them to a bare district-relative name lets the merge step
        prepend the district path once rather than stacking it on the absolute one.
        """
        full = {
            "sf_publications_obb": {
                "type": "multi_file_viewer",
                "endpoint": "/api/v1/federal_reserve/regional_publications_download",
                "params": [
                    {
                        "paramName": "url",
                        "optionsParams": {"district": "sf"},
                        "optionsEndpoint": (
                            "/api/v1/federal_reserve/regional_publications_choices"
                        ),
                    }
                ],
            },
        }
        widgets = district_widgets("sf", full)
        widget = widgets["sf_publications_obb"]
        assert widget["endpoint"] == "regional_publications_download"
        assert widget["params"][0]["optionsEndpoint"] == "regional_publications_choices"

    def test_leaves_unrelated_absolute_endpoint_untouched(self):
        """A non-shared absolute endpoint is preserved verbatim."""
        full = {
            "sf_demo_obb": {
                "endpoint": "/sf/demo",
                "params": [{"paramName": "x", "optionsEndpoint": "/elsewhere/path"}],
            },
        }
        widgets = district_widgets("sf", full)
        assert widgets["sf_demo_obb"]["params"][0]["optionsEndpoint"] == (
            "/elsewhere/path"
        )


class TestSharedPublicationRoutes:
    """Tests that each district router serves the shared publication endpoints."""

    def test_district_router_resolves_publication_routes(self):
        """The merged district path reaches the shared download/choices routes."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from openbb_federal_reserve import federal_reserve_router

        app = FastAPI()
        app.include_router(
            federal_reserve_router.router.api_router, prefix="/api/v1/federal_reserve"
        )
        client = TestClient(app)

        download = client.post(
            "/api/v1/federal_reserve/boston/regional_publications_download",
            json={"url": []},
        )
        assert download.status_code == 200
        assert download.json() == []

    def test_standalone_district_router_resolves_publication_routes(self):
        """A district router mounted at root still serves the shared routes."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from openbb_federal_reserve import federal_reserve_router

        app = FastAPI()
        app.include_router(federal_reserve_router.boston_router.api_router)
        client = TestClient(app)

        download = client.post("/regional_publications_download", json={"url": []})
        assert download.status_code == 200
        assert download.json() == []


class TestSpecRouteFallback:
    """Tests for the served-spec fallback when committed files are missing."""

    @pytest.mark.asyncio
    async def test_builds_specs_live_when_files_missing(self, tmp_path, monkeypatch):
        """A missing asset file makes the route build the spec from the app."""
        import openbb_federal_reserve.utils.widgets as widgets_module
        from openbb_federal_reserve.utils.widgets import register_spec_routes

        monkeypatch.setattr(widgets_module, "_assets_dir", lambda: tmp_path)
        routes: dict = {}

        class _Api:
            """Capture the route functions the registrar attaches."""

            def add_api_route(self, path, endpoint, **_kwargs):
                """Record the endpoint keyed by its path."""
                routes[path] = endpoint

        class _Router:
            """Stand-in district router exposing the api_router."""

            api_router = _Api()

        register_spec_routes(_Router(), "sf", "San Francisco")
        widgets = await routes["/widgets.json"]()
        apps = await routes["/apps.json"]()
        assert widgets and all(
            w["category"] == "Federal Reserve" for w in widgets.values()
        )
        assert isinstance(apps, list) and apps[0]["name"] == "San Francisco Fed"


class TestWriteSpecs:
    """Tests for generating and writing the committed spec files."""

    def test_writes_widgets_and_apps_per_district(self, tmp_path, monkeypatch):
        """Each district's widgets/apps files are written with normalized category."""
        import openbb_federal_reserve.utils.widgets as widgets_module
        from openbb_federal_reserve.utils.widgets import write_specs

        monkeypatch.setattr(widgets_module, "_assets_dir", lambda: tmp_path)
        written = write_specs([(object(), "sf", "San Francisco")])
        assert set(written) == {"sf_widgets.json", "sf_apps.json"}
        widgets = json.loads((tmp_path / "sf_widgets.json").read_text())
        assert widgets and all(
            w["category"] == "Federal Reserve" for w in widgets.values()
        )
        apps = json.loads((tmp_path / "sf_apps.json").read_text())
        assert apps[0]["name"] == "San Francisco Fed"
