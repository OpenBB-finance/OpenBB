"""Index Extension."""

try:
    from openbb_charting import Charting  # type: ignore

    from openbb_index import index_views
except ImportError:
    pass
