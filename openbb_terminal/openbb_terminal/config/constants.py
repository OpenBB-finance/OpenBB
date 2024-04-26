"""Constants module."""

from pathlib import Path

# Paths
HOME_DIRECTORY = Path.home()
REPOSITORY_DIRECTORY = Path(__file__).parent.parent.parent.parent
SRC_DIRECTORY = Path(__file__).parent.parent
SETTINGS_DIRECTORY = HOME_DIRECTORY / ".openbb_terminal"
ASSETS_DIRECTORY = SRC_DIRECTORY / "assets"
STYLES_DIRECTORY = ASSETS_DIRECTORY / "styles"
ENV_FILE_REPOSITORY = REPOSITORY_DIRECTORY / ".env"
ENV_FILE_PROJECT = REPOSITORY_DIRECTORY / "openbb_terminal" / ".env"
ENV_FILE_SETTINGS = SETTINGS_DIRECTORY / ".env"
HIST_FILE_PROMPT = SETTINGS_DIRECTORY / ".openbb_terminal.his"
I18N_FILE = ASSETS_DIRECTORY / "i18n"


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
AVAILABLE_FLAIRS = {
    ":openbb": "(🦋)",
    ":bug": "(🐛)",
    ":rocket": "(🚀)",
    ":diamond": "(💎)",
    ":stars": "(✨)",
    ":baseball": "(⚾)",
    ":boat": "(⛵)",
    ":phone": "(☎)",
    ":mercury": "(☿)",
    ":hidden": "",
    ":sun": "(☼)",
    ":moon": "(☾)",
    ":nuke": "(☢)",
    ":hazard": "(☣)",
    ":tunder": "(☈)",
    ":king": "(♔)",
    ":queen": "(♕)",
    ":knight": "(♘)",
    ":recycle": "(♻)",
    ":scales": "(⚖)",
    ":ball": "(⚽)",
    ":golf": "(⛳)",
    ":piece": "(☮)",
    ":yy": "(☯)",
}
