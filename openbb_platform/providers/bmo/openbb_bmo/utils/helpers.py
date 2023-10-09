"""BMO Helpers Module"""

from datetime import timedelta
from typing import Any, Dict

import pandas as pd
import requests
import requests_cache
from random_user_agent.user_agent import UserAgent

# Only used for obtaining the access token for the API.
bmo_token_session = requests_cache.CachedSession(
    "OpenBB_BMO_Token", expire_after=timedelta(days=1), use_cache_dir=True
)

# Used for obtaining data dump for single ETF.
bmo_etf_session = requests_cache.CachedSession(
    "OpenBB_BMO_ETF_Session", expire_after=timedelta(days=1), use_cache_dir=True
)


def get_random_agent() -> str:
    user_agent_rotator = UserAgent(limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent


def get_token(use_cache: bool = True) -> str:
    """Gets the authorization token for the API."""

    token_url = "https://www.bmogam.com/ksys-app-manager/services/getApplicationAppConfig/default"  # noqa

    if use_cache:
        return bmo_token_session.get(token_url, timeout=5).json()["authentication"][
            "token"
        ]

    return requests.get(token_url, timeout=5).json()["authentication"]["token"]


def get_fund_properties(symbol: str, use_cache: bool = True, **kwargs: Any) -> Dict:
    """Gets the data dump for an individual fund."""

    token = get_token()

    url = (
        "https://api-us.fundpress.io/fund/savedSearchEntity/productPage?"
        f"sourceCulture=Default&culture=en-CA&ticker={symbol}&token={token}"
    )

    data = {}

    if use_cache:
        data = bmo_etf_session.get(url, timeout=5).json()

    if not use_cache:
        data = requests.get(url, timeout=5).json()

    if len(data["values"]) > 0:
        return data["values"]
    return data


def get_data_dump(use_cache: bool = True, **kwargs: Any) -> pd.DataFrame:
    """Gets a data dump with all BMO ETFs."""

    results = []
    token = get_token()
    headers = {
        "Host": "api-us.fundpress.io",
        "User-Agent": get_random_agent(),
        "Accept": "application/json",
        "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.bmogam.com/",
        "content-type": "application/json",
        "x-ksys-token": f"{token}",
        "Origin": "https://www.bmogam.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "TE": "trailers",
    }

    payload = """{"type":"CLSS","clientCode":[""],"fundList":["etf_all_funds"],"fundListExclusion":[],"search":[],"identifierSearch":{"properties":["ticker","fund_name","objective"],"fuzzy":false,"placeholder":{"format":{"singular":"Search by {properties}","plural":"Search by {properties}"},"badge":{"show":true,"align":"right","format":{"singular":"{total} result","plural":"{total} results"}},"aliases":[{"key":"fund_name","value":"fund name"},{"key":"ticker","value":"ticker"},{"key":"objective","value":"keyword"}]},"value":""},"sort":[],"advancedSort":{"type":"Statistics","code":"price","key":"","value":"net_assets","direction":"DESC"},"include":{"statistics":{"limitTo":["price","fund_overview","cumulative_performance","annualized_performance"]},"disclaimers":{"limitTo":["etf_centre_mer_overview","etf_centre_mer_tooltip","annualized_distribution_yield","etf_centre_price_footer","etf_centre_nav_tooltip","etf_centre_performance_footer"]},"documents":{"joinSpec":[]}},"limit":200,"start":0,"culture":"en-CA","sourceCulture":"Default","translate":true,"preserveOriginal":true,"applyFormats":true,"disclaimers":true,"includeProperties":["asset_class","sub_asset_class","strategy","structure","region","fund_name","fund_name_seo","ticker","date_started","management_fee","management_expense_ratio","trading_currency","base_currency"]}"""  # noqa: E501

    if use_cache:
        r = bmo_etf_session.post(
            "https://api-us.fundpress.io/fund/searchEntity",
            data=payload,
            headers=headers,
            timeout=10,
        )

        if r.status_code == 200:
            results = r.json()
    if not use_cache:
        r = requests.post(
            "https://api-us.fundpress.io/fund/searchEntity",
            data=payload,
            headers=headers,
            timeout=10,
        )
        if r.status_code == 200:
            results = r.json()

    return results


def get_all_etfs(use_cache: bool = True) -> pd.DataFrame:
    """Parses the data dump into a DataFrame for a symbol directory"""

    etfs = get_data_dump(use_cache=use_cache)
    symbols = []
    names = []
    inception = []
    currency = []
    trading_currency = []
    management_fee = []
    mer = []
    asset_class = []
    region = []

    for i in range(0, len(etfs["values"])):  # type: ignore
        symbols.append(etfs["values"][i]["clientCode"])  # type: ignore
        names.append(etfs["values"][i]["properties_pub"]["fund_name"]["value"])  # type: ignore
        inception.append(etfs["values"][i]["properties_pub"]["date_started"]["value"])  # type: ignore
        currency.append(etfs["values"][i]["properties_pub"]["base_currency"]["value"])  # type: ignore
        trading_currency.append(etfs["values"][i]["properties_pub"]["trading_currency"]["value"])  # type: ignore
        management_fee.append(etfs["values"][i]["properties_pub"]["management_fee"]["value"])  # type: ignore
        mer.append(etfs["values"][i]["properties_pub"]["management_expense_ratio"]["value"])  # type: ignore
        asset_class.append(etfs["values"][i]["properties_pub"]["asset_class"]["value"])  # type: ignore
        region.append(etfs["values"][i]["properties_pub"]["region"]["value"])  # type: ignore

    results = pd.DataFrame(
        data=[
            symbols,
            names,
            asset_class,
            region,
            currency,
            trading_currency,
            management_fee,
            mer,
            inception,
        ]
    ).transpose()
    results.columns = [
        "symbol",
        "name",
        "asset_class",
        "region",
        "currency",
        "trading_currency",
        "fees",
        "mer",
        "inception_date",
    ]
    results["asset_class"] = (
        results["asset_class"]
        .astype(str)
        .str.replace("[", "")
        .str.replace("]", "")
        .str.replace("'", "")
        .str.replace(", ", ",")
    )
    results["region"] = (
        results["region"]
        .astype(str)
        .str.replace("[", "")
        .str.replace("]", "")
        .str.replace("'", "")
        .str.replace(", ", ",")
    )

    return (
        results.set_index("symbol").sort_values(by="mer", ascending=True).reset_index()
    )
