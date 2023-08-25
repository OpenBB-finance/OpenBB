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
def corr(
        data: List[Data],
)-> OBBject[List[Data]]:
    if isinstance(data, list):
        print("yes")
        df = basemodel_to_df(data)
    corr = df.corr()
    return OBBject(results=df_to_basemodel(corr))


