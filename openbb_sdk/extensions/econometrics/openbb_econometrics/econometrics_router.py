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
import statsmodels.api as sm


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
    corr = df.corr()
    ret = []
    for k, v in corr.items():
        v["comp_to"] = k
        ret.append(Data(**v))
    return OBBject(results=ret)


@router.command(methods=["POST"], include_in_schema=False)
def ols(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """Perform OLS regression.  This returns the model and results objects from statsmodels.

    Parameters
    ----------
    data: List[Data]
        Input dataset.
    y_column: str
        Target column.
    x_columns: str
        List of columns to use as exogenous variables.

    Returns
    -------
    OBBject[Dict]
        OBBject with the results being model and results objects.
    """
    X = sm.add_constant(get_target_columns(basemodel_to_df(data), x_columns))
    y = get_target_column(basemodel_to_df(data), y_column)
    model = sm.OLS(y, X)
    results = model.fit()
    return OBBject(results={"model": model, "results": results})
