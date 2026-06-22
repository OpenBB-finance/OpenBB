"""Government of Canada discovery (router) tests."""

import asyncio
import functools
import importlib
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from hypothesis import (
    given,
    settings,
    strategies as st,
)
from openbb_core.app.router import Router
from openbb_core.provider.abstract.provider import Provider

from openbb_government_ca import government_ca_provider
from openbb_government_ca.government_ca_router import available_indicators, router
from openbb_government_ca.utils.catalog import CatalogReader, CatalogUnavailableError

generate_cache = importlib.import_module("openbb_government_ca.utils.generate_cache")

# A valid PID is exactly 8 numeric digits.
_valid_pid = st.text(alphabet="0123456789", min_size=8, max_size=8)
# Identifiers (dimension/codelist/code/attribute ids) use a safe, XML/JSON-clean
# alphabet so no escaping concerns arise.
_id_text = st.text(
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_",
    min_size=1,
    max_size=12,
)
# Human-readable labels include spaces and French accents to exercise non-ASCII
# handling through the serialize/compress round-trip.
_label = (
    st.text(
        alphabet=(
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789 éàùâêîôûçÉÀÈ-'()"
        ),
        min_size=1,
        max_size=24,
    )
    .map(str.strip)
    .filter(bool)
)
# A French label guaranteed to carry at least one non-ASCII character.
_french_label = st.builds(
    lambda accent, rest: accent + rest,
    st.sampled_from("éàùâêîôûçÉÀÈ"),
    _label,
)


@st.composite
def _catalog_and_lookups(draw):
    """Build a ``Catalog_Cache`` blob plus present and absent lookup keys.

    Each table is keyed by an 8-digit PID and mirrors a ``Normalized_Table_Entry``:
    a bilingual name whose French label always carries an accent, dimensions with
    code-to-bilingual-label pairs, and declared attributes. ``absent`` is a set of
    lookup keys (PID-shaped and arbitrary) guaranteed not to key any table.
    Examples are kept small/bounded for speed. Returns ``(blob, present, absent)``.
    """
    pids = draw(st.lists(_valid_pid, min_size=0, max_size=4, unique=True))
    tables: dict[str, dict] = {}
    for pid in pids:
        n_dims = draw(st.integers(min_value=0, max_value=3))
        dimensions = []
        for position in range(1, n_dims + 1):
            code_ids = draw(st.lists(_id_text, min_size=0, max_size=3, unique=True))
            codes = [
                {"code": code_id, "en": draw(_label), "fr": draw(_french_label)}
                for code_id in code_ids
            ]
            dimensions.append(
                {
                    "id": draw(_id_text),
                    "position": position,
                    "codelist_id": draw(_id_text.map(lambda s: "CL_" + s)),
                    "codes": codes,
                }
            )
        tables[pid] = {
            "pid": pid,
            "name": {"en": draw(_label), "fr": draw(_french_label)},
            "frequency": draw(
                st.sampled_from(["annual", "monthly", "quarterly", "undetermined"])
            ),
            "dimensions": dimensions,
            "attributes": draw(st.lists(_id_text, min_size=0, max_size=4, unique=True)),
        }

    # Candidate absent keys: PID-shaped and arbitrary strings, minus any present.
    candidates = draw(
        st.lists(st.one_of(_valid_pid, st.text(max_size=10)), min_size=0, max_size=6)
    )
    absent = {key for key in candidates if key not in tables}

    blob = {"schema_version": 1, "source": "statcan-sdmx", "tables": tables}
    return blob, list(tables), sorted(absent)


@contextmanager
def _no_network():
    """Force every socket creation to fail for the duration of the block.

    Any attempted network call raises ``AssertionError`` so an operation that
    silently reaches out would fail the test rather than pass quietly.
    """
    with mock.patch(
        "socket.socket",
        side_effect=AssertionError("unexpected network call"),
    ):
        yield


# Feature: government-ca-build-phase-1, Property 7
@settings(max_examples=100)
@given(_catalog_and_lookups())
def test_reader_and_discovery_perform_no_network_io(case):
    """Property 7: Reader and discovery perform no network I/O.

    With all socket creation forced to fail, every reader operation
    (construction/load + LZMA-decompression of a generated temp ``.json.xz``,
    arbitrary present and absent lookups) and any Discovery_Endpoint invocation
    complete successfully — demonstrating that no load, decompression, lookup,
    or discovery call attempts a network request. The test writes its own
    fixture and never depends on the build-time-generated asset.

    Validates: Requirements 9.2, 10.7
    """
    blob, present, absent = case

    with tempfile.TemporaryDirectory() as tmp:
        cache_file = Path(tmp) / "government_ca_cache.json.xz"
        cache_file.write_bytes(
            generate_cache.compress(generate_cache.serialize_catalog(blob))
        )

        # Build the event loop up front: its internal self-pipe is created with
        # sockets, so it must exist before we block socket creation. The command
        # under test opens no sockets, which is exactly what this asserts.
        loop = asyncio.new_event_loop()
        try:
            with _no_network():
                # 1. Construction/load + decompression of the generated catalog.
                reader = CatalogReader(cache_file=cache_file)

                # 2a. Lookup returns the exact entry for every present PID.
                for pid in present:
                    assert reader.lookup(pid) == blob["tables"][pid]
                # 2b. Lookup returns None for every absent PID.
                for pid in absent:
                    assert reader.lookup(pid) is None

                # 3. Discovery_Endpoint invocation. The command constructs a
                # CatalogReader with the DEFAULT (shipped) cache_file, so patch
                # the class the endpoint imports to bind the generated temp
                # fixture, then drive the async command to completion.
                expected = reader.indicators()
                with mock.patch(
                    "openbb_government_ca.utils.catalog.CatalogReader",
                    functools.partial(CatalogReader, cache_file=cache_file),
                ):
                    result = loop.run_until_complete(available_indicators())

                assert result == expected
        finally:
            loop.close()


# Feature: government-ca-build-phase-1, Property 8
@settings(max_examples=100)
@given(_catalog_and_lookups())
def test_discovery_content_and_cross_interface_equivalence(case):
    """Property 8: Discovery content and cross-interface equivalence.

    For any generated catalog, the Discovery_Endpoint returns a list whose length
    equals the number of catalog tables (an empty catalog yields ``[]``), each
    item being the discovery projection of the corresponding
    ``Normalized_Table_Entry`` (``pid``, ``name_en``, ``name_fr``, ``frequency``,
    dimension ids). The content obtained through the ``obb`` Python interface
    (awaiting the command coroutine directly) is identical to the content
    obtained through the REST API: a minimal FastAPI app exposing the same
    command, driven by a ``TestClient``. Both interfaces are bound to the SAME
    generated temp fixture; the test never depends on the build-time asset.

    Validates: Requirements 10.4, 10.6, 10.8
    """
    blob, _present, _absent = case

    # The discovery projection of every Normalized_Table_Entry, in catalog order.
    expected = [
        {
            "pid": entry["pid"],
            "name_en": entry["name"]["en"],
            "name_fr": entry["name"]["fr"],
            "frequency": entry["frequency"],
            "dimensions": [dim["id"] for dim in entry["dimensions"]],
        }
        for entry in blob["tables"].values()
    ]

    with tempfile.TemporaryDirectory() as tmp:
        cache_file = Path(tmp) / "government_ca_cache.json.xz"
        cache_file.write_bytes(
            generate_cache.compress(generate_cache.serialize_catalog(blob))
        )

        loop = asyncio.new_event_loop()
        try:
            # The command constructs a CatalogReader with the DEFAULT (shipped)
            # cache_file, so patch the class it imports to bind the generated temp
            # fixture. The single patch covers BOTH interfaces, guaranteeing they
            # read identical catalog content.
            with mock.patch(
                "openbb_government_ca.utils.catalog.CatalogReader",
                functools.partial(CatalogReader, cache_file=cache_file),
            ):
                # Python interface: await the command coroutine directly.
                python_result = loop.run_until_complete(available_indicators())

                # REST interface: drive the same command through a minimal
                # FastAPI app via TestClient, then read the JSON payload.
                app = FastAPI()
                app.add_api_route(
                    "/available_indicators",
                    available_indicators,
                    methods=["GET"],
                )
                response = TestClient(app).get("/available_indicators")
                assert response.status_code == 200
                rest_result = response.json()
        finally:
            loop.close()

    # Length equals the number of catalog tables; an empty catalog yields [].
    assert len(python_result) == len(blob["tables"])
    if not blob["tables"]:
        assert python_result == []
    # Each item is the discovery projection of the corresponding entry.
    assert python_result == expected
    # Cross-interface equivalence: REST content is identical to Python content.
    assert rest_result == python_result
    assert rest_result == expected


# --------------------------------------------------------------------------- #
# Example/edge tests (provider + router shape, discovery success/empty/error).
# These complement Properties 7 and 8 above and exercise specific requirements
# 10.1-10.6 and 11.3 with concrete cases.
# --------------------------------------------------------------------------- #


def _write_catalog(tmp: str, tables: dict) -> Path:
    """Write a compressed catalog fixture and return its path.

    Parameters
    ----------
    tmp : str
        A temporary directory the ``.json.xz`` fixture is written into.
    tables : dict
        The ``tables`` mapping (PID -> Normalized_Table_Entry) for the blob.

    Returns
    -------
    Path
        The path to the written ``government_ca_cache.json.xz`` fixture.
    """
    blob = {"schema_version": 1, "source": "statcan-sdmx", "tables": tables}
    cache_file = Path(tmp) / "government_ca_cache.json.xz"
    cache_file.write_bytes(
        generate_cache.compress(generate_cache.serialize_catalog(blob))
    )
    return cache_file


def test_provider_declares_zero_credentials():
    """Requirement 10.1: provider is a ``Provider`` declaring no credentials."""
    assert isinstance(government_ca_provider, Provider)
    assert government_ca_provider.credentials == []


def test_router_is_router_instance():
    """Requirement 10.2: the router is a core ``Router`` instance."""
    assert isinstance(router, Router)


def test_router_registers_exactly_one_command():
    """Requirement 10.3: exactly one Discovery_Endpoint is registered."""
    routes = router.api_router.routes
    assert len(routes) == 1
    assert routes[0].name == "available_indicators"
    assert routes[0].endpoint is available_indicators


def test_discovery_returns_within_two_seconds():
    """Requirement 10.4: discovery answers from the catalog within 2 seconds."""
    tables = {
        "00000001": {
            "pid": "00000001",
            "name": {"en": "CPI", "fr": "IPC"},
            "frequency": "monthly",
            "dimensions": [
                {"id": "GEO", "position": 1, "codelist_id": "", "codes": []}
            ],
            "attributes": [],
        }
    }
    with tempfile.TemporaryDirectory() as tmp:
        cache_file = _write_catalog(tmp, tables)
        loop = asyncio.new_event_loop()
        try:
            with mock.patch(
                "openbb_government_ca.utils.catalog.CatalogReader",
                functools.partial(CatalogReader, cache_file=cache_file),
            ):
                start = time.perf_counter()
                result = loop.run_until_complete(available_indicators())
                elapsed = time.perf_counter() - start
        finally:
            loop.close()

    assert elapsed < 2.0
    assert result == [
        {
            "pid": "00000001",
            "name_en": "CPI",
            "name_fr": "IPC",
            "frequency": "monthly",
            "dimensions": ["GEO"],
        }
    ]


def test_discovery_empty_catalog_returns_empty_list():
    """Requirement 10.6: an empty catalog yields ``[]`` rather than an error."""
    with tempfile.TemporaryDirectory() as tmp:
        cache_file = _write_catalog(tmp, {})
        loop = asyncio.new_event_loop()
        try:
            with mock.patch(
                "openbb_government_ca.utils.catalog.CatalogReader",
                functools.partial(CatalogReader, cache_file=cache_file),
            ):
                result = loop.run_until_complete(available_indicators())
        finally:
            loop.close()

    assert result == []


def test_discovery_missing_catalog_surfaces_error():
    """Requirement 10.5: a missing catalog surfaces an error, no partial list."""
    with tempfile.TemporaryDirectory() as tmp:
        missing = Path(tmp) / "does_not_exist.json.xz"
        loop = asyncio.new_event_loop()
        try:
            with mock.patch(
                "openbb_government_ca.utils.catalog.CatalogReader",
                functools.partial(CatalogReader, cache_file=missing),
            ):
                with pytest.raises(CatalogUnavailableError):
                    loop.run_until_complete(available_indicators())
        finally:
            loop.close()


def test_discovery_unreadable_catalog_surfaces_error():
    """Requirement 10.5: an unreadable catalog surfaces an error, no partial list."""
    with tempfile.TemporaryDirectory() as tmp:
        corrupt = Path(tmp) / "government_ca_cache.json.xz"
        # Not a valid LZMA/xz stream -> decompression fails on load.
        corrupt.write_bytes(b"not a valid xz payload")
        loop = asyncio.new_event_loop()
        try:
            with mock.patch(
                "openbb_government_ca.utils.catalog.CatalogReader",
                functools.partial(CatalogReader, cache_file=corrupt),
            ):
                with pytest.raises(CatalogUnavailableError):
                    loop.run_until_complete(available_indicators())
        finally:
            loop.close()
