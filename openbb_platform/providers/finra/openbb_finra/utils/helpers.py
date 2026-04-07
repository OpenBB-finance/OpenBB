"""Helper functions for FINRA API."""

import datetime

# pylint: disable=W0621


def get_finra_weeks(tier: str = "T1", is_ats: bool = True, **kwargs):
    """Fetch the available weeks from FINRA that can be used."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import get_requests_session, make_request

    session = kwargs.get("session", get_requests_session())

    request_header = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    request_data = {
        "compareFilters": [
            {
                "compareType": "EQUAL",
                "fieldName": "summaryTypeCode",
                "fieldValue": "ATS_W_SMBL" if is_ats else "OTC_W_SMBL",
            },
            {
                "compareType": "EQUAL",
                "fieldName": "tierIdentifier",
                "fieldValue": tier,
            },
        ],
        "delimiter": "|",
        "fields": ["weekStartDate"],
        "limit": 52,
        "quoteValues": False,
        "sortFields": ["-weekStartDate"],
    }

    response = make_request(
        method="POST",
        url="https://api.finra.org/data/group/otcMarket/name/weeklyDownloadDetails",
        headers=request_header,
        json=request_data,
        timeout=20,
        session=session,
    )

    return response.json() if response.status_code == 200 else []


def get_finra_data(symbol, week_start, tier: str = "T1", is_ats: bool = True, **kwargs):
    """Get the data for a symbol from FINRA."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import get_requests_session, make_request

    session = kwargs.get("session", get_requests_session())

    req_hdr = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    filters = [
        {
            "compareType": "EQUAL",
            "fieldName": "weekStartDate",
            "fieldValue": week_start,
        },
        {"compareType": "EQUAL", "fieldName": "tierIdentifier", "fieldValue": tier},
        {
            "compareType": "EQUAL",
            "description": "",
            "fieldName": "summaryTypeCode",
            "fieldValue": "ATS_W_SMBL" if is_ats else "OTC_W_SMBL",
        },
    ]

    if symbol:
        filters.append(
            {
                "compareType": "EQUAL",
                "fieldName": "issueSymbolIdentifier",
                "fieldValue": symbol,
            }
        )

    req_data = {
        "compareFilters": filters,
        "delimiter": "|",
        "fields": [
            "issueSymbolIdentifier",
            "totalWeeklyShareQuantity",
            "totalWeeklyTradeCount",
            "lastUpdateDate",
        ],
        "limit": 5000,
        "quoteValues": False,
        "sortFields": ["totalWeeklyShareQuantity"],
    }
    response = make_request(
        url="https://api.finra.org/data/group/otcMarket/name/weeklySummary",
        method="POST",
        headers=req_hdr,
        json=req_data,
        timeout=20,
        session=session,
    )
    return response


def get_full_data(symbol, tier: str = "T1", is_ats: bool = True):
    """Get the full data for a symbol from FINRA."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import get_requests_session

    session = get_requests_session()

    # We make a pre-flight request to the FINRA website to establish a session.
    # This is to avoid the TooManyRedirects error that occurs when the FINRA
    # API redirects to the FINRA website to establish a session.
    session.get("https://www.finra.org/finra-data", timeout=10)

    weeks = [
        week["weekStartDate"] for week in get_finra_weeks(tier, is_ats, session=session)
    ]

    data = []
    for week in weeks:
        response = get_finra_data(symbol, week, tier, is_ats, session=session)
        r_json = response.json()
        if response.status_code == 200 and r_json:
            data.extend(r_json)

    return data


async def aget_finra_weeks(tier: str = "T1", is_ats: bool = True, **kwargs):
    """Fetch the available weeks from FINRA asynchronously."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import amake_request

    session = kwargs.pop("session", None)

    request_header = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    request_data = {
        "compareFilters": [
            {
                "compareType": "EQUAL",
                "fieldName": "summaryTypeCode",
                "fieldValue": "ATS_W_SMBL" if is_ats else "OTC_W_SMBL",
            },
            {
                "compareType": "EQUAL",
                "fieldName": "tierIdentifier",
                "fieldValue": tier,
            },
        ],
        "delimiter": "|",
        "fields": ["weekStartDate"],
        "limit": 52,
        "quoteValues": False,
        "sortFields": ["-weekStartDate"],
    }

    kwargs_for_request = {
        "headers": request_header,
        "json": request_data,
        "timeout": 20,
    }
    if session is not None:
        kwargs_for_request["session"] = session

    result = await amake_request(
        url="https://api.finra.org/data/group/otcMarket/name/weeklyDownloadDetails",
        method="POST",
        **kwargs_for_request,  # type: ignore
    )

    return result if isinstance(result, list) else []


async def aget_finra_data(
    symbol, week_start, tier: str = "T1", is_ats: bool = True, **kwargs
):
    """Get the data for a symbol from FINRA asynchronously."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import amake_request

    session = kwargs.pop("session", None)

    filters = [
        {
            "compareType": "EQUAL",
            "fieldName": "weekStartDate",
            "fieldValue": week_start,
        },
        {"compareType": "EQUAL", "fieldName": "tierIdentifier", "fieldValue": tier},
        {
            "compareType": "EQUAL",
            "description": "",
            "fieldName": "summaryTypeCode",
            "fieldValue": "ATS_W_SMBL" if is_ats else "OTC_W_SMBL",
        },
    ]

    if symbol:
        filters.append(
            {
                "compareType": "EQUAL",
                "fieldName": "issueSymbolIdentifier",
                "fieldValue": symbol,
            }
        )

    req_data = {
        "compareFilters": filters,
        "delimiter": "|",
        "fields": [
            "issueSymbolIdentifier",
            "totalWeeklyShareQuantity",
            "totalWeeklyTradeCount",
            "lastUpdateDate",
        ],
        "limit": 5000,
        "quoteValues": False,
        "sortFields": ["totalWeeklyShareQuantity"],
    }

    req_hdr = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    kwargs_for_request = {"headers": req_hdr, "json": req_data, "timeout": 20}
    if session is not None:
        kwargs_for_request["session"] = session

    return await amake_request(
        url="https://api.finra.org/data/group/otcMarket/name/weeklySummary",
        method="POST",
        **kwargs_for_request,  # type: ignore
    )


async def aget_full_data(symbol, tier: str = "T1", is_ats: bool = True):
    """Get the full data for a symbol from FINRA asynchronously."""
    # pylint: disable=import-outside-toplevel
    import asyncio

    from openbb_core.provider.utils.helpers import get_async_requests_session

    session = await get_async_requests_session()

    try:
        await session.request("GET", "https://www.finra.org/finra-data", timeout=10)

        weeks_data = await aget_finra_weeks(tier, is_ats, session=session)
        weeks = [week["weekStartDate"] for week in weeks_data]

        async def fetch_week(week_start):
            result = await aget_finra_data(
                symbol, week_start, tier, is_ats, session=session
            )
            if isinstance(result, list) and result:
                return result
            if isinstance(result, dict) and result:
                return [result]
            return []

        results = await asyncio.gather(
            *[fetch_week(w) for w in weeks], return_exceptions=True
        )

        flat_results = []
        for r in results:
            if isinstance(r, list):
                flat_results.extend(r)

        return flat_results
    finally:
        await session.close()


def get_adjusted_date(year, month, day):
    """Find the closest date if the date falls on a weekend."""
    # Get the date
    date = datetime.date(year, month, day)

    # If the date is a Saturday, subtract one day
    if date.weekday() == 5:
        date -= datetime.timedelta(days=1)
    # If the date is a Sunday, subtract two days
    elif date.weekday() == 6:
        date -= datetime.timedelta(days=2)

    return date


def get_short_interest_dates() -> list[str]:
    """Get a list of dates for which the short interest data is available.

    It is reported on the 15th and the last day of each month,but if the date falls on a weekend,
    the date is adjusted to the closest friday.
    """

    def get_adjusted_date(year, month, day):
        """Find the closest date if the date falls on a weekend."""
        # Get the date
        date = datetime.date(year, month, day)

        # If the date is a Saturday, subtract one day
        if date.weekday() == 5:
            date -= datetime.timedelta(days=1)
        # If the date is a Sunday, subtract two days
        elif date.weekday() == 6:
            date -= datetime.timedelta(days=2)

        return date

    start_year = 2021
    today = datetime.date.today()  # Get today's date
    end_year = today.year
    dates_list = []

    for yr in range(start_year, end_year + 1):
        start_month = 7 if yr == start_year else 1
        end_month = 12 if yr < today.year else today.month - 1
        for month in range(start_month, end_month + 1):  # Start from July for 2021
            # Date for the 15th of the month
            date_15 = get_adjusted_date(yr, month, 15)
            dates_list.append(date_15.strftime("%Y%m%d"))

            # Date for the last day of the month
            if month == 2:  # February
                last_day = (
                    29 if (yr % 4 == 0 and yr % 100 != 0) or (yr % 400 == 0) else 28
                )
            elif month in [4, 6, 9, 11]:  # Months with 30 days
                last_day = 30
            else:  # Months with 31 days
                last_day = 31

            last_date = get_adjusted_date(yr, month, last_day)
            dates_list.append(last_date.strftime("%Y%m%d"))

    # Manually replace '20220415' with '20220414' due to holiday
    if "20220415" in dates_list:
        index = dates_list.index("20220415")
        dates_list[index] = "20220414"

    return dates_list
