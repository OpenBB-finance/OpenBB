import logging

import requests
import pandas as pd
from bs4 import BeautifulSoup

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_debt() -> pd.DataFrame:
    "Retrieves national debt information for various countries. [Source: UsDebtClock.org]"
    url = "https://www.usdebtclock.org/world-debt-clock.html"
    data = requests.get(url, headers={"User-Agent": get_user_agent()}).content
    print(data)
