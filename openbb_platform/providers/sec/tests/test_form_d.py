"""Tests for exact SEC Form D filing normalization."""

from __future__ import annotations

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_sec.models.form_d import (
    SecFormDFetcher,
    SecFormDQueryParams,
    _complete_submission_url,
    normalize_form_d_document,
)


def test_form_d_query_requires_accession_number() -> None:
    """Form D route is an exact filing lookup, not a broad search endpoint."""
    with pytest.raises(ValueError, match="accession_number"):
        SecFormDQueryParams(cik="0001841359")


def test_form_d_query_requires_issuer_cik() -> None:
    """An accession prefix cannot be assumed to identify the Form D issuer."""
    with pytest.raises(ValueError, match="cik"):
        SecFormDQueryParams(accession_number="0001104659-25-099416")


def test_form_d_fetcher_returns_one_offering_with_related_people(monkeypatch) -> None:
    """The Form D route exposes one normalized filing by accession number."""
    offering = {
        "issuer_cik": "0001841359",
        "issuer_name": "Acme Fund LP",
        "accession_number": "0001841359-24-000001",
        "filing_date": None,
        "first_sale_date": None,
        "industry_group": "Pooled Investment Fund",
        "offering_amount": 1000,
        "sold_amount": 750,
        "remaining_amount": 250,
        "investor_count": 3,
        "is_private_fund": True,
        "related_people": [
            {
                "person_name": "Jane Doe",
                "relationship": "Executive Officer",
                "address_city": "New York",
                "address_state": "NY",
                "address_country": "United States",
            }
        ],
    }

    async def fake_load_form_d_record(**kwargs: object) -> dict[str, object]:
        assert kwargs["accession_number"] == "0001841359-24-000001"
        assert kwargs["cik"] == "0001841359"
        return offering

    monkeypatch.setattr(
        "openbb_sec.models.form_d.load_form_d_record",
        fake_load_form_d_record,
    )

    query = SecFormDQueryParams(
        cik="0001841359",
        accession_number="0001841359-24-000001",
    )
    data = asyncio.run(SecFormDFetcher.aextract_data(query, None))
    result = SecFormDFetcher.transform_data(query, data)

    assert len(result) == 1
    assert result[0].issuer_name == "Acme Fund LP"
    assert result[0].related_people[0]["person_name"] == "Jane Doe"


def test_form_d_fetcher_raises_for_missing_filing(monkeypatch) -> None:
    """An accession lookup with no parseable filing reports an OpenBB error."""

    async def fake_load_form_d_record(**_kwargs: object) -> dict[str, object]:
        return {}

    monkeypatch.setattr(
        "openbb_sec.models.form_d.load_form_d_record",
        fake_load_form_d_record,
    )

    query = SecFormDQueryParams(
        cik="0001841359",
        accession_number="0001841359-24-000001",
    )

    with pytest.raises(OpenBBError, match="No Form D filing"):
        asyncio.run(SecFormDFetcher.aextract_data(query, None))


def test_normalize_form_d_document_embeds_related_people() -> None:
    """Normalized Form D records keep offering fields and related people together."""
    document = """
    <edgarSubmission>
      <primaryIssuer>
        <cik>1841359</cik>
        <entityName>Acme Fund LP</entityName>
        <industryGroup>
          <industryGroupType>Pooled Investment Fund</industryGroupType>
        </industryGroup>
      </primaryIssuer>
      <offeringData>
        <offeringSalesAmounts>
          <totalOfferingAmount>1000</totalOfferingAmount>
          <totalAmountSold>750</totalAmountSold>
          <totalRemaining>250</totalRemaining>
        </offeringSalesAmounts>
        <investors>
          <totalNumberAlreadyInvested>3</totalNumberAlreadyInvested>
        </investors>
      </offeringData>
      <relatedPersonsList>
        <relatedPersonInfo>
          <relatedPersonName>
            <firstName>Jane</firstName>
            <lastName>Doe</lastName>
          </relatedPersonName>
          <relatedPersonRelationshipList>
            <relationship>Executive Officer</relationship>
          </relatedPersonRelationshipList>
          <relatedPersonAddress>
            <relatedPersonCity>New York</relatedPersonCity>
            <relatedPersonStateOrCountry>NY</relatedPersonStateOrCountry>
            <relatedPersonStateOrCountryDescription>United States</relatedPersonStateOrCountryDescription>
          </relatedPersonAddress>
        </relatedPersonInfo>
      </relatedPersonsList>
    </edgarSubmission>
    """

    row = normalize_form_d_document(
        document,
        accession_number="0001841359-24-000001",
    )

    assert row["issuer_cik"] == "0001841359"
    assert row["issuer_name"] == "Acme Fund LP"
    assert row["related_people"] == [
        {
            "person_name": "Jane Doe",
            "relationship": "Executive Officer",
            "address_city": "New York",
            "address_state": "NY",
            "address_country": "United States",
        }
    ]


def test_complete_submission_url_uses_issuer_cik() -> None:
    """Filing-agent accession prefixes do not determine archive directories."""
    assert _complete_submission_url(
        "0001104659-25-099416",
        "0000744452",
    ) == (
        "https://www.sec.gov/Archives/edgar/data/744452/"
        "000110465925099416/0001104659-25-099416.txt"
    )
