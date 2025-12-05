"""BIS helper functions."""

from datetime import date
from pathlib import Path
from warnings import warn

from openbb_bis.utils.constants import (
    CODE_FREQ_TO_KEY,
    CODE_TO_COUNTRY_HOUSE_PRICE_INDEX,
    FREQ_TO_FREQUENCY,
    FREQS,
)
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.utils import get_user_cache_directory
from pandas import to_datetime

cache = get_user_cache_directory() + "/bis"
# Create the cache directory if it does not exist
Path(cache).mkdir(parents=True, exist_ok=True)


def fnCodeFreqKeyStr(countriesCodeList: list, queryFreq: str) -> str:
    """Convert country code with frequency to item(s) download key(s), as merged string."""
    _keysList: list = []
    for code in countriesCodeList:
        # Find the closest data frequency available
        # Scenario 1: user wants DE.M but only DE.Q is there
        # Scenario 2: user wants TH.Q but only TH.M is there
        iLastFound = -1
        for f in FREQS:
            if code + "." + f in CODE_FREQ_TO_KEY:
                iLastFound += 1  # For Scenario 2
                freq = f
                if freq == queryFreq:
                    break  # For Scenario 1
        if freq != queryFreq:
            warn(
                f"({code}) {CODE_TO_COUNTRY_HOUSE_PRICE_INDEX[code]}: "
                + FREQ_TO_FREQUENCY[queryFreq]
                + " data not found. Switching to "
                + FREQ_TO_FREQUENCY[freq]
                + "."
            )
        codeFreq = code + "." + freq
        _keysList.append(CODE_FREQ_TO_KEY[codeFreq])
    return ",".join(_keysList)


def bis_date_to_python_date(input_date: str | int) -> date:
    """Date formatter helper."""
    input_date = str(input_date)
    if "Q" in input_date:
        return to_datetime(input_date).to_period("Q").start_time.date()
    if len(input_date) == 4:
        return date(int(input_date), 1, 1)
    if len(input_date) == 7:
        return to_datetime(input_date).to_period("M").start_time.date()
    raise OpenBBError("Date not in expected format")
