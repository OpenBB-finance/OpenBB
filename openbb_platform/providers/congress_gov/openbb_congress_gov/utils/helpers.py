"""Congress.gov helpers."""

from fastapi.exceptions import HTTPException
from openbb_core.app.model.abstract.singleton import SingletonMeta


class BillsState(metaclass=SingletonMeta):
    """Singleton class to manage application cache."""

    def __init__(self):
        """Initialize the BillsState."""
        if not hasattr(self, "bulk"):
            self.bulk = {}


def year_to_congress(year: int) -> int:
    """Map a year (1935-present) to the corresponding U.S. Congress number."""
    if year < 1935:
        raise ValueError("Year must be 1935 or later.")
    congress_number = 74 + ((year - 1935) // 2)
    return congress_number


def download_bills(urls: list[str]) -> list:
    """Download a bill's text in PDF format."""
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
        except Exception as exc:
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
    """Fetch the direct download links for the available text versions of the specified bill."""
    from openbb_congress_gov.utils import store
    from openbb_congress_gov.utils.bulk import (
        derive_text_formats,
        ensure_billstatus,
        parse_bill_ref,
    )

    congress, bill_type, number = parse_bill_ref(bill_id)
    await ensure_billstatus(congress, bill_type)
    record = store.get_bill(f"{congress}-{bill_type.lower()}-{number}")
    versions = record.get("textVersions", []) if record else []

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


def document_choices_from_records(records: list, is_workspace: bool = False) -> list:
    """Build viewer choices from a list of document records (package_id-based).

    Used as an intelligent fallback when no specific package is selected: each
    record's package id resolves to its content URLs, most-recent records first.
    """
    from openbb_congress_gov.utils.bulk import package_urls

    if is_workspace is True:
        choices = [
            {
                "label": f"{record.get('title') or record['package_id']}"
                + f" - {record['package_id']}.pdf",
                "value": record.get("pdf") or package_urls(record["package_id"])["pdf"],
            }
            for record in records
            if record.get("package_id")
        ]
        return choices or [{"label": "No documents available.", "value": ""}]

    return [
        {"package_id": record["package_id"], **package_urls(record["package_id"])}
        for record in records
        if record.get("package_id")
    ]


def get_document_choices(package_id: str, is_workspace: bool = False) -> list:
    """Resolve a GovInfo package id to its document download links."""
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
    """Resolve an amendment's Congressional Record documents via the link service."""
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
