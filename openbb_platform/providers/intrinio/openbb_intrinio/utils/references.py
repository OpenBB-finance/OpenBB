from typing import Literal

SOURCES = Literal[
    "iex",
    "bats",
    "bats_delayed",
    "utp_delayed",
    "cta_a_delayed",
    "cta_b_delayed",
    "intrinio_mx",
    "intrinio_mx_plus",
    "delayed_sip",
]

TICKER_EXCEPTIONS = [
    "SPX",
    "XSP",
    "XEO",
    "NDX",
    "XND",
    "VIX",
    "RUT",
    "MRUT",
    "DJX",
    "XAU",
    "OEX",
]
