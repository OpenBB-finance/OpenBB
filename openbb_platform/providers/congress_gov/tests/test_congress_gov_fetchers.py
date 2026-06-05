"""Congress.gov Fetchers tests."""

from datetime import datetime

import pytest
from openbb_core.app.service.user_service import UserService

from openbb_congress_gov.models.amendment_info import CongressAmendmentInfoFetcher
from openbb_congress_gov.models.amendment_text import CongressAmendmentTextFetcher
from openbb_congress_gov.models.bill_info import CongressBillInfoFetcher
from openbb_congress_gov.models.bill_text import CongressBillTextFetcher
from openbb_congress_gov.models.congress_amendments import CongressAmendmentsFetcher
from openbb_congress_gov.models.congress_bills import CongressBillsFetcher
from openbb_congress_gov.models.congress_committee_documents import (
    CongressCommitteeDocumentsFetcher,
)
from openbb_congress_gov.models.congress_committee_info import (
    CongressCommitteeInfoFetcher,
)
from openbb_congress_gov.utils.helpers import year_to_congress

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)
test_credentials = (
    test_credentials
    if test_credentials and test_credentials.get("congress_gov_api_key")
    else {"congress_gov_api_key": "MOCK_API_KEY"}
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("api_key", "MOCK_API_KEY"),
        ],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


def test_year_to_congress():
    """Test year to congress conversion."""
    current_year = datetime.now().year
    assert year_to_congress(current_year) >= 119
    assert year_to_congress(2000) == 106
    assert year_to_congress(1993) == 103
    with pytest.raises(ValueError):
        year_to_congress(1930)


_BULK_BILL_RECORD = {
    "congress": 119,
    "number": 1947,
    "type": "S",
    "bill_id": "119-s-1947",
    "originChamber": "Senate",
    "originChamberCode": "S",
    "title": "A Test Bill",
    "introducedDate": "2025-01-03",
    "updateDate": "2025-11-30T06:37:21Z",
    "updateDateIncludingText": "2025-11-30T06:37:21Z",
    "latestAction": {"actionDate": "2025-02-10", "text": "Read the second time."},
    "policyArea": {"name": "Immigration"},
    "sponsors": [{"fullName": "Sen. Example"}],
    "cosponsors": [],
    "actions": [{"actionDate": "2025-02-10", "text": "Read.", "type": "Calendars"}],
    "committees": [],
    "relatedBills": [],
    "subjects": [{"name": "Border security", "updateDate": "2025-01-08"}],
    "titles": [{"title": "A Test Bill", "type": "Short Title"}],
    "summaries": [{"text": "<p>Summary.</p>", "actionDate": "2025-01-03"}],
}


def test_congress_bills_fetcher(monkeypatch, credentials=test_credentials):
    """Test Congress Bills fetcher offline against the GovInfo bulk path."""

    async def _fake_load_billstatus(congress, bill_type):
        return [dict(_BULK_BILL_RECORD)]

    monkeypatch.setattr(
        "openbb_congress_gov.utils.bulk.load_billstatus", _fake_load_billstatus
    )
    params = {
        "limit": 1,
    }

    fetcher = CongressBillsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


def test_congress_bill_info_fetcher(monkeypatch, credentials=test_credentials):
    """Test Congress Bill Info fetcher offline against the GovInfo bulk path."""

    async def _fake_load_bill_record(bill_id):
        return dict(_BULK_BILL_RECORD)

    monkeypatch.setattr(
        "openbb_congress_gov.utils.bulk.load_bill_record", _fake_load_bill_record
    )
    params = {
        "bill_id": "119-s-1947",
    }

    fetcher = CongressBillInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_congress_bill_text_fetcher(credentials=test_credentials):
    """Test Congress Bill Text fetcher."""
    params = {
        "urls": [
            "https://www.govinfo.gov/content/pkg/BILLS-119hr29ih/pdf/BILLS-119hr29ih.pdf"
        ],
    }

    fetcher = CongressBillTextFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


_BULK_AMENDMENT_RECORD = {
    "amendment_id": "119-hamdt-2",
    "congress": 119,
    "number": "2",
    "type": "HAMDT",
    "description": "An amendment in the nature of a substitute.",
    "purpose": "To amend.",
    "chamber": "House of Representatives",
    "updateDate": "2025-02-10T08:00:00Z",
    "proposedDate": "",
    "submittedDate": "2025-02-09T05:00:00Z",
    "latestAction": {
        "actionDate": "2025-02-10",
        "actionTime": "",
        "text": "Agreed to without objection.",
    },
    "sponsors": [{"fullName": "Rep. Example", "party": "R"}],
    "cosponsors": [],
    "actions": [{"actionDate": "2025-02-10", "text": "Agreed.", "type": "X"}],
    "links": [],
    "amendedBill": {"congress": "119", "type": "HR", "number": "1", "title": "A Bill"},
    "amendedAmendment": {},
}


def test_congress_amendments_fetcher(monkeypatch, credentials=test_credentials):
    """Test Congress Amendments fetcher offline against the bulk path."""

    async def _fake_load_amendments(congress, amendment_type=None):
        return [dict(_BULK_AMENDMENT_RECORD)]

    monkeypatch.setattr(
        "openbb_congress_gov.utils.bulk.load_amendments", _fake_load_amendments
    )
    params = {"congress": 119, "limit": 1}

    fetcher = CongressAmendmentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


def test_congress_amendment_info_fetcher(monkeypatch, credentials=test_credentials):
    """Test Congress Amendment Info fetcher offline against the bulk path."""

    async def _fake_load_amendment_record(amendment_id):
        return dict(_BULK_AMENDMENT_RECORD)

    monkeypatch.setattr(
        "openbb_congress_gov.utils.bulk.load_amendment_record",
        _fake_load_amendment_record,
    )
    params = {"amendment_id": "119-hamdt-2"}

    fetcher = CongressAmendmentInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_congress_amendment_text_fetcher(credentials=test_credentials):
    """Test Congress Amendment Text fetcher against a GovInfo CREC document."""
    params = {
        "urls": [
            "https://www.govinfo.gov/content/pkg/CREC-2026-03-21/pdf/CREC-2026-03-21-pt1-PgS1484-6.pdf"
        ],
    }

    fetcher = CongressAmendmentTextFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


def test_congress_committee_documents_fetcher(
    monkeypatch, credentials=test_credentials
):
    """Test Congress Committee Documents fetcher offline against the keyless path."""

    async def _fake_fetch(system_code, congress, doc_type="all", limit=20, offset=0):
        return [
            {
                "doc_type": "report",
                "citation": "S. Rept. 119-5",
                "title": "A Committee Report",
                "date": "2026-05-04",
                "congress": 119,
                "chamber": "Senate",
                "package_id": "CRPT-119srpt5",
                "doc_url": "https://www.govinfo.gov/content/pkg/CRPT-119srpt5/pdf/CRPT-119srpt5.pdf",
            }
        ]

    monkeypatch.setattr(
        "openbb_congress_gov.utils.committees.fetch_committee_documents", _fake_fetch
    )
    params = {
        "chamber": "senate",
        "committee": "slin00",
        "doc_type": "report",
        "congress": 119,
        "limit": 5,
    }

    fetcher = CongressCommitteeDocumentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


def test_congress_committee_info_fetcher(monkeypatch, credentials=test_credentials):
    """Test Congress Committee Info fetcher offline against the keyless path."""

    async def _fake_overview(system_code, chamber):
        return {
            "chamber": chamber,
            "system_code": system_code,
            "detail": {
                "name": "Senate Committee on Indian Affairs",
                "chamber": chamber,
                "type": "senate",
                "website": "https://www.indian.senate.gov",
                "jurisdiction": "Indian affairs.",
                "is_subcommittee": False,
                "parent_name": "",
                "subcommittees": [],
            },
            "members": [{"name": "Sen. Chair", "party": "majority", "title": "Chair"}],
        }

    monkeypatch.setattr(
        "openbb_congress_gov.utils.committees.get_committee_overview", _fake_overview
    )
    params = {
        "chamber": "senate",
        "committee": "slin00",
    }

    fetcher = CongressCommitteeInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
