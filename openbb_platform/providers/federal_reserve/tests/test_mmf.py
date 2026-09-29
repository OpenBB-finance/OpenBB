"""Tests for the Money Market Funds holdings CSV fetch and parse helpers."""

from unittest.mock import MagicMock, patch

from openbb_federal_reserve.utils.mmf import fetch_mmf, parse_mmf


class TestFetchMmf:
    """Tests for the cached CSV download."""

    def test_downloads_and_caches_table_text(self):
        """The producer fetches the table URL and returns its text body."""
        response = MagicMock()
        response.text = '"Date","X (millions)"\n"Dec 31, 2010",1\n'
        response.raise_for_status = MagicMock()
        with patch(
            "openbb_core.provider.utils.helpers.make_request", return_value=response
        ) as mock_request:
            text = fetch_mmf("total")
        assert text == '"Date","X (millions)"\n"Dec 31, 2010",1\n'
        assert mock_request.call_args.args[0].endswith(
            "total-money-market-funds-investment-holdings-historical.csv"
        )
        response.raise_for_status.assert_called_once()


class TestParseMmf:
    """Tests for the holdings melt."""

    def test_unparseable_dates_are_dropped(self):
        """Rows whose date fails to parse are skipped."""
        text = '"Date","X (millions)"\n"Dec 31, 2010",1\n"bad date",2\n'
        rows = parse_mmf(text)
        assert [row["date"].year for row in rows] == [2010]
        assert all(row["label"] == "X" for row in rows)
