""" Alpha Vantage Model """
__docformat__ = "numpy"

import pandas as pd
from alpha_vantage.sectorperformance import SectorPerformances
from gamestonk_terminal import config_terminal as cfg


def get_sector_data() -> pd.DataFrame:
    """Get real-time performance sector data

    Returns
    ----------
    df_sectors : pd.Dataframe
        Real-time performance data
    """
    sector_perf = SectorPerformances(
        key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas"
    )
    # pylint: disable=unbalanced-tuple-unpacking
    df_sectors, _ = sector_perf.get_sector()
    return df_sectors
