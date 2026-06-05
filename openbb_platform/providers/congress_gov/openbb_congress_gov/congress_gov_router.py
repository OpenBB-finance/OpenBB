"""US Congress Router."""

# pylint: disable=import-outside-toplevel,unused-argument,too-many-positional-arguments

from typing import Any

from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
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

from openbb_congress_gov.utils.constants import (
    COMMITTEES,
    SUBCOMMITTEES,
    chamber_options,
)

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


@router.command(
    model="CongressLaws",
    examples=[
        APIEx(parameters={"provider": "congress_gov"}),
        APIEx(
            description="Get the 5 most recent public laws of the 118th Congress.",
            parameters={
                "congress": 118,
                "law_type": "public",
                "limit": 5,
                "provider": "congress_gov",
            },
        ),
    ],
)
async def laws(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get and filter lists of enacted Congressional Laws (public or private)."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CongressCalendars",
    examples=[
        APIEx(parameters={"chamber": "house", "provider": "congress_gov"}),
        APIEx(
            description="Get the most recent Senate calendar.",
            parameters={
                "chamber": "senate",
                "publishdate": "mostrecent",
                "provider": "congress_gov",
            },
        ),
    ],
)
async def calendars(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get House or Senate Congressional Calendar editions."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CongressMandatedReports",
    examples=[
        APIEx(parameters={"provider": "congress_gov"}),
        APIEx(
            description="Get the 10 most recent mandated reports for the 119th Congress.",
            parameters={"congress": 119, "limit": 10, "provider": "congress_gov"},
        ),
    ],
)
async def mandated_reports(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Congressionally Mandated Reports submitted by federal agencies."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CongressSearch",
    examples=[
        APIEx(
            parameters={"query": "artificial intelligence", "provider": "congress_gov"}
        ),
        APIEx(
            description="Search hearings in the 119th Congress for 'immigration'.",
            parameters={
                "query": "immigration",
                "collection": "CHRG",
                "congress": 119,
                "provider": "congress_gov",
            },
        ),
    ],
)
async def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Full-text search across congressional GovInfo collections."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


def _document_viewer_config(
    name: str, description: str, widget_id: str, options_endpoint: str
) -> dict:
    """Build a multi_file_viewer widget_config that groups by ``package_id``."""
    return {
        "widget_config": {
            "name": name,
            "description": description,
            "category": "Government",
            "subCategory": "Congress",
            "type": "multi_file_viewer",
            "widgetId": widget_id,
            "endpoint": f"{api_prefix}/uscongress/bill_text",
            "params": [
                {
                    "paramName": "urls",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix}/uscongress/{options_endpoint}",
                    "optionsParams": {
                        "package_id": "$package_id",
                        "is_workspace": True,
                    },
                    "show": False,
                    "multiSelect": True,
                    "roles": ["fileSelector"],
                },
                {"paramName": "is_workspace", "value": True, "show": False},
                {
                    "label": "Package ID",
                    "description": "The GovInfo package id. Group by 'package_id' on"
                    + " the source table and click a cell to load the document.",
                    "show": True,
                    "paramName": "package_id",
                    "value": "",
                },
            ],
            "refetchInterval": False,
        }
    }


@router.command(
    methods=["GET"],
    examples=[
        APIEx(
            parameters={
                "provider": "congress_gov",
                "law_id": "119-1",
                "law_type": "public",
            }
        ),
    ],
    openapi_extra={
        "widget_config": {
            "name": "Congressional Law Viewer",
            "description": "View the text of an enacted public or private law.",
            "category": "Government",
            "subCategory": "Congress",
            "type": "multi_file_viewer",
            "widgetId": "uscongress_law_viewer_congress_gov_obb",
            "endpoint": f"{api_prefix}/uscongress/bill_text",
            "params": [
                {
                    "paramName": "urls",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix}/uscongress/law_text_urls",
                    "optionsParams": {
                        "law_id": "$law_id",
                        "law_type": "$law_type",
                        "is_workspace": True,
                    },
                    "show": False,
                    "multiSelect": True,
                    "roles": ["fileSelector"],
                },
                {"paramName": "is_workspace", "value": True, "show": False},
                {
                    "label": "Law Type",
                    "show": True,
                    "paramName": "law_type",
                    "value": "public",
                    "options": [
                        {"label": "Public Law", "value": "public"},
                        {"label": "Private Law", "value": "private"},
                    ],
                },
                {
                    "label": "Law ID",
                    "description": "Group the Laws table by 'Law ID' and click a cell"
                    + " to load the law text.",
                    "show": True,
                    "paramName": "law_id",
                    "value": "",
                },
            ],
            "refetchInterval": False,
        }
    },
)
async def law_text_urls(
    law_id: str = "",
    law_type: str = "public",
    provider: str = "congress_gov",
    is_workspace: bool = False,
) -> list:
    """Get the document link for an enacted law, by law id (e.g. '119-1')."""
    # pylint: disable=import-outside-toplevel
    from openbb_congress_gov.utils.helpers import get_document_choices

    if not law_id or "-" not in law_id:
        if is_workspace is True:
            return [{"label": "Select a law to view.", "value": ""}]
        raise HTTPException(
            status_code=500,
            detail="A law_id (e.g. '119-1') is required to view a law.",
        )

    congress, number = law_id.split("-", 1)
    suffix = "pvtl" if law_type.lower() == "private" else "publ"
    package_id = f"PLAW-{congress}{suffix}{number}"

    return get_document_choices(package_id, is_workspace)


@router.command(
    methods=["GET"],
    examples=[
        APIEx(
            parameters={
                "provider": "congress_gov",
                "chamber": "house",
                "calendar_date": "2025-01-03",
            }
        ),
    ],
    openapi_extra={
        "widget_config": {
            "name": "Congressional Calendar Viewer",
            "description": "View a House or Senate Congressional Calendar edition.",
            "category": "Government",
            "subCategory": "Congress",
            "type": "multi_file_viewer",
            "widgetId": "uscongress_calendar_viewer_congress_gov_obb",
            "endpoint": f"{api_prefix}/uscongress/bill_text",
            "params": [
                {
                    "paramName": "urls",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix}/uscongress/calendar_urls",
                    "optionsParams": {
                        "calendar_date": "$calendar_date",
                        "chamber": "$chamber",
                        "congress": "$congress",
                        "is_workspace": True,
                    },
                    "show": False,
                    "multiSelect": True,
                    "roles": ["fileSelector"],
                },
                {"paramName": "is_workspace", "value": True, "show": False},
                {
                    "label": "Chamber",
                    "show": True,
                    "paramName": "chamber",
                    "value": "house",
                    "options": [
                        {"label": "House", "value": "house"},
                        {"label": "Senate", "value": "senate"},
                    ],
                },
                {
                    "label": "Congress",
                    "show": True,
                    "paramName": "congress",
                    "value": 119,
                    "type": "number",
                },
                {
                    "label": "Calendar Date",
                    "description": "Group the Calendars table by 'Calendar Date' and"
                    + " click a cell to load the edition.",
                    "show": True,
                    "paramName": "calendar_date",
                    "value": "",
                },
            ],
            "refetchInterval": False,
        }
    },
)
async def calendar_urls(
    calendar_date: str = "",
    chamber: str = "house",
    congress: int | None = None,
    provider: str = "congress_gov",
    is_workspace: bool = False,
) -> list:
    """Get the document link for a calendar edition, by date and chamber."""
    # pylint: disable=import-outside-toplevel
    from datetime import datetime

    from openbb_congress_gov.utils.bulk import _CCAL_CHAMBER_CODE
    from openbb_congress_gov.utils.helpers import (
        get_document_choices,
        year_to_congress,
    )

    if not calendar_date:
        if is_workspace is True:
            return [{"label": "Select a calendar date to view.", "value": ""}]
        raise HTTPException(
            status_code=500,
            detail="A calendar_date is required to view a calendar.",
        )

    cong = int(congress) if congress else year_to_congress(datetime.now().year)
    code = _CCAL_CHAMBER_CODE.get(chamber.lower(), "h")
    package_id = f"CCAL-{cong}{code}cal-{calendar_date}"

    return get_document_choices(package_id, is_workspace)


@router.command(
    methods=["GET"],
    examples=[
        APIEx(
            parameters={
                "provider": "congress_gov",
                "package_id": "CMR-A98-00199920",
            }
        ),
    ],
    openapi_extra=_document_viewer_config(
        "Mandated Report Viewer",
        "View a Congressionally Mandated Report submitted by a federal agency.",
        "uscongress_mandated_report_viewer_congress_gov_obb",
        "mandated_report_urls",
    ),
)
async def mandated_report_urls(
    package_id: str = "",
    provider: str = "congress_gov",
    is_workspace: bool = False,
) -> list:
    """Get the document link for a mandated report, by GovInfo package id."""
    # pylint: disable=import-outside-toplevel
    from openbb_congress_gov.utils.helpers import get_document_choices

    return get_document_choices(package_id, is_workspace)


@router.command(
    methods=["GET"],
    examples=[
        APIEx(
            parameters={"provider": "congress_gov", "package_id": "CHRG-119hhrg63299"}
        ),
    ],
    openapi_extra=_document_viewer_config(
        "Congressional Search Viewer",
        "View a document returned by the congressional full-text search.",
        "uscongress_search_viewer_congress_gov_obb",
        "search_document_urls",
    ),
)
async def search_document_urls(
    package_id: str = "",
    provider: str = "congress_gov",
    is_workspace: bool = False,
) -> list:
    """Get the document link for a search result, by GovInfo package id."""
    # pylint: disable=import-outside-toplevel
    from openbb_congress_gov.utils.helpers import get_document_choices

    return get_document_choices(package_id, is_workspace)


# pylint: disable=W0212
@router.command(
    methods=["GET"],
    examples=[
        APIEx(parameters={"provider": "congress_gov", "bill_id": "119-hr-29"}),
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
                        "bill_id": "$bill_id",
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
                    "label": "Bill ID",
                    "description": "Enter a bill id (e.g. '119-hr-29'), or group the"
                    + " 'Congressional Bills' widget by 'Bill ID' and click a cell.",
                    "show": True,
                    "paramName": "bill_id",
                    "value": "119-hr-1",
                },
            ],
            "refetchInterval": False,
        }
    },
)
async def bill_text_urls(
    bill_id: str = "",
    provider: str = "congress_gov",
    is_workspace: bool = False,
) -> list:
    """Get the available text-version document links for a bill, by bill id.

    Used by the Congressional Bill Viewer widget to populate the document choices
    for the selected bill (e.g. ``119-hr-29``). Sourced keyless from GovInfo.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_congress_gov.utils.helpers import get_bill_text_choices

    if not bill_id:
        if is_workspace is True:
            return [
                {"label": "Select a bill to view available documents.", "value": ""}
            ]
        raise HTTPException(
            status_code=500,
            detail="A bill_id (e.g. '119-hr-29') is required.",
        )

    return await get_bill_text_choices(bill_id=bill_id, is_workspace=is_workspace)


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
    no_validate=True,
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
    return (await OBBject.from_query(OpenBBQuery(**locals()))).results  # type: ignore


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
        APIEx(parameters={"provider": "congress_gov", "amendment_id": "119-hamdt-2"}),
    ],
    openapi_extra={
        "widget_config": {
            "name": "Congressional Amendment Viewer",
            "description": "View Congressional Record documents for a U.S. Amendment.",
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
                        "amendment_id": "$amendment_id",
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
                    "label": "Amendment ID",
                    "description": "Enter an amendment id (e.g. '119-hamdt-2'), or group"
                    + " the 'Congressional Amendments' widget by 'Amendment ID' and"
                    + " click a cell.",
                    "show": True,
                    "paramName": "amendment_id",
                    "value": "119-hamdt-2",
                },
            ],
            "refetchInterval": False,
        }
    },
)
async def amendment_text_urls(
    amendment_id: str = "",
    provider: str = "congress_gov",
    is_workspace: bool = False,
) -> list:
    """Get the Congressional Record document links for an amendment, by amendment id.

    Used by the Congressional Amendment Viewer widget to populate the document
    choices for the selected amendment (e.g. ``119-hamdt-2``). Resolved keyless
    via the GovInfo link service.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_congress_gov.utils.helpers import get_amendment_text_choices

    if not amendment_id:
        if is_workspace is True:
            return [
                {
                    "label": "Select an amendment to view available documents.",
                    "value": "",
                }
            ]
        raise HTTPException(
            status_code=500,
            detail="An amendment_id (e.g. '119-hamdt-2') is required.",
        )

    return await get_amendment_text_choices(
        amendment_id=amendment_id, is_workspace=is_workspace
    )


@router.command(
    model="CongressAmendmentInfo",
    examples=[
        APIEx(parameters={"provider": "congress_gov", "amendment_id": "119-hamdt-2"}),
    ],
)
async def amendment_info(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get details for a specific amendment.

    Enter the amendment identifier as: {congress}-{type}-{number} (e.g., '119-hamdt-2').

    In OpenBB Workspace, this command returns as a Markdown widget.
    """
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CongressAmendmentText",
    response_model=list,
    no_validate=True,
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "provider": "congress_gov",
                "urls": [
                    "https://www.govinfo.gov/content/pkg/CREC-2022-03-24/pdf/CREC-2022-03-24-pt1-PgS1778-4.pdf"
                ],
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
    return (await OBBject.from_query(OpenBBQuery(**locals()))).results  # type: ignore


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
) -> list:
    """Get document choices for a Congressional Committee.

    This endpoint populates the Committee Document Viewer file selector with the
    committee's available documents by type (sourced keyless from GovInfo). For
    hearings, witness statements and accompanying documents are included.
    """
    # pylint: disable=import-outside-toplevel
    from datetime import datetime

    from openbb_congress_gov.utils.committees import get_committee_doc_choices
    from openbb_congress_gov.utils.helpers import year_to_congress

    if not committee:
        if is_workspace is True:
            return [
                {
                    "label": "Select a committee to view available documents.",
                    "value": "",
                }
            ]
        raise HTTPException(
            status_code=500,
            detail="Committee system code is required.",
        )

    system_code = (subcommittee or committee).lower()
    if congress is None:
        congress = year_to_congress(datetime.now().year)

    return await get_committee_doc_choices(
        system_code=system_code,
        congress=congress,
        doc_type=doc_type,
        is_workspace=is_workspace,
    )


async def get_congress_gov_apps_json() -> list[dict[str, Any]]:
    """Get the Congress.gov apps.json file.

    This endpoint serves the apps.json file containing OpenBB Workspace app configurations
    related to Congress.gov legislative data.

    It is automatically merged with any existing apps.json files in the Workspace and API.

    Returns
    -------
    list[dict[str, Any]]
        A list of OpenBB Workspace app configurations.
    """
    # pylint: disable=import-outside-toplevel
    import json
    from pathlib import Path

    apps_file = Path(__file__).parent / "assets" / "apps.json"

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


async def committee_members(
    chamber: str = "senate",
    committee: str = "ssaf00",
    subcommittee: str | None = None,
    theme: str | None = "dark",
):
    """Render a committee's members as themed HTML cards (OpenBB Workspace HTML widget).

    Returns raw HTML (not an OBBject) so the Workspace HTML widget renders the
    member cards directly. Member photos and real party (R/D) come from the
    keyless unitedstates dataset; the layout is theme-aware.
    """
    from openbb_congress_gov.utils.bulk import load_legislators
    from openbb_congress_gov.utils.committees import get_committee_members
    from openbb_congress_gov.utils.member_cards import render_member_cards

    system_code = (subcommittee or committee).lower()
    members = await get_committee_members(system_code)
    legislators = await load_legislators()

    return HTMLResponse(content=render_member_cards(members, legislators, theme))


router._api_router.add_api_route(
    path="/committee_members",
    endpoint=committee_members,
    methods=["GET"],
    response_class=HTMLResponse,
    openapi_extra={
        "widget_config": {
            "name": "Congressional Committee Members",
            "description": "Member cards for a U.S. Congressional Committee.",
            "category": "Government",
            "subCategory": "Congress",
            "type": "html",
            "widgetId": "uscongress_committee_members_congress_gov_obb",
            "params": [
                {
                    "label": "Chamber",
                    "show": True,
                    "paramName": "chamber",
                    "value": "house",
                    "options": [
                        {"label": "Senate", "value": "senate"},
                        {"label": "House", "value": "house"},
                        {"label": "Joint", "value": "joint"},
                    ],
                },
                {
                    "label": "Committee",
                    "show": True,
                    "paramName": "committee",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix}/uscongress/committee_choices",
                    "optionsParams": {
                        "chamber": "$chamber",
                        "is_workspace": True,
                    },
                    "value": "hsju00",
                    "style": {"popupWidth": 700},
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
                {"paramName": "theme", "show": False},
            ],
            "refetchInterval": False,
        }
    },
)


@router.command(
    model="CongressMembers",
    examples=[
        APIEx(parameters={"provider": "congress_gov"}),
        APIEx(
            parameters={
                "chamber": "house",
                "state": "OH",
                "provider": "congress_gov",
            }
        ),
    ],
)
async def members(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get and filter the current members of the U.S. Congress."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


async def member_info(
    bioguide_id: str = "A000055",
    theme: str | None = "dark",
):
    """Render a member's bio, history, and committees as a themed HTML card.

    Returns raw HTML (not an OBBject) so the OpenBB Workspace HTML widget renders
    the member's photo, party-colored heading, contact details, external profile
    and social links, committee assignments, and full term history directly. All
    data is keyless from the unitedstates congress-legislators datasets.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_congress_gov.utils.bulk import (
        load_member_record,
        load_social_media,
        member_committees,
        member_passage_record,
        member_service,
    )
    from openbb_congress_gov.utils.member_cards import render_member_bio

    record = await load_member_record(bioguide_id)
    committees = await member_committees(bioguide_id)
    social = (await load_social_media()).get(bioguide_id, {})
    voting = await member_passage_record(bioguide_id, member_service(record))

    return HTMLResponse(
        content=render_member_bio(record, committees, social, voting, theme)
    )


router._api_router.add_api_route(
    path="/member_info",
    endpoint=member_info,
    methods=["GET"],
    response_class=HTMLResponse,
    openapi_extra={
        "widget_config": {
            "name": "Congressional Member Info",
            "description": "Bio, history, and committee assignments for a member.",
            "category": "Government",
            "subCategory": "Congress",
            "type": "html",
            "widgetId": "uscongress_member_info_congress_gov_obb",
            "params": [
                {
                    "label": "Member",
                    "show": True,
                    "paramName": "bioguide_id",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix}/uscongress/member_choices",
                    "optionsParams": {"is_workspace": True},
                    "value": "A000055",
                    "style": {"popupWidth": 400},
                },
                {"paramName": "theme", "show": False},
            ],
            "refetchInterval": False,
        }
    },
)


@router.command(
    model="CongressMemberVotes",
    examples=[
        APIEx(parameters={"provider": "congress_gov", "bioguide_id": "A000055"}),
    ],
)
async def member_votes(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get a member's roll-call votes on legislation, House and Senate.

    Sourced keyless from Voteview, spanning the member's full voting history.
    """
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CongressMemberLegislation",
    examples=[
        APIEx(parameters={"provider": "congress_gov", "bioguide_id": "A000055"}),
    ],
)
async def member_legislation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the bills a member sponsored or cosponsored in a Congress."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    methods=["GET"],
    openapi_extra={"widget_config": {"exclude": True}},
)
async def member_choices(
    chamber: str | None = None,
    provider: str = "congress_gov",
    is_workspace: bool = False,
) -> list:
    """Get bioguide picker choices for the member widgets."""
    # pylint: disable=import-outside-toplevel
    from openbb_congress_gov.utils.bulk import (
        filter_members,
        load_members,
        to_member_list_item,
    )

    members_data = await load_members()
    items = filter_members(
        [to_member_list_item(m) for m in members_data], chamber=chamber
    )

    choices: list = []
    for item in items:
        district = f"-{item['district']}" if item.get("district") else ""
        party = (item.get("party") or "")[:1]
        choices.append(
            {
                "label": f"{item['name']} ({party}-{item['state']}{district})",
                "value": item["bioguide_id"],
            }
        )

    return choices or [{"label": "No members found.", "value": ""}]


async def how_to_use(note: str = "bills") -> str:
    """Return a tab's 'How To Use' note as Markdown (OpenBB Workspace markdown widget).

    Returns the raw Markdown string for the requested tab so the Workspace
    markdown widget renders it directly. The ``note`` parameter selects which
    tab's instructions to serve.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_congress_gov.utils.notes import HOW_TO_USE

    return HOW_TO_USE.get(note, "")


router._api_router.add_api_route(
    path="/how_to_use",
    endpoint=how_to_use,
    methods=["GET"],
    openapi_extra={
        "widget_config": {
            "name": "How To Use",
            "description": "Usage notes for the U.S. Congress app tabs.",
            "category": "Government",
            "subCategory": "Congress",
            "type": "markdown",
            "widgetId": "uscongress_how_to_use_congress_gov_obb",
            "data": {"dataKey": ""},
            "params": [
                {
                    "paramName": "note",
                    "value": "bills",
                    "show": False,
                },
            ],
            "refetchInterval": False,
        }
    },
)


# Keep references to background tasks so they are not garbage-collected.
_BACKGROUND_TASKS: set = set()


async def _preload_bills() -> None:
    """Download and cache the current Congress bills bulk data for every bill type.

    Warms BILLSTATUS (backing the bills table, bill_info, and the bill viewer) and
    BILLSUM (the CRS summaries merged into bill_info) so all three bill widgets
    open against a warm cache.
    """
    import asyncio
    from datetime import datetime

    from openbb_congress_gov.utils.bulk import load_billstatus, load_billsum
    from openbb_congress_gov.utils.constants import BillTypes
    from openbb_congress_gov.utils.helpers import year_to_congress

    congress = year_to_congress(datetime.now().year)
    tasks: list = []
    for bill_type in BillTypes:
        tasks.append(load_billstatus(congress, bill_type))
        tasks.append(load_billsum(congress, bill_type))

    await asyncio.gather(*tasks, return_exceptions=True)


def _warm_bills_cache() -> None:
    """Kick off the BILLSTATUS cache warmup in the background at API startup.

    Scheduled as a fire-and-forget task so server startup is never blocked by the
    bulk-data downloads; the cache is populated before the first user query.
    """
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return

    task = loop.create_task(_preload_bills())
    _BACKGROUND_TASKS.add(task)
    task.add_done_callback(_BACKGROUND_TASKS.discard)


router._api_router.add_event_handler("startup", _warm_bills_cache)
