"""Tests for the proxy transport: curl session, retries, disk cache, warmup.

eia.gov TLS-fingerprints its clients, so every fetch goes through a per-thread
curl_cffi session impersonating Chrome. These tests drive that layer through a
fake ``curl_cffi`` rather than a fake of our own code, so the retry, session
recycling, and caching logic all execute for real.
"""

import asyncio
import time

import pytest

from openbb_us_eia import browsers


class FakeResponse:
    def __init__(self, content=b"", content_type="text/html", status=200, history=()):
        self.content = content
        self.headers = {"Content-Type": content_type} if content_type else {}
        self.status_code = status
        self.history = list(history)
        self.url = "https://www.eia.gov/landed"


class FakeCurlSession:
    """Stand in for ``curl_cffi.requests.Session``."""

    instances: list = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.gets: list = []
        self.posts: list = []
        FakeCurlSession.instances.append(self)

    def get(self, target, **kwargs):
        self.gets.append(target)
        result = FakeCurlSession.get_results.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result

    def post(self, target, data=None, headers=None, **kwargs):
        self.posts.append((target, data, headers))
        result = FakeCurlSession.post_results.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result


@pytest.fixture(autouse=True)
def fake_curl(monkeypatch):
    """Route the curl session at a fake, and make retry backoff instant."""
    FakeCurlSession.instances = []
    FakeCurlSession.get_results = []
    FakeCurlSession.post_results = []
    monkeypatch.setattr("curl_cffi.requests.Session", FakeCurlSession)
    monkeypatch.setattr(browsers._CURL_LOCAL, "session", None, raising=False)
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    browsers._PROXY_CACHE.clear()
    browsers._REDIRECTS.clear()
    yield
    browsers._CURL_LOCAL.session = None
    browsers._PROXY_CACHE.clear()
    browsers._REDIRECTS.clear()


class TestCurlSession:
    """One Chrome-impersonating session per thread, reused across fetches."""

    def test_session_impersonates_chrome_and_is_reused(self):
        first = browsers._curl_session()
        second = browsers._curl_session()
        assert first is second
        assert first.kwargs["impersonate"] == "chrome"
        assert first.kwargs["headers"]["Referer"] == browsers._EIA_ORIGIN

    def test_each_thread_gets_its_own_session(self):
        seen: list = []

        def grab():
            seen.append(browsers._curl_session())

        import threading

        main = browsers._curl_session()
        thread = threading.Thread(target=grab)
        thread.start()
        thread.join()
        assert seen[0] is not main


class TestFetchSync:
    """Transient upstream failures are retried on a fresh session."""

    def test_returns_body_content_type_and_status(self):
        FakeCurlSession.get_results = [FakeResponse(b"ok", "text/plain", 200)]
        assert browsers._fetch_sync("https://t/x") == (b"ok", "text/plain", 200, "")

    def test_missing_content_type_defaults_to_octet_stream(self):
        FakeCurlSession.get_results = [FakeResponse(b"x", None)]
        assert browsers._fetch_sync("https://t/x")[1] == "application/octet-stream"

    def test_redirect_history_reports_where_it_landed(self):
        FakeCurlSession.get_results = [
            FakeResponse(b"x", "text/html", 200, history=[object()])
        ]
        assert browsers._fetch_sync("https://t/x")[3] == "https://www.eia.gov/landed"

    def test_retries_then_succeeds_on_a_new_session(self):
        FakeCurlSession.get_results = [
            RuntimeError("reset"),
            FakeResponse(b"ok", "text/plain"),
        ]
        assert browsers._fetch_sync("https://t/x")[0] == b"ok"
        assert len(FakeCurlSession.instances) == 2

    def test_raises_after_exhausting_retries(self):
        FakeCurlSession.get_results = [RuntimeError("down")] * 3
        with pytest.raises(RuntimeError, match="down"):
            browsers._fetch_sync("https://t/x")
        assert len(FakeCurlSession.instances) == 3


class TestPostSync:
    """POST carries the body and content type, and retries the same way."""

    def test_posts_body_and_header(self):
        FakeCurlSession.post_results = [FakeResponse(b"{}", "application/json")]
        result = browsers._post_sync("https://t/x", b"payload", "application/json")
        assert result == (b"{}", "application/json", 200)
        target, data, headers = FakeCurlSession.instances[0].posts[0]
        assert data == b"payload"
        assert headers == {"Content-Type": "application/json"}

    def test_no_content_type_sends_no_header(self):
        FakeCurlSession.post_results = [FakeResponse(b"{}", "application/json")]
        browsers._post_sync("https://t/x", b"p", "")
        assert FakeCurlSession.instances[0].posts[0][2] == {}

    def test_missing_content_type_defaults_to_octet_stream(self):
        FakeCurlSession.post_results = [FakeResponse(b"x", None)]
        assert browsers._post_sync("https://t/x", b"p", "")[1] == (
            "application/octet-stream"
        )

    def test_retries_then_succeeds(self):
        FakeCurlSession.post_results = [
            RuntimeError("reset"),
            FakeResponse(b"{}", "application/json"),
        ]
        assert browsers._post_sync("https://t/x", b"p", "")[0] == b"{}"

    def test_raises_after_exhausting_retries(self):
        FakeCurlSession.post_results = [RuntimeError("down")] * 3
        with pytest.raises(RuntimeError, match="down"):
            browsers._post_sync("https://t/x", b"p", "")

    @pytest.mark.asyncio
    async def test_post_upstream_is_never_cached(self):
        FakeCurlSession.post_results = [
            FakeResponse(b"{}", "application/json"),
            FakeResponse(b"{}", "application/json"),
        ]
        target = "https://t/x"
        await browsers.post_upstream(target, b"p", "")
        await browsers.post_upstream(target, b"p", "")
        assert target not in browsers._PROXY_CACHE
        assert len(FakeCurlSession.instances[0].posts) == 2


class TestDiskCache:
    """Immutable assets are cached to disk; everything else is not."""

    @pytest.mark.parametrize(
        "target",
        [
            "https://t/a.js",
            "https://t/a.css",
            "https://t/a.PNG",
            "https://t/a.woff2?v=1",
            "https://t/m.pdf",
        ],
    )
    def test_static_assets_recognised(self, target):
        assert browsers._is_static(target) is True

    @pytest.mark.parametrize(
        "target", ["https://t/page.html", "https://t/api/data", "https://t/x.json"]
    )
    def test_dynamic_targets_are_not_static(self, target):
        assert browsers._is_static(target) is False

    def test_cache_paths_are_derived_from_the_url(self, monkeypatch, tmp_path):
        monkeypatch.setattr(browsers, "_CACHE_DIR", tmp_path)
        body, type_path = browsers._cache_paths("https://t/a.js")
        assert body.parent == tmp_path
        assert type_path.name == f"{body.name}.type"
        assert browsers._cache_paths("https://t/b.js")[0] != body

    @pytest.mark.asyncio
    async def test_unwritable_cache_dir_does_not_break_the_fetch(
        self, monkeypatch, tmp_path
    ):
        blocker = tmp_path / "blocked"
        blocker.write_text("not a directory")
        monkeypatch.setattr(browsers, "_CACHE_DIR", blocker / "cache")
        FakeCurlSession.get_results = [FakeResponse(b"code", "application/javascript")]
        assert await browsers._fetch_upstream("https://t/a.js") == (
            b"code",
            "application/javascript",
        )


class TestWarmup:
    """The proxy pre-fetches the browser's assets so the first load is warm."""

    ELECTRICITY = browsers.EIA_DATA_BROWSERS["electricity"]["path"]

    @pytest.mark.asyncio
    async def test_page_assets_collects_scripts_styles_and_modules(self, monkeypatch):
        html = (
            '<link href="/global/styles/screen.css" rel="stylesheet">'
            '<script src="app.js"></script>'
            '<script src="https://cdn/x.js"></script>'
            "<script>require['urlArgs'] = 'v=9';"
            'var m = "/coal/data/browser/node_modules/thing";</script>'
        )

        async def fake_fetch(target):
            assert target == f"{browsers._EIA_ORIGIN}/{self.ELECTRICITY}"
            return html.encode(), "text/html"

        monkeypatch.setattr(browsers, "_fetch_upstream", fake_fetch)
        assets = await browsers._page_assets(self.ELECTRICITY)
        assert f"{browsers._EIA_ORIGIN}/global/styles/screen.css" in assets
        assert f"{browsers._EIA_ORIGIN}/{self.ELECTRICITY}app.js" in assets
        assert not any("cdn" in asset for asset in assets)
        assert (
            f"{browsers._EIA_ORIGIN}/coal/data/browser/node_modules/thing.js?v=9"
            in assets
        )

    @pytest.mark.asyncio
    async def test_warm_fetches_shared_assets_and_survives_page_failure(
        self, monkeypatch
    ):
        fetched: list = []

        async def fake_fetch(target):
            fetched.append(target)
            if target.endswith(self.ELECTRICITY):
                raise RuntimeError("page down")
            return b"", "text/plain"

        monkeypatch.setattr(browsers, "_fetch_upstream", fake_fetch)
        await browsers._warm_proxy_cache()
        for asset in browsers._WARM_ASSETS:
            assert f"{browsers._EIA_ORIGIN}/{asset}" in fetched

    @pytest.mark.asyncio
    async def test_warm_swallows_individual_asset_failures(self, monkeypatch):
        async def fake_fetch(_target):
            raise RuntimeError("boom")

        monkeypatch.setattr(browsers, "_fetch_upstream", fake_fetch)
        await browsers._warm_proxy_cache()

    def test_schedule_without_a_running_loop_is_a_no_op(self):
        browsers._WARM_TASKS.clear()
        browsers._schedule_warm()
        assert not browsers._WARM_TASKS

    @pytest.mark.asyncio
    async def test_schedule_tracks_and_discards_the_task(self, monkeypatch):
        async def fake_warm():
            return None

        monkeypatch.setattr(browsers, "_warm_proxy_cache", fake_warm)
        browsers._WARM_TASKS.clear()
        browsers._schedule_warm()
        assert len(browsers._WARM_TASKS) == 1
        await asyncio.gather(*browsers._WARM_TASKS)
        await asyncio.sleep(0)
        assert not browsers._WARM_TASKS

    @pytest.mark.asyncio
    async def test_lifespan_warms_on_startup_and_cancels_on_shutdown(self, monkeypatch):
        started = asyncio.Event()

        async def fake_warm():
            started.set()
            await asyncio.sleep(3600)

        monkeypatch.setattr(browsers, "_warm_proxy_cache", fake_warm)
        browsers._WARM_TASKS.clear()
        async with browsers.lifespan(None):
            await started.wait()
            tasks = list(browsers._WARM_TASKS)
            assert tasks
        await asyncio.sleep(0)
        assert all(task.cancelled() or task.done() for task in tasks)
