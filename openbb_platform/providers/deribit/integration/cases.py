"""The Deribit commands and parameters both consumption surfaces are exercised with."""

SHARED = {
    ("futures", "curve"),
    ("futures", "historical"),
    ("futures", "info"),
    ("futures", "instruments"),
    ("options", "chains"),
}

MODELS = [
    ("futures", "curve", {"symbol": "BTC"}),
    (
        "futures",
        "historical",
        {
            "symbol": "BTC-PERPETUAL",
            "start_date": "2026-01-01",
            "end_date": "2026-02-01",
        },
    ),
    ("futures", "info", {"symbol": "BTC-PERPETUAL"}),
    ("futures", "instruments", {}),
    ("index", "delivery_prices", {"index_name": "btc_usd", "limit": 5}),
    ("index", "historical", {"index_name": "btc_usd", "span": "1h"}),
    ("index", "price", {"index_name": "btc_usd,eth_usd"}),
    ("market", "block_rfq_trades", {"limit": 10}),
    ("market", "book_summary", {"currency": "BTC", "kind": "future"}),
    ("market", "order_book", {"symbol": "BTC-PERPETUAL", "depth": 5}),
    ("market", "settlements", {"currency": "BTC", "limit": 5}),
    ("market", "ticker", {"symbol": "BTC-PERPETUAL"}),
    ("market", "trade_volumes", {}),
    ("market", "trades", {"symbol": "BTC-PERPETUAL", "limit": 5}),
    ("options", "chains", {"symbol": "BTC"}),
    ("rates", "apr_history", {"currency": "usde", "limit": 5}),
    ("rates", "funding_chart", {"symbol": "BTC-PERPETUAL"}),
    ("rates", "funding_history", {"symbol": "BTC-PERPETUAL"}),
    ("reference", "announcements", {"limit": 3}),
    ("reference", "combos", {"currency": "BTC"}),
    ("reference", "currencies", {}),
    ("reference", "expirations", {"currency": "BTC", "kind": "any"}),
    ("reference", "instruments", {"currency": "BTC", "kind": "future"}),
    ("volatility", "index", {"currency": "BTC", "interval": "1d"}),
    ("volatility", "realized", {"currency": "BTC"}),
]

FEEDS = [
    ("futures", "curve_choices", {}),
    ("futures", "perpetual_choices", {}),
    ("options", "underlying_choices", {}),
    ("options", "expiration_choices", {"symbol": "BTC"}),
    ("options", "strike_choices", {"symbol": "BTC"}),
    ("options", "strategy_choices", {"symbol": "BTC"}),
    ("rates", "funding_value", {"symbol": "BTC-PERPETUAL"}),
    ("reference", "combo_choices", {"currency": "BTC"}),
    ("reference", "contract_size", {"symbol": "BTC-PERPETUAL"}),
    ("reference", "currency_choices", {}),
    ("reference", "index_choices", {}),
    ("reference", "index_choices", {"supported": True}),
    ("reference", "instrument_choices", {"kind": "future"}),
    ("reference", "server_time", {}),
    ("reference", "status", {}),
]

TABLES = [
    ("optimizer", {"symbol": "BTC", "target_price": 100000, "limit": 5}),
    ("straddle", {"symbol": "BTC"}),
    ("strangle", {"symbol": "BTC", "moneyness": 5}),
    ("spreads", {"symbol": "BTC", "moneyness": 5}),
    ("straddle", {"symbol": "ETH"}),
]

CHARTS = [
    ("smile", {"symbol": "BTC"}),
    ("smile", {"symbol": "BTC", "otm": True, "skew": True}),
    ("smile", {"symbol": "ETH"}),
    ("stats", {"symbol": "BTC"}),
    ("stats", {"symbol": "BTC", "metric": "volume", "unit": "pcr"}),
    ("stats", {"symbol": "BTC", "by": "strike", "unit": "percent"}),
    ("stats", {"symbol": "SOL_USDC"}),
    ("surface", {"symbol": "BTC"}),
    ("surface", {"symbol": "BTC", "metric": "gex", "option_type": "calls"}),
    ("surface", {"symbol": "BTC", "dte_min": 7, "dte_max": 90, "oi": True}),
    ("term_structure", {"symbol": "BTC"}),
    ("term_structure", {"symbol": "BTC", "metric": "price", "moneyness": 5}),
    ("payoff", {"symbol": "BTC"}),
    ("payoff", {"symbol": "BTC", "target_price": 100000, "budget": 1000}),
]


def namespace(router: str, name: str) -> str:
    """Return where a command is served: its own namespace or the shared one."""
    from openbb_deribit import DERIVATIVES_INSTALLED

    return (
        "derivatives"
        if DERIVATIVES_INSTALLED and (router, name) in SHARED
        else "deribit"
    )


def case_id(case: tuple) -> str:
    """Name a parametrized case by its command and parameters."""
    *path, params = case
    written = ",".join(f"{key}={value}" for key, value in params.items())

    return ".".join(path) + (f"[{written}]" if written else "")
