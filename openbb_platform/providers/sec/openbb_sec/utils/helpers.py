"""SEC Helpers module."""

# pylint: disable =unused-argument

from typing import Dict, List, Optional, Union

from aiohttp_client_cache import SQLiteBackend
from aiohttp_client_cache.session import CachedSession
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.utils import get_user_cache_directory
from openbb_core.provider.utils.helpers import amake_request, make_request
from openbb_sec.utils.definitions import HEADERS, SEC_HEADERS
from pandas import DataFrame


async def sec_callback(response, session):
    """Response callback for SEC requests."""
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        return await response.json()
    if "text/html" in content_type:
        return await response.text(encoding="latin-1")
    return await response.text()


async def get_all_companies(use_cache: bool = True) -> DataFrame:
    """Get all company names, tickers, and CIK numbers registered with the SEC.

    Companies are sorted by market cap.

    Returns
    -------
    DataFrame: Pandas DataFrame with columns for Symbol, Company Name, and CIK Number.

    Example
    -------
    >>> tickers = get_all_companies()
    """
    url = "https://www.sec.gov/files/company_tickers.json"
    response: Union[dict, List[dict]] = {}
    if use_cache is True:
        cache_dir = f"{get_user_cache_directory()}/http/sec_companies"
        async with CachedSession(
            cache=SQLiteBackend(cache_dir, expire_after=3600 * 24 * 2)
        ) as session:
            try:
                await session.delete_expired_responses()
                response = await amake_request(url, headers=SEC_HEADERS, session=session)  # type: ignore
            finally:
                await session.close()
    else:
        response = await amake_request(url, headers=SEC_HEADERS)  # type: ignore

    df = DataFrame(response).transpose()
    cols = ["cik", "symbol", "name"]
    df.columns = cols
    return df.astype(str)


async def get_all_ciks(use_cache: bool = True) -> DataFrame:
    """Get a list of entity names and their CIK number."""
    url = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"

    async def callback(response, session):
        """Response callback for CIK lookup data."""
        return await response.text(encoding="latin-1")

    response: Union[dict, List[dict], str] = {}
    if use_cache is True:
        cache_dir = f"{get_user_cache_directory()}/http/sec_ciks"
        async with CachedSession(
            cache=SQLiteBackend(cache_dir, expire_after=3600 * 24 * 2)
        ) as session:
            try:
                await session.delete_expired_responses()
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
    df = DataFrame(data_list)
    df = df.iloc[:, 0:2]
    cols = ["Institution", "CIK Number"]
    df.columns = cols
    df = df.dropna()

    return df.astype(str)


async def get_mf_and_etf_map(use_cache: bool = True) -> DataFrame:
    """Return the CIK number of a ticker symbol for querying the SEC API."""
    symbols = DataFrame()

    url = "https://www.sec.gov/files/company_tickers_mf.json"
    response: Union[dict, List[dict]] = {}
    if use_cache is True:
        cache_dir = f"{get_user_cache_directory()}/http/sec_mf_etf_map"
        async with CachedSession(
            cache=SQLiteBackend(cache_dir, expire_after=3600 * 24 * 2)
        ) as session:
            try:
                await session.delete_expired_responses()
                response = await amake_request(url, headers=SEC_HEADERS, session=session, response_callback=sec_callback)  # type: ignore
            finally:
                await session.close()
    else:
        response = await amake_request(url, headers=SEC_HEADERS, response_callback=sec_callback)  # type: ignore

    symbols = DataFrame(data=response["data"], columns=response["fields"])  # type: ignore

    return symbols.astype(str)


async def search_institutions(keyword: str, use_cache: bool = True) -> DataFrame:
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


def get_schema_filelist(query: str = "", url: str = "", use_cache: bool = True) -> List:
    """Get a list of schema files from the SEC website."""
    from pandas import read_html  # pylint: disable=import-outside-toplevel

    results: List = []
    url = url if url else f"https://xbrl.fasb.org/us-gaap/{query}"
    _url = url
    _url = url + "/" if query else _url
    response = make_request(_url)
    data = read_html(response.content)[0]["Name"].dropna()
    if len(data) > 0:
        data.iloc[0] = url if not query else url + "/"
        results = data.to_list()

    return results


async def download_zip_file(
    url, symbol: Optional[str] = None, use_cache: bool = True
) -> List[Dict]:
    """Download a list of files from URLs."""
    # pylint: disable=import-outside-toplevel
    from io import BytesIO
    from zipfile import ZipFile

    from pandas import concat, read_csv, to_datetime

    results = DataFrame()

    async def callback(response, session):
        """Response callback for ZIP file downloads."""
        return await response.read()

    response: Union[dict, List[dict]] = {}
    if use_cache is True:
        cache_dir = f"{get_user_cache_directory()}/http/sec_ftd"
        async with CachedSession(cache=SQLiteBackend(cache_dir)) as session:
            try:
                response = await amake_request(url, session=session, headers=HEADERS, response_callback=callback)  # type: ignore
            finally:
                await session.close()
    else:
        response = await amake_request(url, headers=HEADERS, response_callback=callback)  # type: ignore

    try:
        data = read_csv(BytesIO(response), compression="zip", sep="|")  # type: ignore
        results = data.iloc[:-2]
    except ValueError:
        zip_file = ZipFile(BytesIO(response))  # type: ignore
        file_list = [d.filename for d in zip_file.infolist()]
        for item in file_list:
            with zip_file.open(item) as _item:
                _file = read_csv(
                    _item,
                    encoding="ISO-8859-1",
                    sep="|",
                    low_memory=False,
                    on_bad_lines="skip",
                )
                results = concat([results, _file.iloc[:-2]])

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
        if symbol:
            results = results[results["symbol"] == symbol]
        results["date"] = to_datetime(results["date"], format="%Y%m%d").dt.date
        # Replace invalid decimal values with None
        results["price"] = results["price"].mask(
            ~results["price"].str.contains(r"^\d+(?:\.\d+)?$", regex=True), None
        )
        results["price"] = results["price"].astype(float)

    return results.reset_index(drop=True).to_dict("records")


async def get_ftd_urls() -> Dict:
    """Get Fails-to-Deliver Data URLs."""
    from pandas import Series  # pylint: disable=import-outside-toplevel

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
        ftd_urls = Series(index=dates, data=urls)
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

    results = DataFrame()
    if not symbol and not cik:
        raise OpenBBError("Either symbol or cik must be provided.")

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
        raise OpenBBError("Fund not found for, the symbol: " + symbol) from e
    if series_id == "" or series_id is None:
        raise OpenBBError("Fund not found for, the symbol: " + symbol)

    url = f"https://efts.sec.gov/LATEST/search-index?q={series_id}&dateRange=all&forms=NPORT-P"
    response: Union[dict, List[dict]] = {}
    if use_cache is True:
        cache_dir = f"{get_user_cache_directory()}/http/sec_etf"
        async with CachedSession(cache=SQLiteBackend(cache_dir)) as session:
            try:
                await session.delete_expired_responses()
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
