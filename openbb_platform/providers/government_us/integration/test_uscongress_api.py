"""Integration tests for the uscongress REST API."""

import pytest
import requests
from openbb_core.provider.utils.helpers import get_querystring

BASE = "http://127.0.0.1:8000/api/v1/uscongress"


def _get(endpoint: str, params: dict, headers: dict) -> requests.Response:
    """GET an endpoint with None-stripped query params."""
    query = get_querystring({k: v for k, v in params.items() if v is not None}, [])
    return requests.get(f"{BASE}/{endpoint}?{query}", headers=headers, timeout=30)


def _post_urls(endpoint: str, urls: list, headers: dict) -> requests.Response:
    """POST a document-download endpoint with a list of URLs."""
    return requests.post(f"{BASE}/{endpoint}", headers=headers, json=urls, timeout=30)


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "congress_gov"},
        {
            "provider": "congress_gov",
            "congress": 119,
            "bill_type": "hr",
            "limit": 5,
            "offset": 0,
            "sort_by": "desc",
        },
    ],
)
@pytest.mark.integration
def test_uscongress_bills(params, headers):
    """GET /bills."""
    assert _get("bills", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params", [{"provider": "congress_gov", "bill_id": "119-hr-1"}]
)
@pytest.mark.integration
def test_uscongress_bill_info(params, headers):
    """GET /bill_info."""
    assert _get("bill_info", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "bill_id": "119-hr-1", "is_workspace": True}],
)
@pytest.mark.integration
def test_uscongress_bill_text_urls(params, headers):
    """GET /bill_text_urls."""
    assert _get("bill_text_urls", params, headers).status_code == 200


@pytest.mark.parametrize(
    "urls",
    [["https://www.govinfo.gov/content/pkg/BILLS-119hr29ih/pdf/BILLS-119hr29ih.pdf"]],
)
@pytest.mark.integration
def test_uscongress_bill_text(urls, headers):
    """POST /bill_text."""
    assert _post_urls("bill_text", urls, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "provider": "congress_gov",
            "congress": 119,
            "amendment_type": "samdt",
            "limit": 5,
        }
    ],
)
@pytest.mark.integration
def test_uscongress_amendments(params, headers):
    """GET /amendments."""
    assert _get("amendments", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params", [{"provider": "congress_gov", "amendment_id": "119-hamdt-1"}]
)
@pytest.mark.integration
def test_uscongress_amendment_info(params, headers):
    """GET /amendment_info."""
    assert _get("amendment_info", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "amendment_id": "119-hamdt-1", "is_workspace": True}],
)
@pytest.mark.integration
def test_uscongress_amendment_text_urls(params, headers):
    """GET /amendment_text_urls."""
    assert _get("amendment_text_urls", params, headers).status_code == 200


@pytest.mark.parametrize(
    "urls",
    [
        [
            "https://www.govinfo.gov/content/pkg/CREC-2026-03-21/pdf/CREC-2026-03-21-pt1-PgS1484-6.pdf"
        ]
    ],
)
@pytest.mark.integration
def test_uscongress_amendment_text(urls, headers):
    """POST /amendment_text."""
    assert _post_urls("amendment_text", urls, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "congress": 119, "law_type": "public", "limit": 5}],
)
@pytest.mark.integration
def test_uscongress_laws(params, headers):
    """GET /laws."""
    assert _get("laws", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "provider": "congress_gov",
            "law_id": "119-1",
            "law_type": "public",
            "is_workspace": True,
        }
    ],
)
@pytest.mark.integration
def test_uscongress_law_text_urls(params, headers):
    """GET /law_text_urls."""
    assert _get("law_text_urls", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "chamber": "house", "congress": 119, "limit": 5}],
)
@pytest.mark.integration
def test_uscongress_calendars(params, headers):
    """GET /calendars."""
    assert _get("calendars", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "provider": "congress_gov",
            "package_id": "CCAL-119hcal-2025-01-03",
            "is_workspace": True,
        }
    ],
)
@pytest.mark.integration
def test_uscongress_calendar_document_urls(params, headers):
    """GET /calendar_document_urls."""
    assert _get("calendar_document_urls", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params", [{"provider": "congress_gov", "congress": 119, "limit": 5}]
)
@pytest.mark.integration
def test_uscongress_mandated_reports(params, headers):
    """GET /mandated_reports."""
    assert _get("mandated_reports", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "provider": "congress_gov",
            "package_id": "CMR-A98-00199920",
            "is_workspace": True,
        }
    ],
)
@pytest.mark.integration
def test_uscongress_mandated_report_urls(params, headers):
    """GET /mandated_report_urls."""
    assert _get("mandated_report_urls", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "chamber": "senate", "committee": "ssaf00"}],
)
@pytest.mark.integration
def test_uscongress_committee_info(params, headers):
    """GET /committee_info."""
    assert _get("committee_info", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "provider": "congress_gov",
            "chamber": "senate",
            "committee": "ssaf00",
            "doc_type": "report",
            "congress": 119,
            "limit": 5,
        }
    ],
)
@pytest.mark.integration
def test_uscongress_committee_documents(params, headers):
    """GET /committee_documents."""
    assert _get("committee_documents", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params", [{"provider": "congress_gov", "chamber": "senate", "is_workspace": True}]
)
@pytest.mark.integration
def test_uscongress_committee_choices(params, headers):
    """GET /committee_choices."""
    assert _get("committee_choices", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "provider": "congress_gov",
            "chamber": "senate",
            "committee": "ssaf00",
            "doc_type": "report",
            "congress": 119,
            "is_workspace": True,
        }
    ],
)
@pytest.mark.integration
def test_uscongress_committee_document_urls(params, headers):
    """GET /committee_document_urls."""
    assert _get("committee_document_urls", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "provider": "congress_gov",
            "chamber": "house",
            "committee": "hsju00",
            "theme": "dark",
        }
    ],
)
@pytest.mark.integration
def test_uscongress_committee_members(params, headers):
    """GET /committee_members (raw HTML widget)."""
    assert _get("committee_members", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "query": "immigration", "congress": 119, "limit": 5}],
)
@pytest.mark.integration
def test_uscongress_search(params, headers):
    """GET /search."""
    assert _get("search", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "provider": "congress_gov",
            "package_id": "CHRG-119hhrg63299",
            "is_workspace": True,
        }
    ],
)
@pytest.mark.integration
def test_uscongress_search_document_urls(params, headers):
    """GET /search_document_urls."""
    assert _get("search_document_urls", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params", [{"provider": "congress_gov", "chamber": "house", "state": "OH"}]
)
@pytest.mark.integration
def test_uscongress_members(params, headers):
    """GET /members."""
    assert _get("members", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {
            "provider": "congress_gov",
            "bioguide_id": "A000055",
            "congress": 119,
            "limit": 5,
        }
    ],
)
@pytest.mark.integration
def test_uscongress_member_votes(params, headers):
    """GET /member_votes."""
    assert _get("member_votes", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "bioguide_id": "A000055", "congress": 119}],
)
@pytest.mark.integration
def test_uscongress_member_legislation(params, headers):
    """GET /member_legislation."""
    assert _get("member_legislation", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params", [{"provider": "congress_gov", "chamber": "house", "is_workspace": True}]
)
@pytest.mark.integration
def test_uscongress_member_choices(params, headers):
    """GET /member_choices."""
    assert _get("member_choices", params, headers).status_code == 200


@pytest.mark.parametrize("params", [{"bioguide_id": "A000055", "theme": "dark"}])
@pytest.mark.integration
def test_uscongress_member_info(params, headers):
    """GET /member_info (raw HTML bio card)."""
    assert _get("member_info", params, headers).status_code == 200


@pytest.mark.parametrize("params", [{"note": "members"}])
@pytest.mark.integration
def test_uscongress_how_to_use(params, headers):
    """GET /how_to_use (raw Markdown note)."""
    assert _get("how_to_use", params, headers).status_code == 200
