"""OpenBB ETF Extension."""

try:
    from openbb_charting import Charting  # type: ignore

    from openbb_etf import etf_views
except ImportError:
    pass
