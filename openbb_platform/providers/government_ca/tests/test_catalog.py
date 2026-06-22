"""Government of Canada catalog reader tests."""

import importlib
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import pytest
from hypothesis import (
    given,
    settings,
    strategies as st,
)

from openbb_government_ca.utils.catalog import (
    CatalogReader,
    CatalogUnavailableError,
)

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
    lookup keys (PID-shaped and arbitrary) guaranteed not to key any table, so the
    ``None`` branch of ``lookup`` is exercised. Returns ``(blob, present, absent)``.
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


# Feature: government-ca-build-phase-1, Property 6
@settings(max_examples=100)
@given(_catalog_and_lookups())
def test_generator_reader_round_trip_and_lookup_totality(case):
    """Property 6: Generator → reader round-trip and lookup totality.

    For any catalog written to a temp ``.json.xz`` via the generator's
    serialize/compress helpers, a freshly constructed ``CatalogReader`` loads
    tables equal to the originals, and its ``lookup`` is total: it returns the
    exact ``Normalized_Table_Entry`` for any PID present in the catalog and
    ``None`` for any PID absent from it. The test writes its own fixture and
    never depends on the build-time-generated asset.

    Validates: Requirements 9.1, 9.3, 9.4, 9.5
    """
    blob, present, absent = case

    with tempfile.TemporaryDirectory() as tmp:
        cache_file = Path(tmp) / "government_ca_cache.json.xz"
        cache_file.write_bytes(
            generate_cache.compress(generate_cache.serialize_catalog(blob))
        )

        reader = CatalogReader(cache_file=cache_file)

        # Round-trip: the reader's discovery PID set matches the originals exactly,
        # so no table is dropped, duplicated, or invented during load+decompress.
        loaded_pids = {indicator["pid"] for indicator in reader.indicators()}
        assert loaded_pids == set(present)

        # (a) lookup returns the exact entry for every present PID.
        for pid in present:
            assert reader.lookup(pid) == blob["tables"][pid]

        # (b) lookup returns None for every absent PID.
        for pid in absent:
            assert reader.lookup(pid) is None


# A fixed, hand-written catalog blob mirroring two Normalized_Table_Entry
# records, with French accents and an empty-codes / empty-dimensions table to
# exercise the discovery projection without relying on the shipped asset.
_SAMPLE_BLOB = {
    "schema_version": 1,
    "source": "statcan-sdmx",
    "tables": {
        "18100004": {
            "pid": "18100004",
            "name": {
                "en": "Consumer Price Index, monthly",
                "fr": "Indice des prix à la consommation, mensuel",
            },
            "frequency": "monthly",
            "dimensions": [
                {
                    "id": "GEO",
                    "position": 1,
                    "codelist_id": "CL_GEO",
                    "codes": [{"code": "11124", "en": "Canada", "fr": "Canada"}],
                },
                {
                    "id": "PRODUCTS",
                    "position": 2,
                    "codelist_id": "CL_PRODUCTS",
                    "codes": [],
                },
            ],
            "attributes": ["OBS_STATUS", "SCALAR_FACTOR"],
        },
        "14100287": {
            "pid": "14100287",
            "name": {
                "en": "Labour force characteristics",
                "fr": "Caractéristiques de la population active",
            },
            "frequency": "monthly",
            "dimensions": [],
            "attributes": [],
        },
    },
}


@contextmanager
def _no_network():
    """Force every socket creation to fail for the duration of the block.

    Any attempted network call raises ``AssertionError`` so a reader operation
    that silently reaches out would fail the test rather than pass quietly.
    """
    with mock.patch(
        "socket.socket",
        side_effect=AssertionError("unexpected network call"),
    ):
        yield


def _write_cache(cache_file: Path, blob: dict) -> None:
    """Serialize+compress ``blob`` to ``cache_file`` via the generator helpers."""
    cache_file.write_bytes(
        generate_cache.compress(generate_cache.serialize_catalog(blob))
    )


def test_reader_round_trips_sample_catalog(tmp_path):
    """A valid cache round-trips to the expected tables, lookups, and indicators.

    Validates: Requirements 9.1, 9.2
    """
    cache_file = tmp_path / "government_ca_cache.json.xz"
    _write_cache(cache_file, _SAMPLE_BLOB)

    with _no_network():
        reader = CatalogReader(cache_file=cache_file)

        assert reader.indicators() == [
            {
                "pid": "18100004",
                "name_en": "Consumer Price Index, monthly",
                "name_fr": "Indice des prix à la consommation, mensuel",
                "frequency": "monthly",
                "dimensions": ["GEO", "PRODUCTS"],
            },
            {
                "pid": "14100287",
                "name_en": "Labour force characteristics",
                "name_fr": "Caractéristiques de la population active",
                "frequency": "monthly",
                "dimensions": [],
            },
        ]

        # lookup returns the exact entry for present PIDs ...
        assert reader.lookup("18100004") == _SAMPLE_BLOB["tables"]["18100004"]
        assert reader.lookup("14100287") == _SAMPLE_BLOB["tables"]["14100287"]
        # ... and None for an absent PID, with no network fetch.
        assert reader.lookup("99999999") is None


def test_reader_empty_catalog_yields_empty_indicators(tmp_path):
    """An empty catalog loads cleanly and ``indicators()`` returns ``[]``.

    Validates: Requirements 9.1, 9.2
    """
    cache_file = tmp_path / "government_ca_cache.json.xz"
    _write_cache(
        cache_file, {"schema_version": 1, "source": "statcan-sdmx", "tables": {}}
    )

    with _no_network():
        reader = CatalogReader(cache_file=cache_file)
        assert reader.indicators() == []
        assert reader.lookup("18100004") is None


def test_reader_missing_file_raises(tmp_path):
    """A missing cache asset raises ``CatalogUnavailableError`` without network.

    Validates: Requirements 9.6, 11.2
    """
    cache_file = tmp_path / "absent.json.xz"
    with _no_network(), pytest.raises(CatalogUnavailableError):
        CatalogReader(cache_file=cache_file)


def test_reader_truncated_payload_raises(tmp_path):
    """A truncated (undecompressable) payload raises ``CatalogUnavailableError``.

    Validates: Requirements 9.6, 11.2
    """
    cache_file = tmp_path / "government_ca_cache.json.xz"
    compressed = generate_cache.compress(generate_cache.serialize_catalog(_SAMPLE_BLOB))
    cache_file.write_bytes(compressed[: len(compressed) // 2])

    with _no_network(), pytest.raises(CatalogUnavailableError):
        CatalogReader(cache_file=cache_file)


def test_reader_non_json_payload_raises(tmp_path):
    """A decompressable but non-JSON payload raises ``CatalogUnavailableError``.

    Validates: Requirements 9.6, 11.2
    """
    cache_file = tmp_path / "government_ca_cache.json.xz"
    cache_file.write_bytes(generate_cache.compress(b"not valid json"))

    with _no_network(), pytest.raises(CatalogUnavailableError):
        CatalogReader(cache_file=cache_file)
