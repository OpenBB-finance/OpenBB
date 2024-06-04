"""The Currency router init."""

try:
    from openbb_charting import Charting  # type: ignore

    from openbb_currency import currency_views
except ImportError:
    pass
