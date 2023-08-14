class HubEnvironment:
    # BASE_URL = "http://127.0.0.1:8000/"
    BASE_URL = "https://payments.openbb.co/"
    HUB_URL = "https://my.openbb.co/"

    def __new__(cls, *args, **kwargs):  # pylint: disable=W0613
        """Create a singleton instance of the backend."""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)  # pylint: disable=E1120
        return cls.instance


BackendEnvironment = HubEnvironment()

DEFAULT_ROUTINES_URL = "https://openbb-cms.directus.app/items/Routines"

TIMEOUT = 30
CONNECTION_ERROR_MSG = "[red]Connection error.[/red]"
CONNECTION_TIMEOUT_MSG = "[red]Connection timeout.[/red]"

SCRIPT_TAGS = [
    "stocks",
    "crypto",
    "etf",
    "economy",
    "forex",
    "fixed income",
    "alternative",
    "funds",
    "bonds",
    "macro",
    "mutual funds",
    "equities",
    "options",
    "dark pool",
    "shorts",
    "insider",
    "behavioral analysis",
    "fundamental analysis",
    "technical analysis",
    "quantitative analysis",
    "forecasting",
    "government",
    "comparison",
    "nft",
    "on chain",
    "off chain",
    "screener",
    "report",
    "overview",
    "rates",
    "econometrics",
    "portfolio",
    "real estate",
]
