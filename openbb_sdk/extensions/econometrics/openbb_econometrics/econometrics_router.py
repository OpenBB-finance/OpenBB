from typing import List, Literal

import numpy as np
import pandas as pd
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.router import Router
from openbb_core.app.utils import (
    basemodel_to_df,
    df_to_basemodel,
    get_target_column,
    get_target_columns,
)
from openbb_provider.abstract.data import Data
from pydantic import NonNegativeFloat, PositiveInt


router = Router(prefix="")


@router.command(methods=["POST"])
def corr(data: List[Data]) -> OBBject[List[Data]]:
    """Get the corrlelation matrix of an input dataset.

    Parameters
    ----------
    data : List[Data]
        Input dataset.

    Returns
    -------
    OBBject[List[Data]]
        Correlation matrix.
    """
    df = basemodel_to_df(data)
    return OBBject(results=df.corr())
