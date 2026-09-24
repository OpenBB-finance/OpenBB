"""Parser tests."""

import time

from lxml import html

from openbb_news import parser


def test_strip_html_empty():
    assert parser.strip_html("") == ""


def test_strip_html_plain():
    assert parser.strip_html("hello world") == "hello world"


def test_strip_html_tags_and_whitespace():
    assert parser.strip_html("<p>Hello   <b>world</b>\n!</p>") == "Hello world !"


def test_html_to_markdown_empty():
    assert parser.html_to_markdown("") == ""


def test_html_to_markdown_preserves_anchor_links():
    out = parser.html_to_markdown(
        '<a href="https://nyt.test/x" target="_blank">NYT headline</a>&nbsp;'
        '<a href="https://bbc.test/x">BBC headline</a>'
    )
    assert "[NYT headline](https://nyt.test/x)" in out
    assert "[BBC headline](https://bbc.test/x)" in out


def test_html_to_markdown_strips_non_anchor_tags():
    out = parser.html_to_markdown("<p>Hello <b>bold</b> world</p>")
    assert "bold" in out
    assert "<" not in out


def test_html_to_markdown_anchor_without_href():
    out = parser.html_to_markdown('<a target="_blank">just text</a>')
    assert "just text" in out
    assert "[" not in out


def test_html_to_markdown_anchor_without_text():
    out = parser.html_to_markdown('<a href="https://x.test/y"></a>')
    assert "[" not in out


def test_html_to_markdown_handles_paragraphs_and_breaks():
    out = parser.html_to_markdown("<p>Line one</p><p>Line two</p>")
    assert "Line one" in out
    assert "Line two" in out
    assert "Line one" in out.split("\n")[0]


def test_html_to_markdown_handles_br():
    out = parser.html_to_markdown("First<br/>Second")
    assert "First" in out
    assert "Second" in out


def test_html_to_markdown_paragraph_after_text():
    out = parser.html_to_markdown("intro text<p>paragraph</p>")
    assert "intro text" in out
    assert "paragraph" in out
    lines = [line for line in out.split("\n") if line.strip()]
    assert lines.index("intro text") < lines.index("paragraph")


def test_html_to_markdown_lxml_parse_failure_falls_back(monkeypatch):
    from lxml import html as _html

    def boom(*_a, **_kw):
        raise ValueError("synthetic parse failure")

    monkeypatch.setattr(_html, "fragment_fromstring", boom)
    out = parser.html_to_markdown('<a href="x">link</a>')
    assert out == "link"


def test_truncate_short():
    assert parser.truncate("abc", limit=10) == "abc"


def test_truncate_long():
    text = "word " * 100
    truncated = parser.truncate(text, limit=50)
    assert len(truncated) <= 60
    assert truncated.endswith("…")


def test_struct_time_to_iso_none():
    iso = parser.struct_time_to_iso(None)
    assert "T" in iso and iso.endswith("+00:00")


def test_struct_time_to_iso_value():
    st = time.struct_time((2026, 5, 19, 12, 0, 0, 0, 139, 0))
    assert parser.struct_time_to_iso(st) == "2026-05-19T12:00:00+00:00"


def test_article_markdown_joins_with_blank_lines(sample_article_html):
    doc = html.fromstring(sample_article_html)
    article = doc.xpath("//article")[0]
    text = parser._article_markdown(article)
    assert "First paragraph of the article." in text
    assert text.count("\n\n") == 2


def test_article_markdown_requires_two_paragraphs():
    doc = html.fromstring(b"<div><p>only one paragraph</p></div>")
    node = doc.xpath("//div")[0]
    assert parser._article_markdown(node) == ""


def test_article_markdown_filters_video_chapter_timestamps():
    doc = html.fromstring(
        b"<div>"
        b"<p>Real opening paragraph with content.</p>"
        b"<p>2:26</p>"
        b"<p>12:44</p>"
        b"<p>0:58</p>"
        b"<p>1:30:00</p>"
        b"<p>Real closing paragraph.</p>"
        b"</div>"
    )
    text = parser._article_markdown(doc.xpath("//div")[0])
    assert "2:26" not in text
    assert "12:44" not in text
    assert "0:58" not in text
    assert "1:30:00" not in text
    assert "Real opening paragraph" in text
    assert "Real closing paragraph" in text


def test_article_markdown_keeps_timestamp_inside_sentence():
    doc = html.fromstring(
        b"<div>"
        b"<p>The video begins at 2:26 with the host introducing.</p>"
        b"<p>By 12:44 the segment closes.</p>"
        b"</div>"
    )
    text = parser._article_markdown(doc.xpath("//div")[0])
    assert "2:26" in text
    assert "12:44" in text


def test_article_markdown_ignores_non_paragraph_text():
    doc = html.fromstring(b"<div>plain wrapper text <span>here</span></div>")
    node = doc.xpath("//div")[0]
    assert parser._article_markdown(node) == ""


def test_article_markdown_skips_figure_without_img():
    doc = html.fromstring(
        b"<article>"
        b"<p>One.</p>"
        b"<figure><figcaption>No image here</figcaption></figure>"
        b"<p>Two.</p>"
        b"</article>"
    )
    text = parser._article_markdown(doc.xpath("//article")[0])
    assert "![" not in text
    assert "One." in text
    assert "Two." in text


def test_article_markdown_skips_img_without_src():
    doc = html.fromstring(b"<article><p>One.</p><img/><p>Two.</p></article>")
    text = parser._article_markdown(doc.xpath("//article")[0])
    assert "![" not in text


def test_article_markdown_figure_without_caption():
    doc = html.fromstring(
        b"<article>"
        b"<p>One.</p>"
        b'<figure><img src="https://x.test/p.jpg"/></figure>'
        b"<p>Two.</p>"
        b"</article>"
    )
    text = parser._article_markdown(doc.xpath("//article")[0])
    assert "![](https://x.test/p.jpg)" in text


def test_strip_chrome_removes_chrome_tags():
    doc = html.fromstring(
        b"<html><body>"
        b"<nav>nav junk</nav><header>h</header><footer>f</footer>"
        b"<aside>a</aside><form>fm</form><script>s</script><style>.x{}</style>"
        b"<noscript>n</noscript><iframe>i</iframe><button>b</button><svg>sv</svg>"
        b"<article><p>kept one</p><p>kept two</p></article>"
        b"</body></html>"
    )
    parser._strip_chrome(doc)
    leftover_tags = {el.tag for el in doc.iter() if isinstance(el.tag, str)}
    for tag in parser._CHROME_TAGS:
        assert tag not in leftover_tags
    assert "article" in leftover_tags


def test_looks_clean_rejects_templates_and_empty():
    assert parser._looks_clean("Some real text.")
    assert not parser._looks_clean("")
    assert not parser._looks_clean("[[ type === 'moc' ]] body text")
    assert not parser._looks_clean("body with {{ binding }} marker")


async def test_fetch_feed_parses(stub_session_factory, sample_rss):
    session = stub_session_factory({"http://feed.test/rss": sample_rss})
    parsed = await parser.fetch_feed(session, "http://feed.test/rss")
    assert len(parsed.entries) == 2
    assert parsed.entries[0].title == "First Article"


async def test_fetch_feed_client_error(stub_session_factory):
    import aiohttp

    session = stub_session_factory(
        {"http://feed.test/rss": aiohttp.ClientError("boom")}
    )
    parsed = await parser.fetch_feed(session, "http://feed.test/rss")
    assert len(parsed.entries) == 0


async def test_fetch_feed_http_error(stub_session_factory):
    session = stub_session_factory({"http://feed.test/rss": (b"", 500)})
    parsed = await parser.fetch_feed(session, "http://feed.test/rss")
    assert len(parsed.entries) == 0


async def test_fetch_feed_pins_headers_for_gated_host(stub_session_factory, sample_rss):
    url = "https://www.espn.com/espn/rss/nfl/news"
    session = stub_session_factory({url: sample_rss})
    await parser.fetch_feed(session, url)
    assert session.headers_sent == [parser._HOST_HEADERS["espn.com"]]


async def test_fetch_feed_no_headers_for_normal_host(stub_session_factory, sample_rss):
    url = "https://feeds.bbci.co.uk/news/rss.xml"
    session = stub_session_factory({url: sample_rss})
    await parser.fetch_feed(session, url)
    assert session.headers_sent == [None]


def test_extract_body_jsonld_top_level(sample_jsonld_html):
    assert parser._extract_body(sample_jsonld_html) == "JSON-LD top-level body."


def test_extract_body_jsonld_graph():
    payload = (
        b'<html><body><script type="application/ld+json">'
        b'{"@graph":[{"@type":"Other"},'
        b'{"@type":"NewsArticle","articleBody":"Body from graph."}]}'
        b"</script></body></html>"
    )
    assert parser._extract_body(payload) == "Body from graph."


def test_extract_body_jsonld_list():
    payload = (
        b'<html><body><script type="application/ld+json">'
        b'[{"@type":"Other"},'
        b'{"@type":"NewsArticle","articleBody":"Found in list."}]'
        b"</script></body></html>"
    )
    assert parser._extract_body(payload) == "Found in list."


def test_extract_body_jsonld_invalid_then_article():
    payload = (
        b"<html><body>"
        b'<script type="application/ld+json">not json</script>'
        b"<article><p>First sentence.</p><p>Second sentence.</p></article>"
        b"</body></html>"
    )
    assert parser._extract_body(payload) == "First sentence.\n\nSecond sentence."


def test_extract_body_article_selector(sample_article_html):
    body = parser._extract_body(sample_article_html)
    assert body is not None
    assert "First paragraph" in body
    assert body.count("\n\n") == 2


def test_extract_body_picks_largest_article():
    payload = (
        b"<html><body>"
        b"<article><p>Related card one.</p><p>Related card two.</p></article>"
        b"<article>"
        b"<p>Main story paragraph one with more substance.</p>"
        b"<p>Main story paragraph two with detail.</p>"
        b"<p>Main story paragraph three closing the piece.</p>"
        b"</article>"
        b"</body></html>"
    )
    body = parser._extract_body(payload)
    assert body is not None
    assert "Main story paragraph one" in body
    assert "Related card" not in body


def test_extract_body_main_fallback_when_no_article():
    payload = (
        b"<html><body>"
        b"<nav><p>nav link</p><p>nav link two</p></nav>"
        b"<main>"
        b"<div><p>Story paragraph one with content.</p>"
        b"<p>Story paragraph two with more detail.</p></div>"
        b"</main>"
        b"</body></html>"
    )
    assert (
        parser._extract_body(payload)
        == "Story paragraph one with content.\n\nStory paragraph two with more detail."
    )


def test_extract_body_main_requires_two_paragraphs():
    payload = b"<html><body><main><p>Only one paragraph here.</p></main></body></html>"
    assert parser._extract_body(payload) is None


def test_extract_body_article_wins_over_main():
    payload = (
        b"<html><body>"
        b"<main>"
        b"<p>Main paragraph one.</p><p>Main paragraph two.</p>"
        b"<p>Main paragraph three.</p><p>Main paragraph four.</p>"
        b"</main>"
        b"<article><p>Article paragraph one.</p><p>Article paragraph two.</p></article>"
        b"</body></html>"
    )
    assert (
        parser._extract_body(payload)
        == "Article paragraph one.\n\nArticle paragraph two."
    )


def test_extract_body_rejects_unrendered_templates():
    payload = (
        b"<html><body>"
        b"<article>"
        b"<p>[[ type === 'moc' ? 'MARKET ON CLOSE' : 'FREE WEBINAR' ]]</p>"
        b"<p>[[ timeLabel ]] WATCH LIVE</p>"
        b"</article>"
        b"</body></html>"
    )
    assert parser._extract_body(payload) is None


def test_extract_body_strips_chrome_before_extracting():
    payload = (
        b"<html><body>"
        b"<nav><p>nav link one</p><p>nav link two</p></nav>"
        b"<header><p>banner text</p><p>banner two</p></header>"
        b"<article><p>Real story paragraph.</p><p>Story continues here.</p></article>"
        b"<footer><p>footer note</p><p>footer two</p></footer>"
        b"</body></html>"
    )
    assert (
        parser._extract_body(payload)
        == "Real story paragraph.\n\nStory continues here."
    )


def test_extract_body_no_container():
    assert parser._extract_body(b"<html><body>nothing</body></html>") is None


def test_extract_body_html_parse_error():
    assert parser._extract_body(b"") is None


def test_extract_body_jsonld_non_dict_entries():
    payload = (
        b"<html><body>"
        b'<script type="application/ld+json">["string", 42, null]</script>'
        b"<article><p>Fallback one.</p><p>Fallback two.</p></article>"
        b"</body></html>"
    )
    assert parser._extract_body(payload) == "Fallback one.\n\nFallback two."


def test_extract_body_jsonld_graph_no_body():
    payload = (
        b"<html><body>"
        b'<script type="application/ld+json">'
        b'{"@type":"NewsArticle","@graph":[{"@type":"X"}]}'
        b"</script>"
        b"<article><p>Graph fallback one.</p><p>Graph fallback two.</p></article>"
        b"</body></html>"
    )
    assert parser._extract_body(payload) == "Graph fallback one.\n\nGraph fallback two."


def test_extract_body_jsonld_graph_non_dict_entry():
    payload = (
        b"<html><body>"
        b'<script type="application/ld+json">'
        b'{"@type":"NewsArticle","@graph":["scalar",null,42,'
        b'{"@type":"NewsArticle","articleBody":"Graph article body."}]}'
        b"</script></body></html>"
    )
    assert parser._extract_body(payload) == "Graph article body."


def test_extract_body_jsonld_template_falls_through_to_article():
    payload = (
        b"<html><body>"
        b'<script type="application/ld+json">'
        b'{"@type":"NewsArticle","articleBody":"[[ binding ]] template junk"}'
        b"</script>"
        b"<article><p>Clean paragraph one.</p><p>Clean paragraph two.</p></article>"
        b"</body></html>"
    )
    assert (
        parser._extract_body(payload) == "Clean paragraph one.\n\nClean paragraph two."
    )


def test_extract_body_preserves_utf8_smart_punctuation():
    payload = (
        "<html><body><article>"
        "<p>The Court’s ruling — issued Tuesday — was clear.</p>"
        "<p>Dominion’s lawyers said “we won”.</p>"
        "</article></body></html>"
    ).encode()
    body = parser._extract_body(payload)
    assert body is not None
    assert "Court’s" in body
    assert "Dominion’s" in body
    assert "“we won”" in body
    assert "—" in body
    for artifact in ("â€™", "â€“", "Â "):
        assert artifact not in body


async def test_fetch_article_body_end_to_end(stub_session_factory, sample_article_html):
    session = stub_session_factory({"https://x.test/a": sample_article_html})
    body = await parser.fetch_article_body(session, "https://x.test/a")
    assert body is not None
    assert "First paragraph" in body


async def test_fetch_article_body_client_error(stub_session_factory):
    import aiohttp

    session = stub_session_factory({"https://x.test/a": aiohttp.ClientError("boom")})
    assert await parser.fetch_article_body(session, "https://x.test/a") is None


async def test_fetch_article_body_timeout(stub_session_factory):
    session = stub_session_factory(
        {"https://x.test/a": TimeoutError("simulated timeout")}
    )
    assert await parser.fetch_article_body(session, "https://x.test/a") is None


async def test_fetch_article_body_http_error(stub_session_factory):
    session = stub_session_factory({"https://x.test/a": (b"", 403)})
    assert await parser.fetch_article_body(session, "https://x.test/a") is None


async def test_fetch_article_body_no_article_returns_none(stub_session_factory):
    session = stub_session_factory(
        {"https://x.test/a": b"<html><body>nothing</body></html>"}
    )
    assert await parser.fetch_article_body(session, "https://x.test/a") is None


def test_extract_body_preserves_inline_img():
    payload = (
        b"<html><body><article>"
        b"<p>Opening paragraph.</p>"
        b'<img src="https://x.test/inline.jpg" alt="caption text"/>'
        b"<p>Closing paragraph.</p>"
        b"</article></body></html>"
    )
    body = parser._extract_body(payload)
    assert body is not None
    lines = body.split("\n\n")
    assert lines == [
        "Opening paragraph.",
        "![caption text](https://x.test/inline.jpg)",
        "Closing paragraph.",
    ]


def test_extract_body_preserves_figure_with_caption():
    payload = (
        b"<html><body><article>"
        b"<p>Lead in.</p>"
        b'<figure><img src="https://x.test/photo.jpg"/>'
        b"<figcaption>A long caption describing the photo.</figcaption>"
        b"</figure>"
        b"<p>After the photo.</p>"
        b"</article></body></html>"
    )
    body = parser._extract_body(payload)
    assert body is not None
    assert "![A long caption describing the photo.](https://x.test/photo.jpg)" in body
    assert "Lead in." in body
    assert "After the photo." in body


def test_extract_body_prepends_og_image_when_no_inline_image():
    payload = (
        b"<html><head>"
        b'<meta property="og:image" content="https://x.test/hero.jpg">'
        b"</head><body><article>"
        b"<p>Paragraph one.</p><p>Paragraph two.</p>"
        b"</article></body></html>"
    )
    body = parser._extract_body(payload)
    assert body is not None
    assert body.split("\n\n")[0] == "![](https://x.test/hero.jpg)"
    assert "Paragraph one." in body


def test_extract_body_skips_hero_when_inline_image_present():
    payload = (
        b"<html><head>"
        b'<meta property="og:image" content="https://x.test/hero.jpg">'
        b"</head><body><article>"
        b"<p>Lead.</p>"
        b'<img src="https://x.test/inline.jpg"/>'
        b"<p>Body.</p>"
        b"</article></body></html>"
    )
    body = parser._extract_body(payload)
    assert body is not None
    assert "https://x.test/hero.jpg" not in body
    assert "![](https://x.test/inline.jpg)" in body


def test_extract_body_jsonld_articlebody_with_og_hero():
    payload = (
        b"<html><head>"
        b'<meta property="og:image" content="https://x.test/hero.jpg">'
        b"</head><body>"
        b'<script type="application/ld+json">'
        b'{"@type":"NewsArticle","articleBody":"Pure text body."}'
        b"</script></body></html>"
    )
    body = parser._extract_body(payload)
    assert body == "![](https://x.test/hero.jpg)\n\nPure text body."


def test_html_to_markdown_preserves_inline_img():
    out = parser.html_to_markdown(
        '<p>Lead</p><img src="https://x.test/inline.jpg" alt="alt text"/>'
    )
    assert "![alt text](https://x.test/inline.jpg)" in out
    assert "Lead" in out


def test_html_to_markdown_img_tail_text():
    out = parser.html_to_markdown(
        '<img src="https://x.test/inline.jpg"/> trailing text after img'
    )
    assert "![](https://x.test/inline.jpg)" in out
    assert "trailing text after img" in out


def test_jsonld_field_list_of_strings():
    payload = (
        b"<html><body>"
        b'<script type="application/ld+json">'
        b'{"@type":"NewsArticle","image":["https://x.test/first.jpg","https://x.test/second.jpg"]}'
        b"</script></body></html>"
    )
    body = parser._extract_body(payload)
    assert body is None or body.startswith("![](https://x.test/first.jpg)")


def test_jsonld_field_list_of_image_objects():
    payload = (
        b"<html><body>"
        b'<script type="application/ld+json">'
        b'{"@type":"NewsArticle","image":[{"url":"https://x.test/o.jpg"}]}'
        b"</script>"
        b"<article><p>One.</p><p>Two.</p></article>"
        b"</body></html>"
    )
    body = parser._extract_body(payload)
    assert body is not None
    assert body.startswith("![](https://x.test/o.jpg)")


def test_jsonld_field_image_object_with_url():
    payload = (
        b"<html><body>"
        b'<script type="application/ld+json">'
        b'{"@type":"NewsArticle","image":{"@type":"ImageObject","url":"https://x.test/obj.jpg"}}'
        b"</script>"
        b"<article><p>One.</p><p>Two.</p></article>"
        b"</body></html>"
    )
    body = parser._extract_body(payload)
    assert body is not None
    assert body.startswith("![](https://x.test/obj.jpg)")


DRUGS_COM_URL = "https://www.drugs.com/news/fda-clears-cholesterol-pill-130672.html"


def test_host_strips_www():
    assert parser._host("https://www.drugs.com/news/x.html") == "drugs.com"


def test_host_without_www():
    assert parser._host("https://drugs.com/news/x.html") == "drugs.com"


def test_host_is_lowercased():
    assert parser._host("https://WWW.Drugs.COM/news/x.html") == "drugs.com"


def test_host_empty_url():
    assert parser._host(None) == ""
    assert parser._host("") == ""


def test_host_url_without_hostname():
    assert parser._host("not-a-url") == ""


def test_cut_tail_removes_marker_and_everything_after():
    doc = html.fromstring(
        b"<div id='c'>"
        b"<p>Keep one.</p>"
        b"<!-- comment -->"
        b"<p>Keep two.</p>"
        b"<h2>More news resources</h2>"
        b"<ul><li>link</li></ul>"
        b"<p>Newsletter pitch.</p>"
        b"</div>"
    )
    container = doc.xpath("//div")[0]
    parser._cut_tail(container, parser._SITE_RULES["drugs.com"].cut)
    text = container.text_content()
    assert "Keep one." in text
    assert "Keep two." in text
    assert "More news resources" not in text
    assert "Newsletter pitch." not in text


def test_cut_tail_without_marker_keeps_all():
    doc = html.fromstring(b"<div><p>One.</p><p>Two.</p></div>")
    container = doc.xpath("//div")[0]
    parser._cut_tail(container, parser._SITE_RULES["drugs.com"].cut)
    assert len(container.xpath(".//p")) == 2


def test_site_body_no_container_returns_empty():
    doc = html.fromstring(b"<html><body><p>One.</p><p>Two.</p></body></html>")
    assert parser._site_body(doc, parser._SITE_RULES["drugs.com"]) == ""


def test_site_body_picks_largest_container():
    doc = html.fromstring(
        b"<html><body>"
        b"<div class='ddc-main-content'>"
        b"<p>Short one.</p><p>Short two.</p></div>"
        b"<div class='ddc-main-content'>"
        b"<p>Longer container paragraph one with much more substance.</p>"
        b"<p>Longer container paragraph two with additional detail.</p></div>"
        b"</body></html>"
    )
    body = parser._site_body(doc, parser._SITE_RULES["drugs.com"])
    assert "Longer container paragraph one" in body
    assert "Short one." not in body


def test_site_body_skips_unclean_container():
    doc = html.fromstring(
        b"<html><body><div class='ddc-main-content'>"
        b"<p>[[ template ]] junk</p><p>{{ binding }} more junk</p>"
        b"</div></body></html>"
    )
    assert parser._site_body(doc, parser._SITE_RULES["drugs.com"]) == ""


def test_extract_body_drugs_com_keeps_article_text(sample_drugs_com_html):
    body = parser._extract_body(sample_drugs_com_html, DRUGS_COM_URL)
    assert body is not None
    assert "By Ellyn Vohnoutka HealthDay Reporter" in body
    assert "A new daily pill will lower cholesterol." in body
    assert "The FDA acted today to approve the drug for adults." in body


def test_extract_body_drugs_com_drops_trailing_furniture(sample_drugs_com_html):
    body = parser._extract_body(sample_drugs_com_html, DRUGS_COM_URL)
    assert body is not None
    assert "Disclaimer:" not in body
    assert "HealthDay. All rights reserved." not in body
    assert "Related teaser one." not in body
    assert "Whatever your topic of interest" not in body


def test_extract_body_drugs_com_drops_sidebar(sample_drugs_com_html):
    body = parser._extract_body(sample_drugs_com_html, DRUGS_COM_URL)
    assert body is not None
    assert "Sidebar drug teaser one." not in body
    assert "Podcast pitch paragraph." not in body
    assert "ddc-podcast-cover" not in body


def test_extract_body_drugs_com_skips_placeholder_hero(sample_drugs_com_html):
    body = parser._extract_body(sample_drugs_com_html, DRUGS_COM_URL)
    assert body is not None
    assert "ddc-opengraph-logomark" not in body
    assert not body.startswith("![")


def test_extract_body_drugs_com_keeps_real_hero():
    payload = (
        b"<html><head>"
        b'<meta property="og:image" content="https://media.test/featured.jpg">'
        b"</head><body><div class='ddc-main-content'>"
        b"<p>Lede paragraph of the story.</p><p>Second paragraph.</p>"
        b"</div></body></html>"
    )
    body = parser._extract_body(payload, DRUGS_COM_URL)
    assert body is not None
    assert body.split("\n\n")[0] == "![](https://media.test/featured.jpg)"


def test_extract_body_drugs_com_falls_back_when_container_missing():
    payload = (
        b"<html><body><article>"
        b"<p>Generic paragraph one.</p><p>Generic paragraph two.</p>"
        b"</article></body></html>"
    )
    body = parser._extract_body(payload, DRUGS_COM_URL)
    assert body == "Generic paragraph one.\n\nGeneric paragraph two."


def test_extract_body_unknown_host_uses_generic_path(sample_drugs_com_html):
    body = parser._extract_body(sample_drugs_com_html, "https://other.test/x.html")
    assert body is not None
    assert "Whatever your topic of interest" in body


def test_extract_body_without_url_uses_generic_path(sample_drugs_com_html):
    body = parser._extract_body(sample_drugs_com_html)
    assert body is not None
    assert "Whatever your topic of interest" in body


async def test_fetch_article_body_applies_site_rule(
    stub_session_factory, sample_drugs_com_html
):
    session = stub_session_factory({DRUGS_COM_URL: sample_drugs_com_html})
    body = await parser.fetch_article_body(session, DRUGS_COM_URL)
    assert body is not None
    assert "A new daily pill will lower cholesterol." in body
    assert "Whatever your topic of interest" not in body


async def test_fetch_article_body_pins_user_agent_for_drugs_com(
    stub_session_factory, sample_drugs_com_html
):
    session = stub_session_factory({DRUGS_COM_URL: sample_drugs_com_html})
    await parser.fetch_article_body(session, DRUGS_COM_URL)
    assert session.headers_sent == [parser._HOST_HEADERS["drugs.com"]]
    assert session.headers_sent[0]["User-Agent"] == parser._WEBKIT_UA


def test_drugs_com_pinned_user_agent_is_not_gecko():
    # drugs.com articles 403 any Gecko user agent.
    ua = parser._HOST_HEADERS["drugs.com"]["User-Agent"]
    assert "Gecko/" not in ua
    assert "AppleWebKit" in ua


def test_host_headers_pin_safe_encoding():
    # Overriding headers drops the session default Accept-Encoding; every pinned
    # host must exclude br, which the shared session cannot decode.
    for host, headers in parser._HOST_HEADERS.items():
        assert headers["Accept-Encoding"] == "gzip, deflate", host
        assert "br" not in headers["Accept-Encoding"], host


def test_host_headers_cover_expected_hosts():
    assert set(parser._HOST_HEADERS) == {
        "drugs.com",
        "espn.com",
        "heavy.com",
        "bleepingcomputer.com",
        "pbs.org",
        "techmeme.com",
    }


def test_pinned_helper_omits_user_agent_when_none():
    assert "User-Agent" not in parser._pinned()
    assert parser._pinned("UA/1.0")["User-Agent"] == "UA/1.0"


async def test_fetch_article_body_keeps_session_user_agent_for_other_hosts(
    stub_session_factory, sample_article_html
):
    session = stub_session_factory({"https://x.test/a": sample_article_html})
    await parser.fetch_article_body(session, "https://x.test/a")
    assert session.headers_sent == [None]


def test_extract_image_jsonld_fallback_path():
    payload = (
        b"<html><body>"
        b'<script type="application/ld+json">'
        b'{"@type":"NewsArticle","image":"https://x.test/ld.jpg"}'
        b"</script>"
        b"<article><p>One.</p><p>Two.</p></article>"
        b"</body></html>"
    )
    body = parser._extract_body(payload)
    assert body is not None
    assert body.startswith("![](https://x.test/ld.jpg)")
