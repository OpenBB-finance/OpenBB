"""Tests for the update_exchange_data module."""

from openbb_core.provider.utils.update_exchange_data import (
    build_exchange_data,
    process_mic_data,
)


class TestExchangeDataUtils:
    """Test exchange data utility functions."""

    def test_process_mic_data_empty(self):
        """Test processing empty MIC data."""
        result = process_mic_data([])
        assert result == []

    def test_process_mic_data_filters_inactive(self):
        """Test that inactive entries are filtered out."""
        rows = [
            {
                "MIC": "XNYS",
                "STATUS": "ACTIVE",
                "OPRT/SGMT": "OPRT",
                "MARKET NAME-INSTITUTION DESCRIPTION": "New York Stock Exchange",
                "ACRONYM": "NYSE",
            },
            {
                "MIC": "DEAD",
                "STATUS": "INACTIVE",
                "OPRT/SGMT": "OPRT",
                "MARKET NAME-INSTITUTION DESCRIPTION": "Dead Exchange",
                "ACRONYM": "DEAD",
            },
        ]
        result = process_mic_data(rows)
        assert len(result) == 1
        assert result[0]["mic"] == "XNYS"

    def test_process_mic_data_filters_operating_only(self):
        """Test operating_only filter."""
        rows = [
            {
                "MIC": "XNYS",
                "STATUS": "ACTIVE",
                "OPRT/SGMT": "OPRT",
                "MARKET NAME-INSTITUTION DESCRIPTION": "NYSE",
                "ACRONYM": "NYSE",
            },
            {
                "MIC": "XNYS1",
                "STATUS": "ACTIVE",
                "OPRT/SGMT": "SGMT",
                "MARKET NAME-INSTITUTION DESCRIPTION": "NYSE Segment",
                "ACRONYM": "NYSE",
            },
        ]
        result = process_mic_data(rows, operating_only=True)
        assert len(result) == 1
        assert result[0]["mic"] == "XNYS"

    def test_process_mic_data_skips_empty_mic(self):
        """Test that entries without MIC are skipped."""
        rows = [
            {
                "MIC": "",
                "STATUS": "ACTIVE",
                "OPRT/SGMT": "OPRT",
                "MARKET NAME-INSTITUTION DESCRIPTION": "Some Exchange",
            },
        ]
        result = process_mic_data(rows)
        assert len(result) == 0

    def test_process_mic_data_skips_empty_name(self):
        """Test that entries without market name are skipped."""
        rows = [
            {
                "MIC": "XXXX",
                "STATUS": "ACTIVE",
                "OPRT/SGMT": "OPRT",
                "MARKET NAME-INSTITUTION DESCRIPTION": "",
            },
        ]
        result = process_mic_data(rows)
        assert len(result) == 0

    def test_process_mic_data_includes_city_if_present(self):
        """Test that city is included when present."""
        rows = [
            {
                "MIC": "XNYS",
                "STATUS": "ACTIVE",
                "OPRT/SGMT": "OPRT",
                "MARKET NAME-INSTITUTION DESCRIPTION": "NYSE",
                "ACRONYM": "NYSE",
                "CITY": "new york",
            },
        ]
        result = process_mic_data(rows)
        assert result[0]["city"] == "New York"

    def test_process_mic_data_includes_country_if_present(self):
        """Test that country code is included when present."""
        rows = [
            {
                "MIC": "XNYS",
                "STATUS": "ACTIVE",
                "OPRT/SGMT": "OPRT",
                "MARKET NAME-INSTITUTION DESCRIPTION": "NYSE",
                "ACRONYM": "NYSE",
                "ISO COUNTRY CODE (ISO 3166)": "us",
            },
        ]
        result = process_mic_data(rows)
        assert result[0]["country"] == "US"

    def test_process_mic_data_normalizes_website(self):
        """Test website URL normalization."""
        rows = [
            {
                "MIC": "XNYS",
                "STATUS": "ACTIVE",
                "OPRT/SGMT": "OPRT",
                "MARKET NAME-INSTITUTION DESCRIPTION": "NYSE",
                "ACRONYM": "NYSE",
                "WEBSITE": "WWW.NYSE.COM",
            },
        ]
        result = process_mic_data(rows)
        assert result[0]["website"] == "https://www.nyse.com"

    def test_process_mic_data_adds_https_to_website(self):
        """Test that https:// is added to websites without scheme."""
        rows = [
            {
                "MIC": "XNYS",
                "STATUS": "ACTIVE",
                "OPRT/SGMT": "OPRT",
                "MARKET NAME-INSTITUTION DESCRIPTION": "NYSE",
                "ACRONYM": "NYSE",
                "WEBSITE": "www.nyse.com",
            },
        ]
        result = process_mic_data(rows)
        assert result[0]["website"] == "https://www.nyse.com"

    def test_process_mic_data_preserves_http(self):
        """Test that http:// is preserved if present."""
        rows = [
            {
                "MIC": "XNYS",
                "STATUS": "ACTIVE",
                "OPRT/SGMT": "OPRT",
                "MARKET NAME-INSTITUTION DESCRIPTION": "NYSE",
                "ACRONYM": "NYSE",
                "WEBSITE": "HTTP://example.com",
            },
        ]
        result = process_mic_data(rows)
        assert result[0]["website"] == "http://example.com"

    def test_process_mic_data_sorts_operating_first(self):
        """Test that operating MICs are sorted before segments."""
        rows = [
            {
                "MIC": "SGMT",
                "STATUS": "ACTIVE",
                "OPRT/SGMT": "SGMT",
                "MARKET NAME-INSTITUTION DESCRIPTION": "Segment",
                "ACRONYM": "SGMT",
            },
            {
                "MIC": "OPRT",
                "STATUS": "ACTIVE",
                "OPRT/SGMT": "OPRT",
                "MARKET NAME-INSTITUTION DESCRIPTION": "Operating",
                "ACRONYM": "OPRT",
            },
        ]
        result = process_mic_data(rows)
        assert result[0]["mic"] == "OPRT"
        assert result[1]["mic"] == "SGMT"

    def test_build_exchange_data(self):
        """Test building exchange data structure."""
        exchanges = [
            {"mic": "XNYS", "acronym": "NYSE", "name": "New York Stock Exchange"}
        ]
        data = build_exchange_data(exchanges)

        assert "_last_updated" in data
        assert "_source" in data
        assert "_stats" in data
        assert data["_source"]["standard"] == "ISO 10383"
        assert data["_stats"]["total_exchanges"] == 1
        assert data["exchanges"] == exchanges

    def test_process_mic_data_uses_mic_as_default_acronym(self):
        """Test that MIC is used as default acronym when not provided."""
        rows = [
            {
                "MIC": "XNYS",
                "STATUS": "ACTIVE",
                "OPRT/SGMT": "OPRT",
                "MARKET NAME-INSTITUTION DESCRIPTION": "NYSE",
                "ACRONYM": "",
            },
        ]
        result = process_mic_data(rows)
        assert result[0]["acronym"] == "XNYS"

    def test_process_mic_data_status_case_insensitive(self):
        """Test that STATUS check is case-insensitive."""
        rows = [
            {
                "MIC": "XNYS",
                "STATUS": "active",
                "OPRT/SGMT": "OPRT",
                "MARKET NAME-INSTITUTION DESCRIPTION": "NYSE",
                "ACRONYM": "NYSE",
            },
        ]
        result = process_mic_data(rows)
        assert len(result) == 1
