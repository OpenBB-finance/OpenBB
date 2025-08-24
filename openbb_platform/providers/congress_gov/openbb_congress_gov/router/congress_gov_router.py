# pylint: disable=import-outside-toplevel,unused-argument
"""US Congress Router."""

from fastapi.exceptions import HTTPException
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
            "searchCategory": "Congress",
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
