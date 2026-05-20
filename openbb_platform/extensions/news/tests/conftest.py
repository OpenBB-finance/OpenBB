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
        self.closed = False

    async def get(self, url: str, **_kwargs: Any) -> _FakeResponse:
        self.calls.append(url)
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
