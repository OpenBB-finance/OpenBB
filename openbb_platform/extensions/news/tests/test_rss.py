"""RSS endpoint tests."""

import pytest

from openbb_news import registry, rss


@pytest.fixture
def mocked_pipeline(monkeypatch, stub_session_factory, sample_rss, sample_article_html):
    monkeypatch.setattr(
        "openbb_news.registry.get_feed_url",
        lambda key: f"http://feed.test/{key}",
    )
    stub_session_factory(
        {
            "http://feed.test/example": sample_rss,
            "https://example.test/article/1": sample_article_html,
        }
    )


async def test_rss_with_body(mocked_pipeline):
    out = await rss.rss(source="example", limit=5, fetch_body=True)
    items = out.results
    assert len(items) == 2
    assert items[0].title == "First Article"
    assert items[0].date.endswith("+00:00")
    assert items[0].author == "Jane Doe"
    assert items[0].excerpt == "A short summary."
    assert items[0].url == "https://example.test/article/1"
    assert "First paragraph" in items[0].body
    assert items[1].excerpt == "Plain text summary without HTML."
    assert items[1].body == items[1].excerpt
    assert items[1].url == ""
    assert items[1].author == "Sample Feed"


async def test_rss_without_body(mocked_pipeline):
    out = await rss.rss(source="example", limit=5, fetch_body=False)
    assert all(item.body == item.excerpt for item in out.results)


async def test_rss_limit_caps_entries(mocked_pipeline):
    out = await rss.rss(source="example", limit=1, fetch_body=False)
    assert len(out.results) == 1


async def test_rss_empty_feed(monkeypatch, stub_session_factory):
    monkeypatch.setattr(
        "openbb_news.registry.get_feed_url", lambda key: "http://feed.test/empty"
    )
    stub_session_factory({"http://feed.test/empty": b"<rss><channel></channel></rss>"})
    out = await rss.rss(source="empty", limit=5, fetch_body=True)
    assert out.results == []


async def test_rss_unknown_source():
    with pytest.raises(ValueError, match="Unknown RSS feed source"):
        await rss.rss(source="totally_made_up", limit=1, fetch_body=False)


async def test_rss_returns_empty_when_no_source():
    out = await rss.rss(source=None, limit=5, fetch_body=False)
    assert out.results == []
    out2 = await rss.rss(source="", limit=5, fetch_body=False)
    assert out2.results == []


async def test_rss_auto_selects_curated_default_for_outlet(
    monkeypatch, stub_session_factory, sample_rss
):
    monkeypatch.setattr(registry, "default_feed_for", lambda outlet: "curated_default")
    monkeypatch.setattr(
        "openbb_news.registry.get_feed_url",
        lambda key: f"http://feed.test/{key}",
    )
    stub_session_factory({"http://feed.test/curated_default": sample_rss})
    out = await rss.rss(outlet="any", source=None, limit=5, fetch_body=False)
    assert len(out.results) == 2
    assert out.results[0].title == "First Article"


async def test_rss_returns_empty_for_unknown_outlet(monkeypatch):
    monkeypatch.setattr(registry, "default_feed_for", lambda outlet: None)
    out = await rss.rss(outlet="ghost", source=None, limit=5, fetch_body=False)
    assert out.results == []


async def test_rss_sorts_newest_first(monkeypatch, stub_session_factory):
    feed = (
        b"<?xml version='1.0'?><rss version='2.0'><channel>"
        b"<title>Reversed Feed</title>"
        b"<item><title>Oldest</title>"
        b"<pubDate>Mon, 17 May 2026 09:00:00 GMT</pubDate></item>"
        b"<item><title>Middle</title>"
        b"<pubDate>Mon, 18 May 2026 09:00:00 GMT</pubDate></item>"
        b"<item><title>Newest</title>"
        b"<pubDate>Mon, 19 May 2026 09:00:00 GMT</pubDate></item>"
        b"</channel></rss>"
    )
    monkeypatch.setattr(
        "openbb_news.registry.get_feed_url", lambda key: "http://feed.test/rev"
    )
    stub_session_factory({"http://feed.test/rev": feed})
    out = await rss.rss(source="x", limit=5, fetch_body=False)
    assert [item.title for item in out.results] == ["Newest", "Middle", "Oldest"]


async def test_rss_sorts_undated_entries_to_bottom(monkeypatch, stub_session_factory):
    feed = (
        b"<?xml version='1.0'?><rss version='2.0'><channel>"
        b"<title>Mixed Feed</title>"
        b"<item><title>No Date</title>"
        b"<description>no pubdate</description></item>"
        b"<item><title>Dated</title>"
        b"<pubDate>Mon, 19 May 2026 09:00:00 GMT</pubDate></item>"
        b"</channel></rss>"
    )
    monkeypatch.setattr(
        "openbb_news.registry.get_feed_url", lambda key: "http://feed.test/mixed"
    )
    stub_session_factory({"http://feed.test/mixed": feed})
    out = await rss.rss(source="x", limit=5, fetch_body=False)
    assert [item.title for item in out.results] == ["Dated", "No Date"]


async def test_rss_handles_missing_title(monkeypatch, stub_session_factory):
    monkeypatch.setattr(
        "openbb_news.registry.get_feed_url", lambda key: "http://feed.test/notitle"
    )
    feed = (
        b"<?xml version='1.0'?><rss version='2.0'><channel>"
        b"<item><description>Body only</description></item>"
        b"</channel></rss>"
    )
    stub_session_factory({"http://feed.test/notitle": feed})
    items = (await rss.rss(source="x", limit=1, fetch_body=False)).results
    assert items[0].title == "(untitled)"
    assert items[0].author == "Unknown"


async def test_rss_providers_lists_known_providers(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    out = await rss.rss_providers()
    keys = [entry["value"] for entry in out]
    assert "bbc" in keys
    assert "pr_newswire" in keys
    labels = {entry["value"]: entry["label"] for entry in out}
    assert labels["bbc"] == "BBC"
    assert labels["axios"] == "Axios"


async def test_rss_feeds_filtered_by_provider(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    out = await rss.rss_feeds(outlet="bbc")
    labels = [entry["label"] for entry in out]
    assert "World" in labels
    assert "Politics" in labels
    assert labels == sorted(labels)
    fox_out = await rss.rss_feeds(outlet="fox_news")
    fox_labels = [entry["label"] for entry in fox_out]
    assert "Latest Headlines" in fox_labels
    assert "Politics" in fox_labels


async def test_rss_feeds_no_provider_returns_empty(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    assert await rss.rss_feeds(outlet=None) == []


def test_news_item_data_shape():
    item = rss.NewsItemData(
        title="t",
        date="2026-01-01T00:00:00+00:00",
        author="a",
        url="https://example.test/a",
        excerpt="e",
        body="b",
    )
    assert item.title == "t"
    assert item.body == "b"
    assert item.url == "https://example.test/a"


async def test_rss_body_uses_markdown_links_when_extraction_fails(
    monkeypatch, stub_session_factory
):
    feed = (
        b"<?xml version='1.0' encoding='UTF-8'?>"
        b'<rss version="2.0"><channel><title>Aggregator</title>'
        b"<item>"
        b"<title>Cluster</title>"
        b"<link>https://aggregator.test/x</link>"
        b"<description><![CDATA["
        b'<a href="https://nyt.test/story" target="_blank">NYT headline</a>&nbsp;'
        b'<a href="https://bbc.test/story" target="_blank">BBC headline</a>&nbsp;'
        b"]]></description>"
        b"<pubDate>Mon, 19 May 2026 12:00:00 GMT</pubDate>"
        b"</item></channel></rss>"
    )
    monkeypatch.setattr(
        "openbb_news.registry.get_feed_url", lambda key: "http://feed.test/agg"
    )
    stub_session_factory(
        {
            "http://feed.test/agg": feed,
            "https://aggregator.test/x": b"<html><body><div>not an article</div></body></html>",
        }
    )
    items = (await rss.rss(source="x", limit=1, fetch_body=True)).results
    assert len(items) == 1
    body = items[0].body
    assert "[NYT headline](https://nyt.test/story)" in body
    assert "[BBC headline](https://bbc.test/story)" in body
    assert items[0].url == "https://aggregator.test/x"


async def test_rss_body_includes_inline_image_from_article(
    monkeypatch, stub_session_factory
):
    feed = (
        b"<?xml version='1.0' encoding='UTF-8'?>"
        b'<rss version="2.0"><channel><title>X</title>'
        b"<item><title>Story</title>"
        b"<link>https://aggregator.test/story</link>"
        b"<description>x</description>"
        b"<pubDate>Wed, 20 May 2026 13:35:34 EDT</pubDate>"
        b"</item></channel></rss>"
    )
    article = (
        b"<html><body><article>"
        b"<p>Opening sentence.</p>"
        b'<img src="https://x.test/inline.jpg" alt="photo"/>'
        b"<p>Closing sentence.</p>"
        b"</article></body></html>"
    )
    monkeypatch.setattr(
        "openbb_news.registry.get_feed_url", lambda key: "http://feed.test/x"
    )
    stub_session_factory(
        {"http://feed.test/x": feed, "https://aggregator.test/story": article}
    )
    items = (await rss.rss(source="x", limit=1, fetch_body=True)).results
    body = items[0].body
    assert "![photo](https://x.test/inline.jpg)" in body
    assert body.index("Opening sentence.") < body.index("![photo]")
    assert body.index("![photo]") < body.index("Closing sentence.")


async def test_rss_body_prepends_og_image_when_no_inline(
    monkeypatch, stub_session_factory
):
    feed = (
        b"<?xml version='1.0' encoding='UTF-8'?>"
        b'<rss version="2.0"><channel><title>X</title>'
        b"<item><title>Story</title>"
        b"<link>https://aggregator.test/story</link>"
        b"<description>x</description>"
        b"<pubDate>Wed, 20 May 2026 13:35:34 EDT</pubDate>"
        b"</item></channel></rss>"
    )
    article = (
        b"<html><head>"
        b'<meta property="og:image" content="https://x.test/hero.jpg">'
        b"</head><body><article>"
        b"<p>One.</p><p>Two.</p>"
        b"</article></body></html>"
    )
    monkeypatch.setattr(
        "openbb_news.registry.get_feed_url", lambda key: "http://feed.test/x"
    )
    stub_session_factory(
        {"http://feed.test/x": feed, "https://aggregator.test/story": article}
    )
    items = (await rss.rss(source="x", limit=1, fetch_body=True)).results
    assert items[0].body.startswith("![](https://x.test/hero.jpg)")


async def test_rss_body_preserves_cbc_style_description_image(
    monkeypatch, stub_session_factory
):
    feed = (
        b"<?xml version='1.0' encoding='UTF-8'?>"
        b'<rss version="2.0"><channel><title>CBC</title>'
        b"<item><title>Story</title>"
        b"<link>https://aggregator.test/story</link>"
        b"<description><![CDATA["
        b"<img src='https://i.cbc.ca/hero.jpg' alt='photo'/>"
        b"<p>Lead text.</p>"
        b"]]></description>"
        b"<pubDate>Wed, 20 May 2026 13:35:34 EDT</pubDate>"
        b"</item></channel></rss>"
    )
    monkeypatch.setattr(
        "openbb_news.registry.get_feed_url", lambda key: "http://feed.test/x"
    )
    stub_session_factory(
        {
            "http://feed.test/x": feed,
            "https://aggregator.test/story": b"<html><body><div>not an article</div></body></html>",
        }
    )
    items = (await rss.rss(source="x", limit=1, fetch_body=True)).results
    assert "![photo](https://i.cbc.ca/hero.jpg)" in items[0].body


async def test_gather_bodies_returns_none_for_empty_link(stub_session_factory):
    session = stub_session_factory({})
    out = await rss._gather_bodies(session, [None, ""])
    assert out == [None, None]
    assert session.calls == []


async def test_gather_bodies_swallows_per_item_exceptions(
    monkeypatch, stub_session_factory, sample_article_html
):
    import aiohttp

    session = stub_session_factory(
        {
            "https://good.test/a": sample_article_html,
            "https://bad.test/a": aiohttp.ClientError("synthetic failure"),
        }
    )
    out = await rss._gather_bodies(
        session, ["https://good.test/a", "https://bad.test/a"]
    )
    assert out[0] is not None
    assert "First paragraph" in out[0]
    assert out[1] is None


async def test_gather_bodies_propagates_cancellation(monkeypatch):
    import asyncio

    async def cancelling_fetch(session, url):
        raise asyncio.CancelledError

    monkeypatch.setattr("openbb_news.parser.fetch_article_body", cancelling_fetch)
    with pytest.raises(asyncio.CancelledError):
        await rss._gather_bodies(object(), ["https://x.test/a"])


async def test_gather_bodies_swallows_unexpected_exceptions(monkeypatch):
    async def broken_fetch(session, url):
        raise RuntimeError("internal bug")

    monkeypatch.setattr("openbb_news.parser.fetch_article_body", broken_fetch)
    out = await rss._gather_bodies(object(), ["https://x.test/a", "https://x.test/b"])
    assert out == [None, None]
