"""Tests for the EIA data-browser widgets and reverse proxy."""

import json

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
TOKEN = "a" * 32
INTERNATIONAL = browsers.EIA_DATA_BROWSERS["international"]["path"]


def make_info(path, query="", method="GET", body=b"", user="", referer=""):
    """Build the request_info mapping the proxy endpoints consume."""
    return {
        "url": f"http://test{path}",
        "query": query,
        "path": path,
        "method": method,
        "body": body,
        "content_type": "application/x-www-form-urlencoded" if body else "",
        "user": user,
        "referer": referer,
    }


@pytest.fixture(autouse=True)
def isolate_state(monkeypatch, tmp_path):
    """Keep every test off the shared caches, disk, and view stores."""
    monkeypatch.setattr(browsers, "_CACHE_DIR", tmp_path / "cache")
    browsers._PROXY_CACHE.clear()
    browsers._REDIRECTS.clear()
    browsers._REWRITE_CACHE.clear()
    browsers._LAST_DATA.clear()
    browsers._VIEW_DATA.clear()
    browsers._CURRENT_VIEW.clear()
    monkeypatch.setattr(browsers, "_MAPS_CATALOG", None)
    browsers._INTL_LABELS.clear()
    yield
    browsers._INTL_LABELS.clear()
    browsers._PROXY_CACHE.clear()
    browsers._REDIRECTS.clear()
    browsers._REWRITE_CACHE.clear()
    browsers._LAST_DATA.clear()
    browsers._VIEW_DATA.clear()
    browsers._CURRENT_VIEW.clear()


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


class TestUserToken:
    """Identities are reduced to opaque tokens; raw identity never survives."""

    def test_token_is_opaque_and_stable(self):
        token = browsers.user_token("analyst@example.com")
        assert browsers._TOKEN_RE.match(token)
        assert token == browsers.user_token("analyst@example.com")
        assert "analyst@example.com" not in token

    def test_distinct_identities_get_distinct_tokens(self):
        assert browsers.user_token("a@x.com") != browsers.user_token("b@x.com")

    def test_empty_identity_yields_no_token(self):
        assert browsers.user_token("") == ""

    def test_malformed_token_is_rejected(self):
        assert browsers._clean_token("not-a-token") == ""
        assert browsers._clean_token("") == ""
        assert browsers._clean_token(TOKEN) == TOKEN


class TestSalt:
    """The token salt survives restarts, so a user's recorded views survive too."""

    def test_existing_salt_is_reused(self, monkeypatch, tmp_path):
        salt_file = tmp_path / ".user_salt"
        salt_file.write_bytes(b"S" * 32)
        monkeypatch.setattr(browsers.Path, "home", staticmethod(lambda: tmp_path))
        monkeypatch.setattr(
            browsers, "_load_or_create_salt", browsers._load_or_create_salt
        )
        target = tmp_path / ".openbb_platform" / "cache" / "eia_proxy"
        target.mkdir(parents=True)
        (target / ".user_salt").write_bytes(b"S" * 32)
        assert browsers._load_or_create_salt() == b"S" * 32

    def test_salt_is_created_and_persisted_when_absent(self, monkeypatch, tmp_path):
        monkeypatch.setattr(browsers.Path, "home", staticmethod(lambda: tmp_path))
        salt = browsers._load_or_create_salt()
        assert len(salt) == 32
        written = tmp_path / ".openbb_platform" / "cache" / "eia_proxy" / ".user_salt"
        assert written.read_bytes() == salt
        assert browsers._load_or_create_salt() == salt

    def test_wrong_length_salt_is_replaced(self, monkeypatch, tmp_path):
        monkeypatch.setattr(browsers.Path, "home", staticmethod(lambda: tmp_path))
        target = tmp_path / ".openbb_platform" / "cache" / "eia_proxy"
        target.mkdir(parents=True)
        (target / ".user_salt").write_bytes(b"short")
        assert len(browsers._load_or_create_salt()) == 32

    def test_unwritable_home_still_yields_a_salt(self, monkeypatch, tmp_path):
        blocker = tmp_path / "file"
        blocker.write_text("not a directory")
        monkeypatch.setattr(browsers.Path, "home", staticmethod(lambda: blocker))
        assert len(browsers._load_or_create_salt()) == 32


class TestRequestInfo:
    """The proxy reads deepcopy-safe primitives off the request."""

    @pytest.mark.asyncio
    async def test_extracts_url_query_path_and_identity(self):
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
        assert info["user"] == browsers.user_token("analyst@example.com")
        assert "analyst@example.com" not in json.dumps(info, default=str)

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
            f"obb_theme=dark&obb_token={TOKEN}&obb_browser={INTERNATIONAL}"
            "&obb_view=international%2Fdata&frequency=A&pid=44"
        )
        rest, dark, token, browser, view = browsers._split_widget_params(query)
        assert rest == "frequency=A&pid=44"
        assert dark is True
        assert token == TOKEN
        assert browser == INTERNATIONAL
        assert view == "international/data"

    def test_light_theme_and_unknown_browser_are_dropped(self):
        rest, dark, token, browser, view = browsers._split_widget_params(
            "obb_theme=light&obb_browser=bogus&obb_token=nope"
        )
        assert rest == ""
        assert dark is False
        assert token == ""
        assert browser == ""
        assert view == ""


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


class TestViewTracking:
    """``raw`` must answer for the view on screen, including after click-throughs."""

    OVERVIEW = "international/overview/world"
    COUNTRY = "international/data/country/USA/infographic/total-production"

    def test_raw_follows_the_current_view(self):
        browsers.set_current_view(TOKEN, INTERNATIONAL, self.OVERVIEW)
        browsers.set_data_target(
            TOKEN, INTERNATIONAL, self.OVERVIEW, {"url": "OVERVIEW", "method": "GET"}
        )
        assert browsers.get_data_target(TOKEN, INTERNATIONAL)["url"] == "OVERVIEW"

        browsers.set_current_view(TOKEN, INTERNATIONAL, self.COUNTRY)
        browsers.set_data_target(
            TOKEN, INTERNATIONAL, self.COUNTRY, {"url": "COUNTRY", "method": "GET"}
        )
        assert browsers.get_data_target(TOKEN, INTERNATIONAL)["url"] == "COUNTRY"

    def test_returning_to_a_cached_view_resolves_that_view(self):
        for view, url in ((self.OVERVIEW, "OVERVIEW"), (self.COUNTRY, "COUNTRY")):
            browsers.set_current_view(TOKEN, INTERNATIONAL, view)
            browsers.set_data_target(
                TOKEN, INTERNATIONAL, view, {"url": url, "method": "GET"}
            )
        browsers.set_current_view(TOKEN, INTERNATIONAL, self.OVERVIEW)
        assert browsers.get_data_target(TOKEN, INTERNATIONAL)["url"] == "OVERVIEW"

    def test_unseen_view_falls_back_to_the_last_request(self):
        browsers.set_data_target(
            TOKEN, INTERNATIONAL, self.OVERVIEW, {"url": "OVERVIEW", "method": "GET"}
        )
        browsers.set_current_view(TOKEN, INTERNATIONAL, "international/rankings/world")
        assert browsers.get_data_target(TOKEN, INTERNATIONAL)["url"] == "OVERVIEW"

    def test_tokenless_spa_requests_resolve_for_a_known_user(self):
        browsers.set_current_view("", INTERNATIONAL, self.OVERVIEW)
        browsers.set_data_target(
            "", INTERNATIONAL, self.OVERVIEW, {"url": "OVERVIEW", "method": "GET"}
        )
        assert browsers.get_data_target(TOKEN, INTERNATIONAL)["url"] == "OVERVIEW"

    def test_nothing_recorded_yields_no_target(self):
        assert browsers.get_data_target(TOKEN, INTERNATIONAL) is None

    def test_entries_expire(self, monkeypatch):
        monkeypatch.setattr(browsers, "_VIEW_TTL", -1.0)
        browsers.set_current_view(TOKEN, INTERNATIONAL, self.OVERVIEW)
        browsers.set_data_target(
            TOKEN, INTERNATIONAL, self.OVERVIEW, {"url": "OVERVIEW", "method": "GET"}
        )
        assert browsers.get_current_view(TOKEN, INTERNATIONAL) == ""
        assert browsers.get_data_target(TOKEN, INTERNATIONAL) is None

    def test_another_users_expired_entry_is_swept_on_write(self, monkeypatch):
        stale = "1" * 32
        monkeypatch.setattr(browsers, "_VIEW_TTL", -1.0)
        browsers.set_current_view(stale, INTERNATIONAL, self.OVERVIEW)
        browsers.set_data_target(
            stale, INTERNATIONAL, self.OVERVIEW, {"url": "STALE", "method": "GET"}
        )
        assert (stale, INTERNATIONAL) in browsers._CURRENT_VIEW

        monkeypatch.setattr(browsers, "_VIEW_TTL", 3600.0)
        browsers.set_current_view(TOKEN, INTERNATIONAL, self.OVERVIEW)
        browsers.set_data_target(
            TOKEN, INTERNATIONAL, self.OVERVIEW, {"url": "FRESH", "method": "GET"}
        )
        assert (stale, INTERNATIONAL) not in browsers._CURRENT_VIEW
        assert (stale, INTERNATIONAL) not in browsers._LAST_DATA
        assert browsers.get_data_target(TOKEN, INTERNATIONAL)["url"] == "FRESH"

    def test_stores_are_capped_across_users(self, monkeypatch):
        monkeypatch.setattr(browsers, "_VIEW_STATE_MAX", 2)
        for index in range(5):
            token = f"{index:032x}"
            browsers.set_current_view(token, INTERNATIONAL, f"view/{index}")
            browsers.set_data_target(
                token, INTERNATIONAL, f"view/{index}", {"url": "U", "method": "GET"}
            )
        assert len(browsers._CURRENT_VIEW) <= 2
        assert len(browsers._LAST_DATA) <= 2
        assert len(browsers._VIEW_DATA) <= 2

    def test_widget_context_reads_token_and_browser_from_referer(self):
        referer = f"http://t/api/v1/eia_proxy/{INTERNATIONAL}?obb_token={TOKEN}"
        assert browsers.widget_context(referer) == (TOKEN, INTERNATIONAL)

    def test_widget_context_ignores_foreign_referers(self):
        assert browsers.widget_context("http://elsewhere/x") == ("", "")


class TestEiaViewBeacon:
    """The iframe reports each navigation so the server knows the current view."""

    @pytest.mark.asyncio
    async def test_beacon_records_the_view(self):
        info = make_info(
            "/api/v1/eia_view",
            query=f"obb_browser={INTERNATIONAL}&obb_view=international%2Fdata"
            f"&obb_token={TOKEN}",
            method="POST",
        )
        response = await browsers.eia_view(info)
        assert response.status_code == 204
        assert browsers.get_current_view(TOKEN, INTERNATIONAL) == "international/data"

    @pytest.mark.asyncio
    async def test_beacon_without_a_known_browser_records_nothing(self):
        await browsers.eia_view(
            make_info("/api/v1/eia_view", query="obb_browser=bogus&obb_view=x")
        )
        assert not browsers._CURRENT_VIEW


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

    def test_xhr_tagger_carries_token_browser_and_view(self):
        out = browsers.rewrite_html(
            "<head></head>", PROXY_PREFIX, user=TOKEN, browser=INTERNATIONAL
        )
        assert f"browser='{INTERNATIONAL}'" in out
        assert f"token='{TOKEN}'" in out
        assert "obb_view" in out

    def test_tagger_omitted_without_a_browser(self):
        out = browsers.rewrite_html("<head></head>", PROXY_PREFIX)
        assert "obb_browser" not in out

    def test_forged_token_never_reaches_the_page(self):
        out = browsers.rewrite_html(
            "<head></head>", PROXY_PREFIX, user="../../etc", browser=INTERNATIONAL
        )
        assert "token=''" in out

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

    def test_redirect_target_keeps_theme_and_token(self):
        location = browsers._redirect_target(
            PROXY_PREFIX, f"{browsers._EIA_ORIGIN}/coal/?a=1", True, TOKEN
        )
        assert location.startswith(f"{PROXY_PREFIX}/coal/?")
        assert "a=1" in location
        assert "obb_theme=dark" in location
        assert f"obb_token={TOKEN}" in location

    def test_light_theme_and_no_token(self):
        location = browsers._redirect_target(
            PROXY_PREFIX, f"{browsers._EIA_ORIGIN}/coal/", False, ""
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
                query=f"obb_browser={ngqs}&obb_view=ngqs",
                method="POST",
                body=b"items=1",
            ),
        )
        assert captured["body"] == b"items=1"
        browsers.set_current_view("", ngqs, "ngqs")
        recorded = browsers.get_data_target("", ngqs)
        assert recorded["method"] == "POST"
        assert recorded["body"] == b"items=1"
        assert recorded["content_type"] == "application/x-www-form-urlencoded"


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
                query=f"a=1&obb_theme=dark&obb_token={TOKEN}&obb_view=coal",
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
        assert b"Upstream error" in response.body

    @pytest.mark.asyncio
    async def test_data_response_recorded_against_the_tagged_view(self, monkeypatch):
        target = "https://www.eia.gov/international/api/data/data?x=1"
        FakeUpstream({target: (b'{"response":{}}', "application/json")}).install(
            monkeypatch
        )
        await browsers.eia_proxy(
            "international/api/data/data",
            make_info(
                "/api/v1/eia_proxy/international/api/data/data",
                query=f"x=1&obb_browser={INTERNATIONAL}&obb_token={TOKEN}"
                "&obb_view=international%2Fdata",
            ),
        )
        browsers.set_current_view(TOKEN, INTERNATIONAL, "international/data")
        assert browsers.get_data_target(TOKEN, INTERNATIONAL)["url"] == target

    @pytest.mark.asyncio
    async def test_a_data_request_establishes_the_current_view(self, monkeypatch):
        """The view must not stay pinned to whichever view loaded first.

        The navigation beacon is the primary signal, but if it never lands the
        current view would never move and ``raw`` would answer for the first
        view forever. Every data request also carries the view that issued it.
        """
        first = "https://www.eia.gov/international/api/series_data/data?id=1"
        second = "https://www.eia.gov/international/api/series_data/data?id=4"
        FakeUpstream(
            {
                first: (b'{"data":{}}', "application/json"),
                second: (b'{"data":{}}', "application/json"),
            }
        ).install(monkeypatch)
        base = "/api/v1/eia_proxy/international/api/series_data/data"

        await browsers.eia_proxy(
            "international/api/series_data/data",
            make_info(base, query=f"id=1&obb_browser={INTERNATIONAL}&obb_view=view/1"),
        )
        assert browsers.get_current_view("", INTERNATIONAL) == "view/1"
        assert browsers.get_data_target("", INTERNATIONAL)["url"] == first

        await browsers.eia_proxy(
            "international/api/series_data/data",
            make_info(base, query=f"id=4&obb_browser={INTERNATIONAL}&obb_view=view/4"),
        )
        assert browsers.get_current_view("", INTERNATIONAL) == "view/4"
        assert browsers.get_data_target("", INTERNATIONAL)["url"] == second

    @pytest.mark.asyncio
    async def test_deep_linked_spa_route_still_reports_its_view(self, monkeypatch):
        """A restored or deep-linked sub-route is not the browser's root path.

        Injection keyed on the root path alone left these pages with no tagger
        and no beacon, so nothing they fetched was ever tied to a view.
        """
        target = "https://www.eia.gov/international/overview/USA"
        FakeUpstream({target: (b"<head></head>", "text/html")}).install(monkeypatch)
        response = await browsers.eia_proxy(
            "international/overview/USA",
            make_info("/api/v1/eia_proxy/international/overview/USA"),
        )
        page = response.body.decode()
        assert f"browser='{INTERNATIONAL}'" in page
        assert "obb_view" in page
        assert "/eia_view" in page

    @pytest.mark.asyncio
    async def test_article_pages_get_no_tagger(self, monkeypatch):
        target = "https://www.eia.gov/todayinenergy/detail.php?id=1"
        FakeUpstream({target: (b"<head></head>", "text/html")}).install(monkeypatch)
        response = await browsers.eia_proxy(
            "todayinenergy/detail.php",
            make_info("/api/v1/eia_proxy/todayinenergy/detail.php", query="id=1"),
        )
        assert "obb_browser" not in response.body.decode()

    @pytest.mark.asyncio
    async def test_untagged_spa_request_still_records_via_the_path(self, monkeypatch):
        target = "https://www.eia.gov/international/api/data/data"
        FakeUpstream({target: (b'{"response":{}}', "application/json")}).install(
            monkeypatch
        )
        await browsers.eia_proxy(
            "international/api/data/data",
            make_info("/api/v1/eia_proxy/international/api/data/data"),
        )
        assert browsers.get_data_target("", INTERNATIONAL)["url"] == target

    @pytest.mark.asyncio
    async def test_paginated_continuation_does_not_replace_the_view(self, monkeypatch):
        first = "https://www.eia.gov/international/api/data/data?offset=0"
        page2 = "https://www.eia.gov/international/api/data/data?offset=500"
        FakeUpstream(
            {
                first: (b'{"response":{}}', "application/json"),
                page2: (b'{"response":{}}', "application/json"),
            }
        ).install(monkeypatch)
        base = "/api/v1/eia_proxy/international/api/data/data"
        await browsers.eia_proxy(
            "international/api/data/data", make_info(base, "offset=0")
        )
        await browsers.eia_proxy(
            "international/api/data/data", make_info(base, "offset=500")
        )
        assert browsers.get_data_target("", INTERNATIONAL)["url"] == first


class TestRenderBrowser:
    """Each browser is its own widget, carrying EIA's own description."""

    @pytest.mark.asyncio
    async def test_site_payload(self):
        info = make_info("/api/v1/coal_browser")
        response = await browsers.render_browser("coal", "light", False, "", info)
        text = response.body.decode()
        assert '"mode": "site"' in text
        assert '"theme": "light"' in text
        assert "eia_proxy/coal/data/browser/" in text
        assert browsers.EIA_DATA_BROWSERS["coal"]["description"][:40] in text

    @pytest.mark.asyncio
    async def test_unknown_browser_falls_back_to_electricity(self):
        info = make_info("/api/v1/bogus_browser")
        response = await browsers.render_browser("bogus", "dark", False, "", info)
        text = response.body.decode()
        assert "electricity/data/browser/" in text
        assert '"theme": "dark"' in text

    @pytest.mark.asyncio
    async def test_petroleum_imports_lands_on_its_default_view(self):
        info = make_info("/api/v1/petroleum_imports_browser")
        response = await browsers.render_browser(
            "petroleum_imports", "dark", False, "", info
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
        response = await browsers.render_browser("maps", "dark", False, "", info)
        text = response.body.decode()
        assert '"mode": "maps"' in text
        assert "\\u003c" in text
        assert "\\u0026" in text
        assert "/maps/x.pdf" in text

    @pytest.mark.asyncio
    async def test_raw_labels_series_ids_the_way_the_table_does(self, monkeypatch):
        origin = browsers._EIA_ORIGIN
        target = f"{origin}/international/api/data/data"
        upstream = intl_upstream()
        upstream.responses[target] = (
            json.dumps(
                {"data": {"INTL.44-1-USA-QBTU.A": {"2023": [1.5, 1.5]}}}
            ).encode(),
            "application/json",
        )
        upstream.install(monkeypatch)
        browsers.set_current_view(TOKEN, INTERNATIONAL, "international/data")
        browsers.set_data_target(
            TOKEN,
            INTERNATIONAL,
            "international/data",
            {"url": target, "method": "GET"},
        )
        info = make_info("/api/v1/international_browser")
        response = await browsers.render_browser(
            "international", "dark", True, TOKEN, info
        )
        rows = json.loads(response.body)
        assert len(rows) == 1
        row = rows[0]
        assert row["category"] == "Production"
        assert row["country"] == "United States"
        assert row["units"] == "quad Btu"
        assert row["source_key"] == "INTL.44-1-USA-QBTU.A"
        assert row["2023 "] == 1.5

    @pytest.mark.asyncio
    async def test_raw_for_maps_returns_the_catalog(self, monkeypatch):
        async def fake_catalog():
            return [{"tab": "R", "section": "S", "title": "T", "pdf": "/x.pdf"}]

        monkeypatch.setattr(browsers, "fetch_maps_catalog", fake_catalog)
        info = make_info("/api/v1/maps_browser")
        response = await browsers.render_browser("maps", "dark", True, "", info)
        assert json.loads(response.body)[0]["title"] == "T"


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
        browsers.set_current_view("", spec["path"], "ngqs")
        browsers.set_data_target(
            "",
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
        browsers.set_current_view("", spec["path"], "v")
        browsers.set_data_target(
            "", spec["path"], "v", {"url": target, "method": "GET"}
        )
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
    async def test_other_browsers_use_the_shared_pivot(self):
        assert await browsers._labelled_rows("electricity", {"TABLEDATA": {}}) is None

    @pytest.mark.asyncio
    async def test_non_dict_payload_is_not_labelled(self):
        assert await browsers._labelled_rows("international", []) is None


class TestRouterRegistration:
    """Every browser is registered as its own Workspace widget."""

    def routes(self):
        return {route.path: route for route in browsers.router._api_router.routes}

    def test_proxy_and_beacon_are_registered_and_hidden(self):
        routes = self.routes()
        assert "/eia_proxy/{path:path}" in routes
        assert "/eia_view" in routes
        assert routes["/eia_proxy/{path:path}"].include_in_schema is False
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
    def test_endpoint_docstring_is_the_eia_description(self, browser):
        route = self.routes()[browsers.widget_route(browser)]
        assert (
            route.endpoint.__doc__
            == (browsers.EIA_DATA_BROWSERS[browser]["description"])
        )

    @pytest.mark.parametrize("browser", sorted(browsers.EIA_DATA_BROWSERS))
    def test_no_implementation_chatter_in_descriptions(self, browser):
        spec = browsers.EIA_DATA_BROWSERS[browser]
        text = spec["description"].lower()
        for phrase in ("chrome-free", "raw rows", "html widget", "proxy", "embed"):
            assert phrase not in text

    @pytest.mark.asyncio
    @pytest.mark.parametrize("browser", sorted(browsers.EIA_DATA_BROWSERS))
    async def test_registered_endpoint_serves_its_browser(self, browser, monkeypatch):
        async def fake_catalog():
            return []

        monkeypatch.setattr(browsers, "fetch_maps_catalog", fake_catalog)
        endpoint = self.routes()[browsers.widget_route(browser)].endpoint
        response = await endpoint(
            theme="dark",
            raw=False,
            obb_token=TOKEN,
            info=make_info(f"/api/v1{browsers.widget_route(browser)}"),
        )
        text = response.body.decode()
        assert f'"browser": "{browser}"' in text
        assert f"obb_token={TOKEN}" in text
