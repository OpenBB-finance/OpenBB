"""SEC private offerings from Form D filings."""

from __future__ import annotations

import inspect
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING, Any

from defusedxml import ElementTree
from defusedxml.ElementTree import ParseError
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element


@dataclass(frozen=True)
class NormalizedFormD:
    """Normalized Form D offering and related-person rows."""

    offering: dict[str, Any]
    people: list[dict[str, Any]]


class SecPrivateOfferingsQueryParams(QueryParams):
    """SEC private offerings query."""

    cik: str | int | None = Field(
        default=None,
        description="Central Index Key (CIK) for the Form D issuer.",
    )
    issuer: str | None = Field(
        default=None,
        description="Search text matched against the issuer name.",
    )
    start_date: date | None = Field(
        default=None,
        description="Start date for Form D filing dates.",
    )
    end_date: date | None = Field(
        default=None,
        description="End date for Form D filing dates.",
    )
    limit: int | None = Field(
        default=100,
        description="Maximum number of Form D offering rows to return.",
        ge=1,
    )
    use_cache: bool = Field(
        default=True,
        description="Whether or not to use cache.",
    )


class SecPrivateOfferingsData(Data):
    """SEC private offering row."""

    issuer_cik: str | None = Field(
        default=None,
        description="Central Index Key (CIK) for the issuer.",
    )
    issuer_name: str | None = Field(
        default=None,
        description="Name of the Form D issuer.",
    )
    accession_number: str | None = Field(
        default=None,
        description="SEC accession number for the Form D filing.",
    )
    filing_date: date | None = Field(
        default=None,
        description="Date the Form D filing was submitted to EDGAR.",
    )
    first_sale_date: date | None = Field(
        default=None,
        description="Date of first sale disclosed in the Form D filing.",
    )
    industry_group: str | None = Field(
        default=None,
        description="Industry group disclosed in the Form D filing.",
    )
    offering_amount: int | None = Field(
        default=None,
        description="Total offering amount disclosed in the Form D filing.",
    )
    sold_amount: int | None = Field(
        default=None,
        description="Total amount sold disclosed in the Form D filing.",
    )
    remaining_amount: int | None = Field(
        default=None,
        description="Total remaining amount disclosed in the Form D filing.",
    )
    investor_count: int | None = Field(
        default=None,
        description="Number of investors disclosed in the Form D filing.",
    )
    is_private_fund: bool | None = Field(
        default=None,
        description="Whether the offering appears to be a private fund offering.",
    )


class SecPrivateOfferingsFetcher(
    Fetcher[
        SecPrivateOfferingsQueryParams,
        list[SecPrivateOfferingsData],
    ]
):
    """SEC private offerings fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecPrivateOfferingsQueryParams:
        """Transform query parameters."""
        return SecPrivateOfferingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecPrivateOfferingsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return normalized Form D offering rows."""
        loaded = load_private_offering_records(
            cik=query.cik,
            issuer=query.issuer,
            start_date=query.start_date,
            end_date=query.end_date,
            limit=query.limit,
            use_cache=query.use_cache,
            **kwargs,
        )
        records = await loaded if inspect.isawaitable(loaded) else loaded
        return records

    @staticmethod
    def transform_data(
        query: SecPrivateOfferingsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SecPrivateOfferingsData]:
        """Transform raw data to the model format."""
        return [SecPrivateOfferingsData.model_validate(d) for d in data]


def load_private_offering_records(
    *,
    cik: str | int | None = None,
    issuer: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int | None = 100,
    use_cache: bool = True,
    **kwargs: Any,
) -> Any:
    """Load Form D offering records."""
    return _aload_private_offering_records(
        cik=cik,
        issuer=issuer,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        use_cache=use_cache,
        **kwargs,
    )


async def _aload_private_offering_records(
    *,
    cik: str | int | None = None,
    issuer: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int | None = 100,
    use_cache: bool = True,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Load Form D offering records from EDGAR filing documents."""
    normalized = await _load_normalized_form_d(
        cik=cik,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        use_cache=use_cache,
        **kwargs,
    )
    records = [item.offering for item in normalized]
    return _filter_by_issuer(records, issuer)


async def load_normalized_form_d_records(
    *,
    cik: str | int | None = None,
    accession_number: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int | None = 100,
    use_cache: bool = True,
    **kwargs: Any,
) -> list[NormalizedFormD]:
    """Load normalized Form D records for route-specific row projections."""
    return await _load_normalized_form_d(
        cik=cik,
        accession_number=accession_number,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        use_cache=use_cache,
        **kwargs,
    )


async def _load_normalized_form_d(
    *,
    cik: str | int | None = None,
    accession_number: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int | None = 100,
    use_cache: bool = True,
    **kwargs: Any,
) -> list[NormalizedFormD]:
    """Download Form D filing documents and normalize them."""
    from openbb_core.provider.abstract.annotated_result import AnnotatedResult

    from openbb_sec.models.company_filings import SecCompanyFilingsFetcher
    from openbb_sec.models.sec_filing import Filing

    if accession_number and cik is None:
        return await _load_normalized_form_d_by_accession(
            accession_number,
            use_cache=use_cache,
        )

    if cik is None:
        raise OpenBBError("A CIK is required.")

    fetched = await SecCompanyFilingsFetcher().fetch_data(
        {
            "cik": cik,
            "form_type": "D",
            "start_date": start_date,
            "end_date": end_date,
            "limit": 0 if accession_number else limit,
            "use_cache": use_cache,
        },
        {},
    )
    filings = (fetched.result or []) if isinstance(fetched, AnnotatedResult) else fetched
    if accession_number:
        filings = [
            filing
            for filing in filings
            if _clean_text(getattr(filing, "accession_number", None))
            == accession_number
        ]
    normalized: list[NormalizedFormD] = []
    for filing in filings:
        document_url = getattr(filing, "complete_submission_url", None) or getattr(
            filing,
            "report_url",
            None,
        )
        if not document_url:
            continue
        try:
            document = await Filing._adownload_file(str(document_url), use_cache)
            normalized.append(
                normalize_form_d_document(
                    _extract_form_d_document(document or ""),
                    accession_number=_clean_text(
                        getattr(filing, "accession_number", None)
                    ),
                    filing_date=getattr(filing, "filing_date", None),
                )
            )
        except (ParseError, UnicodeDecodeError):
            continue
    return normalized


async def _load_normalized_form_d_by_accession(
    accession_number: str,
    *,
    use_cache: bool,
) -> list[NormalizedFormD]:
    """Download and normalize one Form D filing by accession number."""
    from openbb_sec.models.sec_filing import Filing

    accession = _normalize_accession_number(accession_number)
    url = _complete_submission_url(accession)
    try:
        document = await Filing._adownload_file(url, use_cache)
        return [
            normalize_form_d_document(
                _extract_form_d_document(document or ""),
                accession_number=accession,
            )
        ]
    except (ParseError, UnicodeDecodeError):
        return []


def _complete_submission_url(accession_number: str) -> str:
    """Return the public EDGAR complete-submission URL for an accession."""
    cik = accession_number.split("-", maxsplit=1)[0].lstrip("0")
    accession_path = accession_number.replace("-", "")
    return (
        f"https://www.sec.gov/Archives/edgar/data/{cik}/"
        f"{accession_path}/{accession_number}.txt"
    )


def _normalize_accession_number(accession_number: str) -> str:
    """Normalize and validate a SEC accession number."""
    accession = _clean_text(accession_number) or ""
    match = re.fullmatch(r"(\d{10})-?(\d{2})-?(\d{6})", accession)
    if not match:
        raise OpenBBError("Accession number must use the SEC accession format.")
    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"


def _extract_form_d_document(document: str | bytes) -> str:
    """Extract the Form D document body from a complete-submission text filing."""
    text = (
        document.decode("utf-8", errors="replace")
        if isinstance(document, bytes)
        else document
    )
    for match in re.finditer(
        r"<DOCUMENT>(?P<body>.*?)</DOCUMENT>",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        body = match.group("body")
        type_match = re.search(
            r"<TYPE>\s*(?P<type>[^\n<]+)",
            body,
            flags=re.IGNORECASE,
        )
        if not type_match or _base_form_code(type_match.group("type")) != "D":
            continue
        text_match = re.search(
            r"<TEXT>\s*(?P<text>.*?)(?:</TEXT>|$)",
            body,
            flags=re.IGNORECASE | re.DOTALL,
        )
        content = text_match.group("text") if text_match else body
        xml_match = re.search(
            r"<XML>\s*(?P<xml>.*?)(?:</XML>|$)",
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )
        return (xml_match.group("xml") if xml_match else content).strip()
    return text


def _base_form_code(value: Any) -> str:
    """Return the SEC base form code."""
    form = str(value or "").strip().upper()
    return form[:-2] if form.endswith("/A") else form


def normalize_form_d_document(
    document: str | bytes,
    *,
    accession_number: str | None = None,
    filing_date: date | None = None,
) -> NormalizedFormD:
    """Normalize one Form D XML or text document."""
    text = (
        document.decode("utf-8", errors="replace")
        if isinstance(document, bytes)
        else document
    )
    if _looks_like_xml(text):
        return _normalize_form_d_xml(
            text,
            accession_number=accession_number,
            filing_date=filing_date,
        )
    return _normalize_form_d_text(
        text,
        accession_number=accession_number,
        filing_date=filing_date,
    )


def _normalize_form_d_xml(
    text: str,
    *,
    accession_number: str | None,
    filing_date: date | None,
) -> NormalizedFormD:
    """Normalize one Form D XML document."""
    root = ElementTree.fromstring(text)
    issuer_cik = _normalize_cik(_first_text(root, ("issuerCik", "issuerCIK", "cik")))
    issuer_name = _first_text(root, ("issuerName", "entityName", "nameOfIssuer"))
    industry_group = _first_text(root, ("industryGroupType",))
    offering = _offering_row(
        issuer_cik=issuer_cik,
        issuer_name=issuer_name,
        accession_number=accession_number
        or _first_text(root, ("accessionNumber", "accession-number")),
        filing_date=filing_date,
        first_sale_date=_parse_date(
            _first_text(root, ("dateOfFirstSale", "dateOfFirstSale/value", "value"))
        ),
        industry_group=industry_group,
        offering_amount=_parse_amount(
            _first_text(root, ("totalOfferingAmount", "totalOfferingAmount/value"))
        ),
        sold_amount=_parse_amount(
            _first_text(root, ("totalAmountSold", "totalAmountSold/value"))
        ),
        remaining_amount=_parse_amount(
            _first_text(root, ("totalRemaining", "totalRemaining/value"))
        ),
        investor_count=_parse_int(
            _first_text(root, ("totalNumberAlreadyInvested",))
        ),
        is_private_fund=_is_private_fund(industry_group),
    )
    return NormalizedFormD(
        offering=offering,
        people=_xml_related_people(root, offering),
    )


def _normalize_form_d_text(
    text: str,
    *,
    accession_number: str | None,
    filing_date: date | None,
) -> NormalizedFormD:
    """Normalize one plain-text Form D document."""
    industry_group = _text_field(text, ("INDUSTRY GROUP", "INDUSTRY GROUP TYPE"))
    offering = _offering_row(
        issuer_cik=_normalize_cik(_text_field(text, ("ISSUER CIK", "CIK"))),
        issuer_name=_text_field(
            text,
            (
                "ENTITY NAME",
                "ISSUER NAME",
                "OFFERING NAME",
                "FUND NAME",
                "NAME OF ISSUER",
            ),
        ),
        accession_number=accession_number
        or _text_field(text, ("ACCESSION NUMBER", "ACCESSION NO")),
        filing_date=filing_date,
        first_sale_date=_parse_date(_text_field(text, ("FIRST SALE DATE",))),
        industry_group=industry_group,
        offering_amount=_parse_amount(
            _text_field(text, ("TOTAL OFFERING AMOUNT", "OFFERING AMOUNT"))
        ),
        sold_amount=_parse_amount(
            _text_field(text, ("TOTAL AMOUNT SOLD", "AMOUNT SOLD", "SOLD AMOUNT"))
        ),
        remaining_amount=_parse_amount(
            _text_field(text, ("TOTAL REMAINING", "REMAINING AMOUNT"))
        ),
        investor_count=_parse_int(
            _text_field(text, ("TOTAL NUMBER ALREADY INVESTED", "INVESTOR COUNT"))
        ),
        is_private_fund=_is_private_fund(industry_group),
    )
    return NormalizedFormD(
        offering=offering,
        people=_text_related_people(text, offering),
    )


def _offering_row(**values: Any) -> dict[str, Any]:
    """Return a stable Form D offering row."""
    return {
        "issuer_cik": values.get("issuer_cik"),
        "issuer_name": values.get("issuer_name"),
        "accession_number": values.get("accession_number"),
        "filing_date": values.get("filing_date"),
        "first_sale_date": values.get("first_sale_date"),
        "industry_group": values.get("industry_group"),
        "offering_amount": values.get("offering_amount"),
        "sold_amount": values.get("sold_amount"),
        "remaining_amount": values.get("remaining_amount"),
        "investor_count": values.get("investor_count"),
        "is_private_fund": values.get("is_private_fund"),
    }


def related_person_row(
    offering: dict[str, Any],
    *,
    person_name: str,
    relationship: str | None = None,
    address_city: str | None = None,
    address_state: str | None = None,
    address_country: str | None = None,
) -> dict[str, Any]:
    """Return a stable Form D related-person row."""
    return {
        "issuer_cik": offering.get("issuer_cik"),
        "issuer_name": offering.get("issuer_name"),
        "accession_number": offering.get("accession_number"),
        "filing_date": offering.get("filing_date"),
        "person_name": person_name,
        "relationship": relationship,
        "address_city": address_city,
        "address_state": address_state,
        "address_country": address_country,
    }


def _xml_related_people(
    root: Element,
    offering: dict[str, Any],
) -> list[dict[str, Any]]:
    """Normalize Form D related people from XML."""
    people: list[dict[str, Any]] = []
    for element in root.iter():
        if _local_name(element.tag) != "relatedPersonInfo":
            continue
        name_parts = [
            _first_text(element, ("firstName",)),
            _first_text(element, ("middleName",)),
            _first_text(element, ("lastName",)),
            _first_text(element, ("suffix",)),
        ]
        name = " ".join(part for part in name_parts if part)
        if not name:
            name = _first_text(element, ("relatedPersonName", "personName")) or ""
        name = _clean_text(name)
        if not name:
            continue
        people.append(
            related_person_row(
                offering,
                person_name=name,
                relationship=_first_text(
                    element,
                    (
                        "relationship",
                        "relationshipClarification",
                        "relatedPersonRelationshipList",
                    ),
                ),
                address_city=_first_text(element, ("relatedPersonCity", "city")),
                address_state=_first_text(
                    element,
                    ("relatedPersonStateOrCountry", "stateOrCountry", "state"),
                ),
                address_country=_first_text(
                    element,
                    (
                        "relatedPersonStateOrCountryDescription",
                        "stateOrCountryDescription",
                        "country",
                    ),
                ),
            )
        )
    return people


def _text_related_people(
    text: str,
    offering: dict[str, Any],
) -> list[dict[str, Any]]:
    """Normalize Form D related people from text."""
    people: list[dict[str, Any]] = []
    pattern = re.compile(
        r"^\s*RELATED PERSON\s*:\s*(?P<name>.+?)(?:\s+-\s+(?P<role>.+))?\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    for match in pattern.finditer(text):
        name = _clean_text(match.group("name"))
        if not name:
            continue
        people.append(
            related_person_row(
                offering,
                person_name=name,
                relationship=_clean_text(match.group("role")),
            )
        )
    return people


def _filter_by_issuer(
    records: list[dict[str, Any]],
    issuer: str | None,
) -> list[dict[str, Any]]:
    """Apply issuer-name filtering."""
    if not issuer:
        return records
    needle = issuer.casefold()
    return [
        record
        for record in records
        if needle in str(record.get("issuer_name") or "").casefold()
    ]


def _looks_like_xml(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith("<") or stripped.startswith("<?xml")


def _first_text(root: Element, names: tuple[str, ...]) -> str | None:
    for name in names:
        parts = tuple(part for part in name.split("/") if part)
        for element in root.iter():
            if _local_name(element.tag) != parts[0]:
                continue
            value = (
                _descendant_text(element, parts[1:])
                if len(parts) > 1
                else element.text
            )
            cleaned = _clean_text(value)
            if cleaned:
                return cleaned
    return None


def _descendant_text(element: Element, path: tuple[str, ...]) -> str | None:
    current = element
    for part in path:
        match = next(
            (
                child
                for child in current
                if isinstance(child.tag, str) and _local_name(child.tag) == part
            ),
            None,
        )
        if match is None:
            return None
        current = match
    return current.text


def _text_field(text: str, labels: tuple[str, ...]) -> str | None:
    for label in labels:
        pattern = re.compile(
            rf"^\s*{re.escape(label)}\s*:\s*(?P<value>.+?)\s*$",
            re.IGNORECASE | re.MULTILINE,
        )
        match = pattern.search(text)
        if match:
            return _clean_text(match.group("value"))
    return None


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    match = re.search(r"\d{4}-\d{2}-\d{2}", value)
    if match:
        return date.fromisoformat(match.group(0))
    match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", value)
    if match:
        month, day, year = match.groups()
        return date(int(year), int(month), int(day))
    return None


def _parse_amount(value: str | None) -> int | None:
    if not value:
        return None
    if value.strip().lower() in {"indefinite", "not applicable", "n/a", "na"}:
        return None
    cleaned = re.sub(r"[^0-9.]", "", value)
    if not cleaned:
        return None
    try:
        return int(Decimal(cleaned))
    except InvalidOperation:
        return None


def _parse_int(value: str | None) -> int | None:
    amount = _parse_amount(value)
    return int(amount) if amount is not None else None


def _normalize_cik(value: str | None) -> str | None:
    if not value:
        return None
    digits = "".join(character for character in str(value) if character.isdigit())
    return digits.zfill(10) if digits else str(value).strip()


def _is_private_fund(industry_group: str | None) -> bool | None:
    if not industry_group:
        return None
    value = industry_group.casefold()
    return "pooled investment fund" in value or "private fund" in value


def _local_name(tag: Any) -> str:
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1]


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).split())
    return text or None
