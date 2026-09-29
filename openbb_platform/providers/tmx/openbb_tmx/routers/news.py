"""TMX News sub-router."""

from typing import Annotated

from fastapi import Query as FastAPIQuery
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OBBQuery
from openbb_core.app.router import Router

from openbb_tmx import NEWS_INSTALLED
from openbb_tmx.utils.choices import api_prefix as _api_prefix

router = Router(prefix="/news", description="TMX news.")


if not NEWS_INSTALLED:

    @router.command(
        model="TmxCompanyNews",
        examples=[
            APIEx(
                description="Company news and events.",
                parameters={"symbol": "AC", "provider": "tmx"},
            )
        ],
    )
    async def company(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Company news, press releases, and upcoming events."""
        return await OBBject.from_query(OBBQuery(**locals()))  # pragma: no cover


@router.command(
    methods=["GET"],
    widget_config={
        "name": "TMX News Feed",
        "description": "Company news from the TMX feed, with the full article body.",
        "type": "newsfeed",
        "category": "News",
        "subCategory": "TMX",
        "source": ["TMX"],
        "gridData": {"w": 20, "h": 15},
        "refetchInterval": 300000,
        "params": [
            {
                "paramName": "symbol",
                "label": "Symbol",
                "value": "AC",
                "description": "The symbol to read the news of.",
            },
            {
                "paramName": "limit",
                "label": "Limit",
                "value": 20,
                "description": "The number of articles to return.",
                "type": "number",
                "optional": True,
            },
            {
                "paramName": "offset",
                "label": "Offset",
                "value": 0,
                "description": "The number of articles to skip.",
                "type": "number",
                "optional": True,
            },
            {
                "paramName": "fetch_body",
                "label": "Fetch full body",
                "value": True,
                "description": "Read each article for its full body.",
                "type": "boolean",
                "optional": True,
            },
        ],
    },
    examples=[
        APIEx(
            description="The latest articles, with their bodies.",
            parameters={"symbol": "AC"},
        ),
        APIEx(
            description="The second page of headlines.",
            parameters={"symbol": "AC", "limit": 20, "offset": 20},
        ),
    ],
)
async def feed(
    symbol: Annotated[str, FastAPIQuery(description="The symbol to read.")] = "AC",
    limit: Annotated[
        int, FastAPIQuery(description="The number of articles to return.")
    ] = 20,
    offset: Annotated[
        int, FastAPIQuery(description="The number of articles to skip.")
    ] = 0,
    fetch_body: Annotated[
        bool, FastAPIQuery(description="Read each article for its full body.")
    ] = True,
    locale: Annotated[
        str, FastAPIQuery(description="The language to read, 'en' or 'fr'.")
    ] = "en",
) -> list[dict]:
    """Company news in the shape the news feed widget renders."""
    from openbb_tmx.utils.news import (
        ARTICLE_URL,
        excerpt,
        get_news_page,
        get_stories,
        html_to_markdown,
    )

    rows = await get_news_page(symbol, limit=limit, offset=offset, locale=locale)
    stories = (
        await get_stories([str(r.get("newsid")) for r in rows]) if fetch_body else {}
    )
    articles: list[dict] = []

    for row in rows:
        newsid = str(row.get("newsid"))
        story = stories.get(newsid) or {}
        summary = row.get("summary") or ""
        body = html_to_markdown(story.get("story")) or html_to_markdown(summary)
        articles.append(
            {
                "title": row.get("headline") or "",
                "date": row.get("datetime") or "",
                "author": row.get("source") or "TMX",
                "url": ARTICLE_URL.format(newsid=newsid),
                "excerpt": excerpt(summary),
                "body": body,
            }
        )

    return articles


@router.command(
    methods=["GET"],
    widget_config={
        "name": "TMX Market News",
        "description": "News across a basket of symbols, with the full article"
        + " body and its subject tagging.",
        "type": "newsfeed",
        "category": "News",
        "subCategory": "TMX",
        "source": ["TMX"],
        "gridData": {"w": 20, "h": 15},
        "refetchInterval": 300000,
        "params": [
            {
                "paramName": "symbols",
                "label": "Symbols",
                "value": "AC,RY,BCE,ENB,SHOP",
                "description": "The symbols the news should cover.",
            },
            {
                "paramName": "topic",
                "label": "Topic",
                "value": None,
                "description": "Keep only the articles carrying this subject.",
                "type": "endpoint",
                "optionsEndpoint": f"{_api_prefix()}/tmx/news/topics",
                "optionsParams": {"symbols": "$symbols"},
                "optional": True,
            },
            {
                "paramName": "limit",
                "label": "Limit",
                "value": 20,
                "type": "number",
                "optional": True,
            },
            {
                "paramName": "offset",
                "label": "Offset",
                "value": 0,
                "type": "number",
                "optional": True,
            },
            {
                "paramName": "fetch_body",
                "label": "Fetch full body",
                "value": True,
                "type": "boolean",
                "optional": True,
            },
        ],
    },
    examples=[
        APIEx(
            description="News across the large banks.",
            parameters={"symbols": "RY,TD,BMO,BNS,CM"},
        ),
        APIEx(
            description="Only the earnings coverage.",
            parameters={"symbols": "RY,TD", "topic": "FINANCIAL RESULTS"},
        ),
    ],
)
async def market(
    symbols: Annotated[
        str, FastAPIQuery(description="The symbols the news should cover.")
    ] = "AC,RY,BCE,ENB,SHOP",
    topic: Annotated[
        str | None,
        FastAPIQuery(description="Keep only the articles carrying this subject."),
    ] = None,
    limit: Annotated[int, FastAPIQuery(description="Articles to return.")] = 20,
    offset: Annotated[int, FastAPIQuery(description="Articles to skip.")] = 0,
    fetch_body: Annotated[
        bool, FastAPIQuery(description="Read each article for its full body.")
    ] = True,
    locale: Annotated[str, FastAPIQuery(description="The language to read.")] = "en",
) -> list[dict]:
    """News across a basket of symbols, in the news feed widget's shape."""
    from openbb_tmx.utils.news import (
        ARTICLE_URL,
        excerpt,
        get_market_news,
        get_stories,
        html_to_markdown,
        parse_topics,
    )

    basket = [s.strip() for s in symbols.split(",") if s.strip()]
    rows = await get_market_news(
        basket,
        limit=limit if not topic else max(limit * 5, 50),
        offset=offset,
        locale=locale,
    )

    if topic:
        wanted = topic.casefold()
        rows = [
            row
            for row in rows
            if any(wanted == t.casefold() for t in parse_topics(row.get("topic")))
        ][:limit]

    stories = (
        await get_stories([str(r.get("newsid")) for r in rows]) if fetch_body else {}
    )
    articles: list[dict] = []

    for row in rows:
        newsid = str(row.get("newsid"))
        summary = row.get("summary") or ""
        body = html_to_markdown((stories.get(newsid) or {}).get("story"))
        articles.append(
            {
                "title": row.get("headline") or "",
                "date": row.get("datetime") or "",
                "author": row.get("source") or "TMX",
                "url": ARTICLE_URL.format(newsid=newsid),
                "excerpt": excerpt(summary),
                "body": body or html_to_markdown(summary),
                "topics": parse_topics(row.get("topic")),
            }
        )

    return articles


@router.command(
    methods=["GET"],
    widget_config={
        "name": "TMX Money Blog",
        "description": "The TMX Money editorial feed, with the full post body.",
        "type": "newsfeed",
        "category": "News",
        "subCategory": "TMX",
        "source": ["TMX"],
        "gridData": {"w": 20, "h": 15},
        "refetchInterval": 900000,
    },
    examples=[APIEx(description="The latest posts.", parameters={})],
)
async def blog() -> list[dict]:
    """Read the TMX Money editorial feed, in the news feed widget's shape."""
    from openbb_tmx.utils.news import get_blog_feed

    return await get_blog_feed()


async def news_topics(symbols: str = "AC,RY,BCE,ENB,SHOP") -> list:
    """Serve the subjects the basket's articles are tagged with."""
    from openbb_tmx.utils.news import get_market_news, parse_topics

    basket = [s.strip() for s in symbols.split(",") if s.strip()]
    rows = await get_market_news(basket, limit=50)
    subjects: set[str] = set()

    for row in rows:
        subjects.update(parse_topics(row.get("topic")))

    return [{"label": s, "value": s} for s in sorted(subjects)]


router.api_router.add_api_route(
    path="/topics",
    endpoint=news_topics,
    methods=["GET"],
    include_in_schema=False,
)


@router.command(
    methods=["GET"],
    widget_config={
        "name": "TMX News Search",
        "description": "Search the published corpus by query string, with the"
        + " full article body.",
        "type": "newsfeed",
        "category": "News",
        "subCategory": "TMX",
        "source": ["TMX"],
        "gridData": {"w": 20, "h": 15},
        "refetchInterval": False,
        "params": [
            {
                "paramName": "query",
                "label": "Query",
                "value": "drilling",
                "description": "The words to search for.",
            },
            {
                "paramName": "content_type",
                "label": "Content",
                "value": "News",
                "description": "The kind of content to search.",
                "options": [
                    {"label": "News", "value": "News"},
                    {"label": "Company", "value": "Company"},
                    {"label": "Disclosure", "value": "CompanyDisclouser"},
                ],
                "optional": True,
            },
            {
                "paramName": "limit",
                "label": "Limit",
                "value": 20,
                "type": "number",
                "optional": True,
            },
            {
                "paramName": "offset",
                "label": "Offset",
                "value": 0,
                "type": "number",
                "optional": True,
            },
            {
                "paramName": "fetch_body",
                "label": "Fetch full body",
                "value": True,
                "type": "boolean",
                "optional": True,
            },
        ],
    },
    examples=[
        APIEx(description="Search the news.", parameters={"query": "drilling"}),
        APIEx(
            description="The second page of results.",
            parameters={"query": "lithium", "limit": 20, "offset": 20},
        ),
    ],
)
async def search(
    query: Annotated[str, FastAPIQuery(description="The words to search for.")] = "",
    content_type: Annotated[
        str, FastAPIQuery(description="The kind of content to search.")
    ] = "News",
    limit: Annotated[int, FastAPIQuery(description="Results to return.")] = 20,
    offset: Annotated[int, FastAPIQuery(description="Results to skip.")] = 0,
    fetch_body: Annotated[
        bool, FastAPIQuery(description="Read each article for its full body.")
    ] = True,
) -> list[dict]:
    """Search the published corpus, in the news feed widget's shape."""
    from openbb_tmx.utils.news import (
        ARTICLE_URL,
        excerpt,
        get_stories,
        html_to_markdown,
        search_news,
    )

    rows, _total = await search_news(
        query, limit=limit, offset=offset, content_type=content_type
    )
    newsids = [str(r.get("link")) for r in rows if str(r.get("link") or "").isdigit()]
    stories = await get_stories(newsids) if fetch_body and newsids else {}
    articles: list[dict] = []

    for row in rows:
        newsid = str(row.get("link") or "")
        summary = row.get("description") or ""
        body = html_to_markdown((stories.get(newsid) or {}).get("story"))
        articles.append(
            {
                "title": row.get("title") or "",
                "date": row.get("pubdate") or "",
                "author": row.get("feedname") or row.get("ticker") or "TMX",
                "url": ARTICLE_URL.format(newsid=newsid)
                if newsid.isdigit()
                else f"https://money.tmx.com/en/quote/{row.get('ticker') or ''}",
                "excerpt": excerpt(summary),
                "body": body or html_to_markdown(summary),
                "symbol": row.get("ticker") or "",
            }
        )

    return articles
