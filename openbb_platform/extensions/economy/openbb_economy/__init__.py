"""OpenBB Economy Extension."""

try:
    from openbb_charting import Charting  # type: ignore

    from openbb_economy import economy_views
except ImportError:
    pass
