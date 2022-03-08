import logging

import pandas as pd
import requests

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_economy_calendar_events() -> pd.DataFrame:
    """Get economic calendar events

    Returns
    -------
    pd.DataFrame
        Get dataframe with economic calendar events
    """
    response = requests.get(
        f"https://finnhub.io/api/v1/calendar/economic?token={cfg.API_FINNHUB_KEY}"
    )

    df = pd.DataFrame()

    if response.status_code == 200:
        d_data = response.json()
        if "economicCalendar" in d_data:
            df = pd.DataFrame(d_data["economicCalendar"])
        else:
            console.print("No latest economy calendar events found\n")

    elif response.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    elif response.status_code == 403:
        console.print("[red]API Key not authorized for Premium Feature[/red]\n")
    else:
        console.print(f"Error in request: {response.json()['error']}", "\n")

    return df
