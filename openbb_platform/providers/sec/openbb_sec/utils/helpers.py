"""SEC Helpers module."""

# pylint: disable =unused-argument

from datetime import timedelta
from io import BytesIO
from typing import Dict, List, Optional, Union
from zipfile import ZipFile

import pandas as pd
import requests
import requests_cache
from aiohttp_client_cache import SQLiteBackend
from aiohttp_client_cache.session import CachedSession
from openbb_core.app.utils import get_user_cache_directory
from openbb_core.provider.utils.helpers import amake_request, make_request
from openbb_sec.utils.definitions import HEADERS, QUARTERS, SEC_HEADERS, TAXONOMIES


async def sec_callback(response, session):
    """Response callback for SEC requests."""
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        return await response.json()
    if "text/html" in content_type:
        return await response.text(encoding="latin-1")
    return await response.text()


async def get_all_companies(use_cache: bool = True) -> pd.DataFrame:
    """Get all company names, tickers, and CIK numbers registered with the SEC.

    Companies are sorted by market cap.

    Returns
    -------
    pd.DataFrame: Pandas DataFrame with columns for Symbol, Company Name, and CIK Number.

    Example
    -------
    >>> tickers = get_all_companies()
    """
    url = "https://www.sec.gov/files/company_tickers.json"

    if use_cache is True:
        cache_dir = f"{get_user_cache_directory()}/http/sec_companies"
        async with CachedSession(
            cache=SQLiteBackend(cache_dir, expire_after=3600 * 24 * 2)
        ) as session:
            try:
                response = await amake_request(url, headers=SEC_HEADERS, session=session)  # type: ignore
            finally:
                await session.close()
    else:
        response = await amake_request(url, headers=SEC_HEADERS)  # type: ignore

    df = pd.DataFrame(response).transpose()
    cols = ["cik", "symbol", "name"]
    df.columns = cols
    return df.astype(str)


async def get_all_ciks(use_cache: bool = True) -> pd.DataFrame:
    """Get a list of entity names and their CIK number."""
    url = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"

    async def callback(response, session):
        """Response callback for CIK lookup data."""
        return await response.text(encoding="latin-1")

    if use_cache is True:
        cache_dir = f"{get_user_cache_directory()}/http/sec_ciks"
        async with CachedSession(
            cache=SQLiteBackend(cache_dir, expire_after=3600 * 24 * 2)
        ) as session:
            try:
                response = await amake_request(url, headers=SEC_HEADERS, session=session, response_callback=callback)  # type: ignore
            finally:
                await session.close()
    else:
        response = await amake_request(url, headers=SEC_HEADERS, response_callback=callback)  # type: ignore
    data = response
    lines = data.split("\n")  # type: ignore
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

    return df.astype(str)


async def get_mf_and_etf_map(use_cache: bool = True) -> pd.DataFrame:
    """Return the CIK number of a ticker symbol for querying the SEC API."""
    symbols = pd.DataFrame()

    url = "https://www.sec.gov/files/company_tickers_mf.json"
    if use_cache is True:
        cache_dir = f"{get_user_cache_directory()}/http/sec_mf_etf_map"
        async with CachedSession(
            cache=SQLiteBackend(cache_dir, expire_after=3600 * 24 * 2)
        ) as session:
            try:
                response = await amake_request(url, headers=SEC_HEADERS, session=session, response_callback=sec_callback)  # type: ignore
            finally:
                await session.close()
    else:
        response = await amake_request(url, headers=SEC_HEADERS, response_callback=sec_callback)  # type: ignore

    symbols = pd.DataFrame(data=response["data"], columns=response["fields"])  # type: ignore

    return symbols.astype(str)


async def search_institutions(keyword: str, use_cache: bool = True) -> pd.DataFrame:
    """Search for an institution by name.  It is case-insensitive."""
    institutions = await get_all_ciks(use_cache=use_cache)
    hp = institutions["Institution"].str.contains(keyword, case=False)
    return institutions[hp]


async def symbol_map(symbol: str, use_cache: bool = True) -> str:
    """Return the CIK number of a ticker symbol for querying the SEC API."""
    symbol = symbol.upper().replace(".", "-")
    symbols = await get_all_companies(use_cache=use_cache)

    if symbol not in symbols["symbol"].to_list():
        symbols = await get_mf_and_etf_map(use_cache=use_cache)
        if symbol not in symbols["symbol"].to_list():
            return ""
    cik = symbols[symbols["symbol"] == symbol]["cik"].iloc[0]
    cik_: str = ""
    temp = 10 - len(cik)
    for i in range(temp):  # pylint: disable=W0612
        cik_ = cik_ + "0"

    return str(cik_ + cik)


async def cik_map(cik: Union[str, int], use_cache: bool = True) -> str:
    """Convert a CIK number to a ticker symbol.  Enter CIK as an integer with no leading zeros.

    Function is not meant for funds.

    Parameters
    ----------
    cik : int
        The CIK number to convert to a ticker symbol.

    Returns
    -------
    str: The ticker symbol associated with the CIK number.
    """
    _cik = str(cik) if isinstance(cik, int) else cik.lstrip("0")
    symbol = ""
    companies = await get_all_companies(use_cache=use_cache)
    if _cik in companies["cik"].to_list():
        symbol = companies[companies["cik"] == _cik]["symbol"].iloc[0]
    else:
        return f"Error: CIK, {_cik}, does not have a unique ticker."

    return symbol


def get_frame(  # pylint: disable =too-many-arguments
    year: int,
    quarter: Optional[QUARTERS] = None,
    taxonomy: TAXONOMIES = "us-gaap",
    units: str = "USD",
    fact: str = "Revenues",
    instantaneous: bool = False,
    use_cache: bool = True,
) -> Dict:
    """Get a frame of data for a given fact.

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
    sec_session_frames = requests_cache.CachedSession(
        f"{get_user_cache_directory()}/http/sec_frames", expire_after=timedelta(days=2)
    )
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


def get_schema_filelist(query: str = "", url: str = "", use_cache: bool = True) -> List:
    """Get a list of schema files from the SEC website."""
    results: List = []
    url = url if url else f"https://xbrl.fasb.org/us-gaap/{query}"
    _url = url
    _url = url + "/" if query else _url
    response = make_request(_url)
    data = pd.read_html(response.content)[0]["Name"].dropna()
    if len(data) > 0:
        data.iloc[0] = url if not query else url + "/"
        results = data.to_list()

    return results


async def download_zip_file(
    url, symbol: Optional[str] = None, use_cache: bool = True
) -> List[Dict]:
    """Download a list of files from URLs."""
    results = pd.DataFrame()

    async def callback(response, session):
        """Response callback for ZIP file downloads."""
        return await response.read()

    if use_cache is True:
        cache_dir = f"{get_user_cache_directory()}/http/sec_ftd"
        async with CachedSession(cache=SQLiteBackend(cache_dir)) as session:
            try:
                response = await amake_request(url, session=session, headers=HEADERS, response_callback=callback)  # type: ignore
            finally:
                await session.close()
    else:
        response = await amake_request(url, response_callback=callback)  # type: ignore

    try:
        data = pd.read_csv(BytesIO(response), compression="zip", sep="|")  # type: ignore
        results = data.iloc[:-2]
    except ValueError:
        zip_file = ZipFile(BytesIO(response))  # type: ignore
        file_list = [d.filename for d in zip_file.infolist()]
        for item in file_list:
            with zip_file.open(item) as _item:
                _file = pd.read_csv(
                    _item,
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
            results["price"].str.contains(  # pylint: disable=C0121
                r"^\d+(?:\.\d+)?$", regex=True
            )
            == False,  # noqa
            None,
        )
        results["price"] = results["price"].astype(float)

    return results.reset_index(drop=True).to_dict("records")


async def get_ftd_urls() -> Dict:
    """Get Fails-to-Deliver Data URLs."""
    results = {}
    position = None
    key = "title"
    value = "Fails-to-Deliver Data"

    r = await amake_request("https://www.sec.gov/data.json", headers=SEC_HEADERS)
    data = r.get("dataset", {})  # type: ignore

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


async def get_series_id(
    symbol: Optional[str] = None, cik: Optional[str] = None, use_cache: bool = True
):
    """Map the fund to the series and class IDs for validating the correct filing.

    For an exact match, use a symbol.
    """
    symbol = symbol if symbol else ""
    cik = cik if cik else ""

    results = pd.DataFrame()
    if not symbol and not cik:
        raise ValueError("Either symbol or cik must be provided.")

    target = symbol if symbol else cik
    choice = "cik" if not symbol else "symbol"
    funds = await get_mf_and_etf_map(use_cache=use_cache)

    results = funds[
        funds["cik"].str.contains(target, case=False)
        | funds["seriesId"].str.contains(target, case=False)
        | funds["classId"].str.contains(target, case=False)
        | funds["symbol"].str.contains(target, case=False)
    ]

    if len(results) > 0:
        results = results[results[choice if not symbol else choice] == target]

        return results


async def get_nport_candidates(symbol: str, use_cache: bool = True) -> List[Dict]:
    """Get a list of all NPORT-P filings for a given fund's symbol."""
    results = []
    _series_id = await get_series_id(symbol, use_cache=use_cache)
    try:
        series_id = (
            await symbol_map(symbol, use_cache)
            if _series_id is None or len(_series_id) == 0
            else _series_id["seriesId"].iloc[0]
        )
    except IndexError as e:
        raise ValueError("Fund not found for, the symbol: " + symbol) from e
    if series_id == "" or series_id is None:
        raise ValueError("Fund not found for, the symbol: " + symbol)

    url = f"https://efts.sec.gov/LATEST/search-index?q={series_id}&dateRange=all&forms=NPORT-P"

    if use_cache is True:
        cache_dir = f"{get_user_cache_directory()}/http/sec_etf"
        async with CachedSession(cache=SQLiteBackend(cache_dir)) as session:
            try:
                response = await amake_request(url, session=session, headers=HEADERS, response_callback=sec_callback)  # type: ignore
            finally:
                await session.close()
    else:
        response = await amake_request(url, response_callback=sec_callback)  # type: ignore

    if "hits" in response and len(response["hits"].get("hits")) > 0:  # type: ignore
        hits = response["hits"]["hits"]  # type: ignore
        results = [
            {
                "name": d["_source"]["display_names"][0],
                "cik": d["_source"]["ciks"][0],
                "file_date": d["_source"]["file_date"],
                "period_ending": d["_source"]["period_ending"],
                "form_type": d["_source"]["form"],
                "primary_doc": (
                    f"https://www.sec.gov/Archives/edgar/data/{int(d['_source']['ciks'][0])}"  # noqa
                    + f"/{d['_id'].replace('-', '').replace(':', '/')}"  # noqa
                ),
            }
            for d in hits
        ]
    return (
        sorted(results, key=lambda d: d["file_date"], reverse=True)
        if len(results) > 0
        else results
    )
