"""Shared fixtures for the openbb_jodi test suite."""

import json
import zipfile
from io import BytesIO
from pathlib import Path

import pytest
import yaml

FIXTURES = Path(__file__).parent / "fixtures"

# The fetcher tests cannot use record_http: their HTTP interactions are the
# bulk source archives (tens of MB), which must never be recorded. They use
# the jodi_cassette fixture instead, which replays an in-memory cassette
# synthesized from the trimmed fixtures. Each cassette holds exactly the
# interactions its test performs; strict replay fails on anything else.
CASSETTE_TESTS = {
    "test_jodi_oil_balance_fetcher": ("oil_primary",),
    "test_jodi_oil_production_fetcher": ("oil_primary",),
    "test_jodi_oil_demand_fetcher": ("oil_secondary",),
    "test_jodi_oil_demand_by_product_fetcher": ("oil_secondary",),
    "test_jodi_oil_imports_fetcher": ("oil_primary",),
    "test_jodi_oil_exports_fetcher": ("oil_primary",),
    "test_jodi_oil_stocks_fetcher": ("oil_primary",),
    "test_jodi_gas_balance_fetcher": ("gas_listing", "gas_archive"),
    "test_jodi_gas_production_fetcher": ("gas_listing", "gas_archive"),
    "test_jodi_gas_demand_fetcher": ("gas_listing", "gas_archive"),
    "test_jodi_gas_imports_fetcher": ("gas_listing", "gas_archive"),
    "test_jodi_gas_exports_fetcher": ("gas_listing", "gas_archive"),
    "test_jodi_gas_stocks_fetcher": ("gas_listing", "gas_archive"),
}


def zip_bytes(csv_path: Path) -> bytes:
    """Wrap a CSV fixture in a single-member zip, like the JODI archives."""
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"{csv_path.stem}.csv", csv_path.read_bytes())
    return buffer.getvalue()


def _interaction(url: str, body, status: int, reason: str, headers: dict) -> dict:
    """Build one vcr cassette interaction serving the given body."""
    return {
        "request": {"body": None, "headers": {}, "method": "GET", "uri": url},
        "response": {
            "body": {"string": body},
            "headers": {"Content-Length": [str(len(body))], **headers},
            "status": {"code": status, "message": reason},
        },
    }


def _archive_interaction(url: str, body: bytes) -> dict:
    """A served archive: binary body with the IIS cache validators."""
    return _interaction(
        url,
        body,
        200,
        "OK",
        {
            "Accept-Ranges": ["none"],
            "Content-Type": ["application/x-zip-compressed"],
            "ETag": [f'"{url.rsplit("/", 1)[-1]}"'],
            "Last-Modified": ["Wed, 24 Jun 2026 10:56:04 GMT"],
        },
    )


def _interaction_library() -> dict[str, dict]:
    """Build every synthesized JODI source interaction, keyed for CASSETTE_TESTS."""
    from openbb_jodi.utils.constants import (
        GAS_DOWNLOAD_URL,
        GAS_FILES_URL,
        OIL_TABLE_URLS,
    )

    listing_text = (FIXTURES / "files_gas.json").read_text(encoding="utf-8")
    listing = json.loads(listing_text)
    gas_file = next(
        f for f in listing["files"] if f.get("format") == "CSV" and not f.get("ignore")
    )
    gas_url = GAS_DOWNLOAD_URL.format(
        publication_id=listing["publicationId"], filename=gas_file["filename"]
    )
    return {
        "oil_primary": _archive_interaction(
            OIL_TABLE_URLS["primary"], zip_bytes(FIXTURES / "oil_primary_sample.csv")
        ),
        "oil_secondary": _archive_interaction(
            OIL_TABLE_URLS["secondary"],
            zip_bytes(FIXTURES / "oil_secondary_sample.csv"),
        ),
        "gas_listing": _interaction(
            GAS_FILES_URL,
            listing_text,
            200,
            "OK",
            {"Content-Type": ["application/json"]},
        ),
        "gas_archive": _archive_interaction(
            gas_url, (FIXTURES / "gas_sample.zip").read_bytes()
        ),
    }


class MemoryPersister:
    """A vcr persister that plays one in-memory cassette and never records."""

    def __init__(self, document: str):
        self.document = document

    def load_cassette(self, cassette_path, serializer):
        """Deserialize the in-memory cassette; the path is only a label."""
        from vcr.serialize import deserialize

        return deserialize(self.document, serializer)

    @staticmethod
    def save_cassette(cassette_path, cassette_dict, serializer):
        """Recording is disabled: the cassettes are synthesized from fixtures."""
        raise AssertionError(
            "The JODI source archives are never recorded;"
            " the cassettes are synthesized from the trimmed fixtures."
        )


@pytest.fixture
def jodi_cassette(request, monkeypatch):
    """Replay an in-memory cassette synthesized from the trimmed fixtures.

    The full pipeline executes against vcr's aiohttp interception; nothing is
    downloaded, no cassette file is stored, and live sockets are refused.
    """
    import socket

    import vcr

    def refuse(*args, **kwargs):
        raise AssertionError("jodi_cassette tests replay offline; no live sockets.")

    monkeypatch.setattr(socket, "getaddrinfo", refuse)
    library = _interaction_library()
    document = yaml.safe_dump(
        {
            "interactions": [library[key] for key in CASSETTE_TESTS[request.node.name]],
            "version": 1,
        }
    )
    vcr_object = vcr.VCR(record_mode="none")
    vcr_object.register_persister(MemoryPersister(document))
    with vcr_object.use_cassette(request.node.name) as cassette:
        yield cassette


@pytest.fixture(autouse=True)
def isolate_cache(tmp_path, monkeypatch):
    """Point the JODI cache at a temporary path and return the original getter."""
    from openbb_jodi.utils import helpers

    original = helpers.get_cache_directory
    monkeypatch.setattr(helpers, "get_cache_directory", lambda: tmp_path)
    state = (helpers._DOWNLOAD_LOCKS, helpers._PREFETCH_TASKS)
    for store in state:
        store.clear()
    yield original
    for store in state:
        store.clear()


@pytest.fixture
def mock_download(monkeypatch):
    """Serve trimmed samples of the live JODI files instead of downloading."""
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_jodi.utils import helpers

    files = {
        "world_Primary_CSV.zip": zip_bytes(FIXTURES / "oil_primary_sample.csv"),
        "world_Secondary_CSV.zip": zip_bytes(FIXTURES / "oil_secondary_sample.csv"),
        "web/files/gas": (FIXTURES / "files_gas.json").read_bytes(),
        "GAS_world_NewFormat.zip": (FIXTURES / "gas_sample.zip").read_bytes(),
    }
    calls: list[str] = []

    async def fake_download(url: str, timeout: int = 600) -> tuple:
        import asyncio

        await asyncio.sleep(0)  # yield, so concurrent requests contend for the lock
        calls.append(url)
        for suffix, content in files.items():
            if url.endswith(suffix):
                meta = {
                    "etag": f'"{suffix}"',
                    "last_modified": "Wed, 24 Jun 2026 10:56:04 GMT",
                    "size": len(content),
                }
                return content, meta
        raise OpenBBError(f"Failed to download {url} -> Status Code: 404")

    monkeypatch.setattr(helpers, "download", fake_download)
    return calls
