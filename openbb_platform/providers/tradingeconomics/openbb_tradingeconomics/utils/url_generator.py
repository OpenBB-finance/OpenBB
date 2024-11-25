"""Helper to generate urls for Trading Economics API."""

from datetime import date
from typing import Dict, List
from urllib.parse import quote, urlencode


def check_args(query_args: Dict, to_include: List[str]):
    """Check if all fields in to_include are present in query_args."""
    available_args = ["country", "start_date", "end_date", "importance", "group"]

    # Check if all fields in to_include are present in query_args
    # and elements in available_args that are not in to_include are not present in query_args
    return all(field in query_args for field in to_include) and all(
        field not in query_args for field in available_args if field not in to_include
    )


# pylint: disable = R0912
def generate_url(in_query):
    """Generate the url for trading economimcs.

    There is not a single api endpoint to hit so these are generated based on the combinations.
    There are also some combinations that return no data so that will return an empty string.
    """
    # Converting the input query to a dict of params that are not None
    query = {k: v for k, v in in_query.dict().items() if v is not None}

    # Nothing -- just a snapshot
    if not query:
        return "https://api.tradingeconomics.com/calendar?c="

    # Both start and end date are required
    if "start_date" in query and "end_date" not in query:
        query["end_date"] = date.today().strftime("%Y-%m-%d")
    if "end_date" in query and "start_date" not in query:
        query["start_date"] = query["end_date"]

    # Handle the formatting for the api
    if "country" in query:
        country = quote(query["country"].replace("_", " "))
    if "group" in query:
        group = quote(query["group"])

    base_url = "https://api.tradingeconomics.com/calendar"
    url = ""

    # Construct URL based on query parameters
    # Country Only
    if check_args(query, ["country"]):
        # pylint: disable=possibly-used-before-assignment
        url = f"{base_url}/country/{country}?c="
    # Country + Date
    elif check_args(query, ["country", "start_date", "end_date"]):
        url = (
            f'{base_url}/country/{country}/{query["start_date"]}/{query["end_date"]}?c='
        )
    # Country + Importance
    elif check_args(query, ["country", "importance"]):
        url = f"{base_url}/country/{country}?{urlencode(query)}&c="
    # Country + Group
    elif check_args(query, ["country", "group"]):
        # pylint: disable=possibly-used-before-assignment
        url = f"{base_url}/country/{country}/group/{group}?c="
    # Country + Group + Date
    elif check_args(query, ["country", "group", "start_date", "end_date"]):
        url = f'{base_url}/country/{country}/group/{group}/{query["start_date"]}/{query["end_date"]}?c='
    # Country + Date + Importance
    elif check_args(query, ["country", "importance", "start_date", "end_date"]):
        url = f'{base_url}/country/{country}/{query["start_date"]}/{query["end_date"]}?{urlencode(query)}&c='
    # By date only
    elif check_args(query, ["start_date", "end_date"]):
        url = f'{base_url}/country/All/{query["start_date"]}/{query["end_date"]}?c='
    # By importance only
    elif check_args(query, ["importance"]):
        url = f"{base_url}?{urlencode(query)}&c="
    # By importance and date
    elif check_args(query, ["importance", "start_date", "end_date"]):
        url = f'{base_url}/country/All/{query["start_date"]}/{query["end_date"]}?{urlencode(query)}&c='
    # Group Only
    elif check_args(query, ["group"]):
        url = f'{base_url}/group/{query["group"]}?c='
    # Group + Date
    elif check_args(query, ["group", "start_date", "end_date"]):
        url = f'{base_url}/group/{query["group"]}/{query["start_date"]}/{query["end_date"]}?c='
    # All fields
    elif check_args(
        query, ["country", "group", "importance", "start_date", "end_date"]
    ):
        start_date = query["start_date"]
        end_date = query["end_date"]
        url = f"{base_url}/country/{country}/group/{group}/{start_date}/{end_date}?{urlencode(query)}&c="
    # Calendar IDs
    elif check_args(query, ["calendar_id"]):
        url = f'{base_url}/calendarid/{str(query["calendar_id"])}?c='

    return url if url else ""
