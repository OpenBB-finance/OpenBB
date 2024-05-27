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
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.utils import basemodel_to_df, get_target_column, get_target_columns
from openbb_core.provider.abstract.data import Data
from pydantic import PositiveInt
from statsmodels.stats.diagnostic import acorr_breusch_godfrey  # type: ignore
from statsmodels.stats.stattools import durbin_watson  # type: ignore
from statsmodels.tsa.stattools import adfuller, grangercausalitytests  # type: ignore

from openbb_econometrics.utils import get_engle_granger_two_step_cointegration_test

router = Router(prefix="", description="Econometrics analysis tools.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the correlation matrix of a dataset.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                "obb.econometrics.correlation_matrix(data=stock_data)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def correlation_matrix(data: List[Data]) -> OBBject[List[Data]]:
    """Get the correlation matrix of an input dataset.

    The correlation matrix provides a view of how different variables in your dataset relate to one another.
    By quantifying the degree to which variables move in relation to each other, this matrix can help identify patterns,
    trends, and potential areas for deeper analysis. The correlation score ranges from -1 to 1, with -1 indicating a
    perfect negative correlation, 0 indicating no correlation, and 1 indicating a perfect positive correlation.

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


@router.command(
    methods=["POST"],
    include_in_schema=False,
    examples=[
        PythonEx(
            description="Perform Ordinary Least Squares (OLS) regression.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                'obb.econometrics.ols_regression(data=stock_data, y_column="close", x_columns=["open", "high", "low"])',
            ],
        ),
        APIEx(
            parameters={
                "y_column": "close",
                "x_columns": ["open", "high", "low"],
                "data": APIEx.mock_data("timeseries"),
            }
        ),
    ],
)
def ols_regression(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """Perform Ordinary Least Squares (OLS) regression.

    OLS regression is a fundamental statistical method to explore and model the relationship between a
    dependent variable and one or more independent variables. By fitting the best possible linear equation to the data,
    it helps uncover how changes in the independent variables are associated with changes in the dependent variable.
    This returns the model and results objects from statsmodels library.

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
    OBBject[Dict]
        OBBject with the results being model and results objects.
    """
    X = sm.add_constant(get_target_columns(basemodel_to_df(data), x_columns))
    y = get_target_column(basemodel_to_df(data), y_column)
    model = sm.OLS(y, X)
    results = model.fit()
    return OBBject(results={"model": model, "results": results})


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Perform Ordinary Least Squares (OLS) regression and return the summary.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501  pylint: disable=line-too-long
                'obb.econometrics.ols_regression_summary(data=stock_data, y_column="close", x_columns=["open", "high", "low"])',  # noqa: E501  pylint: disable=line-too-long
            ],
        ),
        APIEx(
            parameters={
                "y_column": "close",
                "x_columns": ["open", "high", "low"],
                "data": APIEx.mock_data("timeseries"),
            }
        ),
    ],
)
def ols_regression_summary(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Data]:
    """Perform Ordinary Least Squares (OLS) regression.

    This returns the summary object from statsmodels.

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
    OBBject[Data]
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


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Perform Durbin-Watson test for autocorrelation.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                'obb.econometrics.autocorrelation(data=stock_data, y_column="close", x_columns=["open", "high", "low"])',
            ],
        ),
        APIEx(
            parameters={
                "y_column": "close",
                "x_columns": ["open", "high", "low"],
                "data": APIEx.mock_data("timeseries"),
            }
        ),
    ],
)
def autocorrelation(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Data]:
    """Perform Durbin-Watson test for autocorrelation.

    The Durbin-Watson test is a widely used method for detecting the presence of autocorrelation in the residuals
    from a statistical or econometric model. Autocorrelation occurs when past values in the data series influence
    future values, which can be a critical issue in time-series analysis, affecting the reliability of
    model predictions. The test provides a statistic that ranges from 0 to 4, where a value around 2 suggests
    no autocorrelation, values towards 0 indicate positive autocorrelation, and values towards 4 suggest
    negative autocorrelation. Understanding the degree of autocorrelation helps in refining models to better capture
    the underlying dynamics of the data, ensuring more accurate and trustworthy results.

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
    OBBject[Dict]
        OBBject with the results being the score from the test.
    """
    X = sm.add_constant(get_target_columns(basemodel_to_df(data), x_columns))
    y = get_target_column(basemodel_to_df(data), y_column)
    results = sm.OLS(y, X).fit()
    return OBBject(results=Data(score=durbin_watson(results.resid)))


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Perform Breusch-Godfrey Lagrange Multiplier tests for residual autocorrelation.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                'obb.econometrics.residual_autocorrelation(data=stock_data, y_column="close", x_columns=["open", "high", "low"])',  # noqa: E501  pylint: disable=line-too-long
            ],
        ),
        APIEx(
            parameters={
                "y_column": "close",
                "x_columns": ["open", "high", "low"],
                "data": APIEx.mock_data("timeseries"),
            }
        ),
    ],
)
def residual_autocorrelation(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
    lags: PositiveInt = 1,
) -> OBBject[Data]:
    """Perform Breusch-Godfrey Lagrange Multiplier tests for residual autocorrelation.

    The Breusch-Godfrey Lagrange Multiplier test is a sophisticated tool for uncovering autocorrelation within the
    residuals of a regression model. Autocorrelation in residuals can indicate that a model fails to capture some
    aspect of the underlying data structure, possibly leading to biased or inefficient estimates.
    By specifying the number of lags, you can control the depth of the test to check for autocorrelation,
    allowing for a tailored analysis that matches the specific characteristics of your data.
    This test is particularly valuable in econometrics and time-series analysis, where understanding the independence
    of errors is crucial for model validity.

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
    OBBject[Data]
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


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Perform co-integration test between two timeseries.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                'obb.econometrics.cointegration(data=stock_data, columns=["open", "close"])',
            ],
        ),
    ],
)
def cointegration(
    data: List[Data],
    columns: List[str],
) -> OBBject[Data]:
    """Show co-integration between two timeseries using the two step Engle-Granger test.

    The two-step Engle-Granger test is a method designed to detect co-integration between two time series.
    Co-integration is a statistical property indicating that two or more time series move together over the long term,
    even if they are individually non-stationary. This concept is crucial in economics and finance, where identifying
    pairs or groups of assets that share a common stochastic trend can inform long-term investment strategies
    and risk management practices. The Engle-Granger test first checks for a stable, long-term relationship by
    regressing one time series on the other and then tests the residuals for stationarity.
    If the residuals are found to be stationary, it suggests that despite any short-term deviations,
    the series are bound by an equilibrium relationship over time.

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


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Perform Granger causality test to determine if X 'causes' y.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                'obb.econometrics.causality(data=stock_data, y_column="close", x_column="open")',
            ],
        ),
        APIEx(
            description="Example with mock data.",
            parameters={
                "y_column": "close",
                "x_column": "open",
                "lag": 1,
                "data": APIEx.mock_data("timeseries"),
            },
        ),
    ],
)
def causality(
    data: List[Data],
    y_column: str,
    x_column: str,
    lag: PositiveInt = 3,
) -> OBBject[Data]:
    """Perform Granger causality test to determine if X 'causes' y.

    The Granger causality test is a statistical hypothesis test to determine if one time series is useful in
    forecasting another. While 'causality' in this context does not imply a cause-and-effect relationship in
    the philosophical sense, it does test whether changes in one variable are systematically followed by changes
    in another variable, suggesting a predictive relationship. By specifying a lag, you set the number of periods to
    look back in the time series to assess this relationship. This test is particularly useful in economic and
    financial data analysis, where understanding the lead-lag relationship between indicators can inform investment
    decisions and policy making.

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
    OBBject[Data]
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


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Perform Augmented Dickey-Fuller (ADF) unit root test.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                'obb.econometrics.unit_root(data=stock_data, column="close")',
                'obb.econometrics.unit_root(data=stock_data, column="close", regression="ct")',
            ],
        ),
        APIEx(
            parameters={
                "column": "close",
                "data": APIEx.mock_data("timeseries"),
            }
        ),
    ],
)
def unit_root(
    data: List[Data],
    column: str,
    regression: Literal["c", "ct", "ctt"] = "c",
) -> OBBject[Data]:
    """Perform Augmented Dickey-Fuller (ADF) unit root test.

    The ADF test is a popular method for testing the presence of a unit root in a time series.
    A unit root indicates that the series may be non-stationary, meaning its statistical properties such as mean,
    variance, and autocorrelation can change over time. The presence of a unit root suggests that the time series might
    be influenced by a random walk process, making it unpredictable and challenging for modeling and forecasting.
    The 'regression' parameter allows you to specify the model used in the test: 'c' for a constant term,
    'ct' for a constant and trend term, and 'ctt' for a constant, linear, and quadratic trend.
    This flexibility helps tailor the test to the specific characteristics of your data, providing a more accurate
    assessment of its stationarity.

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
    OBBject[Data]
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


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "y_column": "portfolio_value",
                "x_columns": ["risk_free_rate"],
                "data": APIEx.mock_data("panel"),
            }
        ),
    ],
)
def panel_random_effects(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """Perform One-way Random Effects model for panel data.

    One-way Random Effects model to panel data is offering a nuanced approach to analyzing data that spans across both
    time and entities (such as individuals, companies, countries, etc.). By acknowledging and modeling the random
    variation that exists within these entities, this method provides insights into the general patterns that
    emerge across the dataset.

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
    OBBject[Dict]
        OBBject with the fit model returned
    """
    X = get_target_columns(basemodel_to_df(data), x_columns)
    if len(X) < 3:
        raise ValueError("This analysis requires at least 3 items in the dataset.")
    y = get_target_column(basemodel_to_df(data), y_column)
    exogenous = sm.add_constant(X)
    results = RandomEffects(y, exogenous).fit()
    return OBBject(results={"results": results})


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "y_column": "portfolio_value",
                "x_columns": ["risk_free_rate"],
                "data": APIEx.mock_data("panel"),
            }
        ),
    ],
)
def panel_between(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """Perform a Between estimator regression on panel data.

    The Between estimator for regression analysis on panel data is focusing on the differences between entities
    (such as individuals, companies, or countries) over time. By aggregating the data for each entity and analyzing the
    average outcomes, this method provides insights into the overall impact of explanatory variables (x_columns) on
    the dependent variable (y_column) across all entities.

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
    OBBject[Dict]
        OBBject with the fit model returned
    """
    X = get_target_columns(basemodel_to_df(data), x_columns)
    y = get_target_column(basemodel_to_df(data), y_column)
    exogenous = sm.add_constant(X)
    results = BetweenOLS(y, exogenous).fit()
    return OBBject(results={"results": results})


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "y_column": "portfolio_value",
                "x_columns": ["risk_free_rate"],
                "data": APIEx.mock_data("panel"),
            }
        ),
    ],
)
def panel_pooled(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """Perform a Pooled coefficient estimator regression on panel data.

    The Pooled coefficient estimator for regression analysis on panel data is treating the data as a large
    cross-section without distinguishing between variations across time or entities
    (such as individuals, companies, or countries). By assuming that the explanatory variables (x_columns) have a
    uniform effect on the dependent variable (y_column) across all entities and time periods, this method simplifies
    the analysis and provides a generalized view of the relationships within the data.

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
    OBBject[Dict]
        OBBject with the fit model returned
    """
    X = get_target_columns(basemodel_to_df(data), x_columns)
    y = get_target_column(basemodel_to_df(data), y_column)
    exogenous = sm.add_constant(X)
    results = PooledOLS(y, exogenous).fit()
    return OBBject(results={"results": results})


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "y_column": "portfolio_value",
                "x_columns": ["risk_free_rate"],
                "data": APIEx.mock_data("panel"),
            }
        ),
    ],
)
def panel_fixed(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """One- and two-way fixed effects estimator for panel data.

    The Fixed Effects estimator to panel data is enabling a focused analysis on the unique characteristics of entities
    (such as individuals, companies, or countries) and/or time periods. By controlling for entity-specific and/or
    time-specific influences, this method isolates the effect of explanatory variables (x_columns) on the dependent
    variable (y_column), under the assumption that these entity or time effects capture unobserved heterogeneity.

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
    OBBject[Dict]
        OBBject with the fit model returned
    """
    X = get_target_columns(basemodel_to_df(data), x_columns)
    y = get_target_column(basemodel_to_df(data), y_column)
    exogenous = sm.add_constant(X)
    results = PanelOLS(y, exogenous).fit()
    return OBBject(results={"results": results})


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "y_column": "portfolio_value",
                "x_columns": ["risk_free_rate"],
                "data": APIEx.mock_data("panel"),
            }
        ),
    ],
)
def panel_first_difference(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """Perform a first-difference estimate for panel data.

    The First-Difference estimator for panel data analysis is focusing on the changes between consecutive observations
    for each entity (such as individuals, companies, or countries). By differencing the data, this method effectively
    removes entity-specific effects that are constant over time, allowing for the examination of the impact of changes
    in explanatory variables (x_columns) on the change in the dependent variable (y_column).

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
    OBBject[Dict]
        OBBject with the fit model returned
    """
    X = get_target_columns(basemodel_to_df(data), x_columns)
    y = get_target_column(basemodel_to_df(data), y_column)
    exogenous = X
    results = FirstDifferenceOLS(y, exogenous).fit()
    return OBBject(results={"results": results})


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "y_column": "portfolio_value",
                "x_columns": ["risk_free_rate"],
                "data": APIEx.mock_data("panel"),
            }
        ),
    ],
)
def panel_fmac(
    data: List[Data],
    y_column: str,
    x_columns: List[str],
) -> OBBject[Dict]:
    """Fama-MacBeth estimator for panel data.

    The Fama-MacBeth estimator, a two-step procedure renowned for its application in finance to estimate the risk
    premiums and evaluate the capital asset pricing model. By first estimating cross-sectional regressions for each
    time period and then averaging the regression coefficients over time, this method provides insights into the
    relationship between the dependent variable (y_column) and explanatory variables (x_columns) across different
    entities (such as individuals, companies, or countries).

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
    OBBject[Dict]
        OBBject with the fit model returned
    """
    X = get_target_columns(basemodel_to_df(data), x_columns)
    y = get_target_column(basemodel_to_df(data), y_column)
    exogenous = sm.add_constant(X)
    results = FamaMacBeth(y, exogenous).fit()
    return OBBject(results={"results": results})
