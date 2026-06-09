"""Integration tests for the uscongress Python interface (obb.uscongress)."""

import pytest
from openbb_core.app.model.obbject import OBBject

from openbb_congress_gov.models.bill_info import CongressBillInfoData


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


def _clean(params: dict) -> dict:
    """Drop None values so omitted params fall back to their defaults."""
    return {k: v for k, v in params.items() if v is not None}


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "congress_gov"},
        {
            "provider": "congress_gov",
            "congress": 119,
            "bill_type": "hr",
            "start_date": None,
            "end_date": None,
            "limit": 5,
            "offset": 0,
            "sort_by": "desc",
        },
    ],
)
@pytest.mark.integration
def test_uscongress_bills(params, obb):
    """List Congressional bills."""
    result = obb.uscongress.bills(**_clean(params))
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "bill_id": "119-hr-1"}],
)
@pytest.mark.integration
def test_uscongress_bill_info(params, obb):
    """Bill metadata + CRS summary as Markdown."""
    result = obb.uscongress.bill_info(**_clean(params))
    assert isinstance(result, OBBject)
    assert isinstance(result.results, CongressBillInfoData)
    assert isinstance(result.results.markdown_content, str)


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "bill_id": "119-hr-1", "is_workspace": True}],
)
@pytest.mark.integration
def test_uscongress_bill_text_urls(params, obb):
    """Resolvable text-version document links for a bill."""
    result = obb.uscongress.bill_text_urls(**_clean(params))
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [
        {
            "provider": "congress_gov",
            "urls": [
                "https://www.govinfo.gov/content/pkg/BILLS-119hr29ih/pdf/BILLS-119hr29ih.pdf"
            ],
        }
    ],
)
@pytest.mark.integration
def test_uscongress_bill_text(params, obb):
    """Download a bill text document from GovInfo."""
    result = obb.uscongress.bill_text(**_clean(params))
    assert isinstance(result, list)
    assert len(result) > 0


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
def test_uscongress_amendments(params, obb):
    """List Congressional amendments."""
    result = obb.uscongress.amendments(**_clean(params))
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "amendment_id": "119-hamdt-1"}],
)
@pytest.mark.integration
def test_uscongress_amendment_info(params, obb):
    """Amendment metadata as Markdown."""
    result = obb.uscongress.amendment_info(**_clean(params))
    assert isinstance(result, OBBject)
    assert isinstance(result.results.markdown_content, str)


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "amendment_id": "119-hamdt-1", "is_workspace": True}],
)
@pytest.mark.integration
def test_uscongress_amendment_text_urls(params, obb):
    """Congressional Record document choices for an amendment."""
    result = obb.uscongress.amendment_text_urls(**_clean(params))
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [
        {
            "provider": "congress_gov",
            "urls": [
                "https://www.govinfo.gov/content/pkg/CREC-2026-03-21/pdf/CREC-2026-03-21-pt1-PgS1484-6.pdf"
            ],
        }
    ],
)
@pytest.mark.integration
def test_uscongress_amendment_text(params, obb):
    """Download an amendment's Congressional Record document from GovInfo."""
    result = obb.uscongress.amendment_text(**_clean(params))
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "congress": 119, "law_type": "public", "limit": 5}],
)
@pytest.mark.integration
def test_uscongress_laws(params, obb):
    """List enacted public/private laws."""
    result = obb.uscongress.laws(**_clean(params))
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


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
def test_uscongress_law_text_urls(params, obb):
    """Document links for an enacted law."""
    result = obb.uscongress.law_text_urls(**_clean(params))
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "chamber": "house", "congress": 119, "limit": 5}],
)
@pytest.mark.integration
def test_uscongress_calendars(params, obb):
    """List daily House/Senate calendar editions."""
    result = obb.uscongress.calendars(**_clean(params))
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


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
def test_uscongress_calendar_document_urls(params, obb):
    """Document links for a calendar edition."""
    result = obb.uscongress.calendar_document_urls(**_clean(params))
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "congress": 119, "limit": 5}],
)
@pytest.mark.integration
def test_uscongress_mandated_reports(params, obb):
    """List congressionally mandated reports."""
    result = obb.uscongress.mandated_reports(**_clean(params))
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


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
def test_uscongress_mandated_report_urls(params, obb):
    """Document link for a mandated report."""
    result = obb.uscongress.mandated_report_urls(**_clean(params))
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "chamber": "senate", "committee": "ssaf00"}],
)
@pytest.mark.integration
def test_uscongress_committee_info(params, obb):
    """Committee overview (structure + members)."""
    result = obb.uscongress.committee_info(**_clean(params))
    assert isinstance(result, OBBject)


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
def test_uscongress_committee_documents(params, obb):
    """Committee documents (reports, hearings, prints)."""
    result = obb.uscongress.committee_documents(**_clean(params))
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "chamber": "senate", "is_workspace": True}],
)
@pytest.mark.integration
def test_uscongress_committee_choices(params, obb):
    """Committee dropdown choices for a chamber."""
    result = obb.uscongress.committee_choices(**_clean(params))
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [
        {
            "provider": "congress_gov",
            "chamber": "senate",
            "committee": "ssaf00",
            "subcommittee": None,
            "doc_type": "report",
            "congress": 119,
            "is_workspace": True,
        }
    ],
)
@pytest.mark.integration
def test_uscongress_committee_document_urls(params, obb):
    """Committee document choices for the viewer."""
    result = obb.uscongress.committee_document_urls(**_clean(params))
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "query": "immigration", "congress": 119, "limit": 5}],
)
@pytest.mark.integration
def test_uscongress_search(params, obb):
    """Full-text search across the congressional GovInfo collections."""
    result = obb.uscongress.search(**_clean(params))
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


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
def test_uscongress_search_document_urls(params, obb):
    """Document link for a search result."""
    result = obb.uscongress.search_document_urls(**_clean(params))
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "chamber": "house", "state": "OH"}],
)
@pytest.mark.integration
def test_uscongress_members(params, obb):
    """List current members of Congress."""
    result = obb.uscongress.members(**_clean(params))
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


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
def test_uscongress_member_votes(params, obb):
    """A member's roll-call votes on legislation (Voteview)."""
    result = obb.uscongress.member_votes(**_clean(params))
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "bioguide_id": "A000055", "congress": 119}],
)
@pytest.mark.integration
def test_uscongress_member_legislation(params, obb):
    """Bills a member sponsored or cosponsored."""
    result = obb.uscongress.member_legislation(**_clean(params))
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "congress_gov", "chamber": "house", "is_workspace": True}],
)
@pytest.mark.integration
def test_uscongress_member_choices(params, obb):
    """Bioguide picker choices for the member widgets."""
    result = obb.uscongress.member_choices(**_clean(params))
    assert isinstance(result, list)
    assert len(result) > 0
