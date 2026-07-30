"""Tests for the ticker to parent holding-company RSSD resolver."""

from unittest.mock import MagicMock

from openbb_federal_reserve.utils import ticker


class TestNormalizeName:
    """Tests for ``normalize_name``."""

    def test_reconciles_legal_name_formats(self):
        """SEC and NIC formatting variants normalize to the same key."""
        assert ticker.normalize_name("JPMORGAN CHASE & CO") == ticker.normalize_name(
            "JPMorgan Chase & Co."
        )
        assert ticker.normalize_name(
            "BANK OF AMERICA CORP /DE/"
        ) == ticker.normalize_name("BANK OF AMERICA CORPORATION")

    def test_order_independent(self):
        """Token order does not change the key."""
        assert ticker.normalize_name("SCHWAB CHARLES CORP") == ticker.normalize_name(
            "CHARLES SCHWAB CORPORATION"
        )

    def test_empty_name(self):
        """An empty name yields an empty key."""
        assert ticker.normalize_name("") == ""


class TestIsParentHoldingCompany:
    """Tests for ``is_parent_holding_company``."""

    def test_holding_company_indicators(self):
        """Any holding-company indicator marks a parent."""
        assert ticker.is_parent_holding_company({"BHC_IND": "1"})
        assert ticker.is_parent_holding_company({"FHC_IND": "1"})
        assert ticker.is_parent_holding_company({"SLHC_IND": "1"})

    def test_non_holding_company(self):
        """A record without indicators is not a parent."""
        assert not ticker.is_parent_holding_company({"BHC_IND": "0"})


class TestFetchSecTickers:
    """Tests for ``fetch_sec_tickers``."""

    def test_flattens_to_ticker_map(self, monkeypatch):
        """The SEC file flattens to an uppercased ticker map."""
        response = MagicMock()
        response.json = lambda: {"0": {"ticker": "jpm", "title": "JPMORGAN CHASE"}}
        response.raise_for_status = MagicMock()
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: response,
        )
        assert ticker.fetch_sec_tickers()["JPM"] == "JPMORGAN CHASE"


class TestParentNameIndex:
    """Tests for ``parent_name_index``."""

    def test_indexes_only_parents(self, monkeypatch):
        """Only holding companies enter the index, keyed by normalized name."""
        records = [
            {"#ID_RSSD": "1039502", "NM_LGL": "JPMORGAN CHASE & CO.", "BHC_IND": "1"},
            {"#ID_RSSD": "852218", "NM_LGL": "JPMORGAN CHASE BANK NA", "BHC_IND": "0"},
        ]
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institutions",
            lambda status="active": records,
        )
        index = ticker.parent_name_index()
        assert index.get(ticker.normalize_name("JPMORGAN CHASE & CO")) == "1039502"
        assert ticker.normalize_name("JPMORGAN CHASE BANK NA") not in index


class TestResolveTickerToRssd:
    """Tests for ``resolve_ticker_to_rssd``."""

    def test_resolves_to_parent_rssd(self, monkeypatch):
        """A known ticker resolves to its parent holding company's RSSD."""
        monkeypatch.setattr(
            ticker, "fetch_sec_tickers", lambda: {"JPM": "JPMORGAN CHASE & CO"}
        )
        monkeypatch.setattr(
            ticker,
            "parent_name_index",
            lambda: {ticker.normalize_name("JPMORGAN CHASE & CO."): "1039502"},
        )
        assert ticker.resolve_ticker_to_rssd("jpm") == "1039502"

    def test_unknown_ticker_returns_none(self, monkeypatch):
        """A ticker absent from the SEC file resolves to ``None``."""
        monkeypatch.setattr(ticker, "fetch_sec_tickers", lambda: {})
        assert ticker.resolve_ticker_to_rssd("ZZZ") is None

    def test_no_parent_match_returns_none(self, monkeypatch):
        """A ticker with no parent-company name match resolves to ``None``."""
        monkeypatch.setattr(ticker, "fetch_sec_tickers", lambda: {"X": "SOME CO"})
        monkeypatch.setattr(ticker, "parent_name_index", lambda: {})
        assert ticker.resolve_ticker_to_rssd("X") is None


class TestControlledSubtree:
    """Tests for ``controlled_subtree``."""

    def test_traverses_active_controlled_links(self, monkeypatch):
        """Active controlled descendants of any depth are returned.

        A bank held through an intermediate holding company must still be
        reached, while ended and non-controlled links are excluded.
        """
        rels = [
            {  # direct intermediate
                "#ID_RSSD_PARENT": "P",
                "ID_RSSD_OFFSPRING": "MID",
                "RELN_LVL": "1",
                "CTRL_IND": "1",
                "DT_END": "99991231",
            },
            {  # bank held through the intermediate
                "#ID_RSSD_PARENT": "MID",
                "ID_RSSD_OFFSPRING": "BANK",
                "RELN_LVL": "1",
                "CTRL_IND": "1",
                "DT_END": "99991231",
            },
            {  # relationship has ended
                "#ID_RSSD_PARENT": "P",
                "ID_RSSD_OFFSPRING": "OLD",
                "RELN_LVL": "1",
                "CTRL_IND": "1",
                "DT_END": "20080630",
            },
            {  # not controlled (minority)
                "#ID_RSSD_PARENT": "P",
                "ID_RSSD_OFFSPRING": "MINORITY",
                "RELN_LVL": "1",
                "CTRL_IND": "0",
                "DT_END": "99991231",
            },
            {  # different parent
                "#ID_RSSD_PARENT": "Q",
                "ID_RSSD_OFFSPRING": "OTHER",
                "RELN_LVL": "1",
                "CTRL_IND": "1",
                "DT_END": "99991231",
            },
        ]
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_relationships", lambda: rels
        )
        assert ticker.controlled_subtree("P") == {"MID", "BANK"}


class TestResolveTickerToBank:
    """Tests for ``resolve_ticker_to_bank`` and ``lead_subsidiary_bank``."""

    def test_resolves_subtree_bank_present_in_filers(self, monkeypatch):
        """The holding company's subsidiary bank that files the report is returned."""
        monkeypatch.setattr(ticker, "resolve_ticker_to_rssd", lambda _: "1039502")
        monkeypatch.setattr(
            ticker, "controlled_subtree", lambda _: {"852218", "999999"}
        )
        assert ticker.resolve_ticker_to_bank("JPM", {"852218", "37"}) == "852218"

    def test_returns_holding_when_it_files(self, monkeypatch):
        """A holding company that itself appears in the filers is returned."""
        monkeypatch.setattr(ticker, "resolve_ticker_to_rssd", lambda _: "37")
        assert ticker.resolve_ticker_to_bank("X", {"37"}) == "37"

    def test_largest_assets_when_multiple_banks(self, monkeypatch):
        """With several subsidiary banks, the largest by total assets is chosen.

        The lowest RSSD would mis-pick a small subsidiary, so the lead bank is
        the one with the largest reported total assets.
        """
        monkeypatch.setattr(ticker, "resolve_ticker_to_rssd", lambda _: "P")
        monkeypatch.setattr(ticker, "controlled_subtree", lambda _: {"852218", "100"})
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr.total_assets_by_rssd",
            lambda period, ids: {"852218": 3.5e12, "100": 1.0e6},
        )
        assert ticker.resolve_ticker_to_bank("X", {"852218", "100"}) == "852218"

    def test_unresolved_ticker_returns_none(self, monkeypatch):
        """A ticker that resolves to no holding company returns ``None``."""
        monkeypatch.setattr(ticker, "resolve_ticker_to_rssd", lambda _: None)
        assert ticker.resolve_ticker_to_bank("ZZZ", {"37"}) is None

    def test_no_subsidiary_bank_returns_none(self, monkeypatch):
        """A holding company with no filing bank in its subtree returns ``None``."""
        monkeypatch.setattr(ticker, "resolve_ticker_to_rssd", lambda _: "P")
        monkeypatch.setattr(ticker, "controlled_subtree", lambda _: {"999999"})
        assert ticker.resolve_ticker_to_bank("X", {"37"}) is None


class TestCallReportFilers:
    """Tests for ``call_report_filers``."""

    def test_returns_bulk_rssids(self, monkeypatch):
        """A ZIP bulk response yields the parsed filer RSSD set."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr.fetch_bulk",
            lambda *a, **k: b"PK\x03\x04rest",
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr.bulk_rssids",
            lambda content: {"852218", "451965"},
        )
        assert ticker.call_report_filers() == {"852218", "451965"}

    def test_non_zip_returns_empty(self, monkeypatch):
        """A non-ZIP bulk response yields an empty filer set."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr.fetch_bulk", lambda *a, **k: b"<html"
        )
        assert ticker.call_report_filers() == set()


class TestResolveRssdToBank:
    """Tests for ``resolve_rssd_to_bank``."""

    def test_bank_rssd_unchanged_no_name(self, monkeypatch):
        """An RSSD that already files is returned unchanged with no resolved name."""
        monkeypatch.setattr(ticker, "call_report_filers", lambda: {"852218"})
        monkeypatch.setattr(
            ticker, "lead_subsidiary_bank", lambda rssd, filers, period: "852218"
        )
        assert ticker.resolve_rssd_to_bank("852218") == ("852218", None)

    def test_unresolved_falls_back_to_input(self, monkeypatch):
        """When no subsidiary bank files, the input RSSD is returned unchanged."""
        empty: set[str] = set()
        monkeypatch.setattr(ticker, "call_report_filers", lambda: empty)
        monkeypatch.setattr(
            ticker, "lead_subsidiary_bank", lambda rssd, filers, period: None
        )
        assert ticker.resolve_rssd_to_bank("1039502") == ("1039502", None)

    def test_holding_company_resolves_with_name(self, monkeypatch):
        """A holding company resolves to its lead bank with that bank's NIC name."""
        monkeypatch.setattr(ticker, "call_report_filers", lambda: {"852218"})
        monkeypatch.setattr(
            ticker, "lead_subsidiary_bank", lambda rssd, filers, period: "852218"
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.rssd_names",
            lambda: {"852218": "JPMORGAN CHASE BANK NA"},
        )
        assert ticker.resolve_rssd_to_bank("1039502") == (
            "852218",
            "JPMORGAN CHASE BANK NA",
        )
