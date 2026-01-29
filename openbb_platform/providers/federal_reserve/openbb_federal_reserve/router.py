"""OpenBB Federal Reserve Router Module."""

from typing import Annotated

from fastapi import APIRouter, Body
from openbb_core.app.model.abstract.error import OpenBBError

router = APIRouter()


@router.get("/apps.json", include_in_schema=False)
async def get_apps_json():
    """Get the apps.json for the Federal Reserve provider."""
    # pylint: disable=import-outside-toplevel
    import json
    from pathlib import Path

    apps_json_path = Path(__file__).parent / "assets" / "apps.json"
    with open(apps_json_path, encoding="utf-8") as file:
        apps_data = json.load(file)
    return apps_data


@router.post(
    "/fomc_documents_download",
    include_in_schema=False,
    openapi_extra={},
)
async def fomc_documents_download(params: Annotated[dict, Body()]) -> list:
    """Download FOMC documents from the Federal Reserve's website.

    PDFs are base64 encoded under the `content` key in the response.

    Parameters
    ----------
    params : dict
        A dictionary with a key "url" containing a list of URLs to download.

    Returns
    -------
    list
        A list of dictionaries, each containing keys `filename`, `content`, and `data_format`.
    """
    # pylint: disable=import-outside-toplevel
    import base64  # noqa
    from io import BytesIO
    from urllib.parse import urlparse
    from openbb_core.provider.utils.helpers import make_request

    urls = params.get("url", [])
    results: list = []

    for url in urls:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname or ""

        if parsed_url.scheme != "https" or hostname not in {
            "www.federalreserve.gov",
            "federalreserve.gov",
        }:
            raise OpenBBError(
                "Invalid URL provided for download. Must be from federalreserve.gov -> "
                + url
            )

        is_pdf = url.lower().endswith(".pdf")

        if (
            not is_pdf
            and not url.lower().endswith(".htm")
            and not url.lower().endswith(".html")
        ):
            raise OpenBBError(
                "Unsupported document format. File must be PDF or HTM type -> " + url
            )

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
                        "data_type": "pdf" if is_pdf else "markdown",
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


@router.get("/fomc_documents_choices", include_in_schema=False)
async def fomc_documents_choices(
    year: int | None = None, document_type: str | None = None
) -> list:
    """Get the available choices for FOMC document types.

    Returns
    -------
    list
        A list of available document choices with URLs for download.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_federal_reserve.utils.fomc_documents import (
        get_fomc_documents_by_year,
    )

    docs = get_fomc_documents_by_year(year, document_type, True)
    choices_list: list = []

    for doc in docs:
        title = (
            doc.get("doc_type", "").replace("_", " ").title()
            + " - "
            + doc.get("date", "")
        )
        value = doc.get("url", "")
        if title and value:
            choices_list.append(
                {
                    "label": title,
                    "value": value,
                }
            )

    return choices_list
