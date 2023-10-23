"""SEC Helpers module"""
from datetime import timedelta
from typing import Dict, List, Optional

import pandas as pd
import requests
import requests_cache
from openbb_sec.utils.definitions import HEADERS, QUARTERS, SEC_HEADERS, TAXONOMIES

sec_session_companies = requests_cache.CachedSession(
    "OpenBB_SEC_Companies", expire_after=timedelta(days=7), use_cache_dir=True
)
sec_session_frames = requests_cache.CachedSession(
    "OpenBB_SEC_Frames", expire_after=timedelta(days=30), use_cache_dir=True
)


def get_all_companies(use_cache: bool = True) -> pd.DataFrame:
    """Gets all company names, tickers, and CIK numbers registered with the SEC.
    Companies are sorted by market cap.

    Returns
    -------
    pd.DataFrame: Pandas DataFrame with columns for Symbol, Company Name, and CIK Number.

    Example
    -------
    >>> tickers = get_all_companies()
    """

    url = "https://www.sec.gov/files/company_tickers.json"

    r = (
        sec_session_companies.get(url, headers=SEC_HEADERS, timeout=5)
        if use_cache is True
        else requests.get(url, headers=SEC_HEADERS, timeout=5)
    )
    df = pd.DataFrame(r.json()).transpose()
    cols = ["cik", "symbol", "name"]
    df.columns = cols
    return df.astype(str)


def get_all_ciks(use_cache: bool = True) -> pd.DataFrame:
    """Gets a list of entity names and their CIK number."""

    HEADERS = {
        "User-Agent": "my real company name definitelynot@fakecompany.com",
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.sec.gov",
    }
    url = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"
    r = (
        sec_session_companies.get(url, headers=HEADERS, timeout=5)
        if use_cache is True
        else requests.get(url, headers=HEADERS, timeout=5)
    )
    data = r.text
    lines = data.split("\n")
    data_list = []
    delimiter = ":"
    for line in lines:
        row = line.split(delimiter)
        data_list.append(row)
    df = pd.DataFrame(data_list)
    df = df.iloc[:, 0:2]
    cols = ["Institution", "CIK Number"]
    df.columns = cols
    df = df.dropna()

    return df


def get_mf_and_etf_map(use_cache: bool = True) -> pd.DataFrame:
    """Returns the CIK number of a ticker symbol for querying the SEC API."""

    symbols = pd.DataFrame()

    url = "https://www.sec.gov/files/company_tickers_mf.json"
    r = (
        sec_session_companies.get(url, headers=SEC_HEADERS, timeout=5)
        if use_cache is True
        else requests.get(url, headers=SEC_HEADERS, timeout=5)
    )
    if r.status_code == 200:
        symbols = pd.DataFrame(data=r.json()["data"], columns=r.json()["fields"])

    return symbols


def search_institutions(keyword: str, use_cache: bool = True) -> pd.DataFrame:
    """Search for an institution by name.  It is case-insensitive."""
    institutions = get_all_ciks(use_cache=use_cache)
    hp = institutions["Institution"].str.contains(keyword, case=False)
    return institutions[hp].astype(str)


def symbol_map(symbol: str, use_cache: bool = True) -> str:
    """Returns the CIK number of a ticker symbol for querying the SEC API."""

    symbol = symbol.upper().replace(".", "-")
    symbols = get_all_companies(use_cache=use_cache)

    if symbol not in symbols["symbol"].to_list():
        symbols = get_mf_and_etf_map().astype(str)
        if symbol not in symbols["symbol"].to_list():
            return ""

    cik = symbols[symbols["symbol"] == symbol]["cik"].iloc[0]
    cik_: str = ""
    temp = 10 - len(cik)
    for i in range(temp):
        cik_ = cik_ + "0"

    return str(cik_ + cik)


def cik_map(cik: int) -> str:
    """
    Converts a CIK number to a ticker symbol.  Enter CIK as an integer with no leading zeros.

    Function is not meant for funds.

    Parameters
    ----------
    cik : int
        The CIK number to convert to a ticker symbol.

    Returns
    -------
    str: The ticker symbol associated with the CIK number.
    """
    _cik = str(cik)
    symbol = ""
    companies = get_all_companies().astype(str)
    if _cik in companies["cik"].to_list():
        symbol = companies[companies["cik"] == _cik]["symbol"].iloc[0]
    else:
        return f"Error: CIK, {cik}, does not have a unique ticker."

    return symbol


def catching_diff_url_formats(ftd_urls: list) -> list:
    """Catches if URL for SEC data is one of the few URLS that are not in the
    standard format. Catches are for either specific date ranges that have a different
    format or singular URLs that have a different format.

    Parameters
    ----------
    ftd_urls : list
        list of urls of sec data

    Returns
    -------
    list
        list of ftd urls
    """
    feb_mar_apr_catch = ["202002", "202003", "202004"]
    for i, ftd_url in enumerate(ftd_urls):
        # URLs with dates prior to the first half of June 2017 have different formats
        if int(ftd_url[58:64]) < 201706 or "201706a" in ftd_url:
            ftd_urls[i] = ftd_url.replace(
                "fails-deliver-data",
                "frequently-requested-foia-document-fails-deliver-data",
            )
        # URLs between february, march, and april of 2020 have different formats
        elif any(x in ftd_urls[i] for x in feb_mar_apr_catch):
            ftd_urls[i] = ftd_url.replace(
                "data/fails-deliver-data", "node/add/data_distribution"
            )
        # First half of october 2019 has a different format
        elif (
            ftd_url
            == "https://www.sec.gov/files/data/fails-deliver-data/cnsfails201910a.zip"
        ):
            ftd_urls[
                i
            ] = "https://www.sec.gov/files/data/fails-deliver-data/cnsfails201910a_0.zip"

    return ftd_urls


def get_frame(
    year: int,
    quarter: Optional[QUARTERS] = None,
    taxonomy: TAXONOMIES = "us-gaap",
    units: str = "USD",
    fact: str = "Revenues",
    instantaneous: bool = False,
    use_cache: bool = True,
) -> Dict:
    """
    The xbrl/frames API aggregates one fact for each reporting entity
    that is last filed that most closely fits the calendrical period requested.

    This API supports for annual, quarterly and instantaneous data:

    https://data.sec.gov/api/xbrl/frames/us-gaap/AccountsPayableCurrent/USD/CY2019Q1I.json

    Where the units of measure specified in the XBRL contains a numerator and a denominator,
    these are separated by “-per-” such as “USD-per-shares”. Note that the default unit in XBRL is “pure”.

    CY####Q# for quarterly data (duration 91 days +/- 30 days).
    Because company financial calendars can start and end on any month or day and even change in length from quarter to
    quarter according to the day of the week, the frame data is assembled by the dates that best align with a calendar
    quarter or year. Data users should be mindful different reporting start and end dates for facts contained in a frame.

    Example facts:
    Revenues
    GrossProfit
    CostOfRevenue
    DividendsCash
    DistributedEarnings
    AccountsPayableCurrent
    OperatingExpenses
    OperatingIncomeLoss
    NoninterestIncome
    InterestAndDebtExpense
    IncomeTaxExpenseBenefit
    NetIncomeLoss

    Facts where units are, "shares":
    WeightedAverageNumberOfDilutedSharesOutstanding
    """

    if fact in ["WeightedAverageNumberOfDilutedSharesOutstanding"]:
        units = "shares"

    url = f"https://data.sec.gov/api/xbrl/frames/{taxonomy}/{fact}/{units}/CY{year}"

    if quarter:
        url = url + f"Q{quarter}"

    if instantaneous:
        url = url + "I"
    url = url + ".json"
    r = (
        requests.get(url, headers=HEADERS, timeout=5)
        if use_cache is False
        else sec_session_frames.get(url, headers=HEADERS, timeout=5)
    )

    if r.status_code != 200:
        raise RuntimeError(f"Request failed with status code {r.status_code}")

    response = r.json()

    data = sorted(response["data"], key=lambda x: x["val"], reverse=True)
    metadata = {
        "frame": response["ccp"],
        "tag": response["tag"],
        "label": response["label"],
        "description": response["description"],
        "taxonomy": response["taxonomy"],
        "unit": response["uom"],
        "count": response["pts"],
    }

    results = {"metadata": metadata, "data": data}

    return results


def get_schema_filelist(query: str = "", url: str = "") -> List:
    results: List = []
    url = url if url else f"https://xbrl.fasb.org/us-gaap/{query}"
    _url = url
    _url = url + "/" if query else _url
    r = sec_session_frames.get(_url, headers=HEADERS, timeout=5)

    if r.status_code != 200:
        raise RuntimeError(f"Request failed with status code {r.status_code}")

    data = pd.read_html(r.content.decode())[0]["Name"].dropna()
    if len(data) > 0:
        data.iloc[0] = url if not query else url + "/"
        results = data.to_list()

    return results
