""""""  #
"""
Copyright (c) 2020-2022, Dany Cajas
All rights reserved.
This work is licensed under BSD 3-Clause "New" or "Revised" License.
License available at https://github.com/dcajasn/Riskfolio-Lib/blob/master/LICENSE.txt
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import sklearn.covariance as skcov
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from numpy.linalg import inv
import openbb_terminal.portfolio.portfolio_optimization.riskfolio.AuxFunctions as af
import arch.bootstrap as bs
import openbb_terminal.portfolio.portfolio_optimization.riskfolio.DBHT as db


def mean_vector(X, method="hist", d=0.94):
    r"""
    Calculate the expected returns vector using the selected method.

    Parameters
    ----------
    X : DataFrame of shape (n_samples, n_features)
        Features matrix, where n_samples is the number of samples and
        n_features is the number of features.
    method : str, optinal
        The method used to estimate the expected returns.
        The default value is 'hist'. Posible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
    d : scalar
        The smoothing factor of ewma methods.
        The default is 0.94.

    Returns
    -------
    mu : 1d-array
        The estimation of expected returns.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    """

    if not isinstance(X, pd.DataFrame):
        raise ValueError("X must be a DataFrame")

    assets = X.columns.tolist()

    if method == "hist":
        mu = np.array(X.mean(), ndmin=2)
    elif method == "ewma1":
        mu = np.array(X.ewm(alpha=1 - d).mean().iloc[-1, :], ndmin=2)
    elif method == "ewma2":
        mu = np.array(X.ewm(alpha=1 - d, adjust=False).mean().iloc[-1, :], ndmin=2)

    mu = pd.DataFrame(np.array(mu, ndmin=2), columns=assets)

    return mu


def covar_matrix(X, method="hist", d=0.94, **kwargs):
    r"""
    Calculate the covariance matrix using the selected method.

    Parameters
    ----------
    X : DataFrame of shape (n_samples, n_features)
        Features matrix, where n_samples is the number of samples and
        n_features is the number of features.
    method : str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Posible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: :cite:`b-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of :cite:`b-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of :cite:`b-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of :cite:`b-MLforAM`.
    d : scalar
        The smoothing factor of ewma methods.
        The default is 0.94.
    **kwargs:
        Other variables related to covariance estimation. See
        `Scikit Learn <https://scikit-learn.org/stable/modules/covariance.html>`_
        and chapter 2 of :cite:`b-MLforAM` for more details.

    Returns
    -------
    cov : nd-array
        The estimation of covariance matrix.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    """

    if not isinstance(X, pd.DataFrame):
        raise ValueError("X must be a DataFrame")

    assets = X.columns.tolist()

    if method == "hist":
        cov = np.cov(X.T)
    elif method == "ewma1":
        cov = X.ewm(alpha=1 - d).cov()
        item = cov.iloc[-1, :].name[0]
        cov = cov.loc[(item, slice(None)), :]
    elif method == "ewma2":
        cov = X.ewm(alpha=1 - d, adjust=False).cov()
        item = cov.iloc[-1, :].name[0]
        cov = cov.loc[(item, slice(None)), :]
    elif method == "ledoit":
        lw = skcov.LedoitWolf(**kwargs)
        lw.fit(X)
        cov = lw.covariance_
    elif method == "oas":
        oas = skcov.OAS(**kwargs)
        oas.fit(X)
        cov = oas.covariance_
    elif method == "shrunk":
        sc = skcov.ShrunkCovariance(**kwargs)
        sc.fit(X)
        cov = sc.covariance_
    elif method == "gl":
        gl = skcov.GraphicalLassoCV(**kwargs)
        gl.fit(X)
        cov = gl.covariance_
    elif method == "jlogo":
        S = np.cov(X.T)
        R = np.corrcoef(X.T)
        D = np.sqrt(np.clip((1 - R) / 2, a_min=0.0, a_max=1.0))
        (_, _, separators, cliques, _) = db.PMFG_T2s(1 - D**2, nargout=4)
        cov = db.j_LoGo(S, separators, cliques)
        cov = np.linalg.inv(cov)
    elif method in ["fixed", "spectral", "shrink"]:
        cov = np.cov(X.T)
        T, N = X.shape
        q = T / N
        cov = af.denoiseCov(cov, q, kind=method, **kwargs)

    cov = pd.DataFrame(np.array(cov, ndmin=2), columns=assets, index=assets)

    return cov


def forward_regression(X, y, criterion="pvalue", threshold=0.05, verbose=False):
    r"""
    Select the variables that estimate the best model using stepwise
    forward regression. In case none of the variables has a p-value lower
    than threshold, the algorithm will select the variable with lowest p-value.

    Parameters
    ----------
    X : DataFrame of shape (n_samples, n_features)
        Features matrix, where n_samples is the number of samples and
        n_features is the number of features.
    y : Series of shape (n_samples, 1)
        Target vector, where n_samples in the number of samples.
    criterion : str, optional
        The default is 'pvalue'. Posible values of the criterion used to select
        the best features are:

        - 'pvalue': select the features based on p-values.
        - 'AIC': select the features based on lowest Akaike Information Criterion.
        - 'SIC': select the features based on lowest Schwarz Information Criterion.
        - 'R2': select the features based on highest R Squared.
        - 'R2_A': select the features based on highest Adjusted R Squared.

    thresholdt : scalar, optional
        Is the maximum p-value for each variable that will be
        accepted in the model. The default is 0.05.
    verbose : bool, optional
        Enable verbose output. The default is False.

    Returns
    -------
    value : list
        A list of the variables that produce the best model.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    """
    if not isinstance(X, pd.DataFrame):
        raise ValueError("X must be a DataFrame")

    if not isinstance(y, pd.DataFrame) and not isinstance(y, pd.Series):
        raise ValueError("y must be a column DataFrame")

    if isinstance(y, pd.DataFrame):
        if y.shape[0] > 1 and y.shape[1] > 1:
            raise ValueError("y must be a column DataFrame")

    included = []
    aic = 1e10
    sic = 1e10
    r2 = -1e10
    r2_a = -1e10
    pvalues = None

    if criterion == "pvalue":
        value = 0
        while value <= threshold:
            excluded = list(set(X.columns) - set(included))
            best_pvalue = 999999
            new_feature = None
            for i in excluded:
                factors = included + [i]
                X1 = X[factors]
                X1 = sm.add_constant(X1)
                results = sm.OLS(y, X1).fit()
                new_pvalues = results.pvalues
                new_pvalues = new_pvalues[new_pvalues.index != "const"]
                cond_1 = new_pvalues.max()
                if best_pvalue > new_pvalues[i] and cond_1 <= threshold:
                    best_pvalue = results.pvalues[i]
                    new_feature = i
                    pvalues = new_pvalues.copy()

            if pvalues is not None:
                value = pvalues[pvalues.index != "const"].max()

            if new_feature is None:
                break
            else:
                included.append(new_feature)

            if verbose:
                print("Add {} with p-value {:.6}".format(new_feature, best_pvalue))

        # This part is how to deal when there isn't an asset with pvalue lower than threshold
        if len(included) == 0:
            excluded = list(set(X.columns) - set(included))
            best_pvalue = 999999
            new_feature = None
            for i in excluded:
                factors = included + [i]
                X1 = X[factors]
                X1 = sm.add_constant(X1)
                results = sm.OLS(y, X1).fit()
                new_pvalues = results.pvalues
                new_pvalues = new_pvalues[new_pvalues.index != "const"]
                if best_pvalue > new_pvalues[i]:
                    best_pvalue = results.pvalues[i]
                    new_feature = i
                    pvalues = new_pvalues.copy()

            value = pvalues[pvalues.index != "const"].max()

            included.append(new_feature)

            if verbose:
                print(
                    "Add {} with p-value {:.6}".format(pvalues.idxmax(), pvalues.max())
                )

    else:
        excluded = X.columns.tolist()
        for i in range(X.shape[1]):
            j = 0
            value = None
            for i in excluded:
                factors = included.copy()
                factors.append(i)
                X1 = X[factors]
                X1 = sm.add_constant(X1)
                results = sm.OLS(y, X1).fit()

                if criterion == "AIC":
                    if results.aic < aic:
                        value = i
                        aic = results.aic
                if criterion == "SIC":
                    if results.bic < sic:
                        value = i
                        sic = results.bic
                if criterion == "R2":
                    if results.rsquared > r2:
                        value = i
                        r2 = results.rsquared
                if criterion == "R2_A":
                    if results.rsquared_adj > r2_a:
                        value = i
                        r2_a = results.rsquared_adj

                j += 1
                if j == len(excluded):
                    if value is None:
                        break
                    else:
                        excluded.remove(value)
                        included.append(value)
                        if verbose:
                            if criterion == "AIC":
                                print(
                                    "Add {} with AIC {:.6}".format(value, results.aic)
                                )
                            elif criterion == "SIC":
                                print(
                                    "Add {} with SIC {:.6}".format(value, results.bic)
                                )
                            elif criterion == "R2":
                                print(
                                    "Add {} with R2 {:.6}".format(
                                        value, results.rsquared
                                    )
                                )
                            elif criterion == "R2_A":
                                print(
                                    "Add {} with Adjusted R2 {:.6}".format(
                                        value, results.rsquared_adj
                                    )
                                )

    return included


def backward_regression(X, y, criterion="pvalue", threshold=0.05, verbose=False):
    r"""
    Select the variables that estimate the best model using stepwise
    backward regression. In case none of the variables has a p-value lower
    than threshold, the algorithm will select the variable with lowest p-value.

    Parameters
    ----------
    X : DataFrame of shape (n_samples, n_features)
        Features matrix, where n_samples is the number of samples and
        n_features is the number of features.
    y : Series of shape (n_samples, 1)
        Target vector, where n_samples in the number of samples.
    criterion : str, optional
        The default is 'pvalue'. Posible values of the criterion used to select
        the best features are:

        - 'pvalue': select the features based on p-values.
        - 'AIC': select the features based on lowest Akaike Information Criterion.
        - 'SIC': select the features based on lowest Schwarz Information Criterion.
        - 'R2': select the features based on highest R Squared.
        - 'R2_A': select the features based on highest Adjusted R Squared.
    threshold : scalar, optional
        Is the maximum p-value for each variable that will be
        accepted in the model. The default is 0.05.
    verbose : bool, optional
        Enable verbose output. The default is False.

    Returns
    -------
    value : list
        A list of the variables that produce the best model.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    """

    if not isinstance(X, pd.DataFrame):
        raise ValueError("X must be a DataFrame")

    if not isinstance(y, pd.DataFrame) and not isinstance(y, pd.Series):
        raise ValueError("y must be a column DataFrame")

    if isinstance(y, pd.DataFrame):
        if y.shape[0] > 1 and y.shape[1] > 1:
            raise ValueError("y must be a column DataFrame")

    X1 = sm.add_constant(X)
    results = sm.OLS(y, X1).fit()
    pvalues = results.pvalues
    aic = results.aic
    sic = results.bic
    r2 = results.rsquared
    r2_a = results.rsquared_adj

    included = pvalues.index.tolist()
    excluded = ["const"]

    if criterion == "pvalue":
        while pvalues[pvalues.index != "const"].max() > threshold:
            factors = pvalues[~pvalues.index.isin(excluded)].index.tolist()
            X1 = X[factors]
            X1 = sm.add_constant(X1)
            results = sm.OLS(y, X1).fit()
            pvalues = results.pvalues
            pvalues = pvalues[pvalues.index != "const"]
            if pvalues.shape[0] == 0:
                break
            excluded = ["const", pvalues.idxmax()]
            if verbose and pvalues.max() > threshold:
                print(
                    "Drop {} with p-value {:.6}".format(pvalues.idxmax(), pvalues.max())
                )

        included = pvalues.index.tolist()

        # This part is how to deal when there isn't an asset with pvalue lower than threshold
        if len(included) == 0:
            excluded = list(set(X.columns) - set(included))
            best_pvalue = 999999
            new_feature = None
            for i in excluded:
                factors = included + [i]
                X1 = X[factors]
                X1 = sm.add_constant(X1)
                results = sm.OLS(y, X1).fit()
                new_pvalues = results.pvalues
                new_pvalues = results.pvalues
                new_pvalues = new_pvalues[new_pvalues.index != "const"]
                if best_pvalue > new_pvalues[i]:
                    best_pvalue = results.pvalues[i]
                    new_feature = i
                    pvalues = new_pvalues.copy()

            value = pvalues[pvalues.index != "const"].max()

            included.append(new_feature)

            if verbose:
                print(
                    "Add {} with p-value {:.6}".format(pvalues.idxmax(), pvalues.max())
                )

    else:
        included.remove("const")
        for i in range(X.shape[1]):
            j = 0
            value = None
            for i in included:
                factors = included.copy()
                factors.remove(i)
                X1 = X[factors]
                X1 = sm.add_constant(X1)
                results = sm.OLS(y, X1).fit()

                if criterion == "AIC":
                    if results.aic < aic:
                        value = i
                        aic = results.aic
                elif criterion == "SIC":
                    if results.bic < sic:
                        value = i
                        sic = results.bic
                elif criterion == "R2":
                    if results.rsquared > r2:
                        value = i
                        r2 = results.rsquared
                elif criterion == "R2_A":
                    if results.rsquared_adj > r2_a:
                        value = i
                        r2_a = results.rsquared_adj

                j += 1
                if j == len(included):
                    if value is None:
                        break
                    else:
                        included.remove(value)
                        if verbose:
                            if criterion == "AIC":
                                print(
                                    "Drop {} with AIC {:.6}".format(value, results.aic)
                                )
                            elif criterion == "SIC":
                                print(
                                    "Drop {} with SIC {:.6}".format(value, results.bic)
                                )
                            elif criterion == "R2":
                                print(
                                    "Drop {} with R2 {:.6}".format(
                                        value, results.rsquared
                                    )
                                )
                            elif criterion == "R2_A":
                                print(
                                    "Drop {} with Adjusted R2 {:.6}".format(
                                        value, results.rsquared_adj
                                    )
                                )

    return included


def PCR(X, y, n_components=0.95):
    r"""
    Estimate the coeficients using Principal Components Regression (PCR).

    Parameters
    ----------
    X : DataFrame of shape (n_samples, n_features)
        Features matrix, where n_samples is the number of samples and
        n_features is the number of features.
    y : Series of shape (n_samples, 1)
        Target vector, where n_samples in the number of samples.
    n_components : int, float, None or str, optional
        if 1 < n_components (int), it represents the number of components that
        will be keep. if 0 < n_components < 1 (float), it represents the
        percentage of variance that the is explained by the components keeped.
        See `PCA <https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html>`_
        for more details. The default is 0.95.

    Returns
    -------
    value : nd-array
        An array with the coefficients of the model calculated using PCR.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    """

    if not isinstance(X, pd.DataFrame):
        raise ValueError("X must be a DataFrame")

    if not isinstance(y, pd.DataFrame) and not isinstance(y, pd.Series):
        raise ValueError("y must be a column DataFrame")

    if isinstance(y, pd.DataFrame):
        if y.shape[0] > 1 and y.shape[1] > 1:
            raise ValueError("y must be a column DataFrame")

    scaler = StandardScaler()
    scaler.fit(X)
    X_std = scaler.transform(X)

    pca = PCA(n_components=n_components)
    pca.fit(X_std)
    Z_p = pca.transform(X_std)
    V_p = pca.components_.T

    results = sm.OLS(y, sm.add_constant(Z_p)).fit()
    beta_pc = results.params[1:]
    beta_pc = np.array(beta_pc, ndmin=2)

    std = np.array(np.std(X, axis=0, ddof=1), ndmin=2)
    mean = np.array(np.mean(X, axis=0), ndmin=2)
    beta = V_p @ beta_pc.T / std.T

    beta_0 = np.array(y.mean(), ndmin=2) - np.sum(beta * mean.T)

    beta = np.insert(beta, 0, beta_0)
    beta = np.array(beta, ndmin=2)

    return beta


def loadings_matrix(
    X,
    Y,
    feature_selection="stepwise",
    stepwise="Forward",
    criterion="pvalue",
    threshold=0.05,
    n_components=0.95,
    verbose=False,
):
    r"""
    Estimate the loadings matrix using stepwise regression.

    Parameters
    ----------
    X : DataFrame of shape (n_samples, n_features)
        Features matrix, where n_samples is the number of samples and
        n_features is the number of features.
    Y : DataFrame of shape (n_samples, n_assets)
        Target matrix, where n_samples in the number of samples and
        n_assets is the number of assets.
    feature_selection: str 'stepwise' or 'PCR', optional
        Indicate the method used to estimate the loadings matrix.
        The default is 'stepwise'.
    stepwise: str 'Forward' or 'Backward', optional
        Indicate the method used for stepwise regression.
        The default is 'Forward'.
    criterion : str, optional
        The default is 'pvalue'. Posible values of the criterion used to select
        the best features are:

        - 'pvalue': select the features based on p-values.
        - 'AIC': select the features based on lowest Akaike Information Criterion.
        - 'SIC': select the features based on lowest Schwarz Information Criterion.
        - 'R2': select the features based on highest R Squared.
        - 'R2_A': select the features based on highest Adjusted R Squared.
    threshold : scalar, optional
        Is the maximum p-value for each variable that will be
        accepted in the model. The default is 0.05.
    n_components : int, float, None or str, optional
        if 1 < n_components (int), it represents the number of components that
        will be keep. if 0 < n_components < 1 (float), it represents the
        percentage of variance that the is explained by the components keeped.
        See `PCA <https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html>`_
        for more details. The default is 0.95.
    verbose : bool, optional
        Enable verbose output. The default is False.

    Returns
    -------
    loadings : DataFrame
        A DataFrame with the loadings matrix.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    """
    if not isinstance(X, pd.DataFrame):
        raise ValueError("X must be a DataFrame")

    if not isinstance(Y, pd.DataFrame):
        raise ValueError("Y must be a DataFrame")

    rows = Y.columns.tolist()
    cols = X.columns.tolist()
    cols.insert(0, "const")
    loadings = np.zeros((len(rows), len(cols)))
    loadings = pd.DataFrame(loadings, index=rows, columns=cols)

    for i in rows:
        if feature_selection == "stepwise":
            if stepwise == "Forward":
                included = forward_regression(
                    X, Y[i], criterion=criterion, threshold=threshold, verbose=verbose
                )
            elif stepwise == "Backward":
                included = backward_regression(
                    X, Y[i], criterion=criterion, threshold=threshold, verbose=verbose
                )
            else:
                raise ValueError("Choose and adecuate stepwise method")
            results = sm.OLS(Y[i], sm.add_constant(X[included])).fit()
            params = results.params
            loadings.loc[i, params.index.tolist()] = params.T
        elif feature_selection == "PCR":
            beta = PCR(X, Y[i], n_components=n_components)
            beta = pd.Series(np.ravel(beta), index=cols)
            loadings.loc[i, cols] = beta.T

    return loadings


def risk_factors(
    X,
    Y,
    B=None,
    const=False,
    method_mu="hist",
    method_cov="hist",
    feature_selection="stepwise",
    stepwise="Forward",
    criterion="pvalue",
    threshold=0.05,
    n_components=0.95,
    error=True,
    **kwargs
):
    r"""
    Estimate the expected returns vector and covariance matrix based on risk
    factors models :cite:`b-Ross` :cite:`b-Fan`.

    .. math::
        \begin{aligned}
        R & = \alpha + B F + \epsilon \\
        \mu_{f} & = \alpha +BE(F) \\
        \Sigma_{f} & = B \Sigma_{F} B^{T} + \Sigma_{\epsilon} \\
        \end{aligned}
        
        
    where:

    :math:`R` is the series returns.

    :math:`\alpha` is the intercept.

    :math:`B` is the loadings matrix.

    :math:`F` is the expected returns vector of the risk factors.

    :math:`\Sigma_{F}` is the covariance matrix of the risk factors.

    :math:`\Sigma_{\epsilon}` is the covariance matrix of error terms.

    :math:`\mu_{f}` is the expected returns vector obtained with the
    risk factor model.

    :math:`\Sigma_{f}` is the covariance matrix obtained with the risk
    factor model.

    Parameters
    ----------
    X : DataFrame of shape (n_samples, n_features)
        Features matrix, where n_samples is the number of samples and
        n_features is the number of features.
    Y : DataFrame of shape (n_samples, n_assets)
        Target matrix, where n_samples in the number of samples and
        n_assets is the number of assets.
    B : DataFrame of shape (n_assets, n_features), optional
        Loadings matrix. If is not specified, is estimated using
        stepwise regression. The default is None.
    const : bool, optional
        Indicate if the loadings matrix has a constant.
        The default is False.
    method: str, 'stepwise' or 'PCR', optional
        Indicate the method used to estimate the loadings matrix.
        The default is 'stepwise'.
    stepwise: str, 'Forward' or 'Backward'
        Indicate the method used for stepwise regression.
        The default is 'Forward'.
    criterion : str, optional
        The default is 'pvalue'. Posible values of the criterion used to select
        the best features are:

        - 'pvalue': select the features based on p-values.
        - 'AIC': select the features based on lowest Akaike Information Criterion.
        - 'SIC': select the features based on lowest Schwarz Information Criterion.
        - 'R2': select the features based on highest R Squared.
        - 'R2_A': select the features based on highest Adjusted R Squared.
    threshold : scalar, optional
        Is the maximum p-value for each variable that will be
        accepted in the model. The default is 0.05.
    n_components : int, float, None or str, optional
        if 1 < n_components (int), it represents the number of components that
        will be keep. if 0 < n_components < 1 (float), it represents the
        percentage of variance that the is explained by the components keeped.
        See `PCA <https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html>`_
        for more details. The default is 0.95.
    error : bool
        Indicate if diagonal covariance matrix of errors is included (only
        when B is estimated through a regression).
    **kwargs : dict
        Other variables related to the expected returns and covariance estimation.

    Returns
    -------
    mu : DataFrame
        The mean vector of risk factors model.
    cov : DataFrame
        The covariance matrix of risk factors model.
    returns : DataFrame
        The returns based on a risk factor model.
    nav : DataFrame
        The cumulated uncompound returns based on a risk factor model.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    """
    if not isinstance(X, pd.DataFrame) and not isinstance(Y, pd.DataFrame):
        raise ValueError("X and Y must be DataFrames")

    if B is None:
        B = loadings_matrix(
            X,
            Y,
            feature_selection=feature_selection,
            stepwise=stepwise,
            criterion=criterion,
            threshold=threshold,
            n_components=n_components,
            verbose=False,
        )
    elif not isinstance(B, pd.DataFrame):
        raise ValueError("B must be a DataFrame")

    X1 = X.copy()
    if const == True or "const" in B.columns.tolist():
        X1 = sm.add_constant(X)

    assets = Y.columns.tolist()
    dates = X.index.tolist()

    mu_f = np.array(mean_vector(X1, method=method_mu, **kwargs), ndmin=2)
    S_f = np.array(covar_matrix(X1, method=method_cov, **kwargs), ndmin=2)
    B = np.array(B, ndmin=2)

    returns = np.array(X1, ndmin=2) @ B.T
    mu = B @ mu_f.T

    if error == True:
        e = np.array(Y, ndmin=2) - returns
        S_e = np.diag(np.var(np.array(e), ddof=1, axis=0))
        S = B @ S_f @ B.T + S_e
    elif error == False:
        S = B @ S_f @ B.T

    mu = pd.DataFrame(mu.T, columns=assets)
    cov = pd.DataFrame(S, index=assets, columns=assets)
    returns = pd.DataFrame(returns, index=dates, columns=assets)
    nav = returns.cumsum()

    return mu, cov, returns, nav


def black_litterman(
    X, w, P, Q, delta=1, rf=0, eq=True, method_mu="hist", method_cov="hist", **kwargs
):
    r"""
    Estimate the expected returns vector and covariance matrix based
    on the Black Litterman model :cite:`b-BlackLitterman` :cite:`b-Black1`.

    .. math::
        \begin{aligned}
        \Pi & = \delta \Sigma w \\
        \Pi_{BL} & = \left [ (\tau\Sigma)^{-1}+ P^{T} \Omega^{-1}P \right]^{-1}
        \left[(\tau\Sigma)^{-1} \Pi + P^{T} \Omega^{-1} Q \right] \\
        M & = \left((\tau\Sigma)^{-1} + P^{T}\Omega^{-1} P \right)^{-1} \\
        \mu_{BL} & = \Pi_{BL} + r_{f} \\
        \Sigma_{BL} & = \Sigma + M \\
        \end{aligned}


    where:

    :math:`r_{f}` is the risk free rate.

    :math:`\delta` is the risk aversion factor.

    :math:`\Pi` is the equilibrium excess returns.

    :math:`\Sigma` is the covariance matrix.

    :math:`P` is the views matrix.

    :math:`Q` is the views returns matrix.

    :math:`\Omega` is the covariance matrix of the error views.

    :math:`\mu_{BL}` is the mean vector obtained with the black
    litterman model.

    :math:`\Sigma_{BL}` is the covariance matrix obtained with the black
    litterman model.

    Parameters
    ----------
    X : DataFrame of shape (n_samples, n_assets)
        Assets matrix, where n_samples is the number of samples and
        n_assets is the number of assets.
    w : DataFrame of shape (n_assets, 1)
        Weights matrix, where n_assets is the number of assets.
    P : DataFrame of shape (n_views, n_assets)
        Analyst's views matrix, can be relative or absolute.
    Q : DataFrame of shape (n_views, 1)
        Expected returns of analyst's views.
    delta : float, optional
        Risk aversion factor. The default value is 1.
    rf : scalar, optional
        Risk free rate. The default is 0.
    eq : bool, optional
        Indicate if use equilibrum or historical excess returns.
        The default is True.
    method_mu : str, can be {'hist', 'ewma1' or 'ewma2'}
        The method used to estimate the expected returns.
        The default value is 'hist'.

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
    method_cov : str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Posible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: :cite:`b-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of :cite:`b-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of :cite:`b-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of :cite:`b-MLforAM`.
    **kwargs : dict
        Other variables related to the expected returns and covariance estimation.

    Returns
    -------
    mu : DataFrame
        The mean vector of Black Litterman model.
    cov : DataFrame
        The covariance matrix of Black Litterman model.
    w : DataFrame
        The equilibrium weights of Black Litterman model, without constraints.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    """
    if not isinstance(X, pd.DataFrame) and not isinstance(w, pd.DataFrame):
        raise ValueError("X and w must be DataFrames")

    if w.shape[0] > 1 and w.shape[1] > 1:
        raise ValueError("w must be a column DataFrame")

    assets = X.columns.tolist()

    w = np.array(w, ndmin=2)
    if w.shape[0] == 1:
        w = w.T

    mu = np.array(mean_vector(X, method=method_mu, **kwargs), ndmin=2)
    S = np.array(covar_matrix(X, method=method_cov, **kwargs), ndmin=2)
    P = np.array(P, ndmin=2)
    Q = np.array(Q, ndmin=2)
    tau = 1 / X.shape[0]
    Omega = np.array(np.diag(np.diag(P @ (tau * S) @ P.T)), ndmin=2)

    if eq == True:
        PI = delta * (S @ w)
    elif eq == False:
        PI = mu.T - rf

    PI_ = inv(inv(tau * S) + P.T @ inv(Omega) @ P) @ (
        inv(tau * S) @ PI + P.T @ inv(Omega) @ Q
    )
    M = inv(inv(tau * S) + P.T @ inv(Omega) @ P)
    # PI_1 = PI + (tau * S* P.T) * inv(P * tau * S * P.T + Omega) * (Q - P * PI)
    # M = tau * S - (tau * S * P.T) * inv(P * tau * S * P.T + Omega) * P * tau * S

    mu = PI_ + rf
    mu = mu.T
    cov = S + M
    w = inv(delta * cov) @ PI_

    mu = pd.DataFrame(mu, columns=assets)
    cov = pd.DataFrame(cov, index=assets, columns=assets)
    w = pd.DataFrame(w, index=assets)

    return mu, cov, w


def augmented_black_litterman(
    X,
    w,
    F=None,
    B=None,
    P=None,
    Q=None,
    P_f=None,
    Q_f=None,
    delta=1,
    rf=0,
    eq=True,
    const=True,
    method_mu="hist",
    method_cov="hist",
    **kwargs
):
    r"""
    Estimate the expected returns vector and covariance matrix based
    on the Augmented Black Litterman model :cite:`b-WCheung`.

    .. math::
        \begin{aligned}
        \Pi^{a} & = \delta \left [ \begin{array}{c} \Sigma \\ \Sigma_{F} B^{T} \\ \end{array} \right ] w \\
        P^{a} & = \left [ \begin{array}{cc} P & 0 \\ 0 & P_{F} \\ \end{array} \right ] \\
        Q^{a} & = \left [ \begin{array}{c} Q \\ Q_{F} \\ \end{array} \right ] \\
        \Sigma^{a} & = \left [ \begin{array}{cc} \Sigma & B \Sigma_{F}\\ \Sigma_{F} B^{T} & \Sigma_{F} \\ \end{array} \right ] \\
        \Omega^{a} & = \left [ \begin{array}{cc} \Omega & 0 \\ 0 & \Omega_{F} \\ \end{array} \right ] \\
        \Pi^{a}_{BL} & = \left [ (\tau \Sigma^{a})^{-1} + (P^{a})^{T} (\Omega^{a})^{-1} P^{a} \right ]^{-1}
        \left [ (\tau\Sigma^{a})^{-1} \Pi^{a} + (P^{a})^{T} (\Omega^{a})^{-1} Q^{a} \right ] \\
        M^{a} & = \left ( (\tau\Sigma^{a})^{-1} + (P^{a})^{T} (\Omega^{a})^{-1} P^{a} \right )^{-1} \\
        \mu^{a}_{BL} & = \Pi^{a}_{BL} + r_{f} \\
        \Sigma^{a}_{BL} & = \Sigma^{a} + M^{a} \\
        \end{aligned}


    where:

    :math:`r_{f}` is the risk free rate.

    :math:`\delta` is the risk aversion factor.

    :math:`B` is the loadings matrix.
    
    :math:`\Sigma` is the covariance matrix of assets.
    
    :math:`\Sigma_{F}` is the covariance matrix of factors.

    :math:`\Sigma^{a}` is the augmented covariance matrix.
    
    :math:`P` is the assets views matrix.

    :math:`Q` is the assets views returns matrix.
    
    :math:`P_{F}` is the factors views matrix.

    :math:`Q_{F}` is the factors views returns matrix.    

    :math:`P^{a}` is the augmented views matrix.
    
    :math:`Q^{a}` is the augmented views returns matrix.
    
    :math:`\Pi^{a}` is the augmented equilibrium excess returns.

    :math:`\Omega` is the covariance matrix of errors of assets views.

    :math:`\Omega_{F}` is the covariance matrix of errors of factors views.

    :math:`\Omega^{a}` is the covariance matrix of errors of augmented views.

    :math:`\mu^{a}_{BL}` is the mean vector obtained with the Augmented Black
    Litterman model.

    :math:`\Sigma^{a}_{BL}` is the covariance matrix obtained with the Augmented
    Black Litterman model.

    Parameters
    ----------
    X : DataFrame of shape (n_samples, n_assets)
        Assets matrix, where n_samples is the number of samples and
        n_assets is the number of features.
    w : DataFrame of shape (n_assets, 1)
        Weights matrix, where n_assets is the number of assets.
    F : DataFrame of shape (n_samples, n_features)
        Features matrix, where n_samples is the number of samples and
        n_features is the number of features.
    B : DataFrame of shape (n_assets, n_features), optional
        Loadings matrix. The default is None.    
    P : DataFrame of shape (n_views, n_assets)
        Analyst's views matrix, can be relative or absolute.
    Q : DataFrame of shape (n_views, 1)
        Expected returns of analyst's views.
    P_f : DataFrame of shape (n_views, n_features)
        Analyst's factors views matrix, can be relative or absolute.
    Q_f : DataFrame of shape (n_views, 1)
        Expected returns of analyst's factors views.
    delta : float, optional
        Risk aversion factor. The default value is 1.
    rf : scalar, optional
        Risk free rate. The default is 0.
    eq : bool, optional
        Indicate if use equilibrum or historical excess returns.
        The default is True.
    const : bool, optional
        Indicate if use equilibrum or historical excess returns.
        The default is True.
    method_mu : str, can be {'hist', 'ewma1' or 'ewma2'}
        The method used to estimate the expected returns.
        The default value is 'hist'.

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
    method_cov : str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Posible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: :cite:`b-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of :cite:`b-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of :cite:`b-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of :cite:`b-MLforAM`.
    **kwargs : dict
        Other variables related to the expected returns and covariance estimation.

    Returns
    -------
    mu : DataFrame
        The mean vector of Augmented Black Litterman model.
    cov : DataFrame
        The covariance matrix of Augmented Black Litterman model.
    w : DataFrame
        The equilibrium weights of Augmented Black Litterman model, without constraints.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    """
    if not isinstance(X, pd.DataFrame) and not isinstance(w, pd.DataFrame):
        raise ValueError("X and w must be DataFrames")

    if not isinstance(F, pd.DataFrame) and not isinstance(B, pd.DataFrame):
        raise ValueError("F and B must be DataFrames")

    if w.shape[0] > 1 and w.shape[1] > 1:
        raise ValueError("w must be a column DataFrame")

    assets = X.columns.tolist()
    N = len(assets)

    w = np.array(w, ndmin=2)
    if w.shape[0] == 1:
        w = w.T

    if B is not None:
        B = np.array(B, ndmin=2)
        if const == True:
            alpha = B[:, :1]
            B = B[:, 1:]

    mu = np.array(mean_vector(X, method=method_mu, **kwargs), ndmin=2)
    S = np.array(covar_matrix(X, method=method_cov, **kwargs), ndmin=2)

    tau = 1 / X.shape[0]

    if F is not None:
        mu_f = np.array(mean_vector(F, method=method_mu, **kwargs), ndmin=2)
        S_f = np.array(covar_matrix(F, method=method_cov, **kwargs), ndmin=2)

    if P is not None and Q is not None and P_f is None and Q_f is None:
        S_a = S
        P_a = P
        Q_a = Q
        Omega = np.array(np.diag(np.diag(P @ (tau * S) @ P.T)), ndmin=2)
        Omega_a = Omega

        if eq == True:
            PI_a_ = delta * S_a @ w
        elif eq == False:
            PI_a_ = mu.T - rf
    elif P is None and Q is None and P_f is not None and Q_f is not None:
        S_a = S_f
        P_a = P_f
        Q_a = Q_f
        Omega_f = np.array(np.diag(np.diag(P_f @ (tau * S_f) @ P_f.T)), ndmin=2)
        Omega_a = Omega_f

        if eq == True:
            PI_a_ = delta * (S_f @ B.T) @ w
        elif eq == False:
            PI_a_ = mu_f.T - rf

    elif P is not None and Q is not None and P_f is not None and Q_f is not None:
        S_a = np.hstack((np.vstack((S, S_f @ B.T)), np.vstack((B @ S_f, S_f))))

        P = np.array(P, ndmin=2)
        Q = np.array(Q, ndmin=2)
        P_f = np.array(P_f, ndmin=2)
        Q_f = np.array(Q_f, ndmin=2)
        zeros_1 = np.zeros((P_f.shape[0], P.shape[1]))
        zeros_2 = np.zeros((P.shape[0], P_f.shape[1]))
        P_a = np.hstack((np.vstack((P, zeros_1)), np.vstack((zeros_2, P_f))))
        Q_a = np.vstack((Q, Q_f))

        Omega = np.array(np.diag(np.diag(P @ (tau * S) @ P.T)), ndmin=2)
        Omega_f = np.array(np.diag(np.diag(P_f @ (tau * S_f) @ P_f.T)), ndmin=2)
        zeros = np.zeros((Omega.shape[0], Omega_f.shape[0]))
        Omega_a = np.hstack((np.vstack((Omega, zeros.T)), np.vstack((zeros, Omega_f))))

        if eq == True:
            PI_a_ = delta * (np.vstack((S, S_f @ B.T)) @ w)
        elif eq == False:
            PI_a_ = np.vstack((mu.T, mu_f.T)) - rf

    PI_a = inv(inv(tau * S_a) + P_a.T @ inv(Omega_a) @ P_a) @ (
        inv(tau * S_a) @ PI_a_ + P_a.T @ inv(Omega_a) @ Q_a
    )
    M_a = inv(inv(tau * S_a) + P_a.T @ inv(Omega_a) @ P_a)
    # PI_a = PI_a_ + (tau * S_a @ P_a.T) * inv(P_a @ tau * S_a @ P_a.T + Omega) * (Q_a - P_a @ PI_a_)
    # M = tau * S_a - (tau * S_a @ P_a.T) * inv(P_a @ tau * S_a @ P_a.T + Omega_a) @ P_a @ tau * S_a

    mu_a = PI_a + rf
    mu_a = mu_a.T
    cov_a = S_a + M_a
    w_a = inv(delta * cov_a) @ PI_a

    if P is None and Q is None and P_f is not None and Q_f is not None:
        mu_a = mu_a @ B.T
        cov_a = B @ cov_a @ B.T
        w_a = inv(delta * cov_a) @ B @ PI_a

    if const == True:
        mu_a = mu_a[:, :N] + alpha.T

    mu_a = pd.DataFrame(mu_a[:, :N], columns=assets)
    cov_a = pd.DataFrame(cov_a[:N, :N], index=assets, columns=assets)
    w_a = pd.DataFrame(w_a[:N, 0], index=assets)

    return mu_a, cov_a, w_a


def black_litterman_bayesian(
    X,
    F,
    B,
    P_f,
    Q_f,
    delta=1,
    rf=0,
    eq=True,
    const=True,
    diag=True,
    method_mu="hist",
    method_cov="hist",
    **kwargs
):
    r"""
    Estimate the expected returns vector and covariance matrix based
    on the black litterman model :cite:`b-BLB`.

    .. math::
        \begin{aligned}
        \Sigma_{F} & = B \Sigma_{F} B^{T} + D \\
        \overline{\Pi}_{F} & = \left ( \Sigma_{F}^{-1} + P_{F}^{T}\Omega_{F}^{-1}P_{F} \right )^{-1} \left ( \Sigma_{F}^{-1}\Pi_{F} + P_{F}^{T}\Omega_{F}^{-1}Q_{F} \right) \\
        \overline{\Sigma}_{F} & = \left ( \Sigma_{F}^{-1} + P_{F}^{T}\Omega_{F}^{-1}P_{F} \right )^{-1} \\
        \Sigma_{BLB} & = \left( \Sigma^{-1} - \Sigma^{-1} B \left( \overline{\Sigma}_{F}^{-1} + B^{T}\Sigma^{-1}B \right)^{-1} B^{T}\Sigma^{-1} \right )^{-1} \\
        \mu_{BLB} & = \Sigma_{BLB} \left ( \Sigma^{-1} B \left( \overline{\Sigma}_{F}^{-1} +B^{T}\Sigma^{-1}B \right)^{-1} \overline{\Sigma}_{F}^{-1} \overline{\Pi}_{F} \right ) + r_{f} \\
        \end{aligned}


    where:

    :math:`r_{f}` is the risk free rate.

    :math:`B` is the loadings matrix.

    :math:`D` is a diagonal matrix of variance of errors of a factor model.

    :math:`\Sigma` is the covariance matrix obtained with a factor model.

    :math:`\Pi_{F}` is the equilibrium excess returns of factors.

    :math:`\overline{\Pi}_{F}` is the posterior excess returns of factors.
    
    :math:`\Sigma_{F}` is the covariance matrix of factors.

    :math:`\overline{\Sigma}_{F}` is the posterior covariance matrix of factors.
    
    :math:`P_{F}` is the factors views matrix.

    :math:`Q_{F}` is the factors views returns matrix.    

    :math:`\Omega_{F}` is the covariance matrix of errors of factors views.

    :math:`\mu_{BLB}` is the mean vector obtained with the Black
    Litterman Bayesian model or posterior predictive mean.

    :math:`\Sigma_{BLB}` is the covariance matrix obtained with the Black
    Litterman Bayesian model or posterior predictive covariance.

    Parameters
    ----------
    X : DataFrame of shape (n_samples, n_assets)
        Assets matrix, where n_samples is the number of samples and
        n_assets is the number of assets.
    F : DataFrame of shape (n_samples, n_features)
        Features matrix, where n_samples is the number of samples and
        n_features is the number of features.
    B : DataFrame of shape (n_assets, n_features), optional
        Loadings matrix. The default is None.
    P_f : DataFrame of shape (n_views, n_features)
        Analyst's factors views matrix, can be relative or absolute.
    Q_f : DataFrame of shape (n_views, 1)
        Expected returns of analyst's factors views.
    delta : float, optional
        Risk aversion factor. The default value is 1.
    rf : scalar, optional
        Risk free rate. The default is 0.
    eq : bool, optional
        Indicate if use equilibrum or historical excess returns.
        The default is True.
    const : bool, optional
        Indicate if the loadings matrix has a constant.
        The default is True.
    diag : bool, optional
        Indicate if we use the diagonal matrix to calculate covariance matrix
        of factor model, only useful when we work with a factor model based on 
        a regresion model (only equity portfolio).
        The default is True.
    method_mu : str, can be {'hist', 'ewma1' or 'ewma2'}
        The method used to estimate the expected returns.
        The default value is 'hist'.

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
        - 'ewma2': use ewma with adjust=False, For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
    method_cov : str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Posible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: :cite:`b-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of :cite:`b-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of :cite:`b-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of :cite:`b-MLforAM`.
    **kwargs : dict
        Other variables related to the expected returns and covariance estimation.

    Returns
    -------
    mu : DataFrame
        The mean vector of Black Litterman model.
    cov : DataFrame
        The covariance matrix of Black Litterman model.
    w : DataFrame
        The equilibrium weights of Black Litterman model, without constraints.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    """
    if not isinstance(X, pd.DataFrame):
        raise ValueError("X must be DataFrames")

    if not isinstance(F, pd.DataFrame) and not isinstance(B, pd.DataFrame):
        raise ValueError("F and B must be DataFrames")

    assets = X.columns.tolist()

    if B is not None:
        B = np.array(B, ndmin=2)
        if const == True:
            alpha = B[:, :1]
            B = B[:, 1:]

    mu_f = np.array(mean_vector(F, method=method_mu, **kwargs), ndmin=2)
    mu_f = (mu_f - rf).T

    tau = 1 / X.shape[0]

    S_f = np.array(covar_matrix(F, method=method_cov, **kwargs), ndmin=2)
    S = B @ S_f @ B.T

    if diag == True:
        D = X.to_numpy() - F @ B.T
        D = np.diag(D.var())
        S = S + D

    Omega_f = np.array(np.diag(np.diag(P_f @ (tau * S_f) @ P_f.T)), ndmin=2)

    S_hat = inv(inv(S_f) + P_f.T @ inv(Omega_f) @ P_f)

    Pi_hat = S_hat @ (inv(S_f) @ mu_f + P_f.T @ inv(Omega_f) @ Q_f)

    S_blb = inv(inv(S) - inv(S) @ B @ inv(inv(S_hat) + B.T @ inv(S) @ B) @ B.T @ inv(S))

    Pi_blb = (
        S_blb @ inv(S) @ B @ inv(inv(S_hat) + B.T @ inv(S) @ B) @ inv(S_hat) @ Pi_hat
    )

    mu = Pi_blb + rf

    if const == True:
        mu = mu + alpha
    mu = mu.T
    cov = S_blb
    w = inv(delta * cov) @ mu.T

    mu = pd.DataFrame(mu, columns=assets)
    cov = pd.DataFrame(cov, index=assets, columns=assets)
    w = pd.DataFrame(w, index=assets)

    return mu, cov, w


def bootstrapping(X, kind="stationary", q=0.05, n_sim=3000, window=3, seed=0):
    r"""
    Estimates the uncertainty sets of mean and covariance matrix through the selected
    bootstrapping method.

    Parameters
    ----------
    X : DataFrame of shape (n_samples, n_features)
        Features matrix, where n_samples is the number of samples and
        n_features is the number of features.
    kind : str
        The bootstrapping method. The default value is 'stationary'. Posible values are:

        - 'stationary': stationary bootstrapping method, see `StationaryBootstrap <https://bashtage.github.io/arch/bootstrap/generated/arch.bootstrap.StationaryBootstrap.html#arch.bootstrap.StationaryBootstrap>`_ for more details.
        - 'circular': circular bootstrapping method, see `CircularBlockBootstrap <https://bashtage.github.io/arch/bootstrap/generated/arch.bootstrap.CircularBlockBootstrap.html#arch.bootstrap.CircularBlockBootstrap>`_ for more details.
        - 'moving': moving bootstrapping method, see `MovingBlockBootstrap <https://bashtage.github.io/arch/bootstrap/generated/arch.bootstrap.MovingBlockBootstrap.html#arch.bootstrap.MovingBlockBootstrap>`_ for more details.
    q : scalar
        Significance level of the selected bootstrapping method.
        The default is 0.05.
    n_sim : scalar
        Number of simulations of the bootstrapping method.
        The default is 3000.
    window:
        Block size of the bootstrapping method. Must be greather than 1
        and lower than the n_samples - n_features + 1
        The default is 3.
    seed:
        Seed used to generate random numbers for bootstrapping method.
        The default is 0.

    Returns
    -------
    mu_l : DataFrame
        The q/2 percentile of mean vector obtained through the selected bootstrapping method.
    mu_u : DataFrame
        The 1-q/2 percentile of mean vector obtained through the selected bootstrapping method.
    cov_l : DataFrame
        The q/2 percentile of covariance matrix obtained through the selected bootstrapping method.
    cov_u : DataFrame
        The 1-q/2 percentile of covariance matrix obtained through the selected bootstrapping method.
    cov_mu : DataFrame
        The covariance matrix of estimation errors of mean vector obtained through the selected bootstrapping method.
        We take the diagonal of this matrix following :cite:`b-fabozzi2007robust`.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    """

    if not isinstance(X, pd.DataFrame):
        raise ValueError("X must be a DataFrame")

    if window >= X.shape[0] - window + 1:
        raise ValueError("block must be lower than  n_samples - window + 1")
    elif window <= 1:
        raise ValueError("block must be greather than 1")

    cols = X.columns.tolist()
    cols_2 = [i + "-" + j for i in cols for j in cols]
    m = len(cols)
    mus = np.zeros((n_sim, 1, m))
    covs = np.zeros((n_sim, m, m))

    if kind == "stationary":
        gen = bs.StationaryBootstrap(window, X, seed=seed)
    elif kind == "circular":
        gen = bs.CircularBlockBootstrap(window, X, seed=seed)
    elif kind == "moving":
        gen = bs.MovingBlockBootstrap(window, X, seed=seed)
    else:
        raise ValueError("kind only can be 'stationary', 'circular' or 'moving'")

    i = 0
    for data in gen.bootstrap(n_sim):
        A = data[0][0]
        mus[i] = A.mean().to_numpy().reshape(1, m)
        covs[i] = A.cov().to_numpy()
        i += 1

    mu_l = np.percentile(mus, q / 2 * 100, axis=0, keepdims=True).reshape(1, m)
    mu_u = np.percentile(mus, 100 - q / 2 * 100, axis=0, keepdims=True).reshape(1, m)

    cov_l = np.percentile(covs, q / 2 * 100, axis=0, keepdims=True).reshape(m, m)
    cov_u = np.percentile(covs, 100 - q / 2 * 100, axis=0, keepdims=True).reshape(m, m)

    mu_l = pd.DataFrame(mu_l, index=[0], columns=cols)
    mu_u = pd.DataFrame(mu_u, index=[0], columns=cols)

    cov_l = pd.DataFrame(cov_l, index=cols, columns=cols)
    cov_u = pd.DataFrame(cov_u, index=cols, columns=cols)

    cov_mu = mus.reshape(n_sim, m) - X.mean().to_numpy().reshape(1, m)
    cov_mu = np.cov(cov_mu.T)

    cov_mu = np.diag(np.diag(cov_mu))
    cov_mu = pd.DataFrame(cov_mu, index=cols, columns=cols)

    cov_sigma = covs - X.cov().to_numpy()
    cov_sigma = cov_sigma.reshape((n_sim, m * m), order="F")
    cov_sigma = np.cov(cov_sigma.T)

    cov_sigma = np.diag(np.diag(cov_sigma))
    cov_sigma = pd.DataFrame(cov_sigma, index=cols_2, columns=cols_2)

    if af.is_pos_def(cov_l) == False:
        cov_l = af.cov_fix(cov_l, method="clipped", threshold=1e-3)

    if af.is_pos_def(cov_u) == False:
        cov_u = af.cov_fix(cov_u, method="clipped", threshold=1e-3)

    return mu_l, mu_u, cov_l, cov_u, cov_mu, cov_sigma
