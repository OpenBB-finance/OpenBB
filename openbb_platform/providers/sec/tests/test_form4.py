"""Tests for the SEC Form 4 utilities."""

import asyncio
import sqlite3
from unittest.mock import Mock

import pandas
import pytest
from openbb_core.app import utils as app_utils
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_sec.utils import form4


@pytest.mark.asyncio
async def test_download_data_serializes_cached_calls(monkeypatch, tmp_path):
    """Cached calls serialize their lifecycle but retain per-URL concurrency."""

    class FakeDataFrame:
        """Minimal DataFrame replacement for empty parsed filings."""

        def __init__(self, *_args, **_kwargs):
            pass

        def to_sql(self, *_args, **_kwargs):
            """Stand in for a cache write."""

    real_sleep = asyncio.sleep
    active_urls = 0
    active_groups: dict[str, int] = {}
    max_active_urls = 0
    max_active_groups = 0

    async def fake_get_form_4_data(url):
        nonlocal active_urls, max_active_groups, max_active_urls
        group = url.split("/")[0]
        active_urls += 1
        active_groups[group] = active_groups.get(group, 0) + 1
        max_active_urls = max(max_active_urls, active_urls)
        max_active_groups = max(max_active_groups, len(active_groups))
        try:
            await real_sleep(0.02)
        finally:
            active_urls -= 1
            active_groups[group] -= 1
            if active_groups[group] == 0:
                del active_groups[group]
        return {}

    async def fake_parse_form_4_data(_data):
        return []

    async def skip_rate_limit_delay(_delay):
        await real_sleep(0)

    connections = []
    close_calls = []

    def fake_connect(_path):
        connection = object()
        connections.append(connection)
        return connection

    monkeypatch.setattr(app_utils, "get_user_cache_directory", lambda: str(tmp_path))
    monkeypatch.setattr(sqlite3, "connect", fake_connect)
    monkeypatch.setattr(pandas, "DataFrame", FakeDataFrame)
    monkeypatch.setattr(form4, "setup_database", lambda _conn: None)
    monkeypatch.setattr(form4, "get_cached_data", lambda _urls, _conn: [])
    monkeypatch.setattr(form4, "get_form_4_data", fake_get_form_4_data)
    monkeypatch.setattr(form4, "parse_form_4_data", fake_parse_form_4_data)
    monkeypatch.setattr(
        form4, "close_db", lambda conn, path: close_calls.append((conn, path))
    )
    monkeypatch.setattr(asyncio, "sleep", skip_rate_limit_delay)

    results = await asyncio.gather(
        form4.download_data(["first/1", "first/2"]),
        form4.download_data(["second/1", "second/2"]),
    )

    assert results == [[], []]
    assert len(connections) == 2
    assert len(close_calls) == 2
    assert max_active_groups == 1
    assert max_active_urls == 2


@pytest.mark.asyncio
async def test_download_data_handles_failure_before_connection(monkeypatch, tmp_path):
    """A cache failure before connect preserves the original error."""
    db_dir = tmp_path / "sql"
    db_dir.mkdir()
    (db_dir / "sec_form4.db.gz").write_bytes(b"corrupt")
    close_db = Mock()

    def fail_decompression(_db_path):
        raise OSError("corrupt cache")

    monkeypatch.setattr(app_utils, "get_user_cache_directory", lambda: str(tmp_path))
    monkeypatch.setattr(form4, "decompress_db", fail_decompression)
    monkeypatch.setattr(form4, "close_db", close_db)

    with pytest.raises(OpenBBError, match="OSError: corrupt cache"):
        await form4.download_data([])

    close_db.assert_not_called()
