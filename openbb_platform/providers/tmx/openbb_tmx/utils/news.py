"""The news feed, its stories, and the markdown they are rendered as."""

import re
from typing import Any

STORY_QUERY = """query getNewsStoryById($newsid: String!) {
  getNewsStoryById(newsid: $newsid) {
    headline
    story
    datetime
    source
  }
}"""

ARTICLE_URL = "https://money.tmx.com/en/news/{newsid}"

_TOPIC_SPLIT = re.compile(r",(?!\s)")

SEARCH_URL = "https://api.queryly.com/v4/search.aspx"

SEARCH_KEY = "7262bd5347e044d2"

CONTENT_TYPES = ("News", "Company", "CompanyDisclouser")

_RESULTS = re.compile(r"results\s*=\s*JSON\.parse\('(.*?)'\);", re.S)

_BLOCK_END = re.compile(r"</(p|div|h[1-6]|li|ul|ol|tr)\s*>", re.I)
_BREAK = re.compile(r"<br\s*/?>", re.I)
_LIST_ITEM = re.compile(r"<li[^>]*>", re.I)
_LINK = re.compile(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.I | re.S)
_IMAGE = re.compile(r'<img\b[^>]*src="([^"]+)"[^>]*>', re.I)
_BOLD = re.compile(r"</?(strong|b)\s*>", re.I)
_ITALIC = re.compile(r"</?(em|i)\s*>", re.I)
_TAG = re.compile(r"<[^>]+>")
_BLANKS = re.compile(r"\n{3,}")


def html_to_markdown(fragment: str | None) -> str:
    """Render a story's markup as markdown.

    Parameters
    ----------
    fragment : str or None
        The story as the feed publishes it.

    Returns
    -------
    str
        The story as markdown, with links, images, and emphasis preserved.
    """
    if not fragment:
        return ""

    from html import unescape

    text = fragment
    text = _IMAGE.sub(lambda m: f"\n![]({m.group(1)})\n", text)
    text = _LINK.sub(
        lambda m: f"[{_TAG.sub('', m.group(2)).strip()}]({m.group(1)})", text
    )
    text = _BOLD.sub("**", text)
    text = _ITALIC.sub("_", text)
    text = _LIST_ITEM.sub("\n- ", text)
    text = _BREAK.sub("\n", text)
    text = _BLOCK_END.sub("\n\n", text)
    text = _TAG.sub("", text)
    text = unescape(text)
    text = "\n".join(line.rstrip() for line in text.splitlines())

    return _BLANKS.sub("\n\n", text).strip()


def excerpt(text: str, limit: int = 280) -> str:
    """Shorten a summary to a single readable line.

    Parameters
    ----------
    text : str
        The summary as published.
    limit : int
        The greatest number of characters to keep.

    Returns
    -------
    str
        The shortened summary.
    """
    plain = " ".join(html_to_markdown(text).split())

    if len(plain) <= limit:
        return plain

    return plain[: limit - 1].rsplit(" ", 1)[0] + "…"


async def get_news_page(
    symbol: str,
    limit: int = 20,
    offset: int = 0,
    locale: str = "en",
    use_cache: bool = True,
) -> list[dict]:
    """Read one page of the symbol's news.

    Parameters
    ----------
    symbol : str
        The symbol to read the news of.
    limit : int
        The number of articles to return.
    offset : int
        The number of articles to skip.
    locale : str
        The language to read, 'en' or 'fr'.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    list[dict]
        One entry per article.
    """
    from openbb_tmx.utils import gql
    from openbb_tmx.utils.cache import amake_gql_request
    from openbb_tmx.utils.helpers import normalize_symbol

    symbol = normalize_symbol(symbol)
    limit = max(int(limit or 20), 1)
    offset = max(int(offset or 0), 0)
    first = offset // limit + 1
    wanted = offset % limit + limit
    rows: list[dict] = []
    page = first

    while len(rows) < wanted:
        response = await amake_gql_request(
            "getNewsForSymbol",
            gql.NEWS_FOR_SYMBOL,
            {"symbol": symbol, "page": page, "limit": limit, "locale": locale},
            symbol=symbol,
            use_cache=use_cache,
        )
        batch = (response or {}).get("getNewsForSymbol") or []

        if not batch:
            break

        rows.extend(batch)
        page += 1

    return rows[offset % limit :][:limit]


async def get_story(newsid: str, use_cache: bool = True) -> dict[str, Any]:
    """Read one article in full.

    Parameters
    ----------
    newsid : str
        The article id the feed published.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    dict
        The article, or an empty mapping when the feed has no story for it.
    """
    from openbb_tmx.utils.cache import amake_gql_request

    try:
        response = await amake_gql_request(
            "getNewsStoryById",
            STORY_QUERY,
            {"newsid": str(newsid)},
            symbol=str(newsid),
            use_cache=use_cache,
        )
    except Exception:  # noqa: BLE001
        return {}

    return (response or {}).get("getNewsStoryById") or {}


async def get_stories(newsids: "list[str]", use_cache: bool = True) -> dict[str, dict]:
    """Read several articles in full, concurrently.

    Parameters
    ----------
    newsids : list[str]
        The article ids to read.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    dict
        The article for each id that carried one.
    """
    import asyncio

    semaphore = asyncio.Semaphore(6)

    async def one(newsid: str) -> tuple[str, dict]:
        async with semaphore:
            return str(newsid), await get_story(newsid, use_cache)

    return dict(await asyncio.gather(*(one(n) for n in newsids)))


def parse_topics(raw: str | None) -> list[str]:
    """Read the readable subjects out of an article's topic tagging.

    Parameters
    ----------
    raw : str or None
        The topic tagging as published.

    Returns
    -------
    list[str]
        The subjects, sorted.
    """
    if not raw:
        return []

    subjects = set()

    for token in _TOPIC_SPLIT.split(raw.strip("[]")):
        subject = token.strip()

        if ":" in subject or any(c.isdigit() for c in subject):
            continue

        if " " in subject or "/" in subject:
            subjects.add(subject)

    return sorted(subjects)


async def get_market_news(
    symbols: "list[str]",
    limit: int = 20,
    offset: int = 0,
    locale: str = "en",
    use_cache: bool = True,
) -> list[dict]:
    """Read the news covering a basket of symbols.

    Parameters
    ----------
    symbols : list[str]
        The symbols the news should cover.
    limit : int
        The number of articles to return.
    offset : int
        The number of articles to skip.
    locale : str
        The language to read, 'en' or 'fr'.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    list[dict]
        One entry per article, each carrying its topic tagging.
    """
    from openbb_tmx.utils import gql
    from openbb_tmx.utils.cache import amake_gql_request
    from openbb_tmx.utils.helpers import normalize_symbol

    basket = [normalize_symbol(s) for s in symbols if s]
    limit = max(int(limit or 20), 1)
    offset = max(int(offset or 0), 0)
    wanted = offset + limit
    rows: list[dict] = []
    page = 1

    while len(rows) < wanted:
        response = await amake_gql_request(
            "getNewsForSymbols",
            gql.NEWS_FOR_SYMBOLS,
            {"symbols": basket, "page": page, "limit": limit, "locale": locale},
            symbol=",".join(basket),
            use_cache=use_cache,
        )
        batch = (response or {}).get("news") or []

        if not batch:
            break

        rows.extend(batch)
        page += 1

    return rows[offset:wanted]


async def get_blog_feed(use_cache: bool = True) -> list[dict]:
    """Read the TMX Money editorial feed.

    Returns
    -------
    list[dict]
        One entry per post, with its body already rendered as markdown.
    """
    from openbb_tmx.utils.cache import amake_gql_request

    query = 'query getFeed { getFeed(format: "rss") { feed } }'
    response = await amake_gql_request(
        "getFeed", query, {}, symbol="feed", use_cache=use_cache
    )
    blob = ((response or {}).get("getFeed") or {}).get("feed") or ""
    posts: list[dict] = []

    for chunk in re.findall(r"<item>(.*?)</item>", blob, re.S):
        posts.append(
            {
                "title": _rss_field(chunk, "title"),
                "url": _rss_field(chunk, "link"),
                "date": _rss_field(chunk, "pubDate"),
                "author": "TMX Money",
                "excerpt": excerpt(_rss_field(chunk, "description")),
                "body": html_to_markdown(
                    _rss_field(chunk, "content:encoded")
                    or _rss_field(chunk, "description")
                ),
                "topics": re.findall(
                    r"<category[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</category>",
                    chunk,
                    re.S,
                ),
            }
        )

    return posts


def _rss_field(chunk: str, tag: str) -> str:
    """Read one element out of an RSS item."""
    match = re.search(
        rf"<{tag}[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{tag}>", chunk, re.S
    )

    return match.group(1).strip() if match else ""


def _read_search_payload(script: str | None) -> dict:
    """Read the result set out of the search response.

    Parameters
    ----------
    script : str or None
        The response body.

    Returns
    -------
    dict
        The result set, or an empty mapping when none was assigned.
    """
    import json

    match = _RESULTS.search(script or "")

    if not match:
        return {}

    blob = match.group(1)
    blob = blob.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")

    try:
        return json.loads(blob)
    except ValueError:
        return {}


async def search_news(
    query: str,
    limit: int = 20,
    offset: int = 0,
    content_type: str = "News",
    use_cache: bool = True,
) -> "tuple[list[dict], int]":
    """Search the published corpus by query string.

    Parameters
    ----------
    query : str
        The words to search for.
    limit : int
        The number of results to return.
    offset : int
        The number of results to skip.
    content_type : str
        Restrict to one kind of content, such as 'News'.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    tuple[list[dict], int]
        The results, and the number the corpus holds for the query.
    """
    from urllib.parse import urlencode

    from openbb_tmx.utils.cache import amake_request

    if not query:
        return [], 0

    params = {
        "queryly_key": SEARCH_KEY,
        "query": query,
        "endindex": max(int(offset or 0), 0),
        "batchsize": max(int(limit or 20), 1),
        "callback": "",
        "extendeddatafields": "contenttype,ticker,guid",
    }

    if content_type:
        params["facetedkey"] = "contenttype"
        params["facetedvalue"] = content_type

    script = await amake_request(
        f"{SEARCH_URL}?{urlencode(params)}", accept_type="text", use_cache=use_cache
    )
    payload = _read_search_payload(script)

    return payload.get("items") or [], int(
        (payload.get("metadata") or {}).get("total") or 0
    )
