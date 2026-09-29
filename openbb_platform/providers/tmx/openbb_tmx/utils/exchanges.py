"""The global exchange suffixes the quote feed addresses."""

EXCHANGE_SUFFIXES = {
    "AE": "Nasdaq Dubai Exchange",
    "AR": "Merval, Argentina",
    "AS": "Amsterdam",
    "AT": "Athens, Greece",
    "AU": "Sydney, Australia",
    "BE": "Berlin, Germany",
    "BR": "Brussels, Belgium",
    "BV": "Bovespa, Brazil",
    "CL": "Santiago, Chile",
    "CO": "Copenhagen, Denmark",
    "CZ": "Shenzhen, China",
    "DB": "Xetra, Deutsche Boerse",
    "DU": "Dusseldorf, Germany",
    "FF": "Frankfurt, Germany",
    "HA": "Hanover, Germany",
    "HI": "Helsinki, Finland",
    "HK": "Hong Kong",
    "HM": "Hamburg, Germany",
    "IE": "Irish Stock Exchange",
    "LN": "London Stock Exchange and FTSE UK Indices",
    "LS": "Lisbon, Portugal",
    "MA": "Madrid, Spain",
    "MB": "Bombay, India",
    "MI": "Milan, Italy",
    "MU": "Munich, Germany",
    "MX": "Mexico",
    "NKK": "Japan, Nikkei",
    "OS": "Oslo, Norway",
    "PA": "Paris, France",
    "SG": "Stuttgart, Germany",
    "SH": "Shanghai, China",
    "SM": "Swiss Market, Switzerland",
    "ST": "Stockholm, Sweden",
    "STOX": "STOXX, Dow Jones",
    "US": "United States",
    "VX": "Virt-X, Switzerland",
}

NORTH_AMERICAN_EXCHANGES = {
    "TSX": "Toronto Stock Exchange",
    "TSXV": "TSX Venture Exchange",
    "ALPHA": "TSX Alpha Exchange",
    "CSE": "Canadian Securities Exchange",
    "NEO-L": "Cboe Canada, Lit book",
    "NEO-D": "Cboe Canada, Dark book",
    "NEO-N": "Cboe Canada, Neo book",
    "CXD": "Nasdaq Canada, Dark book",
    "MOE": "Montreal Options Exchange",
    "CMF": "Canadian Mutual Funds",
    "NYSE": "New York Stock Exchange",
    "NYSE American": "NYSE American",
    "ARCA": "NYSE Arca",
    "NASD": "Nasdaq",
    "NSD": "Nasdaq",
    "NGS": "Nasdaq Global Select Market",
    "NCM": "Nasdaq Capital Market",
    "CBOE BZX": "Cboe BZX",
    "CFE": "Cboe Futures Exchange",
    "OTCPK": "OTC Pink",
    "OTCQB": "OTCQB Venture Market",
    "OTCQX": "OTCQX Best Market",
    "OTCID": "OTC Identified",
    "OTCBB": "OTC Bulletin Board",
    "Greys": "Grey Market",
    "CMEG": "CME Group",
    "CBOT": "Chicago Board of Trade",
    "CMX": "COMEX",
    "NMX": "NYMEX",
    "CMESP": "CME Spot",
    "FOREX": "Foreign Exchange",
    "Crypto": "Cryptocurrency",
}

DIRECTORY_VENUES = {
    "TSX": "Toronto Stock Exchange",
    "TSXV": "TSX Venture Exchange",
    "ALPHA": "TSX Alpha Exchange",
    "CSE": "Canadian Securities Exchange",
    "NEO-L": "Cboe Canada, Lit book",
    "NEO-D": "Cboe Canada, Dark book",
    "NEO-N": "Cboe Canada, Neo book",
    "CXD": "Nasdaq Canada, Dark book",
    "MOE": "Montreal Exchange",
    "CMF": "Canadian Mutual Funds",
    "TSXSTAT": "TSX Market Statistics",
    "TSVST": "TSX Venture Market Statistics",
    "NYSE": "New York Stock Exchange",
    "NYSE American": "NYSE American",
    "ARCA": "NYSE Arca",
    "NASD": "Nasdaq",
    "NSD": "Nasdaq",
    "NGS": "Nasdaq Global Select Market",
    "NCM": "Nasdaq Capital Market",
    "CBOE BZX": "Cboe BZX",
    "OTCPK": "OTC Pink",
    "OTCQB": "OTCQB Venture Market",
    "OTCQX": "OTCQX Best Market",
    "OTCID": "OTC Identified",
    "OTCBB": "OTC Bulletin Board",
    "Greys": "Grey Market",
    "EXPM": "Expert Market",
    "NMF": "United States Mutual Funds",
    "CMEG": "CME Group",
    "CBOT": "Chicago Board of Trade",
    "CMX": "COMEX",
    "NMX": "NYMEX",
    "NYMEX": "NYMEX Look-Alike Futures",
    "CFE": "Cboe Futures Exchange",
    "FOREX": "Foreign Exchange",
    "Crypto": "Cryptocurrency",
    "NYGIF": "NYSE Global Index Feed",
    "SPIC": "S&P Global Indices",
    "SPIB": "S&P Benchmark Indices",
    "CMESP": "CME Spot Indices",
    "DJI": "Dow Jones Averages",
    "DJX": "Dow Jones Global Indices",
    "DJUS": "Dow Jones United States Indices",
    "RUSSELL": "Russell Indices",
    "ISE": "ISE Indices",
    "CGIF Main": "Cboe Global Indices",
    "CGIF CGI": "Cboe Strategy Indices",
    "CGIF INAV": "Cboe Intraday Indicative Values",
    "CGIF CCCY": "Cboe Cryptocurrency Indices",
    "CGIF FTSE": "Cboe FTSE Russell Indices",
    "CGIF MSCI": "Cboe MSCI Indices",
}


CHARTABLE_VENUES = (
    "TSX",
    "TSXV",
    "ALPHA",
    "CSE",
    "NEO-L",
    "NEO-D",
    "NEO-N",
    "CXD",
    "MOE",
    "CMF",
    "TSXSTAT",
    "TSVST",
    "NYSE",
    "NYSE American",
    "ARCA",
    "NASD",
    "NSD",
    "NGS",
    "NCM",
    "CBOE BZX",
    "OTCPK",
    "OTCQB",
    "OTCQX",
    "OTCID",
    "Greys",
    "EXPM",
    "NMX",
    "NYMEX",
    "CMX",
    "FOREX",
    "Crypto",
    "ISE",
)


SYMBOL_PREFIXES = {
    "^": "Index",
    "/": "Future",
    "$": "Currency pair",
    "~": "Cryptocurrency pair",
    "@": "Option contract",
}


def describe_symbol(symbol: str) -> dict:
    """Describe how a symbol addresses the quote feed.

    Parameters
    ----------
    symbol : str
        The symbol, with any prefix or exchange suffix.

    Returns
    -------
    dict
        The instrument kind, exchange suffix, and the market it names.
    """
    symbol = symbol.strip().upper()
    prefix = symbol[:1]
    suffix = symbol.rsplit(":", 1)[1] if ":" in symbol else None

    return {
        "symbol": symbol,
        "kind": SYMBOL_PREFIXES.get(prefix, "Equity or fund"),
        "exchange_suffix": suffix,
        "market": EXCHANGE_SUFFIXES.get(suffix) if suffix else "Canada",
    }
