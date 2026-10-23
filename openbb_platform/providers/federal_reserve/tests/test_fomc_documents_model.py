"""Unit tests for the Federal Reserve FOMC documents model."""

# ruff: noqa: I001

from datetime import date as dateType

import pytest

from openbb_core.provider.utils.errors import EmptyDataError
from openbb_federal_reserve.models.fomc_documents import (
    FederalReserveFomcDocumentsData,
    FederalReserveFomcDocumentsFetcher,
    FederalReserveFomcDocumentsQueryParams,
)

FAKE_DOCS = [
    {
        "date": "2024-12-18",
        "doc_type": "projections",
        "doc_format": "htm",
        "url": "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20241218.htm",
    },
    {
        "date": "2024-06-14",
        "doc_type": "minutes",
        "doc_format": "pdf",
        "url": "https://www.federalreserve.gov/monetarypolicy/fomcminutes20240614.pdf",
    },
]


class TestQueryParams:
    """Tests for ``FederalReserveFomcDocumentsQueryParams``."""

    def test_defaults_are_none(self):
        """Year and document type default to ``None``."""
        q = FederalReserveFomcDocumentsQueryParams()
        assert q.year is None
        assert q.document_type is None

    def test_valid_document_type_passes(self):
        """A recognised document type validates unchanged."""
        q = FederalReserveFomcDocumentsQueryParams(document_type="minutes")
        assert q.document_type == "minutes"

    def test_invalid_document_type_raises(self):
        """An unknown document type raises a validation error."""
        with pytest.raises(ValueError, match="Invalid document type"):
            FederalReserveFomcDocumentsQueryParams(document_type="not_a_type")

    def test_none_document_type_is_allowed(self):
        """A ``None`` document type bypasses the validator."""
        q = FederalReserveFomcDocumentsQueryParams(document_type=None)
        assert q.document_type is None

    def test_transform_query_builds_params(self):
        """``transform_query`` constructs the params model from a dict."""
        q = FederalReserveFomcDocumentsFetcher.transform_query(
            {"year": 2024, "document_type": "minutes"}
        )
        assert isinstance(q, FederalReserveFomcDocumentsQueryParams)
        assert q.year == 2024
        assert q.document_type == "minutes"


class TestAExtractData:
    """Tests for ``FederalReserveFomcDocumentsFetcher.aextract_data``."""

    @pytest.mark.asyncio
    async def test_delegates_to_get_fomc_documents_by_year(self, monkeypatch):
        """Extract forwards year/document_type to the utility and returns its rows."""
        seen: dict = {}

        def _fake(year=None, document_type=None):
            """Record the call arguments and return canned docs."""
            seen["year"] = year
            seen["document_type"] = document_type
            return FAKE_DOCS

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.fomc_documents.get_fomc_documents_by_year",
            _fake,
        )
        q = FederalReserveFomcDocumentsQueryParams(year=2024, document_type="minutes")
        out = await FederalReserveFomcDocumentsFetcher.aextract_data(q, None)
        assert out == FAKE_DOCS
        assert seen == {"year": 2024, "document_type": "minutes"}

    @pytest.mark.asyncio
    async def test_passes_none_arguments(self, monkeypatch):
        """``None`` year/document_type are forwarded verbatim."""
        seen: dict = {}

        def _fake(year=None, document_type=None):
            """Record the call arguments."""
            seen["year"] = year
            seen["document_type"] = document_type
            return []

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.fomc_documents.get_fomc_documents_by_year",
            _fake,
        )
        q = FederalReserveFomcDocumentsQueryParams()
        out = await FederalReserveFomcDocumentsFetcher.aextract_data(q, None)
        assert out == []
        assert seen == {"year": None, "document_type": None}


class TestTransformData:
    """Tests for ``FederalReserveFomcDocumentsFetcher.transform_data``."""

    def test_validates_rows_into_models(self):
        """Each raw row validates into a data model."""
        q = FederalReserveFomcDocumentsQueryParams(year=2024)
        out = FederalReserveFomcDocumentsFetcher.transform_data(q, FAKE_DOCS)
        assert len(out) == 2
        assert all(isinstance(d, FederalReserveFomcDocumentsData) for d in out)
        assert out[0].date == dateType(2024, 12, 18)
        assert out[0].doc_type == "projections"
        assert out[0].doc_format == "htm"
        assert out[1].doc_type == "minutes"

    def test_empty_data_raises(self):
        """An empty data list raises ``EmptyDataError``."""
        q = FederalReserveFomcDocumentsQueryParams(year=2024)
        with pytest.raises(EmptyDataError, match="No FOMC documents found."):
            FederalReserveFomcDocumentsFetcher.transform_data(q, [])


class TestData:
    """Tests for ``FederalReserveFomcDocumentsData``."""

    def test_parses_date_string(self):
        """A ``YYYY-MM-DD`` string coerces to a ``date``."""
        d = FederalReserveFomcDocumentsData.model_validate(
            {
                "date": "2024-06-14",
                "doc_type": "minutes",
                "doc_format": "pdf",
                "url": "https://example.com/doc.pdf",
            }
        )
        assert d.date == dateType(2024, 6, 14)
        assert d.url == "https://example.com/doc.pdf"
