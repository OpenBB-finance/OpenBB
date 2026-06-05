"""Congress.gov helpers."""

from fastapi.exceptions import HTTPException
from openbb_core.app.model.abstract.singleton import SingletonMeta


# pylint: disable=R0903
class BillsState(metaclass=SingletonMeta):
    """Singleton class to manage application cache."""

    def __init__(self):
        """Initialize the BillsState."""
        if not hasattr(self, "bulk"):
            self.bulk = {}


def year_to_congress(year: int) -> int:
    """
    Map a year (1935-present) to the corresponding U.S. Congress number.

    Raises ValueError if the year is before 1935.
    """
    if year < 1935:
        raise ValueError("Year must be 1935 or later.")
    # 74th Congress started in 1935
    congress_number = 74 + ((year - 1935) // 2)
    return congress_number


def download_bills(urls: list[str]) -> list:
    """Download a bill's text in PDF format.

    This helper is not intended to be used directly.

    OpenBB Workspace uses this, as a POST endpoint, to download
    the selected bill(s) in PDF format. Results are returned as base64-encoded PDF content.

    Parameters
    ----------
    urls: list[str]
        A list of URLs to download. Each URL must be a valid Congress.gov URL.

    Returns
    -------
    list
        A list of dictionaries containing the base64-encoded PDF content.
        The dictionaries have the following structure:
            [
                {
                    "content": str,  # Base64-encoded PDF content
                    "data_format": {
                        "data_type": "pdf",
                        "filename": str,  # The filename of the downloaded PDF
                    },
                },
                ...
            ]

        If an error occurs during the download, the dictionary will contain:
            [
                {
                    "error_type": str,  # Type of error (e.g., "download_error")
                    "content": str,  # Error content
                    "filename": str,  # The filename of the attempted download
                },
                ...
            ]
    """
    # pylint: disable=import-outside-toplevel
    import base64  # noqa
    from io import BytesIO
    from openbb_core.provider.utils.helpers import make_request

    results: list = []

    for url in urls:
        if "congress.gov" not in url and "govinfo.gov" not in url:
            results.append(
                {
                    "error_type": "invalid_url",
                    "content": f"Invalid URL: {url}. Must be a valid Congress.gov or GovInfo.gov URL.",
                    "filename": url.split("/")[-1],
                }
            )
            continue
        try:
            response = make_request(url)
            response.raise_for_status()
            pdf = (
                base64.b64encode(BytesIO(response.content).getvalue()).decode("utf-8")
                if isinstance(response.content, bytes)
                else response.content
            )
            results.append(
                {
                    "content": pdf,
                    "data_format": {
                        "data_type": "pdf",
                        "filename": url.split("/")[-1],
                    },
                }
            )
        except Exception as exc:  # pylint: disable=broad-except
            results.append(
                {
                    "error_type": "download_error",
                    "content": f"{exc.__class__.__name__}: {exc.args[0]}",
                    "filename": url.split("/")[-1],
                }
            )
            continue

    return results


async def get_bill_text_choices(bill_id: str, is_workspace: bool = False) -> list:
    """Fetch the direct download links for the available text versions of the specified bill.

    This function is used by the Congressional Bills Viewer widget,
    in OpenBB Workspace, to populate the document choices
    for the selected bill. When `is_workspace` is True,
    it returns a list of dictionaries with 'label' and 'value' keys.

    Text versions and their PDF/HTM/XML links are sourced from the cached
    GovInfo BILLSTATUS bulk record, so no Congress.gov API key is required.

    Parameters
    ----------
    bill_id : str
        The bill id (e.g. "119-hr-29", congress-billtype-number).

    Returns
    -------
    list[dict]
        List of dictionaries with the results.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_congress_gov.utils.bulk import (
        derive_text_formats,
        load_billstatus,
        parse_bill_ref,
    )

    congress, bill_type, number = parse_bill_ref(bill_id)
    records = await load_billstatus(congress, bill_type)
    record = next((r for r in records if r.get("number") == number), None)
    versions = record.get("textVersions", []) if record else []

    # Build one entry per text version, de-duplicated by PDF URL.
    seen_urls: set = set()
    formatted: list[dict] = []
    for version in versions:
        entry = derive_text_formats(version)
        if entry is None or entry["pdf"] in seen_urls:
            continue
        seen_urls.add(entry["pdf"])
        formatted.append(entry)

    if is_workspace is False:
        if not formatted:
            raise HTTPException(
                status_code=404,
                detail="No text available for this bill currently.",
            )
        return formatted

    if not formatted:
        return [
            {
                "label": "No text available for this bill currently.",
                "value": "",
            }
        ]

    results: list = []
    for entry in formatted:
        doc_name = entry["pdf"].split("/")[-1]
        version_date = entry["version_date"]
        label = (
            f"{entry['version_type']} - {version_date} - {doc_name}"
            if version_date
            else doc_name
        )
        results.append({"label": label, "value": entry["pdf"]})

    return results


def get_document_choices(package_id: str, is_workspace: bool = False) -> list:
    """Resolve a GovInfo package id to its document download links.

    Shared by the law, calendar, and mandated-report viewer widgets, which each
    group by a single ``package_id`` representing one document. The PDF/HTM/XML
    URLs are derived from the package id; no API key or network call is required.

    Parameters
    ----------
    package_id : str
        The GovInfo package id (e.g. "PLAW-119publ1", "CCAL-119hcal-2025-01-03").
    is_workspace : bool
        When True, returns ``[{label, value}]`` choices for the Workspace viewer.

    Returns
    -------
    list[dict]
        Document choices (workspace) or a single ``{package_id, pdf, htm, xml}`` dict.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_congress_gov.utils.bulk import package_urls

    if not package_id:
        if is_workspace is True:
            return [{"label": "Select a row to view the document.", "value": ""}]
        raise HTTPException(
            status_code=404,
            detail="A package_id is required to view a document.",
        )

    urls = package_urls(package_id)

    if is_workspace is True:
        return [{"label": f"{package_id}.pdf", "value": urls["pdf"]}]

    return [{"package_id": package_id, **urls}]


async def get_amendment_text_choices(
    amendment_id: str, is_workspace: bool = False
) -> list:
    """Resolve an amendment's Congressional Record documents via the link service.

    The amendment record is loaded from the cached GovInfo BILLSTATUS bulk data,
    then its House/Senate amendment is resolved to the Congressional Record
    document(s) through the GovInfo link service. No Congress.gov API key is
    required.

    Parameters
    ----------
    amendment_id : str
        The amendment id (e.g. "119-hamdt-2", congress-type-number).
    is_workspace : bool
        When True, returns {label, value} dicts suitable for workspace dropdowns.

    Returns
    -------
    list
        List of dictionaries with the available document formats.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_congress_gov.utils.bulk import (
        load_amendment_record,
        resolve_amendment_text,
    )

    record = await load_amendment_record(amendment_id)
    documents = await resolve_amendment_text(record)

    if is_workspace is False:
        if not documents:
            raise HTTPException(
                status_code=404,
                detail="No text available for this amendment currently.",
            )

        by_date: dict[str, dict] = {}
        for doc in documents:
            entry = by_date.setdefault(
                doc["date"],
                {"version_type": "Congressional Record", "version_date": doc["date"]},
            )
            entry[doc["format_key"]] = doc["url"]

        return list(by_date.values())

    # The Workspace multi-file viewer only renders PDFs, so offer just the PDF
    # documents (matching the bill, law, calendar, and report viewers).
    results: list = []
    for doc in documents:
        if doc["format_key"] != "pdf":
            continue
        filename = doc["url"].split("/")[-1]
        label = (
            f"Congressional Record - {doc['date']} - {filename}"
            if doc["date"]
            else f"Congressional Record - {filename}"
        )
        results.append({"label": label, "value": doc["url"]})

    if not results:
        return [
            {"label": "No text available for this amendment currently.", "value": ""}
        ]

    return results
