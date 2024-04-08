"""Helper functions for FINRA API."""

import datetime
from typing import List

import requests

# pylint: disable=W0621


def get_finra_weeks(tier: str = "T1", is_ats: bool = True):
    """Fetch the available weeks from FINRA that can be used."""
    request_header = {"Accept": "application/json", "Content-Type": "application/json"}

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

    response = requests.post(
        "https://api.finra.org/data/group/otcMarket/name/weeklyDownloadDetails",
        headers=request_header,
        json=request_data,
        timeout=3,
    )

    return response.json() if response.status_code == 200 else []


def get_finra_data(symbol, week_start, tier: str = "T1", is_ats: bool = True):
    """Get the data for a symbol from FINRA."""
    req_hdr = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ",
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
    response = requests.post(
        "https://api.finra.org/data/group/otcMarket/name/weeklySummary",
        headers=req_hdr,
        json=req_data,
        timeout=2,
    )
    return response


def get_full_data(symbol, tier: str = "T1", is_ats: bool = True):
    """Get the full data for a symbol from FINRA."""
    weeks = [week["weekStartDate"] for week in get_finra_weeks(tier, is_ats)]

    data = []
    for week in weeks:
        response = get_finra_data(symbol, week, tier, is_ats)
        r_json = response.json()
        if response.status_code == 200 and r_json:
            data.append(response.json()[0])

    return data


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


def get_short_interest_dates() -> List[str]:
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
