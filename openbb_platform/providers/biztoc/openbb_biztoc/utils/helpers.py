"""Biztoc Helpers"""

from datetime import timedelta
from typing import Dict, List, Literal

import requests
import requests_cache
from openbb_core.app.utils import get_user_cache_directory

cache_dir = get_user_cache_directory()

biztoc_session_tags = requests_cache.CachedSession(
    f"{cache_dir}/http/biztoc_tags", expire_after=timedelta(days=1)
)
biztoc_session_sources = requests_cache.CachedSession(
    f"{cache_dir}/http/biztoc_sources", expire_after=timedelta(days=3)
)


def get_sources(api_key: str) -> List[Dict]:
    """Valid sources for Biztoc queries."""

    headers = {
        "X-RapidAPI-Key": f"{api_key}",
        "X-RapidAPI-Host": "biztoc.p.rapidapi.com",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
    }
    sources = biztoc_session_sources.get(
        "https://biztoc.p.rapidapi.com/sources", headers=headers, timeout=10
    )

    return sources.json()


def get_pages(api_key: str) -> List[str]:
    """Valid pages for Biztoc queries."""

    headers = {
        "X-RapidAPI-Key": f"{api_key}",
        "X-RapidAPI-Host": "biztoc.p.rapidapi.com",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
    }
    pages = biztoc_session_sources.get(
        "https://biztoc.p.rapidapi.com/pages", headers=headers, timeout=10
    )

    return pages.json()


def get_tags_by_page(page_id: str, api_key: str) -> List[str]:
    """Valid tags required for Biztoc queries."""

    headers = {
        "X-RapidAPI-Key": f"{api_key}",
        "X-RapidAPI-Host": "biztoc.p.rapidapi.com",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
    }
    tags = biztoc_session_tags.get(
        f"https://biztoc.p.rapidapi.com/tags/{page_id}", headers=headers, timeout=10
    )

    return tags.json()


def get_all_tags(api_key) -> Dict[str, List[str]]:
    tags: Dict[str, List[str]] = {}

    pages = get_pages(api_key)
    for page in pages:
        page_tags = get_tags_by_page(page, api_key)
        tags.update({page: [x["tag"] for x in page_tags]})

    return tags


def get_news(
    api_key: str,
    filter_: Literal[
        "crypto", "hot", "latest", "main", "media", "source", "tag"
    ] = "latest",
    source: str = "bloomberg",
    tag: str = "",
    term: str = "",
) -> List[Dict]:
    """Calls the BizToc API and returns the data."""

    results = []
    term = term.replace(" ", "%20") if term else ""
    _tags = get_all_tags(api_key)
    pages = get_pages(api_key)
    tags = []
    tag = tag.lower() if tag else ""
    for page in pages:
        tags.extend(_tags[page][:])

    _sources = get_sources(api_key)
    sources = sorted([i["id"] for i in _sources])

    headers = {
        "X-RapidAPI-Key": f"{api_key}",
        "X-RapidAPI-Host": "biztoc.p.rapidapi.com",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
    }

    filter_dict = {
        "hot": "news/hot",
        "latest": "news/latest",
        "crypto": "news/latest/crypto",
        "main": "news/latest/main",
        "media": "news/latest/media",
        "source": f"news/source/{source.lower()}",
        "tag": f"tag/{tag}",
    }
    if filter_ == "source" and source.lower() not in sources:
        raise ValueError(f"{source} not a valid source. Valid sources: {sources}")

    if filter_ == "tag" and tag.lower().replace(" ", "") not in tags:
        raise ValueError(f"{tag} not a valid tag. Valid tags: {tags}")

    url = (
        f"https://biztoc.p.rapidapi.com/search?q={term}"
        if term
        else f"https://biztoc.p.rapidapi.com/{filter_dict[filter_]}"
    )
    r = requests.get(url, headers=headers, timeout=5)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP error - > {r.text}")

    try:
        results = r.json()
    except Exception as e:
        raise (e)

    return results
