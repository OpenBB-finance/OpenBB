# Helper functions for FINRA API

import requests


def get_finra_weeks(tier: str = "T1", is_ats: bool = True):
    """Fetches the available weeks from FINRA that can be used."""
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
    weeks = [week["weekStartDate"] for week in get_finra_weeks(tier, is_ats)]

    data = []
    for week in weeks:
        response = get_finra_data(symbol, week, tier, is_ats)
        r_json = response.json()
        if response.status_code == 200 and r_json:
            data.append(response.json()[0])

    return data
