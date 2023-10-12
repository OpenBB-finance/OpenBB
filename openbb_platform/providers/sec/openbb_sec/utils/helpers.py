"""SEC Helpers module"""
from datetime import timedelta

import pandas as pd
import requests
import requests_cache

sec_session_companies = requests_cache.CachedSession(
    "OpenBB_SEC_Companies", expire_after=timedelta(days=7), use_cache_dir=True
)


SEC_HEADERS = {
    "User-Agent": "my real company name definitelynot@fakecompany.com",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov",
}


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


def search_companies(query: str, use_cache: bool = True) -> pd.DataFrame:
    """Search the SEC ticker list by keyword.  Partial words are accepted.
    Results are sorted by market cap and are case-insensitive.

    Parameters
    ----------
    query: str
        The keyword to search for. Partial words are accepted. Results are case-sensitive.

    Returns
    -------
    pd.DataFrame: Pandas DataFrame with the results.

    Examples
    --------
    >>> results = search_companies('Credit')

    >>> results = search_companies('TRUST')

    >>> results = search_companies('Trust')
    """

    companies = get_all_companies(use_cache=use_cache)
    hp = (
        companies["name"].str.contains(query, case=False)
        | companies["symbol"].str.contains(query, case=False)
        | companies["cik"].str.contains(query, case=False)
    )

    return companies[hp].reset_index(drop=True)


def symbol_map(symbol: str, use_cache: bool = True) -> str:
    """Returns a ticker's CIK number for querying the SEC API."""

    symbol = symbol.upper().replace(".", "-")
    symbols = get_all_companies(use_cache=use_cache)

    if symbol not in symbols["symbol"].to_list():
        raise ValueError(f"Ticker {symbol} not found.")

    cik = symbols[symbols["symbol"] == symbol]["cik"].iloc[0]
    cik_: str = ""
    temp = 10 - len(cik)
    for i in range(temp):
        cik_ = cik_ + "0"

    return str(cik_ + cik)


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
