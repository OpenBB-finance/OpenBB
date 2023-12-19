"""Econometrics Router."""
import re
from itertools import combinations
from typing import Dict, List, Literal

import numpy as np
import pandas as pd
import statsmodels.api as sm  # type: ignore
from linearmodels.panel import (
    BetweenOLS,
    FamaMacBeth,
    FirstDifferenceOLS,
    PanelOLS,
    PooledOLS,
    RandomEffects,
)
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.utils import basemodel_to_df, get_target_column, get_target_columns
from openbb_core.provider.abstract.data import Data
from pydantic import PositiveInt
from statsmodels.stats.diagnostic import acorr_breusch_godfrey  # type: ignore
from statsmodels.stats.stattools import durbin_watson  # type: ignore
from statsmodels.tsa.stattools import adfuller, grangercausalitytests  # type: ignore

from openbb_econometrics.utils import get_engle_granger_two_step_cointegration_test

router = Router(prefix="")


@router.command(methods=["POST"])
def correlation_matrix(data: List[Data]) -> OBBject[List[Data]]:
    """Get the correlation matrix of an input dataset.

    Parameters
    ----------
    data : List[Data]
        Input dataset.

    Returns
    -------
    OBBject[List[Data]]:
        Correlation matrix.
    """
    df = basemodel_to_df(data)
    # remove non float columns from the dataframe to perform the correlation
    df = df.select_dtypes(include=["float64"])

    corr = df.corr()

    # replace nan values with None to allow for json serialization
    corr = corr.replace(np.NaN, None)

    ret = []
    for k, v in corr.items():
        v["comp_to"] = k
        ret.append(Data(**v))
    return OBBject(results=ret)


@router.command(methods=["POST"], include_in_schema=False)
def ols_regression(
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
    x_columns: List[str]
        List of columns to use as exogenous variables.

    Returns
    -------
    OBBject[Dict]:
        OBBject with the results being model and results objects.
    """
    X = sm.add_constant(get_target_columns(basemodel_to_df(data), x_columns))
    y = get_target_column(basemodel_to_df(data), y_column)
    model = sm.OLS(y, X)
    results = model.fit()
    return OBBject(results={"model": model, "results": results})


@router.command(methods=["POST"])
def ols_regression_summary(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Data]:
    """Perform OLS regression. This returns the summary object from statsmodels.

    Parameters
    ----------
    data: List[Data]
        Input dataset.
    y_column: str
        Target column.
    x_columns: List[str]
        List of columns to use as exogenous variables.

    Returns
    -------
    OBBject[Data]:
        OBBject with the results being summary object.
    """
    X = sm.add_constant(get_target_columns(basemodel_to_df(data), x_columns))
    y = get_target_column(basemodel_to_df(data), y_column)

    try:
        X = X.astype(float)
        y = y.astype(float)
    except ValueError as exc:
        raise ValueError("All columns must be numeric") from exc

    results = sm.OLS(y, X).fit()
    results_summary = results.summary()
    results = {}

    for item in results_summary.tables[0].data:
        results[item[0].strip()] = item[1].strip()
        results[item[2].strip()] = str(item[3]).strip()

    table_1 = results_summary.tables[1]
    headers = table_1.data[0]  # Assuming the headers are in the first row
    for i, row in enumerate(table_1.data):
        if i == 0:  # Skipping the header row
            continue
        for j, cell in enumerate(row):
            if j == 0:  # Skipping the row index
                continue
            key = f"{row[0].strip()}_{headers[j].strip()}"  # Combining row index and column header
            results[key] = cell.strip()

    for item in results_summary.tables[2].data:
        results[item[0].strip()] = item[1].strip()
        results[item[2].strip()] = str(item[3]).strip()

    results = {k: v for k, v in results.items() if v}
    clean_results = {}
    for k, v in results.items():
        new_key = re.sub(r"[.,\]\[:-]", "", k).lower().strip().replace(" ", "_")
        clean_results[new_key] = v

    clean_results["raw"] = str(results_summary)

    return OBBject(results=clean_results)


@router.command(methods=["POST"])
def autocorrelation(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """Perform Durbin-Watson test for autocorrelation.

    Parameters
    ----------
    data: List[Data]
        Input dataset.
    y_column: str
        Target column.
    x_columns: List[str]
        List of columns to use as exogenous variables.

    Returns
    -------
    OBBject[Dict]:
        OBBject with the results being the score from the test.
    """
    X = sm.add_constant(get_target_columns(basemodel_to_df(data), x_columns))
    y = get_target_column(basemodel_to_df(data), y_column)
    results = sm.OLS(y, X).fit()
    return OBBject(results=Data(score=durbin_watson(results.resid)))


@router.command(methods=["POST"])
def residual_autocorrelation(
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
    x_columns: List[str]
        List of columns to use as exogenous variables.
    lags: PositiveInt
        Number of lags to use in the test.

    Returns
    -------
    OBBject[Data]:
        OBBject with the results being the score from the test.
    """
    X = sm.add_constant(get_target_columns(basemodel_to_df(data), x_columns))
    y = get_target_column(basemodel_to_df(data), y_column)
    model = sm.OLS(y, X)
    results = model.fit()
    lm_stat, p_value, f_stat, fp_value = acorr_breusch_godfrey(results, nlags=lags)

    results = {
        "lm_stat": lm_stat,
        "p_value": p_value,
        "f_stat": f_stat,
        "fp_value": fp_value,
    }

    return OBBject(results=results)


@router.command(methods=["POST"])
def cointegration(
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
    OBBject[Data]:
        OBBject with the results being the score from the test.
    """
    pairs = list(combinations(columns, 2))
    dataset = get_target_columns(basemodel_to_df(data), columns)
    result = {}
    for x, y in pairs:
        (
            c,
            gamma,
            alpha,
            _,  # z
            adfstat,
            pvalue,
        ) = get_engle_granger_two_step_cointegration_test(dataset[x], dataset[y])
        result[f"{x}/{y}"] = {
            "c": c,
            "gamma": gamma,
            "alpha": alpha,
            "adfstat": adfstat,
            "pvalue": pvalue,
        }

    return OBBject(results=result)


@router.command(methods=["POST"])
def causality(
    data: List[Data],
    y_column: str,
    x_column: str,
    lag: PositiveInt = 3,
) -> OBBject[Data]:
    """Perform Granger causality test to determine if X "causes" y.

    Parameters
    ----------
    data: List[Data]
        Input dataset.
    y_column: str
        Target column.
    x_column: str
        Columns to use as exogenous variables.
    lag: PositiveInt
        Number of lags to use in the test.

    Returns
    -------
    OBBject[Data]:
        OBBject with the results being the score from the test.
    """
    X = get_target_column(basemodel_to_df(data), x_column)
    y = get_target_column(basemodel_to_df(data), y_column)

    granger = grangercausalitytests(pd.concat([y, X], axis=1), [lag], verbose=False)

    for test in granger[lag][0]:
        # As ssr_chi2test and lrtest have one less value in the tuple, we fill
        # this value with a '-' to allow the conversion to a DataFrame
        if len(granger[lag][0][test]) != 4:
            pars = granger[lag][0][test]
            granger[lag][0][test] = (pars[0], pars[1], "-", pars[2])

    df = pd.DataFrame(granger[lag][0], index=["F-test", "P-value", "Count", "Lags"]).T
    results = df.to_dict()

    return OBBject(results=results)


@router.command(methods=["POST"])
def unit_root(
    data: List[Data],
    column: str,
    regression: Literal["c", "ct", "ctt"] = "c",
) -> OBBject[Data]:
    """Perform Augmented Dickey-Fuller unit root test.

    Parameters
    ----------
    data: List[Data]
        Input dataset.
    column: str
        Data columns to check unit root
    regression: Literal["c", "ct", "ctt"]
        Regression type to use in the test.  Either "c" for constant only, "ct" for constant and trend, or "ctt" for
        constant, trend, and trend-squared.

    Returns
    -------
    OBBject[Data]:
        OBBject with the results being the score from the test.
    """
    dataset = get_target_column(basemodel_to_df(data), column)
    adfstat, pvalue, usedlag, nobs, _, icbest = adfuller(dataset, regression=regression)
    results = {
        "adfstat": adfstat,
        "pvalue": pvalue,
        "usedlag": usedlag,
        "nobs": nobs,
        "icbest": icbest,
    }
    return OBBject(results=results)


@router.command(methods=["POST"], include_in_schema=False)
def panel_random_effects(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """Perform One-way Random Effects model for panel data.

    Parameters
    ----------
    data: List[Data]
        Input dataset.
    y_column: str
        Target column.
    x_columns: List[str]
        List of columns to use as exogenous variables.

    Returns
    -------
    OBBject[Dict]:
        OBBject with the fit model returned
    """
    X = get_target_columns(basemodel_to_df(data), x_columns)
    y = get_target_column(basemodel_to_df(data), y_column)
    exogenous = sm.add_constant(X)
    results = RandomEffects(y, exogenous).fit()
    return OBBject(results={"results": results})


@router.command(methods=["POST"], include_in_schema=False)
def panel_between(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """Perform a Between estimator regression on panel data.

    Parameters
    ----------
    data: List[Data]
        Input dataset.
    y_column: str
        Target column.
    x_columns: List[str]
        List of columns to use as exogenous variables.

    Returns
    -------
    OBBject[Dict]:
        OBBject with the fit model returned
    """
    X = get_target_columns(basemodel_to_df(data), x_columns)
    y = get_target_column(basemodel_to_df(data), y_column)
    exogenous = sm.add_constant(X)
    results = BetweenOLS(y, exogenous).fit()
    return OBBject(results={"results": results})


@router.command(methods=["POST"], include_in_schema=False)
def panel_pooled(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """Perform a Pooled coefficient estimator regression on panel data.

    Parameters
    ----------
    data: List[Data]
        Input dataset.
    y_column: str
        Target column.
    x_columns: List[str]
        List of columns to use as exogenous variables.

    Returns
    -------
    OBBject[Dict]:
        OBBject with the fit model returned
    """
    X = get_target_columns(basemodel_to_df(data), x_columns)
    y = get_target_column(basemodel_to_df(data), y_column)
    exogenous = sm.add_constant(X)
    results = PooledOLS(y, exogenous).fit()
    return OBBject(results={"results": results})


@router.command(methods=["POST"], include_in_schema=False)
def panel_fixed(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """One- and two-way fixed effects estimator for panel data.

    Parameters
    ----------
    data: List[Data]
        Input dataset.
    y_column: str
        Target column.
    x_columns: List[str]
        List of columns to use as exogenous variables.

    Returns
    -------
    OBBject[Dict]:
        OBBject with the fit model returned
    """
    X = get_target_columns(basemodel_to_df(data), x_columns)
    y = get_target_column(basemodel_to_df(data), y_column)
    exogenous = sm.add_constant(X)
    results = PanelOLS(y, exogenous).fit()
    return OBBject(results={"results": results})


@router.command(methods=["POST"], include_in_schema=False)
def panel_first_difference(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """Perform a first-difference estimate for panel data.

    Parameters
    ----------
    data: List[Data]
        Input dataset.
    y_column: str
        Target column.
    x_columns: List[str]
        List of columns to use as exogenous variables.

    Returns
    -------
    OBBject[Dict]:
        OBBject with the fit model returned
    """
    X = get_target_columns(basemodel_to_df(data), x_columns)
    y = get_target_column(basemodel_to_df(data), y_column)
    exogenous = X
    results = FirstDifferenceOLS(y, exogenous).fit()
    return OBBject(results={"results": results})


@router.command(methods=["POST"], include_in_schema=False)
def panel_fmac(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """Fama-MacBeth estimator for panel data.

    Parameters
    ----------
    data: List[Data]
        Input dataset.
    y_column: str
        Target column.
    x_columns: List[str]
        List of columns to use as exogenous variables.

    Returns
    -------
    OBBject[Dict]:
        OBBject with the fit model returned
    """
    X = get_target_columns(basemodel_to_df(data), x_columns)
    y = get_target_column(basemodel_to_df(data), y_column)
    exogenous = sm.add_constant(X)
    results = FamaMacBeth(y, exogenous).fit()
    return OBBject(results={"results": results})
