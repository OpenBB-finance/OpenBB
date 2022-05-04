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
    "sp400": {"name": "S&P 400 Mid Cap Index", "ticker": "^SP400"},
    "sp600": {"name": "S&P 600 Small Cap Index", "ticker": "^SP600"},
    "sp500tr": {"name": "S&P 500 TR Index", "ticker": "^SP500TR"},
    "sp-xsp": {"name": "S&P 500 Mini SPX Options Index", "ticker": "^XSP"},
    "nyse-ny": {"name": "NYSE US 100 Index", "ticker": "^NY"},
    "dow-djus": {"name": "Dow Jones US Index", "ticker": "^DJUS"},
    "nyse": {"name": "NYSE Composite Index", "ticker": "^NYA"},
    "amex": {"name": "NYSE-AMEX Composite Index", "ticker": "^XAX"},
    "nasdaq": {"name": "Nasdaq Composite Index", "ticker": "^IXIC"},
    "russell1000": {"name": "Russell 1000 Index", "ticker": "^RUI"},
    "russell2000": {"name": "Russell 2000 Index", "ticker": "^RUT"},
    "cboe-bxr": {"name": "CBOE Russell 2000 Buy-Write Index", "ticker": "^BXR"},
    "cboe-bxrt": {
        "name": "CBOE Russell 2000 30-Delta Buy-Write Index",
        "ticker": "^BXRT",
    },
    "russell3000": {"name": "Russell 3000 Index", "ticker": "^RUA"},
    "russellvalue": {"name": "Russell 2000 Value Index", "ticker": "^RUJ"},
    "russellgrowth": {"name": "Russell 2000 Growth Index", "ticker": "^RUO"},
    "dow-dja": {"name": "Dow Jones Composite Average Index", "ticker": "^DJA"},
    "dow-dji": {"name": "Dow Jones Industrial Average Index", "ticker": "^DJI"},
    "ca-tsx": {"name": "TSX Composite Index (CAD)", "ticker": "^GSPTSE"},
    "mx-ipc": {"name": "IPC Mexico Index (MXN)", "ticker": "^MXX"},
    "arca-mxy": {"name": "NYSE ARCA Mexico Index (USD)", "ticker": "^MXY"},
    "br-bvsp": {"name": "IBOVESPA Sao Paulo Brazil Index (BRL)", "ticker": "^BVSP"},
    "eu-fteu1": {"name": "FTSE Eurotop 100 Index (EUR)", "ticker": "^FTEU1"},
    "eu-speup": {"name": "S&P Europe 350 Index (EUR)", "ticker": "^SPEUP"},
    "eu-n100": {"name": "Euronext 100 Index (EUR)", "ticker": "^N100"},
    "ftse100": {"name": "FTSE Global 100 Index (GBP)", "ticker": "^FTSE"},
    "ftse250": {"name": "FTSE Global 250 Index (GBP)", "ticker": "^FTMC"},
    "ftse350": {"name": "FTSE Global 350 Index (GBP)", "ticker": "^FTLC"},
    "ftai": {"name": "FTSE AIM All-Share Global Index (GBP)", "ticker": "^FTAI"},
    "uk-ftas": {"name": "UK FTSE All-Share Index (GBP)", "ticker": "^FTAS"},
    "uk-spuk": {"name": "S&P United Kingdom Index (PDS)", "ticker": "^SPUK"},
    "uk100": {"name": "CBOE UK 100 Index (GBP)", "ticker": "^BUK100P"},
    "ie-iseq": {"name": "ISEQ Irish All Shares Index (EUR)", "ticker": "^ISEQ"},
    "nl-aex": {"name": "Euronext Dutch 25 Index (EUR)", "ticker": "^AEX"},
    "nl-amx": {"name": "Euronext Dutch Mid Cap Index (EUR)", "ticker": "^AMX"},
    "at-atx": {"name": "Wiener Börse Austrian 20 Index (EUR)", "ticker": "^ATX"},
    "ch-stoxx": {"name": "Zurich STXE 600 PR Index (EUR)", "ticker": "^STOXX"},
    "ch-stoxx50e": {"name": "Zurich ESTX 50 PR Index (EUR)", "ticker": "^STOXX50E"},
    "ch-ssip": {"name": "Swiss All Shares Index (CHF)", "ticker": "SSIP.SW"},
    "ch-airlines": {"name": "STXE TM Airlines Index (EUR)", "ticker": "U0A.Z"},
    "omxn40": {"name": "OMX Nordic 40 (EUR)", "ticker": "^OMXN40"},
    "se-omx30": {"name": "OMX Stockholm 30 Index (SEK)", "ticker": "^OMX"},
    "se-omxspi": {"name": "OMX Stockholm All Share PI (SEK)", "ticker": "^OMXSPI"},
    "se-benchmark": {"name": "OMX Stockholm Benchmark GI (SEK)", "ticker": "^OMXSBGI"},
    "dk-benchmark": {"name": "OMX Copenhagen Benchamrk GI (DKK)", "ticker": "^OMXCBGI"},
    "dk-omxc25": {"name": "OMX Copenhagen 25 Index (DKK)", "ticker": "^OMXC25"},
    "fi-omxhbgi": {"name": "OMX Helsinki Benchmark GI (EUR)", "ticker": "^OMXHPI"},
    "fi-omxh25": {"name": "OMX Helsinki 25 (EUR)", "ticker": "^OMXH25"},
    "de-dax40": {"name": "DAX Performance Index (EUR)", "ticker": "^GDAXI"},
    "de-mdax60": {"name": "DAX Mid Cap Performance Index (EUR)", "ticker": "^MDAXI"},
    "de-sdax70": {"name": "DAX Small Cap Performance Index (EUR)", "ticker": "^SDAXI"},
    "de-tecdax30": {"name": "DAX Tech Sector TR Index (EUR)", "ticker": "^TECDAX"},
    "fr-cac40": {"name": "CAC 40 PR Index (EUR)", "ticker": "^FCHI"},
    "fr-next20": {"name": "CAC Next 20 Index (EUR)", "ticker": "^CN20"},
    "fr-sbf120": {"name": "Paris SBF 120 Index (EUR)", "ticker": "^SBF120"},
    "it-mib40": {"name": "FTSE MIB 40 Index (EUR)", "ticker": "FTSEMIB.MI"},
    "be-bel20": {"name": "BEL 20 Brussels Index (EUR)", "ticker": "^BFX"},
    "pt-bvlg": {
        "name": "Lisbon PSI All-Share Index GR (EUR)",
        "ticker": "^BVLG",
    },
    "es-ibex35": {"name": "IBEX 35 - Madrid CATS (EUR)", "ticker": "^IBEX"},
    "in-bse": {"name": "S&P Bombay SENSEX (INR)", "ticker": "^BSESN"},
    "in-bse-mcap": {
        "name": "S&P Bombay Mid Cap Index (INR)",
        "ticker": "BSE-MIDCAP.BO",
    },
    "in-bse-scap": {
        "name": "S&P Bombay Small Cap Index (INR)",
        "ticker": "BSE-SMLCAP.BO",
    },
    "in-nse50": {"name": "NSE Nifty 50 Index (INR)", "ticker": "^NSEI"},
    "in-nse-mcap": {"name": "NSE Nifty 50 Mid Cap Index (INR)", "ticker": "^NSEMDCP50"},
    "in-nse-bank": {
        "name": "NSE Nifty Bank Industry Index (INR)",
        "ticker": "^NSEBANK",
    },
    "in-nse500": {"name": "NSE Nifty 500 Index (INR)", "ticker": "^CRSLDX"},
    "il-ta125": {"name": "Tel-Aviv 125 Index (ILS)", "ticker": "^TA125.TA"},
    "za-shariah": {
        "name": "Johannesburg Shariah All Share Index (ZAR)",
        "ticker": "^J143.JO",
    },
    "za-jo": {"name": "Johannesburg All Share Index (ZAR)", "ticker": "^J203.JO"},
    "za-jo-mcap": {
        "name": "Johannesburg Large and Mid Cap Index (ZAR)",
        "ticker": "^JO206.JO",
    },
    "za-jo-altex": {
        "name": "Johannesburg Alt Exchange Index (ZAR)",
        "ticker": "^J232.JP",
    },
    "ru-moex": {"name": "MOEX Russia Index (RUB)", "ticker": "IMOEX.ME"},
    "au-asx200": {"name": "S&P/ASX 200 Index (AUD)", "ticker": "^AXJO"},
    "au-aord": {"name": "Australia All Ordinary Share Index (AUD)", "ticker": "^AORD"},
    "nz50": {"name": "S&P New Zealand 50 Index (NZD)", "ticker": "^nz50"},
    "kr-kospi": {"name": "KOSPI Composite Index (KRW)", "ticker": "^KS11"},
    "jp-arca": {"name": "NYSE ARCA Japan Index (JPY)", "ticker": "^JPN"},
    "jp-n225": {"name": "Nikkei 255 Index (JPY)", "ticker": "^N225"},
    "jp-n300": {"name": "Nikkei 300 Index (JPY)", "ticker": "^N300"},
    "jp-nknr": {"name": "Nikkei Avg Net TR Index (JPY)", "ticker": "^NKVI.OS"},
    "jp-nkrc": {"name": "Nikkei Avg Risk Control Index (JPY)", "ticker": "^NKRC.OS"},
    "jp-nklv": {"name": "Nikkei Avg Leverage Index (JPY)", "ticker": "^NKLV.OS"},
    "jp-nkcc": {"name": "Nikkei Avg Covered Call Index (JPY)", "ticker": "^NKCC.OS"},
    "jp-nkhd": {
        "name": "Nikkei Avg High Dividend Yield Index (JPY)",
        "ticker": "^NKHD.OS",
    },
    "jp-auto": {
        "name": "Nikkei 500 Auto & Auto Parts Index (JPY)",
        "ticker": "^NG17.OS",
    },
    "jp-fintech": {
        "name": "Global Fintech Japan Hedged Index (JPY)",
        "ticker": "^FDSFTPRJPY",
    },
    "jp-nkdh": {"name": "Nikkei Average USD Hedge Index (JPY)", "ticker": "^NKDH.OS"},
    "jp-nkeh": {"name": "Nikkei Average EUR Hedghe Index (JPY)", "ticker": "^NKEH.OS"},
    "cn-sse-comp": {"name": "SSE Composite Index (CNY)", "ticker": "000001.SS"},
    "cn-sse-a": {"name": "SSE A Share Index (CNY)", "ticker": "000002.SS"},
    "cn-szse-comp": {"name": "SZSE Component Index (CNY)", "ticker": "399001.SZ"},
    "cn-szse-a": {"name": "SZSE A-Shares Index (CNY)", "ticker": "399107.SZ"},
    "tw-twii": {"name": "TSEC Weighted Index (TWD)", "ticker": "^TWII"},
    "tw-tpai": {"name": "TSEC Paper and Pulb Subindex (TWD)", "ticker": "^TPAI"},
    "hk-hsi": {"name": "Hang Seng Index (HKD)", "ticker": "^HSI"},
    "hk-hko": {"name": "NYSE ARCA Hong Kong Options Index (USD)", "ticker": "^HKO"},
    "id-jkse": {"name": "Jakarta Composite Index (IDR)", "ticker": "^JKSE"},
    "my-klci": {"name": "FTSE Bursa Malaysia KLCI (MYR)", "ticker": "^KLSE"},
    "sg-sti": {"name": "STI Singapore Index (SGD)", "ticker": "^STI"},
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
    "sphyda": {"name": "S&P High Yield Aristocrats Index", "ticker": "^SPHYDA"},
    "dow-djt": {"name": "Dow Jones Transportation Average Index", "ticker": "^DJT"},
    "dow-dju": {"name": "Dow Jones Utility Average Index", "ticker": "^DJU"},
    "dow-rci": {"name": "Dow Jones Composite All REIT Index", "ticker": "^RCI"},
    "reit-fnar": {"name": "FTSE Nareit All Equity REITs Index", "ticker": "^FNAR"},
    "nq-q50": {"name": "NASDAQ Q50 Index", "ticker": "^NXTQ"},
    "nq-ixch": {"name": "NASDAQ Health Care Index", "ticker": "^IXCH"},
    "nq-tech": {"name": "NASDAQ 100 Technology Sector Index", "ticker": "^NDXT"},
    "nq-ex-tech": {"name": "NASDAQ 100 Ex-Tech Total Return Index", "ticker": "^NXTR"},
    "nq-ixtc": {"name": "NASDAQ Telecommunications Index", "ticker": "^IXTC"},
    "nq-inds": {"name": "NASDAQ Industrial Index", "ticker": "^INDS"},
    "nq-ixco": {"name": "NASDAQ Computer Index", "ticker": "^INCO"},
    "nq-bank": {"name": "NASDAQ Bank Index", "ticker": "^BANK"},
    "nq-tran": {"name": "NASDAQ Transportation Index", "ticker": "^TRAN"},
    "ice-auto": {"name": "ICE FactSet Global NextGen Auto Index", "ticker": "^ICEFSNA"},
    "ice-comm": {
        "name": "ICE FactSet Global NextGen Communications Index",
        "ticker": "^ICEFSNC",
    },
    "nyse-nyl": {"name": "NYSE World Leaders Index", "ticker": "^NYL"},
    "nyse-nyi": {"name": "NYSE International 100 Index", "ticker": "^NYI"},
    "nyse-nyy": {"name": "NYSE TMT Index", "ticker": "^NYY"},
    "arca-xmi": {"name": "NYSE ARCA Major Market Index", "ticker": "^XMI"},
    "arca-xbd": {"name": "NYSE ARCA Securities Broker/Dealer Index", "ticker": "^XBD"},
    "arca-xii": {"name": "NYSE ARCA Institutional Index", "ticker": "^XII"},
    "arca-xoi": {"name": "NYSE ARCA Oil and Gas Index", "ticker": "^XOI"},
    "arca-xng": {"name": "NYSE ARCA Natural Gas Index", "ticker": "^XNG"},
    "arca-hui": {"name": "NYSE ARCA Gold Bugs Index", "ticker": "^HUI"},
    "arca-ixb": {"name": "NYSE Materials Select Sector Index", "ticker": "^IXB"},
    "arca-drg": {"name": "NYSE ARCA Phramaceutical Index", "ticker": "^DRG"},
    "arca-btk": {"name": "NYSE ARCA Biotech Index", "ticker": "^BKT"},
    "arca-pse": {"name": "NYSE ARCA Tech 100 Index", "ticker": "^PSE"},
    "arca-nwx": {"name": "NYSE ARCA Networking Index", "ticker": "^NWX"},
    "arca-xci": {"name": "NYSE ARCA Computer Tech Index", "ticker": "^XCI"},
    "arca-xal": {"name": "NYSE ARCA Airline Index", "ticker": "^XAL"},
    "arca-xtc": {"name": "NYSE ARCA N.A. Telecom Industry Index", "ticker": "^XTC"},
    "phlx-sox": {"name": "PHLX Semiconductor Index", "ticker": "^SOX"},
    "phlx-xau": {"name": "PHLX Gold/Silver Index", "ticker": "^XAU"},
    "phlx-hgx": {"name": "PHLX Housing Sector Index", "ticker": "^HGX"},
    "phlx-osx": {"name": "PHLX Oil Services Sector Index", "ticker": "^OSX"},
    "phlx-uty": {"name": "PHLX Utility Sector Index", "ticker": "^UTY"},
    "w5000": {"name": "Wilshire 5000", "ticker": "^W5000"},
    "w5000flt": {"name": "Wilshire 5000 Float Adjusted Index", "ticker": "^W5000FLT"},
    "reit-wgreit": {"name": "Wilshire Global REIT Index", "ticker": "^WGREIT"},
    "reit-wgresi": {
        "name": "Wilshire Global Real Estate Sector Index",
        "ticker": "^WGRESI",
    },
    "reit-wilreit": {"name": "Wilshire US REIT Index", "ticker": "^WILREIT"},
    "reit-wilresi": {
        "name": "Wilshire US Real Estate Security Index",
        "ticker": "^WILRESI",
    },
    "cboe-bxm": {"name": "CBOE Buy-Write Monthly Index", "ticker": "^BXM"},
    "cboe-vix": {"name": "CBOE Volatility Index", "ticker": "^VIX"},
    "cboe-vin": {"name": "CBOE Near-Term VIX Index", "ticker": "^VIN"},
    "cobe-vvix": {"name": "CBOE VIX Volatility Index", "ticker": "^VVIX"},
    "cboe-shortvol": {"name": "CBOE Short VIX Futures Index", "ticker": "^SHORTVOL"},
    "cboe-skew": {"name": "CBOE Skew Index", "ticker": "^SKEW"},
    "cboe-vxn": {"name": "CBOE NASDAQ 100 Volatility Index", "ticker": "^VXN"},
    "cboe-gvz": {"name": "CBOE Gold Volatility Index", "ticker": "^GVZ"},
    "cboe-ovx": {"name": "CBOE Crude Oil Volatility Index", "ticker": "^OVX"},
    "cboe-tnx": {"name": "CBOE Interest Rate 10 Year T-Note", "ticker": "^TNX"},
    "cboe-tyx": {"name": "CBOE 30 year Treasury Yields", "ticker": "^TYX"},
    "cboe-irx": {"name": "CBOE 13 Week Treasury Bill", "ticker": "^IRX"},
    "us-dx-y": {"name": "US Dollar Index", "ticker": "DX-Y.NYB"},
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
