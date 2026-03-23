"""US Congress Router."""

# pylint: disable=import-outside-toplevel,unused-argument,too-many-positional-arguments

from typing import Any

from fastapi.exceptions import HTTPException
from openbb_congress_gov.utils.constants import (
    COMMITTEES,
    SUBCOMMITTEES,
    chamber_options,
)
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

NO_SUBCOMMITTEES = [{"label": "None (Parent Committee)", "value": ""}]
router = Router(prefix="", description="Data connector to Congress.gov API.")
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
        APIEx(
            description="Get all bills of type 's' (Senate) for the 118th Congress.",
            parameters={
                "bill_type": "s",
                "congress": 118,
                "limit": 0,
                "provider": "congress_gov",
            },
        ),
    ],
)
async def bills(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get and filter lists of Congressional Bills."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


# pylint: disable=W0212
@router.command(
    methods=["GET"],
    examples=[
        APIEx(
            parameters={
                "provider": "congress_gov",
                "bill_url": "https://api.congress.gov/v3/bill/119/s/1947?",
            },
        ),
        APIEx(
            parameters={
                "provider": "congress_gov",
                "bill_url": "119/s/1947",
            },
        ),
    ],
    openapi_extra={
        "widget_config": {
            "name": "Congressional Bill Viewer",
            "description": "View current and historical U.S. Congressional Bills.",
            "category": "Government",
            "subCategory": "Congress",
            "type": "multi_file_viewer",
            "widgetId": "uscongress_bill_text_congress_gov_obb",
            "endpoint": f"{api_prefix}/uscongress/bill_text",
            "params": [
                {
                    "paramName": "urls",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix}/uscongress/bill_text_urls",
                    "optionsParams": {
                        "bill_url": "$bill_url",
                        "is_workspace": True,
                    },
                    "show": False,
                    "multiSelect": True,
                    "roles": ["fileSelector"],
                },
                {
                    "paramName": "is_workspace",
                    "value": True,
                    "show": False,
                },
                {
                    "label": "Bill URL",
                    "description": "Enter a base URL of a bill (e.g., 'https://api.congress.gov/v3/bill/119/s/1947?format=json')."
                    + " Alternatively, you can enter a bill number (e.g., '119/s/1947')."
                    + " Create a group on the 'Bill URL' field of the 'Congressional Bills' widget"
                    + " and click on the cell to view the available documents.",
                    "show": True,
                    "paramName": "bill_url",
                    "value": "119/hr/1",
                },
            ],
            "refetchInterval": False,
        }
    },
)
async def bill_text_urls(
    bill_url: str,
    provider: str = "congress_gov",
    is_workspace: bool = False,
) -> list:
    """Get document choices for a specific bill.

    This function is used by the Congressional Bills Viewer widget, in OpenBB Workspace,
    to populate PDF document choices for the selected bill.

    When 'is_workspace' is False (default), it returns a list of the available text versions
    of the specified bill and their download links for the different formats.

    Parameters
    ----------
    bill_url : str
        The base URL of the bill (e.g., "https://api.congress.gov/v3/bill/119/s/1947?format=json").
        This can also be a shortened version like "119/s/1947".
    provider : str
        The provider name, always "congress_gov". This is a dummy parameter.
    is_workspace : bool
        Whether the request is coming from the OpenBB Workspace.
        This alters the output format to conform to the Workspace's expectations.

    Returns
    -------
    list[dict]
        Returns a list of dictionaries with 'label' and 'value' keys, when `is_workspace` is True.
        Otherwise, returns the 'text' object from the Congress.gov API response.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_congress_gov.utils.helpers import get_bill_text_choices

    if not bill_url and is_workspace is True:
        return [
            {
                "label": "Enter a valid bill URL to view available documents.",
                "value": "",
            }
        ]

    if not bill_url:
        raise HTTPException(
            status_code=500,
            detail="Bill URL is required. Please provide a valid bill URL or number.",
        )

    if (bill_url.startswith("/") and bill_url[1].isdigit()) or bill_url[0].isdigit():
        # If the bill_url is a number, assume it is a congress number and append the base URL
        base_url = "https://api.congress.gov/v3/bill"
        bill_url = (
            base_url + bill_url
            if bill_url.startswith("/")
            else (base_url + "/" + bill_url if bill_url[0].isdigit() else bill_url)
        ) + "?format=json"

    return await get_bill_text_choices(bill_url=bill_url, is_workspace=is_workspace)


@router.command(
    model="CongressBillInfo",
    examples=[
        APIEx(
            parameters={
                "provider": "congress_gov",
                "bill_url": "https://api.congress.gov/v3/bill/119/s/1947?",
            }
        ),
        APIEx(
            description="The bill URL can be shortened to just the bill number (e.g., '119/s/1947').",
            parameters={
                "bill_url": "119/s/1947",
                "provider": "congress_gov",
            },
        ),
    ],
)
async def bill_info(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get summary, status, and other metadata for a specific bill.

    Enter the URL of the bill as: https://api.congress.gov/v3/bill/119/hr/131?

    URLs for bills can be found from the `uscongress.bills` endpoint.

    The raw JSON response from the API will be returned along with a formatted
    text version of the key information from the raw response.

    In OpenBB Workspace, this command returns as a Markdown widget.
    """
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CongressBillText",
    response_model=list,
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "provider": "congress_gov",
                "urls": ["https://www.congress.gov/119/bills/hr1/BILLS-119hr1eh.pdf"],
            }
        ),
    ],
    openapi_extra={
        "widget_config": {
            "exclude": True,
        }
    },
)
async def bill_text(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Download the content of bill(s) from a Congress.gov file.

    Note: This endpoint returns only the results array of the OBBject.

    Enter a list of URLs to download the bill text.

    For the API, the body of the request will look like this:

    ```json
    {
        "urls": [
            "https://www.congress.gov/119/bills/hr1/BILLS-119hr1eh.pdf"
        ]
    }
    ```

    In OpenBB Workspace, this command returns as a multi-file viewer widget.
    """
    return (await OBBject.from_query(OpenBBQuery(**locals()))).results  # type: ignore[return-value]


@router.command(
    model="CongressAmendments",
    examples=[
        APIEx(parameters={"provider": "congress_gov"}),
        APIEx(
            parameters={
                "congress": 119,
                "amendment_type": "hamdt",
                "provider": "congress_gov",
            }
        ),
    ],
)
async def amendments(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get and filter lists of Congressional Amendments."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    methods=["GET"],
    examples=[
        APIEx(
            parameters={
                "provider": "congress_gov",
                "amendment_url": "119/hamdt/2",
            },
        ),
    ],
    openapi_extra={
        "widget_config": {
            "name": "Congressional Amendment Viewer",
            "description": "View text documents for a U.S. Congressional Amendment.",
            "category": "Government",
            "subCategory": "Congress",
            "type": "multi_file_viewer",
            "widgetId": "uscongress_amendment_text_congress_gov_obb",
            "endpoint": f"{api_prefix}/uscongress/amendment_text",
            "params": [
                {
                    "paramName": "urls",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix}/uscongress/amendment_text_urls",
                    "optionsParams": {
                        "amendment_url": "$amendment_url",
                        "is_workspace": True,
                    },
                    "show": False,
                    "multiSelect": True,
                    "roles": ["fileSelector"],
                },
                {
                    "paramName": "is_workspace",
                    "value": True,
                    "show": False,
                },
                {
                    "label": "Amendment URL",
                    "description": "Enter an amendment shorthand (e.g., '119/hamdt/2')."
                    + " Create a group on the 'amendment_url' field of the 'Congressional Amendments' widget"
                    + " and click on the cell to view the available documents.",
                    "show": True,
                    "paramName": "amendment_url",
                    "value": "119/hamdt/2",
                },
            ],
            "refetchInterval": False,
        }
    },
)
async def amendment_text_urls(
    amendment_url: str,
    provider: str = "congress_gov",
    is_workspace: bool = False,
) -> list:
    """Get document choices for a specific amendment.

    This function is used by the Congressional Amendment Viewer widget, in OpenBB Workspace,
    to populate document choices for the selected amendment.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_congress_gov.utils.helpers import get_amendment_text_choices

    if not amendment_url and is_workspace is True:
        return [
            {
                "label": "Enter a valid amendment URL to view available documents.",
                "value": "",
            }
        ]

    if not amendment_url:
        raise HTTPException(
            status_code=500,
            detail="Amendment URL is required. Please provide a valid amendment shorthand (e.g., '119/hamdt/2').",
        )

    return await get_amendment_text_choices(
        amendment_url=amendment_url, is_workspace=is_workspace
    )


@router.command(
    model="CongressAmendmentInfo",
    examples=[
        APIEx(
            parameters={
                "provider": "congress_gov",
                "amendment_url": "119/hamdt/2",
            }
        ),
    ],
)
async def amendment_info(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get details for a specific amendment.

    Enter the amendment identifier as: {congress}/{type}/{number} (e.g., '119/hamdt/2').

    In OpenBB Workspace, this command returns as a Markdown widget.
    """
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CongressAmendmentText",
    response_model=list,
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "provider": "congress_gov",
                "urls": ["https://www.congress.gov/119/bills/hamdt2/HAMDT2.pdf"],
            }
        ),
    ],
    openapi_extra={
        "widget_config": {
            "exclude": True,
        }
    },
)
async def amendment_text(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Download amendment document(s) from Congress.gov.

    Note: This endpoint returns only the results array of the OBBject.
    """
    return (await OBBject.from_query(OpenBBQuery(**locals()))).results  # type: ignore[return-value]


@router.command(
    model="CongressCommitteeInfo",
    examples=[
        APIEx(
            parameters={
                "chamber": "senate",
                "committee": "ssaf00",
                "provider": "congress_gov",
            }
        ),
        APIEx(
            parameters={
                "chamber": "house",
                "committee": "hsju00",
                "provider": "congress_gov",
            }
        ),
        APIEx(
            description="Get info for a subcommittee.",
            parameters={
                "chamber": "senate",
                "committee": "ssga00",
                "subcommittee": "ssga22",
                "provider": "congress_gov",
            },
        ),
    ],
)
async def committee_info(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get metadata and membership for a single U.S. Congressional Committee.

    Fetches the committee detail (type, website, subcommittees, activity counts)
    and current member roster with party affiliations and leadership titles.

    Select a chamber, committee, and optional subcommittee to view details.
    """
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CongressCommitteeDocuments",
    openapi_extra={"widget_config": {"exclude": True}},
    examples=[
        APIEx(
            description="Get reports from the Senate Agriculture Committee.",
            parameters={
                "chamber": "senate",
                "committee": "ssaf00",
                "doc_type": "report",
                "provider": "congress_gov",
            },
        ),
        APIEx(
            description="Get hearings from the House Judiciary Committee for the 119th Congress.",
            parameters={
                "chamber": "house",
                "committee": "hsju00",
                "doc_type": "meeting",
                "congress": 119,
                "provider": "congress_gov",
            },
        ),
    ],
)
async def committee_documents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get documents (reports, hearings, prints, meetings) produced by a single Congressional Committee.

    Select a chamber, committee, and optional subcommittee.
    """
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)
async def committee_choices(
    chamber: str | None = None,
    congress: int | None = None,
    committee: str | None = None,
    subcommittees: bool = False,
    provider: str = "congress_gov",
    is_workspace: bool = False,
) -> list:
    """Get committee or subcommittee choices for cascading dropdowns."""
    if not chamber:
        return chamber_options

    chamber = chamber.lower()

    if subcommittees and not committee:
        return [{"label": "Select a committee first.", "value": ""}]

    if subcommittees and committee:
        return SUBCOMMITTEES.get(f"{chamber}/{committee}", NO_SUBCOMMITTEES)

    if chamber not in ("senate", "house", "joint"):
        return [{"label": "Invalid chamber.", "value": ""}]

    return COMMITTEES.get(chamber, [{"label": "No committees found.", "value": ""}])


@router.command(
    methods=["GET"],
    examples=[
        APIEx(
            parameters={
                "provider": "congress_gov",
                "chamber": "senate",
                "committee": "ssaf00",
            },
        ),
    ],
    openapi_extra={
        "widget_config": {
            "name": "Committee Document Viewer",
            "description": "Browse and view documents for a U.S. Congressional Committee.",
            "category": "Government",
            "subCategory": "Congress",
            "type": "multi_file_viewer",
            "widgetId": "uscongress_committee_document_viewer_congress_gov_obb",
            "endpoint": f"{api_prefix}/uscongress/bill_text",
            "params": [
                {
                    "paramName": "urls",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix}/uscongress/committee_document_urls",
                    "optionsParams": {
                        "chamber": "$chamber",
                        "committee": "$committee",
                        "subcommittee": "$subcommittee",
                        "doc_type": "$doc_type",
                        "congress": "$congress",
                        "is_workspace": True,
                    },
                    "show": False,
                    "multiSelect": True,
                    "roles": ["fileSelector"],
                },
                {
                    "paramName": "is_workspace",
                    "value": True,
                    "show": False,
                },
                {
                    "label": "Congress",
                    "description": "Congress number (e.g. 119).",
                    "show": True,
                    "paramName": "congress",
                    "value": 119,
                    "type": "number",
                },
                {
                    "label": "Chamber",
                    "show": True,
                    "paramName": "chamber",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix}/uscongress/committee_choices",
                    "optionsParams": {"congress": "$congress", "is_workspace": True},
                },
                {
                    "label": "Committee",
                    "show": True,
                    "paramName": "committee",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix}/uscongress/committee_choices",
                    "optionsParams": {
                        "chamber": "$chamber",
                        "congress": "$congress",
                        "is_workspace": True,
                    },
                    "style": {"popupWidth": 750},
                },
                {
                    "label": "Subcommittee",
                    "show": True,
                    "paramName": "subcommittee",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix}/uscongress/committee_choices",
                    "optionsParams": {
                        "chamber": "$chamber",
                        "committee": "$committee",
                        "subcommittees": True,
                        "is_workspace": True,
                    },
                    "style": {"popupWidth": 750},
                },
                {
                    "label": "Document Type",
                    "description": "Type of committee document to browse.",
                    "show": True,
                    "paramName": "doc_type",
                    "value": "meeting",
                    "options": [
                        {"label": "Reports", "value": "report"},
                        {"label": "Meetings & Hearings", "value": "meeting"},
                        {"label": "Publications & Prints", "value": "publication"},
                        {"label": "Legislation", "value": "legislation"},
                    ],
                },
            ],
            "refetchInterval": False,
        }
    },
)
async def committee_document_urls(
    chamber: str,
    committee: str,
    subcommittee: str | None = None,
    doc_type: str = "all",
    congress: int | None = None,
    provider: str = "congress_gov",
    is_workspace: bool = False,
    use_cache: bool = True,
) -> list:
    """Get document choices for a Congressional Committee.

    This endpoint populates the Committee Document Viewer file selector
    with the committee's available documents by type.
    """
    # pylint: disable=import-outside-toplevel
    import datetime
    import re as _re

    from openbb_congress_gov.utils.committees import fetch_committee_documents
    from openbb_congress_gov.utils.helpers import (
        check_api_key,
        year_to_congress,
    )

    if not committee and is_workspace is True:
        return [
            {
                "label": "Select a committee to view available documents.",
                "value": "",
            }
        ]

    if not committee:
        raise HTTPException(
            status_code=500,
            detail="Committee system code is required.",
        )

    api_key = check_api_key()
    system_code = (subcommittee or committee).lower()

    if congress is None:
        congress = year_to_congress(datetime.date.today().year)

    items = await fetch_committee_documents(
        chamber=chamber.lower(),
        system_code=system_code,
        congress=congress,
        doc_type=doc_type,
        api_key=api_key,
        use_cache=use_cache,
    )

    def _clean_label(text: str) -> str:
        text = _re.sub(r"\s*\[TEXT NOT AVAILABLE[^\]]*\]", "", text)
        text = _re.sub(r"\s*\[REFER TO[^\]]*\]", "", text)
        return text.strip()

    _date_re = _re.compile(r"^\[(\d{4}-\d{2}-\d{2})\]\s*")

    choices = []

    for item in items:
        citation = item.get("citation") or ""
        title = _clean_label(item.get("title") or "")
        short_cite = ""

        if citation:
            cite_m = _re.match(
                r"((?:S|H)\.\s*(?:Hrg|Rept|Rpt|Prt|Doc)\.\s*\d{2,3}-\d+(?:,\s*(?:Book|Part)\s*\d+)?)",
                citation,
            )
            if cite_m:
                short_cite = cite_m.group(1)

        date_m = _date_re.match(title)
        date_prefix = ""
        if date_m:
            date_prefix = f"[{date_m.group(1)}] "
            title = title[date_m.end() :]

        if short_cite and title:
            label = f"{date_prefix}{short_cite} — {title}"
        elif title:
            label = f"{date_prefix}{title}"
        elif citation:
            label = date_prefix + _re.sub(r"\s*\(.*?\)\s*$", "", citation).strip()
        else:
            label = date_prefix + item.get("doc_url", "Unknown")

        choices.append({"label": label, "value": item.get("doc_url", "")})

    choices.sort(key=lambda c: c["label"], reverse=True)

    if not choices:
        return [{"label": "No documents found.", "value": ""}]

    return choices


async def get_congress_gov_apps_json() -> list[dict[str, Any]]:
    """Get the IMF apps.json file.

    This endpoint serves the apps.json file containing OpenBB Workspace app configurations
    related to IMF data and utilities.

    It is automatically merged with any existing apps.json files in the Workspace and API.

    Returns
    -------
    list[dict[str, Any]]
        A list of OpenBB Workspace app configurations.
    """
    # pylint: disable=import-outside-toplevel
    import json
    from pathlib import Path

    apps_file = Path(__file__).parent / "apps.json"

    try:
        with apps_file.open("r", encoding="utf-8") as f:
            apps_json = json.load(f)
            return apps_json
    except Exception:
        return []


router._api_router.add_api_route(
    path="/apps.json",
    endpoint=get_congress_gov_apps_json,
    methods=["GET"],
    include_in_schema=False,
)
