"""Tests for the news feed, its stories, and the markdown it renders."""

import pytest

from openbb_tmx.utils import news


class TestMarkdown:
    """A story's markup becomes markdown."""

    def test_nothing_renders_as_nothing(self):
        assert news.html_to_markdown(None) == ""
        assert news.html_to_markdown("") == ""

    def test_paragraphs_are_separated(self):
        assert news.html_to_markdown("<p>One</p><p>Two</p>") == "One\n\nTwo"

    def test_a_break_becomes_a_newline(self):
        assert news.html_to_markdown("One<br/>Two") == "One\nTwo"

    def test_a_link_keeps_its_target(self):
        rendered = news.html_to_markdown('<a href="https://x.test">Read</a>')

        assert rendered == "[Read](https://x.test)"

    def test_an_image_is_kept(self):
        rendered = news.html_to_markdown('<img src="https://x.test/a.png" alt="a">')

        assert rendered == "![](https://x.test/a.png)"

    def test_emphasis_is_kept(self):
        assert news.html_to_markdown("<strong>a</strong> <em>b</em>") == "**a** _b_"

    def test_a_list_becomes_bullets(self):
        rendered = news.html_to_markdown("<ul><li>One</li><li>Two</li></ul>")

        assert "- One" in rendered and "- Two" in rendered

    def test_entities_are_decoded(self):
        assert news.html_to_markdown("<p>A &amp; B</p>") == "A & B"

    def test_no_markup_survives(self):
        rendered = news.html_to_markdown("<div><p>Body</p><span>More</span></div>")

        assert "<" not in rendered

    def test_blank_runs_are_collapsed(self):
        assert news.html_to_markdown("<p>a</p><p></p><p></p><p>b</p>") == "a\n\nb"


class TestExcerpt:
    """A summary is shortened for the card."""

    def test_a_short_summary_is_kept(self):
        assert news.excerpt("<p>Short summary.</p>") == "Short summary."

    def test_a_long_summary_is_cut_on_a_word(self):
        text = "word " * 200
        cut = news.excerpt(text, limit=40)

        assert len(cut) <= 40
        assert cut.endswith("…")

    def test_nothing_excerpts_to_nothing(self):
        assert news.excerpt("") == ""


class TestPagination:
    """The page-based feed is served by row offset."""

    @pytest.fixture
    def feed(self, monkeypatch):
        """Serve five numbered articles per page."""
        calls: list = []

        async def request(operation, query, variables, **kwargs):
            calls.append(variables)
            page = variables["page"]
            limit = variables["limit"]
            start = (page - 1) * limit

            return {
                "getNewsForSymbol": [
                    {
                        "newsid": start + i,
                        "headline": f"Article {start + i}",
                        "datetime": "2026-07-24T12:00:00Z",
                        "source": "Feed",
                        "summary": "s",
                    }
                    for i in range(limit)
                ]
            }

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", request)

        return calls

    async def test_the_first_page_is_served_whole(self, feed):
        rows = await news.get_news_page("AC", limit=5, offset=0)

        assert [r["newsid"] for r in rows] == [0, 1, 2, 3, 4]

    async def test_a_whole_page_offset_skips_a_page(self, feed):
        rows = await news.get_news_page("AC", limit=5, offset=5)

        assert [r["newsid"] for r in rows] == [5, 6, 7, 8, 9]

    async def test_a_partial_offset_spans_two_pages(self, feed):
        rows = await news.get_news_page("AC", limit=5, offset=2)

        assert [r["newsid"] for r in rows] == [2, 3, 4, 5, 6]

    async def test_an_exhausted_feed_stops(self, monkeypatch):
        async def nothing(*args, **kwargs):
            return {"getNewsForSymbol": []}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", nothing)

        assert await news.get_news_page("AC", limit=5, offset=0) == []

    async def test_an_absent_limit_falls_back_and_a_negative_offset_floors(self, feed):
        rows = await news.get_news_page("AC", limit=0, offset=-5)

        assert len(rows) == 20
        assert rows[0]["newsid"] == 0


class TestStories:
    """The full article body."""

    async def test_a_story_is_read(self, monkeypatch):
        async def request(operation, query, variables, **kwargs):
            return {"getNewsStoryById": {"headline": "H", "story": "<p>Body</p>"}}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", request)
        story = await news.get_story("1")

        assert story["story"] == "<p>Body</p>"

    async def test_an_unavailable_story_is_empty(self, monkeypatch):
        async def boom(*args, **kwargs):
            raise RuntimeError("gone")

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", boom)

        assert await news.get_story("1") == {}

    async def test_several_stories_are_read_together(self, monkeypatch):
        async def request(operation, query, variables, **kwargs):
            return {"getNewsStoryById": {"story": f"<p>{variables['newsid']}</p>"}}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", request)
        stories = await news.get_stories(["1", "2"])

        assert stories["1"]["story"] == "<p>1</p>"
        assert stories["2"]["story"] == "<p>2</p>"


class TestFeedCommand:
    """The command that shapes the widget's articles."""

    @pytest.fixture
    def wired(self, monkeypatch):
        """Serve one article and its story."""

        async def page(symbol, limit=20, offset=0, locale="en", use_cache=True):
            return [
                {
                    "newsid": 42,
                    "headline": "Headline",
                    "datetime": "2026-07-24T12:00:00Z",
                    "source": "GlobeNewswire",
                    "summary": "<p>Summary text.</p>",
                }
            ]

        async def stories(newsids, use_cache=True):
            return {"42": {"story": "<p>The body.</p>"}}

        monkeypatch.setattr(news, "get_news_page", page)
        monkeypatch.setattr(news, "get_stories", stories)

    async def test_an_article_carries_the_widget_shape(self, wired):
        from openbb_tmx.routers.news import feed

        articles = await feed(symbol="AC", limit=1)
        article = articles[0]

        assert sorted(article) == ["author", "body", "date", "excerpt", "title", "url"]
        assert article["title"] == "Headline"
        assert article["author"] == "GlobeNewswire"
        assert article["url"] == "https://money.tmx.com/en/news/42"
        assert article["body"] == "The body."
        assert article["excerpt"] == "Summary text."

    async def test_the_body_may_be_skipped(self, monkeypatch, wired):
        from openbb_tmx.routers.news import feed

        async def unexpected(newsids, use_cache=True):
            raise AssertionError("the stories should not be read")

        monkeypatch.setattr(news, "get_stories", unexpected)
        articles = await feed(symbol="AC", limit=1, fetch_body=False)

        assert articles[0]["body"] == "Summary text."

    async def test_an_article_without_a_story_falls_back(self, monkeypatch, wired):
        from openbb_tmx.routers.news import feed

        async def empty(newsids, use_cache=True):
            return {}

        monkeypatch.setattr(news, "get_stories", empty)
        articles = await feed(symbol="AC", limit=1)

        assert articles[0]["body"] == "Summary text."


class TestFeedWidget:
    """The widget the feed registers."""

    def test_the_feed_is_a_newsfeed_widget(self):
        import warnings

        warnings.filterwarnings("ignore")
        from openbb_core.api.rest_api import app
        from openbb_platform_api.utils.widgets import build_json

        widget = build_json(app.openapi(), [])["tmx_news_feed_custom_obb"]

        assert widget["type"] == "newsfeed"
        assert widget["source"] == ["TMX"]
        assert {p["paramName"] for p in widget["params"]} >= {
            "symbol",
            "limit",
            "offset",
            "fetch_body",
        }


class TestTopics:
    """The subject tagging on an article."""

    def test_nothing_parses_to_nothing(self):
        assert news.parse_topics(None) == []
        assert news.parse_topics("") == []

    def test_tickers_and_mnemonics_are_dropped(self):
        raw = "[AC:CA,RY:CA,WEBCONTM,TEL10802,BANKING/FINANCIAL SERVICES]"

        assert news.parse_topics(raw) == ["BANKING/FINANCIAL SERVICES"]

    def test_a_label_carrying_a_comma_stays_whole(self):
        raw = "[ACQUISITIONS, MERGERS, TAKEOVERS,BANKFINA,EARNINGS RELEASES]"

        assert news.parse_topics(raw) == [
            "ACQUISITIONS, MERGERS, TAKEOVERS",
            "EARNINGS RELEASES",
        ]

    def test_subjects_are_sorted_and_unique(self):
        raw = "[MEDIA AND ENTERTAINMENT,REAL ESTATE,MEDIA AND ENTERTAINMENT]"

        assert news.parse_topics(raw) == ["MEDIA AND ENTERTAINMENT", "REAL ESTATE"]


class TestMarketNews:
    """News across a basket of symbols."""

    @pytest.fixture
    def basket(self, monkeypatch):
        """Serve numbered basket articles."""

        async def request(operation, query, variables, **kwargs):
            page = variables["page"]
            limit = variables["limit"]
            start = (page - 1) * limit

            return {
                "news": [
                    {
                        "newsid": start + i,
                        "headline": f"Article {start + i}",
                        "datetime": "2026-07-24T12:00:00Z",
                        "source": "Wire",
                        "summary": "s",
                        "topic": "[RY:CA,BANKING/FINANCIAL SERVICES]"
                        if (start + i) % 2 == 0
                        else "[RY:CA,REAL ESTATE]",
                    }
                    for i in range(limit)
                ]
            }

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", request)

    async def test_a_basket_is_read(self, basket):
        rows = await news.get_market_news(["RY", "TD"], limit=5)

        assert [r["newsid"] for r in rows] == [0, 1, 2, 3, 4]

    async def test_an_offset_skips_articles(self, basket):
        rows = await news.get_market_news(["RY"], limit=3, offset=4)

        assert [r["newsid"] for r in rows] == [4, 5, 6]

    async def test_an_exhausted_basket_stops(self, monkeypatch):
        async def nothing(*args, **kwargs):
            return {"news": []}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", nothing)

        assert await news.get_market_news(["RY"], limit=5) == []

    async def test_the_command_shapes_and_filters(self, basket, monkeypatch):
        from openbb_tmx.routers.news import market

        async def stories(newsids, use_cache=True):
            return {}

        monkeypatch.setattr(news, "get_stories", stories)
        articles = await market(symbols="RY,TD", topic="REAL ESTATE", limit=3)

        assert articles
        assert all("REAL ESTATE" in a["topics"] for a in articles)
        assert all(
            a["url"].startswith("https://money.tmx.com/en/news/") for a in articles
        )

    async def test_the_topics_endpoint_lists_the_subjects(self, basket):
        from openbb_tmx.routers.news import news_topics

        options = await news_topics(symbols="RY,TD")

        assert {o["label"] for o in options} == {
            "BANKING/FINANCIAL SERVICES",
            "REAL ESTATE",
        }
        assert all(o["label"] == o["value"] for o in options)


class TestBlogFeed:
    """The editorial feed."""

    FEED = (
        "<rss><channel><title>TMX Money Blog</title>"
        "<item><title>Post One</title><link>https://x.test/1</link>"
        "<pubDate>Mon, 20 Jul 2026 10:00:00 +0000</pubDate>"
        "<description>A summary.</description>"
        "<content:encoded><![CDATA[<p>The body.</p>]]></content:encoded>"
        "<category>TSX30</category></item>"
        "</channel></rss>"
    )

    @pytest.fixture
    def feed(self, monkeypatch):
        """Serve one editorial post."""

        async def request(operation, query, variables, **kwargs):
            return {"getFeed": {"feed": self.FEED}}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", request)

    async def test_a_post_is_shaped_for_the_widget(self, feed):
        posts = await news.get_blog_feed()

        assert len(posts) == 1
        post = posts[0]

        assert post["title"] == "Post One"
        assert post["url"] == "https://x.test/1"
        assert post["author"] == "TMX Money"
        assert post["body"] == "The body."
        assert post["excerpt"] == "A summary."
        assert post["topics"] == ["TSX30"]

    async def test_an_empty_feed_yields_nothing(self, monkeypatch):
        async def request(*args, **kwargs):
            return {"getFeed": {"feed": ""}}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", request)

        assert await news.get_blog_feed() == []

    async def test_the_command_serves_the_feed(self, feed):
        from openbb_tmx.routers.news import blog

        assert (await blog())[0]["title"] == "Post One"


class TestNewsWidgets:
    """Every news surface registers as a feed."""

    def test_all_three_feeds_are_registered(self):
        import warnings

        warnings.filterwarnings("ignore")
        from openbb_core.api.rest_api import app
        from openbb_platform_api.utils.widgets import build_json

        widgets = build_json(app.openapi(), [])

        for name in ("feed", "market", "blog"):
            widget = widgets[f"tmx_news_{name}_custom_obb"]

            assert widget["type"] == "newsfeed"
            assert widget["source"] == ["TMX"]


class TestSearch:
    """The corpus search."""

    SCRIPT = (
        "(function(){ var results = null; results = JSON.parse('"
        '{"metadata":{"query":"drilling","total":44837,"endindex":2},'
        '"items":[{"title":"Rose Begins Drilling","link":"5198340031394687",'
        '"description":"A summary.","pubdate":"Jul 24, 2026","ticker":"CRB",'
        '"contenttype":"News","feedname":"TheNewswire"},'
        '{"title":"Second Result","link":"6006198820983123","description":"More.",'
        '"pubdate":"Jul 23, 2026","ticker":"SCOT","contenttype":"News",'
        '"feedname":"Newsfile"}]}'
        "'); })();"
    )

    def test_the_payload_is_lifted_from_the_script(self):
        payload = news._read_search_payload(self.SCRIPT)

        assert payload["metadata"]["total"] == 44837
        assert len(payload["items"]) == 2

    def test_a_response_without_results_is_empty(self):
        assert news._read_search_payload("no assignment here") == {}
        assert news._read_search_payload(None) == {}

    def test_an_unparsable_payload_is_empty(self):
        assert news._read_search_payload("results = JSON.parse('{not json');") == {}

    async def test_an_empty_query_searches_nothing(self):
        assert await news.search_news("") == ([], 0)

    async def test_a_query_returns_its_results_and_total(self, monkeypatch):
        seen: dict = {}

        async def request(url, accept_type="json", use_cache=True, **kwargs):
            seen["url"] = url
            return self.SCRIPT

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", request)
        rows, total = await news.search_news("drilling", limit=2, offset=4)

        assert total == 44837
        assert [r["ticker"] for r in rows] == ["CRB", "SCOT"]
        assert "endindex=4" in seen["url"] and "batchsize=2" in seen["url"]
        assert "facetedvalue=News" in seen["url"]

    async def test_a_content_type_may_be_dropped(self, monkeypatch):
        seen: dict = {}

        async def request(url, accept_type="json", use_cache=True, **kwargs):
            seen["url"] = url
            return self.SCRIPT

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", request)
        await news.search_news("drilling", content_type="")

        assert "facetedkey" not in seen["url"]

    async def test_the_command_shapes_the_results(self, monkeypatch):
        from openbb_tmx.routers.news import search

        async def request(url, accept_type="json", use_cache=True, **kwargs):
            return self.SCRIPT

        async def stories(newsids, use_cache=True):
            return {"5198340031394687": {"story": "<p>The body.</p>"}}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", request)
        monkeypatch.setattr(news, "get_stories", stories)
        articles = await search(query="drilling", limit=2)

        assert [a["symbol"] for a in articles] == ["CRB", "SCOT"]
        assert articles[0]["url"] == "https://money.tmx.com/en/news/5198340031394687"
        assert articles[0]["author"] == "TheNewswire"
        assert articles[0]["body"] == "The body."
        assert articles[1]["body"] == "More."

    async def test_a_company_hit_links_to_its_quote(self, monkeypatch):
        from openbb_tmx.routers.news import search

        script = (
            "results = JSON.parse('"
            '{"metadata":{"total":7716},"items":[{"title":"Barrick","link":"GOLD",'
            '"description":"d","pubdate":"","ticker":"GOLD","contenttype":"Company"}]}'
            "');"
        )

        async def request(url, accept_type="json", use_cache=True, **kwargs):
            return script

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", request)
        articles = await search(query="gold", content_type="Company", fetch_body=False)

        assert articles[0]["url"] == "https://money.tmx.com/en/quote/GOLD"

    def test_the_search_registers_as_a_feed(self):
        import warnings

        warnings.filterwarnings("ignore")
        from openbb_core.api.rest_api import app
        from openbb_platform_api.utils.widgets import build_json

        widget = build_json(app.openapi(), [])["tmx_news_search_custom_obb"]

        assert widget["type"] == "newsfeed"
        assert {p["paramName"] for p in widget["params"]} >= {
            "query",
            "content_type",
            "limit",
            "offset",
        }
