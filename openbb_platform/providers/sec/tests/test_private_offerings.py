"""Tests for SEC private offering routes."""

from __future__ import annotations

import asyncio
from datetime import date
from types import SimpleNamespace

from openbb_sec.models.private_offering_people import (
    SecPrivateOfferingPeopleFetcher,
    SecPrivateOfferingPeopleQueryParams,
    load_private_offering_people_records,
)
from openbb_sec.models.private_offerings import (
    SecPrivateOfferingsFetcher,
    SecPrivateOfferingsQueryParams,
    load_normalized_form_d_records,
    normalize_form_d_document,
)

FORM_D_XML = """<?xml version="1.0"?>
<edgarSubmission>
  <primaryIssuer>
    <entityName>Acme Fund LP</entityName>
    <issuerCik>123456789</issuerCik>
    <industryGroup>
      <industryGroupType>Pooled Investment Fund</industryGroupType>
    </industryGroup>
  </primaryIssuer>
  <offeringData>
    <typeOfFiling>
      <dateOfFirstSale>
        <value>2024-06-15</value>
      </dateOfFirstSale>
    </typeOfFiling>
    <offeringSalesAmounts>
      <totalOfferingAmount>1000000</totalOfferingAmount>
      <totalAmountSold>250000</totalAmountSold>
      <totalRemaining>750000</totalRemaining>
    </offeringSalesAmounts>
    <investors>
      <totalNumberAlreadyInvested>4</totalNumberAlreadyInvested>
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
        <relatedPersonCity>Boston</relatedPersonCity>
        <relatedPersonStateOrCountry>MA</relatedPersonStateOrCountry>
        <relatedPersonStateOrCountryDescription>Massachusetts</relatedPersonStateOrCountryDescription>
      </relatedPersonAddress>
    </relatedPersonInfo>
  </relatedPersonsList>
</edgarSubmission>
"""


def test_private_offering_query_models_do_not_expose_url() -> None:
    """Private offering routes use business identifiers, not document URLs."""
    assert "url" not in SecPrivateOfferingsQueryParams.model_fields
    assert "url" not in SecPrivateOfferingPeopleQueryParams.model_fields
    assert "accession_number" in SecPrivateOfferingPeopleQueryParams.model_fields


def test_normalize_form_d_document_returns_offering_and_people() -> None:
    """A Form D XML document is normalized into two dataframeable row groups."""
    normalized = normalize_form_d_document(
        FORM_D_XML,
        accession_number="0001234567-24-000001",
        filing_date=date(2024, 6, 20),
    )

    assert normalized.offering == {
        "issuer_cik": "0123456789",
        "issuer_name": "Acme Fund LP",
        "accession_number": "0001234567-24-000001",
        "filing_date": date(2024, 6, 20),
        "first_sale_date": date(2024, 6, 15),
        "industry_group": "Pooled Investment Fund",
        "offering_amount": 1000000,
        "sold_amount": 250000,
        "remaining_amount": 750000,
        "investor_count": 4,
        "is_private_fund": True,
    }
    assert normalized.people == [
        {
            "issuer_cik": "0123456789",
            "issuer_name": "Acme Fund LP",
            "accession_number": "0001234567-24-000001",
            "filing_date": date(2024, 6, 20),
            "person_name": "Jane Doe",
            "relationship": "Executive Officer",
            "address_city": "Boston",
            "address_state": "MA",
            "address_country": "Massachusetts",
        }
    ]


def test_private_offerings_fetcher_returns_flat_offering_rows(monkeypatch) -> None:
    """The private offerings route returns one row per Form D offering."""
    monkeypatch.setattr(
        "openbb_sec.models.private_offerings.load_private_offering_records",
        lambda **_kwargs: [
            {
                "issuer_cik": "0123456789",
                "issuer_name": "Acme Fund LP",
                "accession_number": "0001234567-24-000001",
                "filing_date": date(2024, 6, 20),
                "sold_amount": 250000,
            }
        ],
    )

    query = SecPrivateOfferingsQueryParams(cik="123456789")
    data = asyncio.run(SecPrivateOfferingsFetcher.aextract_data(query, None))
    result = SecPrivateOfferingsFetcher.transform_data(query, data)

    assert len(result) == 1
    assert result[0].issuer_cik == "0123456789"
    assert result[0].sold_amount == 250000


def test_private_offerings_skip_malformed_form_d_documents(monkeypatch) -> None:
    """Malformed individual Form D documents do not fail the CIK-level route."""
    filings = [
        SimpleNamespace(
            report_url="https://www.sec.gov/valid.xml",
            accession_number="0001234567-24-000001",
            filing_date=date(2024, 6, 20),
        ),
        SimpleNamespace(
            report_url="https://www.sec.gov/bad.xml",
            accession_number="0001234567-24-000002",
            filing_date=date(2024, 6, 21),
        ),
        SimpleNamespace(
            report_url="https://www.sec.gov/bad-encoding.txt",
            accession_number="0001234567-24-000003",
            filing_date=date(2024, 6, 22),
        ),
    ]

    async def fake_fetch_data(*_args: object, **_kwargs: object) -> list[object]:
        return filings

    async def fake_download(url: str, _use_cache: bool) -> str:
        if url.endswith("bad-encoding.txt"):
            raise UnicodeDecodeError("utf-8", b"\xe2", 0, 1, "bad encoding")
        if url.endswith("bad.xml"):
            return "<edgarSubmission><primaryIssuer></edgarSubmission>"
        return FORM_D_XML

    monkeypatch.setattr(
        "openbb_sec.models.company_filings.SecCompanyFilingsFetcher.fetch_data",
        fake_fetch_data,
    )
    monkeypatch.setattr(
        "openbb_sec.models.sec_filing.Filing._adownload_file",
        fake_download,
    )

    result = asyncio.run(load_normalized_form_d_records(cik="123456789"))

    assert len(result) == 1
    assert result[0].offering["accession_number"] == "0001234567-24-000001"


def test_private_offerings_prefer_complete_submission_url(monkeypatch) -> None:
    """Form D parsing uses the raw complete submission when available."""
    filings = [
        SimpleNamespace(
            report_url="https://www.sec.gov/transformed.xml",
            complete_submission_url="https://www.sec.gov/raw.txt",
            accession_number="0001234567-24-000001",
            filing_date=date(2024, 6, 20),
        )
    ]
    downloaded_urls: list[str] = []

    async def fake_fetch_data(*_args: object, **_kwargs: object) -> list[object]:
        return filings

    async def fake_download(url: str, _use_cache: bool) -> str:
        downloaded_urls.append(url)
        return FORM_D_XML

    monkeypatch.setattr(
        "openbb_sec.models.company_filings.SecCompanyFilingsFetcher.fetch_data",
        fake_fetch_data,
    )
    monkeypatch.setattr(
        "openbb_sec.models.sec_filing.Filing._adownload_file",
        fake_download,
    )

    result = asyncio.run(load_normalized_form_d_records(cik="123456789"))

    assert len(result) == 1
    assert downloaded_urls == ["https://www.sec.gov/raw.txt"]


def test_private_offering_people_fetcher_returns_flat_person_rows(monkeypatch) -> None:
    """The private offering people route returns one row per related person."""
    monkeypatch.setattr(
        "openbb_sec.models.private_offering_people.load_private_offering_people_records",
        lambda **_kwargs: [
            {
                "issuer_cik": "0123456789",
                "issuer_name": "Acme Fund LP",
                "accession_number": "0001234567-24-000001",
                "filing_date": date(2024, 6, 20),
                "person_name": "Jane Doe",
            }
        ],
    )

    query = SecPrivateOfferingPeopleQueryParams(cik="123456789")
    data = asyncio.run(SecPrivateOfferingPeopleFetcher.aextract_data(query, None))
    result = SecPrivateOfferingPeopleFetcher.transform_data(query, data)

    assert len(result) == 1
    assert result[0].person_name == "Jane Doe"


def test_private_offering_people_can_load_exact_accession_number(
    monkeypatch,
) -> None:
    """The people route can load a staged Form D filing by accession number."""
    downloaded_urls = []

    async def fake_fetch_data(*_args: object, **_kwargs: object) -> list[object]:
        raise AssertionError("CIK filing scan should not be used")

    async def fake_download(url: str, _use_cache: bool) -> str:
        downloaded_urls.append(url)
        return f"""
<SEC-DOCUMENT>0001234567-24-000001.txt
<DOCUMENT>
<TYPE>D
<SEQUENCE>1
<FILENAME>primary_doc.xml
<TEXT>
{FORM_D_XML}
</TEXT>
</DOCUMENT>
</SEC-DOCUMENT>
"""

    monkeypatch.setattr(
        "openbb_sec.models.company_filings.SecCompanyFilingsFetcher.fetch_data",
        fake_fetch_data,
    )
    monkeypatch.setattr(
        "openbb_sec.models.sec_filing.Filing._adownload_file",
        fake_download,
    )

    result = asyncio.run(
        load_private_offering_people_records(
            accession_number="0001234567-24-000001",
            use_cache=False,
        )
    )

    assert downloaded_urls == [
        "https://www.sec.gov/Archives/edgar/data/1234567/"
        "000123456724000001/0001234567-24-000001.txt"
    ]
    assert result == [
        {
            "issuer_cik": "0123456789",
            "issuer_name": "Acme Fund LP",
            "accession_number": "0001234567-24-000001",
            "filing_date": None,
            "person_name": "Jane Doe",
            "relationship": "Executive Officer",
            "address_city": "Boston",
            "address_state": "MA",
            "address_country": "Massachusetts",
        }
    ]


def test_private_offering_people_fetcher_passes_accession_selector(
    monkeypatch,
) -> None:
    """The people route can select one exact Form D filing by accession number."""
    calls: list[dict[str, object]] = []

    def fake_loader(**kwargs: object) -> list[dict[str, object]]:
        calls.append(kwargs)
        return []

    monkeypatch.setattr(
        "openbb_sec.models.private_offering_people.load_private_offering_people_records",
        fake_loader,
    )

    query = SecPrivateOfferingPeopleQueryParams(
        cik="123456789",
        accession_number="0001234567-24-000001",
    )
    asyncio.run(SecPrivateOfferingPeopleFetcher.aextract_data(query, None))

    assert calls[0]["accession_number"] == "0001234567-24-000001"
