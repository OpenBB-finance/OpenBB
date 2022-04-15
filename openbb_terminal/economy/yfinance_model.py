""" Yahoo Finance Model """
__docformat__ = "numpy"

import logging

import pandas as pd
import yfinance as yf

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

INDICES = {
    "sp500": {"name": "S&P 500 Index", "ticker": "^GSPC"},
    "speup": {"name": "S&P Europe 350 Index", "ticker": "^SPEUP"},
    "sp400": {"name": "S&P 400 Mid Cap Index", "ticker": "^SP400"},
    "sp600": {"name": "S&P 600 Small Cap Index", "ticker": "^SP600"},
    "ny": {"name": "NYSE US 100 Index", "ticker": "^NY"},
    "nyse": {"name": "NYSE Composite Index", "ticker": "^NYA"},
    "amex": {"name": "NYSE-AMEX Composite Index", "ticker": "^XAX"},
    "nasdaq": {"name": "Nasdaq Composite Index", "ticker": "^IXIC"},
    "russell1000": {"name": "Russell 1000 Index", "ticker": "^RUI"},
    "russell2000": {"name": "Russell 2000 Index", "ticker": "^RUT"},
    "russell3000": {"name": "Russell 3000 Index", "ticker": "^RUA"},
    "russellvalue": {"name": "Russell 2000 Value Index", "ticker": "^RUJ"},
    "russellgrowth": {"name": "Russell 2000 Growth Index", "ticker": "^RUO"},
    "dja": {"name": "Dow Jones Composite Average Index", "ticker": "^DJA"},
    "dji": {"name": "Dow Jones Industrial Average Index", "ticker": "^DJI"},
    "tsx": {"name": "TSX Composite Index", "ticker": "^GSPTSE"},
    "ftse100": {"name": "FTSE Global 100 Index", "ticker": "^FTSE"},
    "ftse250": {"name": "FTSE Global 250 Index", "ticker": "^FTMC"},
    "ftse350": {"name": "FTSE Global 350 Index", "ticker": "^FTLC"},
    "ftai": {"name": "FTSE AIM All-Share Global Index", "ticker": "^FTAI"},
    "fteu1": {"name": "FTSE Eurotop 100 Index", "ticker": "^FTEU1"},
    "ftas": {"name": "UK FTSE All-Share Index", "ticker": "^FTAS"},
    "spuk": {"name": "S&P United Kingdom (PDS)", "ticker": "^SPUK"},
    "uk100": {"name": "CBOE UK 100 Index", "ticker": "^BUK100P"},
    "stoxx": {"name": "Zurich Stock Exchange STXE 600 PR.EUR", "ticker": "^STOXX"},
    "stoxx50e": {"name": "Zurich Stock Exchange ESTX 50 PR.EU", "ticker": "^STOXX50E"},
    "dax": {"name": "DAX Performance Index", "ticker": "^GDAXI"},
    "cac": {"name": "CAC Paris 40 Index", "ticker": "^FCHI"},
    "bel": {"name": "BEL 20 Brussels Exchange Index", "ticker": "^BFX"},
    "lisbon": {
        "name": "Lisbon Stock Exchange PSI All-Share Index GR",
        "ticker": "^BVLG",
    },
    "madrid": {"name": "IBEX 35 - Madrid Stock Exchange CATS - EUR", "ticker": "^IBEX"},
    "bse": {"name": "S&P Bombay SENSEX", "ticker": "^BSESN"},
    "bse-midcap": {"name": "S&P Bombay Mid Cap Index", "ticker": "BSE-MIDCAP.BO"},
    "bse-smallcap": {"name": "S&P Bombay Small Cap Index", "ticker": "BSE-SMLCAP.BO"},
    "tel-aviv": {"name": "Tel-Aviv 125 Index", "ticker": "^TA125.TA"},
    "russia": {"name": "MOEX Russia Index", "ticker": "IMOEX.ME"},
    "asx200": {"name": "S&P/ASX 200 Index", "ticker": "^AXJO"},
    "australia": {"name": "Australia All Ordinary Shares Index", "ticker": "^AORD"},
    "nz50": {"name": "S&P New Zealand 50 Index", "ticker": "^nz50"},
    "kospi": {"name": "KOSPI Composite Index", "ticker": "^KS11"},
    "nikkei": {"name": "Nikkei 255 Index", "ticker": "^N225"},
    "shanghai": {"name": "Shanghai Composite Index", "ticker": "000001.SS"},
    "shenzhen": {"name": "Shenzhen Component Index", "ticker": "399001.SZ"},
    "taiwan": {"name": "TSEC Weighted Index", "ticker": "^TWII"},
    "hang-seng": {"name": "Hang Seng Index", "ticker": "^HSI"},
    "jakarta": {"name": "Jakarta Composite Index", "ticker": "^JKSE"},
    "malaysia": {"name": "FTSE Bursa Malaysia KLCI", "ticker": "^KLSE"},
    "singapore": {"name": "STI Index - Singapore SGD", "ticker": "^STI"},
    "mexico": {"name": "IPC Mexico Index", "ticker": "^MXX"},
    "brazil": {"name": "IBOVESPA Sao Paulo Brazil Index", "ticker": "^BVSP"},
    "vix": {"name": "CBOE Volatility Index", "ticker": "^VIX"},
    "vin": {"name": "CBOE Near-Term VIX Index", "ticker": "^VIN"},
    "vvix": {"name": "CBOE VIX Volatility Index", "ticker": "^VVIX"},
    "shortvol": {"name": "CBOE Short VIX Futures Index", "ticker": "^SHORTVOL"},
    "vxn": {"name": "CBOE NASDAQ 100 Volatility Index", "ticker": "^VXN"},
    "gvz": {"name": "CBOE Gold Volatility Index", "ticker": "^GVZ"},
    "ovx": {"name": "CBOE Crude Oil Volatility Index", "ticker": "^OVX"},
    "dx-y": {"name": "US Dollar Index", "ticker": "DX-Y.NYB"},
    "tnx": {"name": "CBOE Interest Rate 10 Year T-Note", "ticker": "^TNX"},
    "tyx": {"name": "CBOE 30 year Treasury Yields", "ticker": "^TYX"},
    "irx": {"name": "CBOE 13 Week Treasury Bill", "ticker": "^IRX"},
    "sp500tr": {"name": "S&P 500 Total Return USD", "ticker": "^SP500TR"},
    "xsp": {"name": "S&P 500 Mini SPX Options Index", "ticker": "^XSP"},
    "sp-materials": {"name": "S&P 500 Materials Sector Index", "ticker": "^SP500-15"},
    "sp-industrials": {
        "name": "S&P 500 Industrials Sector Index",
        "ticker": "^SP500-20",
    },
    "sp-discretionary": {
        "name": "S&P 500 Consumer Discretionary Index",
        "ticker": "^SP500-25",
    },
    "sp-staples": {
        "name": "S&P 500 Consumer Staples Sector Index",
        "ticker": "^SP500-30",
    },
    "sp-health": {"name": "S&P 500 Health Care Sector Index", "ticker": "^SP500-35"},
    "sp-financials": {"name": "S&P 500 Financials Sector Index", "ticker": "^SP500-40"},
    "sp-it": {"name": "S&P 500 IT Sector Index", "ticker": "^SP500-45"},
    "sp-communications": {
        "name": "S&P 500 Communications Sector Index",
        "ticker": "^SP500-50",
    },
    "sp-utilities": {"name": "S&P 500 Utilities Sector Index", "ticker": "^SP500-55"},
    "sp-real_estate": {
        "name": "S&P 500 Real Estate Sector Index",
        "ticker": "^SP500-60",
    },
    "sp-airlines": {
        "name": "S&P 500 Airlines Industry Index",
        "ticker": "^SP500-203020",
    },
    "sp-tech_hardware": {
        "name": "S&P 500 Technology Hardware Industry",
        "ticker": "^SP500-452020",
    },
    "djt": {"name": "Dow Jones Transportation Average Index", "ticker": "^DJT"},
    "dju": {"name": "Dow Jones Utility Average Index", "ticker": "^DJU"},
    "ixch": {"name": "NASDAQ Health Care Index", "ticker": "^IXCH"},
    "ixtc": {"name": "NASDAQ Telecommunications Index", "ticker": "^IXTC"},
    "inds": {"name": "NASDAQ Industrial Index", "ticker": "^INDS"},
    "ixco": {"name": "NASDAQ Computer Index", "ticker": "^INCO"},
    "bank": {"name": "NASDAQ Bank Index", "ticker": "^BANK"},
    "tran": {"name": "NASDAQ Transportation Index", "ticker": "^TRAN"},
    "ice-auto": {"name": "ICE FactSet Global NextGen Auto Index", "ticker": "^ICEFSNA"},
    "ice-comm": {
        "name": "ICE FactSet Global NextGen Communications Index",
        "ticker": "^ICEFSNC",
    },
    "nyl": {"name": "NYSE World Leaders Index", "ticker": "^NYL"},
    "nyi": {"name": "NYSE International 100 Index", "ticker": "^NYI"},
    "nyy": {"name": "NYSE TMT Index", "ticker": "^NYY"},
    "xmi": {"name": "NYSE ARCA Major Market Index", "ticker": "^XMI"},
    "xoi": {"name": "NYSE ARCA Oil and Gas Index", "ticker": "^XOI"},
    "ixb": {"name": "NYSE Materials Select Sector Index", "ticker": "^IXB"},
    "pse": {"name": "NYSE ARCA Tech 100 Index", "ticker": "^PSE"},
    "xci": {"name": "NYSE ARCA Computer Tech Index", "ticker": "^XCI"},
    "xal": {"name": "NYSE ARCA Airline Index", "ticker": "^XAL"},
    "xtc": {
        "name": "NYSE ARCA North American Telecom Industry Index",
        "ticker": "^XTC",
    },
    "bxm": {"name": "CBOE Buy-Write Monthly Index", "ticker": "^BXM"},
    "sox": {"name": "PHLX Semiconductor Index", "ticker": "^SOX"},
    "xau": {"name": "PHLX Gold/Silver Index", "ticker": "^XAU"},
    "hgx": {"name": "PHLX Housing Sector Index", "ticker": "^HGX"},
    "osx": {"name": "PHLX Oil Services Sector Index", "ticker": "^OSX"},
    "uty": {"name": "PHLX Utility Sector Index", "ticker": "^UTY"},
    "w5000": {"name": "Wilshire 5000", "ticker": "^W5000"},
    "w5000flt": {"name": "Wilshire 5000 Float Adjusted Index", "ticker": "^W5000FLT"},
    "wgreit": {"name": "Wilshire Global REIT Index", "ticker": "^WGREIT"},
    "wgresi": {"name": "Wilshire Global Real Estate Sector Index", "ticker": "^WGRESI"},
    "wilreit": {"name": "Wilshire US REIT Index", "ticker": "^WILREIT"},
    "wilresi": {"name": "Wilshire US Real Estate Security Index", "ticker": "^WILRESI"},
}


@log_start_end(log=logger)
def get_index(
    index: str,
    interval: str = "1d",
    start_date: int = None,
    end_date: int = None,
    column: str = "Adj Close",
) -> pd.Series:
    """Obtain data on any index [Source: Yahoo Finance]

    Parameters
    ----------
    index: str
        The index you wish to collect data for.
    start_date : str
       the selected country
    end_date : bool
        The currency you wish to convert the data to.
    interval : str
        Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo or 3mo
        Intraday data cannot extend last 60 days
    column : str
        The column you wish to select, by default this is Adjusted Close.

    Returns
    ----------
    pd.Series
        A series with the requested index
    """
    if index.lower() in INDICES:
        ticker = INDICES[index.lower()]["ticker"]
    else:
        ticker = index

    index_data = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        interval=interval,
        progress=False,
        show_errors=False,
    )

    if column not in index_data.columns:
        console.print(
            f"The chosen column is not available for {ticker}. Please choose "
            f"between: {', '.join(index_data.columns)}\n"
        )
        return pd.Series()
    if index_data.empty or len(index_data) < 2:
        console.print(
            f"The chosen index {ticker}, returns no data. Please check if "
            f"there is any data available.\n"
        )
        return pd.Series()

    return index_data[column]
