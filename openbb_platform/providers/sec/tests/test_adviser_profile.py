"""Tests for SEC investment adviser profiles and documents."""

from __future__ import annotations

import asyncio
from datetime import date
from json import dumps
from typing import cast

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_sec.models import adviser_profile
from openbb_sec.models.adviser_profile import (
    SecAdviserDocumentsFetcher,
    SecAdviserDocumentsQueryParams,
    SecAdviserProfileFetcher,
    SecAdviserProfileQueryParams,
)


def _firm_content(**updates: object) -> dict[str, object]:
    content: dict[str, object] = {
        "basicInformation": {
            "firmId": 148826,
            "firmName": "CITADEL ADVISORS LLC",
            "iaScope": "ACTIVE",
            "advFilingDate": "06/11/2026",
            "hasPdf": "Y",
            "iaSECNumber": "70860",
            "iaSECNumberType": "801",
        },
        "iaFirmAddressDetails": {
            "officeAddress": {
                "street1": "830 BRICKELL PLAZA",
                "street2": "FLOOR 15",
                "city": "MIAMI",
                "state": "FL",
                "country": "United States",
                "postalCode": "33131",
            }
        },
        "orgScopeStatusFlags": {
            "isSECRegistered": "Y",
            "isStateRegistered": "N",
            "isERARegistered": "N",
            "isSECERARegistered": "N",
            "isStateERARegistered": "N",
        },
        "relyingAdvisors": [
            {"firmId": 292030, "name": "ASHLER CAPITAL LLC", "status": "INACTIVE"}
        ],
        "brochures": {
            "part2ExemptFlag": "N",
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


@pytest.mark.parametrize("crd", [None, "", "abc", True])
def test_adviser_profile_requires_numeric_crd(crd: object) -> None:
    """Profile queries require a numeric CRD identifier."""
    params = {} if crd is None else {"crd": crd}
    with pytest.raises(ValidationError):
        SecAdviserProfileQueryParams.model_validate(params)


def test_adviser_profile_returns_one_flat_row(monkeypatch) -> None:
    """The profile fetcher maps structured IAPD metadata to one flat row."""
    calls: list[tuple[str, dict[str, str | int], bool]] = []

    async def fake_request_iapd(
        path: str, params: dict[str, str | int], use_cache: bool
    ) -> object:
        calls.append((path, params, use_cache))
        return _firm_payload()

    monkeypatch.setattr(adviser_profile, "request_iapd", fake_request_iapd)
    query = SecAdviserProfileQueryParams(crd="148826", use_cache=False)

    records = asyncio.run(SecAdviserProfileFetcher.aextract_data(query, None))

    assert calls == [
        (
            "firm/148826",
            {},
            False,
        )
    ]
    assert records == [
        {
            "crd": "148826",
            "name": "CITADEL ADVISORS LLC",
            "sec_number": "801-70860",
            "registration_type": "SEC Registered",
            "status": "ACTIVE",
            "filing_date": date(2026, 6, 11),
            "address_line_1": "830 BRICKELL PLAZA",
            "address_line_2": "FLOOR 15",
            "city": "MIAMI",
            "state": "FL",
            "postal_code": "33131",
            "country": "United States",
            "part_2_exempt": False,
        }
    ]


def test_adviser_documents_return_one_row_per_document() -> None:
    """ADV and brochure metadata produce independent flat rows."""
    content = _firm_content()

    records = adviser_profile._document_records(content)

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
            "url": "https://files.adviserinfo.sec.gov/IAPD/Content/Common/crd_iapd_Brochure.aspx?BRCHR_VRSN_ID=1038247",
        },
    ]


@pytest.mark.parametrize(
    ("number_type", "flags", "expected"),
    [
        ("802", {}, "SEC Exempt Reporting Adviser"),
        (None, {"isStateRegistered": "Y"}, "State Registered"),
        (None, {"isSECERARegistered": "Y"}, "SEC Exempt Reporting Adviser"),
        (None, {"isStateERARegistered": "Y"}, "State Exempt Reporting Adviser"),
    ],
)
def test_profile_registration_type_uses_source_flags(
    number_type: str | None,
    flags: dict[str, object],
    expected: str,
) -> None:
    """Profiles classify SEC, state, and exempt registrations explicitly."""
    basic: dict[str, object] = {}
    if number_type is not None:
        basic["iaSECNumberType"] = number_type
    firm: dict[str, object] = {"orgScopeStatusFlags": flags}

    assert adviser_profile._registration_type(firm, basic) == expected


def test_documents_do_not_fabricate_unreported_urls(monkeypatch) -> None:
    """The documents route fails when IAPD reports no available documents."""
    content = _firm_content(brochures={"part2ExemptFlag": "Y"})
    basic = cast(dict[str, object], content["basicInformation"])
    basic["hasPdf"] = "N"

    async def fake_get_adviser_firm(*_args: object) -> dict[str, object]:
        return content

    monkeypatch.setattr(
        adviser_profile,
        "_get_adviser_firm",
        fake_get_adviser_firm,
    )
    query = SecAdviserDocumentsQueryParams(crd="148826")

    with pytest.raises(EmptyDataError, match="No regulatory documents"):
        asyncio.run(SecAdviserDocumentsFetcher.aextract_data(query, None))


@pytest.mark.parametrize(
    "payload",
    [
        {"hits": {"hits": []}},
        {"hits": {"hits": [{"_source": {}}]}},
        {"hits": {"hits": [{"_source": {"iacontent": "not-json"}}]}},
    ],
)
def test_profile_rejects_empty_or_malformed_responses(monkeypatch, payload) -> None:
    """Missing and malformed profile responses fail explicitly."""

    async def fake_request_iapd(*_args: object) -> object:
        return payload

    monkeypatch.setattr(adviser_profile, "request_iapd", fake_request_iapd)
    query = SecAdviserProfileQueryParams(crd="148826")

    with pytest.raises((EmptyDataError, OpenBBError)):
        asyncio.run(SecAdviserProfileFetcher.aextract_data(query, None))
