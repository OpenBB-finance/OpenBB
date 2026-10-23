"""Shared test fixtures."""

from typing import Any

import pytest

_SAMPLE_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Sample Feed</title>
    <item>
      <title>First Article</title>
      <link>https://example.test/article/1</link>
      <description>&lt;p&gt;A short summary.&lt;/p&gt;</description>
      <pubDate>Mon, 19 May 2026 13:00:00 GMT</pubDate>
      <author>Jane Doe</author>
    </item>
    <item>
      <title>Second Article</title>
      <description>Plain text summary without HTML.</description>
      <pubDate>Mon, 19 May 2026 12:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""

_SAMPLE_ARTICLE_HTML = b"""<!DOCTYPE html><html><body>
<article>
<p>First paragraph of the article.</p>
<p>Second paragraph with more detail.</p>
<p>Third paragraph closing the story.</p>
</article>
</body></html>
"""

_SAMPLE_JSONLD_HTML = b"""<!DOCTYPE html><html><body>
<script type="application/ld+json">{"@type":"NewsArticle","articleBody":"JSON-LD top-level body."}</script>
</body></html>
"""

# Mirrors the real drugs.com article DOM: no <article>, sidebar inside <main>,
# and trailing furniture after the disclaimer.
_SAMPLE_DRUGS_COM_HTML = b"""<!DOCTYPE html><html><head>
<meta property="og:image" content="https://www.drugs.com/img/social/ddc-opengraph-logomark.png">
</head><body>
<main id="container" class="ddc-main-container ddc-width-container">
<div class="ddc-main-content">
<div class="ddc-main-content-head">Home News Consumer News Print page</div>
<nav>All News Consumer Pro New Drugs</nav>
<h1 class="ddc-title-length-xl">FDA Clears First Cholesterol Pill</h1>
<p class="ddc-mgt-2 ddc-mgb-0 ddc-media-metadata">By Ellyn Vohnoutka HealthDay Reporter</p>
<!-- comment node between children -->
<p>THURSDAY, July 16, 2026 &mdash; A new daily pill will lower cholesterol.</p>
<p>The FDA acted today to approve the drug for adults.</p>
<div class="ddc-reference-list"><ul><li>Sources</li></ul></div>
<p class="ddc-disclaimer">Disclaimer: Statistical data in medical articles provide general trends.</p>
<div class="ddc-mgt-3 ddc-mgb-3"><img src="/img/logo/vendor/healthday-logo.png"/>
<p class="ddc-mgt-0">&copy; 2026 HealthDay. All rights reserved.</p></div>
<div class="more-resources"><h2>Read this next</h2>
<div class="ddc-media-list"><p>Related teaser one.</p><p>Related teaser two.</p></div></div>
<h2>More news resources</h2>
<ul><li>FDA Medwatch Drug Alerts</li></ul>
<h2>Subscribe to our newsletter</h2>
<p>Whatever your topic of interest, subscribe to our newsletters.</p>
</div>
<div class="ddc-main-sidebar">
<div class="ddc-sidebox ddc-sidebox-podcast"><img src="/img/banners/ddc-podcast-cover.png"/>
<p>Podcast pitch paragraph.</p></div>
<div class="ddc-sidebox ddc-sidebox-news"><p>Sidebar drug teaser one.</p>
<p>Sidebar drug teaser two.</p></div>
</div>
</main>
</body></html>
"""


@pytest.fixture
def sample_drugs_com_html() -> bytes:
    return _SAMPLE_DRUGS_COM_HTML


@pytest.fixture
def sample_rss() -> bytes:
    return _SAMPLE_RSS


@pytest.fixture
def sample_article_html() -> bytes:
    return _SAMPLE_ARTICLE_HTML


@pytest.fixture
def sample_jsonld_html() -> bytes:
    return _SAMPLE_JSONLD_HTML


class _FakeResponse:
    def __init__(self, content: bytes = b"", status: int = 200) -> None:
        self._content = content
        self.status = status

    async def read(self) -> bytes:
        return self._content

    def raise_for_status(self) -> None:
        if self.status >= 400:
            import aiohttp

            raise aiohttp.ClientResponseError(
                request_info=None,  # type: ignore[arg-type]
                history=(),
                status=self.status,
            )

    async def __aenter__(self) -> "_FakeResponse":
        return self

    async def __aexit__(self, *_args: Any) -> None:
        return None


class _FakeSession:
    def __init__(self, response_map: dict) -> None:
        self.response_map = response_map
        self.calls: list[str] = []
        self.headers_sent: list[dict | None] = []
        self.closed = False

    async def get(self, url: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append(url)
        self.headers_sent.append(kwargs.get("headers"))
        result = self.response_map.get(url)
        if result is None:
            raise KeyError(f"unmocked URL: {url}")
        if isinstance(result, BaseException):
            raise result
        return result

    async def __aenter__(self) -> "_FakeSession":
        return self

    async def __aexit__(self, *_args: Any) -> None:
        self.closed = True

    async def close(self) -> None:
        self.closed = True


@pytest.fixture
def stub_session_factory(monkeypatch):
    def factory(response_map: dict) -> _FakeSession:
        normalized: dict = {}
        for url, value in response_map.items():
            if isinstance(value, (bytes, bytearray)):
                normalized[url] = _FakeResponse(bytes(value))
            elif (
                isinstance(value, tuple)
                and len(value) == 2
                and isinstance(value[0], (bytes, bytearray))
            ):
                content, status = value
                normalized[url] = _FakeResponse(bytes(content), status=int(status))
            else:
                normalized[url] = value
        session = _FakeSession(normalized)

        async def _factory(*_a: Any, **_kw: Any) -> _FakeSession:
            return session

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.get_async_requests_session",
            _factory,
        )
        return session

    return factory
