"""Tests for the International Portfolio Investment CSV fetch and parse helpers."""

from unittest.mock import MagicMock, patch

from openbb_federal_reserve.utils.ipi import fetch_ipi, parse_ipi


class TestFetchIpi:
    """Tests for the cached CSV download."""

    def test_downloads_and_caches_table_text(self):
        """The producer fetches the table URL and returns its text body."""
        response = MagicMock()
        response.text = "Date,Africa\nJan 2012,1.0\n"
        response.raise_for_status = MagicMock()
        with patch(
            "openbb_core.provider.utils.helpers.make_request", return_value=response
        ) as mock_request:
            text = fetch_ipi("table1")
        assert text == "Date,Africa\nJan 2012,1.0\n"
        assert mock_request.call_args.args[0].endswith(
            "international-portfolio-investment-table1-historical.csv"
        )
        response.raise_for_status.assert_called_once()


class TestParseIpi:
    """Tests for the holdings-by-country melt."""

    def test_unparseable_dates_are_dropped(self):
        """Rows whose date fails to parse are skipped."""
        text = "Date,Africa\nJan 2012,1.0\nnot-a-date,2.0\n"
        rows = parse_ipi(text, "Measure")
        assert [row["date"].year for row in rows] == [2012]
        assert all(row["label"] == "Measure" for row in rows)
