"""SEC investment adviser regulatory documents."""

from __future__ import annotations

from datetime import date
from json import JSONDecodeError, loads
from typing import Literal
from urllib.parse import urlencode

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_sec.utils.adviser_info import (
    clean_date,
    clean_text,
    iapd_sources,
    request_iapd,
    required_text,
    string_dict,
)

ADV_REPORT_URL = "https://reports.adviserinfo.sec.gov/reports/ADV"
BROCHURE_URL = (
    "https://files.adviserinfo.sec.gov/IAPD/Content/Common/crd_iapd_Brochure.aspx"
)


class SecAdviserDocumentsQueryParams(QueryParams):
    """SEC investment adviser document query."""

    crd: str = Field(
        description="Central Registration Depository (CRD) number.",
        pattern=r"^\d+$",
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use cached SEC responses.",
    )


class SecAdviserDocumentsData(Data):
    """SEC investment adviser regulatory document."""

    crd: str = Field(description="Central Registration Depository (CRD) number.")
    firm_name: str = Field(description="Investment adviser firm name.")
    document_type: Literal["Form ADV", "Brochure"] = Field(
        description="Regulatory document type."
    )
    document_id: str | None = Field(
        default=None,
        description="Document identifier reported by IAPD.",
    )
    title: str = Field(description="Document title.")
    filing_date: date | None = Field(
        default=None,
        description="Date the document was filed or submitted.",
    )
    url: str = Field(description="Public adviserinfo.sec.gov document URL.")


class SecAdviserDocumentsFetcher(
    Fetcher[SecAdviserDocumentsQueryParams, list[SecAdviserDocumentsData]]
):
    """SEC investment adviser regulatory documents fetcher."""

    @staticmethod
    def transform_query(params: dict[str, object]) -> SecAdviserDocumentsQueryParams:
        """Transform query parameters."""
        return SecAdviserDocumentsQueryParams.model_validate(params)

    @staticmethod
    async def aextract_data(
        query: SecAdviserDocumentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: object,
    ) -> list[dict[str, object]]:
        """Return one row per available IAPD regulatory document."""
        firm = await _get_adviser_firm(query.crd, query.use_cache)
        records = _document_records(firm)
        if not records:
            raise EmptyDataError(
                f"No regulatory documents were found for adviser CRD {query.crd}."
            )
        return records

    @staticmethod
    def transform_data(
        query: SecAdviserDocumentsQueryParams,
        data: list[dict[str, object]],
        **kwargs: object,
    ) -> list[SecAdviserDocumentsData]:
        """Transform raw records to the public model."""
        return [SecAdviserDocumentsData.model_validate(record) for record in data]


async def _get_adviser_firm(crd: str, use_cache: bool) -> dict[str, object]:
    """Fetch and parse one IAPD firm profile by CRD."""
    payload = await request_iapd(
        f"firm/{crd}",
        {},
        use_cache,
    )
    sources = iapd_sources(payload, "firm profile")
    if not sources:
        raise EmptyDataError(f"No investment adviser firm was found for CRD {crd}.")

    for source in sources:
        content = source.get("iacontent")
        if not isinstance(content, str):
            raise OpenBBError(
                "Invalid IAPD firm profile response: iacontent must be JSON text."
            )
        try:
            firm = string_dict(
                loads(content),
                "Invalid IAPD firm profile response: iacontent must be an object.",
            )
        except JSONDecodeError as exc:
            raise OpenBBError(
                "Invalid IAPD firm profile response: iacontent contains invalid JSON."
            ) from exc
        basic = string_dict(
            firm.get("basicInformation"),
            "Invalid IAPD firm profile response: missing basic information.",
        )
        if clean_text(basic.get("firmId")) == crd:
            return firm
    raise EmptyDataError(f"No investment adviser firm was found for CRD {crd}.")


def _document_records(firm: dict[str, object]) -> list[dict[str, object]]:
    """Build flat document rows from structured IAPD metadata."""
    basic = _profile_section(firm, "basicInformation")
    crd = required_text(basic.get("firmId"), "firm CRD", "firm profile")
    name = required_text(basic.get("firmName"), "firm name", "firm profile")
    records: list[dict[str, object]] = []

    if _yes_no(basic.get("hasPdf")) is True:
        records.append(
            {
                "crd": crd,
                "firm_name": name,
                "document_type": "Form ADV",
                "document_id": None,
                "title": "Form ADV",
                "filing_date": clean_date(basic.get("advFilingDate"), "%m/%d/%Y"),
                "url": f"{ADV_REPORT_URL}/{crd}/PDF/{crd}.pdf",
            }
        )

    brochures = _profile_section(firm, "brochures", required=False)
    for brochure in _object_list(brochures.get("brochuredetails"), "brochuredetails"):
        version_id = required_text(
            brochure.get("brochureVersionID"),
            "brochure version ID",
            "firm profile",
        )
        records.append(
            {
                "crd": crd,
                "firm_name": name,
                "document_type": "Brochure",
                "document_id": version_id,
                "title": required_text(
                    brochure.get("brochureName"),
                    "brochure name",
                    "firm profile",
                ),
                "filing_date": clean_date(brochure.get("dateSubmitted"), "%m/%d/%Y"),
                "url": f"{BROCHURE_URL}?{urlencode({'BRCHR_VRSN_ID': version_id})}",
            }
        )

    return records


def _profile_section(
    firm: dict[str, object],
    name: str,
    *,
    required: bool = True,
) -> dict[str, object]:
    """Return a validated profile object section."""
    value = firm.get(name)
    if value is None and not required:
        return {}
    return string_dict(
        value,
        f"Invalid IAPD firm profile response: {name} must be an object.",
    )


def _object_list(value: object, field: str) -> list[dict[str, object]]:
    """Validate an optional list of profile objects."""
    if value is None:
        return []
    if not isinstance(value, list):
        raise OpenBBError(
            f"Invalid IAPD firm profile response: {field} must be a list."
        )
    return [
        string_dict(
            item,
            f"Invalid IAPD firm profile response: {field} entries must be objects.",
        )
        for item in value
    ]


def _yes_no(value: object) -> bool | None:
    """Normalize an optional IAPD Y/N flag."""
    cleaned = clean_text(value)
    if cleaned is None:
        return None
    if cleaned == "Y":
        return True
    if cleaned == "N":
        return False
    raise OpenBBError("Invalid IAPD firm profile response: expected a Y/N flag.")
