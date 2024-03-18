"""SEC Helpers module"""

from datetime import timedelta
from io import BytesIO
from typing import Dict, List, Optional
from zipfile import ZipFile

import pandas as pd
import requests
import requests_cache
from openbb_core.app.utils import get_user_cache_directory
from openbb_sec.utils.definitions import HEADERS, QUARTERS, SEC_HEADERS, TAXONOMIES

cache_dir = get_user_cache_directory()

sec_session_companies = requests_cache.CachedSession(
    f"{cache_dir}/http/sec_companies", expire_after=timedelta(days=2)
)
sec_session_frames = requests_cache.CachedSession(
    f"{cache_dir}/http/sec_frames", expire_after=timedelta(days=2)
)
sec_session_ftd = requests_cache.CachedSession(f"{cache_dir}/http/sec_ftd")

sec_session_etf = requests_cache.CachedSession(f"{cache_dir}/http/sec_etf")

sec_session_company_filings = requests_cache.CachedSession(
    f"{cache_dir}/http/sec_company_filings", expire_after=timedelta(days=1)
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
        symbols = get_mf_and_etf_map(use_cache=use_cache).astype(str)
        if symbol not in symbols["symbol"].to_list():
            return ""

    cik = symbols[symbols["symbol"] == symbol]["cik"].iloc[0]
    cik_: str = ""
    temp = 10 - len(cik)
    for i in range(temp):
        cik_ = cik_ + "0"

    return str(cik_ + cik)


def cik_map(cik: int, use_cache: bool = True) -> str:
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
    companies = get_all_companies(use_cache=use_cache).astype(str)
    if _cik in companies["cik"].to_list():
        symbol = companies[companies["cik"] == _cik]["symbol"].iloc[0]
    else:
        return f"Error: CIK, {cik}, does not have a unique ticker."

    return symbol


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
    r = sec_session_companies.get(_url, headers=HEADERS, timeout=5)

    if r.status_code != 200:
        raise RuntimeError(f"Request failed with status code {r.status_code}")

    data = pd.read_html(r.content.decode())[0]["Name"].dropna()
    if len(data) > 0:
        data.iloc[0] = url if not query else url + "/"
        results = data.to_list()

    return results


def download_zip_file(url, symbol: Optional[str] = None) -> List[Dict]:
    """Download a list of files from URLs."""
    results = pd.DataFrame()
    r = sec_session_ftd.get(url, timeout=5, headers=HEADERS)
    if r.status_code == 200:
        try:
            data = pd.read_csv(BytesIO(r.content), compression="zip", sep="|")
            results = data.iloc[:-2]
        except ValueError:
            zip_file = ZipFile(BytesIO(r.content))
            file_list = [d.filename for d in zip_file.infolist()]
            for item in file_list:
                _file = pd.read_csv(
                    zip_file.open(item),
                    encoding="ISO-8859-1",
                    sep="|",
                    low_memory=False,
                    on_bad_lines="skip",
                )
                results = pd.concat([results, _file.iloc[:-2]])
        if "SETTLEMENT DATE" in results.columns:
            results = results.rename(
                columns={
                    "SETTLEMENT DATE": "date",
                    "SYMBOL": "symbol",
                    "CUSIP": "cusip",
                    "QUANTITY (FAILS)": "quantity",
                    "PRICE": "price",
                    "DESCRIPTION": "description",
                }
            )
            if symbol is not None:
                results = results[results["symbol"] == symbol]
            results["date"] = pd.to_datetime(results["date"], format="%Y%m%d").dt.date
            results["price"] = results["price"].mask(
                results["price"].str.contains(r"^\d+(?:\.\d+)?$", regex=True)
                == False,  # noqa
                None,
            )
            results["price"] = results["price"].astype(float)

    return results.reset_index(drop=True).to_dict("records")


def get_ftd_urls() -> Dict:
    """Get Fails-to-Deliver Data URLs."""

    results = {}
    position = None
    key = "title"
    value = "Fails-to-Deliver Data"

    r = requests.get("https://www.sec.gov/data.json", timeout=5, headers=SEC_HEADERS)
    if r.status_code != 200:
        raise RuntimeError(f"Request failed with status code {str(r.status_code)}")
    data = r.json()["dataset"]

    for index, d in enumerate(data):
        if key in d and d[key] == value:
            position = index
            break
    if position is not None:
        fails = data[position]["distribution"]
        key = "downloadURL"
        urls = list(map(lambda d: d[key], filter(lambda d: key in d, fails)))
        dates = [d[-11:-4] for d in urls]
        ftd_urls = pd.Series(index=dates, data=urls)
        ftd_urls.index = ftd_urls.index.str.replace("_", "")
        results = ftd_urls.to_dict()

    return results


def get_series_id(
    symbol: Optional[str] = None, cik: Optional[str] = None, use_cache: bool = True
):
    """
    This function maps the fund to the series and class IDs for validating the correct filing.
    For an exact match, use a symbol.
    """
    symbol = symbol if symbol else ""
    cik = cik if cik else ""

    results = pd.DataFrame()
    if not symbol and not cik:
        raise ValueError("Either symbol or cik must be provided.")

    target = symbol if symbol else cik
    choice = "cik" if not symbol else "symbol"
    funds = get_mf_and_etf_map(use_cache=use_cache).astype(str)

    results = funds[
        funds["cik"].str.contains(target, case=False)
        | funds["seriesId"].str.contains(target, case=False)
        | funds["classId"].str.contains(target, case=False)
        | funds["symbol"].str.contains(target, case=False)
    ]

    if len(results) > 0:
        results = results[results[choice if not symbol else choice] == target]

        return results


def get_nport_candidates(symbol: str, use_cache: bool = True) -> List[Dict]:
    """Gets a list of all NPORT-P filings for a given fund's symbol."""

    results = []
    _series_id = get_series_id(symbol, use_cache=use_cache)
    try:
        series_id = (
            symbol_map(symbol, use_cache)
            if _series_id is None or len(_series_id) == 0
            else _series_id["seriesId"].iloc[0]
        )
    except IndexError:
        raise ValueError("Fund not found for, the symbol: " + symbol)
    if series_id == "" or series_id is None:
        raise ValueError("Fund not found for, the symbol: " + symbol)

    url = f"https://efts.sec.gov/LATEST/search-index?q={series_id}&dateRange=all&forms=NPORT-P"

    def request_data(url: str = url, use_cache: bool = use_cache):
        r = (
            sec_session_companies.get(url, timeout=5, headers=HEADERS)
            if use_cache is True
            else requests.get(url, headers=HEADERS, timeout=5)
        )
        return r

    r = request_data(url, use_cache=use_cache)

    if r.status_code != 200:
        if r.status_code == 500:
            r = request_data()
            if r.status_code != 200:
                raise RuntimeError(
                    f"Request failed with status code {str(r.status_code)}"
                )
        if r.status_code not in (200, 500):
            raise RuntimeError(f"Request failed with status code {str(r.status_code)}")
    r_json = r.json()

    if "hits" in r_json and len(r_json["hits"]["hits"]) > 0:
        hits = r_json["hits"]["hits"]
        results = [
            {
                "name": d["_source"]["display_names"][0],
                "cik": d["_source"]["ciks"][0],
                "file_date": d["_source"]["file_date"],
                "period_ending": d["_source"]["period_ending"],
                "form_type": d["_source"]["form"],
                "primary_doc": f"https://www.sec.gov/Archives/edgar/data/{int(d['_source']['ciks'][0])}/{d['_id'].replace('-', '').replace(':', '/')}",  # noqa
            }
            for d in hits
        ]
    return (
        sorted(results, key=lambda d: d["file_date"], reverse=True)
        if len(results) > 0
        else results
    )
