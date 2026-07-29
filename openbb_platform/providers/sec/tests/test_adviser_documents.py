"""Tests for SEC investment adviser regulatory documents."""

from __future__ import annotations

import asyncio
from datetime import date
from json import dumps
from typing import cast

import pytest
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_sec.models import adviser_documents
from openbb_sec.models.adviser_documents import (
    SecAdviserDocumentsFetcher,
    SecAdviserDocumentsQueryParams,
)


def _firm_content(**updates: object) -> dict[str, object]:
    content: dict[str, object] = {
        "basicInformation": {
            "firmId": 148826,
            "firmName": "CITADEL ADVISORS LLC",
            "advFilingDate": "06/11/2026",
            "hasPdf": "Y",
        },
        "brochures": {
            "brochuredetails": [
                {
                    "brochureVersionID": 1038247,
                    "brochureName": "CITADEL ADVISORS LLC ADV BROCHURE",
                    "dateSubmitted": "3/31/2026",
                }
            ],
        },
    }
    content.update(updates)
    return content


def _firm_payload(content: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "iacontent": dumps(content or _firm_content()),
                    }
                }
            ]
        }
    }


@pytest.mark.parametrize("crd", [None, "", "abc", True, 148826])
def test_adviser_documents_query_requires_numeric_crd(crd: object) -> None:
    """Document queries require a numeric CRD string."""
    params = {} if crd is None else {"crd": crd}
    with pytest.raises(ValidationError):
        SecAdviserDocumentsQueryParams.model_validate(params)


def test_adviser_documents_return_one_row_per_document() -> None:
    """ADV and brochure metadata produce independent flat rows."""
    records = adviser_documents._document_records(_firm_content())

    assert records == [
        {
            "crd": "148826",
            "firm_name": "CITADEL ADVISORS LLC",
            "document_type": "Form ADV",
            "document_id": None,
            "title": "Form ADV",
            "filing_date": date(2026, 6, 11),
            "url": "https://reports.adviserinfo.sec.gov/reports/ADV/148826/PDF/148826.pdf",
        },
        {
            "crd": "148826",
            "firm_name": "CITADEL ADVISORS LLC",
            "document_type": "Brochure",
            "document_id": "1038247",
            "title": "CITADEL ADVISORS LLC ADV BROCHURE",
            "filing_date": date(2026, 3, 31),
            "url": (
                "https://files.adviserinfo.sec.gov/IAPD/Content/Common/"
                "crd_iapd_Brochure.aspx?BRCHR_VRSN_ID=1038247"
            ),
        },
    ]


def test_documents_require_source_document_metadata(monkeypatch) -> None:
    """The documents route fails when IAPD reports no available documents."""
    content = _firm_content(brochures={})
    basic = cast(dict[str, object], content["basicInformation"])
    basic["hasPdf"] = "N"

    async def fake_get_adviser_firm(*_args: object) -> dict[str, object]:
        return content

    monkeypatch.setattr(
        adviser_documents,
        "_get_adviser_firm",
        fake_get_adviser_firm,
    )
    query = SecAdviserDocumentsQueryParams(crd="148826")

    with pytest.raises(EmptyDataError, match="No regulatory documents"):
        asyncio.run(SecAdviserDocumentsFetcher.aextract_data(query, None))


def test_documents_reject_malformed_iapd_response(monkeypatch) -> None:
    """Missing profile data fails explicitly."""

    async def fake_request_iapd(*_args: object) -> object:
        return {"hits": {"hits": []}}

    monkeypatch.setattr(adviser_documents, "request_iapd", fake_request_iapd)
    query = SecAdviserDocumentsQueryParams(crd="148826")

    with pytest.raises(EmptyDataError, match="No investment adviser firm"):
        asyncio.run(SecAdviserDocumentsFetcher.aextract_data(query, None))
