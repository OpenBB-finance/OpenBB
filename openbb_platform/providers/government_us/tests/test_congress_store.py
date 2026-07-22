"""Tests for the SQLite-backed BILLSTATUS + member store."""

from datetime import date

from openbb_government_us.congress.models.congress_bills import (
    CongressBillsFetcher,
    CongressBillsQueryParams,
)
from openbb_government_us.congress.models.member_legislation import (
    CongressMemberLegislationFetcher,
    CongressMemberLegislationQueryParams,
)
from openbb_government_us.congress.utils import bulk, store


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


def test_store_bill_list_purges_empty_strings(monkeypatch, tmp_path):
    """A bill with no recorded action lists as None so the Data model validates."""
    monkeypatch.setattr(bulk, "_cache_dir", lambda: str(tmp_path))
    store.reset()
    record = {
        "bill_id": "119-hr-2",
        "number": 2,
        "type": "HR",
        "title": "Reserved for the Speaker",
        "originChamber": "House",
        "originChamberCode": "H",
        "updateDate": "2026-07-17T00:00:00Z",
        "updateDateIncludingText": "",
        "latestAction": {"actionDate": "", "text": ""},
    }
    store.ingest_bills(119, "hr", [record], [])

    row = store.list_bills(119, ["hr"], None, None, None, None, "desc")[0]
    assert row["latestAction"] == {"actionDate": None, "text": None}
    assert row["updateDateIncludingText"] is None

    result = CongressBillsFetcher.transform_data(
        CongressBillsQueryParams(sort_by="desc"), [row]
    )
    assert result[0].latest_action_date is None
    assert result[0].latest_action is None
    assert result[0].update_date == date(2026, 7, 17)


def test_store_legislation_purges_empty_strings(monkeypatch, tmp_path):
    """A sponsored bill with no recorded action lists as None, not ''."""
    monkeypatch.setattr(bulk, "_cache_dir", lambda: str(tmp_path))
    store.reset()
    record = {
        "bill_id": "119-hr-2",
        "number": 2,
        "type": "HR",
        "title": "Reserved for the Speaker.",
        "introducedDate": "2026-07-17",
        "latestAction": {"actionDate": "", "text": ""},
    }
    store.ingest_bills(
        119, "hr", [record], [("J000299", 119, "hr", "119-hr-2", "Sponsor")]
    )

    row = store.get_legislation("J000299", [119])[0]
    assert row["latest_action_date"] is None
    assert row["latest_action"] is None

    result = CongressMemberLegislationFetcher.transform_data(
        CongressMemberLegislationQueryParams(bioguide_id="J000299", congress=119), [row]
    )
    assert result[0].latest_action_date is None


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
