"""OpenBB Crypto Extension."""

try:
    from openbb_charting import Charting  # type: ignore

    from openbb_crypto import crypto_views
except ImportError:
    pass
