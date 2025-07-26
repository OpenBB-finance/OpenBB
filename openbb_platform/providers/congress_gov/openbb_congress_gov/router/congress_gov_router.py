# pylint: disable=import-outside-toplevel,unused-argument
"""US Congress Router."""

from typing import Annotated, Optional

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OpenBBQuery
from openbb_core.app.router import Router
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data

router = Router(prefix="", description="U.S. Congress API.")

api_prefix = SystemService().system_settings.api_settings.prefix


@router.command(
    model="CongressBills",
    examples=[
        APIEx(parameters={"provider": "congress_gov"}),
        APIEx(
            parameters={
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
                "provider": "congress_gov",
            }
        ),
    ],
)
async def bills(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Congress Bills Data."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    methods=["POST"],
    openapi_extra={
        "widget_config": {
            "exclude": True,
        }
    },
)
async def download_bill_text(params: Data) -> list:
    """Downloads a bill in PDF format.

    This endpoint is used by the Congressional Bills Viewer widget to download
    the selected bill in PDF format. It accepts a list of URLs to download and
    returns a a list of dictionaries with base64-encoded PDF content.

    Parameters
    ----------
    params : Data
        A pydantic base model with a single field `document_url` which is a list of URLs to download.
        The function expects the following structure in the body of the request:
            {
                "url": list,  # List of URLs to download
            }

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

    urls = getattr(params, "document_url", [])
    results: list = []

    for url in urls:
        if "congress.gov" not in url:
            results.append(
                {
                    "error_type": "invalid_url",
                    "content": f"Invalid URL: {url}. Must be a valid Congress.gov API URL.",
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


# pylint: disable=W0212
@router._api_router.get(
    "/bills/bill_text_choices",
    openapi_extra={
        "widget_config": {
            "name": "Congressional Bills Viewer",
            "description": "View current and historical U.S. Congressional Bills.",
            "category": "Government",
            "type": "multi_file_viewer",
            "searchCategory": "Congress",
            "widgetId": "uscongress_download_bill_text_congress_gov_obb",
            "endpoint": f"{api_prefix}/uscongress/download_bill_text",
            "params": [
                {
                    "paramName": "document_url",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix}/uscongress/bills/bill_text_choices",
                    "optionsParams": {
                        "bill_url": "$bill_url",
                    },
                    "show": False,
                    "multiSelect": True,
                    "roles": ["fileSelector"],
                },
                {
                    "label": "Bill URL",
                    "description": "Enter a base URL of a bill (e.g., 'https://api.congress.gov/v3/bill/119/s/1947?format=json')."
                    + " Create a group on the 'Bill URL' field of the 'Congressional Bills' widget"
                    + " and click on the cell to view the available documents.",
                    "show": True,
                    "paramName": "bill_url",
                    "row": 1,
                },
            ],
        }
    },
)
async def get_bill_text_links(bill_url: str, provider: str = "congress_gov") -> list:
    """Helper function to populate document choices for a specific bill.

    This function is not intended to be used directly and is used by the Congressional Bills Viewer widget,
    in OpenBB Workspace, to populate the document choices
    for the selected bill.

    Parameters
    ----------
    bill_url : str
        The base URL of the bill (e.g., "https://api.congress.gov/v3/bill/119/s/1947?format=json").
    provider : str
        The provider name, always "congress_gov". This is a dummy parameter.

    Returns
    -------
    str
        The text of the specified bill.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_congress_gov.utils.helpers import get_bill_text_choices

    if not bill_url:
        return [
            {
                "label": "Enter a valid bill URL to view available documents.",
                "value": "",
            }
        ]

    return await get_bill_text_choices(bill_url=bill_url)
