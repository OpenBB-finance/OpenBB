"""Cboe Helpers"""

# pylint: disable=expression-not-assigned, unused-argument

from datetime import date as dateType
from io import BytesIO, StringIO
from typing import Any, List, Literal, Optional

from aiohttp_client_cache import SQLiteBackend
from aiohttp_client_cache.session import CachedSession
from openbb_core.app.utils import get_user_cache_directory
from openbb_core.provider.utils.client import ClientResponse
from openbb_core.provider.utils.helpers import amake_request, to_snake_case
from pandas import DataFrame, read_csv

TICKER_EXCEPTIONS = ["NDX", "RUT"]

CONSTITUENTS_EU = Literal[  # pylint: disable=invalid-name
    "BAT20P",
    "BBE20P",
    "BCH20P",
    "BCHM30P",
    "BDE40P",
    "BDEM50P",
    "BDES50P",
    "BDK25P",
    "BEP50P",
    "BEPACP",
    "BEPBUS",
    "BEPCNC",
    "BEPCONC",
    "BEPCONS",
    "BEPENGY",
    "BEPFIN",
    "BEPHLTH",
    "BEPIND",
    "BEPNEM",
    "BEPTEC",
    "BEPTEL",
    "BEPUTL",
    "BEPXUKP",
    "BES35P",
    "BEZ50P",
    "BEZACP",
    "BFI25P",
    "BFR40P",
    "BFRM20P",
    "BIE20P",
    "BIT40P",
    "BNL25P",
    "BNLM25P",
    "BNO25G",
    "BNORD40P",
    "BPT20P",
    "BSE30P",
    "BUK100P",
    "BUK250P",
    "BUK350P",
    "BUKAC",
    "BUKBISP",
    "BUKBUS",
    "BUKCNC",
    "BUKCONC",
    "BUKCONS",
    "BUKENGY",
    "BUKFIN",
    "BUKHI50P",
    "BUKHLTH",
    "BUKIND",
    "BUKLO50P",
    "BUKMINP",
    "BUKNEM",
    "BUKSC",
    "BUKTEC",
    "BUKTEL",
    "BUKUTL",
]

cache_dir = get_user_cache_directory()
backend = SQLiteBackend(f"{cache_dir}/http/cboe_directories", expire_after=3600 * 24)


async def response_callback(response: ClientResponse, _: Any):
    """Callback for HTTP Client Response."""
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        return await response.json()
    if "text" in content_type:
        return await response.text()
    return await response.read()


async def get_cboe_data(url, use_cache: bool = True, **kwargs) -> Any:
    """Generic Cboe HTTP request."""
    if use_cache is True:
        async with CachedSession(cache=backend) as cached_session:
            try:
                response = await cached_session.get(url, timeout=10, **kwargs)
                data = await response_callback(response, None)
            finally:
                await cached_session.close()
    else:
        data = await amake_request(url, response_callback=response_callback)

    return data


async def get_company_directory(use_cache: bool = True, **kwargs) -> DataFrame:
    """
    Get the US Company Directory for Cboe options. If use_cache is True,
    the data will be cached for 24 hours.

    Returns
    -------
    DataFrame: Pandas DataFrame of the Cboe listings directory
    """

    url = "https://www.cboe.com/us/options/symboldir/equity_index_options/?download=csv"

    results = await get_cboe_data(url, use_cache)

    response = BytesIO(results)

    directory = read_csv(response)

    directory = directory.rename(
        columns={
            " Stock Symbol": "symbol",
            " DPM Name": "dpm_name",
            " Post/Station": "post_station",
            "Company Name": "name",
        }
    ).set_index("symbol")

    return directory.astype(str)


async def get_index_directory(use_cache: bool = True, **kwargs) -> DataFrame:
    """
    Get the Cboe Index Directory. If use_cache is True,
    the data will be cached for 24 hours.

    Returns
    --------
    List[Dict]: A list of dictionaries containing the index information.
    """

    url = "https://cdn.cboe.com/api/global/us_indices/definitions/all_indices.json"

    results = await get_cboe_data(url, use_cache=use_cache)

    [result.pop("featured") for result in results]
    [result.pop("featured_order") for result in results]
    [result.pop("display") for result in results]
    results = DataFrame(results)
    results = results[results["source"] != "morningstar"]

    return results


async def list_futures(**kwargs) -> List[dict]:
    """List of CBOE futures and their underlying symbols.

    Returns
    --------
    pd.DataFrame
        Pandas DataFrame with results.
    """

    r = await get_cboe_data(
        "https://cdn.cboe.com/api/global/delayed_quotes/symbol_book/futures-roots.json"
    )
    data = r.get("data")
    [d.pop("sort_order") for d in data]

    return data


async def get_settlement_prices(
    settlement_date: Optional[dateType] = None,
    options: bool = False,
    archives: bool = False,
    final_settlement: bool = False,
    **kwargs,
) -> DataFrame:
    """Gets the settlement prices of CBOE futures.

    Parameters
    -----------
    settlement_date: Optional[date]
        The settlement date. Only valid for active contracts. [YYYY-MM-DD]
    options: bool
        If true, returns options on futures.
    archives: bool
        Settlement price archives for select years and products.  Overridden by other parameters.
    final_settlement: bool
        Final settlement prices for expired contracts.  Overrides archives.

    Returns
    -------
    DataFrame
        Pandas DataFrame with results.
    """
    url = ""
    if settlement_date is not None:
        url = (
            "https://www.cboe.com/us/futures/market_statistics"
            + f"/settlement/csv?dt={settlement_date}"
        )
        if options is True:
            url = (
                "https://www.cboe.com/us/futures/market_statistics/"
                + f"settlement/csv?options=t&dt={settlement_date}"
            )
    if settlement_date is None:
        url = "https://www.cboe.com/us/futures/market_statistics/settlement/csv"
        if options is True:
            url = "https://www.cboe.com/us/futures/market_statistics/settlement/csv?options=t"

    if final_settlement is True:
        url = "https://www.cboe.com/us/futures/market_statistics/final_settlement_prices/csv/"

    if archives is True:
        url = (
            "https://cdn.cboe.com/resources/futures/archive"
            + "/volume-and-price/CFE_FinalSettlement_Archive.csv"
        )

    response = await get_cboe_data(url, use_cache=False, **kwargs)

    data = read_csv(StringIO(response), index_col=None, parse_dates=True)

    if data.empty:
        return DataFrame()

    data.columns = [to_snake_case(c) for c in data.columns]
    data = data.rename(columns={"expiration_date": "expiration"})

    if len(data) > 0:
        return data

    return DataFrame()
