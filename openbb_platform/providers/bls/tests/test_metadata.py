"""Tests for the ``BlsMetadata`` singleton."""

import copy

import pytest

from openbb_bls.utils.metadata import BlsMetadata, BlsMetadataDependency


def test_singleton_identity(stub_cache_path):
    """``__new__`` returns the same instance on subsequent calls."""
    a = BlsMetadata()
    b = BlsMetadata()
    assert a is b


def test_deepcopy_returns_self(stub_cache_path):
    """``__deepcopy__`` returns ``self`` to short-circuit deepcopy walkers."""
    meta = BlsMetadata()
    assert copy.deepcopy(meta) is meta


def test_copy_returns_self(stub_cache_path):
    """``__copy__`` returns ``self`` so ``copy.copy`` also stops."""
    meta = BlsMetadata()
    assert copy.copy(meta) is meta


def test_call_returns_self(stub_cache_path):
    """The singleton is callable so it can stand in as a FastAPI dependency."""
    meta = BlsMetadata()
    assert meta() is meta


def test_reset_clears_state(stub_cache_path):
    """``_reset`` zeroes both the instance and the initialised flag."""
    BlsMetadata()
    assert BlsMetadata._instance is not None
    assert BlsMetadata._initialized is True
    BlsMetadata._reset()
    assert BlsMetadata._instance is None
    assert BlsMetadata._initialized is False


def test_categories_populated_from_index(stub_cache_path):
    """``categories`` reflects the keys parsed from ``index.json``."""
    meta = BlsMetadata()
    assert meta.categories == ["cpi", "ppi"]
    assert meta.category_info("cpi") == {
        "name": "Consumer Price Index",
        "surveys": ["cu"],
        "series_count": 2,
    }
    assert meta.category_info("missing") == {}


def test_get_series_lazy_and_memoised(stub_cache_path):
    """``get_series`` reads the CSV once and caches the result."""
    meta = BlsMetadata()
    df1 = meta.get_series("cpi")
    df2 = meta.get_series("cpi")
    assert df1 is df2
    assert list(df1["series_id"]) == ["CUUR0000SA0", "CUUR0000SAF1"]


def test_get_codes_lazy_and_memoised(stub_cache_path):
    """``get_codes`` reads JSON once and caches the result."""
    meta = BlsMetadata()
    a = meta.get_codes("cpi")
    b = meta.get_codes("cpi")
    assert a is b
    assert a["cu"]["area_code"]["0000"] == "U.S. city average"


def test_get_codes_missing_member_returns_empty(stub_cache_path):
    """``get_codes`` for a category lacking ``codes.json`` returns ``{}``."""
    meta = BlsMetadata()
    assert meta.get_codes("ppi") == {}


def test_unknown_category_raises_keyerror(stub_cache_path):
    """``get_series`` and ``get_codes`` raise ``KeyError`` for unknown keys."""
    meta = BlsMetadata()
    with pytest.raises(KeyError, match="Unknown BLS category"):
        meta.get_series("not-a-real-category")
    with pytest.raises(KeyError, match="Unknown BLS category"):
        meta.get_codes("not-a-real-category")


def test_missing_archive_skips_load(tmp_path, monkeypatch):
    """Absent archive leaves the singleton with empty state."""
    missing = tmp_path / "nope.zip"
    monkeypatch.setattr(
        "openbb_bls.utils.metadata._core._SHIPPED_CACHE_FILE",
        missing,
    )
    meta = BlsMetadata()
    assert meta.categories == []
    assert meta._archive_bytes is None


def test_open_without_archive_raises(tmp_path, monkeypatch):
    """``_open`` raises ``FileNotFoundError`` when there is no archive in memory."""
    missing = tmp_path / "nope.zip"
    monkeypatch.setattr(
        "openbb_bls.utils.metadata._core._SHIPPED_CACHE_FILE",
        missing,
    )
    meta = BlsMetadata()
    # Force the path through ``get_series`` -> ``_open`` after seeding the
    # index manually so the category lookup passes the gate.
    meta._index = {"cpi": {"surveys": ["cu"]}}
    with pytest.raises(FileNotFoundError, match="BLS cache archive not found"):
        meta.get_series("cpi")


def test_archive_without_index_json(tmp_path, make_stub_zip, monkeypatch):
    """An archive lacking ``index.json`` yields an empty category list."""
    archive = tmp_path / "no_index.zip"
    payload = make_stub_zip(include_index=False)
    archive.write_bytes(payload)
    monkeypatch.setattr(
        "openbb_bls.utils.metadata._core._SHIPPED_CACHE_FILE",
        archive,
    )
    meta = BlsMetadata()
    assert meta.categories == []
    assert meta._archive_bytes is not None


def test_dependency_wrapper_resolves_to_class(stub_cache_path):
    """``BlsMetadataDependency`` is an Annotated alias on ``BlsMetadata``."""
    args = getattr(BlsMetadataDependency, "__metadata__", ())
    assert args, "Annotated metadata should not be empty"
    origin = getattr(BlsMetadataDependency, "__origin__", None)
    assert origin is BlsMetadata


def test_init_no_op_when_already_initialised(stub_cache_path):
    """Calling ``__init__`` again is a no-op once the singleton is ready."""
    meta = BlsMetadata()
    sentinel = object()
    meta._index = sentinel  # type: ignore[assignment]
    BlsMetadata().__init__()
    assert meta._index is sentinel
