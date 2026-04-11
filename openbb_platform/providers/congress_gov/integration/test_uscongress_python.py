"""Test Government extension."""

import pytest
from openbb_congress_gov.models.bill_info import CongressBillInfoData
from openbb_congress_gov.models.bill_text import CongressBillTextData
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):  # pylint: disable=inconsistent-return-statements
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


# pylint: disable=redefined-outer-name


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
            }
        ),
        (
            {
                "provider": "congress_gov",
                "limit": 5,
                "offset": 0,
                "sort_by": "desc",
                "congress": None,
                "bill_type": None,
                "start_date": None,
                "end_date": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_bills(params, obb):
    """Test US Congress bills."""
    params = {p: v for p, v in params.items() if v}

    result = obb.uscongress.bills(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "bill_url": "119/hr/1",
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_bill_info(params, obb):
    """Test US Congress bill info."""
    params = {p: v for p, v in params.items() if v}

    result = obb.uscongress.bill_info(**params)
    assert result
    assert isinstance(result, OBBject)
    assert isinstance(result.results, CongressBillInfoData)
    assert isinstance(result.results.markdown_content, str)
    assert isinstance(result.results.raw_data, dict)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "bill_url": "https://api.congress.gov/v3/bill/119/s/1947?format=json",
                "is_workspace": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_bill_text_urls(params, obb):
    """Test US Congress bill text URLs."""
    params = {p: v for p, v in params.items() if v}

    result = obb.uscongress.bill_text_urls(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "urls": [
                    "https://www.congress.gov/119/bills/hr1/BILLS-119hr1eh.pdf",
                ],
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_bill_text(params, obb):
    """Test US Congress bill text."""
    params = {p: v for p, v in params.items() if v}

    result = obb.uscongress.bill_text(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], CongressBillTextData)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "congress": 119,
                "limit": 1,
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_amendments(params, obb):
    """Test US Congress amendments."""
    params = {p: v for p, v in params.items() if v}

    result = obb.uscongress.amendments(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "amendment_url": "119/hamdt/2",
                "is_workspace": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_amendment_text_urls(params, obb):
    """Test US Congress amendment text URLs."""
    params = {p: v for p, v in params.items() if v}

    result = obb.uscongress.amendment_text_urls(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "amendment_url": "119/hamdt/2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_amendment_info(params, obb):
    """Test US Congress amendment info."""
    params = {p: v for p, v in params.items() if v}

    result = obb.uscongress.amendment_info(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "urls": [
                    "https://www.congress.gov/119/crec/2026/03/21/172/52/CREC-2026-03-21-pt1-PgS1484-6.pdf",
                ],
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_amendment_text(params, obb):
    """Test US Congress amendment text."""
    params = {p: v for p, v in params.items() if v}

    result = obb.uscongress.amendment_text(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "chamber": "senate",
                "committee": "slin00",
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_committee_info(params, obb):
    """Test US Congress committee info."""
    params = {p: v for p, v in params.items() if v}

    result = obb.uscongress.committee_info(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "chamber": "senate",
                "committee": "slin00",
                "doc_type": "report",
                "congress": 119,
                "limit": 5,
                "use_cache": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_committee_documents(params, obb):
    """Test US Congress committee documents."""
    params = {p: v for p, v in params.items() if v}

    result = obb.uscongress.committee_documents(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "chamber": "senate",
                "congress": None,
                "committee": None,
                "subcommittees": None,
                "is_workspace": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_committee_choices(params, obb):
    """Test US Congress committee choices."""
    params = {p: v for p, v in params.items() if v}

    result = obb.uscongress.committee_choices(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "congress_gov",
                "chamber": "senate",
                "committee": "slin00",
                "subcommittee": None,
                "doc_type": "report",
                "congress": 119,
                "is_workspace": False,
                "use_cache": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_uscongress_committee_document_urls(params, obb):
    """Test US Congress committee document URLs."""
    params = {p: v for p, v in params.items() if v}

    result = obb.uscongress.committee_document_urls(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0
