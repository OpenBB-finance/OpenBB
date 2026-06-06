"""Tests for the SQLite-backed BILLSTATUS + member store."""

from openbb_congress_gov.utils import bulk, store


def _records() -> list[dict]:
    return [
        {
            "bill_id": "119-hr-1",
            "number": 1,
            "title": "A",
            "introducedDate": "2025-01-01",
        },
        {
            "bill_id": "119-hr-2",
            "number": 2,
            "title": "B",
            "introducedDate": "2025-01-02",
        },
    ]


def _listed(congress: int, bill_type: str) -> set:
    rows = store.list_bills(congress, [bill_type], None, None, None, None, "desc")
    return {row["bill_id"] for row in rows}


def test_store_roundtrip(monkeypatch, tmp_path):
    """Bill records, legislation rows, and passage tallies round-trip through the DB."""
    monkeypatch.setattr(bulk, "_cache_dir", lambda: str(tmp_path))
    store.reset()
    assert store.loaded_keys("bills") == set()
    assert store.get_bill("119-hr-1") is None

    leg = [("A000055", 119, "hr", "119-hr-1", "Sponsor")]
    store.ingest_bills(119, "hr", _records(), leg)

    assert _listed(119, "hr") == {"119-hr-1", "119-hr-2"}
    assert store.get_bill("119-hr-1")["title"] == "A"
    assert store.loaded_keys("bills") == {"119-hr"}
    legislation = store.get_legislation("A000055", [119])
    assert [r["bill_id"] for r in legislation] == ["119-hr-1"]
    assert legislation[0]["title"] == "A"
    assert store.get_legislation("A000055", []) == []
    assert store.get_legislation("A000055", [118]) == []

    # Re-ingesting a unit replaces its rows (idempotent) and clears stale sponsors.
    store.ingest_bills(119, "hr", _records()[:1], [])
    assert _listed(119, "hr") == {"119-hr-1"}
    assert store.get_legislation("A000055", [119]) == []

    # Passage is stored per Congress/chamber and summed across them on read.
    store.add_passage(119, "S", {"A000055": (3, 1)})
    store.add_passage(118, "S", {"A000055": (1, 0)})
    assert store.get_passage("A000055") == (4, 1)
    assert store.get_passage("ZZZ") is None
    # Re-ingesting one unit replaces it, never double-counts.
    store.add_passage(119, "S", {"A000055": (5, 2)})
    assert store.get_passage("A000055") == (6, 2)

    # Parsed blobs round-trip and delete.
    assert store.get_parsed("k") is None
    store.put_parsed("k", {"x": 1})
    assert store.get_parsed("k") == {"x": 1}
    store.delete_parsed("k")
    assert store.get_parsed("k") is None

    store.compact()
    store.reset()
    assert store.get_bill("119-hr-1") is None
    assert store.get_passage("A000055") is None
    assert _listed(119, "hr") == set()


def test_store_no_cache(monkeypatch):
    """Without a writable cache, every store operation is a safe no-op."""
    monkeypatch.setattr(bulk, "_cache_dir", lambda: None)
    assert store.loaded_keys("bills") == set()
    assert store.bills_loaded(119, "hr") is False
    assert store.get_bill("119-hr-1") is None
    assert store.list_bills(119, ["hr"], None, None, None, None, "desc") == []
    assert store.list_amendments(119, None) == []
    assert store.get_amendment("119-hamdt-1") is None
    assert store.get_legislation("A", [119]) == []
    assert store.get_passage("A") is None
    assert store.get_parsed("k") is None
    store.ingest_bills(119, "hr", [], [])
    store.ingest_legislation(119, "hr", [], [])
    store.add_passage(119, "S", {"A": (1, 1)})
    store.put_parsed("k", {"x": 1})
    store.delete_parsed("k")
    store.compact()
    store.reset()


def test_store_connect_error(monkeypatch, tmp_path):
    """An unopenable database path degrades to empty results instead of raising."""
    not_a_db = tmp_path / "blocker"
    not_a_db.write_text("x")
    monkeypatch.setattr(bulk, "_cache_dir", lambda: str(not_a_db))
    assert store.loaded_keys("bills") == set()
    assert store.get_bill("119-hr-1") is None
    assert store.get_passage("A") is None
