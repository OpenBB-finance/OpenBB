"""Tests for the Richmond Fed survey-release PDF helpers and commands."""

import base64
from datetime import date
from unittest.mock import MagicMock

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_federal_reserve.utils import richmond_surveys

_MEDIA = (
    "/-/media/RichmondFedOrg/region_communities/regional_data_analysis"
    "/regional_economy/surveys_of_business_conditions"
)
_MFG_HTML = (
    f'<a href="{_MEDIA}/manufacturing/2026/pdf/mfg_06_23_26.pdf">x</a>'
    f'<a href="{_MEDIA}/manufacturing/2026/pdf/mfg_05_27_26.pdf">x</a>'
    f'<a href="{_MEDIA}/manufacturing/2025/pdf/mfg_12_23_25.pdf">x</a>'
    f'<a href="{_MEDIA}/manufacturing/questionnaire/mfg_questionnaire.pdf">x</a>'
    f'<a href="{_MEDIA}/manufacturing/2026/pdf/mfg_03_24_26_draft.pdf">x</a>'
    f'<a href="{_MEDIA}/manufacturing/2026/pdf/mfg_99_99_26.pdf">x</a>'
)
_NMF_HTML = (
    f'<a href="{_MEDIA}/non-manufacturing/2026/pdf/nmf_06_23_26.pdf">x</a>'
    f'<a href="{_MEDIA}/non-manufacturing/2026/pdf/nmf_05_27_26.pdf">x</a>'
)


def _make_request(url, *args, **kwargs):
    """Path-aware fake: archive HTML for survey pages, PDF bytes otherwise."""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    if "manufacturing/archive" in url:
        response.text = _MFG_HTML
        response.content = _MFG_HTML.encode()
    elif "non-manufacturing?mode=archive" in url:
        response.text = _NMF_HTML
        response.content = _NMF_HTML.encode()
    else:
        response.content = b"%PDF-1.7 fake richmond release"
    return response


def _patch(monkeypatch):
    """Route all Richmond requests through the path-aware fake."""
    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.make_request", _make_request
    )


class TestClassifyRelease:
    """Tests for the release filename classifier."""

    def test_manufacturing_release(self):
        """A dated manufacturing release classifies with its release date."""
        href = f"{_MEDIA}/manufacturing/2026/pdf/mfg_06_23_26.pdf"
        record = richmond_surveys._classify_release("manufacturing", href)
        assert record["survey"] == "manufacturing"
        assert record["date"] == "2026-06-23"
        assert record["title"] == "Manufacturing Survey June 23, 2026"
        assert record["url"].startswith("https://www.richmondfed.org")

    def test_non_release_returns_none(self):
        """A non-dated href (questionnaire) is not classifiable."""
        href = f"{_MEDIA}/manufacturing/questionnaire/mfg_questionnaire.pdf"
        assert richmond_surveys._classify_release("manufacturing", href) is None

    def test_invalid_date_returns_none(self):
        """An href with an impossible calendar date is not classifiable."""
        href = f"{_MEDIA}/manufacturing/2026/pdf/mfg_99_99_26.pdf"
        assert richmond_surveys._classify_release("manufacturing", href) is None


class TestListSurveyReleases:
    """Tests for ``list_survey_releases``."""

    def test_both_surveys_dedup_and_sort(self, monkeypatch):
        """Both archives index, the questionnaire drops, newest first."""
        _patch(monkeypatch)
        catalog = richmond_surveys.list_survey_releases()
        keys = {(r["survey"], r["date"]) for r in catalog}
        assert ("manufacturing", "2026-06-23") in keys
        assert ("manufacturing", "2025-12-23") in keys
        assert ("non_manufacturing", "2026-06-23") in keys
        assert not any("questionnaire" in r["url"] for r in catalog)
        ordering = [(r["survey"], r["date"]) for r in catalog]
        assert ordering == sorted(ordering, reverse=True)

    def test_snapshots_folded_in(self, monkeypatch):
        """The static Regional Economic Snapshots fold in with real urls."""
        _patch(monkeypatch)
        catalog = richmond_surveys.list_survey_releases()
        snapshots = [r for r in catalog if r["survey"] == "regional_snapshot"]
        assert len(snapshots) == len(richmond_surveys._SNAPSHOTS)
        urls = {r["url"] for r in snapshots}
        for filename in richmond_surveys._SNAPSHOTS.values():
            assert f"{richmond_surveys._SNAPSHOT_DIR}/{filename}" in urls
        district = next(r for r in snapshots if r["url"].endswith("/snapshot.pdf"))
        assert district["title"] == "Regional Economic Snapshot"

    def test_single_survey_filter(self, monkeypatch):
        """A survey filter scrapes only that archive, no static snapshots."""
        _patch(monkeypatch)
        catalog = richmond_surveys.list_survey_releases("non_manufacturing")
        assert {r["survey"] for r in catalog} == {"non_manufacturing"}


class TestFetchSurveyReleasePdf:
    """Tests for ``fetch_survey_release_pdf``."""

    def test_latest_release(self, monkeypatch):
        """The latest manufacturing release downloads as a base64 PDF."""
        _patch(monkeypatch)
        out = richmond_surveys.fetch_survey_release_pdf("manufacturing")
        assert out["data_format"]["filename"] == (
            "Richmond_manufacturing_2026-06-23.pdf"
        )
        assert base64.b64decode(out["content"]).startswith(b"%PDF")

    def test_specific_month(self, monkeypatch):
        """A requested month selects that release."""
        _patch(monkeypatch)
        out = richmond_surveys.fetch_survey_release_pdf("manufacturing", date="2025-12")
        assert out["data_format"]["filename"] == (
            "Richmond_manufacturing_2025-12-23.pdf"
        )

    def test_unknown_month_raises(self, monkeypatch):
        """A missing month raises ``OpenBBError``."""
        _patch(monkeypatch)
        with pytest.raises(OpenBBError):
            richmond_surveys.fetch_survey_release_pdf("manufacturing", date="1999-01")

    def test_unknown_survey_raises(self, monkeypatch):
        """An unknown survey raises ``OpenBBError``."""
        _patch(monkeypatch)
        with pytest.raises(OpenBBError):
            richmond_surveys.fetch_survey_release_pdf("widgets")

    def test_no_catalog_raises(self, monkeypatch):
        """An empty catalog raises ``OpenBBError``."""
        monkeypatch.setattr(richmond_surveys, "list_survey_releases", lambda s=None: [])
        with pytest.raises(OpenBBError):
            richmond_surveys.fetch_survey_release_pdf("manufacturing")


class TestPublicationsIndex:
    """Tests for the survey-releases index data model."""

    _CATALOG = [
        {
            "survey": "manufacturing",
            "date": "2026-06-23",
            "title": "Manufacturing Survey June 23, 2026",
            "url": "https://x/mfg_06_23_26.pdf",
        },
        {
            "survey": "manufacturing",
            "date": "2026-01-27",
            "title": "Manufacturing Survey January 27, 2026",
            "url": "https://x/mfg_01_27_26.pdf",
        },
        {
            "survey": "non_manufacturing",
            "date": "2026-06-23",
            "title": "Service Sector Survey June 23, 2026",
            "url": "https://x/nmf_06_23_26.pdf",
        },
    ]

    def _patch_catalog(self, monkeypatch):
        """Point the index model at a synthetic catalog."""
        monkeypatch.setattr(
            richmond_surveys, "list_survey_releases", lambda s=None: list(self._CATALOG)
        )

    def test_filters_start_date(self, monkeypatch):
        """The start_date filter narrows the catalog."""
        from openbb_federal_reserve.models.regional.richmond_publications import (
            FederalReserveRichmondPublicationsData as DataModel,
            FederalReserveRichmondPublicationsFetcher as Fetcher,
        )

        self._patch_catalog(monkeypatch)
        query = Fetcher.transform_query({"start_date": "2026-02-01"})
        rows = Fetcher.transform_data(query, Fetcher.extract_data(query, None))
        assert all(isinstance(r, DataModel) for r in rows)
        assert {r.date for r in rows} == {date(2026, 6, 23)}

    def test_filters_end_date(self, monkeypatch):
        """The end_date filter narrows the catalog."""
        from openbb_federal_reserve.models.regional.richmond_publications import (
            FederalReserveRichmondPublicationsFetcher as Fetcher,
        )

        self._patch_catalog(monkeypatch)
        query = Fetcher.transform_query({"end_date": "2026-01-31"})
        rows = Fetcher.transform_data(query, Fetcher.extract_data(query, None))
        assert [r.date for r in rows] == [date(2026, 1, 27)]

    def test_no_filter_returns_all(self, monkeypatch):
        """With no filters the full catalog is returned."""
        from openbb_federal_reserve.models.regional.richmond_publications import (
            FederalReserveRichmondPublicationsFetcher as Fetcher,
        )

        self._patch_catalog(monkeypatch)
        query = Fetcher.transform_query({})
        rows = Fetcher.transform_data(query, Fetcher.extract_data(query, None))
        assert len(rows) == 3

    def test_empty_raises(self, monkeypatch):
        """An empty catalog raises ``EmptyDataError``."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_federal_reserve.models.regional.richmond_publications import (
            FederalReserveRichmondPublicationsFetcher as Fetcher,
        )

        monkeypatch.setattr(richmond_surveys, "list_survey_releases", lambda s=None: [])
        query = Fetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            Fetcher.extract_data(query, None)


class TestPublicationsChoices:
    """Tests for the shared regional_publications_choices contract."""

    @pytest.mark.asyncio
    async def test_choices_include_snapshots(self, monkeypatch):
        """The choices endpoint surfaces the folded Regional Economic Snapshots."""
        from openbb_federal_reserve.federal_reserve_router import (
            regional_publications_choices,
        )

        _patch(monkeypatch)
        choices = await regional_publications_choices("richmond")
        urls = {choice["value"] for choice in choices}
        for filename in richmond_surveys._SNAPSHOTS.values():
            assert f"{richmond_surveys._SNAPSHOT_DIR}/{filename}" in urls
