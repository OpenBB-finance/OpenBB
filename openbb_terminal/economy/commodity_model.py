import logging
import re

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request

logger = logging.getLogger(__name__)


def format_number(text: str) -> float:
    numbers = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", text)
    if "t" in text.lower():
        multiplier = 1_000_000_000_000
    elif "b" in text.lower():
        multiplier = 1_000_000_000
    elif "m" in text.lower():
        multiplier = 1_000_000
    else:
        multiplier = 1

    return round(float(numbers[0]) * multiplier, 2)


@log_start_end(log=logger)
def get_debt() -> pd.DataFrame:
    """Retrieves national debt information for various countries. [Source: wikipedia.org]

    Returns
    -------
    pd.DataFrame
        Country, Debt [$], Debt [% of GDP], Debt per capita [$], Debt per capita [% of GDP]
    """
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_external_debt"
    response = request(url, headers={"User-Agent": get_user_agent()})
    df = pd.read_html(response.text)[0]
    df = df.rename(
        columns={
            "Country/Region": "Country",
            "External debtUS dollars": "Debt",
            "Per capitaUS dollars": "Per Capita",
            "External debt US dollars": "Debt",
            "Per capita US dollars": "Per Capita",
        }
    )
    df = df.drop(["Date", "% of GDP"], axis=1)
    df["Debt"] = df["Debt"].apply(lambda x: format_number(x))
    df["Rank"] = df["Debt"].rank(ascending=False).astype(int)
    indexes = ["Rank", "Country", "Per Capita", "Debt"]
    df = df[indexes]

    return df
