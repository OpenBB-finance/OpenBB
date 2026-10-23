"""USAspending recipient helpers."""

REQUEST_TIMEOUT = 90

EARLIEST_FISCAL_YEAR = 2008

EARLIEST_SEARCH_DATE = "2007-10-01"

RECIPIENT_LEVELS = {"P", "C", "R"}

TOP_CATEGORIES: dict[str, str] = {
    "awarding_agency": "Awarding Agencies",
    "awarding_subagency": "Awarding Sub-Agencies",
    "federal_account": "Federal Accounts",
    "cfda": "Assistance Listings",
    "country": "Countries",
    "state_territory": "U.S. States or Territories",
}


def normalize_recipient_id(recipient_id: str) -> str:
    """Normalize a recipient id to the casing the source requires.

    Parameters
    ----------
    recipient_id : str
        A recipient id of the form '<uuid>-<P|C|R>'.

    Returns
    -------
    str
        The id with a lower-cased hash and an upper-cased level.

    Raises
    ------
    OpenBBError
        If the id carries no recipient level.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    value = (recipient_id or "").strip()
    head, separator, level = value.rpartition("-")

    if not separator or level.upper() not in RECIPIENT_LEVELS:
        raise OpenBBError(
            f"Invalid recipient_id: '{recipient_id}'. It must end with a recipient"
            " level, one of '-P' (parent), '-C' (child), or '-R' (neither),"
            " e.g. 'ab4b0d9e-2a56-a67b-1fb7-b54a68b680ed-P'."
        )

    return f"{head.lower()}-{level.upper()}"


def fiscal_year_window(year: int) -> dict[str, str]:
    """Build the time_period entry spanning a federal fiscal year."""
    return {"start_date": f"{year - 1}-10-01", "end_date": f"{year}-09-30"}


def resolve_window(start_date, end_date) -> dict[str, str]:
    """Build a time_period entry, clamped to the source's earliest search date."""
    from datetime import date

    end = end_date or date.today()
    start = start_date or date(end.year - 1, end.month, end.day)
    floor = EARLIEST_SEARCH_DATE

    return {
        "start_date": max(str(start), floor),
        "end_date": str(end),
    }


async def get_profile(recipient_id: str, year: str | None = None) -> dict:
    """Fetch a recipient's profile.

    Parameters
    ----------
    recipient_id : str
        The recipient id, normalized before the request.
    year : str | None
        'latest', 'all', or a fiscal year. Omitted entirely when None, because
        an empty value is read by the source as 'all'.

    Returns
    -------
    dict
        The recipient profile payload.
    """
    from openbb_government_us.treasury.utils.usaspending import get_usaspending

    path = f"recipient/{normalize_recipient_id(recipient_id)}/"

    if year:
        path = f"{path}?year={year}"

    return await get_usaspending(path, timeout=REQUEST_TIMEOUT)


async def get_children(duns_or_uei: str, year: str | None = None) -> list[dict]:
    """Fetch a parent recipient's children.

    Parameters
    ----------
    duns_or_uei : str
        The parent's 9-character DUNS or 12-character UEI.
    year : str | None
        'latest', 'all', or a fiscal year. Omitted entirely when None.

    Returns
    -------
    list[dict]
        The child recipient rows, or an empty list when the key is unusable.
    """
    from openbb_government_us.treasury.utils.usaspending import get_usaspending

    key = (duns_or_uei or "").strip()

    if len(key) not in (9, 12):
        return []

    path = f"recipient/children/{key}/"

    if year:
        path = f"{path}?year={year}"

    response = await get_usaspending(path, timeout=REQUEST_TIMEOUT)

    return response if isinstance(response, list) else []


async def get_spending_over_time(
    recipient_id: str, group: str, window: dict[str, str]
) -> list[dict]:
    """Fetch a recipient's obligations by period.

    Parameters
    ----------
    recipient_id : str
        The recipient id, normalized before the request.
    group : str
        'fiscal_year', 'calendar_year', 'quarter', or 'month'.
    window : dict[str, str]
        A single time_period entry.

    Returns
    -------
    list[dict]
        The period rows, ascending.
    """
    from openbb_government_us.treasury.utils.usaspending import post_usaspending

    response = await post_usaspending(
        "search/spending_over_time/",
        {
            "group": group,
            "filters": {
                "recipient_id": normalize_recipient_id(recipient_id),
                "time_period": [window],
            },
        },
        timeout=REQUEST_TIMEOUT,
    )

    return response.get("results") or []


async def get_new_awards_over_time(
    recipient_id: str, group: str, window: dict[str, str]
) -> list[dict]:
    """Fetch a recipient's new-award counts by period, retrying one timeout.

    Parameters
    ----------
    recipient_id : str
        The recipient id, normalized before the request.
    group : str
        'quarter' or 'month'. Both are fiscal; 'fiscal_year' is not, so it is
        not offered here.
    window : dict[str, str]
        A single time_period entry.

    Returns
    -------
    list[dict]
        The period rows, or an empty list when the recipient has no parent
        records for the requested level.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_government_us.treasury.utils.usaspending import post_usaspending

    payload = {
        "group": group,
        "filters": {
            "recipient_id": normalize_recipient_id(recipient_id),
            "time_period": [window],
        },
    }

    try:
        response = await post_usaspending(
            "search/new_awards_over_time/", payload, timeout=REQUEST_TIMEOUT
        )
    except OpenBBError:
        response = await post_usaspending(
            "search/new_awards_over_time/", payload, timeout=REQUEST_TIMEOUT
        )

    return response.get("results") or []


async def get_top_category(
    recipient_id: str, category: str, window: dict[str, str], limit: int = 5
) -> list[dict]:
    """Fetch a recipient's top entries for one spending category.

    Parameters
    ----------
    recipient_id : str
        The recipient id, normalized before the request.
    category : str
        One of the keys of TOP_CATEGORIES.
    window : dict[str, str]
        A single time_period entry. Always sent, because an unbounded query
        times out.
    limit : int
        Number of entries to return, capped by the source at 100.

    Returns
    -------
    list[dict]
        The category rows, descending by amount.
    """
    from openbb_government_us.treasury.utils.usaspending import post_usaspending

    response = await post_usaspending(
        f"search/spending_by_category/{category}/",
        {
            "filters": {
                "recipient_id": normalize_recipient_id(recipient_id),
                "time_period": [window],
            },
            "limit": min(limit, 100),
            "page": 1,
        },
        timeout=REQUEST_TIMEOUT,
    )

    return response.get("results") or []
