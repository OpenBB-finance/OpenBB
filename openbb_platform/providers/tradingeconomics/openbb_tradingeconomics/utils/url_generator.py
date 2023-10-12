"""Helper to generate urls for Trading Economics API."""
from datetime import date
from urllib.parse import quote


def generate_url(in_query):
    """
    Generate the url for trading economimcs.  There is not a single api endpoint to hit so these are
    generated based on the cominations.  There are also some combinations that return no data so that will return ""
    """
    # Converting the input query to a dict of params that are not None
    query = {k: v for k, v in in_query.dict().items() if v is not None}

    # Nothing -- just a snapshot
    if not query:
        return "https://api.tradingeconomics.com/calendar?c=api_key"

    # Both start and end date are required
    if "start_date" in query and "end_date" not in query:
        query["end_date"] = date.today().strftime("%Y-%m-%d")
    if "end_date" in query and "start_date" not in query:
        query["start_date"] = query["end_date"]

    # Handle the formatting for the api
    if "country" in query:
        country = quote(",".join(query["country"]).replace("_", " "))
    if "group" in query:
        group = quote(query["group"])

    # We can have the possible combinations:
    # Country only
    if (
        "country" in query
        and "start_date" not in query
        and "importance" not in query
        and "group" not in query
        and "end_date" not in query
    ):
        return f"https://api.tradingeconomics.com/calendar/country/{country}?c=api_key"
    #  Country + Date
    if (
        "country" in query
        and "start_date" in query
        and "end_date" in query
        and "importance" not in query
        and "group" not in query
    ):
        return f'https://api.tradingeconomics.com/calendar/country/{country}/{query["start_date"]}/{query["end_date"]}?c=api_key'
    #  Country + Importance
    if (
        "country" in query
        and "importance" in query
        and "start_date" not in query
        and "end_date" not in query
        and "group" not in query
    ):
        return f'https://api.tradingeconomics.com/calendar/country/{country}?c=api_key&importance{query["importance"]}'
    #  Country + Group
    if (
        "country" in query
        and "group" in query
        and "start_date" not in query
        and "end_date" not in query
        and "importance" not in query
    ):
        return f"https://api.tradingeconomics.com/calendar/country/{country}/group/{group}?c=api_key"
    #  Country + group + date
    if (
        "country" in query
        and "group" in query
        and "start_date" in query
        and "end_date" in query
        and "importance" not in query
    ):
        return f'https://api.tradingeconomics.com/calendar/country/{country}&group={group}/{query["start_date"]}/{query["end_date"]}?c=api_key'

    # By date only
    if (
        "start_date" in query
        and "end_date" in query
        and "country" not in query
        and "importance" not in query
        and "group" not in query
    ):
        return f'https://api.tradingeconomics.com/calendar/country/All/{query["start_date"]}/{query["end_date"]}?c=api_key'

    # By importance only
    if (
        "importance" in query
        and "country" not in query
        and "group" not in query
        and "start_date" not in query
        and "end_date" not in query
    ):
        return f'https://api.tradingeconomics.com/calendar?c=api_key&importance={query["importance"]}'

    # By importance and date
    if (
        "importance" in query
        and "start_date" in query
        and "end_date" in query
        and "country" not in query
        and "group" not in query
    ):
        return f'https://api.tradingeconomics.com/calendar/country/All/{query["start_date"]}/{query["end_date"]}?c=api_key&importance={query["importance"]}'

    # Group Only
    if (
        "group" in query
        and "country" not in query
        and "start_date" not in query
        and "end_date" not in query
        and "importance" not in query
    ):
        return f'https://api.tradingeconomics.com/calendar/group/{query["group"]}?c=api_key'

    # Group + Date
    if (
        "group" in query
        and "start_date" in query
        and "end_date" in query
        and "country" not in query
        and "importance" not in query
    ):
        return f'https://api.tradingeconomics.com/calendar/group/{query["group"]}/{query["start_date"]}/{query["end_date"]}?c=api_key'

    return ""
