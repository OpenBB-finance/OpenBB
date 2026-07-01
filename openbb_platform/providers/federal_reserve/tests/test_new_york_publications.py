"""Tests for the New York Fed publications aggregator, index model, and widget."""

from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.new_york_publications import (
    FederalReserveNewYorkPublicationsData,
    FederalReserveNewYorkPublicationsFetcher,
)
from openbb_federal_reserve.utils import ny_publications as npub


@pytest.fixture(autouse=True)
def _stub_archives(monkeypatch):
    """Point every per-archive indexer at a small synthetic listing."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ny_empire.list_empire_state_reports",
        lambda: [{"period": "202606", "url": "https://x/empire-202606.pdf"}],
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ny_reports.list_business_leaders_reports",
        lambda: [{"period": "202605", "url": "https://x/bls-202605.pdf"}],
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ny_reports"
        ".list_business_leaders_supplemental_reports",
        lambda: [{"period": "202604", "url": "https://x/bls-suppl-202604.pdf"}],
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ny_hhdc.list_household_debt_quarters",
        lambda: ["2026Q1"],
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ny_surveys.list_market_expectations",
        lambda: [
            {
                "date": "2026-03-01",
                "kind": "results",
                "subtype": "combined",
                "title": "March 2026 Results (Combined)",
                "url": "https://x/sme-2026-03.pdf",
            }
        ],
    )


class TestListPublications:
    """Tests for the merged publications catalog."""

    def test_merges_all_five_archives_newest_first(self):
        """The merged catalog spans all five report series, newest first."""
        catalog = npub.list_publications()
        series = {record["series"] for record in catalog}
        assert series == {
            "empire_state_report",
            "business_leaders_report",
            "business_leaders_supplemental_report",
            "household_debt_report",
            "market_expectations_report",
        }
        assert all(record["url"].startswith("https://") for record in catalog)
        assert catalog == sorted(catalog, key=lambda r: r["date"], reverse=True)

    def test_records_carry_date_series_title_url(self):
        """Every record carries a date, series, title, and url."""
        catalog = npub.list_publications()
        for record in catalog:
            assert set(record) == {"date", "series", "title", "url"}
            assert record["date"] and record["title"] and record["url"]

    def test_household_debt_quarter_end_date_and_url(self):
        """The HHDC record uses a quarter-end date and the quarter PDF URL."""
        catalog = npub.list_publications("household_debt_report")
        assert len(catalog) == 1
        record = catalog[0]
        assert record["date"] == "2026-03-31"
        assert record["url"].endswith("HHDC_2026Q1.pdf")

    def test_series_filter_narrows_to_one_archive(self):
        """A series filter restricts the catalog to that one archive."""
        catalog = npub.list_publications("empire_state_report")
        assert {record["series"] for record in catalog} == {"empire_state_report"}


class TestPublicationsIndexModel:
    """Tests for the publications index data model and fetcher."""

    def test_transform_query_requires_no_params(self):
        """``transform_query`` works with an empty dict."""
        query = FederalReserveNewYorkPublicationsFetcher.transform_query({})
        assert query.series is None
        assert query.start_date is None

    def test_no_filter_returns_all_with_urls(self):
        """The full catalog validates to dated records carrying urls."""
        query = FederalReserveNewYorkPublicationsFetcher.transform_query({})
        rows = FederalReserveNewYorkPublicationsFetcher.transform_data(
            query, FederalReserveNewYorkPublicationsFetcher.extract_data(query, None)
        )
        assert len(rows) == 5
        assert all(
            isinstance(row, FederalReserveNewYorkPublicationsData) for row in rows
        )
        assert all(row.url.startswith("https://") for row in rows)
        assert {row.series for row in rows} == {
            "empire_state_report",
            "business_leaders_report",
            "business_leaders_supplemental_report",
            "household_debt_report",
            "market_expectations_report",
        }

    def test_filters_start_and_end_date(self):
        """The start_date and end_date filters narrow the catalog."""
        query = FederalReserveNewYorkPublicationsFetcher.transform_query(
            {"start_date": "2026-05-01", "end_date": "2026-06-30"}
        )
        rows = FederalReserveNewYorkPublicationsFetcher.transform_data(
            query, FederalReserveNewYorkPublicationsFetcher.extract_data(query, None)
        )
        assert {row.series for row in rows} == {
            "empire_state_report",
            "business_leaders_report",
        }
        assert rows[0].date == date(2026, 6, 1)

    def test_empty_raises(self, monkeypatch):
        """An empty catalog raises ``EmptyDataError``."""
        monkeypatch.setattr(npub, "list_publications", lambda series=None: [])
        query = FederalReserveNewYorkPublicationsFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveNewYorkPublicationsFetcher.extract_data(query, None)


class TestPublicationsWidgetConfig:
    """Tests for the multi_file_viewer x-widget_config carried by the model."""

    def test_multi_file_viewer_config(self):
        """The data model carries a multi_file_viewer config wired to the NY choices."""
        config = FederalReserveNewYorkPublicationsData.model_config[
            "json_schema_extra"
        ]["x-widget_config"]
        assert config["$.type"] == "multi_file_viewer"
        assert config["$.name"] == "New York Fed Reports"
        assert config["$.subCategory"] == "Publications & Reports"
        assert config["$.source"] == ["Federal Reserve Bank of New York"]
        assert config["$.endpoint"].endswith("/regional_publications_download")
        param = config["$.params"][0]
        assert param["roles"] == ["fileSelector"]
        assert param["multiSelect"] is True
        assert param["optionsEndpoint"].endswith("/regional_publications_choices")
        assert param["optionsParams"] == {"district": "ny"}
