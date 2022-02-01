"""Custom Controller Model"""
__docformat__ = "numpy"

import logging
from pathlib import Path

import pandas as pd

from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def load(file: str) -> pd.DataFrame:
    """Load custom file into dataframe.  Currently will work with csv

    Parameters
    ----------
    file: str
        Path to file

    Returns
    -------
    pd.DataFrame:
        Dataframe with custom data
    """
    if not Path(file).exists():
        return pd.DataFrame()
    file_type = Path(file).suffix
    # TODO More data types
    if file_type != ".csv":
        return pd.DataFrame()
    return pd.read_csv(file)
