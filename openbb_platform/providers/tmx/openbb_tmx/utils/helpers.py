"""TMX Helpers Module."""

# pylint: disable=too-many-lines,unused-argument,simplifiable-if-expression

from datetime import (
    date as dateType,
    datetime,
    time,
    timedelta,
)
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_tmx.utils import gql

if TYPE_CHECKING:
    from aiohttp_client_cache import SQLiteBackend
    from pandas import DataFrame

# Column map for ETFs.
COLUMNS_DICT = {
    "symbol": "symbol",
    "shortname": "short_name",
    "longname": "name",
    "fundfamily": "fund_family",
    "regions": "regions",
    "sectors": "sectors",
    "currency": "currency",
    "inceptiondate": "inception_date",
    "unitprice": "unit_price",
    "prevClose": "prev_close",
    "close": "close",
    "esg": "esg",
    "investmentstyle": "investment_style",
    "avgdailyvolume": "volume_avg_daily",
    "totalreturn1month": "return_1m",
    "totalreturn3month": "return_3m",
    "totalreturn1year": "return_1y",
    "totalreturn3year": "return_3y",
    "totalreturn5year": "return_5y",
    "totalreturnytd": "return_ytd",
    "totalreturnsinceinception": "return_from_inception",
    "distributionyeld": "distribution_yield",
    "dividendfrequency": "dividend_frequency",
    "pricetoearnings": "pe_ratio",
    "pricetobook": "pb_ratio",
    "assetclass": "asset_class_id",
    "prospectobjective": "investment_objectives",
    "beta1y": "beta_1y",
    "beta2y": "beta_2y",
    "beta3y": "beta_3y",
    "beta4y": "beta_4y",
    "beta5y": "beta_5y",
    "beta6y": "beta_6y",
    "beta7y": "beta_7y",
    "beta8y": "beta_8y",
    "beta9y": "beta_9y",
    "beta10y": "beta_10y",
    "beta11y": "beta_11y",
    "beta12y": "beta_12y",
    "beta13y": "beta_13y",
    "beta14y": "beta_14y",
    "beta15y": "beta_15y",
    "beta16y": "beta_16y",
    "beta17y": "beta_17y",
    "beta18y": "beta_18y",
    "beta19y": "beta_19y",
    "beta20y": "beta_20y",
    "avgvol30days": "volume_avg_30d",
    "aum": "aum",
    "top10holdings": "holdings_top10",
    "top10holdingsummary": "holdings_top10_summary",
    "totalreturn6month": "return_6m",
    "totalreturn10year": "return_10y",
    "managementfee": "management_fee",
    "altData": "additional_data",
}

# Additional Indices Supported By TMX for Snapshots Data.

NASDAQ_GIDS = {
    "^ADRAI": "BLDRS Asia 50 ADR Index Fund",
    "^ADRDI": "BLDRS Developed Markets 100 ADR Index Fund",
    "^ADREI": "BLDRS Emerging Markets 50 ADR Index Fund",
    "^ASRN": "AlphaSector Rotation Index",
    "^ASRX": "AlphaSector Rotation Total Return Index",
    "^AVSPY": "NASDAQ OMX Alpha AAPL vs. SPY Index",
    "^BIXR": "BetterInvesting 100 Total Return Index",
    "^BIXX": "BetterInvesting 100 Index",
    "^BKX": "KBW Bank Index",
    "^BSCBK": "NASDAQ BulletShares USD Corporate Bond 2020 Index",
    "^BSCBL": "NASDAQ BulletShares USD Corporate Bond 2021 Index",
    "^BSCBM": "NASDAQ BulletShares USD Corporate Bond 2022 Index",
    "^BSCBN": "NASDAQ BulletShares USD Corporate Bond 2023 Index",
    "^BSCBO": "NASDAQ BulletShares USD Corporate Bond 2024 Index",
    "^BSCBP": "NASDAQ BulletShares USD Corporate Bond 2025 Index",
    "^BSJKK": "NASDAQ BulletShares USD High Yield Corporate Bond",
    "^BSJKL": "NASDAQ BulletShares USD High Yield Corporate Bond",
    "^BSJKM": "NASDAQ BulletShares USD High Yield Corporate Bond",
    "^BSJKN": "NASDAQ BulletShares USD High Yield Corporate Bond",
    "^BXN": "CBOE NASDAQ-100 BuyWrite Index",
    "^CELS": "NASDAQ Clean Edge Green Energy Index",
    "^CEXX": "NASDAQ Clean Edge Green Energy Total Return Index",
    "^CHXN": "NASDAQ China Index",
    "^CIX100": "Cryptoindex.com",
    "^CND": "NASDAQ Canada",
    "^COMPX": "NASDAQ Composite",
    "^CVXLF": "NASDAQ OMX Alpha C vs. XLF Index",
    "^DFX": "PHLX Defense Sector",
    "^DIVQ": "NASDAQ Dividend Achievers Index",
    "^DOT": "TheStreet.com Internet Sector",
    "^DTEC": "NASDAQ Dallas Regional Chamber Index",
    "^DVQT": "NASDAQ Dividend Achievers Total Return Index",
    "^DWAFIR": "Dorsey Wright Fixed Income Allocation Index",
    "^DWANQFF": "Dorsey Wright Focus Five Index",
    "^EMCLOUD": "BVP Nasdaq Emerging Cloud Index",
    "^EPX": "SIG Oil Exploration & Production Index",
    "^ABAQ": "ABA Community Bank NASDAQ Index",
    "^EVSPY": "NASDAQ OMX Alpha EEM vs. SPY Index",
    "^GESPY": "NASDAQ OMX Alpha GE vs. SPY Index",
    "^GOOSY": "NASDAQ OMX Alpha GOOG vs. SPY Index",
    "^GVSPY": "NASDAQ OMX Alpha GLD vs. SPY Index",
    "^HAUL": "Wilder NASDAQ OMX Global Energy Efficient Transport Index",
    "^HGX": "PHLX Housing Sector",
    "^IBMSY": "NASDAQ OMX Alpha IBM vs. SPY Index",
    "^ILTI": "NASDAQ OMX AeA Illinois Tech Index",
    "^INTSY": "NASDAQ OMX Alpha INTC vs. SPY Index",
    "^ISRQ": "NASDAQ Israel Index",
    "^ISRX": "NASDAQ Israel Total Return",
    "^IVSPY": "NASDAQ OMX Alpha IBM vs. SPY Index",
    "^IXBK": "NASDAQ Bank",
    "^IXCO": "NASDAQ Computer",
    "^IXF": "NASDAQ Financial",
    "^IXFN": "NASDAQ Other Finance",
    "^IXHC": "NASDAQ Health Care Index",
    "^IXID": "NASDAQ Industrial",
    "^IXIS": "NASDAQ Insurance",
    "^IXTC": "NASDAQ Telecommunications",
    "^IXTR": "NASDAQ Transportation",
    "^JVSPY": "NASDAQ OMX Alpha INTC vs. SPY Index",
    "^KRX": "KBW Regional Banking Index",
    "^LVSPY": "NASDAQ OMX Alpha GE vs. SPY Index",
    "^MFX": "KBW Mortgage Finance Index",
    "^MRKSY": "NASDAQ OMX Alpha MRK vs. SPY Index",
    "^MSH": "Morgan Stanley Technology index",
    "^MXZ": "PHLX Medical Device Sector",
    "^NBI": "NASDAQ Biotechnology",
    "^NBIE": "NASDAQ Biotechnology Equal Weighted Index",
    "^NBIJR": "Nasdaq Junior Biotechnology Index",
    "^NCI": "Nasdaq Crypto Index",
    "^NDX": "NASDAQ 100 Index",
    "^NDXE": "The NASDAQ-100 Equal Weighted Index",
    "^NDXT": "NASDAQ-100 Technology Sector Index",
    "^NDXX": "NASDAQ-100 Ex-Tech Sector Index",
    "^NEUX": "NASDAQ OMX Europe Index",
    "^NGX": "Nasdaq Next Generation 100 Index",
    "^NQ7HANDLTL": "Nasdaq 7HANDL Index",
    "^NQCICLER": "NASDAQ Commodity Crude Oil Index ER",
    "^NQCIGCER": "NASDAQ Commodity Gold Index ER",
    "^NQCIHGER": "NASDAQ Commodity HG Copper Index ER",
    "^NQCINGER": "NASDAQ Commodity Natural Gas Index ER",
    "^NQCISIER": "NASDAQ Commodity Silver Index ER",
    "^NQCYBRT": "Nasdaq CTA Cybersecurity Index",
    "^NQGM": "NASDAQ Global Market Composite",
    "^NQGS": "NASDAQ Global Select Market Composite",
    "^NQH2O": "Nasdaq Veles California Water Index",
    "^NQMGUSL": "Nasdaq US Mega Cap Select Leaders Index",
    "^NQVWLCCT": "Nasdaq Victory US 500 Large Vol Wt L/C TR",
    "^NQVWLCT": "Nasdaq Victory US 500 Large Vol Wt TR",
    "^NQVWLDCT": "Nasdaq Victory US 100 Large High Div Vol Wt L/C TR",
    "^NQX": "NASDAQ-100 Reduced Value Index",
    "^NVSPY": "NASDAQ OMX Alpha MRK vs. SPY Index",
    "^NXTQ": "NASDAQ Q-50",
    "^OMXB10": "OMX Baltic 10",
    "^OMXC20": "OMX Copenhagen 20",
    "^OMXH25": "OMX Helsinki 25",
    "^OMXN40": "OMX Nordic 40",
    "^OMXS30": "OMX Stockholm 30 Index",
    "^ONEQI": "Fidelity Nasdaq Composite Index Tracking Stock",
    "^OSX": "PHLX Oil Service Sector",
    "^PRFEI": "PowerShares FTSE RAFI Energy Sector Portfolio",
    "^PRFFI": "PowerShares FTSE RAFI Financials Sector Portfolio",
    "^PRFGI": "PowerShares FTSE RAFI Consumer Goods Sector Portfolio",
    "^PRFHI": "PowerShares FTSE RAFI Health Care Sector Portfolio",
    "^PRFMI": "PowerShares FTSE RAFI Basic Materials Sector Portfolio",
    "^PRFNI": "PowerShares FTSE RAFI Industrials Sector Portfolio",
    "^PRFQI": "PowerShares FTSE RAFI Telecom & Tech Sector Portfolio",
    "^PRFSI": "PowerShares FTSE RAFI Consumer Goods Sector Portfolio",
    "^PRFUI": "PowerShares FTSE RAFI Utilities Sector Portfolio",
    "^PRFZI": "PowerShares FTSE RAFI US 1500 Small-Mid Portfolio",
    "^QAGR": "NASDAQ OMX Global Agriculture Index",
    "^QCLNI": "First Trust NASDAQ Clean Edge U.S. Liquid Series",
    "^QCOL": "NASDAQ OMX Global Coal Index",
    "^QGLD": "NASDAQ OMX Global Gold & Precious Metals Index",
    "^QGRI": "NASDAQ OMX Government Relief Index",
    "^QIRL": "NASDAQ OMX Ireland Index",
    "^QIV": "NASDAQ 100 After Hours Indicator",
    "^QMEA": "NASDAQ OMX Middle East North Africa Index",
    "^QMI": "NASDAQ 100 Pre Market Indicator",
    "^QNET": "NASDAQ Internet Index",
    "^QOMX": "NASDAQ OMX 100 Index",
    "^QQEWI": "First Trust NASDAQ 100 Equal Weighted Index Fund",
    "^NOCO": "NASDAQ OMX Carbon Excess Return Index",
    "^QQXTI": "First Trust NASDAQ 100 Ex-Technology Sector",
    "^QSTL": "NASDAQ OMX Global Steel Index",
    "^QTECI": "First Trust NASDAQ 100 Technology Sector",
    "^QWND": "NASDAQ OMX Clean Edge Global Wind Energy Index",
    "^RCMP": "NASDAQ Capital Market Composite Index",
    "^RXS": "PHLX Drug Sector",
    "^SHX": "PHLX Marine Shipping Sector",
    "^SOX": "PHLX Semiconductor Sector",
    "^SRVRSCPR": "Kelly Data Center and Tech Infrastructure Index",
    "^SVO": "SIG Energy MLP Index",
    "^TRAN": "Dow Transportation",
    "^TVSPY": "NASDAQ OMX Alpha TLT vs. SPY Index",
    "^UTY": "PHLX Utility Sector",
    "^UVSPY": "NASDAQ OMX Alpha GOOG vs. SPY Index",
    "^VOLNDX": "Volatility NASDAQ - 100",
    "^VOLQ": "Nasdaq-100 Volatility Index",
    "^WMTSY": "NASDAQ OMX Alpha WMT vs. SPY Index",
    "^WVSPY": "NASDAQ OMX Alpha WMT vs. SPY Index",
    "^XAU": "PHLX Gold/Silver Sector",
    "^XCM": "PHLX Chemicals Sector",
    "^XEX": "PHLX Europe Sector",
    "^XND": "Nasdaq-100 Micro Index",
}


def get_random_agent() -> str:
    """Get a random user agent."""
    # pylint: disable=import-outside-toplevel
    from random_user_agent.user_agent import UserAgent

    user_agent_rotator = UserAgent(limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent


def get_companies_backend():
    """Get the SQLiteBackend for the TMX companies."""
    # pylint: disable=import-outside-toplevel
    from aiohttp_client_cache import SQLiteBackend  # noqa
    from openbb_core.app.utils import get_user_cache_directory  # noqa

    # Only used for obtaining the directory of all valid company tickers.
    tmx_companies_backend = SQLiteBackend(
        f"{get_user_cache_directory()}/http/tmx_companies",
        expire_after=timedelta(days=2),
    )

    return tmx_companies_backend


def get_indices_backend():
    """Get the SQLiteBackend for the TMX indices."""
    # pylint: disable=import-outside-toplevel
    from aiohttp_client_cache import SQLiteBackend  # noqa
    from openbb_core.app.utils import get_user_cache_directory  # noqa

    # Only used for obtaining the directory of all valid indices.
    tmx_indices_backend = SQLiteBackend(
        f"{get_user_cache_directory()}/http/tmx_indices", expire_after=timedelta(days=1)
    )

    return tmx_indices_backend


async def response_callback(response, _: Any):
    """Use callback for HTTP Client Response."""
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        return await response.json()
    if "text" in content_type:
        return await response.text()
    return await response.read()


async def get_data_from_url(
    url: str,
    use_cache: bool = True,
    backend: Optional["SQLiteBackend"] = None,
    **kwargs: Any,
) -> Any:
    """Make an asynchronous HTTP request to a static file."""
    # pylint: disable=import-outside-toplevel
    from aiohttp_client_cache.session import CachedSession
    from openbb_core.provider.utils.helpers import amake_request

    data: Any = None
    if use_cache is True:
        async with CachedSession(cache=backend) as cached_session:
            try:
                response = await cached_session.get(url, **kwargs)
                data = await response_callback(response, None)
            finally:
                await cached_session.close()
    else:
        data = await amake_request(url, response_callback=response_callback, timeout=20)

    return data


async def get_data_from_gql(url: str, headers, data, **kwargs: Any) -> Any:
    """Make an asynchronous GraphQL request."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import amake_request

    response = await amake_request(
        url=url,
        method="POST",
        response_callback=response_callback,
        headers=headers,
        data=data,
        timeout=30,
    )

    return response


def replace_values_in_list_of_dicts(data):
    """Replace "NA" and "-" with None in a list of dictionaries."""
    for d in data:
        for k, v in d.items():
            if isinstance(v, dict):
                replace_values_in_list_of_dicts([v])  # Recurse into nested dictionary
            elif isinstance(v, list):
                for i in range(len(v)):  # pylint: disable=C0200
                    if isinstance(v[i], dict):
                        replace_values_in_list_of_dicts(
                            [v[i]]
                        )  # Recurse into nested dictionary in list
                    elif v[i] in ("NA", "-"):
                        v[i] = None  # Replace "NA" and "-" with None
            elif v in ("NA", "-"):
                d[k] = None  # Replace "NA" and "-" with None
    return data


def check_weekday(date) -> str:
    """Check if the input date is a weekday, and if not, returns the next weekday.

    Parameters
    ----------
    date: str
        The date to check in YYYY-MM-DD format.

    Returns
    -------
    str
        Date in YYYY-MM-DD format.  If the date is a weekend, returns the date of the next weekday.
    """
    # pylint: disable=import-outside-toplevel
    from pandas import to_datetime
    from pandas.tseries.holiday import next_workday

    if to_datetime(date).weekday() > 4:
        return next_workday(to_datetime(date)).strftime("%Y-%m-%d")
    return date


async def get_all_etfs(use_cache: bool = True) -> List[Dict]:
    """Get a summary of the TMX ETF universe.

    Returns
    -------
    Dict
        Dictionary with all TMX-listed ETFs.
    """
    # pylint: disable=import-outside-toplevel
    from aiohttp_client_cache import SQLiteBackend  # noqa
    from openbb_core.app.utils import get_user_cache_directory  # noqa
    from pandas import DataFrame  # noqa

    # Only used for obtaining the all ETFs JSON file.
    tmx_etfs_backend = SQLiteBackend(
        f"{get_user_cache_directory()}/http/tmx_etfs", expire_after=timedelta(hours=4)
    )

    url = "https://dgr53wu9i7rmp.cloudfront.net/etfs/etfs.json"

    response = await get_data_from_url(
        url, use_cache=use_cache, backend=tmx_etfs_backend
    )

    if not response or response is None:
        raise OpenBBError("There was a problem with the request. Could not get ETFs.")

    response = replace_values_in_list_of_dicts(response)

    etfs = DataFrame(response).rename(columns=COLUMNS_DICT)

    etfs = etfs.drop(
        columns=[
            "beta_2y",
            "beta_4y",
            "beta_6y",
            "beta_7y",
            "beta_8y",
            "beta_9y",
            "beta_11y",
            "beta_12y",
            "beta_13y",
            "beta_14y",
            "beta_16y",
            "beta_17y",
            "beta_18y",
            "beta_19y",
        ]
    )

    for i in etfs.index:
        etfs.loc[i, "fund_family"] = etfs.loc[i, "additional_data"].get("fundfamilyen", None)  # type: ignore
        etfs.loc[i, "website"] = etfs.loc[i, "additional_data"].get("websitefactsheeten", None)  # type: ignore
        etfs.loc[i, "mer"] = etfs.loc[i, "additional_data"].get("mer", None)  # type: ignore
    etfs = etfs.fillna("N/A").replace("N/A", None)

    return etfs.to_dict(orient="records")


async def get_tmx_tickers(
    exchange: Literal["tsx", "tsxv"] = "tsx", use_cache: bool = True
) -> Dict:
    """Get a dictionary of either TSX or TSX-V symbols and names."""
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame

    tsx_json_url = "https://www.tsx.com/json/company-directory/search"
    url = f"{tsx_json_url}/{exchange}/*"
    response = await get_data_from_url(
        url, use_cache=use_cache, backend=get_companies_backend()
    )
    data = (
        DataFrame.from_records(response["results"])[["symbol", "name"]]
        .set_index("symbol")
        .sort_index()
    )
    results = data.to_dict()["name"]
    return results


async def get_all_tmx_companies(use_cache: bool = True) -> Dict:
    """Merge TSX and TSX-V listings into a single dictionary."""
    all_tmx = {}
    tsx_tickers = await get_tmx_tickers(use_cache=use_cache)
    tsxv_tickers = await get_tmx_tickers("tsxv", use_cache=use_cache)
    all_tmx.update(tsxv_tickers)
    all_tmx.update(tsx_tickers)
    return all_tmx


async def get_all_options_tickers(use_cache: bool = True) -> "DataFrame":
    """Return a DataFrame with all valid ticker symbols."""
    # pylint: disable=import-outside-toplevel
    from io import StringIO  # noqa
    from pandas import concat, read_html  # noqa
    from openbb_core.provider.utils.helpers import to_snake_case  # noqa

    url = "https://www.m-x.ca/en/trading/data/options-list"

    r = await get_data_from_url(
        url, use_cache=use_cache, backend=get_companies_backend()
    )

    if r is None or r == []:
        raise OpenBBError("Error with the request")  # mypy: ignore

    options_listings = read_html(StringIO(r))
    listings = concat(options_listings)
    listings = listings.set_index("Option Symbol").drop_duplicates().sort_index()
    symbols = listings[:-1]
    symbols = symbols.fillna(value="")
    symbols["Underlying Symbol"] = (
        symbols["Underlying Symbol"].str.replace(" u", ".UN").str.replace("––", "")
    )
    symbols = symbols.reset_index()
    symbols.columns = [
        to_snake_case(col).replace("name_of_", "") for col in symbols.columns
    ]

    return symbols.set_index("option_symbol")


async def get_current_options(symbol: str, use_cache: bool = True) -> "DataFrame":
    """Get the current quotes for the complete options chain."""
    # pylint: disable=import-outside-toplevel
    from io import StringIO  # noqa
    from pandas import DataFrame, DatetimeIndex, concat, read_html, to_datetime  # noqa
    from openbb_core.provider.utils.helpers import to_snake_case  # noqa

    SYMBOLS = await get_all_options_tickers(use_cache=use_cache)
    data = DataFrame()
    symbol = symbol.upper()

    # Remove exchange  identifiers from the symbol.
    symbol = symbol.upper().replace("-", ".").replace(".TO", "").replace(".TSX", "")
    # Underlying symbol may have a different ticker symbol than the ticker used to lookup options.
    if len(SYMBOLS[SYMBOLS["underlying_symbol"].str.contains(symbol)]) == 1:
        symbol = SYMBOLS[SYMBOLS["underlying_symbol"] == symbol].index.values[0]
    # Check if the symbol has options trading.
    if symbol not in SYMBOLS.index and not SYMBOLS.empty:
        raise OpenBBError(
            f"The symbol, {symbol}, is not a valid listing or does not trade options."
        )

    QUOTES_URL = f"https://www.m-x.ca/en/trading/data/quotes?symbol={symbol}"

    cols = [
        "expiration",
        "strike",
        "bid",
        "ask",
        "lastTradePrice",
        "change",
        "openInterest",
        "volume",
        "optionType",
    ]

    r = await get_data_from_url(QUOTES_URL, use_cache=False)
    data = read_html(StringIO(r))[0]
    data = data.iloc[:-1]

    expirations = (
        data["Unnamed: 0_level_0"]["Expiry date"].astype(str).rename("expiration")
    )

    expirations = expirations.str.strip("(Weekly)")

    strikes = (
        data["Unnamed: 7_level_0"]
        .dropna()
        .sort_values("Strike")  # type: ignore
        .rename(columns={"Strike": "strike"})
    )

    calls = concat([expirations, strikes, data["Calls"]], axis=1)
    calls["expiration"] = DatetimeIndex(calls["expiration"]).astype(str)
    calls["optionType"] = "call"
    calls.columns = cols
    calls = calls.set_index(["expiration", "strike", "optionType"])

    puts = concat([expirations, strikes, data["Puts"]], axis=1)
    puts["expiration"] = DatetimeIndex(puts["expiration"]).astype(str)
    puts["optionType"] = "put"
    puts.columns = cols
    puts = puts.set_index(["expiration", "strike", "optionType"])

    chains = concat([calls, puts])
    chains["openInterest"] = chains["openInterest"].astype("int64")
    chains["volume"] = chains["volume"].astype("int64")
    chains["change"] = chains["change"].astype(float)
    chains["lastTradePrice"] = chains["lastTradePrice"].astype(float)
    chains["bid"] = chains["bid"].astype(float)
    chains["ask"] = chains["ask"].astype(float)
    chains = chains.sort_index()
    chains = chains.reset_index()
    now = datetime.now()
    temp = DatetimeIndex(chains.expiration)
    temp_ = (temp - now).days + 1  # type: ignore
    chains["dte"] = temp_

    # Create the standardized contract symbol.
    _strikes = chains["strike"]
    strikes = []
    for _strike in _strikes:
        _strike = str(_strike).split(".")
        front = "0" * (5 - len(_strike[0]))
        back = "0" * (3 - len(_strike[1]))
        strike = f"{front}{_strike[0]}{_strike[1]}{back}"
        strikes.append(str(strike))

    chains["strikes"] = strikes
    chains["contract_symbol"] = (
        symbol
        + " " * (6 - len(symbol))
        + to_datetime(chains["expiration"]).dt.strftime("%y%m%d")
        + (chains["optionType"].replace("call", "C").replace("put", "P"))
        + chains["strikes"]
    )
    chains.drop(columns=["strikes"], inplace=True)

    chains.columns = [to_snake_case(c) for c in chains.columns.to_list()]

    return chains


async def download_eod_chains(
    symbol: str, date: Optional[dateType] = None, use_cache: bool = False
) -> "DataFrame":
    """Download EOD chains data for a given symbol and date."""
    # pylint: disable=import-outside-toplevel
    from io import StringIO  # noqa
    import exchange_calendars as xcals  # noqa
    from pandas import DatetimeIndex, Timedelta, read_csv, to_datetime  # noqa
    from openbb_core.provider.utils.helpers import to_snake_case  # noqa

    symbol = symbol.upper()
    SYMBOLS = await get_all_options_tickers(use_cache=False)
    # Remove echange  identifiers from the symbol.
    symbol = symbol.upper().replace("-", ".").replace(".TO", "").replace(".TSX", "")

    # Underlying symbol may have a different ticker symbol than the ticker used to lookup options.
    if len(SYMBOLS[SYMBOLS["underlying_symbol"].str.contains(symbol)]) == 1:
        symbol = SYMBOLS[SYMBOLS["underlying_symbol"] == symbol].index.values[0]
    # Check if the symbol has options trading.
    if symbol not in SYMBOLS.index and not SYMBOLS.empty:
        raise OpenBBError(
            f"The symbol, {symbol}, is not a valid listing or does not trade options."
        )

    BASE_URL = "https://www.m-x.ca/en/trading/data/historical?symbol="

    cal = xcals.get_calendar("XTSE")

    if date is None:
        EOD_URL = BASE_URL + f"{symbol}" "&dnld=1#quotes"
    else:
        date = check_weekday(date)  # type: ignore
        if cal.is_session(date) is False:  # type: ignore
            date = (to_datetime(date) + timedelta(days=1)).strftime("%Y-%m-%d")  # type: ignore
        date = check_weekday(date)  # type: ignore
        if cal.is_session(date=date) is False:  # type: ignore
            date = (to_datetime(date) + timedelta(days=1)).strftime("%Y-%m-%d")  # type: ignore

        EOD_URL = (
            BASE_URL + f"{symbol}" "&from=" f"{date}" "&to=" f"{date}" "&dnld=1#quotes"
        )

    r = await get_data_from_url(EOD_URL, use_cache=use_cache)  # type: ignore

    if r is None:
        raise OpenBBError("Error with the request, no data was returned.")

    data = read_csv(StringIO(r))
    if data.empty:
        raise OpenBBError(
            f"No data found for, {symbol}, on, {date}."
            "The symbol may not have been listed, or traded options, before that date."
        )

    data["contractSymbol"] = data["Symbol"]

    data["optionType"] = data["Call/Put"].replace(0, "call").replace(1, "put")

    data = data.drop(
        columns=[
            "Symbol",
            "Class Symbol",
            "Root Symbol",
            "Underlying Symbol",
            "Ins. Type",
            "Call/Put",
        ]
    )

    cols = [
        "eod_date",
        "strike",
        "expiration",
        "closeBid",
        "closeAsk",
        "closeBidSize",
        "closeAskSize",
        "lastTradePrice",
        "volume",
        "prevClose",
        "change",
        "open",
        "high",
        "low",
        "totalValue",
        "transactions",
        "settlementPrice",
        "openInterest",
        "impliedVolatility",
        "contractSymbol",
        "optionType",
    ]

    data.columns = cols
    data["underlying_symbol"] = symbol + ":CA"
    data["expiration"] = to_datetime(data["expiration"], format="%Y-%m-%d")
    data["eod_date"] = to_datetime(data["eod_date"], format="%Y-%m-%d")
    data["impliedVolatility"] = 0.01 * data["impliedVolatility"]

    date_ = data["eod_date"]
    temp = DatetimeIndex(data.expiration)
    temp_ = temp - date_  # type: ignore
    data["dte"] = [Timedelta(_temp_).days for _temp_ in temp_]
    data = data.set_index(["expiration", "strike", "optionType"]).sort_index()
    data["eod_date"] = data["eod_date"].astype(str)
    underlying_price = data.iloc[-1]["lastTradePrice"]
    data["underlyingPrice"] = underlying_price
    data = data.reset_index()
    data = data[data["strike"] != 0]
    data["expiration"] = to_datetime(data["expiration"]).dt.strftime("%Y-%m-%d")

    data.columns = [to_snake_case(c) for c in data.columns.to_list()]

    return data


async def get_company_filings(
    symbol: str,
    start_date: Optional[str] = (datetime.now() - timedelta(days=30)).strftime(
        "%Y-%m-%d"
    ),
    end_date: Optional[str] = datetime.now().date().strftime("%Y-%m-%d"),
    limit: int = 50,
) -> List[Dict]:
    """Get company filings."""
    # pylint: disable=import-outside-toplevel
    import json

    user_agent = get_random_agent()
    results: List[Dict] = []
    symbol = symbol.upper().replace("-", ".").replace(".TO", "").replace(".TSX", "")

    payload = gql.get_company_filings_payload
    payload["variables"]["symbol"] = symbol
    payload["variables"]["fromDate"] = start_date
    payload["variables"]["toDate"] = end_date
    payload["variables"]["limit"] = limit
    url = "https://app-money.tmx.com/graphql"
    try:
        r = await get_data_from_gql(
            url=url,
            data=json.dumps(payload),
            headers={
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "Host": "app-money.tmx.com",
                "Origin": "https://money.tmx.com",
                "Referer": "https://money.tmx.com/",
                "locale": "en",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "TE": "trailers",
                "User-Agent": user_agent,
            },
        )
    except Exception as _e:
        raise OpenBBError(_e) from _e
    if r["data"]["filings"] is None:
        results = []
    results = r.get("data").get("filings")

    return results


async def get_daily_price_history(
    symbol: str,
    start_date: Optional[Union[str, dateType]] = None,
    end_date: Optional[Union[str, dateType]] = None,
    adjustment: Literal[
        "splits_only", "unadjusted", "splits_and_dividends"
    ] = "splits_only",
):
    """Get historical price data."""
    # pylint: disable=import-outside-toplevel
    import json  # noqa
    import asyncio  # noqa
    from dateutil import rrule  # noqa

    start_date = (
        datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(start_date, str)
        else start_date
    )
    end_date = (
        datetime.strptime(end_date, "%Y-%m-%d")
        if isinstance(end_date, str)
        else end_date
    )
    user_agent = get_random_agent()
    results: List[Dict] = []
    symbol = symbol.upper().replace("-", ".").replace(".TO", "").replace(".TSX", "")
    start_date = (
        (datetime.now() - timedelta(weeks=52)).date()
        if start_date is None
        else start_date
    )
    end_date = datetime.now() if end_date is None else end_date

    # Generate a list of dates from start_date to end_date with a frequency of 4 weeks
    dates = list(
        rrule.rrule(rrule.WEEKLY, interval=4, dtstart=start_date, until=end_date)
    )

    # Add end_date to the list if it's not there already
    if dates[-1] != end_date:
        dates.append(end_date)  # type: ignore

    # Create a list of 4-week chunks
    chunks = [
        (dates[i], dates[i + 1] - timedelta(days=1)) for i in range(len(dates) - 1)
    ]

    # Adjust the end date of the last chunk to be the final end date
    chunks[-1] = (chunks[-1][0], end_date)  # type: ignore

    async def create_task(start, end, results):
        """Create a task from a start and end date chunk."""
        payload = gql.get_company_price_history_payload.copy()
        payload["variables"]["adjusted"] = (
            False if adjustment == "unadjusted" else True  # noqa: SIM211
        )
        payload["variables"]["adjustmentType"] = (
            "SO" if adjustment == "splits_only" else None
        )
        payload["variables"]["end"] = end.strftime("%Y-%m-%d")
        payload["variables"]["start"] = start.strftime("%Y-%m-%d")
        payload["variables"]["symbol"] = symbol
        payload["variables"]["unadjusted"] = (
            True if adjustment == "unadjusted" else False  # noqa: SIM210
        )
        if payload["variables"]["adjustmentType"] is None:
            payload["variables"].pop("adjustmentType")
        url = "https://app-money.tmx.com/graphql"

        async def try_again():
            """Try again if it fails."""
            return await get_data_from_gql(
                method="POST",
                url=url,
                data=json.dumps(payload),
                headers={
                    "authority": "app-money.tmx.com",
                    "referer": f"https://money.tmx.com/en/quote/{symbol}",
                    "locale": "en",
                    "Content-Type": "application/json",
                    "User-Agent": user_agent,
                    "Accept": "*/*",
                },
                timeout=3,
            )

        try:
            data = await get_data_from_gql(
                method="POST",
                url=url,
                data=json.dumps(payload),
                headers={
                    "authority": "app-money.tmx.com",
                    "referer": f"https://money.tmx.com/en/quote/{symbol}",
                    "locale": "en",
                    "Content-Type": "application/json",
                    "User-Agent": user_agent,
                    "Accept": "*/*",
                },
                timeout=3,
            )
        except Exception:
            data = await try_again()

        if isinstance(data, str):
            data = await try_again()

        if data.get("data") and data["data"].get("getCompanyPriceHistory"):
            results.extend(data["data"].get("getCompanyPriceHistory"))

        return results

    tasks = [create_task(chunk[0], chunk[1], results) for chunk in chunks]

    await asyncio.gather(*tasks)

    results = [d for d in results if d["openPrice"] is not None]

    return sorted(results, key=lambda x: x["datetime"], reverse=False)


async def get_weekly_or_monthly_price_history(
    symbol: str,
    start_date: Optional[Union[str, dateType]] = None,
    end_date: Optional[Union[str, dateType]] = None,
    interval: Literal["month", "week"] = "month",
):
    """Get historical price data."""
    # pylint: disable=import-outside-toplevel
    import json

    if start_date:
        start_date = (
            datetime.strptime(start_date, "%Y-%m-%d")
            if isinstance(start_date, str)
            else start_date
        )
    if end_date:
        end_date = (
            datetime.strptime(end_date, "%Y-%m-%d")
            if isinstance(end_date, str)
            else end_date
        )
    user_agent = get_random_agent()
    results: List[Dict] = []
    symbol = symbol.upper().replace("-", ".").replace(".TO", "").replace(".TSX", "")
    start_date = (
        (datetime.now() - timedelta(weeks=52 * 100)).date()
        if start_date is None
        else start_date
    )
    end_date = datetime.now() if end_date is None else end_date

    payload = gql.get_timeseries_payload.copy()
    if "interval" in payload["variables"]:
        payload["variables"].pop("interval")
    if "startDateTime" in payload["variables"]:
        payload["variables"].pop("startDateTime")
    if "endDateTime" in payload["variables"]:
        payload["variables"].pop("endDateTime")
    payload["variables"]["symbol"] = symbol
    payload["variables"]["freq"] = interval
    payload["variables"]["end"] = (
        end_date.strftime("%Y-%m-%d") if isinstance(end_date, dateType) else end_date
    )
    payload["variables"]["start"] = (
        start_date.strftime("%Y-%m-%d")
        if isinstance(start_date, dateType)
        else start_date
    )
    url = "https://app-money.tmx.com/graphql"
    data = await get_data_from_gql(
        method="POST",
        url=url,
        data=json.dumps(payload),
        headers={
            "authority": "app-money.tmx.com",
            "referer": f"https://money.tmx.com/en/quote/{symbol}",
            "locale": "en",
            "Content-Type": "application/json",
            "User-Agent": user_agent,
            "Accept": "*/*",
        },
        timeout=3,
    )

    async def try_again():
        """Try again if the request fails."""
        return await get_data_from_gql(
            method="POST",
            url=url,
            data=json.dumps(payload),
            headers={
                "authority": "app-money.tmx.com",
                "referer": f"https://money.tmx.com/en/quote/{symbol}",
                "locale": "en",
                "Content-Type": "application/json",
                "User-Agent": user_agent,
                "Accept": "*/*",
            },
            timeout=3,
        )

    if isinstance(data, str):
        data = await try_again()

    if data.get("data") and data["data"].get("getTimeSeriesData"):
        results = data["data"].get("getTimeSeriesData")
        results = sorted(results, key=lambda x: x["dateTime"], reverse=False)
    return results


async def get_intraday_price_history(
    symbol: str,
    start_date: Optional[Union[str, dateType]] = None,
    end_date: Optional[Union[str, dateType]] = None,
    interval: Optional[int] = 1,
):
    """Get historical price data."""
    # pylint: disable=import-outside-toplevel
    import json  # noqa
    import asyncio  # noqa
    import pytz  # noqa
    from dateutil import rrule  # noqa

    if start_date:
        start_date = (
            datetime.strptime(start_date, "%Y-%m-%d")
            if isinstance(start_date, str)
            else start_date
        )
    if end_date:
        end_date = (
            datetime.strptime(end_date, "%Y-%m-%d")
            if isinstance(end_date, str)
            else end_date
        )
    user_agent = get_random_agent()
    results: List[Dict] = []
    symbol = symbol.upper().replace("-", ".").replace(".TO", "").replace(".TSX", "")
    start_date = (
        (datetime.now() - timedelta(weeks=4)).date()
        if start_date is None
        else start_date
    )
    end_date = datetime.now().date() if end_date is None else end_date
    # This is the first date of available intraday data.
    date_check = datetime(2022, 4, 12).date()
    start_date = max(start_date, date_check)
    if end_date < date_check:  # type: ignore
        end_date = datetime.now().date()
    # Generate a list of dates from start_date to end_date with a frequency of 3 weeks
    dates = list(
        rrule.rrule(rrule.WEEKLY, interval=4, dtstart=start_date, until=end_date)  # type: ignore
    )

    if dates[-1] != end_date:
        dates.append(end_date)  # type: ignore

    # Create a list of 4-week chunks
    chunks = [
        (dates[i], dates[i + 1] - timedelta(days=1)) for i in range(len(dates) - 1)
    ]

    # Adjust the end date of the last chunk to be the final end date
    chunks[-1] = (chunks[-1][0], end_date)  # type: ignore

    async def create_task(start, end, results):
        """Create a task from a start and end date chunk."""
        # Create a datetime object representing 9:30 AM on the date
        start_obj = datetime.combine(start, time(9, 30))
        end_obj = datetime.combine(end, time(16, 0))

        # Convert the datetime object to EST
        est = pytz.timezone("US/Eastern")
        start_obj_est = est.localize(start_obj)
        end_obj_est = est.localize(end_obj)

        # Convert the datetime object to a timestamp
        start_time = int(start_obj_est.timestamp())
        end_time = int(end_obj_est.timestamp())

        payload = gql.get_timeseries_payload.copy()
        payload["variables"]["interval"] = None
        if payload["variables"].get("start"):
            payload["variables"].pop("start")
        payload["variables"]["startDateTime"] = int(start_time)
        if payload["variables"].get("end"):
            payload["variables"].pop("end")
        payload["variables"]["endDateTime"] = int(end_time)
        payload["variables"]["interval"] = interval
        payload["variables"]["symbol"] = symbol
        if payload["variables"].get("freq"):
            payload["variables"].pop("freq")
        url = "https://app-money.tmx.com/graphql"
        data = await get_data_from_gql(
            method="POST",
            url=url,
            data=json.dumps(payload),
            headers={
                "authority": "app-money.tmx.com",
                "referer": f"https://money.tmx.com/en/quote/{symbol}",
                "locale": "en",
                "Content-Type": "application/json",
                "User-Agent": user_agent,
                "Accept": "*/*",
            },
            timeout=3,
        )

        async def try_again():
            """Try again if the request fails."""
            return await get_data_from_gql(
                method="POST",
                url=url,
                data=json.dumps(payload),
                headers={
                    "authority": "app-money.tmx.com",
                    "referer": f"https://money.tmx.com/en/quote/{symbol}",
                    "locale": "en",
                    "Content-Type": "application/json",
                    "User-Agent": user_agent,
                    "Accept": "*/*",
                },
                timeout=3,
            )

        if isinstance(data, str):
            data = await try_again()

        if data.get("data") and data["data"].get("getTimeSeriesData"):
            result = data["data"].get("getTimeSeriesData")
            results.extend(result)

        return results

    tasks = [create_task(chunk[0], chunk[1], results) for chunk in chunks]

    await asyncio.gather(*tasks)

    if len(results) > 0 and "dateTime" in results[0]:
        results = sorted(results, key=lambda x: x["dateTime"], reverse=False)

    return results


async def get_all_bonds(use_cache: bool = True) -> "DataFrame":
    """Get all bonds reference data published by CIRO.

    The complete list is approximately 70-100K securities.
    """
    # pylint: disable=import-outside-toplevel
    from aiohttp_client_cache import SQLiteBackend  # noqa
    from openbb_core.app.utils import get_user_cache_directory  # noqa
    from pandas import DataFrame  # noqa

    tmx_bonds_backend = SQLiteBackend(
        f"{get_user_cache_directory()}/http/tmx_bonds", expire_after=timedelta(days=1)
    )

    url = "https://bondtradedata.iiroc.ca/debtip/designatedbonds/list"
    response = await get_data_from_url(
        url, use_cache=use_cache, timeout=30, backend=tmx_bonds_backend
    )

    # Convert the response to a DataFrame and set the types for proper filtering in-fetcher.
    # This is done here because multiple functions might share this response object.
    bonds_data = (
        DataFrame.from_records(response)
        .replace("N/A", None)
        .sort_values(by=["lastTradedDate", "totalTrades"], ascending=False)
    )

    bonds_data["issuer"] = (
        bonds_data["issuer"].fillna("-").replace("-", None).astype(str)
    )

    int_columns = ["totalTrades", "secKey"]
    for column in int_columns:
        bonds_data[column] = bonds_data[column].astype(int)

    float_columns = [
        "lastPrice",
        "lowestPrice",
        "highestPrice",
        "lastYield",
        "couponRate",
    ]
    for column in float_columns:
        bonds_data[column] = bonds_data[column].astype(float)

    return bonds_data
