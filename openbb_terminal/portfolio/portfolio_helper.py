"""Portfolio Helper"""
__docformat__ = "numpy"

from datetime import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import pandas as pd

# pylint: disable=too-many-return-statements

BENCHMARK_LIST = {
    "SPDR S&P 500 ETF Trust (SPY)": "SPY",
    "iShares Core S&P 500 ETF (IVV)": "IVV",
    "Vanguard Total Stock Market ETF (VTI)": "VTI",
    "Vanguard S&P 500 ETF (VOO)": "VOO",
    "Invesco QQQ Trust (QQQ)": "QQQ",
    "Vanguard Value ETF (VTV)": "VTV",
    "Vanguard FTSE Developed Markets ETF (VEA)": "VEA",
    "iShares Core MSCI EAFE ETF (IEFA)": "IEFA",
    "iShares Core U.S. Aggregate Bond ETF (AGG)": "AGG",
    "Vanguard Total Bond Market ETF (BND)": "BND",
    "Vanguard FTSE Emerging Markets ETF (VWO)": "VWO",
    "Vanguard Growth ETF (VUG)": "VUG",
    "iShares Core MSCI Emerging Markets ETF (IEMG)": "IEMG",
    "iShares Core S&P Small-Cap ETF (IJR)": "IJR",
    "SPDR Gold Shares (GLD)": "GLD",
    "iShares Russell 1000 Growth ETF (IWF)": "IWF",
    "iShares Core S&P Mid-Cap ETF (IJH)": "IJH",
    "Vanguard Dividend Appreciation ETF (VIG)": "VIG",
    "iShares Russell 2000 ETF (IWM)": "IWM",
    "iShares Russell 1000 Value ETF (IWD)": "IWD",
    "Vanguard Mid-Cap ETF (VO)": "VO",
    "iShares MSCI EAFE ETF (EFA)": "EFA",
    "Vanguard Total International Stock ETF (VXUS)": "VXUS",
    "Vanguard Information Technology ETF (VGT)": "VGT",
    "Vanguard High Dividend Yield Index ETF (VYM)": "VYM",
    "Vanguard Total International Bond ETF (BNDX)": "BNDX",
    "Vanguard Real Estate ETF (VNQ)": "VNQ",
    "Vanguard Small Cap ETF (VB)": "VB",
    "Technology Select Sector SPDR Fund (XLK)": "XLK",
    "iShares Core S&P Total U.S. Stock Market ETF (ITOT)": "ITOT",
    "Vanguard Intermediate-Term Corporate Bond ETF (VCIT)": "VCIT",
    "Vanguard Short-Term Corporate Bond ETF (VCSH)": "VCSH",
    "Energy Select Sector SPDR Fund (XLE)": "XLE",
    "Health Care Select Sector SPDR Fund (XLV)": "XLV",
    "Vanguard Short-Term Bond ETF (BSV)": "BSV",
    "Financial Select Sector SPDR Fund (XLF)": "XLF",
    "Schwab US Dividend Equity ETF (SCHD)": "SCHD",
    "Invesco S&P 500® Equal Weight ETF (RSP)": "RSP",
    "iShares iBoxx $ Investment Grade Corporate Bond ETF (LQD)": "LQD",
    "iShares S&P 500 Growth ETF (IVW)": "IVW",
    "Vanguard FTSE All-World ex-US Index Fund (VEU)": "VEU",
    "iShares TIPS Bond ETF (TIP)": "TIP",
    "iShares Gold Trust (IAU)": "IAU",
    "Schwab U.S. Large-Cap ETF (SCHX)": "SCHX",
    "iShares Core MSCI Total International Stock ETF (IXUS)": "IXUS",
    "iShares Russell Midcap ETF (IWR)": "IWR",
    "iShares Russell 1000 ETF (IWB)": "IWB",
    "SPDR Dow Jones Industrial Average ETF Trust (DIA)": "DIA",
    "iShares MSCI Emerging Markets ETF (EEM)": "EEM",
    "iShares MSCI USA Min Vol Factor ETF (USMV)": "USMV",
    "Schwab International Equity ETF (SCHF)": "SCHF",
    "iShares S&P 500 Value ETF (IVE)": "IVE",
    "iShares National Muni Bond ETF (MUB)": "MUB",
    "Vanguard Large Cap ETF (VV)": "VV",
    "Vanguard Small Cap Value ETF (VBR)": "VBR",
    "iShares ESG Aware MSCI USA ETF (ESGU)": "ESGU",
    "Vanguard Total World Stock ETF (VT)": "VT",
    "iShares Core Dividend Growth ETF (DGRO)": "DGRO",
    "iShares 1-3 Year Treasury Bond ETF (SHY)": "SHY",
    "iShares Select Dividend ETF (DVY)": "DVY",
    "iShares MSCI USA Quality Factor ETF (QUAL)": "QUAL",
    "Schwab U.S. Broad Market ETF (SCHB)": "SCHB",
    "iShares MBS ETF (MBB)": "MBB",
    "SPDR S&P Dividend ETF (SDY)": "SDY",
    "iShares 1-5 Year Investment Grade Corporate Bond ETF (IGSB)": "IGSB",
    "Vanguard Short-Term Inflation-Protected Securities ETF (VTIP)": "VTIP",
    "JPMorgan Ultra-Short Income ETF (JPST)": "JPST",
    "iShares 20+ Year Treasury Bond ETF (TLT)": "TLT",
    "iShares MSCI ACWI ETF (ACWI)": "ACWI",
    "SPDR S&P Midcap 400 ETF Trust (MDY)": "MDY",
    "iShares Core Total USD Bond Market ETF (IUSB)": "IUSB",
    "iShares Short Treasury Bond ETF (SHV)": "SHV",
    "Vanguard FTSE Europe ETF (VGK)": "VGK",
    "Consumer Discretionary Select Sector SPDR Fund (XLY)": "XLY",
    "SPDR Bloomberg 1-3 Month T-Bill ETF (BIL)": "BIL",
    "iShares U.S. Treasury Bond ETF (GOVT)": "GOVT",
    "Vanguard Health Care ETF (VHT)": "VHT",
    "Vanguard Mid-Cap Value ETF (VOE)": "VOE",
    "Consumer Staples Select Sector SPDR Fund (XLP)": "XLP",
    "Schwab U.S. TIPS ETF (SCHP)": "SCHP",
    "iShares 7-10 Year Treasury Bond ETF (IEF)": "IEF",
    "iShares Preferred & Income Securities ETF (PFF)": "PFF",
    "Utilities Select Sector SPDR Fund (XLU)": "XLU",
    "Vanguard Tax-Exempt Bond ETF (VTEB)": "VTEB",
    "iShares MSCI EAFE Value ETF (EFV)": "EFV",
    "Schwab U.S. Large-Cap Growth ETF (SCHG)": "SCHG",
    "iShares J.P. Morgan USD Emerging Markets Bond ETF (EMB)": "EMB",
    "Dimensional U.S. Core Equity 2 ETF (DFAC)": "DFAC",
    "Schwab U.S. Small-Cap ETF (SCHA)": "SCHA",
    "VanEck Gold Miners ETF (GDX)": "GDX",
    "Vanguard Mortgage-Backed Securities ETF (VMBS)": "VMBS",
    "ProShares UltraPro QQQ (TQQQ)": "TQQQ",
    "Vanguard Short-Term Treasury ETF (VGSH)": "VGSH",
    "iShares iBoxx $ High Yield Corporate Bond ETF (HYG)": "HYG",
    "Industrial Select Sector SPDR Fund (XLI)": "XLI",
    "iShares Russell Mid-Cap Value ETF (IWS)": "IWS",
    "Vanguard Extended Market ETF (VXF)": "VXF",
    "SPDR Portfolio S&P 500 ETF (SPLG)": "SPLG",
    "SPDR Portfolio S&P 500 Value ETF (SPYV)": "SPYV",
    "iShares Russell 2000 Value ETF (IWN)": "IWN",
}

PERIODS = ["mtd", "qtd", "ytd", "3m", "6m", "1y", "3y", "5y", "10y", "all"]

now = datetime.now()
PERIODS_DAYS = {
    "mtd": (now - datetime(now.year, now.month, 1)).days,
    "qtd": (
        now
        - datetime(
            now.year,
            1 if now.month < 4 else 4 if now.month < 7 else 7 if now.month < 7 else 10,
            1,
        )
    ).days,
    "ytd": (now - datetime(now.year, 1, 1)).days,
    "all": 0,
    "3m": 3 * 21,
    "6m": 6 * 21,
    "1y": 12 * 21,
    "3y": 3 * 12 * 21,
    "5y": 5 * 12 * 21,
    "10y": 10 * 12 * 21,
}


def is_ticker(ticker: str) -> bool:
    """Determine whether a string is a valid ticker

    Parameters
    ----------
    ticker : str
        The string to be tested

    Returns
    ----------
    bool
        Whether the string is a ticker
    """
    item = yf.Ticker(ticker)
    return "previousClose" in item.info


# TODO: Is this being used anywhere?
def beta_word(beta: float) -> str:
    """Describe a beta

    Parameters
    ----------
    beta : float
        The beta for a portfolio

    Returns
    ----------
    str
        The description of the beta
    """
    if abs(1 - beta) > 3:
        part = "extremely "
    elif abs(1 - beta) > 2:
        part = "very "
    elif abs(1 - beta) > 1:
        part = ""
    else:
        part = "moderately "

    return part + "high" if beta > 1 else "low"


def clean_name(name: str) -> str:
    """Clean a name to a ticker

    Parameters
    ----------
    name : str
        The value to be cleaned

    Returns
    ----------
    str
        A cleaned value
    """
    return name.replace("beta_", "").upper()


def filter_df_by_period(df: pd.DataFrame, period: str = "all") -> pd.DataFrame:
    """Filter dataframe by selected period

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe to be filtered in terms of time
    period : str
        Period in which to filter dataframe.
        Possible choices are: mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all

    Returns
    ----------
    pd.DataFrame
        A cleaned value
    """
    if period == "mtd":
        return df[df.index.strftime("%Y-%m") == datetime.now().strftime("%Y-%m")]
    if period == "qtd":
        if datetime.now().month < 4:
            return df[
                df.index.strftime("%Y-%m") < f"{datetime.now().strftime('%Y')}-04"
            ]
        if datetime.now().month < 7:
            return df[
                (df.index.strftime("%Y-%m") >= f"{datetime.now().strftime('%Y')}-04")
                & (df.index.strftime("%Y-%m") < f"{datetime.now().strftime('%Y')}-07")
            ]
        if datetime.now().month < 10:
            return df[
                (df.index.strftime("%Y-%m") >= f"{datetime.now().strftime('%Y')}-07")
                & (df.index.strftime("%Y-%m") < f"{datetime.now().strftime('%Y')}-10")
            ]
        return df[df.index.strftime("%Y-%m") >= f"{datetime.now().strftime('%Y')}-10"]
    if period == "ytd":
        return df[df.index.strftime("%Y") == datetime.now().strftime("%Y")]
    if period == "3m":
        return df[df.index >= (datetime.now() - relativedelta(months=3))]
    if period == "6m":
        return df[df.index >= (datetime.now() - relativedelta(months=6))]
    if period == "1y":
        return df[df.index >= (datetime.now() - relativedelta(years=1))]
    if period == "3y":
        return df[df.index >= (datetime.now() - relativedelta(years=3))]
    if period == "5y":
        return df[df.index >= (datetime.now() - relativedelta(years=5))]
    if period == "10y":
        return df[df.index >= (datetime.now() - relativedelta(years=10))]
    return df


def make_equal_length(df1: pd.DataFrame, df2: pd.DataFrame):
    """Filter dataframe by selected period

     Parameters
     ----------
     df1: pd.DataFrame
         The first DataFrame that needs to be compared.
     df2: pd.DataFrame
         The second DataFrame that needs to be compared.

     Returns
     ----------
    df1 and df2
         Both DataFrames returned
    """
    # Match the DataFrames so they share a similar length
    if len(df1.index) > len(df2.index):
        df1 = df1.loc[df2.index]
    elif len(df2.index) > len(df1.index):
        df2 = df2.loc[df1.index]

    return df1, df2
