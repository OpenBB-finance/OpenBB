"""Congress.gov helpers."""

from typing import Literal, Optional, Union

from fastapi.exceptions import HTTPException
from openbb_congress_gov.utils.constants import BillTypes, base_url, bill_type_options
from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.provider.utils.errors import UnauthorizedError


# pylint: disable=R0903
class BillsState(metaclass=SingletonMeta):
    """Singleton class to manage application cache."""

    def __init__(self):
        """Initialize the BillsState."""
        if not hasattr(self, "bills"):
            self.bills = {}


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


def check_api_key() -> str:
    """Check if the Congress.gov API key is set in user settings.

    Raises UnauthorizedError if the API key is not set.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.service.user_service import UserSettings
    from pydantic import SecretStr

    credentials = UserSettings().credentials
    api_key = getattr(
        credentials, "congress_gov_api_key", SecretStr("")
    ).get_secret_value()

    if not api_key:
        raise UnauthorizedError("Missing credentials: congress_gov_api_key")

    return api_key


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


# pylint: disable=R0917
async def get_bills_by_type(
    congress: Optional[int] = None,
    bill_type: str = "hr",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    sort_by: Literal["asc", "desc"] = "desc",
) -> Union[dict, list]:
    """Fetch bills of a specific type for a given Congress number.

    Results are sorted by date of the latest action on the bill.

    Parameters
    ----------
    congress : Optional[int]
        The Congress number (e.g., 118 for the 118th Congress).
        If None, defaults to the current Congress based on the current year.
    bill_type : str
        The type of bill to fetch (e.g., "hr" for House bills).
    start_date : Optional[str]
        The start date in ISO format (YYYY-MM-DD) for filtering bills.
        If None, no start date filter is applied.
    end_date : Optional[str]
        The end date in ISO format (YYYY-MM-DD) for filtering bills.
        If None, no end date filter is applied.
    limit : Optional[int]
        The maximum number of bills to return. Defaults to 10 if None.
        To fetch all bills, use `get_all_bills_by_type()` instead.
    offset : Optional[int]
        The number of results to skip before starting to collect the result set.
        Defaults to 0 if None.
    sort_by : Literal["asc", "desc"]
        The sort order for the results. Defaults to "desc".

    Returns
    -------
    dict
        A dictionary of the raw JSON response from the API.
    """
    # pylint: disable=import-outside-toplevel
    from datetime import (  # noqa
        date as dateType,
        datetime,
    )
    from openbb_core.provider.utils.helpers import amake_request

    if bill_type and bill_type not in BillTypes:
        raise ValueError(
            f"Invalid bill type: {bill_type}. Must be one of {', '.join(BillTypes)}."
        )

    api_key = check_api_key()

    if start_date is None and end_date is None and congress is None:
        congress = year_to_congress(datetime.now().year)
    elif congress is None and start_date is not None:
        congress = year_to_congress(dateType.fromisoformat(start_date).year)
    elif congress is None and end_date is not None and start_date is None:
        congress = year_to_congress(dateType.fromisoformat(end_date).year)
    elif start_date is not None and end_date is not None:
        start_year = dateType.fromisoformat(start_date).year
        end_year = dateType.fromisoformat(end_date).year
        congress_start = year_to_congress(start_year)
        congress_end = year_to_congress(end_year)
        if congress_start != congress_end:
            raise ValueError(
                "Start and end dates must be in the same Congress session."
            )
        congress = congress_start

    if congress is None:
        congress = year_to_congress(datetime.now().year)

    url = (
        f"{base_url}bill/{congress}/{bill_type}"
        + (f"?fromDateTime={start_date + 'T00:00:00Z'}" if start_date else "")
        + (f"&toDateTime={end_date + 'T23:59:59Z'}" if end_date else "")
        + f"?limit={limit if limit is not None else 10}"
        + (f"&offset={offset}" if offset else "")
        + f"&sort=updateDate+{sort_by}"
        + f"&format=json&api_key={api_key}"
    )

    return await amake_request(url)


async def get_all_bills_by_type(
    congress: Optional[int] = None,
    bill_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Fetch all bills of a specific type for a given Congress number.

    Parameters
    ----------
    congress : Optional[int]
        The Congress number (e.g., 118 for the 118th Congress).
        If None, defaults to the current Congress based on the current year.
    bill_type : Optional[str]
        The type of bill to fetch (e.g., "hr" for House bills).
        Must be one of: "hr", "s", "hjres", "sjres", "hconres", "sconres", "hres", "sres"
        If None, defaults to "hr".
    start_date : Optional[str]
        The start date in ISO format (YYYY-MM-DD) for filtering bills.
        If None, no start date filter is applied.
    end_date : Optional[str]
        The end date in ISO format (YYYY-MM-DD) for filtering bills.
        If None, no end date filter is applied.
    Returns
    -------
    list
        A list of dictionaries containing all bills of the specified type for the given Congress.
    """
    # pylint: disable=import-outside-toplevel
    import math  # noqa
    from openbb_core.provider.utils.helpers import amake_requests

    bill_type = "hr" if bill_type is None else bill_type.lower()

    if bill_type not in BillTypes:
        raise ValueError(
            f"Invalid bill type: {bill_type}. Must be one of {', '.join(BillTypes)}."
        )

    api_key = check_api_key()
    results: list = []
    limit = 250
    offset = 0
    res = await get_bills_by_type(
        congress=congress,
        bill_type=bill_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    results.extend(res.get("bills", []))  # type: ignore
    total_bills = res.get("pagination", {}).get("count", 0)  # type: ignore
    next_url = res.get("pagination", {}).get("next", None)  # type: ignore
    urls: list = []

    # Generate the list of URLs instead of paginating in a loop.
    for i in range(1, math.ceil(total_bills / limit)):
        offset = i * limit
        url = (
            next_url.replace(f"offset={limit}", f"offset={offset}").replace(
                "updateDate ", "updateDate+"
            )
            + f"&api_key={api_key}"
        )
        urls.append(url)

    async def response_callback(response, _):
        """Process the response from the API and append the results."""
        result = await response.json()
        if result and "bills" in result and (bills := result.get("bills", [])):
            results.extend(bills)

    _ = await amake_requests(urls, response_callback=response_callback)  # type: ignore

    return sorted(results, key=lambda x: x["updateDate"], reverse=True)


async def get_bill_choices(
    congress: Optional[int] = None,
    bill_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    bill_url: Optional[str] = None,
    is_document_choices: Optional[bool] = None,
) -> list:
    """Fetch a list of bills of a specific type for a given Congress number.

    This function is not intended to be used directly.

    It is used by the OpenBB Workspace Congressional Bills Viewer widget
    to populate dynamic parameter choices based on the widget's state.
    """
    # pylint: disable=import-outside-toplevel
    from datetime import datetime

    bills_state = BillsState()

    if bill_type and bill_type not in [option["value"] for option in bill_type_options]:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid bill type: {bill_type}."
            + f" Must be one of {', '.join([option['value'] for option in bill_type_options])}.",
        )

    if bill_url:
        return await get_bill_text_choices(bill_url=bill_url)

    if is_document_choices is True and not bill_url:
        return [
            {
                "label": "Select a bill to view associated text.",
                "value": "",
            }
        ]

    if not bill_type:
        bill_type = "hr"

    if not congress:
        congress = year_to_congress(datetime.now().year)

    cached_bills = bills_state.bills.get(f"{congress}_{bill_type}")

    if not cached_bills:
        bills = await get_all_bills_by_type(
            congress=congress,
            bill_type=bill_type,  # type: ignore
        )
        bills_state.bills[f"{congress}_{bill_type}"] = bills
    else:
        bills = cached_bills

    if start_date:
        bills = (
            [bill for bill in bills if bill["latestAction"]["actionDate"] >= start_date]
            if not end_date
            else [
                bill
                for bill in bills
                if bill["latestAction"]["actionDate"] >= start_date
                and bill["latestAction"]["actionDate"] <= end_date
            ]
        )
    elif end_date and not start_date:
        bills = [
            bill for bill in bills if bill["latestAction"]["actionDate"] <= end_date
        ]

    results: list = []

    for bill in sorted(
        bills, key=lambda x: x["latestAction"]["actionDate"], reverse=True
    ):
        bill_title = bill.get("title", "")

        if not bill_title:
            continue

        bill_url = bill.get("url", "")
        label = (
            bill_title
            + f" ({bill.get('number', '')} - {bill['latestAction']['actionDate']})"
        )
        results.append(
            {
                "label": label,
                "value": bill_url,
            }
        )

    return results


async def get_bill_text_choices(bill_url: str, is_workspace: bool = False) -> list:
    """Fetch the direct download links for the available text versions of the specified bill.

    This function is used by the Congressional Bills Viewer widget,
    in OpenBB Workspace, to populate the document choices
    for the selected bill. When `is_workspace` is True,
    it returns a list of dictionaries with 'label' and 'value' keys.

    Parameters
    ----------
    bill_url : str
        The base URL of the bill (e.g., "https://api.congress.gov/v3/bill/119/s/1947?format=json").

    Returns
    -------
    list[dict]
        List of dictionaries with the results.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import amake_request

    api_key = check_api_key()
    results: list = []
    url = bill_url.replace("?", "/text?") + f"&api_key={api_key}"
    response = await amake_request(url)
    bill_text = response.get("textVersions", [])  # type: ignore

    # Return the results for non-Workspace queries
    if is_workspace is False:

        if not bill_text:
            raise HTTPException(
                status_code=404,
                detail="No text available for this bill currently.",
            )

        text_output: list = []

        for version in bill_text:
            bill_version: dict = {}
            formats = version.get("formats", [])
            bill_type = version.get("type", "")
            version_date = version.get("date", "")
            if not formats or not version_date:
                continue
            bill_version["version_type"] = bill_type
            bill_version["version_date"] = version_date
            for fmt in formats:
                doc_url = fmt.get("url")
                doc_type = fmt.get("type", "").replace("Formatted ", "").lower()
                bill_version[doc_type] = doc_url

            if bill_version:
                text_output.append(bill_version)

        return text_output

    if not bill_text:
        return [
            {
                "label": "No text available for this bill currently.",
                "value": "",
            }
        ]

    for version in bill_text:
        version_date = version.get("date")
        formats = version.get("formats", [])
        version_type = version.get("type", "")
        for fmt in formats:
            if (doc_type := fmt.get("type")) and doc_type == "PDF":
                doc_url = fmt.get("url")
                doc_name = doc_url.split("/")[-1]
                filename = (
                    f"{version_type} - {version_date} - {doc_name}"
                    if version_date
                    else doc_name
                )
                results.append(
                    {
                        "label": filename,
                        "value": doc_url,
                    }
                )
                break

    return results
