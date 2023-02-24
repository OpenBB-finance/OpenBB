"""Screener model"""
__docformat__ = "numpy"

import configparser
import logging
from pathlib import Path
from typing import Dict

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_preset_choices() -> Dict:
    """
    Return a dict containing keys as name of preset and
    filepath as value
    """

    PRESETS_PATH = (
        get_current_user().preferences.USER_PRESETS_DIRECTORY / "etf" / "screener"
    )
    PRESETS_PATH_DEFAULT = Path(__file__).parent / "presets"
    preset_choices = {
        filepath.name: filepath
        for filepath in PRESETS_PATH.iterdir()
        if filepath.suffix == ".ini"
    }
    preset_choices.update(
        {
            filepath.name: filepath
            for filepath in PRESETS_PATH_DEFAULT.iterdir()
            if filepath.suffix == ".ini"
        }
    )

    return preset_choices


@log_start_end(log=logger)
def etf_screener(preset: str):
    """
    Screens the etfs pulled from my repo (https://github.com/jmaslek/etf_scraper),
    which is updated hourly through the market day

    Parameters
    ----------
    preset: str
        Screener to use from presets

    Returns
    -------
    df : pd.DataFrame
        Screened dataframe
    """

    # pylint: disable=no-member

    df = pd.read_csv(
        "https://raw.githubusercontent.com/jmaslek/etf_scraper/main/etf_overviews.csv",
        index_col=0,
    )

    cf = configparser.ConfigParser()

    cf.read(get_preset_choices()[preset])
    cols = cf.sections()

    for col in cols:
        if cf[col]["Min"] != "None":
            query = f"{col} > {cf[col]['Min']} "
            df = df.query(query)
        if cf[col]["Max"] != "None":
            query = f"{col} < {cf[col]['Max']} "
            df = df.query(query)

    return df
