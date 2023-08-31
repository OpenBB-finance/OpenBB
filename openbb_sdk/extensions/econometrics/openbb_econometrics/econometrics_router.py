from itertools import combinations
from typing import Dict, List

import statsmodels.api as sm
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.utils import (
    basemodel_to_df,
    get_target_column,
    get_target_columns,
)
from openbb_provider.abstract.data import Data
from pydantic import PositiveInt
from statsmodels.stats.diagnostic import acorr_breusch_godfrey
from statsmodels.stats.stattools import durbin_watson

from openbb_econometrics.utils import get_engle_granger_two_step_cointegration_test

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


@router.command(methods=["POST"])
def ols_summary(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Data]:
    """Perform OLS regression.  This returns the summary object from statsmodels.

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
        OBBject with the results being summary object.
    """
    X = sm.add_constant(get_target_columns(basemodel_to_df(data), x_columns))
    y = get_target_column(basemodel_to_df(data), y_column)
    results = sm.OLS(y, X).fit()
    return OBBject(results=Data(summary=results.summary()))


@router.command(methods=["POST"])
def dwat(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """Perform Durbin-Watson test for autocorrelation

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
    OBBject[Data]
        OBBject with the results being the score from the test.
    """
    X = sm.add_constant(get_target_columns(basemodel_to_df(data), x_columns))
    y = get_target_column(basemodel_to_df(data), y_column)
    results = sm.OLS(y, X).fit()
    return OBBject(results=Data(score=durbin_watson(results.resid)))


@router.command(methods=["POST"])
def bgot(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
    lags: PositiveInt = 1,
) -> OBBject[Data]:
    """Perform Breusch-Godfrey Lagrange Multiplier tests for residual autocorrelation.

    Parameters
    ----------
    data: List[Data]
        Input dataset.
    y_column: str
        Target column.
    x_columns: str
        List of columns to use as exogenous variables.
    lags: PositiveInt
        Number of lags to use in the test.
    Returns
    -------
    OBBject[Data]
        OBBject with the results being the score from the test.
    """
    X = sm.add_constant(get_target_columns(basemodel_to_df(data), x_columns))
    y = get_target_column(basemodel_to_df(data), y_column)
    model = sm.OLS(y, X)
    lm_stat, p_value, f_stat, fp_value = acorr_breusch_godfrey(model, nlags=lags)
    return OBBject(
        results=Data(lm_stat=lm_stat, p_value=p_value, f_stat=f_stat, fp_value=fp_value)
    )


@router.command(methods=["POST"])
def coint(
    data: List[Data],
    columns: List[str],
) -> OBBject[Data]:
    """Show co-integration between two timeseries using the two step Engle-Granger test.

    Parameters
    ----------
    data: List[Data]
        Input dataset.
    columns: List[str]
        Data columns to check cointegration
    maxlag: PositiveInt
        Number of lags to use in the test.
    Returns
    -------
    OBBject[Data]
        OBBject with the results being the score from the test.
    """
    pairs = list(combinations(columns, 2))
    dataset = get_target_columns(basemodel_to_df(data), columns)
    result = []
    for x, y in pairs:
        (
            c,
            gamma,
            alpha,
            z,
            adfstat,
            pvalue,
        ) = get_engle_granger_two_step_cointegration_test(dataset[x], dataset[y])
        result.append(
            Data(
                pair=f"{x}/{y}",
                c=c,
                gamma=gamma,
                alpha=alpha,
                adfstat=adfstat,
                pvalue=pvalue,
            )
        )

    return OBBject(results=result)
