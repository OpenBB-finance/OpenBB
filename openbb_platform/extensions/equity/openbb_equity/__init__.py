"""Equity Data."""

try:
    from openbb_charting import Charting  # type: ignore

    from openbb_equity import equity_views
except ImportError:
    pass
