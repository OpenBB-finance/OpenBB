from typing import List
import re
import pandas as pd
from bots.stocks.due_diligence.analyst import analyst_command
from bots.stocks.due_diligence.arktrades import arktrades_command
from bots.stocks.due_diligence.customer import customer_command
from bots.stocks.due_diligence.est import est_command
from bots.stocks.due_diligence.pt import pt_command
from bots.stocks.due_diligence.sec import sec_command
from bots.stocks.due_diligence.supplier import supplier_command
from bots.stocks.dark_pool_shorts.dpotc import dpotc_command
from bots.stocks.dark_pool_shorts.ftd import ftd_command
from bots.stocks.dark_pool_shorts.hsi import hsi_command
from bots.stocks.dark_pool_shorts.pos import pos_command
from bots.stocks.dark_pool_shorts.psi import psi_command
from bots.stocks.dark_pool_shorts.shorted import shorted_command
from bots.stocks.dark_pool_shorts.sidtc import sidtc_command
from bots.stocks.dark_pool_shorts.spos import spos_command

re_date = re.compile(r"/^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/")
re_int = re.compile(r"^[1-9]\d*$")


econ_group = [
    "basic_materials",
    "capitalization",
    "communication_services",
    "consumer_cyclical",
    "consumer_defensive",
    "country",
    "energy",
    "financial",
    "healthcare",
    "industry",
    "industrials",
    "real_estate",
    "sector",
    "technology",
    "utilities",
]

econ_fgind = {
    "Junk Bond Demand": "jbd",
    "Market Volatility": "mv",
    "Put and Call Options": "pco",
    "Market Momentum": "mm",
    "Stock Price Strength": "sps",
    "Stock Price Breadth": "spb",
    "Safe Heaven Demand": "shd",
}


def get_tickers() -> List[str]:
    col_list = ["Name"]
    df = pd.read_csv("files/tickers.csv", usecols=col_list)
    df = df["Name"]
    return df.tolist()


tickers = get_tickers()

commands = {
    "dd-analyst": {
        "function": analyst_command,
        "required": {"ticker": tickers},
    },
    "dd-pt": {
        "function": pt_command,
        "required": {"ticker": tickers},
        "optional": {"raw": [True, False], "start": re_date},
    },
    "dd-est": {"function": est_command, "required": {"ticker": tickers}},
    "dd-sec": {"function": sec_command, "required": {"ticker": tickers}},
    "dd-supplier": {
        "function": supplier_command,
        "required": {"ticker": tickers},
    },
    "dd-customer": {
        "function": customer_command,
        "required": {"ticker": tickers},
    },
    "dd-arktrades": {
        "function": arktrades_command,
        "required": {
            "ticker": tickers,
        },
        "optional": {"num": re_int},
    },
    "dps-shorted": {"function": shorted_command, "optional": re_int},
    "dps-hsi": {"function": hsi_command, "optional": {"num": re_int}},
    "dps-pos": {
        "function": pos_command,
        "required": {
            "sort": ["sv", "sv_pct", "nsv", "nsv_dollar", "dpp", "dpp_dollar"]
        },
        "optional": {"num": re_int},
    },
    "dps-sidtc": {
        "function": sidtc_command,
        "required": {"sort": ["float", "dtc", "si"]},
        "optional": {"num": re_int},
    },
    "dps-ftd": {
        "function": ftd_command,
        "required": {"ticker": tickers},
        "optional": {"start": re_date, "end": re_date},
    },
    "dps-dpotc": {
        "function": dpotc_command,
        "required": {"ticker": tickers},
    },
    "dps-spos": {"function": spos_command, "required": {"ticker": tickers}},
    "dps-psi": {"function": psi_command, "required": {"ticker": tickers}},
}
