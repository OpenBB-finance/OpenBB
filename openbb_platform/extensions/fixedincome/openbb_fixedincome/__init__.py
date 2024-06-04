"""Fixed income router init."""

try:
    from openbb_charting import Charting  # type: ignore

    from openbb_fixedincome import fixedincome_views
except ImportError:
    pass
