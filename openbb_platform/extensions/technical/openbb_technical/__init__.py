"""OpenBB Technical Analysis Extension."""

try:
    from openbb_charting import Charting  # type: ignore

    from openbb_technical import technical_views
except ImportError:
    pass
