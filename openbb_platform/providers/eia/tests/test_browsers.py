"""Tests for the EIA data-browser widgets and reverse proxy."""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
from fastapi import Request

from openbb_us_eia import browsers

MAPS_HTML = """
<ul>
  <li><label for="maps-eia-tab-1"><b>Recent</b> maps</label></li>
  <li><label for="maps-eia-tab-2">Historical maps</label></li>
</ul>
<div class="tab-content">
<h1>Lower 48</h1>
<h2 class="list-header">Overview &amp; boundaries</h2>
<a href="/maps/images/shale_2023.pdf" title="Shale plays, Lower 48 States (12/13/2023)(pdf)">PDF</a>
<a href="/maps/images/shale_2023.jpg" title="Shale plays, Lower 48 States (12/13/2023)(jpg)">JPG</a>
<a href="/maps/images/tight_gas.pdf" title="Major tight gas plays(pdf)">PDF</a>
</div>
<div class="tab-content">
<h2>Historical basins</h2>
<a href="/maps/images/old_map.jpg" title="Historic basin map (6/1/2011)(jpg)">JPG</a>
<a href="/maps/data.zip" title="Ignored (1/1/2011)(zip)">ZIP</a>
<a href="/maps/images/field_maps/app_boe.pdf" title="Historical basins: Western Area BOE (pdf)">BOE</a>
</div>
"""

PROXY_PREFIX = "/api/v1/eia_proxy"
INTERNATIONAL = browsers.EIA_DATA_BROWSERS["international"]["path"]
IMPORTS = browsers.EIA_DATA_BROWSERS["petroleum_imports"]["path"]
ELECTRICITY = browsers.EIA_DATA_BROWSERS["electricity"]["path"]


def make_info(path, query="", method="GET", body=b"", referer="", user=""):
    """Build the request_info mapping the proxy endpoints consume."""
    return {
        "url": f"http://test{path}",
        "query": query,
        "path": path,
        "method": method,
        "body": body,
        "content_type": "application/x-www-form-urlencoded" if body else "",
        "referer": referer,
        "user": user,
    }


@pytest.fixture(autouse=True)
def isolate_state(monkeypatch, tmp_path):
    """Keep every test off the shared caches, disk, and view stores."""
    monkeypatch.setattr(
        "openbb_core.app.utils.get_user_cache_directory",
        lambda: str(tmp_path / "cache"),
    )
    monkeypatch.setattr(browsers, "_MAPS_CATALOG", None)
    stores = (
        browsers._PROXY_CACHE,
        browsers._REDIRECTS,
        browsers._REWRITE_CACHE,
        browsers._TABLE_ROWS,
        browsers._LAST_DATA,
        browsers._VIEW_DATA,
        browsers._CURRENT_VIEW,
        browsers._INTL_LABELS,
        browsers._IMPORTS_LABELS,
    )
    for store in stores:
        store.clear()
    yield
    for store in stores:
        store.clear()


class FakeUpstream:
    """Stand in for eia.gov at the one place the code touches the network."""

    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __call__(self, target):
        self.calls.append(target)
        result = self.responses[target]
        if isinstance(result, BaseException):
            raise result
        body, content_type = result[0], result[1]
        status = result[2] if len(result) > 2 else 200
        landed = result[3] if len(result) > 3 else target
        return body, content_type, status, landed

    def install(self, monkeypatch):
        monkeypatch.setattr(browsers, "_fetch_sync", self)
        return self


class TestRequestInfo:
    """The proxy reads deepcopy-safe primitives off the request."""

    @pytest.mark.asyncio
    async def test_extracts_url_query_path_and_method(self):
        request = Request(
            scope={
                "type": "http",
                "method": "GET",
                "scheme": "http",
                "server": ("test", 80),
                "path": "/api/v1/eia_proxy/coal/",
                "query_string": b"a=1",
                "headers": [(b"x-openbb-user", b"analyst@example.com")],
            }
        )
        info = await browsers.request_info(request)
        assert info["url"] == "http://test/api/v1/eia_proxy/coal/"
        assert info["query"] == "a=1"
        assert info["path"] == "/api/v1/eia_proxy/coal/"
        assert info["method"] == "GET"
        assert "analyst@example.com" not in json.dumps(info, default=str)

    @pytest.mark.asyncio
    async def test_the_user_is_stashed_as_an_opaque_key(self):
        def info_for(headers):
            return browsers.request_info(
                Request(
                    scope={
                        "type": "http",
                        "method": "GET",
                        "scheme": "http",
                        "server": ("test", 80),
                        "path": "/api/v1/coal_browser",
                        "query_string": b"",
                        "headers": headers,
                    }
                )
            )

        alice = (await info_for([(b"x-openbb-user", b"alice@x.com")]))["user"]
        bob = (await info_for([(b"x-openbb-user", b"bob@x.com")]))["user"]
        assert alice and bob and alice != bob
        assert "alice@x.com" not in alice
        assert (await info_for([]))["user"] == ""

    @pytest.mark.asyncio
    async def test_post_body_is_read(self):
        async def receive():
            return {"type": "http.request", "body": b"a=1", "more_body": False}

        request = Request(
            scope={
                "type": "http",
                "method": "POST",
                "scheme": "http",
                "server": ("test", 80),
                "path": "/api/v1/eia_proxy/x",
                "query_string": b"",
                "headers": [(b"content-type", b"application/json")],
            },
            receive=receive,
        )
        info = await browsers.request_info(request)
        assert info["method"] == "POST"
        assert info["body"] == b"a=1"
        assert info["content_type"] == "application/json"

    @pytest.mark.asyncio
    async def test_unreadable_post_body_is_empty(self):
        async def receive():
            raise RuntimeError("disconnected")

        request = Request(
            scope={
                "type": "http",
                "method": "POST",
                "scheme": "http",
                "server": ("test", 80),
                "path": "/api/v1/eia_proxy/x",
                "query_string": b"",
                "headers": [],
            },
            receive=receive,
        )
        assert (await browsers.request_info(request))["body"] == b""


class TestSplitWidgetParams:
    """Widget markers are consumed by the proxy, never forwarded upstream."""

    def test_splits_markers_and_keeps_the_rest(self):
        query = (
            f"obb_theme=dark&obb_browser={INTERNATIONAL}&obb_user=abc123"
            "&obb_view=international%2Fdata&obb_seq=1700&frequency=A&pid=44"
        )
        rest, dark, browser, view, seq, user = browsers._split_widget_params(query)
        assert rest == "frequency=A&pid=44"
        assert dark is True
        assert browser == INTERNATIONAL
        assert view == "international/data"
        assert seq == 1700.0
        assert user == "abc123"

    def test_light_theme_and_unknown_browser_are_dropped(self):
        rest, dark, browser, view, seq, user = browsers._split_widget_params(
            "obb_theme=light&obb_browser=bogus"
        )
        assert rest == ""
        assert dark is False
        assert browser == ""
        assert view == ""
        assert seq == 0.0
        assert user == ""

    def test_a_malformed_sequence_is_ignored(self):
        assert browsers._split_widget_params("obb_seq=nope")[4] == 0.0


class TestDeriveBrowser:
    """Angular SPAs issue untagged requests, so the path must identify the app."""

    def test_maps_app_root_to_browser(self):
        assert browsers._derive_browser("international/api/data/data") == INTERNATIONAL
        assert (
            browsers._derive_browser("states/api/x")
            == (browsers.EIA_DATA_BROWSERS["states"]["path"])
        )

    def test_outlooks_keeps_two_segments(self):
        assert browsers._app_root("outlooks/steo/data/browser/") == "outlooks/steo/"

    def test_unknown_path_has_no_browser(self):
        assert browsers._derive_browser("nowhere/x") == ""


class TestIsDataResponse:
    """Only a view's table payload counts as its data."""

    @pytest.mark.parametrize(
        "target",
        [
            "https://www.eia.gov/international/api/data/data?x=1",
            "https://www.eia.gov/international/api/ranking/latestWorldTop",
            "https://www.eia.gov/coal/data/browser/data/index.php?x=1",
        ],
    )
    def test_table_payloads_are_data(self, target):
        assert browsers.is_data_response(target, "application/json") is True

    @pytest.mark.parametrize(
        "target",
        [
            "https://www.eia.gov/international/api/articles/getLatestArticles",
            "https://www.eia.gov/international/api/countries/data",
            "https://www.eia.gov/states/api/Projects/States/Json/geo.json",
            "https://www.eia.gov/global/x.json",
            "https://www.eia.gov/coal/data/browser/?method=getConfig",
        ],
    )
    def test_config_and_chrome_payloads_are_not_data(self, target):
        assert browsers.is_data_response(target, "application/json") is False

    def test_non_json_is_never_data(self):
        assert browsers.is_data_response("https://www.eia.gov/x", "text/html") is False

    def test_ngqs_report_config_and_report_table_are_distinguished(self):
        base = "https://www.eia.gov/naturalgas/ngqs/data/report"
        assert browsers.is_data_response(base, "application/json") is False
        assert browsers.is_data_response(f"{base}/1", "application/json") is True


class TestRenderedTable:
    """``raw`` serves the table the page has rendered -- the current view itself."""

    ROWS = [
        {"category": "All grades", "2024": None},
        {"category": "World", "2024": None},
        {"category": "Total U.S.", "2024": 2410516.0},
    ]

    @pytest.mark.asyncio
    async def test_the_page_publishes_its_table(self):
        info = make_info(
            "/api/v1/eia_table",
            query=f"obb_browser={IMPORTS}&obb_seq=2000",
            method="POST",
            body=json.dumps(self.ROWS).encode(),
        )
        response = await browsers.eia_table(info)
        assert response.status_code == 204
        assert browsers.get_table_rows(IMPORTS) == self.ROWS

    @pytest.mark.asyncio
    async def test_raw_serves_the_rendered_table_verbatim(self, monkeypatch):
        browsers.set_table_rows(IMPORTS, self.ROWS, 2000)
        spec = browsers.EIA_DATA_BROWSERS["petroleum_imports"]
        assert await browsers.raw_table("petroleum_imports", spec) == self.ROWS

    @pytest.mark.asyncio
    async def test_imports_raw_prefers_the_hierarchical_payload(self, monkeypatch):
        spec = browsers.EIA_DATA_BROWSERS["petroleum_imports"]
        target = f"{browsers._EIA_ORIGIN}/petroleum/imports/browser/data/index.php?x=1"
        payload = {
            "TABLE_DATA": [
                {
                    "seriesID": "PET_IMPORTS.WORLD-RP_3-LSO.A",
                    "data": {"2009": 100, "2011": 300, "2010": 200},
                }
            ]
        }
        FakeUpstream(
            {
                f"{browsers._EIA_ORIGIN}/{browsers._IMPORTS_CONFIG}": (
                    json.dumps(IMPORTS_CONFIG).encode(),
                    "application/json",
                ),
                target: (json.dumps(payload).encode(), "application/json"),
            }
        ).install(monkeypatch)
        browsers._IMPORTS_LABELS.clear()
        browsers.set_table_rows(IMPORTS, [{"category": "Texas", "2009 ": 1}], 2000)
        browsers.set_current_view(spec["path"], "imports/view")
        browsers.set_data_target(
            spec["path"], "imports/view", {"url": target, "method": "GET"}
        )
        rows = await browsers.raw_table("petroleum_imports", spec)
        assert rows[0]["category"] == (
            "Imports of Light Sour from World to PADD3 (Gulf Coast), annual"
        )
        assert rows[0]["origin"] == "World"
        assert rows[0]["destination"] == "PADD3 (Gulf Coast)"
        assert rows[0]["grade"] == "Light Sour"
        assert list(rows[0])[-3:] == ["2009 ", "2010 ", "2011 "]
        browsers._IMPORTS_LABELS.clear()

    @pytest.mark.asyncio
    async def test_a_later_table_replaces_an_earlier_one(self):
        browsers.set_table_rows(IMPORTS, self.ROWS, 2000)
        newer = [{"category": "Light Sweet", "2024": 7.0}]
        browsers.set_table_rows(IMPORTS, newer, 3000)
        assert browsers.get_table_rows(IMPORTS) == newer

    @pytest.mark.asyncio
    async def test_a_table_from_a_view_the_user_left_is_ignored(self):
        browsers.set_table_rows(IMPORTS, self.ROWS, 3000)
        stale = [{"category": "STALE", "2024": 1.0}]
        browsers.set_table_rows(IMPORTS, stale, 1000)
        assert browsers.get_table_rows(IMPORTS) == self.ROWS

    @pytest.mark.asyncio
    async def test_an_unknown_browser_publishes_nothing(self):
        await browsers.eia_table(
            make_info(
                "/api/v1/eia_table",
                query="obb_browser=bogus",
                method="POST",
                body=json.dumps(self.ROWS).encode(),
            )
        )
        assert not browsers._TABLE_ROWS

    @pytest.mark.asyncio
    async def test_a_malformed_body_publishes_nothing(self):
        for body in (b"not json", b"[]", b'["junk"]', b'{"a":1}'):
            await browsers.eia_table(
                make_info(
                    "/api/v1/eia_table",
                    query=f"obb_browser={IMPORTS}",
                    method="POST",
                    body=body,
                )
            )
        assert not browsers._TABLE_ROWS

    def test_the_extractor_is_injected_into_the_page(self):
        page = browsers.rewrite_html("<head></head>", PROXY_PREFIX, browser=IMPORTS)
        assert browsers._table_bridge_js(IMPORTS) in page
        assert "eia:table" in page
        assert "/eia_table" in page
        assert "forEachNodeAfterFilterAndSort" in page

    def test_the_extractor_is_not_injected_without_a_browser(self):
        page = browsers.rewrite_html("<head></head>", PROXY_PREFIX)
        assert "eia:table" not in page

    @pytest.mark.asyncio
    async def test_raw_does_not_fall_back_to_the_default_view(self, monkeypatch):
        spec = browsers.EIA_DATA_BROWSERS["electricity"]
        browsers.set_table_rows(ELECTRICITY, self.ROWS, 2000)

        def unused(_target):
            raise AssertionError("raw must not re-fetch when a table was published")

        monkeypatch.setattr(browsers, "_fetch_sync", unused)
        assert await browsers.raw_table("electricity", spec) == self.ROWS


NODE = shutil.which("node") or "/usr/local/bin/node"

HARNESS = """
var posted = null, sent = null;
var listeners = {};
global.window = global;
global.location = { pathname: "/api/v1/eia_proxy/electricity/data/browser/",
                    search: "", hash: "", origin: "http://test" };
global.document = {
  documentElement: {},
  querySelectorAll: function () { return []; },
};
global.MutationObserver = function () { return { observe: function () {} }; };
global.fetch = function (url, init) {
  sent = {
    url: url,
    body: init && init.body,
    keepalive: !!(init && init.keepalive),
  };
  return { catch: function () {} };
};
window.parent = { postMessage: function (msg) { posted = msg; } };
window.addEventListener = function (name, fn) { listeners[name] = fn; };

__BRIDGE__

__GRID__

setTimeout(function () {
  process.stdout.write(JSON.stringify({ posted: posted, sent: sent }), function () {
    process.exit(0);
  });
}, 1600);
"""

XHR_TAG_HARNESS = """
var beacon = null;
global.window = global;
global.location = {
  pathname: "/api/v1/eia_proxy/totalenergy/data/browser/",
  search: "__SEARCH__", hash: "#/?f=M", origin: "http://test",
  href: "http://test/api/v1/eia_proxy/totalenergy/data/browser/",
};
global.document = { baseURI: location.href };
var store = __STORE__;
global.sessionStorage = {
  getItem: function (k) { return k in store ? store[k] : null; },
  setItem: function (k, v) { store[k] = v; },
};
try { global.navigator = { sendBeacon: function (u) { beacon = u; return true; } }; }
catch (e) { /* node ships a read-only navigator; the beacon falls back to fetch */ }
global.history = { pushState: function () {}, replaceState: function () {} };
global.XMLHttpRequest = function () {};
global.XMLHttpRequest.prototype = { open: function () {} };
global.fetch = function (url) {
  if (typeof url === "string" && url.indexOf("/eia_view") >= 0) beacon = url;
  return { catch: function () {} };
};
window.addEventListener = function () {};

__SCRIPT__

process.stdout.write(JSON.stringify({ beacon: beacon, store: store }));
"""


@pytest.mark.skipif(not Path(NODE).exists(), reason="node is not installed")
class TestProxyRequestTagger:
    """The tagger keeps every proxied request bound to its user across reloads."""

    def run(self, search, store):
        script = (
            browsers._xhr_tag_js("totalenergy/data/browser/", "")
            .replace("<script>", "")
            .replace("</script>", "")
        )
        source = (
            XHR_TAG_HARNESS.replace("__SEARCH__", search)
            .replace("__STORE__", json.dumps(store))
            .replace("__SCRIPT__", script)
        )
        result = subprocess.run(  # noqa: S603
            [NODE, "-e", source],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        return json.loads(result.stdout)

    def test_the_user_key_is_persisted_on_the_first_load(self):
        out = self.run("?obb_theme=dark&obb_user=HASH123", {})
        assert out["store"]["obb_user"] == "HASH123"
        assert "obb_user=HASH123" in out["beacon"]

    def test_the_user_key_survives_a_query_clobbering_navigation(self):
        out = self.run("?tbl=T09.05", {"obb_user": "HASH123"})
        assert "obb_user=HASH123" in out["beacon"]


@pytest.mark.skipif(not Path(NODE).exists(), reason="node is not installed")
class TestHostRestore:
    """The host rebuilds the iframe src from the saved nav, per browser."""

    def run(self, browser, src, nav):
        html = browsers._TEMPLATE.read_text(encoding="utf-8")
        funcs = html[html.index("var storeKey") : html.index("function reportView")]
        data = {"browser": browser, "user": "U9", "src": src}
        store = {f"eia:view:{browser}:U9": json.dumps(nav)}
        source = (
            "global.window = global;\n"
            f"var _store = {json.dumps(store)};\n"
            "global.localStorage = { getItem: function (k) { return _store[k] || null; },"
            " setItem: function () {}, removeItem: function () {} };\n"
            f"var DATA = {json.dumps(data)};\n"
            f"{funcs}\n"
            "process.stdout.write(restoredSrc());"
        )
        return subprocess.run(  # noqa: S603
            [NODE, "-e", source],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        ).stdout

    def test_mer_restores_the_full_state_including_the_range(self):
        out = self.run(
            "total_energy",
            "http://h/api/v1/eia_proxy/totalenergy/data/browser/?obb_theme=dark&obb_user=U9",
            {
                "pathname": "/api/v1/eia_proxy/totalenergy/data/browser/",
                "search": "?tbl=T09.01",
                "hash": "#/?f=M&start=201506&end=202604&charted=1-2",
            },
        )
        assert out.endswith(
            "/totalenergy/data/browser/?obb_theme=dark&obb_user=U9&tbl=T09.01"
            "#/?f=M&start=201506&end=202604&charted=1-2"
        )

    def test_other_browsers_restore_the_full_hash(self):
        out = self.run(
            "electricity",
            "http://h/api/v1/eia_proxy/electricity/data/browser/?obb_theme=dark&obb_user=U9",
            {
                "pathname": "/api/v1/eia_proxy/electricity/data/browser/",
                "search": "",
                "hash": "#/topic/0?agg=2,0,1&fuel=vtvv",
            },
        )
        assert out.endswith("#/topic/0?agg=2,0,1&fuel=vtvv")

    def test_the_frame_is_nudged_to_repaint_the_grid(self):
        html = browsers._TEMPLATE.read_text(encoding="utf-8")
        nudge = html[html.index("function nudge()") : html.index("function ready()")]
        source = (
            "var dispatched = [];\n"
            "global.Event = function (t) { this.type = t; };\n"
            "var frame = { contentWindow: { dispatchEvent: function (e) {"
            " dispatched.push(e.type); } } };\n"
            "global.setTimeout = function (fn) { fn(); };\n"
            f"{nudge}\n"
            "nudge();\n"
            "process.stdout.write(JSON.stringify({ dispatched: dispatched }));"
        )
        out = json.loads(
            subprocess.run(  # noqa: S603
                [NODE, "-e", source],
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            ).stdout
        )
        assert out["dispatched"] == ["resize", "resize", "resize", "resize"]


@pytest.mark.skipif(not Path(NODE).exists(), reason="node is not installed")
class TestSlickGridExtraction:
    """The classic browsers draw with SlickGrid, and raw must read what they drew."""

    GRID = """
    function resolver(field, datum) {
      var path = field.split('.');
      var ret = datum;
      for (var i = 0; i < path.length; i++) {
        ret = ret[path[i]];
        if (!ret || typeof ret == 'undefined') break;
      }
      return ret;
    }
    var descriptionOutputFormatter = function (row, cell, value, columnDef, datum) {
      return datum.CHART_NAME || value;
    };
    var numericalDataFormatter = function (row, cell, value, columnDef, datum) {
      if (!datum.HAS_DATA) return '';
      var ret = isNaN(parseFloat(value))
        ? value
        : Number(value).toFixed(datum.PRECISION !== undefined ? datum.PRECISION : 0)
            .replace(/\\B(?=(\\d{3})+(?!\\d))/g, ',');
      return ret === undefined || ret === '' || ret === null ? '--' : ret;
    };
    var COLUMNS = __COLUMNS__;
    for (var i = 0; i < COLUMNS.length; i++) {
      if (COLUMNS[i].outputFormatter === '@description')
        COLUMNS[i].outputFormatter = descriptionOutputFormatter;
      if (COLUMNS[i].dataFormatter === '@numerical')
        COLUMNS[i].dataFormatter = numericalDataFormatter;
    }
    var OPTIONS = {
      frozenColumn: 2,
      addSpacerColumn: true,
      dataItemColumnValueExtractor: function (item, colDef) {
        if (colDef && colDef.field) return resolver(colDef.field, item);
        return null;
      }
    };
    function Grid(container, data, columns, options) {
      this.data = data; this.columns = columns; this.options = options;
      this.onRendered = { subscribe: function () {} };
    }
    Grid.prototype.getColumns = function () { return this.columns; };
    Grid.prototype.getOptions = function () { return this.options; };
    Grid.prototype.getDataLength = function () { return this.data.length; };
    Grid.prototype.getDataItem = function (i) { return this.data[i]; };
    window.Slick = { Grid: Grid };
    setTimeout(function () {
      new window.Slick.Grid("#g", __DATA__, COLUMNS, OPTIONS);
    }, __DELAY__);
    """

    COLUMNS = [
        {"id": "pinKey", "field": "HAS_DATA", "output": False},
        {
            "id": "description",
            "field": "DESCRIPTION",
            "outputFormatter": "@description",
        },
        {"id": "chart", "field": "HAS_DATA", "output": False},
        {"id": "units", "name": "units", "field": "UNITS", "display": False},
        {
            "id": "source key",
            "name": "source key",
            "field": "SERIES_ID",
            "display": False,
        },
        {
            "id": "200101",
            "name": "Jan 2001",
            "field": "DATA.200101",
            "rseField": "RSE_DATA.200101",
            "dataFormatter": "@numerical",
        },
        {"id": "spacer", "name": " ", "autoWidth": True},
    ]
    DATA = [
        {
            "DESCRIPTION": "United States",
            "LEVEL": 0,
            "CHART_NAME": "United States",
            "SERIES_ID": "ELEC.GEN..M",
            "HAS_DATA": False,
            "PRECISION": 0,
            "DATA": {"200101": "--"},
        },
        {
            "DESCRIPTION": "All fuels",
            "LEVEL": 2,
            "CHART_NAME": "United States : all fuels (utility-scale)",
            "SERIES_ID": "ELEC.GEN.ALL-US-99.M",
            "HAS_DATA": True,
            "PRECISION": 0,
            "UNITS": "thousand megawatthours",
            "DATA": {"200101": 332493.16},
        },
        {
            "DESCRIPTION": "Coal",
            "LEVEL": 3,
            "CHART_NAME": "United States : coal",
            "SERIES_ID": "ELEC.GEN.COW-US-99.M",
            "HAS_DATA": True,
            "PRECISION": 0,
            "UNITS": "thousand megawatthours",
            "DATA": {"200101": 177287.111},
        },
    ]

    ANNUAL_COLUMNS = [
        {"id": "pinKey", "field": "HAS_DATA", "output": False},
        {
            "id": "description",
            "field": "DESCRIPTION",
            "outputFormatter": "@description",
        },
    ] + [
        {
            "id": str(year),
            "name": str(year),
            "field": f"DATA.{year}",
            "dataFormatter": "@numerical",
        }
        for year in (2014, 2015, 2009, 2010)
    ]
    ANNUAL_DATA = [
        {
            "DESCRIPTION": "Total U.S.",
            "LEVEL": 0,
            "CHART_NAME": "Total U.S.",
            "SERIES_ID": "PET_IMPORTS.WORLD-US-ALL.A",
            "HAS_DATA": True,
            "PRECISION": 0,
            "UNITS": "thousand barrels",
            "DATA": {"2009": 100, "2010": 200, "2014": 239554, "2015": 244173},
        },
    ]

    def run(self, data=None, columns=None, delay=120):
        script = browsers._table_bridge_js(ELECTRICITY)
        bridge = script.replace("<script>", "").replace("</script>", "")
        grid = (
            self.GRID.replace(
                "__DATA__", json.dumps(self.DATA if data is None else data)
            )
            .replace(
                "__COLUMNS__",
                json.dumps(self.COLUMNS if columns is None else columns),
            )
            .replace("__DELAY__", str(delay))
        )
        source = HARNESS.replace("__BRIDGE__", bridge).replace("__GRID__", grid)
        with tempfile.TemporaryDirectory() as tmp:
            script_path = Path(tmp) / "harness.js"
            script_path.write_text(source, encoding="utf-8")
            result = subprocess.run(  # noqa: S603
                [NODE, str(script_path)],
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )
        return json.loads(result.stdout)

    def test_the_rendered_grid_is_published_to_the_shell(self):
        posted = self.run()["posted"]
        assert posted["type"] == "eia:table"
        assert posted["rows"] == [
            {"category": "United States", "Jan 2001": None},
            {
                "category": "United States : all fuels (utility-scale)",
                "Jan 2001": 332493.16,
            },
            {"category": "United States : coal", "Jan 2001": 177287.111},
        ]

    def test_the_same_rows_are_posted_to_the_backend(self):
        result = self.run()
        assert result["sent"]["url"].startswith("/api/v1/eia_table?obb_browser=")
        assert json.loads(result["sent"]["body"]) == result["posted"]["rows"]

    def test_a_period_value_is_read_through_its_dotted_field_path(self):
        posted = self.run()["posted"]
        assert [row["Jan 2001"] for row in posted["rows"]] == [
            None,
            332493.16,
            177287.111,
        ]

    def test_full_precision_survives_the_grids_own_formatter(self):
        posted = self.run()["posted"]
        assert posted["rows"][2]["Jan 2001"] == 177287.111

    def test_the_hierarchy_is_the_one_the_grid_renders(self):
        posted = self.run()["posted"]
        assert [row["category"] for row in posted["rows"]] == [
            "United States",
            "United States : all fuels (utility-scale)",
            "United States : coal",
        ]

    def test_only_the_columns_on_screen_are_published(self):
        posted = self.run()["posted"]
        for row in posted["rows"]:
            assert list(row) == ["category", "Jan 2001"]

    def test_an_annual_table_keeps_its_label_column_first(self):
        result = self.run(data=self.ANNUAL_DATA, columns=self.ANNUAL_COLUMNS)
        rows = json.loads(result["sent"]["body"])
        assert list(rows[0]) == ["category", "2009 ", "2010 ", "2014 ", "2015 "]
        assert rows[0]["category"] == "Total U.S."
        assert rows[0]["2014 "] == 239554

    def test_a_row_with_no_data_yields_nulls_not_the_dash(self):
        posted = self.run()["posted"]
        assert posted["rows"][0]["Jan 2001"] is None

    def test_the_post_does_not_use_keepalive(self):
        assert self.run()["sent"]["keepalive"] is False

    def test_a_table_over_the_keepalive_limit_is_posted_whole(self):
        columns = (
            self.COLUMNS[:5]
            + [
                {
                    "id": str(200101 + n),
                    "name": f"period {n}",
                    "field": f"DATA.{200101 + n}",
                    "dataFormatter": "@numerical",
                }
                for n in range(305)
            ]
            + [self.COLUMNS[-1]]
        )
        data = [
            {
                "DESCRIPTION": f"Fuel {r}",
                "CHART_NAME": f"United States : fuel {r}",
                "SERIES_ID": f"ELEC.GEN.F{r}-US-99.M",
                "HAS_DATA": True,
                "PRECISION": 0,
                "DATA": {str(200101 + n): 177287.111 + n for n in range(305)},
            }
            for r in range(21)
        ]
        sent = self.run(data=data, columns=columns)["sent"]
        assert len(sent["body"]) > 64 * 1024
        rows = json.loads(sent["body"])
        assert len(rows) == 21
        assert rows[0]["period 0"] == 177287.111

    def test_a_grid_with_no_rows_publishes_nothing(self):
        assert self.run(data=[])["posted"] is None

    def test_a_grid_built_much_later_is_still_captured(self):
        assert self.run(delay=500)["posted"]["rows"]

    def test_the_page_is_left_holding_a_working_grid(self):
        source = HARNESS.replace(
            "__BRIDGE__",
            browsers._table_bridge_js(ELECTRICITY)
            .replace("<script>", "")
            .replace("</script>", ""),
        ).replace(
            "__GRID__",
            self.GRID.replace("__DATA__", json.dumps(self.DATA))
            .replace("__COLUMNS__", json.dumps(self.COLUMNS))
            .replace("__DELAY__", "120")
            .replace(
                'new window.Slick.Grid("#g", ',
                'var g = new window.Slick.Grid("#g", ',
            )
            .replace(
                "}, 120);",
                "  if (!(g instanceof window.Slick.Grid)) throw new Error('broke instanceof');"
                "  if (g.getDataLength() !== 3) throw new Error('broke the grid');"
                "}, 120);",
            ),
        )
        subprocess.run(  # noqa: S603
            [NODE, "-e", source], capture_output=True, text=True, timeout=30, check=True
        )


SYNC_HARNESS = """
var intervals = [], listeners = {};
global.window = global;
var select = {
  tagName: 'SELECT',
  value: '-1',
  options: [
    { value: '-1', text: 'Select a view' },
    { value: '0', text: 'Imports of all grades to US' },
    { value: '8', text: 'Top 10 light crude oil importing refineries in 2013' },
  ],
};
global.location = {
  pathname: '/api/v1/eia_proxy/petroleum/imports/browser/',
  hash: '#/?vs=PET_IMPORTS.WORLD-US-ALL.A',
};
global.document = {
  getElementsByTagName: function (tag) { return tag === 'select' ? [select] : []; },
};
global.window.addEventListener = function (name, fn) { listeners[name] = fn; };
global.setInterval = function (fn) { intervals.push(fn); return intervals.length; };
var CONFIG = __CONFIG__;
global.fetch = function () {
  return Promise.resolve({ json: function () { return Promise.resolve(CONFIG); } });
};

__SCRIPT__

function tick() { for (var i = 0; i < intervals.length; i++) intervals[i](); }
setTimeout(function () {
  __DRIVER__
  process.stdout.write(JSON.stringify({ value: select.value }));
}, 80);
"""

V0_VS = "PET_IMPORTS.WORLD-US-ALL.A"
V8_VS = "PET_IMPORTS.WORLD-RF_465-O.A~PET_IMPORTS.WORLD-RF_225-O.A"
CONFIG_WITH_VIEWS = {
    "views": [
        {"id": "0", "json": json.dumps({"vs": V0_VS})},
        {
            "id": "8",
            "json": json.dumps({"columnendpoints": "2", "d": "abc", "vs": V8_VS}),
        },
    ]
}
CONFIG_NO_VIEWS = {"status": "OK"}


@pytest.mark.skipif(not Path(NODE).exists(), reason="node is not installed")
class TestFeaturedViewSync:
    """The Featured views select must mirror the view encoded in the live hash."""

    def run(self, driver, config=None):
        script = browsers._VIEW_SELECT_SYNC_JS.replace("<script>", "").replace(
            "</script>", ""
        )
        source = (
            SYNC_HARNESS.replace(
                "__CONFIG__",
                json.dumps(CONFIG_WITH_VIEWS if config is None else config),
            )
            .replace("__SCRIPT__", script)
            .replace("__DRIVER__", driver)
        )
        result = subprocess.run(  # noqa: S603
            [NODE, "-e", source],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        return json.loads(result.stdout)

    def test_the_default_view_is_reflected_on_load(self):
        assert self.run("")["value"] == "0"

    def test_a_view_in_the_hash_is_reflected(self):
        driver = (
            f"location.hash = '#/?d=xyz&f=a&vs=' + encodeURIComponent('{V8_VS}');"
            "tick();"
        )
        assert self.run(driver)["value"] == "8"

    def test_matching_ignores_the_other_view_params(self):
        driver = (
            f"location.hash = '#/?vs=' + encodeURIComponent('{V8_VS}') + '&d=DIFF';"
            "tick();"
        )
        assert self.run(driver)["value"] == "8"

    def test_a_hashchange_event_drives_the_sync(self):
        driver = (
            f"location.hash = '#/?vs=' + encodeURIComponent('{V8_VS}');"
            "listeners['hashchange']();"
        )
        assert self.run(driver)["value"] == "8"

    def test_an_unmatched_state_clears_to_the_placeholder(self):
        driver = "location.hash = '#/?vs=PET_IMPORTS.NO_SUCH_SERIES.A';tick();"
        assert self.run(driver)["value"] == "-1"

    def test_a_browser_without_view_config_is_left_untouched(self):
        driver = "select.value = '0';tick();"
        assert self.run(driver, config=CONFIG_NO_VIEWS)["value"] == "0"

    def test_the_script_is_injected_into_the_classic_browser_page(self):
        page = browsers.rewrite_html(
            "<head></head><body></body>",
            PROXY_PREFIX,
            browser=IMPORTS,
        )
        assert browsers._VIEW_SELECT_SYNC_JS in page


class TestText:
    def test_strips_tags_and_unescapes(self):
        assert browsers._text("<b>A &amp;\n  B</b>") == "A & B"


class TestParseMapsPage:
    def test_groups_formats_by_document(self):
        entries = browsers.parse_maps_page(MAPS_HTML)
        assert len(entries) == 4
        shale = entries[0]
        assert shale["tab"] == "Recent maps"
        assert shale["section"] == "Overview & boundaries"
        assert shale["title"] == "Shale plays, Lower 48 States"
        assert shale["date"] == "12/13/2023"
        assert shale["pdf"] == "/maps/images/shale_2023.pdf"
        assert shale["image"] == "/maps/images/shale_2023.jpg"

    def test_title_without_date_strips_format_suffix(self):
        assert browsers.parse_maps_page(MAPS_HTML)[1] == {
            "tab": "Recent maps",
            "section": "Overview & boundaries",
            "title": "Major tight gas plays",
            "date": "",
            "pdf": "/maps/images/tight_gas.pdf",
        }

    def test_second_tab_and_image_only(self):
        assert browsers.parse_maps_page(MAPS_HTML)[2] == {
            "tab": "Historical maps",
            "section": "Historical basins",
            "title": "Historic basin map",
            "date": "6/1/2011",
            "image": "/maps/images/old_map.jpg",
        }

    def test_section_prefix_stripped_from_title(self):
        assert browsers.parse_maps_page(MAPS_HTML)[3] == {
            "tab": "Historical maps",
            "section": "Historical basins",
            "title": "Western Area BOE",
            "date": "",
            "pdf": "/maps/images/field_maps/app_boe.pdf",
        }

    def test_unsupported_format_skipped(self):
        assert not any(
            entry.get("pdf", "").endswith(".zip")
            for entry in browsers.parse_maps_page(MAPS_HTML)
        )

    def test_anchor_outside_tabs_skipped(self):
        html = '<a href="/maps/x.pdf" title="Loose (1/1/2020)(pdf)">PDF</a>'
        assert browsers.parse_maps_page(html) == []

    def test_more_tabs_than_labels_get_placeholder(self):
        html = (
            '<div class="tab-content">'
            '<a href="/maps/a.pdf" title="A (1/1/2020)(pdf)">PDF</a></div>'
        )
        assert browsers.parse_maps_page(html)[0]["tab"] == "Maps 1"


class TestFetchMapsCatalog:
    @pytest.mark.asyncio
    async def test_fetches_parses_and_caches(self, monkeypatch):
        target = f"{browsers._EIA_ORIGIN}/{browsers.MAPS_PAGE}"
        upstream = FakeUpstream({target: (MAPS_HTML.encode(), "text/html")})
        upstream.install(monkeypatch)
        first = await browsers.fetch_maps_catalog()
        second = await browsers.fetch_maps_catalog()
        assert first is second
        assert len(upstream.calls) == 1
        assert first[0]["title"] == "Shale plays, Lower 48 States"


class TestRewriteHtml:
    """Injected CSS/JS must hide EIA's site chrome without eating its apps."""

    def test_rewrites_root_paths_and_injects_into_head(self):
        html = '<head></head><body><a href="/coal/">x</a><img src="/img.png"/></body>'
        out = browsers.rewrite_html(html, PROXY_PREFIX)
        assert f'"{PROXY_PREFIX}/coal/"' in out
        assert f'"{PROXY_PREFIX}/img.png"' in out
        assert out.index("<style>") < out.index("</head>")

    def test_without_head_prepends_injection(self):
        assert browsers.rewrite_html("<body></body>", "/p").startswith("<style>")

    def test_protocol_relative_untouched(self):
        out = browsers.rewrite_html('<head></head><a href="//cdn/x.js">', "/p")
        assert '"//cdn/x.js"' in out

    def test_absolute_eia_urls_repointed_at_the_proxy(self):
        out = browsers.rewrite_html(
            '<head></head><a href="https://www.eia.gov/coal/">x</a>', PROXY_PREFIX
        )
        assert "https://www.eia.gov/coal/" not in out
        assert f'"{PROXY_PREFIX}/coal/"' in out

    def test_chrome_hidden_but_app_headers_survive(self):
        out = browsers.rewrite_html("<head></head>", PROXY_PREFIX)
        hide = out.split("{display:none!important}", 1)[0]
        assert "header" in hide
        assert "#sticker" in hide
        assert ".l-row.header" not in hide
        assert ".sub-navigation" not in hide
        assert ".title-banner" not in hide

    def test_article_pages_hide_their_own_banner(self):
        out = browsers.rewrite_html("<head></head>", PROXY_PREFIX, article=True)
        assert browsers._ARTICLE_CSS in out

    def test_browser_pages_do_not_get_the_article_chrome(self):
        out = browsers.rewrite_html(
            "<head></head>", PROXY_PREFIX, browser=INTERNATIONAL
        )
        assert browsers._ARTICLE_CSS not in out

    def test_dark_root_background_inverts_to_dark(self):
        out = browsers.rewrite_html("<head></head>", PROXY_PREFIX, dark=True)
        assert "background:#fff!important" in out
        assert "#111418" not in out

    def test_dark_mode_uninverts_country_flags(self):
        out = browsers.rewrite_html("<head></head>", PROXY_PREFIX, dark=True)
        dark = out[out.index("filter:invert(0.92)") :]
        assert dark.index('img[src*=".svg"]') < dark.index('img[src*="flags/"]')

    def test_light_mode_has_no_filter(self):
        out = browsers.rewrite_html("<head></head>", PROXY_PREFIX, dark=False)
        assert "invert(0.92)" not in out

    def test_asset_fixer_injected_for_runtime_root_absolute_images(self):
        out = browsers.rewrite_html("<head></head>", PROXY_PREFIX)
        assert browsers._ASSET_FIX_JS in out

    def test_the_table_bridge_is_bound_to_its_browser(self):
        out = browsers.rewrite_html(
            "<head></head>", PROXY_PREFIX, browser=INTERNATIONAL
        )
        assert f"browser='{INTERNATIONAL}'" in out
        assert "eia:table" in out

    def test_the_tagger_binds_each_request_to_its_view(self):
        out = browsers.rewrite_html(
            "<head></head>", PROXY_PREFIX, browser=INTERNATIONAL
        )
        assert "XMLHttpRequest.prototype.open" in out
        assert "obb_view" in out
        assert "obb_token" not in out

    def test_the_tagger_leaves_the_widgets_own_endpoints_alone(self):
        """A tagged POST to ``/eia_table`` would be proxied to eia.gov."""
        out = browsers.rewrite_html(
            "<head></head>", PROXY_PREFIX, browser=INTERNATIONAL
        )
        assert "var mine=[parts[0]+'/eia_table',parts[0]+'/eia_view'];" in out
        assert (
            "for(var m=0;m<mine.length;m++)if(u.pathname===mine[m])return raw;" in out
        )

    def test_tagger_omitted_without_a_browser(self):
        out = browsers.rewrite_html("<head></head>", PROXY_PREFIX)
        assert "obb_browser" not in out

    def test_analytics_and_akamai_scripts_dropped(self):
        html = (
            "<head>"
            '<script src="https://www.googletagmanager.com/gtag/js?id=X"></script>'
            '<script src="/akam/13/abc" defer></script>'
            "</head>"
        )
        out = browsers.rewrite_html(html, PROXY_PREFIX)
        assert "googletagmanager" not in out
        assert "/akam/" not in out

    @pytest.mark.parametrize(
        ("browser", "css"),
        [
            ("electricity/data/browser/", "_MAP_LAYOUT_CSS"),
            ("coal/data/browser/", "_MAP_LAYOUT_CSS"),
            ("naturalgas/ngqs/", "_NGQS_GRID_CSS"),
            ("states/", "_STATES_CSS"),
            ("international/overview/world", "_INTERNATIONAL_CSS"),
        ],
    )
    def test_per_browser_css_only_reaches_its_own_browser(self, browser, css):
        expected = getattr(browsers, css)
        assert expected in browsers.rewrite_html(
            "<head></head>", PROXY_PREFIX, browser=browser
        )
        assert expected not in browsers.rewrite_html(
            "<head></head>", PROXY_PREFIX, browser="outlooks/steo/data/browser/"
        )


class TestRewrittenCache:
    """Rewritten static assets are cached; the cache is bounded."""

    def test_second_rewrite_is_served_from_cache(self):
        calls = []

        def build():
            calls.append(1)
            return "rewritten"

        key = ("https://t/a.js", "/p")
        assert browsers._rewritten(key, build) == "rewritten"
        assert browsers._rewritten(key, build) == "rewritten"
        assert len(calls) == 1

    def test_cache_is_bounded(self, monkeypatch):
        monkeypatch.setattr(browsers, "_REWRITE_CACHE_MAX", 2)
        for index in range(4):
            browsers._rewritten((f"https://t/{index}.js", "/p"), lambda: "x")
        assert len(browsers._REWRITE_CACHE) <= 2

    @pytest.mark.asyncio
    async def test_spa_bundle_rewrites_only_its_own_app_roots(self, monkeypatch):
        script = b'fetch("/states/api/geo.json");var api="/api/analysis";var s="/";'
        FakeUpstream(
            {
                "https://www.eia.gov/states/main.js": (
                    script,
                    "application/javascript",
                )
            }
        ).install(monkeypatch)
        response = await browsers.eia_proxy(
            "states/main.js", make_info("/api/v1/eia_proxy/states/main.js")
        )
        text = response.body.decode()
        assert f'"{PROXY_PREFIX}/states/api/geo.json"' in text
        assert 'var api="/api/analysis"' in text
        assert 'var s="/"' in text


class TestRedirects:
    """An upstream redirect is mapped back onto the proxy, keeping the markers."""

    def test_redirect_target_keeps_the_theme(self):
        location = browsers._redirect_target(
            PROXY_PREFIX, f"{browsers._EIA_ORIGIN}/coal/?a=1", True
        )
        assert location.startswith(f"{PROXY_PREFIX}/coal/?")
        assert "a=1" in location
        assert "obb_theme=dark" in location

    def test_light_theme_is_carried_through(self):
        location = browsers._redirect_target(
            PROXY_PREFIX, f"{browsers._EIA_ORIGIN}/coal/", False
        )
        assert "obb_theme=light" in location
        assert "obb_token" not in location

    @pytest.mark.asyncio
    async def test_proxy_redirects_the_iframe_to_where_it_landed(self, monkeypatch):
        target = "https://www.eia.gov/from"
        landed = "https://www.eia.gov/to"
        FakeUpstream({target: (b"<head></head>", "text/html", 200, landed)}).install(
            monkeypatch
        )
        response = await browsers.eia_proxy(
            "from", make_info("/api/v1/eia_proxy/from", query="obb_theme=dark")
        )
        assert response.status_code == 307
        assert response.headers["location"].startswith(f"{PROXY_PREFIX}/to?")

    @pytest.mark.asyncio
    async def test_landing_on_the_same_path_is_served_not_redirected(self, monkeypatch):
        target = "https://www.eia.gov/coal/"
        FakeUpstream({target: (b"<head></head>", "text/html", 200, target)}).install(
            monkeypatch
        )
        response = await browsers.eia_proxy(
            "coal/", make_info("/api/v1/eia_proxy/coal/")
        )
        assert response.status_code == 200


class TestProxyPost:
    """NGQS submits its query as a POST, which must be proxied and recorded."""

    @pytest.mark.asyncio
    async def test_post_is_forwarded_with_its_body(self, monkeypatch):
        captured: dict = {}

        def fake_post(target, body, content_type):
            captured.update(target=target, body=body, content_type=content_type)
            return b'{"TABLE_DATA":[]}', "application/json", 200

        monkeypatch.setattr(browsers, "_post_sync", fake_post)
        ngqs = browsers.EIA_DATA_BROWSERS["natural_gas_query"]["path"]
        await browsers.eia_proxy(
            "naturalgas/ngqs/data/report/1",
            make_info(
                "/api/v1/eia_proxy/naturalgas/ngqs/data/report/1",
                query=f"obb_browser={ngqs}",
                method="POST",
                body=b"items=1",
            ),
        )
        assert captured["body"] == b"items=1"
        assert captured["content_type"] == "application/x-www-form-urlencoded"
        assert captured["target"] == (
            "https://www.eia.gov/naturalgas/ngqs/data/report/1"
        )


class TestFetchUpstream:
    """Memory, then disk, then network."""

    @pytest.mark.asyncio
    async def test_caches_successful_fetch_in_memory(self, monkeypatch):
        upstream = FakeUpstream({"https://t/x": (b"payload", "text/plain")})
        upstream.install(monkeypatch)
        assert await browsers._fetch_upstream("https://t/x") == (
            b"payload",
            "text/plain",
        )
        assert await browsers._fetch_upstream("https://t/x") == (
            b"payload",
            "text/plain",
        )
        assert len(upstream.calls) == 1

    @pytest.mark.asyncio
    async def test_non_200_not_cached(self, monkeypatch):
        upstream = FakeUpstream({"https://t/x": (b"gone", "text/plain", 404)})
        upstream.install(monkeypatch)
        await browsers._fetch_upstream("https://t/x")
        await browsers._fetch_upstream("https://t/x")
        assert len(upstream.calls) == 2

    @pytest.mark.asyncio
    async def test_cache_evicts_oldest(self, monkeypatch):
        monkeypatch.setattr(browsers, "_PROXY_CACHE_MAX", 1)
        upstream = FakeUpstream(
            {"https://t/a": (b"a", "text/plain"), "https://t/b": (b"b", "text/plain")}
        )
        upstream.install(monkeypatch)
        await browsers._fetch_upstream("https://t/a")
        await browsers._fetch_upstream("https://t/b")
        assert "https://t/a" not in browsers._PROXY_CACHE
        assert "https://t/b" in browsers._PROXY_CACHE

    @pytest.mark.asyncio
    async def test_expired_entry_refetched(self, monkeypatch):
        upstream = FakeUpstream({"https://t/x": (b"payload", "text/plain")})
        upstream.install(monkeypatch)
        await browsers._fetch_upstream("https://t/x")
        stamp, body, content_type = browsers._PROXY_CACHE["https://t/x"]
        browsers._PROXY_CACHE["https://t/x"] = (
            stamp - browsers._PROXY_CACHE_TTL - 1,
            body,
            content_type,
        )
        await browsers._fetch_upstream("https://t/x")
        assert len(upstream.calls) == 2

    @pytest.mark.asyncio
    async def test_static_asset_persisted_to_disk_and_served_from_it(self, monkeypatch):
        target = "https://t/app.js"
        upstream = FakeUpstream({target: (b"code", "application/javascript")})
        upstream.install(monkeypatch)
        await browsers._fetch_upstream(target)
        body_path, type_path = browsers._cache_paths(target)
        assert body_path.read_bytes() == b"code"
        assert type_path.read_text() == "application/javascript"

        browsers._PROXY_CACHE.clear()
        assert await browsers._fetch_upstream(target) == (
            b"code",
            "application/javascript",
        )
        assert len(upstream.calls) == 1

    @pytest.mark.asyncio
    async def test_html_is_never_written_to_disk(self, monkeypatch):
        target = "https://t/page.html"
        FakeUpstream({target: (b"<html>", "text/html")}).install(monkeypatch)
        await browsers._fetch_upstream(target)
        assert not browsers._cache_paths(target)[0].exists()

    @pytest.mark.asyncio
    async def test_redirect_target_remembered(self, monkeypatch):
        target = "https://t/from"
        landed = "https://t/to"
        FakeUpstream({target: (b"x", "text/html", 200, landed)}).install(monkeypatch)
        await browsers._fetch_upstream(target)
        assert browsers._REDIRECTS[target] == landed


class TestEiaProxy:
    """The proxy rewrites what it must and passes the rest through untouched."""

    @pytest.mark.asyncio
    async def test_html_rewritten_and_query_forwarded(self, monkeypatch):
        upstream = FakeUpstream(
            {
                "https://www.eia.gov/coal/?a=1": (
                    b'<head></head><a href="/x">x</a>',
                    "text/html",
                )
            }
        )
        upstream.install(monkeypatch)
        response = await browsers.eia_proxy(
            "coal/", make_info("/api/v1/eia_proxy/coal/", query="a=1")
        )
        assert f'"{PROXY_PREFIX}/x"' in response.body.decode()
        assert upstream.calls == ["https://www.eia.gov/coal/?a=1"]

    @pytest.mark.asyncio
    async def test_html_is_never_cached_by_the_browser(self, monkeypatch):
        FakeUpstream(
            {"https://www.eia.gov/coal/": (b"<head></head>", "text/html")}
        ).install(monkeypatch)
        response = await browsers.eia_proxy(
            "coal/", make_info("/api/v1/eia_proxy/coal/")
        )
        assert response.headers["Cache-Control"] == "no-store"

    @pytest.mark.asyncio
    async def test_widget_markers_stripped_before_upstream(self, monkeypatch):
        upstream = FakeUpstream(
            {"https://www.eia.gov/coal/?a=1": (b"<head></head>", "text/html")}
        )
        upstream.install(monkeypatch)
        await browsers.eia_proxy(
            "coal/",
            make_info(
                "/api/v1/eia_proxy/coal/",
                query="a=1&obb_theme=dark",
            ),
        )
        assert "obb_" not in upstream.calls[0]

    @pytest.mark.asyncio
    async def test_css_urls_rewritten(self, monkeypatch):
        FakeUpstream(
            {
                "https://www.eia.gov/s.css": (
                    b"body{background:url(/img.png)}",
                    "text/css",
                )
            }
        ).install(monkeypatch)
        response = await browsers.eia_proxy(
            "s.css", make_info("/api/v1/eia_proxy/s.css")
        )
        assert f"url({PROXY_PREFIX}/img.png)".encode() in response.body

    @pytest.mark.asyncio
    async def test_js_spa_roots_rewritten_but_bare_slash_untouched(self, monkeypatch):
        script = b'fetch("/states/api/x");var sep="/";var g="/global/a.js";'
        FakeUpstream(
            {"https://www.eia.gov/app.js": (script, "application/javascript")}
        ).install(monkeypatch)
        response = await browsers.eia_proxy(
            "app.js", make_info("/api/v1/eia_proxy/app.js")
        )
        text = response.body.decode()
        assert f'"{PROXY_PREFIX}/states/api/x"' in text
        assert f'"{PROXY_PREFIX}/global/a.js"' in text
        assert 'sep="/"' in text

    @pytest.mark.asyncio
    async def test_binary_passthrough(self, monkeypatch):
        FakeUpstream(
            {"https://www.eia.gov/m.pdf": (b"%PDF-1.6", "application/pdf")}
        ).install(monkeypatch)
        response = await browsers.eia_proxy(
            "m.pdf", make_info("/api/v1/eia_proxy/m.pdf")
        )
        assert response.body == b"%PDF-1.6"
        assert response.media_type == "application/pdf"

    @pytest.mark.asyncio
    async def test_upstream_error_returns_502(self, monkeypatch):
        FakeUpstream({"https://www.eia.gov/x": RuntimeError("boom")}).install(
            monkeypatch
        )
        response = await browsers.eia_proxy("x", make_info("/api/v1/eia_proxy/x"))
        assert response.status_code == 502
        assert response.body == b"Upstream request failed."
        assert b"boom" not in response.body

    @pytest.mark.asyncio
    async def test_deep_linked_spa_route_still_gets_the_bridge(self, monkeypatch):
        """A deep-linked sub-route is not the root path, but still needs the bridge."""
        target = "https://www.eia.gov/international/overview/USA"
        FakeUpstream({target: (b"<head></head>", "text/html")}).install(monkeypatch)
        response = await browsers.eia_proxy(
            "international/overview/USA",
            make_info("/api/v1/eia_proxy/international/overview/USA"),
        )
        page = response.body.decode()
        assert f"browser='{INTERNATIONAL}'" in page
        assert "/eia_table" in page

    @pytest.mark.asyncio
    async def test_article_pages_get_no_tagger(self, monkeypatch):
        target = "https://www.eia.gov/todayinenergy/detail.php?id=1"
        FakeUpstream({target: (b"<head></head>", "text/html")}).install(monkeypatch)
        response = await browsers.eia_proxy(
            "todayinenergy/detail.php",
            make_info("/api/v1/eia_proxy/todayinenergy/detail.php", query="id=1"),
        )
        assert "obb_browser" not in response.body.decode()


class TestRenderBrowser:
    """Each browser is its own widget, carrying EIA's own description."""

    @pytest.mark.asyncio
    async def test_site_payload(self):
        info = make_info("/api/v1/coal_browser")
        response = await browsers.render_browser("coal", "light", False, info)
        text = response.body.decode()
        assert '"mode": "site"' in text
        assert '"theme": "light"' in text
        assert "eia_proxy/coal/data/browser/" in text
        assert browsers.EIA_DATA_BROWSERS["coal"]["description"][:40] in text

    @pytest.mark.asyncio
    async def test_unknown_browser_falls_back_to_electricity(self):
        info = make_info("/api/v1/bogus_browser")
        response = await browsers.render_browser("bogus", "dark", False, info)
        text = response.body.decode()
        assert "electricity/data/browser/" in text
        assert '"theme": "dark"' in text

    @pytest.mark.asyncio
    async def test_petroleum_imports_lands_on_its_default_view(self):
        info = make_info("/api/v1/petroleum_imports_browser")
        response = await browsers.render_browser(
            "petroleum_imports", "dark", False, info
        )
        assert "%23/?vs=PET_IMPORTS.WORLD-US-ALL.A" in response.body.decode() or (
            "#/?vs=PET_IMPORTS.WORLD-US-ALL.A" in response.body.decode()
        )

    @pytest.mark.asyncio
    async def test_maps_mode_embeds_catalog_and_escapes_html(self, monkeypatch):
        async def fake_catalog():
            return [{"tab": "R", "section": "S", "title": "T<'&", "pdf": "/maps/x.pdf"}]

        monkeypatch.setattr(browsers, "fetch_maps_catalog", fake_catalog)
        info = make_info("/api/v1/maps_browser")
        response = await browsers.render_browser("maps", "dark", False, info)
        text = response.body.decode()
        assert '"mode": "maps"' in text
        assert "\\u003c" in text
        assert "\\u0026" in text
        assert "/maps/x.pdf" in text

    @pytest.mark.asyncio
    async def test_raw_serves_the_table_the_page_published(self, monkeypatch):
        rows = [{"category": "Production", "2023": 1.5}]
        browsers.set_table_rows(INTERNATIONAL, rows, 2000)

        def unused(_target):
            raise AssertionError("raw must not reach upstream")

        monkeypatch.setattr(browsers, "_fetch_sync", unused)
        info = make_info("/api/v1/international_browser")
        response = await browsers.render_browser("international", "dark", True, info)
        assert json.loads(response.body) == rows

    @pytest.mark.asyncio
    async def test_raw_replays_the_view_the_page_is_showing(self, monkeypatch):
        """Grids whose API the page cannot reach are served from their payload."""
        spec = browsers.EIA_DATA_BROWSERS["electricity"]
        target = "https://www.eia.gov/electricity/x?method=getAggregateData"
        payload = json.dumps(
            {
                "TABLEDATA": {
                    "ROWS": [
                        {
                            "DESCRIPTION": "United States",
                            "LEVEL": 0,
                            "UNITS": "thousand megawatthours",
                            "SERIES_ID": "ELEC.GEN.ALL-US-99.M",
                            "DATA": {"200101": 332493.16},
                        }
                    ],
                    "DATACOLUMNS": [200101],
                }
            }
        ).encode()
        FakeUpstream({target: (payload, "application/json")}).install(monkeypatch)
        browsers.set_current_view(spec["path"], "electricity/data/browser/#/topic/0")
        browsers.set_data_target(
            spec["path"],
            "electricity/data/browser/#/topic/0",
            {"url": target, "method": "GET"},
        )
        info = make_info("/api/v1/electricity_browser")
        response = await browsers.render_browser("electricity", "dark", True, info)
        rows = json.loads(response.body)
        assert rows[0]["category"] == "United States"
        assert rows[0]["2001-01"] == 332493.16

    @pytest.mark.asyncio
    async def test_raw_for_maps_returns_the_catalog(self, monkeypatch):
        async def fake_catalog():
            return [{"tab": "R", "section": "S", "title": "T", "pdf": "/x.pdf"}]

        monkeypatch.setattr(browsers, "fetch_maps_catalog", fake_catalog)
        info = make_info("/api/v1/maps_browser")
        response = await browsers.render_browser("maps", "dark", True, info)
        assert json.loads(response.body)[0]["title"] == "T"


class TestWidgetStateRestore:
    """Each user's iframe navigation is stashed and restored across the raw toggle."""

    MER = browsers.EIA_DATA_BROWSERS["total_energy"]["path"]

    def test_state_stores_isolate_users(self):
        browsers.set_current_view(self.MER, "mer#/topic/1", 1000, "alice")
        browsers.set_current_view(self.MER, "mer#/topic/2", 1000, "bob")
        assert browsers.get_current_view(self.MER, "alice") == "mer#/topic/1"
        assert browsers.get_current_view(self.MER, "bob") == "mer#/topic/2"
        assert browsers.get_current_view(self.MER) == ""
        browsers.set_table_rows(self.MER, [{"a": 1}], 1000, "alice")
        assert browsers.get_table_rows(self.MER, "alice") == [{"a": 1}]
        assert browsers.get_table_rows(self.MER, "bob") is None

    @pytest.mark.asyncio
    async def test_the_iframe_restores_the_users_last_view(self):
        view = f"{self.MER}?obb_theme=dark&obb_user=u123#/topic/5?agg=2,0,1"
        browsers.set_current_view(self.MER, view, 2000, "u123")
        info = make_info("/api/v1/total_energy_browser", user="u123")
        response = await browsers.render_browser("total_energy", "dark", False, info)
        text = response.body.decode()
        assert "topic/5" in text
        assert "obb_user=u123" in text

    @pytest.mark.asyncio
    async def test_the_default_view_is_used_without_a_stash(self):
        info = make_info("/api/v1/total_energy_browser", user="u123")
        response = await browsers.render_browser("total_energy", "dark", False, info)
        text = response.body.decode()
        assert f"eia_proxy/{self.MER}" in text
        assert "topic/" not in text

    @pytest.mark.asyncio
    async def test_a_users_view_never_leaks_into_another_users_iframe(self):
        browsers.set_current_view(self.MER, f"{self.MER}#/topic/9", 2000, "alice")
        info = make_info("/api/v1/total_energy_browser", user="bob")
        response = await browsers.render_browser("total_energy", "dark", False, info)
        assert "topic/9" not in response.body.decode()

    @pytest.mark.asyncio
    async def test_the_beacon_keys_the_view_by_user(self):
        await browsers.eia_view(
            make_info(
                "/api/v1/eia_view",
                query=f"obb_browser={self.MER}&obb_user=carol&obb_view=mer%23%2Ftopic%2F7&obb_seq=3000",
            )
        )
        assert browsers.get_current_view(self.MER, "carol") == "mer#/topic/7"
        assert browsers.get_current_view(self.MER, "dave") == ""

    @pytest.mark.asyncio
    async def test_raw_serves_each_user_their_own_table(self, monkeypatch):
        browsers.set_current_view(
            self.MER, f"{self.MER}?tbl=T09.05#/?f=M", 2000, "alice"
        )
        browsers.set_current_view(self.MER, f"{self.MER}?tbl=T01.01#/?f=M", 2000, "bob")

        def table(desc):
            return (
                '<script>var sampleData = {"UNITS":"u","ROWS":'
                '[{"MSN":"X","DESCRIPTION":"'
                + desc
                + '","DATA":{"2024":"1"}}]};</script>'
            ).encode()

        FakeUpstream(
            {
                f"{browsers._EIA_ORIGIN}/{self.MER}?tbl=T09.05": (
                    table("Refiner Prices"),
                    "text/html",
                ),
                f"{browsers._EIA_ORIGIN}/{self.MER}?tbl=T01.01": (
                    table("Primary Energy"),
                    "text/html",
                ),
            }
        ).install(monkeypatch)
        alice = await browsers.render_browser(
            "total_energy", "dark", True, make_info("/api/v1/x", user="alice")
        )
        bob = await browsers.render_browser(
            "total_energy", "dark", True, make_info("/api/v1/x", user="bob")
        )
        assert json.loads(alice.body)[0]["category"] == "Refiner Prices"
        assert json.loads(bob.body)[0]["category"] == "Primary Energy"

    def test_the_bridges_carry_the_user_key(self):
        xhr = browsers._xhr_tag_js(self.MER, "u9")
        tbl = browsers._table_bridge_js(self.MER, "u9")
        assert "user='u9'" in xhr and "obb_user" in xhr
        assert "user='u9'" in tbl and "obb_user" in tbl
        assert "obb_user" in browsers._NAV_GUARD_JS

    def test_the_view_bridge_reports_the_query_string(self):
        assert "search:location.search" in browsers._view_bridge_js()

    def test_a_view_query_keeps_page_params_and_drops_widget_markers(self):
        view = f"{self.MER}?obb_theme=dark&obb_user=X&tbl=T09.05#/?f=M"
        assert browsers._view_query(view) == "tbl=T09.05"
        assert browsers._view_query("") == ""

    @pytest.mark.asyncio
    async def test_the_host_carries_the_user_and_path_for_state_reporting(self):
        info = make_info("/api/v1/total_energy_browser", user="HASH9")
        response = await browsers.render_browser("total_energy", "dark", False, info)
        text = response.body.decode()
        assert '"user": "HASH9"' in text
        assert '"path": "totalenergy/data/browser/"' in text
        assert "reportView" in text and "restoredSrc" in text

    @pytest.mark.asyncio
    async def test_home_is_the_default_view_not_the_restored_one(self):
        browsers.set_current_view(
            self.MER, f"{self.MER}?tbl=T09.05#/?f=M&start=201506", 2000, "u123"
        )
        info = make_info("/api/v1/total_energy_browser", user="u123")
        text = (
            await browsers.render_browser("total_energy", "dark", False, info)
        ).body.decode()
        marker = '<script id="browser-data" type="application/json">'
        blob = text.split(marker, 1)[1].split("</script>", 1)[0]
        data = json.loads(
            blob.replace("\\u003c", "<").replace("\\u003e", ">").replace("\\u0026", "&")
        )
        assert "tbl=T09.05" in data["src"]
        assert "tbl=T09.05" not in data["home"] and "start=" not in data["home"]


class TestRouterRegistration:
    """Every browser is registered as its own Workspace widget."""

    def routes(self):
        return {route.path: route for route in browsers.router._api_router.routes}

    def test_proxy_and_table_sink_are_registered_and_hidden(self):
        routes = self.routes()
        assert "/eia_proxy/{path:path}" in routes
        assert "/eia_table" in routes
        assert routes["/eia_proxy/{path:path}"].include_in_schema is False
        assert routes["/eia_table"].include_in_schema is False

    def test_the_view_beacon_is_registered_and_hidden(self):
        routes = self.routes()
        assert "/eia_view" in routes
        assert routes["/eia_view"].include_in_schema is False

    def test_one_widget_route_per_browser(self):
        routes = self.routes()
        for browser in browsers.EIA_DATA_BROWSERS:
            assert browsers.widget_route(browser) in routes

    @pytest.mark.parametrize("browser", sorted(browsers.EIA_DATA_BROWSERS))
    def test_widget_config_metadata(self, browser):
        route = self.routes()[browsers.widget_route(browser)]
        config = route.openapi_extra["widget_config"]
        spec = browsers.EIA_DATA_BROWSERS[browser]
        assert config["name"] == f"EIA {spec['label']} Browser"
        assert config["description"] == spec["description"]
        assert config["category"] == "EIA"
        assert config["subCategory"] == "Data Browsers"
        assert config["source"] == ["EIA"]
        assert config["widgetId"] == browsers.widget_id(browser)
        assert config["raw"] is True
        params = {p["paramName"]: p for p in config["params"]}
        assert params["theme"]["show"] is False
        assert params["raw"]["show"] is False

    @pytest.mark.parametrize("browser", sorted(browsers.EIA_DATA_BROWSERS))
    def test_the_browser_widget_never_refetches_itself(self, browser):
        config = self.routes()[browsers.widget_route(browser)].openapi_extra[
            "widget_config"
        ]
        assert config["refetchInterval"] is False
        assert config["staleTime"] == 1000


class TestViewTracking:
    """``raw`` must answer for the view on screen, including after click-throughs."""

    OVERVIEW = "international/overview/world"
    COUNTRY = "international/data/country/USA/infographic/total-production"

    def test_raw_follows_the_current_view(self):
        browsers.set_current_view(INTERNATIONAL, self.OVERVIEW)
        browsers.set_data_target(
            INTERNATIONAL, self.OVERVIEW, {"url": "OVERVIEW", "method": "GET"}
        )
        assert browsers.get_data_target(INTERNATIONAL)["url"] == "OVERVIEW"

        browsers.set_current_view(INTERNATIONAL, self.COUNTRY)
        browsers.set_data_target(
            INTERNATIONAL, self.COUNTRY, {"url": "COUNTRY", "method": "GET"}
        )
        assert browsers.get_data_target(INTERNATIONAL)["url"] == "COUNTRY"

    def test_returning_to_a_cached_view_resolves_that_view(self):
        for view, url in ((self.OVERVIEW, "OVERVIEW"), (self.COUNTRY, "COUNTRY")):
            browsers.set_current_view(INTERNATIONAL, view)
            browsers.set_data_target(INTERNATIONAL, view, {"url": url, "method": "GET"})
        browsers.set_current_view(INTERNATIONAL, self.OVERVIEW)
        assert browsers.get_data_target(INTERNATIONAL)["url"] == "OVERVIEW"

    def test_unseen_view_falls_back_to_the_last_request(self):
        browsers.set_data_target(
            INTERNATIONAL, self.OVERVIEW, {"url": "OVERVIEW", "method": "GET"}
        )
        browsers.set_current_view(INTERNATIONAL, "international/rankings/world")
        assert browsers.get_data_target(INTERNATIONAL)["url"] == "OVERVIEW"

    def test_tokenless_spa_requests_resolve_for_a_known_user(self):
        browsers.set_current_view(INTERNATIONAL, self.OVERVIEW)
        browsers.set_data_target(
            INTERNATIONAL, self.OVERVIEW, {"url": "OVERVIEW", "method": "GET"}
        )
        assert browsers.get_data_target(INTERNATIONAL)["url"] == "OVERVIEW"

    def test_nothing_recorded_yields_no_target(self):
        assert browsers.get_data_target(INTERNATIONAL) is None


class TestEiaViewBeacon:
    """The iframe reports each navigation so the server knows the current view."""

    @pytest.mark.asyncio
    async def test_beacon_records_the_view(self):
        info = make_info(
            "/api/v1/eia_view",
            query=f"obb_browser={INTERNATIONAL}&obb_view=international%2Fdata",
            method="POST",
        )
        response = await browsers.eia_view(info)
        assert response.status_code == 204
        assert browsers.get_current_view(INTERNATIONAL) == "international/data"

    @pytest.mark.asyncio
    async def test_beacon_without_a_known_browser_records_nothing(self):
        await browsers.eia_view(
            make_info("/api/v1/eia_view", query="obb_browser=bogus&obb_view=x")
        )
        assert not browsers._CURRENT_VIEW


class TestRawTable:
    """``raw`` replays the recorded request, falling back to the default view."""

    @pytest.mark.asyncio
    async def test_total_energy_falls_back_to_the_inline_table(self, monkeypatch):
        spec = browsers.EIA_DATA_BROWSERS["total_energy"]
        html = (
            '<script>var sampleData = {"UNITS":"u","ROWS":'
            '[{"MSN":"TETCB","DESCRIPTION":"Total","DATA":{"2024":"1"}}]};</script>'
        )
        FakeUpstream(
            {f"{browsers._EIA_ORIGIN}/{spec['path']}": (html.encode(), "text/html")}
        ).install(monkeypatch)
        rows = await browsers.raw_table("total_energy", spec)
        assert rows == [
            {"category": "Total", "units": "u", "source_key": "TETCB", "2024 ": 1.0}
        ]

    @pytest.mark.asyncio
    async def test_falls_back_to_the_browser_default_view(self, monkeypatch):
        spec = browsers.EIA_DATA_BROWSERS["electricity"]
        captured: dict = {}

        def fake_fetch(target):
            captured["target"] = target
            return b'{"TABLEDATA":{"ROWS":[]}}', "application/json", 200, target

        monkeypatch.setattr(browsers, "_fetch_sync", fake_fetch)
        await browsers.raw_table("electricity", spec)
        assert browsers._TABLE_ENDPOINT in captured["target"]
        assert f"method={browsers._TABLE_METHOD}" in captured["target"]

    @pytest.mark.asyncio
    async def test_browser_without_a_default_view_yields_no_rows(self, monkeypatch):
        spec = dict(browsers.EIA_DATA_BROWSERS["electricity"], hash="")
        assert await browsers.raw_table("electricity", spec) == []

    @pytest.mark.asyncio
    async def test_recorded_post_is_replayed_as_a_post(self, monkeypatch):
        spec = browsers.EIA_DATA_BROWSERS["natural_gas_query"]
        captured: dict = {}

        def fake_post(target, body, content_type):
            captured.update(target=target, body=body, content_type=content_type)
            return b'{"TABLE_DATA":[]}', "application/json", 200

        monkeypatch.setattr(browsers, "_post_sync", fake_post)
        browsers.set_current_view(spec["path"], "ngqs")
        browsers.set_data_target(
            spec["path"],
            "ngqs",
            {
                "url": "https://www.eia.gov/naturalgas/ngqs/data/report",
                "method": "POST",
                "body": b"payload",
                "content_type": "application/json",
            },
        )
        assert await browsers.raw_table("natural_gas_query", spec) == []
        assert captured["body"] == b"payload"
        assert captured["content_type"] == "application/json"

    @pytest.mark.asyncio
    async def test_non_json_response_yields_no_rows(self, monkeypatch):
        spec = browsers.EIA_DATA_BROWSERS["electricity"]
        target = "https://www.eia.gov/x"
        FakeUpstream({target: (b"<html>", "text/html")}).install(monkeypatch)
        browsers.set_current_view(spec["path"], "v")
        browsers.set_data_target(spec["path"], "v", {"url": target, "method": "GET"})
        assert await browsers.raw_table("electricity", spec) == []


INTL_FEEDS = {
    "countries": [{"iso": "USA", "name": "United States"}],
    "political_groups": [{"iso": "OPEC", "name": "OPEC"}],
    "units": [{"code": "QBTU", "short_name": "quad Btu"}],
    "products": [
        {"id": 44, "name": "primary energy", "parent": None},
        {"id": 80, "name": "fuel ethanol", "parent": 79},
    ],
    "activities": [{"id": 1, "name": "production"}],
}


def intl_upstream() -> FakeUpstream:
    """Serve every International label feed the pivot needs."""
    origin = browsers._EIA_ORIGIN
    return FakeUpstream(
        {
            f"{origin}/international/api/{feed}/data": (
                json.dumps({"data": records}).encode(),
                "application/json",
            )
            for feed, records in INTL_FEEDS.items()
        }
    )


class TestTotalEnergyState:
    """The MER raw reflects the full tracked state: table, frequency and range."""

    MER = browsers.EIA_DATA_BROWSERS["total_energy"]["path"]
    SPEC = browsers.EIA_DATA_BROWSERS["total_energy"]
    PAGE = (
        '<script>var sampleData = {"UNITS":"u","ROWS":[{"MSN":"X",'
        '"DESCRIPTION":"Series","DATA":{"2018":"10","2019":"11",'
        '"201812":"1.2","201901":"1.3","202604":"9.9"}}]};</script>'
    )

    async def _raw(self, monkeypatch, view, page=None):
        browsers.set_current_view(self.MER, view, 2000, "u1")
        query = browsers._view_query(view)
        url = f"{browsers._EIA_ORIGIN}/{self.MER}" + (f"?{query}" if query else "")
        FakeUpstream(
            {url: ((page if page is not None else self.PAGE).encode(), "text/html")}
        ).install(monkeypatch)
        return await browsers.raw_table("total_energy", self.SPEC, "u1")

    def _periods(self, rows):
        return [k for k in rows[0] if k not in ("category", "units", "source_key")]

    @pytest.mark.asyncio
    async def test_monthly_range_narrows_to_the_slider(self, monkeypatch):
        rows = await self._raw(
            monkeypatch, f"{self.MER}?tbl=T09.01#/?f=M&start=201812&end=201901"
        )
        assert self._periods(rows) == ["2018-12", "2019-01"]

    @pytest.mark.asyncio
    async def test_annual_frequency_keeps_yearly_columns(self, monkeypatch):
        rows = await self._raw(monkeypatch, f"{self.MER}?tbl=T09.01#/?f=A")
        assert self._periods(rows) == ["2018 ", "2019 "]

    @pytest.mark.asyncio
    async def test_no_hash_defaults_to_monthly_full_range(self, monkeypatch):
        rows = await self._raw(monkeypatch, f"{self.MER}?tbl=T09.01")
        assert self._periods(rows) == ["2018-12", "2019-01", "2026-04"]

    @pytest.mark.asyncio
    async def test_a_page_without_inline_data_is_empty(self, monkeypatch):
        assert (
            await self._raw(monkeypatch, f"{self.MER}?tbl=T99", "<html>no</html>") == []
        )

    def test_hash_state_reads_frequency_and_range(self):
        assert browsers._mer_hash_state(
            f"{self.MER}?tbl=T01.01#/?f=M&start=201812&end=202604"
        ) == ("M", "201812", "202604")
        assert browsers._mer_hash_state("no-hash") == ("", "", "")

    def test_filter_skips_non_dict_rows(self):
        payload = {"ROWS": ["junk", {"DATA": {"201812": "1"}}]}
        browsers._filter_mer_payload(payload, "M", "", "")
        assert payload["ROWS"][1]["DATA"] == {"201812": "1"}


class TestInternationalLabelMaps:
    """Names for country, unit, product and activity are fetched once and cached."""

    @pytest.mark.asyncio
    async def test_labels_fetched_once_then_cached(self, monkeypatch):
        upstream = intl_upstream()
        upstream.install(monkeypatch)
        labels = await browsers._intl_label_maps()
        assert labels["region"] == {"USA": "United States", "OPEC": "OPEC"}
        assert labels["unit"] == {"QBTU": "quad Btu"}
        assert labels["product"] == {"44": "primary energy", "80": "fuel ethanol"}
        assert labels["activity"] == {"1": "production"}
        assert labels["parent"] == {"44": None, "80": 79}

        await browsers._intl_label_maps()
        assert len(upstream.calls) == len(INTL_FEEDS)

    @pytest.mark.asyncio
    async def test_unreachable_labels_degrade_to_codes(self, monkeypatch):
        async def fake_fetch(_target):
            raise OSError("offline")

        monkeypatch.setattr(browsers, "_fetch_upstream", fake_fetch)
        assert await browsers._intl_label_maps() == {}

    @pytest.mark.asyncio
    async def test_overview_payload_uses_the_infographic_pivot(self, monkeypatch):
        intl_upstream().install(monkeypatch)
        rows = await browsers._intl_rows(
            {
                "data": [
                    {
                        "series_id": "INTL.44-1-USA-QBTU.A",
                        "iso": "USA",
                        "unit": "QBTU",
                        "frequency": "A",
                        "data": [{"date": 1672531200000, "value": 96.34}],
                    }
                ]
            }
        )
        assert rows == [
            {
                "category": "Production",
                "country": "United States",
                "units": "quad Btu",
                "source_key": "INTL.44-1-USA-QBTU.A",
                "2023 ": 96.34,
            }
        ]

    @pytest.mark.asyncio
    async def test_unrecognised_payload_is_not_labelled(self):
        assert await browsers._intl_rows({"data": [1, 2]}) is None


IMPORTS_CONFIG = {
    "countries": [{"id": "SA", "name": "Saudi Arabia"}],
    "regions": [{"id": "WORLD", "name": "World"}],
    "opecNonOpec": [{"id": "Y", "name": "OPEC"}, {"id": "N", "name": "Non-OPEC"}],
    "refineries": [{"id": "465", "name": "Motiva Port Arthur"}],
    "ports": [{"id": "US", "name": "Total U.S."}],
    "states": [{"id": "TX", "name": "Texas"}],
    "padds": [{"id": "3", "name": "PADD3 (Gulf Coast)"}],
    "grades": [{"id": "LSO", "name": "Light Sour"}],
}


class TestBrowserSpecificLabelling:
    """Imports and NGQS label their tables from sources the payload does not carry."""

    @pytest.mark.asyncio
    async def test_imports_config_fetched_once_then_cached(self, monkeypatch):
        browsers._IMPORTS_LABELS.clear()
        upstream = FakeUpstream(
            {
                f"{browsers._EIA_ORIGIN}/{browsers._IMPORTS_CONFIG}": (
                    json.dumps(IMPORTS_CONFIG).encode(),
                    "application/json",
                )
            }
        )
        upstream.install(monkeypatch)
        labels = await browsers._imports_label_maps()
        assert labels["origin"]["REG"] == {"WORLD": "World"}
        assert labels["origin"]["OPN"]["Y"] == "OPEC"
        assert labels["destination"]["RP"] == {"3": "PADD3 (Gulf Coast)"}
        assert labels["destination"]["RS"] == {"TX": "Texas"}
        assert labels["grade"] == {"LSO": "Light Sour"}

        await browsers._imports_label_maps()
        assert len(upstream.calls) == 1
        browsers._IMPORTS_LABELS.clear()

    @pytest.mark.asyncio
    async def test_unreachable_imports_config_degrades_to_codes(self, monkeypatch):
        browsers._IMPORTS_LABELS.clear()

        async def fake_fetch(_target):
            raise OSError("offline")

        monkeypatch.setattr(browsers, "_fetch_upstream", fake_fetch)
        assert await browsers._imports_label_maps() == {}

    @pytest.mark.asyncio
    async def test_imports_payload_is_labelled(self, monkeypatch):
        browsers._IMPORTS_LABELS.clear()
        FakeUpstream(
            {
                f"{browsers._EIA_ORIGIN}/{browsers._IMPORTS_CONFIG}": (
                    json.dumps(IMPORTS_CONFIG).encode(),
                    "application/json",
                )
            }
        ).install(monkeypatch)
        rows = await browsers._labelled_rows(
            "petroleum_imports",
            {
                "TABLE_DATA": [
                    {
                        "seriesID": "PET_IMPORTS.WORLD-RP_3-LSO.M",
                        "data": {"200901": 9091},
                    }
                ]
            },
        )
        assert rows[0]["category"] == (
            "Imports of Light Sour from World to PADD3 (Gulf Coast), monthly"
        )
        browsers._IMPORTS_LABELS.clear()

    @pytest.mark.asyncio
    async def test_empty_imports_payload_is_not_labelled(self):
        assert (
            await browsers._labelled_rows("petroleum_imports", {"TABLE_DATA": []})
            is None
        )

    @pytest.mark.asyncio
    async def test_international_overview_ranking_is_labelled(self, monkeypatch):
        browsers._INTL_LABELS.clear()
        feeds = {
            "countries": [{"iso": "CHN", "name": "China"}],
            "political_groups": [],
            "units": [{"code": "QBTU", "short_name": "quad Btu"}],
            "products": [{"id": 44, "name": "primary energy", "parent": None}],
            "activities": [{"id": 1, "name": "production"}],
        }
        FakeUpstream(
            {
                f"{browsers._EIA_ORIGIN}/international/api/{feed}/data": (
                    json.dumps({"data": rows}).encode(),
                    "application/json",
                )
                for feed, rows in feeds.items()
            }
        ).install(monkeypatch)
        rows = await browsers._labelled_rows(
            "international",
            {
                "data": [
                    {
                        "productid": 44,
                        "activityid": 1,
                        "frequency": "A",
                        "ranking": 1,
                        "iso": "CHN",
                        "date": "2024-01-01",
                        "value": 130.757,
                        "unitcode": "QBTU",
                        "ug_bmi": 0,
                    },
                    "not a record",
                ]
            },
        )
        assert rows == [
            {
                "category": "Primary energy production",
                "country": "China",
                "rank": 1.0,
                "value": 130.757,
                "units": "quad Btu",
                "period": "2024",
                "source_key": "CHN",
            }
        ]
        browsers._INTL_LABELS.clear()

    @pytest.mark.asyncio
    async def test_ngqs_payload_uses_its_grid_headers(self):
        rows = await browsers._labelled_rows(
            "natural_gas_query",
            {
                "columns": [{"headerName": "Area", "field": "a"}],
                "data": [{"a": "U.S. Total"}],
            },
        )
        assert rows == [{"Area": "U.S. Total"}]

    @pytest.mark.asyncio
    async def test_ngqs_headers_strip_their_html_line_breaks(self):
        rows = await browsers._labelled_rows(
            "natural_gas_query",
            {
                "columns": [
                    {"headerName": "Report<BR>State<BR>", "field": "s"},
                    {"headerName": "Gas<BR>Field Code", "field": "g", "numeric": True},
                ],
                "data": [{"s": "AK", "g": "691992"}],
            },
        )
        assert rows == [{"Report State": "AK", "Gas Field Code": 691992.0}]

    @pytest.mark.asyncio
    async def test_other_browsers_use_the_shared_pivot(self):
        assert await browsers._labelled_rows("electricity", {"TABLEDATA": {}}) is None

    @pytest.mark.asyncio
    async def test_non_dict_payload_is_not_labelled(self):
        assert await browsers._labelled_rows("international", []) is None


class TestPlantAndMineLists:
    """The plant-, mine- and shipment-level views are a record per site."""

    PAYLOAD = {
        "SINGLE_STATE": False,
        "DATA": [
            {
                "id": 66729,
                "Plant Name": "(3K) 59 Hetcheltown Rd",
                "Plant Code": 66729,
                "State": "NY",
                "Sector Name": "Electric utility non-cogen",
                "lat": 42.87657,
                "lon": -73.91048,
                "HAS_DATA": True,
            }
        ],
        "DATA_COLUMNS": ["Plant Name", "Plant Code", "State", "Sector Name"],
        "DESCRIPTION": "List of plants",
    }

    def test_only_the_columns_the_grid_shows_are_kept(self):
        rows = browsers._plant_list_rows(self.PAYLOAD)
        assert rows == [
            {
                "Plant Name": "(3K) 59 Hetcheltown Rd",
                "Plant Code": 66729,
                "State": "NY",
                "Sector Name": "Electric utility non-cogen",
            }
        ]

    def test_the_record_carries_more_than_the_table_does(self):
        rows = browsers._plant_list_rows(self.PAYLOAD)
        assert "lat" not in rows[0]
        assert "HAS_DATA" not in rows[0]

    def test_a_plant_list_is_dispatched_by_rows_from_payload(self):
        rows = browsers.rows_from_payload(self.PAYLOAD)
        assert rows[0]["Plant Name"] == "(3K) 59 Hetcheltown Rd"

    @pytest.mark.parametrize(
        "payload",
        [
            {"DATA": [], "DATA_COLUMNS": ["Plant Name"]},
            {"DATA": ["junk"], "DATA_COLUMNS": ["Plant Name"]},
            {"DATA": [{"a": 1}], "DATA_COLUMNS": [7]},
            {"DATA": [{"a": 1}]},
            {"DATA_COLUMNS": ["Plant Name"]},
        ],
    )
    def test_anything_that_is_not_a_site_list_is_declined(self, payload):
        assert browsers._plant_list_rows(payload) is None

    @pytest.mark.parametrize(
        "method",
        ["method=getPlantList", "method=getMineList", "method=getShipmentList"],
    )
    def test_the_site_lists_count_as_table_data(self, method):
        """These were being discarded, so the plant/mine views served nothing."""
        target = f"https://www.eia.gov/coal/data/browser/data/index.php?{method}"
        assert browsers.is_data_response(target, "application/json") is True


class TestPagedPayload:
    """A view whose data arrives in pages must be replayed to its end."""

    def _payload(self, keys, total):
        return {
            "data": {key: {"2023": [1.0, 1.0]} for key in keys},
            "totalCount": total,
            "recordCount": len(keys),
        }

    @pytest.mark.asyncio
    async def test_every_page_is_followed(self, monkeypatch):
        base = (
            "https://www.eia.gov/international/api/series_data/data"
            "?frequency=A&limit=2&offset=0"
        )
        page2 = (
            "https://www.eia.gov/international/api/series_data/data"
            "?frequency=A&limit=2&offset=2"
        )
        FakeUpstream(
            {
                page2: (
                    json.dumps(self._payload(["c", "d"], 4)).encode(),
                    "application/json",
                )
            }
        ).install(monkeypatch)
        merged = await browsers._all_pages({"url": base}, self._payload(["a", "b"], 4))
        assert sorted(merged["data"]) == ["a", "b", "c", "d"]
        assert merged["recordCount"] == 4

    @pytest.mark.asyncio
    async def test_a_complete_payload_is_left_alone(self, monkeypatch):
        def unused(_target):
            raise AssertionError("a complete payload must not be re-fetched")

        monkeypatch.setattr(browsers, "_fetch_sync", unused)
        payload = self._payload(["a", "b"], 2)
        assert (
            await browsers._all_pages({"url": "https://x/y?limit=2"}, payload)
            is payload
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "url",
        [
            "https://www.eia.gov/x?limit=0",
            "https://www.eia.gov/x?limit=nope",
            "https://www.eia.gov/x",
        ],
    )
    async def test_a_payload_with_no_usable_page_size_is_left_alone(self, url):
        payload = self._payload(["a"], 9)
        assert await browsers._all_pages({"url": url}, payload) is payload

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload",
        [
            {"data": [1, 2]},
            {"data": {"a": {}}, "totalCount": "many"},
            "not a payload",
        ],
    )
    async def test_an_unpaged_shape_is_left_alone(self, payload):
        assert (
            await browsers._all_pages({"url": "https://x?limit=2"}, payload) is payload
        )

    @pytest.mark.asyncio
    async def test_a_broken_page_stops_the_walk(self, monkeypatch):
        base = "https://www.eia.gov/x?limit=2&offset=0"
        FakeUpstream(
            {
                "https://www.eia.gov/x?limit=2&offset=2": (
                    b"not json",
                    "application/json",
                )
            }
        ).install(monkeypatch)
        merged = await browsers._all_pages({"url": base}, self._payload(["a", "b"], 6))
        assert sorted(merged["data"]) == ["a", "b"]

    @pytest.mark.asyncio
    async def test_an_empty_page_stops_the_walk(self, monkeypatch):
        base = "https://www.eia.gov/x?limit=2&offset=0"
        FakeUpstream(
            {
                "https://www.eia.gov/x?limit=2&offset=2": (
                    json.dumps({"data": {}}).encode(),
                    "application/json",
                )
            }
        ).install(monkeypatch)
        merged = await browsers._all_pages({"url": base}, self._payload(["a", "b"], 6))
        assert sorted(merged["data"]) == ["a", "b"]


class TestRecordedViewOrdering:
    """A late report must never drag the current view backwards."""

    def test_an_older_report_does_not_overwrite_a_newer_one(self):
        path = ELECTRICITY
        browsers.set_data_target(path, "view/new", {"url": "NEW"}, 2000)
        browsers.set_data_target(path, "view/old", {"url": "OLD"}, 1000)
        assert browsers.get_data_target(path)["url"] == "NEW"

    @pytest.mark.asyncio
    async def test_a_data_response_records_the_view_that_asked_for_it(
        self, monkeypatch
    ):
        target = "https://www.eia.gov/international/api/data/data?x=1"
        FakeUpstream({target: (b'{"response":{}}', "application/json")}).install(
            monkeypatch
        )
        await browsers.eia_proxy(
            "international/api/data/data",
            make_info(
                "/api/v1/eia_proxy/international/api/data/data",
                query=f"x=1&obb_browser={INTERNATIONAL}"
                "&obb_view=international%2Fdata&obb_seq=5",
            ),
        )
        assert browsers.get_current_view(INTERNATIONAL) == "international/data"
        assert browsers.get_data_target(INTERNATIONAL)["url"] == target


class TestInternationalRawEndToEnd:
    """International's grid API is unreachable, so raw is served from its payload."""

    LABEL_FEEDS = {
        "countries": [{"iso": "USA", "name": "United States"}],
        "political_groups": [],
        "units": [{"code": "QBTU", "short_name": "quad Btu"}],
        "products": [{"id": 44, "name": "primary energy", "parent": None}],
        "activities": [{"id": 1, "name": "production"}],
    }

    def _upstream(self, target, payload):
        responses = {
            f"{browsers._EIA_ORIGIN}/international/api/{feed}/data": (
                json.dumps({"data": rows}).encode(),
                "application/json",
            )
            for feed, rows in self.LABEL_FEEDS.items()
        }
        responses[target] = (json.dumps(payload).encode(), "application/json")
        return FakeUpstream(responses)

    @pytest.mark.asyncio
    async def test_raw_serves_the_view_the_page_is_showing(self, monkeypatch):
        spec = browsers.EIA_DATA_BROWSERS["international"]
        target = f"{browsers._EIA_ORIGIN}/international/api/series_data/data"
        payload = {"data": {"INTL.44-1-USA-QBTU.A": {"2023": [96.0, 96.34]}}}
        self._upstream(target, payload).install(monkeypatch)

        browsers.set_current_view(spec["path"], "international/data/world")
        browsers.set_data_target(
            spec["path"], "international/data/world", {"url": target, "method": "GET"}
        )
        rows = await browsers.raw_table("international", spec)
        assert rows == [
            {
                "category": "Production",
                "country": "United States",
                "units": "quad Btu",
                "source_key": "INTL.44-1-USA-QBTU.A",
                "2023 ": 96.34,
            }
        ]

    @pytest.mark.asyncio
    async def test_the_widget_endpoint_serves_those_rows(self, monkeypatch):
        spec = browsers.EIA_DATA_BROWSERS["international"]
        target = f"{browsers._EIA_ORIGIN}/international/api/series_data/data"
        payload = {"data": {"INTL.44-1-USA-QBTU.A": {"2023": [96.0, 96.34]}}}
        self._upstream(target, payload).install(monkeypatch)
        browsers.set_current_view(spec["path"], "international/data/world")
        browsers.set_data_target(
            spec["path"], "international/data/world", {"url": target, "method": "GET"}
        )

        routes = {r.path: r for r in browsers.router._api_router.routes}
        endpoint = routes["/international_browser"].endpoint
        response = await endpoint(
            theme="dark", raw=True, info=make_info("/api/v1/international_browser")
        )
        assert json.loads(response.body)[0]["country"] == "United States"


class TestMapContrast:
    """The map series is unreadable at eia.gov's own colours on a white page."""

    def _page(self, dark):
        return browsers.rewrite_html(
            "<head></head>", PROXY_PREFIX, dark=dark, browser=INTERNATIONAL
        )

    @pytest.mark.parametrize("dark", [False, True])
    def test_regions_with_no_value_are_given_a_readable_fill(self, dark):
        page = self._page(dark)
        assert (
            ".highcharts-map-series .highcharts-null-point{fill:#dde2e8!important}"
            in page
        )

    @pytest.mark.parametrize("dark", [False, True])
    def test_every_region_is_outlined_so_the_shapes_read(self, dark):
        page = self._page(dark)
        assert (
            ".highcharts-map-series .highcharts-point"
            "{stroke:#98a2b0!important;stroke-width:0.7px!important}" in page
        )

    def test_a_choropleths_own_colours_are_left_alone(self):
        """A shaded map's fill is the data; only no-data regions may be recoloured."""
        page = self._page(False)
        assert ".highcharts-map-series .highcharts-point{fill:" not in page
