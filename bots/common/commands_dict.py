import re
from typing import List

import pandas as pd
from bots.economy.currencies import currencies_command
from bots.economy.energy import energy_command
from bots.economy.feargreed import feargreed_command
from bots.economy.futures import futures_command
from bots.economy.glbonds import glbonds_command
from bots.economy.grains import grains_command
from bots.economy.indices import indices_command
from bots.economy.meats import meats_command
from bots.economy.metals import metals_command
from bots.economy.overview import overview_command
from bots.economy.performance import performance_command
from bots.economy.softs import softs_command
from bots.economy.usbonds import usbonds_command
from bots.economy.valuation import valuation_command
from bots.stocks.candle import candle_command
from bots.stocks.dark_pool_shorts.dpotc import dpotc_command
from bots.stocks.dark_pool_shorts.ftd import ftd_command
from bots.stocks.dark_pool_shorts.hsi import hsi_command
from bots.stocks.dark_pool_shorts.pos import pos_command
from bots.stocks.dark_pool_shorts.psi import psi_command
from bots.stocks.dark_pool_shorts.shorted import shorted_command
from bots.stocks.dark_pool_shorts.sidtc import sidtc_command
from bots.stocks.dark_pool_shorts.spos import spos_command
from bots.stocks.disc.ford import ford_command
from bots.stocks.due_diligence.analyst import analyst_command
from bots.stocks.due_diligence.arktrades import arktrades_command
from bots.stocks.due_diligence.customer import customer_command
from bots.stocks.due_diligence.est import est_command
from bots.stocks.due_diligence.pt import pt_command
from bots.stocks.due_diligence.sec import sec_command
from bots.stocks.due_diligence.supplier import supplier_command
from bots.stocks.government.contracts import contracts_command
from bots.stocks.government.gtrades import gtrades_command
from bots.stocks.government.histcont import histcont_command
from bots.stocks.government.lastcontracts import lastcontracts_command
from bots.stocks.government.lasttrades import lasttrades_command
from bots.stocks.government.lobbying import lobbying_command
from bots.stocks.government.qtrcontracts import qtrcontracts_command
from bots.stocks.government.topbuys import topbuys_command
from bots.stocks.government.toplobbying import toplobbying_command
from bots.stocks.government.topsells import topsells_command
from bots.stocks.insider.lins import lins_command
from bots.stocks.options.cc_hist import cc_hist_command
from bots.stocks.options.hist import hist_command
from bots.stocks.options.iv import iv_command
from bots.stocks.options.oi import oi_command
from bots.stocks.options.opt_chain import chain_command
from bots.stocks.options.overview import overview_command as overview_opt_command
from bots.stocks.options.unu import unu_command
from bots.stocks.options.vol import vol_command
from bots.stocks.options.vsurf import vsurf_command
from bots.stocks.quote import quote_command
from bots.stocks.screener.financial import financial_command
from bots.stocks.screener.historical import historical_command
from bots.stocks.screener.overview import overview_command as overview_screener_command
from bots.stocks.screener.ownership import ownership_command
from bots.stocks.screener.performance import (
    performance_command as performance_screener_command,
)
from bots.stocks.screener.presets_custom import presets_custom_command
from bots.stocks.screener.presets_default import presets_default_command
from bots.stocks.screener.technical import technical_command
from bots.stocks.screener.valuation import (
    valuation_command as valuation_screener_command,
)
from bots.stocks.technical_analysis.ad import ad_command
from bots.stocks.technical_analysis.adosc import adosc_command
from bots.stocks.technical_analysis.adx import adx_command
from bots.stocks.technical_analysis.aroon import aroon_command
from bots.stocks.technical_analysis.bbands import bbands_command
from bots.stocks.technical_analysis.cci import cci_command
from bots.stocks.technical_analysis.donchian import donchian_command
from bots.stocks.technical_analysis.ema import ema_command
from bots.stocks.technical_analysis.fib import fib_command
from bots.stocks.technical_analysis.fisher import fisher_command
from bots.stocks.technical_analysis.hma import hma_command
from bots.stocks.technical_analysis.kc import kc_command
from bots.stocks.technical_analysis.macd import macd_command
from bots.stocks.technical_analysis.obv import obv_command
from bots.stocks.technical_analysis.recom import recom_command
from bots.stocks.technical_analysis.rsi import rsi_command
from bots.stocks.technical_analysis.sma import sma_command
from bots.stocks.technical_analysis.stoch import stoch_command
from bots.stocks.technical_analysis.summary import summary_command
from bots.stocks.technical_analysis.view import view_command
from bots.stocks.technical_analysis.wma import wma_command
from bots.stocks.technical_analysis.zlma import zlma_command

re_date = re.compile(r"/^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/")
re_int = re.compile(r"^[1-9]\d*$")
re_float = re.compile(r"^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$")
re_name = re.compile(r"(?s).*")
re_window = re.compile(r"(?s).*")

gov_type = ["congress", "senate", "house"]

dps_pos_choices = {
    "Short Vol (1M)": "sv",
    "Short Vol %": "sv_pct",
    "Net Short Vol (1M)": "nsv",
    "Net Short Vol ($100M)": "nsv_dollar",
    "DP Position (1M)": "dpp",
    "DP Position ($1B)": "dpp_dollar",
}

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

options_vsurf_choices = {
    "Volatility": "IV",
    "Open Interest": "OI",
    "Last Price": "LP",
}

opt_intervals = [1, 5, 15, 30, 60, 1440]


screener_sort = {
    "overview": [
        "Ticker",
        "Company",
        "Sector",
        "Industry",
        "Country",
        "Market Cap",
        "P/E",
        "Price",
        "Change",
        "Volume",
    ],
    "valuation": [
        "Ticker",
        "Market Cap",
        "P/E",
        "Fwd P/E",
        "PEG",
        "P/S",
        "P/B",
        "P/C",
        "P/FCF",
        "EPS this Y",
        "EPS next Y",
        "EPS past 5Y",
        "EPS next 5Y",
        "Sales past 5Y",
        "Price",
        "Change",
        "Volume",
    ],
    "financial": [
        "Ticker",
        "Market Cap",
        "Dividend",
        "ROA",
        "ROE",
        "ROI",
        "Curr R",
        "Quick R",
        "LTDebt/Eq",
        "Debt/Eq",
        "Gross M",
        "Oper M",
        "Profit M",
        "Earnings",
        "Price",
        "Change",
        "Volume",
    ],
    "ownership": [
        "Ticker",
        "Market Cap",
        "Outstanding",
        "Float",
        "Insider Own",
        "Insider Trans",
        "Inst Own",
        "Inst Trans",
        "Float Short",
        "Short Ratio",
        "Avg Volume",
        "Price",
        "Change",
        "Volume",
    ],
    "performance": [
        "Ticker",
        "Perf Week",
        "Perf Month",
        "Perf Quart",
        "Perf Half",
        "Perf Year",
        "Perf YTD",
        "Volatility W",
        "Volatility M",
        "Recom",
        "Avg Volume",
        "Rel Volume",
        "Price",
        "Change",
        "Volume",
    ],
    "technical": [
        "Ticker",
        "Beta",
        "ATR",
        "SMA20",
        "SMA50",
        "SMA200",
        "52W High",
        "52W Low",
        "RSI",
        "Price",
        "Change",
        "from Open",
        "Gap",
        "Volume",
    ],
}

presets = [
    "potential_reversals",
    "golden_cross_penny",
    "rosenwald_gtfo",
    "golden_cross",
    "bull_runs_over_10pct",
    "recent_growth_and_support",
    "heavy_inst_ins",
    "short_squeeze_scan",
    "under_15dol_stocks",
    "top_performers_healthcare",
    "oversold_under_3dol",
    "value_stocks",
    "cheap_dividend",
    "death_cross",
    "top_performers_tech",
    "unusual_volume",
    "cheap_oversold",
    "undervalue",
    "high_vol_and_low_debt",
    "simplistic_momentum_scanner_under_7dol",
    "5pct_above_low",
    "growth_stocks",
    "cheap_bottom_dividend",
    "analyst_strong_buy",
    "oversold",
    "rosenwald",
    "weak_support_and_top_performers",
    "channel_up_and_low_debt_and_sma_50and200",
    "template",
    "modified_neff",
    "buffett_like",
    "oversold_under_5dol",
    "sexy_year",
    "news_scanner",
    "top_performers_all",
    "stocks_strong_support_levels",
    "continued_momentum_scan",
    "modified_dreman",
    "break_out_stocks",
]
signals = [
    "top_gainers",
    "top_losers",
    "new_high",
    "new_low",
    "most_volatile",
    "most_active",
    "unusual_volume",
    "overbought",
    "oversold",
    "downgrades",
    "upgrades",
    "earnings_before",
    "earnings_after",
    "recent_insider_buying",
    "recent_insider_selling",
    "major_news",
    "horizontal_sr",
    "tl_resistance",
    "tl_support",
    "wedge_up",
    "wedge_down",
    "wedge",
    "triangle_ascending",
    "triangle_descending",
    "channel_up",
    "channel_down",
    "channel",
    "double_top",
    "double_bottom",
    "multiple_top",
    "multiple_bottom",
    "head_shoulders",
    "head_shoulders_inverse",
]

possible_ma = [
    "dema",
    "ema",
    "fwma",
    "hma",
    "linreg",
    "midpoint",
    "pwma",
    "rma",
    "sinwma",
    "sma",
    "swma",
    "t3",
    "tema",
    "trima",
    "vidya",
    "wma",
    "zlma",
]


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
        "required": {"sort": dps_pos_choices.values()},
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
    "econ-feargreed": {
        "function": feargreed_command,
    },
    "econ-overview": {
        "function": overview_command,
    },
    "econ-indices": {
        "function": indices_command,
    },
    "econ-futures": {
        "function": futures_command,
    },
    "econ-usbonds": {
        "function": usbonds_command,
    },
    "econ-glbonds": {
        "function": glbonds_command,
    },
    "econ-energy": {
        "function": energy_command,
    },
    "econ-metals": {
        "function": metals_command,
    },
    "econ-meats": {
        "function": meats_command,
    },
    "econ-grains": {
        "function": grains_command,
    },
    "econ-softs": {
        "function": softs_command,
    },
    "econ-currencies": {
        "function": currencies_command,
    },
    "econ-valuation": {
        "function": valuation_command,
        "required": {"economy_group": econ_group},
    },
    "econ-performance": {
        "function": performance_command,
        "required": {"economy_group": econ_group},
    },
    "gov-lasttrades": {
        "function": lasttrades_command,
        "required": {"gov_type": gov_type},
        "optional": {"past_days": re_int, "representative": re_name},
    },
    "gov-topbuys": {
        "function": topbuys_command,
        "required": {"gov_type": gov_type},
        "optional": {
            "past_transactions_months": re_int,
            "num": re_int,
            "raw": [True, False],
        },
    },
    "gov-topsells": {
        "function": topsells_command,
        "required": {"gov_type": gov_type},
        "optional": {
            "past_transactions_months": re_int,
            "num": re_int,
            "raw": [True, False],
        },
    },
    "gov-lastcontracts": {
        "function": lastcontracts_command,
        "optional": {"past_transactions_days": re_int, "num": re_int},
    },
    "gov-qtrcontracts": {
        "function": qtrcontracts_command,
        "required": {"analysis": ["total", "upmom", "downmom"]},
        "optional": {
            "num": re_int,
        },
    },
    "gov-toplobbying": {
        "function": toplobbying_command,
        "optional": {"num": re_int, "raw": [True, False]},
    },
    "gov-gtrades": {
        "function": gtrades_command,
        "required": {
            "ticker": tickers,
            "gov_type": gov_type,
        },
        "optional": {"past_transactions_months": re_int, "raw": [True, False]},
    },
    "gov-contracts": {
        "function": contracts_command,
        "required": {
            "ticker": tickers,
            "past_transaction_days": re_int,
            "raw": [True, False],
        },
    },
    "gov-histcont": {"function": histcont_command, "required": {"ticker": tickers}},
    "gov-lobbying": {
        "function": lobbying_command,
        "required": {"ticker": tickers},
        "optional": {
            "num": re_int,
        },
    },
    "opt-chain": {
        "function": chain_command,
        "required": {
            "ticker": tickers,
            "expiry": re_date,
            "opt_type": ["Calls", "Puts"],
        },
        "optional": {"min_sp": re_float, "max_sp": re_float},
    },
    "opt-oi": {
        "function": oi_command,
        "required": {"ticker": tickers, "expiry": re_date},
        "optional": {"min_sp": re_float, "max_sp": re_float},
    },
    "opt-iv": {
        "function": iv_command,
        "required": {"ticker": tickers},
    },
    "q": {"function": quote_command, "required": {"ticker": tickers}},
    "disc-ford": {
        "function": ford_command,
    },
    "opt-unu": {
        "function": unu_command,
    },
    "ins-last": {
        "function": lins_command,
        "required": {"ticker": tickers},
        "optional": {"num": re_int},
    },
    "cc": {
        "function": candle_command,
        "required": {"ticker": tickers, "interval": opt_intervals},
        "optional": {"past_days": re_int, "start": re_date, "end": re_date},
    },
    "opt-overview": {
        "function": overview_opt_command,
        "required": {"ticker": tickers, "expiry": re_date},
        "optional": {
            "min_sp": re_float,
            "max_sp": re_float,
        },
    },
    "opt-vol": {
        "function": vol_command,
        "required": {"ticker": tickers, "expiry": re_date},
    },
    "opt-vsurf": {
        "function": vsurf_command,
        "required": {"ticker": tickers, "z": options_vsurf_choices.values()},
    },
    "opt-hist": {
        "function": hist_command,
        "required": {
            "ticker": tickers,
            "expiry": re_date,
            "strike": re_float,
            "opt_type": ["Calls", "Puts"],
            "greek": ["iv", "gamma", "delta", "theta", "rho", "vega"],
        },
    },
    "opt-cc-hist": {
        "function": cc_hist_command,
        "required": {
            "ticker": tickers,
            "expiry": re_date,
            "strike": re_float,
            "opt_type": ["Calls", "Puts"],
        },
    },
    "scr-presets_default": {
        "function": presets_default_command,
    },
    "scr-presets_custom": {
        "function": presets_custom_command,
    },
    "scr-historical": {
        "function": historical_command,
        "required": {"signal": signals},
        "optional": {"start": re_date},
    },
    "scr-overview": {
        "function": overview_screener_command,
        "required": {"preset": presets, "sort": screener_sort["overview"]},
        "optional": {"limit": re_int, "ascend": [True, False]},
    },
    "scr-valuation": {
        "function": valuation_screener_command,
        "required": {"preset": presets, "sort": screener_sort["valuation"]},
        "optional": {"limit": re_int, "ascend": [True, False]},
    },
    "scr-financial": {
        "function": financial_command,
        "required": {"preset": presets, "sort": screener_sort["financial"]},
        "optional": {"limit": re_int, "ascend": [True, False]},
    },
    "scr-ownership": {
        "function": ownership_command,
        "required": {"preset": presets, "sort": screener_sort["ownership"]},
        "optional": {"limit": re_int, "ascend": [True, False]},
    },
    "scr-performance": {
        "function": performance_screener_command,
        "required": {"preset": presets, "sort": screener_sort["performance"]},
        "optional": {"limit": re_int, "ascend": [True, False]},
    },
    "scr-technical": {
        "function": technical_command,
        "required": {"preset": presets, "sort": screener_sort["technical"]},
        "optional": {"limit": re_int, "ascend": [True, False]},
    },
    "ta-ema": {
        "function": ema_command,
        "required": {"ticker": tickers},
        "optional": {
            "window": re_window,
            "offset": re_int,
            "start": re_date,
            "end": re_date,
        },
    },
    "ta-sma": {
        "function": sma_command,
        "required": {"ticker": tickers},
        "optional": {
            "window": re_window,
            "offset": re_int,
            "start": re_date,
            "end": re_date,
        },
    },
    "ta-wma": {
        "function": wma_command,
        "required": {"ticker": tickers},
        "optional": {
            "window": re_window,
            "offset": re_int,
            "start": re_date,
            "end": re_date,
        },
    },
    "ta-hma": {
        "function": hma_command,
        "required": {"ticker": tickers},
        "optional": {
            "window": re_window,
            "offset": re_int,
            "start": re_date,
            "end": re_date,
        },
    },
    "ta-zlma": {
        "function": zlma_command,
        "required": {"ticker": tickers},
        "optional": {
            "window": re_window,
            "offset": re_int,
            "start": re_date,
            "end": re_date,
        },
    },
    "ta-cci": {
        "function": cci_command,
        "required": {"ticker": tickers},
        "optional": {
            "length": re_int,
            "scalar": re_float,
            "start": re_date,
            "end": re_date,
        },
    },
    "ta-macd": {
        "function": macd_command,
        "required": {"ticker": tickers},
        "optional": {
            "length": re_int,
            "scalar": re_float,
            "start": re_date,
            "end": re_date,
        },
    },
    "ta-rsi": {
        "function": rsi_command,
        "required": {"ticker": tickers},
        "optional": {
            "length": re_int,
            "scalar": re_float,
            "drift": re_int,
            "start": re_date,
            "end": re_date,
        },
    },
    "ta-stoch": {
        "function": stoch_command,
        "required": {"ticker": tickers},
        "optional": {
            "fast_k": re_int,
            "slow_k": re_int,
            "slow_d": re_int,
            "start": re_date,
            "end": re_date,
        },
    },
    "ta-fisher": {
        "function": fisher_command,
        "required": {"ticker": tickers},
        "optional": {"length": re_int, "start": re_date, "end": re_date},
    },
    "ta-cg": {
        "function": fisher_command,
        "required": {"ticker": tickers},
        "optional": {"length": re_int, "start": re_date, "end": re_date},
    },
    "ta-adx": {
        "function": adx_command,
        "required": {"ticker": tickers},
        "optional": {
            "length": re_int,
            "scalar": re_int,
            "drift": re_int,
            "start": re_date,
            "end": re_date,
        },
    },
    "ta-aroon": {
        "function": aroon_command,
        "required": {"ticker": tickers},
        "optional": {
            "length": re_int,
            "scalar": re_int,
            "start": re_date,
            "end": re_date,
        },
    },
    "ta-bbands": {
        "function": bbands_command,
        "required": {
            "ticker": tickers,
            "mamode": ["ema", "sma", "wma", "hma", "zlma"],
        },
        "optional": {"length": re_int, "std": re_int, "start": re_date, "end": re_date},
    },
    "ta-donchian": {
        "function": donchian_command,
        "required": {"ticker": tickers},
        "optional": {
            "upper_length": re_int,
            "lower_length": re_int,
            "start": re_date,
            "end": re_date,
        },
    },
    "ta-kc": {
        "function": kc_command,
        "required": {
            "ticker": tickers,
            "mamode": ["ema", "sma", "wma", "hma", "zlma"],
        },
        "optional": {
            "length": re_int,
            "scalar": re_int,
            "offset": re_int,
            "start": re_date,
            "end": re_date,
        },
    },
    "ta-ad": {
        "function": ad_command,
        "required": {"ticker": tickers},
        "optional": {"is_open": ["True", "False"], "start": re_date, "end": re_date},
    },
    "ta-adosc": {
        "function": adosc_command,
        "required": {
            "ticker": tickers,
        },
        "optional": {
            "is_open": ["True", "False"],
            "fast": re_int,
            "slow": re_int,
            "start": re_date,
            "end": re_date,
        },
    },
    "ta-obv": {
        "function": obv_command,
        "required": {"ticker": tickers},
        "optional": {"start": re_date, "end": re_date},
    },
    "ta-fib": {
        "function": fib_command,
        "required": {"ticker": tickers},
        "optional": {"start": re_date, "end": re_date},
    },
    "ta-view": {"function": view_command, "required": {"ticker": tickers}},
    "ta-summary": {"function": summary_command, "required": {"ticker": tickers}},
    "ta-recom": {"function": recom_command, "required": {"ticker": tickers}},
}
