"""Nasdaq Router.

Assembly point for the Nasdaq sub-routers. Each sub-router owns one namespace
and registers its model-backed commands only when the OpenBB extension that
normally serves those standard models is absent, so an install of
``openbb-nasdaq`` alone still exposes every dataset.

This replaces the standalone ``app.py`` factory; the dashboard it defined is
now served from ``assets/apps.json`` on the normal ``openbb-api`` server.
"""

import json
from pathlib import Path

from openbb_core.app.router import Router

from openbb_nasdaq import (
    CRYPTO_INSTALLED,
    DERIVATIVES_INSTALLED,
    ECONOMY_INSTALLED,
    EQUITY_INSTALLED,
    ETF_INSTALLED,
    INDEX_INSTALLED,
    NEWS_INSTALLED,
)
from openbb_nasdaq.routers.calendar import router as calendar_router
from openbb_nasdaq.routers.crypto import router as crypto_router
from openbb_nasdaq.routers.derivatives import router as derivatives_router
from openbb_nasdaq.routers.economy import router as economy_router
from openbb_nasdaq.routers.equity import router as equity_router
from openbb_nasdaq.routers.estimates import router as estimates_router
from openbb_nasdaq.routers.etf import router as etf_router
from openbb_nasdaq.routers.fundamentals import router as fundamentals_router
from openbb_nasdaq.routers.index import router as index_router
from openbb_nasdaq.routers.markets import router as markets_router
from openbb_nasdaq.routers.news import router as news_router
from openbb_nasdaq.routers.nordic import router as nordic_router
from openbb_nasdaq.routers.ownership import router as ownership_router

router = Router(prefix="", description="Nasdaq provider router.")

for _subrouter in (
    equity_router,
    calendar_router,
    fundamentals_router,
    ownership_router,
    estimates_router,
    etf_router,
    index_router,
    crypto_router,
    derivatives_router,
    news_router,
    economy_router,
    markets_router,
    nordic_router,
):
    router.include_router(_subrouter)

_APPS_JSON = Path(__file__).parent / "assets" / "apps.json"

# The template stores the widget IDs of the standard OpenBB namespaces. When the
# extension that owns a namespace is absent, the Nasdaq router serves the same
# data under ``/nasdaq/...``, so the stored ID is swapped for the standalone one.
_STANDALONE_WIDGET_IDS: dict[str, tuple[str, bool]] = {
    "equity_calendar_earnings_nasdaq_obb": (
        "nasdaq_equity_calendar_earnings_nasdaq_obb",
        EQUITY_INSTALLED,
    ),
    "equity_calendar_dividend_nasdaq_obb": (
        "nasdaq_equity_calendar_dividend_nasdaq_obb",
        EQUITY_INSTALLED,
    ),
    "equity_calendar_ipo_nasdaq_obb": (
        "nasdaq_equity_calendar_ipo_nasdaq_obb",
        EQUITY_INSTALLED,
    ),
    "equity_calendar_splits_nasdaq_obb": (
        "nasdaq_equity_calendar_splits_nasdaq_obb",
        EQUITY_INSTALLED,
    ),
    "equity_fundamental_dividends_nasdaq_obb": (
        "nasdaq_equity_fundamental_dividends_nasdaq_obb",
        EQUITY_INSTALLED,
    ),
    "equity_screener_nasdaq_obb": (
        "nasdaq_equity_screener_nasdaq_obb",
        EQUITY_INSTALLED,
    ),
    "equity_price_quote_nasdaq_obb": (
        "nasdaq_equity_quote_nasdaq_obb",
        EQUITY_INSTALLED,
    ),
    "equity_ownership_insider_trading_nasdaq_obb": (
        "nasdaq_equity_ownership_insider_trading_nasdaq_obb",
        EQUITY_INSTALLED,
    ),
    "economy_calendar_nasdaq_obb": (
        "nasdaq_economy_calendar_nasdaq_obb",
        ECONOMY_INSTALLED,
    ),
    "derivatives_options_chains_nasdaq_obb": (
        "nasdaq_options_chains_nasdaq_obb",
        DERIVATIVES_INSTALLED,
    ),
    "etf_info_nasdaq_obb": ("nasdaq_etf_info_nasdaq_obb", ETF_INSTALLED),
    "etf_search_nasdaq_obb": ("nasdaq_etf_search_nasdaq_obb", ETF_INSTALLED),
    "etf_holdings_nasdaq_obb": ("nasdaq_etf_holdings_nasdaq_obb", ETF_INSTALLED),
    "etf_equity_exposure_nasdaq_obb": (
        "nasdaq_etf_equity_exposure_nasdaq_obb",
        ETF_INSTALLED,
    ),
    "index_price_historical_nasdaq_obb": (
        "nasdaq_index_historical_nasdaq_obb",
        INDEX_INSTALLED,
    ),
    "index_snapshots_nasdaq_obb": (
        "nasdaq_index_snapshots_nasdaq_obb",
        INDEX_INSTALLED,
    ),
    "crypto_price_historical_nasdaq_obb": (
        "nasdaq_crypto_historical_nasdaq_obb",
        CRYPTO_INSTALLED,
    ),
    "news_company_nasdaq_obb": ("nasdaq_news_company_nasdaq_obb", NEWS_INSTALLED),
}


def _resolve_widget_id(widget_id: str) -> str:
    """Return the widget ID that resolves against the active install."""
    standalone, installed = _STANDALONE_WIDGET_IDS.get(widget_id, (widget_id, True))

    return widget_id if installed else standalone


@router.api_router.get("/apps.json", include_in_schema=False)
async def nasdaq_apps() -> list:
    """Serve the bundled Nasdaq dashboard template (``assets/apps.json``)."""
    apps = json.loads(_APPS_JSON.read_text(encoding="utf-8"))

    for app in apps:
        for tab in app.get("tabs", {}).values():
            for widget in tab.get("layout", []):
                widget["i"] = _resolve_widget_id(widget["i"])

        for group in app.get("groups", []):
            if "widgetIds" in group:
                group["widgetIds"] = [
                    _resolve_widget_id(wid) for wid in group["widgetIds"]
                ]

    return apps
