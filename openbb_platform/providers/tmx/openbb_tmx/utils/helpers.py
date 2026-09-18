"""TMX Helpers Module."""

# pylint: disable=too-many-lines,unused-argument,simplifiable-if-expression

from datetime import (
    date as dateType,
    datetime,
    time,
    timedelta,
)
from typing import TYPE_CHECKING, Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_tmx.utils import gql

if TYPE_CHECKING:
    from pandas import DataFrame

EARLIEST_SESSION = dateType(1970, 1, 1)

INTRADAY_EPOCH = dateType(2022, 4, 12)

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


async def get_data_from_url(url: str, use_cache: bool = True, **kwargs: Any) -> Any:
    """Fetch a URL through the shared TMX response cache.

    Parameters
    ----------
    url : str
        The URL to fetch.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    Any
        The decoded response body.
    """
    from openbb_tmx.utils.cache import amake_request

    kwargs.pop("backend", None)
    accept_type = kwargs.pop("accept_type", None)

    if accept_type is None:
        accept_type = "text" if _is_markup(url) else "json"

    return await amake_request(
        url, use_cache=use_cache, accept_type=accept_type, **kwargs
    )


def _is_markup(url: str) -> bool:
    """Report whether a URL serves markup or a delimited download."""
    return "m-x.ca" in url or "tsx.com/en/" in url


def replace_values_in_list_of_dicts(data):
    """Replace "NA" and "-" with None in a list of dictionaries."""
    for d in data:
        for k, v in d.items():
            if isinstance(v, dict):
                replace_values_in_list_of_dicts([v])
            elif isinstance(v, list):
                for i in range(len(v)):  # pylint: disable=C0200
                    if isinstance(v[i], dict):
                        replace_values_in_list_of_dicts([v[i]])
                    elif v[i] in ("NA", "-"):
                        v[i] = None
            elif v in ("NA", "-"):
                d[k] = None
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


async def get_all_etfs(use_cache: bool = True) -> list[dict]:
    """Get a summary of the TMX ETF universe.

    Returns
    -------
    Dict
        Dictionary with all TMX-listed ETFs.
    """
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame

    url = "https://dgr53wu9i7rmp.cloudfront.net/etfs/etfs.json"

    response = await get_data_from_url(url, use_cache=use_cache)

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
        extra = etfs.loc[i, "additional_data"] or {}
        etfs.loc[i, "fund_family"] = extra.get("fundfamilyen")
        etfs.loc[i, "website"] = extra.get("websitefactsheeten")
        etfs.loc[i, "mer"] = extra.get("mer")
        etfs.loc[i, "asset_class"] = extra.get("assetclassen")
        etfs.loc[i, "region"] = extra.get("regionen")
        etfs.loc[i, "index_fund"] = extra.get("indexfunden")
    etfs = purge_nulls(etfs)

    return etfs.to_dict(orient="records")


async def get_tmx_tickers(
    exchange: Literal["tsx", "tsxv"] = "tsx", use_cache: bool = True
) -> dict:
    """Get a dictionary of either TSX or TSX-V symbols and names."""
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame

    tsx_json_url = "https://www.tsx.com/json/company-directory/search"
    url = f"{tsx_json_url}/{exchange}/*"
    response = await get_data_from_url(url, use_cache=use_cache)
    data = (
        DataFrame.from_records(response["results"])[["symbol", "name"]]
        .set_index("symbol")
        .sort_index()
    )
    results = data.to_dict()["name"]
    return results


async def get_all_tmx_companies(use_cache: bool = True) -> dict:
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

    r = await get_data_from_url(url, use_cache=use_cache)

    if r is None or r == []:
        raise OpenBBError("Error with the request")  # mypy: ignore

    options_listings = read_html(
        StringIO(r), flavor="lxml", keep_default_na=False, na_values=[""]
    )
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

    symbol = symbol.upper().replace("-", ".").replace(".TO", "").replace(".TSX", "")
    if len(SYMBOLS[SYMBOLS["underlying_symbol"].str.contains(symbol)]) == 1:
        symbol = SYMBOLS[SYMBOLS["underlying_symbol"] == symbol].index.values[0]
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
    data = read_html(StringIO(r), flavor="lxml")[0]
    data = data.iloc[:-1]

    expirations = (
        data["Unnamed: 0_level_0"]["Expiry date"].astype(str).rename("expiration")
    )

    expirations = expirations.str.strip("(Weekly)")

    strikes = (
        data["Unnamed: 7_level_0"]
        .dropna()
        .sort_values("Strike")
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
    temp_ = (temp - now).days + 1
    chains["dte"] = temp_

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
    symbol: str, date: dateType | None = None, use_cache: bool = False
) -> "DataFrame":
    """Download EOD chains data for a given symbol and date."""
    # pylint: disable=import-outside-toplevel
    from io import StringIO  # noqa
    import exchange_calendars as xcals  # noqa
    from pandas import DatetimeIndex, Timedelta, read_csv, to_datetime  # noqa
    from openbb_core.provider.utils.helpers import to_snake_case  # noqa

    symbol = symbol.upper()
    SYMBOLS = await get_all_options_tickers(use_cache=False)
    symbol = symbol.upper().replace("-", ".").replace(".TO", "").replace(".TSX", "")

    if len(SYMBOLS[SYMBOLS["underlying_symbol"].str.contains(symbol)]) == 1:
        symbol = SYMBOLS[SYMBOLS["underlying_symbol"] == symbol].index.values[0]
    if symbol not in SYMBOLS.index and not SYMBOLS.empty:
        raise OpenBBError(
            f"The symbol, {symbol}, is not a valid listing or does not trade options."
        )

    BASE_URL = "https://www.m-x.ca/en/trading/data/historical?symbol="

    cal = xcals.get_calendar("XTSE")

    def _is_session(dt: str) -> bool:
        """Check if date is a trading session."""
        return to_datetime(dt) in cal.sessions

    if date is None:
        EOD_URL = BASE_URL + f"{symbol}&dnld=1#quotes"
    else:
        date = check_weekday(date)  # type: ignore
        if _is_session(date) is False:  # type: ignore
            date = (to_datetime(date) + timedelta(days=1)).strftime("%Y-%m-%d")  # type: ignore
        date = check_weekday(date)  # type: ignore
        if _is_session(date) is False:  # type: ignore
            date = (to_datetime(date) + timedelta(days=1)).strftime("%Y-%m-%d")  # type: ignore

        EOD_URL = BASE_URL + f"{symbol}&from={date}&to={date}&dnld=1#quotes"

    r = await get_data_from_url(EOD_URL, use_cache=use_cache)

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
    temp_ = temp - date_
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


def _as_date(value) -> "dateType | None":
    """Read a date out of a date, a datetime, or a 'YYYY-MM-DD' string.

    Parameters
    ----------
    value : date or datetime or str or None
        The value as supplied.

    Returns
    -------
    date or None
        The date, or None when nothing was supplied.
    """
    if not value:
        return None

    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d").date()

    return value.date() if isinstance(value, datetime) else value


def purge_nulls(frame):
    """Return a frame with every absent value as None.

    Parameters
    ----------
    frame : DataFrame
        The frame to purge.

    Returns
    -------
    DataFrame
        The frame, with NaN and the source's placeholders as None.
    """
    purged = frame.replace(["N/A", "-", ""], None)

    return purged.astype(object).where(purged.notna(), None)


ABSENT_URLS = {"", "nan", "none", "null", "n/a", "-"}


def normalize_url(value) -> str | None:
    """Return a website as an absolute URL, or None when none was published.

    Parameters
    ----------
    value : Any
        The website as published.

    Returns
    -------
    str or None
        The URL, prefixed with a scheme when the source left one off.
    """
    text = str(value or "").strip()

    if text.lower() in ABSENT_URLS:
        return None

    if "://" in text:
        return text

    return f"https://{text.lstrip('/')}"


def normalize_symbol(symbol: str) -> str:
    """Strip exchange identifiers from a TMX symbol.

    Parameters
    ----------
    symbol : str
        The symbol as supplied.

    Returns
    -------
    str
        The symbol in the form the TMX API expects.
    """
    symbol = symbol.strip().upper()

    if symbol[:1] in ("^", "/", "$") or ":" in symbol:
        return symbol

    return symbol.replace("-", ".").replace(".TO", "").replace(".TSX", "")


async def get_company_filings(
    symbol: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """Get the filings a company has published.

    Parameters
    ----------
    symbol : str
        The company symbol.
    start_date : str or None
        The first filing date to return.
    end_date : str or None
        The last filing date to return.
    limit : int
        The maximum number of filings to return.

    Returns
    -------
    list[dict]
        One entry per filing.
    """
    from openbb_tmx.utils.cache import amake_gql_request

    symbol = normalize_symbol(symbol)
    start_date = start_date or (datetime.now() - timedelta(days=30)).strftime(
        "%Y-%m-%d"
    )
    end_date = end_date or datetime.now().date().strftime("%Y-%m-%d")

    data = await amake_gql_request(
        "getCompanyFilings",
        gql.COMPANY_FILINGS,
        {
            "symbol": symbol,
            "fromDate": start_date,
            "toDate": end_date,
            "limit": limit,
        },
        symbol=symbol,
    )

    return (data or {}).get("filings") or []


async def get_daily_price_history(
    symbol: str,
    start_date: str | dateType | None = None,
    end_date: str | dateType | None = None,
    adjustment: Literal[
        "splits_only", "unadjusted", "splits_and_dividends"
    ] = "splits_only",
):
    """Get historical price data."""
    # pylint: disable=import-outside-toplevel
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
    results: list[dict] = []
    symbol = symbol.upper().replace("-", ".").replace(".TO", "").replace(".TSX", "")
    start_date = EARLIEST_SESSION if start_date is None else start_date
    end_date = datetime.now() if end_date is None else end_date

    dates = list(
        rrule.rrule(
            rrule.WEEKLY,
            interval=4,
            dtstart=start_date,
            until=end_date,
        )
    )

    if dates[-1] != end_date:
        dates.append(end_date)  # type: ignore

    chunks = [
        (dates[i], dates[i + 1] - timedelta(days=1)) for i in range(len(dates) - 1)
    ]

    chunks[-1] = (chunks[-1][0], end_date)  # type: ignore

    async def create_task(start, end, results):
        """Fetch one date chunk of daily history."""
        from openbb_tmx.utils.cache import amake_gql_request

        variables = {
            "symbol": symbol,
            "start": start.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "adjusted": adjustment != "unadjusted",
            "unadjusted": adjustment == "unadjusted",
        }

        if adjustment == "splits_only":
            variables["adjustmentType"] = "SO"

        data = await amake_gql_request(
            "getCompanyPriceHistory",
            gql.COMPANY_PRICE_HISTORY,
            variables,
            symbol=symbol,
        )

        if data and data.get("getCompanyPriceHistory"):
            results.extend(data["getCompanyPriceHistory"])

        return results

    tasks = [create_task(chunk[0], chunk[1], results) for chunk in chunks]

    await asyncio.gather(*tasks)

    results = [d for d in results if d["openPrice"] is not None]

    return sorted(results, key=lambda x: x["datetime"], reverse=False)


async def get_weekly_or_monthly_price_history(
    symbol: str,
    start_date: str | dateType | None = None,
    end_date: str | dateType | None = None,
    interval: Literal["month", "week"] = "month",
):
    """Get historical price data."""
    # pylint: disable=import-outside-toplevel

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
    results: list[dict] = []
    symbol = symbol.upper().replace("-", ".").replace(".TO", "").replace(".TSX", "")
    start_date = EARLIEST_SESSION if start_date is None else start_date
    end_date = datetime.now() if end_date is None else end_date

    from openbb_tmx.utils.cache import amake_gql_request

    data = await amake_gql_request(
        "getTimeSeriesData",
        gql.TIME_SERIES,
        {
            "symbol": symbol,
            "freq": interval,
            "start": (
                start_date.strftime("%Y-%m-%d")
                if isinstance(start_date, dateType)
                else start_date
            ),
            "end": (
                end_date.strftime("%Y-%m-%d")
                if isinstance(end_date, dateType)
                else end_date
            ),
        },
        symbol=symbol,
    )

    if data and data.get("getTimeSeriesData"):
        results = sorted(data["getTimeSeriesData"], key=lambda x: x["dateTime"])

    return results


async def get_intraday_price_history(
    symbol: str,
    start_date: str | dateType | None = None,
    end_date: str | dateType | None = None,
    interval: int | None = 1,
):
    """Get historical price data."""
    # pylint: disable=import-outside-toplevel
    import asyncio  # noqa
    import pytz  # noqa
    from dateutil import rrule  # noqa

    results: list[dict] = []
    symbol = normalize_symbol(symbol)
    start = max(_as_date(start_date) or INTRADAY_EPOCH, INTRADAY_EPOCH)
    end = _as_date(end_date) or datetime.now().date()

    if end < INTRADAY_EPOCH:
        end = datetime.now().date()

    start_date, end_date = start, end
    dates = list(
        rrule.rrule(
            rrule.WEEKLY,
            interval=4,
            dtstart=start_date,
            until=end_date,
        )
    )

    if dates[-1] != end_date:
        dates.append(end_date)  # type: ignore

    chunks = [
        (dates[i], dates[i + 1] - timedelta(days=1)) for i in range(len(dates) - 1)
    ]

    chunks[-1] = (chunks[-1][0], end_date)  # type: ignore

    async def create_task(start, end, results):
        """Create a task from a start and end date chunk."""
        start_obj = datetime.combine(start, time(9, 30))
        end_obj = datetime.combine(end, time(16, 0))

        est = pytz.timezone("US/Eastern")
        start_obj_est = est.localize(start_obj)
        end_obj_est = est.localize(end_obj)

        start_time = int(start_obj_est.timestamp())
        end_time = int(end_obj_est.timestamp())

        from openbb_tmx.utils.cache import amake_gql_request

        data = await amake_gql_request(
            "getTimeSeriesData",
            gql.TIME_SERIES,
            {
                "symbol": symbol,
                "interval": interval,
                "startDateTime": int(start_time),
                "endDateTime": int(end_time),
            },
            symbol=symbol,
        )

        if data and data.get("getTimeSeriesData"):
            results.extend(data["getTimeSeriesData"])

        return results

    tasks = [create_task(chunk[0], chunk[1], results) for chunk in chunks]

    await asyncio.gather(*tasks)

    if len(results) > 0 and "dateTime" in results[0]:
        results = sorted(results, key=lambda x: x["dateTime"], reverse=False)

    return results


CIRO_BONDS_URL = "https://bondtradedata.ciro.ca/debtip/designatedbonds/list"


def _bonds_cache_path():
    """Return today's parquet path for the CIRO bond master."""
    from pathlib import Path

    from openbb_core.app.utils import get_user_cache_directory

    directory = Path(get_user_cache_directory()) / "tmx"
    directory.mkdir(parents=True, exist_ok=True)

    return directory / f"ciro_bonds_{datetime.now().date().isoformat()}.parquet"


def _normalize_bonds(records: list[dict]) -> "DataFrame":
    """Type and sort the CIRO bond master."""
    from pandas import DataFrame, to_numeric

    bonds = (
        DataFrame.from_records(records)
        .replace("N/A", None)
        .sort_values(by=["lastTradedDate", "totalTrades"], ascending=False)
    )
    bonds["issuer"] = bonds["issuer"].fillna("-").replace("-", None).astype(str)

    for column in ("totalTrades", "secKey"):
        bonds[column] = to_numeric(bonds[column], errors="coerce").astype("Int64")

    for column in (
        "lastPrice",
        "lowestPrice",
        "highestPrice",
        "lastYield",
        "couponRate",
    ):
        bonds[column] = to_numeric(bonds[column], errors="coerce")

    return bonds


async def get_all_bonds(use_cache: bool = True) -> "DataFrame":
    """Get the complete bond reference master published by CIRO.

    Parameters
    ----------
    use_cache : bool
        Whether to read and write the on-disk parquet copy.

    Returns
    -------
    DataFrame
        Every designated bond, typed and sorted by last traded date.
    """
    from pandas import read_parquet

    from openbb_tmx.utils.curl_session import get_json

    path = _bonds_cache_path()

    if use_cache and path.exists():
        return read_parquet(path)

    bonds = _normalize_bonds(await get_json("ciro", CIRO_BONDS_URL))

    if use_cache:
        for stale in path.parent.glob("ciro_bonds_*.parquet"):
            if stale != path:
                stale.unlink(missing_ok=True)

        bonds.to_parquet(path, index=False)

    return bonds


async def get_timeseries_history(
    symbol: str,
    start_date=None,
    end_date=None,
    interval: str = "day",
) -> list[dict]:
    """Get daily, weekly, or monthly bars for any quotable instrument.

    Parameters
    ----------
    symbol : str
        The instrument symbol, including any market prefix or suffix.
    start_date : date or str or None
        The first date to return.
    end_date : date or str or None
        The last date to return.
    interval : str
        One of 'day', 'week', or 'month'.

    Returns
    -------
    list[dict]
        The bars, oldest first.
    """
    from openbb_tmx.utils.cache import amake_gql_request

    symbol = normalize_symbol(symbol)
    start_date = start_date or EARLIEST_SESSION
    end_date = end_date or datetime.now().date()
    data = await amake_gql_request(
        "getTimeSeriesData",
        gql.TIME_SERIES,
        {
            "symbol": symbol,
            "freq": interval,
            "start": (
                start_date.strftime("%Y-%m-%d")
                if isinstance(start_date, dateType)
                else str(start_date)
            ),
            "end": (
                end_date.strftime("%Y-%m-%d")
                if isinstance(end_date, dateType)
                else str(end_date)
            ),
        },
        symbol=symbol,
    )
    results = (data or {}).get("getTimeSeriesData") or []

    return sorted(results, key=lambda x: x["dateTime"])
