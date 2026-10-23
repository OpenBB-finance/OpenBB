"""Unit tests for ``openbb_sec.models.htm_file``."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_sec.models.htm_file import (
    SecHtmFileData,
    SecHtmFileFetcher,
    SecHtmFileQueryParams,
)


def test_htm_file_transform_query_empty_url():
    """htm_file.py:44 -> raise on empty URL."""
    with pytest.raises(OpenBBError) as exc:
        SecHtmFileFetcher.transform_query({"url": ""})
    assert "enter a URL" in str(exc.value)


def test_htm_file_transform_query_invalid_url():
    """htm_file.py:53 -> raise on a non-SEC / non-htm URL."""
    with pytest.raises(OpenBBError) as exc:
        SecHtmFileFetcher.transform_query({"url": "https://example.com/file.pdf"})
    assert "Invalid URL" in str(exc.value)


def test_htm_file_transform_query_valid_url():
    """htm_file.py happy path: a valid SEC htm URL is accepted."""
    url = "https://www.sec.gov/Archives/edgar/data/320193/x.htm"
    query = SecHtmFileFetcher.transform_query({"url": url})
    assert query.url == url


def test_htm_file_transform_query_missing_url_key():
    with pytest.raises(OpenBBError) as exc:
        SecHtmFileFetcher.transform_query({})
    assert "enter a URL" in str(exc.value)


def test_htm_file_transform_query_whitespace_url():
    with pytest.raises(OpenBBError) as exc:
        SecHtmFileFetcher.transform_query({"url": "   "})
    assert "enter a URL" in str(exc.value)


def test_htm_file_transform_query_non_string_url():
    with pytest.raises(OpenBBError) as exc:
        SecHtmFileFetcher.transform_query({"url": 12345})
    assert "enter a URL" in str(exc.value)


def test_htm_file_transform_query_invalid_scheme():
    with pytest.raises(OpenBBError) as exc:
        SecHtmFileFetcher.transform_query(
            {"url": "ftp://www.sec.gov/Archives/edgar/data/320193/x.htm"}
        )
    assert "http or https" in str(exc.value)


def test_htm_file_transform_query_lookalike_host():
    with pytest.raises(OpenBBError) as exc:
        SecHtmFileFetcher.transform_query(
            {"url": "https://sec.gov.evil.com/Archives/edgar/data/320193/x.htm"}
        )
    assert "host must be sec.gov" in str(exc.value)


def test_htm_file_transform_query_apex_sec_host_accepted():
    url = "https://sec.gov/Archives/edgar/data/320193/x.htm"
    query = SecHtmFileFetcher.transform_query({"url": url})
    assert query.url == url


def test_htm_file_transform_query_subdomain_sec_host_accepted():
    url = "https://efts.sec.gov/Archives/edgar/data/320193/x.html"
    query = SecHtmFileFetcher.transform_query({"url": url})
    assert query.url == url


def test_htm_file_transform_query_non_htm_path():
    with pytest.raises(OpenBBError) as exc:
        SecHtmFileFetcher.transform_query(
            {"url": "https://www.sec.gov/Archives/edgar/data/320193/x.pdf"}
        )
    assert "HTM or HTML file" in str(exc.value)


def test_htm_file_transform_query_strips_query_and_fragment():
    url = "https://www.sec.gov/Archives/edgar/data/320193/x.htm?evil=1#frag"
    query = SecHtmFileFetcher.transform_query({"url": url})
    assert query.url == "https://www.sec.gov/Archives/edgar/data/320193/x.htm"


def test_htm_file_transform_query_strips_surrounding_whitespace():
    url = "  https://www.sec.gov/Archives/edgar/data/320193/x.htm  "
    query = SecHtmFileFetcher.transform_query({"url": url})
    assert query.url == "https://www.sec.gov/Archives/edgar/data/320193/x.htm"


def test_htm_file_transform_query_query_string_with_htm_in_it_is_rejected():
    """Path must end in .htm/.html — query strings can't sneak past."""
    with pytest.raises(OpenBBError) as exc:
        SecHtmFileFetcher.transform_query(
            {"url": "https://www.sec.gov/Archives/edgar/data/320193/x.pdf?foo=bar.htm"}
        )
    assert "HTM or HTML file" in str(exc.value)


def test_htm_file_transform_data_empty_content():
    """htm_file.py:84 -> raise OpenBBError when content is missing."""
    with pytest.raises(OpenBBError) as exc:
        SecHtmFileFetcher.transform_data(
            query=None, data={"url": "https://www.sec.gov/x.htm", "content": ""}
        )
    assert "Failed to extract HTM file data" in str(exc.value)


def test_htm_file_transform_data_strips_row_attrs():
    """htm_file.py:90-95 -> style/class/bgcolor stripped from table rows."""
    content = (
        "<html><body><table>"
        "<tr class='x' bgcolor='#fff' style='background-color:#fff'>"
        "<td>1</td></tr></table></body></html>"
    )
    result = SecHtmFileFetcher.transform_data(
        query=None,
        data={"url": "https://www.sec.gov/x.htm", "content": content},
    )
    assert isinstance(result, SecHtmFileData)
    assert "bgcolor" not in result.content
    assert "class=" not in result.content
    assert "background-color" not in result.content
    assert "<td>1</td>" in result.content


def test_htm_file_aextract_data_returns_download(monkeypatch):
    captured: dict = {}

    def fake_download_file(url, read_html_table, use_cache):
        captured["url"] = url
        captured["read_html_table"] = read_html_table
        captured["use_cache"] = use_cache
        return "<html></html>"

    from openbb_sec.models import sec_filing

    monkeypatch.setattr(
        sec_filing.SecBaseFiling,
        "download_file",
        staticmethod(fake_download_file),
    )

    query = SecHtmFileQueryParams(
        url="https://www.sec.gov/Archives/edgar/data/320193/x.htm",
        use_cache=False,
    )
    result = asyncio.run(SecHtmFileFetcher.aextract_data(query, None))

    assert result["url"] == query.url
    assert result["content"] == "<html></html>"
    assert captured["url"] == query.url
    assert captured["read_html_table"] is False
    assert captured["use_cache"] is False
