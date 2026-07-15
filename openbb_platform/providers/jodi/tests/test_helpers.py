"""Test the JODI provider helpers."""

import asyncio
import json
import threading
import time
import zipfile
from datetime import date
from io import BytesIO
from pathlib import Path

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from pandas import read_csv

from openbb_jodi.utils import constants, helpers

from .conftest import zip_bytes

FIXTURES = Path(__file__).parent / "fixtures"


def _fixture_frame(name: str = "oil_primary_sample.csv"):
    df = read_csv(FIXTURES / name, dtype=helpers.CSV_DTYPES)
    return helpers.clean_chunk(df)


def test_get_cache_directory(isolate_cache, monkeypatch, tmp_path):
    import openbb_core.app.utils as core_utils

    monkeypatch.setattr(
        core_utils, "get_user_cache_directory", lambda: str(tmp_path / "user")
    )
    path = isolate_cache()
    assert path == tmp_path / "user" / "jodi"
    assert path.is_dir()
    assert isolate_cache() == path


def test_write_cached_raw_atomic(tmp_path):
    helpers.write_cached_raw("file.zip", b"content")
    assert [p.name for p in tmp_path.iterdir()] == ["file.zip"]
    assert (tmp_path / "file.zip").read_bytes() == b"content"
    # Nested paths create their parent directory.
    helpers.write_cached_raw("oil_primary/manifest.json", b"{}")
    assert (tmp_path / "oil_primary" / "manifest.json").read_bytes() == b"{}"


def test_partition_filename():
    assert helpers.partition_filename("CRUDEOIL_INDPROD") == "CRUDEOIL_INDPROD.parquet"


def test_partition_filters():
    assert helpers.partition_filters(None, None, None, None) is None
    filters = helpers.partition_filters(
        {"US", "SA"}, {"KBD"}, date(2024, 1, 1), date(2024, 3, 31)
    )
    assert filters == [
        ("REF_AREA", "in", ["SA", "US"]),
        ("UNIT_MEASURE", "in", ["KBD"]),
        ("TIME_PERIOD", ">=", "2024-01"),
        ("TIME_PERIOD", "<=", "2024-03"),
    ]


def test_table_lock_serializes(tmp_path):
    handle = helpers.acquire_table_lock("oil_primary")
    acquired_at: dict[str, float] = {}

    def waiter():
        other = helpers.acquire_table_lock("oil_primary")
        acquired_at["at"] = time.perf_counter()
        helpers.release_table_lock(other)

    thread = threading.Thread(target=waiter)
    thread.start()
    time.sleep(0.3)
    released_at = time.perf_counter()
    helpers.release_table_lock(handle)
    thread.join(timeout=10)
    # The second holder could only proceed after the first released.
    assert acquired_at["at"] >= released_at


def test_acquire_table_lock_failure(tmp_path, monkeypatch):
    def boom(handle):
        raise RuntimeError("lock failed")

    monkeypatch.setattr(helpers, "_lock_handle_nt", boom)
    monkeypatch.setattr(helpers, "_lock_handle_posix", boom)
    with pytest.raises(RuntimeError, match="lock failed"):
        helpers.acquire_table_lock("oil_primary")


def test_source_meta():
    meta = helpers.source_meta(
        206,
        {
            "Content-Range": "bytes 0-0/23320973",
            "ETag": '"1a34eeb4554dd1:0"',
            "Last-Modified": "Thu, 25 Jun 2026 03:50:04 GMT",
        },
    )
    assert meta == {
        "etag": '"1a34eeb4554dd1:0"',
        "last_modified": "Thu, 25 Jun 2026 03:50:04 GMT",
        "size": 23320973,
    }
    # A complete (200) response reports its size in Content-Length.
    assert helpers.source_meta(200, {"Content-Length": "10"})["size"] == 10
    # An unknown total is reported as zero.
    assert helpers.source_meta(206, {"Content-Range": "bytes 0-0/*"})["size"] == 0
    assert helpers.source_meta(200, {}) == {
        "etag": "",
        "last_modified": "",
        "size": 0,
    }


def test_source_unchanged():
    cached = {"etag": '"a"', "last_modified": "Mon", "size": 10}
    # The strongest available validator decides.
    assert helpers.source_unchanged(cached, {"etag": '"a"', "size": 99})
    assert not helpers.source_unchanged(cached, {"etag": '"b"', "size": 10})
    # Missing ETag falls back to Last-Modified, then size.
    assert helpers.source_unchanged(cached, {"etag": "", "last_modified": "Mon"})
    assert not helpers.source_unchanged(cached, {"last_modified": "Tue"})
    assert helpers.source_unchanged({"size": 10}, {"size": 10})
    assert not helpers.source_unchanged({"size": 10}, {"size": 11})
    # Nothing comparable is treated as changed.
    assert not helpers.source_unchanged({}, {"etag": '"a"'})


class FakeResponse:
    """Bare response object for request_range header tests."""

    def __init__(self):
        self.status = 206
        self.headers = {"Content-Range": "bytes 0-0/2"}

    async def read(self):
        return b"x"


def test_request_range_headers(monkeypatch):
    import openbb_core.provider.utils.helpers as core_helpers

    captured: list[dict] = []

    async def fake_amake_request(url, timeout=60, response_callback=None, headers=None):
        captured.append(dict(headers))
        return await response_callback(FakeResponse(), None)

    monkeypatch.setattr(core_helpers, "amake_request", fake_amake_request)
    asyncio.run(helpers.request_range("http://x", 10, 0, 0, validator='"e"'))
    assert captured[0]["Range"] == "bytes=0-0"
    assert captured[0]["If-Range"] == '"e"'  # a mid-transfer swap returns 200
    asyncio.run(helpers.request_range("http://x", 10, 0, 0))
    assert "If-Range" not in captured[1]
    asyncio.run(helpers.request_range("http://x", 10))
    assert "Range" not in captured[2]


@pytest.mark.record_http
def test_download():
    body, meta = asyncio.run(helpers.download(constants.GAS_FILES_URL))
    assert b"publicationId" in body
    assert isinstance(meta, dict)


@pytest.mark.record_http
def test_download_error():
    url = "https://www.jodidata.org/_resources/files/downloads/oil-data/annual-csv/primary/1990.csv"
    with pytest.raises(OpenBBError, match="Status Code: 404"):
        asyncio.run(helpers.download(url))


class RangeServer:
    """Fake request_range serving a body with configurable behavior."""

    def __init__(
        self,
        body: bytes,
        ranges: bool = True,
        break_chunks: bool = False,
        raise_chunks: bool = False,
        etag: str = "",
    ):
        self.body = body
        self.ranges = ranges
        self.break_chunks = break_chunks
        self.raise_chunks = raise_chunks
        self.etag = etag
        self.calls: list[tuple[int | None, int | None]] = []
        self.validators: list[str] = []

    async def __call__(self, url, timeout, start=None, end=None, validator=""):
        self.calls.append((start, end))
        if start is None or not self.ranges:
            return 200, {"Content-Length": str(len(self.body))}, self.body
        if (start, end) != (0, 0):
            self.validators.append(validator)
        if self.raise_chunks and start > 0:
            raise ConnectionError("connection reset by the throttling server")
        if self.break_chunks and start > 0:
            return 200, {}, self.body  # a proxy mishandling the range
        chunk = self.body[start : end + 1]
        headers = {
            "Content-Range": f"bytes {start}-{start + len(chunk) - 1}/{len(self.body)}"
        }
        if self.etag:
            headers["ETag"] = self.etag
        return 206, headers, chunk


def test_download_without_range_support(monkeypatch):
    server = RangeServer(b"small body", ranges=False)
    monkeypatch.setattr(helpers, "request_range", server)
    body, meta = asyncio.run(helpers.download("http://x"))
    assert body == b"small body"
    assert meta["size"] == len(b"small body")
    assert server.calls == [(0, 0)]  # the probe returned the whole file


def test_download_single_chunk(monkeypatch):
    server = RangeServer(b"0123456789")
    monkeypatch.setattr(helpers, "request_range", server)
    body, meta = asyncio.run(helpers.download("http://x"))
    assert body == b"0123456789"
    assert meta["size"] == 10
    assert server.calls == [(0, 0), (0, 9)]


def test_download_segmented_sends_if_range(monkeypatch):
    body = bytes(range(256)) * 100
    server = RangeServer(body, etag='"v1"')
    monkeypatch.setattr(helpers, "request_range", server)
    monkeypatch.setattr(helpers, "MIN_RANGE_CHUNK", 4096)
    assert asyncio.run(helpers.download("http://x"))[0] == body
    assert len(server.calls) == 1 + 7  # probe + ceil(25600 / 4096) chunks
    # Every segment carries the probe's validator as If-Range.
    assert server.validators == ['"v1"'] * 7


def test_download_broken_chunks_falls_back(monkeypatch):
    body = bytes(range(256)) * 100
    server = RangeServer(body, break_chunks=True)
    monkeypatch.setattr(helpers, "request_range", server)
    monkeypatch.setattr(helpers, "MIN_RANGE_CHUNK", 4096)
    assert asyncio.run(helpers.download("http://x"))[0] == body
    assert server.calls[-1] == (None, None)  # the full-request fallback


def test_download_failed_chunk_falls_back(monkeypatch):
    body = bytes(range(256)) * 100
    server = RangeServer(body, raise_chunks=True)
    monkeypatch.setattr(helpers, "request_range", server)
    monkeypatch.setattr(helpers, "MIN_RANGE_CHUNK", 4096)
    # A dropped connection on one segment must not abort the download.
    assert asyncio.run(helpers.download("http://x"))[0] == body
    assert server.calls[-1] == (None, None)


def test_download_unknown_total_falls_back(monkeypatch):
    async def fake_request(url, timeout, start=None, end=None, validator=""):
        if start is not None:
            return 206, {"Content-Range": "bytes 0-0/*"}, b"x"
        return 200, {}, b"full body"

    monkeypatch.setattr(helpers, "request_range", fake_request)
    assert asyncio.run(helpers.download("http://x"))[0] == b"full body"


def test_download_fallback_error(monkeypatch):
    async def fake_request(url, timeout, start=None, end=None, validator=""):
        if start is not None:
            return 206, {"Content-Range": "bytes 0-0/*"}, b"x"
        return 500, {}, b""

    monkeypatch.setattr(helpers, "request_range", fake_request)
    with pytest.raises(OpenBBError, match="Status Code: 500"):
        asyncio.run(helpers.download("http://x"))


def test_download_probe_error(monkeypatch):
    async def fake_request(url, timeout, start=None, end=None, validator=""):
        return 404, {}, b""

    monkeypatch.setattr(helpers, "request_range", fake_request)
    with pytest.raises(OpenBBError, match="Status Code: 404"):
        asyncio.run(helpers.download("http://x"))


def test_probe_source(monkeypatch):
    async def ok(url, timeout, start=None, end=None, validator=""):
        return 206, {"Content-Range": "bytes 0-0/10", "ETag": '"a"'}, b"x"

    monkeypatch.setattr(helpers, "request_range", ok)
    assert asyncio.run(helpers.probe_source("http://x")) == {
        "etag": '"a"',
        "last_modified": "",
        "size": 10,
    }

    async def gone(url, timeout, start=None, end=None, validator=""):
        return 404, {}, b""

    monkeypatch.setattr(helpers, "request_range", gone)
    assert asyncio.run(helpers.probe_source("http://x")) == {}

    async def unreachable(url, timeout, start=None, end=None, validator=""):
        raise ConnectionError("network down")

    monkeypatch.setattr(helpers, "request_range", unreachable)
    assert asyncio.run(helpers.probe_source("http://x")) is None


def test_read_manifest(tmp_path):
    # Missing, corrupt, or incomplete manifests read as None.
    assert helpers.read_manifest("oil_primary") is None
    helpers.write_cached_raw("oil_primary/manifest.json", b"{corrupt")
    assert helpers.read_manifest("oil_primary") is None
    helpers.write_cached_raw("oil_primary/manifest.json", b"[]")
    assert helpers.read_manifest("oil_primary") is None
    helpers.write_cached_raw("oil_primary/manifest.json", b'{"source": {}}')
    assert helpers.read_manifest("oil_primary") is None
    manifest = {"source": {"url": "http://x"}, "checked_at": 1.0, "partitions": {}}
    helpers.write_manifest("oil_primary", manifest)
    assert helpers.read_manifest("oil_primary") == manifest


def test_bump_checked_at(tmp_path):
    newer = {
        "source": {"url": "http://new", "etag": '"n"'},
        "checked_at": 1.0,
        "partitions": {},
    }
    helpers.write_manifest("oil_primary", newer)
    snapshot = {
        "source": {"url": "http://old", "etag": '"o"'},
        "checked_at": 0.0,
        "partitions": {},
    }
    # A concurrent refresh's newer manifest is never clobbered.
    assert helpers.bump_checked_at("oil_primary", snapshot) == newer
    assert helpers.read_manifest("oil_primary")["checked_at"] == 1.0
    # A matching source bumps in place.
    bumped = helpers.bump_checked_at("oil_primary", dict(newer))
    assert bumped["checked_at"] > 1.0
    # A missing manifest is restored from the snapshot.
    (tmp_path / "oil_primary" / "manifest.json").unlink()
    restored = helpers.bump_checked_at("oil_primary", snapshot)
    assert restored["source"] == snapshot["source"]
    assert restored["checked_at"] > 0.0


def test_open_archive_csv(tmp_path):
    csv = b"REF_AREA,TIME_PERIOD\nUS,2024-01\n"
    plain = tmp_path / "plain.csv"
    plain.write_bytes(csv)
    with helpers.open_archive_csv(plain) as stream:
        assert stream.read() == csv  # a plain CSV passes through
    archive = tmp_path / "archive.zip"
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("data.csv", csv)
    archive.write_bytes(buffer.getvalue())
    with helpers.open_archive_csv(archive) as stream:
        assert stream.read() == csv


def test_open_archive_csv_no_member(tmp_path):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("readme.txt", "not a csv")
    path = tmp_path / "bad.zip"
    path.write_bytes(buffer.getvalue())
    with pytest.raises(OpenBBError, match="No CSV member"):
        with helpers.open_archive_csv(path):
            pass


def test_open_archive_csv_corrupt_zip(tmp_path):
    path = tmp_path / "corrupt.zip"
    path.write_bytes(b"PK\x03\x04 torn download bytes")
    with pytest.raises(OpenBBError, match="unreadable"):
        with helpers.open_archive_csv(path):
            pass


def test_clean_chunk_drops_na_tokens():
    raw = (
        b"REF_AREA,TIME_PERIOD,ENERGY_PRODUCT,FLOW_BREAKDOWN,UNIT_MEASURE,OBS_VALUE,ASSESSMENT_CODE\n"
        b"US,2024-01,CRUDEOIL,INDPROD,KBD,100.5,1\n"
        b"US,2024-02,CRUDEOIL,INDPROD,KBD,N/A,1\n"
        b"US,2024-03,CRUDEOIL,INDPROD,KBD,x,1\n"
        b"US,2024-04,CRUDEOIL,INDPROD,KBD,-,1\n"
    )
    df = helpers.clean_chunk(read_csv(BytesIO(raw), dtype=helpers.CSV_DTYPES))
    assert len(df) == 1
    assert df["OBS_VALUE"].iloc[0] == 100.5


def test_clean_chunk_bad_format():
    with pytest.raises(OpenBBError, match="Unexpected JODI file format"):
        helpers.clean_chunk(read_csv(BytesIO(b"a,b\n1,2\n")))


def test_ingest_table(tmp_path):
    source = tmp_path / "source.zip"
    source.write_bytes(zip_bytes(FIXTURES / "oil_primary_sample.csv"))
    partitions = helpers.ingest_table("oil_primary", source)
    directory = tmp_path / "oil_primary"
    # Only partition files remain: the staging files are converted and removed.
    assert sorted(p.name for p in directory.iterdir()) == sorted(
        helpers.partition_filename(name) for name in partitions
    )
    assert not list(tmp_path.glob("*.tmp"))
    assert all(
        name == f"{product}_{flow}" for name, (product, flow) in partitions.items()
    )
    # Every valid observation lands in exactly one partition.
    expected = _fixture_frame()
    total = sum(
        len(
            helpers.load_partitions(
                "oil_primary", {p}, {f}, {"partitions": {n: [p, f]}}
            )
        )
        for n, (p, f) in partitions.items()
    )
    assert total == len(expected)


def test_ingest_table_multi_chunk(tmp_path, monkeypatch):
    monkeypatch.setattr(helpers, "INGEST_CHUNK_ROWS", 5)
    source = tmp_path / "source.zip"
    source.write_bytes(zip_bytes(FIXTURES / "oil_primary_sample.csv"))
    partitions = helpers.ingest_table("oil_primary", source)
    manifest = {"partitions": partitions}
    df = helpers.load_partitions("oil_primary", None, None, manifest)
    assert len(df) == len(_fixture_frame())  # appended chunks, one header each


def test_ingest_table_bad_source(tmp_path):
    source = tmp_path / "source.html"
    source.write_bytes(b"<html><body>surprise maintenance page</body></html>")
    with pytest.raises(OpenBBError, match="Unexpected JODI file format"):
        helpers.ingest_table("oil_primary", source)
    # The staging directory is cleaned up and nothing is committed.
    assert not (tmp_path / "oil_primary").exists()
    assert not list(tmp_path.glob("*.tmp"))


def test_ingest_table_empty_source(tmp_path):
    source = tmp_path / "empty.csv"
    source.write_bytes(b"")
    with pytest.raises(OpenBBError, match="Unexpected JODI file format"):
        helpers.ingest_table("oil_primary", source)


def test_ingest_table_no_observations(tmp_path):
    header = (
        b"REF_AREA,TIME_PERIOD,ENERGY_PRODUCT,FLOW_BREAKDOWN,UNIT_MEASURE,"
        b"OBS_VALUE,ASSESSMENT_CODE\n"
    )
    source = tmp_path / "empty_table.csv"
    source.write_bytes(header)
    # Committing an empty table would destroy the existing good cache.
    with pytest.raises(OpenBBError, match="contains no observations"):
        helpers.ingest_table("oil_primary", source)
    assert not (tmp_path / "oil_primary").exists()
    assert not list(tmp_path.glob("*.tmp"))


def test_ingest_table_commit_retries_swap(tmp_path, monkeypatch):
    import shutil as shutil_module

    source = tmp_path / "source.zip"
    source.write_bytes(zip_bytes(FIXTURES / "oil_primary_sample.csv"))
    helpers.ingest_table("oil_primary", source)  # the directory now exists
    real_rmtree = shutil_module.rmtree
    failures = {"count": 0}

    def flaky_rmtree(path, *args, **kwargs):
        if failures["count"] == 0 and not kwargs.get("ignore_errors"):
            failures["count"] += 1
            raise OSError("a reader holds a partition file open")
        return real_rmtree(path, *args, **kwargs)

    monkeypatch.setattr(shutil_module, "rmtree", flaky_rmtree)
    partitions = helpers.ingest_table("oil_primary", source)
    assert partitions
    assert failures["count"] == 1  # the swap succeeded on the retry


def test_ingest_table_commit_swap_failure(tmp_path, monkeypatch):
    import shutil as shutil_module

    source = tmp_path / "source.zip"
    source.write_bytes(zip_bytes(FIXTURES / "oil_primary_sample.csv"))
    helpers.ingest_table("oil_primary", source)
    real_rmtree = shutil_module.rmtree

    def stuck_rmtree(path, *args, **kwargs):
        if kwargs.get("ignore_errors"):
            return real_rmtree(path, *args, **kwargs)
        raise OSError("the directory is locked open")

    monkeypatch.setattr(shutil_module, "rmtree", stuck_rmtree)
    with pytest.raises(OSError, match="locked open"):
        helpers.ingest_table("oil_primary", source)
    assert not list(tmp_path.glob("*.tmp"))  # staging cleaned on failure


def test_get_table_slice(tmp_path, mock_download):
    df = asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    assert not df.empty
    assert mock_download == [constants.OIL_TABLE_URLS["primary"]]
    # Only the manifest and partitions are kept: the spent archive is deleted.
    assert not (tmp_path / "oil_primary.zip").exists()
    assert not list(tmp_path.glob("*.tmp"))
    manifest = helpers.read_manifest("oil_primary")
    assert manifest is not None
    assert manifest["source"]["url"] == constants.OIL_TABLE_URLS["primary"]
    assert manifest["source"]["size"] > 0
    # A second call reads the partitions without touching the network.
    again = asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    assert again.equals(df)
    assert len(mock_download) == 1
    # Slices read only the requested partitions.
    sliced = asyncio.run(
        helpers.get_table_slice("oil_primary", {"CRUDEOIL"}, {"INDPROD"})
    )
    assert set(sliced["ENERGY_PRODUCT"]) == {"CRUDEOIL"}
    assert set(sliced["FLOW_BREAKDOWN"]) == {"INDPROD"}
    # Codes with no matching partition read as an empty, well-formed frame.
    empty = asyncio.run(helpers.get_table_slice("oil_primary", {"XXX"}, None))
    assert empty.empty
    assert list(empty.columns) == helpers.EXPECTED_COLUMNS
    # use_cache=False forces a fresh download.
    asyncio.run(helpers.get_table_slice("oil_primary", None, None, use_cache=False))
    assert len(mock_download) == 2


def test_get_table_slice_pushdown(mock_download):
    df = asyncio.run(
        helpers.get_table_slice(
            "oil_primary",
            {"CRUDEOIL"},
            {"INDPROD"},
            countries={"US"},
            units={"KBD"},
            start_date=date(2024, 1, 1),
            end_date=date(2024, 2, 29),
        )
    )
    # The country, unit, and period predicates filtered inside the reads.
    assert set(df["REF_AREA"]) == {"US"}
    assert set(df["UNIT_MEASURE"]) == {"KBD"}
    assert set(df["TIME_PERIOD"]) == {"2024-01", "2024-02"}
    # A pushdown filter matching nothing reads as an empty, well-formed frame.
    empty = asyncio.run(
        helpers.get_table_slice("oil_primary", None, None, countries={"FR"})
    )
    assert empty.empty
    assert list(empty.columns) == helpers.EXPECTED_COLUMNS


def test_get_table_slice_bad_body_not_cached(tmp_path, monkeypatch):
    async def fake_download(url: str, timeout: int = 600) -> tuple:
        return b"<html>surprise maintenance page</html>", {}

    monkeypatch.setattr(helpers, "download", fake_download)
    with pytest.raises(OpenBBError, match="Unexpected JODI file format"):
        asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    assert not (tmp_path / "oil_primary.zip").exists()
    assert helpers.read_manifest("oil_primary") is None
    assert not list(tmp_path.glob("*.tmp"))


def test_refresh_table_skips_when_fresh(mock_download):
    asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    # A refresh finding a fresh manifest (a concurrent process won) skips.
    manifest = asyncio.run(helpers.refresh_table("oil_primary"))
    assert manifest is not None
    assert len(mock_download) == 1


def test_refresh_clears_orphaned_temp(tmp_path, mock_download):
    orphan_dir = tmp_path / "oil_primary.999dead.tmp"
    orphan_dir.mkdir()
    (orphan_dir / "leftover.csv").write_bytes(b"from a crashed ingest")
    orphan_zip = tmp_path / "oil_primary.zip.999dead.tmp"
    orphan_zip.write_bytes(b"from a crashed download")
    legacy_zip = tmp_path / "oil_primary.zip"
    legacy_zip.write_bytes(b"kept by an older version")
    asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    assert not orphan_dir.exists()
    assert not orphan_zip.exists()
    assert not legacy_zip.exists()


def _age_manifest(table: str) -> dict:
    """Rewrite a table manifest as past due for revalidation."""
    manifest = helpers.read_manifest(table)
    manifest["checked_at"] = time.time() - 2 * helpers.REVALIDATE_INTERVAL
    helpers.write_manifest(table, manifest)
    return manifest


def test_ensure_table_revalidates_unchanged(mock_download, monkeypatch):
    asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    stale = _age_manifest("oil_primary")
    probes: list[str] = []

    async def fake_probe(url: str):
        probes.append(url)
        return dict(stale["source"])

    monkeypatch.setattr(helpers, "probe_source", fake_probe)
    asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    # The probe confirmed the source is unchanged: no new download.
    assert probes == [stale["source"]["url"]]
    assert len(mock_download) == 1
    assert helpers.read_manifest("oil_primary")["checked_at"] > stale["checked_at"]


def test_ensure_table_revalidates_changed(mock_download, monkeypatch):
    asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    _age_manifest("oil_primary")

    async def fake_probe(url: str):
        return {"etag": '"new-publication"', "last_modified": "", "size": 1}

    monkeypatch.setattr(helpers, "probe_source", fake_probe)
    asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    # The source changed: the table was downloaded again.
    assert len(mock_download) == 2


def test_ensure_table_serves_stale_when_unreachable(mock_download, monkeypatch):
    asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    stale = _age_manifest("oil_primary")

    async def fake_probe(url: str):
        return None

    monkeypatch.setattr(helpers, "probe_source", fake_probe)
    df = asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    # The source is unreachable: the cached table is served.
    assert not df.empty
    assert len(mock_download) == 1
    assert helpers.read_manifest("oil_primary")["checked_at"] > stale["checked_at"]


def test_ensure_table_serves_stale_on_probe_http_error(mock_download, monkeypatch):
    asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    _age_manifest("oil_primary")

    async def fake_probe(url: str):
        return {}  # the probe got a 503/404, not a transport failure

    monkeypatch.setattr(helpers, "probe_source", fake_probe)
    df = asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    # An HTTP error must never turn a healthy cache into an outage.
    assert not df.empty
    assert len(mock_download) == 1


def test_ensure_table_serves_stale_when_refresh_fails(mock_download, monkeypatch):
    asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    _age_manifest("oil_primary")

    async def fake_probe(url: str):
        return {"etag": '"new-publication"', "last_modified": "", "size": 1}

    async def broken_download(url: str, timeout: int = 600) -> tuple:
        raise OpenBBError(f"Failed to download {url} -> Status Code: 503")

    monkeypatch.setattr(helpers, "probe_source", fake_probe)
    monkeypatch.setattr(helpers, "download", broken_download)
    df = asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    # The refresh failed but a readable table is on disk: serve it.
    assert not df.empty
    assert helpers.manifest_is_fresh(helpers.read_manifest("oil_primary"))


def test_ensure_table_empty_source_preserves_cache(mock_download, monkeypatch):
    asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    good = helpers.read_manifest("oil_primary")
    _age_manifest("oil_primary")

    header = (
        b"REF_AREA,TIME_PERIOD,ENERGY_PRODUCT,FLOW_BREAKDOWN,UNIT_MEASURE,"
        b"OBS_VALUE,ASSESSMENT_CODE\n"
    )
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("empty.csv", header)

    async def fake_probe(url: str):
        return {"etag": '"regenerating"', "last_modified": "", "size": 1}

    async def empty_download(url: str, timeout: int = 600) -> tuple:
        return buffer.getvalue(), {"etag": '"regenerating"', "size": 1}

    monkeypatch.setattr(helpers, "probe_source", fake_probe)
    monkeypatch.setattr(helpers, "download", empty_download)
    df = asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    # A transiently empty source must not destroy the good cache.
    assert not df.empty
    assert helpers.read_manifest("oil_primary")["partitions"] == good["partitions"]


def test_gas_revalidation_unchanged(mock_download, monkeypatch):
    asyncio.run(helpers.get_table_slice("gas_world", None, None))
    stale = _age_manifest("gas_world")

    async def fake_probe(url: str):
        return dict(stale["source"])

    monkeypatch.setattr(helpers, "probe_source", fake_probe)
    df = asyncio.run(helpers.get_table_slice("gas_world", None, None))
    assert not df.empty
    # Revalidation refetched only the tiny listing, not the archive.
    assert len(mock_download) == 3
    assert mock_download[-1] == constants.GAS_FILES_URL


def test_gas_revalidation_rotated_publication(monkeypatch):
    publication = {"id": 1}
    archive_downloads: list[str] = []

    async def fake_download(url: str, timeout: int = 600) -> tuple:
        if url.endswith("web/files/gas"):
            listing = {
                "publicationId": publication["id"],
                "files": [{"filename": "GAS_world_NewFormat.zip", "format": "CSV"}],
            }
            return json.dumps(listing).encode(), {}
        archive_downloads.append(url)
        raw = (FIXTURES / "gas_sample.zip").read_bytes()
        return raw, {"etag": f'"{publication["id"]}"', "size": len(raw)}

    monkeypatch.setattr(helpers, "download", fake_download)
    asyncio.run(helpers.get_table_slice("gas_world", None, None))
    assert len(archive_downloads) == 1
    _age_manifest("gas_world")
    publication["id"] = 2
    asyncio.run(helpers.get_table_slice("gas_world", None, None))
    # The listing rotated to a new publication: the archive was refreshed.
    assert len(archive_downloads) == 2
    assert helpers.read_manifest("gas_world")["source"]["url"].endswith(
        "/2/GAS_world_NewFormat.zip"
    )


def test_gas_revalidation_listing_error(mock_download, monkeypatch):
    asyncio.run(helpers.get_table_slice("gas_world", None, None))
    _age_manifest("gas_world")

    async def broken_download(url: str, timeout: int = 600) -> tuple:
        raise OpenBBError(f"Failed to download {url} -> Status Code: 503")

    monkeypatch.setattr(helpers, "download", broken_download)
    df = asyncio.run(helpers.get_table_slice("gas_world", None, None))
    # The publisher API is down: the cached table is served.
    assert not df.empty
    assert len(mock_download) == 2


def test_get_table_slice_self_heal_redownloads(tmp_path, mock_download):
    asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    # Break one partition file: the table is downloaded and ingested again.
    name = next(iter(helpers.read_manifest("oil_primary")["partitions"]))
    (tmp_path / "oil_primary" / helpers.partition_filename(name)).unlink()
    df = asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    assert not df.empty
    assert len(mock_download) == 2
    assert (tmp_path / "oil_primary" / helpers.partition_filename(name)).exists()


def test_get_table_slice_unreadable(mock_download, monkeypatch):
    monkeypatch.setattr(helpers, "load_partitions", lambda *args, **kwargs: None)
    with pytest.raises(OpenBBError, match="could not be read"):
        asyncio.run(helpers.get_table_slice("oil_primary", None, None))


def test_concurrent_self_heal_single_rebuild(tmp_path, mock_download, monkeypatch):
    asyncio.run(helpers.get_table_slice("oil_primary", None, None))
    name = next(iter(helpers.read_manifest("oil_primary")["partitions"]))
    (tmp_path / "oil_primary" / helpers.partition_filename(name)).unlink()
    real_ingest = helpers.ingest_table
    ingests: list[str] = []

    def counting_ingest(table, source_path):
        ingests.append(table)
        return real_ingest(table, source_path)

    monkeypatch.setattr(helpers, "ingest_table", counting_ingest)

    async def two_at_once():
        return await asyncio.gather(
            helpers.get_table_slice("oil_primary", None, None),
            helpers.get_table_slice("oil_primary", None, None),
        )

    first, second = asyncio.run(two_at_once())
    assert first.equals(second)
    # The second query found the healed table instead of downloading again.
    assert ingests == ["oil_primary"]
    assert len(mock_download) == 2  # the initial build + one healing download


def test_get_gas_slice(mock_download):
    df = asyncio.run(helpers.get_table_slice("gas_world", None, None))
    assert not df.empty
    assert set(df["ENERGY_PRODUCT"].unique()) == {"NATGAS"}
    assert len(mock_download) == 2  # file listing + archive
    # A second call is served from the cache.
    asyncio.run(helpers.get_table_slice("gas_world", None, None))
    assert len(mock_download) == 2


def test_get_gas_no_csv_listed(monkeypatch):
    async def fake_download(url: str, timeout: int = 600) -> tuple:
        listing = (
            b'{"publicationId": 1, "files": [{"filename": "ivt.zip", "format": "IVT"}]}'
        )
        return listing, {}

    monkeypatch.setattr(helpers, "download", fake_download)
    with pytest.raises(OpenBBError, match="No CSV file is listed"):
        asyncio.run(helpers.get_table_slice("gas_world", None, None))


def test_get_gas_no_csv_member(monkeypatch):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("readme.txt", "not a csv")

    async def fake_download(url: str, timeout: int = 600) -> tuple:
        if url.endswith("web/files/gas"):
            return (FIXTURES / "files_gas.json").read_bytes(), {}
        return buffer.getvalue(), {}

    monkeypatch.setattr(helpers, "download", fake_download)
    with pytest.raises(OpenBBError, match="No CSV member"):
        asyncio.run(helpers.get_table_slice("gas_world", None, None))


def test_get_gas_plain_csv(monkeypatch):
    with zipfile.ZipFile(FIXTURES / "gas_sample.zip") as archive:
        raw_csv = archive.read("STAGING_world_NewFormat.csv")

    async def fake_download(url: str, timeout: int = 600) -> tuple:
        if url.endswith("web/files/gas"):
            listing = b'{"publicationId": 1, "files": [{"filename": "world.csv", "format": "CSV"}]}'
            return listing, {}
        return raw_csv, {}

    monkeypatch.setattr(helpers, "download", fake_download)
    df = asyncio.run(helpers.get_table_slice("gas_world", None, None))
    assert not df.empty


def test_concurrent_downloads_coalesce(mock_download):
    async def two_at_once():
        return await asyncio.gather(
            helpers.get_table_slice("oil_primary", None, None),
            helpers.get_table_slice("oil_primary", None, None),
        )

    first, second = asyncio.run(two_at_once())
    assert first.equals(second)  # the second request waited for the first download
    assert len(mock_download) == 1


def test_concurrent_gas_downloads_coalesce(mock_download):
    async def two_at_once():
        return await asyncio.gather(
            helpers.get_table_slice("gas_world", None, None),
            helpers.get_table_slice("gas_world", None, None),
        )

    first, second = asyncio.run(two_at_once())
    assert first.equals(second)
    assert len(mock_download) == 2  # one file listing + one archive


def test_prefetch_tables(mock_download):
    async def main():
        helpers.start_prefetch()
        loop = asyncio.get_running_loop()
        task = helpers._PREFETCH_TASKS[loop]
        helpers.start_prefetch()  # a second call must not start another task
        assert helpers._PREFETCH_TASKS[loop] is task
        await task

    asyncio.run(main())
    # Both oil tables and the gas listing + archive were fetched.
    assert len(mock_download) == 4
    # Every table is now cached and readable.
    assert helpers.read_manifest("oil_primary") is not None
    assert helpers.read_manifest("oil_secondary") is not None
    assert helpers.read_manifest("gas_world") is not None


def test_start_prefetch_without_loop():
    helpers.start_prefetch()  # outside an event loop: a quiet no-op
    assert not helpers._PREFETCH_TASKS


def test_get_filtered_oil_both_tables(mock_download):
    records = asyncio.run(
        helpers.get_filtered_oil(
            tables=["primary", "secondary"],
            countries=None,
            product_codes={"CRUDEOIL", "GASOLINE"},
            flow_codes={"INDPROD", "TOTDEMO"},
            unit_codes={"KBD"},
            start_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
        )
    )
    products = {row["ENERGY_PRODUCT"] for row in records}
    assert "CRUDEOIL" in products
    assert "GASOLINE" in products


def test_get_filtered_oil_empty(mock_download):
    from openbb_core.provider.utils.errors import EmptyDataError

    with pytest.raises(EmptyDataError, match="No results"):
        asyncio.run(
            helpers.get_filtered_oil(
                tables=["primary"],
                countries={"FR"},  # not in the fixture sample
                product_codes={"CRUDEOIL"},
                flow_codes={"INDPROD"},
                unit_codes={"KBD"},
                start_date=date(2024, 1, 1),
                end_date=date(2024, 3, 31),
            )
        )


def test_get_filtered_gas_empty(mock_download):
    from openbb_core.provider.utils.errors import EmptyDataError

    with pytest.raises(EmptyDataError, match="No results"):
        asyncio.run(
            helpers.get_filtered_gas(
                countries={"FR"},  # not in the fixture sample
                flow_codes={"INDPROD"},
                unit_codes={"M3"},
                start_date=date(2024, 1, 1),
                end_date=date(2024, 3, 31),
            )
        )


def _record(period, flow, value, area="US", assessment="1"):
    return {
        "REF_AREA": area,
        "TIME_PERIOD": period,
        "ENERGY_PRODUCT": "CRUDEOIL",
        "FLOW_BREAKDOWN": flow,
        "UNIT_MEASURE": "KBD",
        "OBS_VALUE": value,
        "ASSESSMENT_CODE": assessment,
    }


def test_build_field_table():
    records = [
        _record("2024-01", "TOTIMPSB", 2.0),
        _record("2024-01", "INDPROD", 1.0),
        _record("2024-02", "TOTIMPSB", 3.0),
    ]
    rows = helpers.build_field_table(
        records, "FLOW_BREAKDOWN", {"INDPROD": "production", "TOTIMPSB": "imports"}
    )
    # Columns follow the field-map order, not the record order.
    assert list(rows[0]) == ["date", "production", "imports"]
    assert rows[0] == {"date": date(2024, 1, 1), "production": 1.0, "imports": 2.0}
    # A missing observation is an explicit None, not a dropped column.
    assert rows[1] == {"date": date(2024, 2, 1), "production": None, "imports": 3.0}


def test_build_country_table():
    records = [
        _record("2024-01", "INDPROD", 10.0, area="US"),
        _record("2024-01", "INDPROD", 9.0, area="SA"),
    ]
    rows = helpers.build_country_table(records)
    assert rows == [
        {"date": date(2024, 1, 1), "saudi_arabia": 9.0, "united_states": 10.0}
    ]


def test_build_assessments():
    records = [
        _record("2024-01", "INDPROD", 1.0, assessment="3"),
        _record("2024-02", "INDPROD", 1.0, assessment="1"),
        _record("2024-01", "TOTIMPSB", 2.0, assessment="99"),
    ]
    result = helpers.build_assessments(
        records, "FLOW_BREAKDOWN", {"INDPROD": "production", "TOTIMPSB": "imports"}
    )
    # The most recent assessment wins; unknown codes are omitted.
    assert result == {"production": "Reasonable levels of comparability"}


def test_validate_country_param():
    assert helpers.validate_country_param(None, multiple=True, default=None) is None
    assert (
        helpers.validate_country_param("US, saudi arabia", multiple=True, default=None)
        == "united_states,saudi_arabia"
    )
    with pytest.raises(OpenBBError, match="Only one country"):
        helpers.validate_country_param("us,sa", multiple=False, default=None)
    with pytest.raises(OpenBBError, match="Invalid country"):
        helpers.validate_country_param("narnia", multiple=True, default=None)


def test_normalize_token():
    assert helpers.normalize_token(None, "kbd") == "kbd"
    assert helpers.normalize_token(" Crude Oil ", "kbd") == "crude_oil"


def test_resolve_date_range():
    start, end = helpers.resolve_date_range(None, None, 2002)
    assert start == date(2002, 1, 1)  # full-history default
    assert end == date.today()
    with pytest.raises(OpenBBError, match="start_date must be"):
        helpers.resolve_date_range(date(2024, 2, 1), date(2024, 1, 1), 2002)


def test_check_oil_dates():
    helpers.check_oil_dates(date(2002, 1, 1), date(2003, 1, 1))
    with pytest.raises(OpenBBError, match="The data starts in 2002"):
        helpers.check_oil_dates(date(2000, 1, 1), date(2001, 12, 31))


def test_check_gas_dates():
    helpers.check_gas_dates(date(2009, 1, 1), date(2010, 1, 1))
    with pytest.raises(OpenBBError, match="The data starts in 2009"):
        helpers.check_gas_dates(date(2007, 1, 1), date(2008, 12, 31))


def test_apply_filters():
    df = _fixture_frame()
    filtered = helpers.apply_filters(
        df,
        countries={"US"},
        products={"CRUDEOIL"},
        flows={"INDPROD"},
        units={"KBD"},
        start_date=date(2024, 1, 1),
        end_date=date(2024, 2, 29),
    )
    assert len(filtered) == 2
    assert set(filtered["REF_AREA"]) == {"US"}
    unfiltered = helpers.apply_filters(
        df,
        countries=None,
        products=None,
        flows=None,
        units=None,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
    )
    assert len(unfiltered) == len(df)
