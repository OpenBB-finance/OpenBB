"""Nasdaq Provider Constants."""

from typing import Literal

from openbb_core.app.service.system_service import SystemService

API_PREFIX = (
    SystemService()
    .system_settings.python_settings.model_dump()
    .get("api_settings", {})
    .get("prefix", "")
    or "/api/v1"
)

SYMBOL_CHOICES_ENDPOINT = f"{API_PREFIX}/nasdaq/equity/symbol_choices"
DOCUMENT_CHOICES_ENDPOINT = f"{API_PREFIX}/nasdaq/equity/document_choices"
FILING_YEARS_ENDPOINT = f"{API_PREFIX}/nasdaq/equity/filing_years"
NORDIC_SYMBOL_CHOICES_ENDPOINT = f"{API_PREFIX}/nasdaq/nordic/symbol_choices"
INDEX_SYMBOL_CHOICES_ENDPOINT = f"{API_PREFIX}/nasdaq/index/symbol_choices"
ETF_SYMBOL_CHOICES_ENDPOINT = f"{API_PREFIX}/nasdaq/etf/symbol_choices"

BASE_URL = "https://api.nasdaq.com/api"

SYMBOL_DIRECTORY_FILES = "https://www.nasdaqtrader.com/dynamic/SymDir"

ASSET_CLASSES = Literal["stocks", "etf", "index", "crypto", "mutualfunds"]

FORM_GROUPS = Literal[
    "annual",
    "quarterly",
    "proxy",
    "insider",
    "8k",
    "registration",
    "comment",
]

MOVER_LISTS = Literal[
    "most_active_share_volume",
    "most_active_dollar_volume",
    "most_advanced",
    "most_declined",
    "nasdaq_100",
]

MOVER_KEYS = {
    "most_active_share_volume": "MostActiveByShareVolume",
    "most_active_dollar_volume": "MostActiveByDollarVolume",
    "most_advanced": "MostAdvanced",
    "most_declined": "MostDeclined",
    "nasdaq_100": "Nasdaq100Movers",
}

MOVER_ASSET_CLASSES = {"stocks": "STOCKS", "etf": "ETF", "mutualfunds": "MUTUALFUNDS"}

MOVER_SESSIONS = Literal["market", "pre_market", "after_hours"]

MOVER_SESSION_KEYS = {
    "market": "currentMarket",
    "pre_market": "premarket",
    "after_hours": "afterHours",
}

HOLDER_TYPES = Literal["all", "increased", "decreased", "new", "sold_out"]

HOLDER_TYPE_KEYS = {
    "all": "TOTAL",
    "increased": "INCREASED",
    "decreased": "DECREASED",
    "new": "NEW",
    "sold_out": "SOLDOUT",
}

HOLDER_SORT_COLUMNS = Literal[
    "owner_name",
    "date",
    "shares_held",
    "shares_change",
    "shares_change_percent",
    "market_value",
]

HOLDER_SORT_KEYS = {
    "owner_name": "ownerName",
    "date": "date",
    "shares_held": "sharesHeld",
    "shares_change": "sharesChange",
    "shares_change_percent": "sharesChangePCT",
    "market_value": "marketValue",
}

CALENDAR_EVENTS = {
    "Stock Splits": "splitsList",
    "Earnings": "earningsList",
    "Dividends": "dividendsList",
    "Economic": "econsList",
    "IPOs": "iposList",
    "SPOs": "sposList",
}

CELL_CLICK_SYMBOL = {
    "renderFn": "cellOnClick",
    "renderFnParams": {
        "actionType": "groupBy",
        "groupBy": {"paramName": "symbol", "valueField": "symbol"},
    },
}

GHOST_SYMBOL_PARAM = {
    "paramName": "symbol",
    "type": "endpoint",
    "optionsEndpoint": SYMBOL_CHOICES_ENDPOINT,
    "label": "Symbol",
    "value": "",
    "show": False,
}

GHOST_INDEX_SYMBOL_PARAM = {
    "paramName": "symbol",
    "type": "endpoint",
    "optionsEndpoint": INDEX_SYMBOL_CHOICES_ENDPOINT,
    "label": "Symbol",
    "value": "",
    "show": False,
}

GHOST_ETF_SYMBOL_PARAM = {
    "paramName": "symbol",
    "type": "endpoint",
    "optionsEndpoint": ETF_SYMBOL_CHOICES_ENDPOINT,
    "label": "Symbol",
    "value": "",
    "show": False,
}
