""""""  #
"""
Copyright (c) 2020-2022, Dany Cajas
All rights reserved.
This work is licensed under BSD 3-Clause "New" or "Revised" License.
License available at https://github.com/dcajasn/Riskfolio-Lib/blob/master/LICENSE.txt
"""

import numpy as np
import pandas as pd
import cvxpy as cv
import scipy.stats as st
from scipy.linalg import sqrtm
import openbb_terminal.portfolio.portfolio_optimization.riskfolio.RiskFunctions as rk
import openbb_terminal.portfolio.portfolio_optimization.riskfolio.ParamsEstimation as pe
import openbb_terminal.portfolio.portfolio_optimization.riskfolio.AuxFunctions as af
import openbb_terminal.portfolio.portfolio_optimization.riskfolio.OwaWeights as owa


class Portfolio(object):
    r"""
    Class that creates a portfolio object with all properties needed to
    calculate optimal portfolios.

    Parameters
    ----------
    returns : DataFrame, optional
        A dataframe that containts the returns of the assets.
        The default is None.
    sht : bool, optional
        Indicate if the portfolio consider short positions (negative weights).
        The default is False.
    uppersht : float, optional
        Indicate the maximum value of the sum of absolute values of short
        positions (negative weights). The default is 0.2.
    upperlng : float, optional
        Indicate the maximum value of the sum of long positions (positive
        weights). When sht=True, the difference between upperlng and uppersht
        must be equal to the budget (upperlng - uppersht = budget)
        The default is 1.
    budget : float, optional
        Indicate the maximum value of the sum of long positions (positive
        weights) and short positions (negative weights). The default is 1.
    nea : int, optional
        Indicate the minimum number of effective assets (NEA) used in
        portfolio. This value is the inverse of Herfindahl-Hirschman index of
        portfolio's weights. The default is None.
    card : int, optional
        Indicate the maximum number of assets used in portfolio. It requires
        a solver that supports Mixed Integer Programs (MIP), see `Solvers <https://www.cvxpy.org/tutorial/advanced/index.html#solve-method-options>`_ for more details.
        This constraint is based on :cite:`a-YUE2014949`. The default is None.
    factors : DataFrame, optional
        A dataframe that containts the returns of the factors.
        The default is None.
    B : DataFrame, optional
        A dataframe that containts the loadings matrix.
        The default is None.
    alpha : float, optional
        Significance level of CVaR, EVaR, CDaR, EDaR and Tail Gini of losses. The default is 0.05.
    a_sim : float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default is 100.
    beta : float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
        The default is None.
    b_sim : float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
        The default is None.
    kindbench : bool, optional
        True if the benchmark is a portfolio with detailed weights and False if
        the benchmark is an index. The default is True.
    allowTO : bool, optional
        Indicate if there is turnover constraints. The default is False.
    turnover : float, optional
        The maximum limit of turnover deviatons. The default is 0.05.
    allowTE : bool, optional
        Indicate if there is tracking error constraints.. The default is False.
    TE : float, optional
        The maximum limit of tracking error deviatons. The default is 0.05.
    benchindex : DataFrame, optional
        A dataframe that containts the returns of an index. If kindbench is
        False the tracking error constraints are calculated respect to this
        index. The default is None.
    benchweights : DataFrame, optional
        A dataframe that containts the weights of an index. The default is the
        equally weighted portfolio 1/N.
    ainequality : nd-array, optional
        The matrix :math:`A` of the linear constraint :math:`A \geq B`.
        The default is None.
    binequality : 1d-array, optional
        The matrix :math:`B` of the linear constraint :math:`A \geq B`.
        The default is None.
    lowerret : float, optional
        Constraint on min level of expected return. The default is None.
    upperdev : float, optional
        Constraint on max level of standard deviation. The default is None.
    uppermad : float, optional
        Constraint on max level of MAD. The default is None.
    uppergmd : float, optional
        Constraint on max level of GMD. The default is None.
    uppersdev : float, optional
        Constraint on max level of semi standard deviation. The default is None.
    upperflpm : float, optional
        Constraint on max level of first lower partial moment.
        The default is None.
    upperslpm : float, optional
        Constraint on max level of second lower partial moment.
        The default is None.
    upperCVaR : float, optional
        Constraint on max level of CVaR. The default is None.
    uppertg : float, optional
        Constraint on max level of Tail Gini. The default is None.
    upperEVaR : float, optional
        Constraint on max level of EVaR. The default is None.
    upperwr : float, optional
        Constraint on max level of worst realization. The default is None.
    upperrg : float, optional
        Constraint on max level of range. The default is None.
    uppercvrg : float, optional
        Constraint on max level of CVaR range. The default is None.
    uppertgrg : float, optional
        Constraint on max level of Tail Gini range. The default is None.
    uppermdd : float, optional
        Constraint on max level of maximum drawdown of uncompounded cumulative
        returns. The default is None.
    upperadd : float, optional
        Constraint on max level of average drawdown of uncompounded cumulative
        returns. The default is None.
    upperCDaR : float, optional
        Constraint on max level of conditional drawdown at risk (CDaR) of
        uncompounded cumulative returns. The default is None.
    upperEDaR : float, optional
        Constraint on max level of entropic drawdown at risk (EDaR) of
        uncompounded cumulative returns. The default is None.
    upperuci : float, optional
        Constraint on max level of ulcer index (UCI) of
        uncompounded cumulative returns. The default is None.
    """

    def __init__(
        self,
        returns=None,
        sht=False,
        uppersht=0.2,
        upperlng=1,
        budget=1,
        nea=None,
        card=None,
        factors=None,
        B=None,
        alpha=0.05,
        a_sim=100,
        beta=None,
        b_sim=None,
        kindbench=True,
        allowTO=False,
        turnover=0.05,
        allowTE=False,
        TE=0.05,
        benchindex=None,
        benchweights=None,
        ainequality=None,
        binequality=None,
        lowerret=None,
        upperdev=None,
        uppermad=None,
        uppersdev=None,
        upperflpm=None,
        upperslpm=None,
        upperCVaR=None,
        upperEVaR=None,
        upperwr=None,
        uppermdd=None,
        upperadd=None,
        upperCDaR=None,
        upperEDaR=None,
        upperuci=None,
        uppergmd=None,
        uppertg=None,
        upperrg=None,
        uppercvrg=None,
        uppertgrg=None,
    ):

        # Optimization Models Options

        self._returns = returns
        self.sht = sht
        self.uppersht = uppersht
        self.upperlng = upperlng
        self.budget = budget
        self.nea = nea
        self.card = card
        self._factors = factors
        self.alpha = alpha
        self.a_sim = a_sim
        self.beta = beta
        self.b_sim = b_sim
        self.kindbench = kindbench
        self.benchindex = benchindex
        self._benchweights = benchweights
        self._ainequality = ainequality
        self._binequality = binequality
        self.lowerret = lowerret
        self.upperdev = upperdev
        self.uppermad = uppermad
        self.uppersdev = uppersdev
        self.upperCVaR = upperCVaR
        self.upperEVaR = upperEVaR
        self.upperwr = upperwr
        self.uppermdd = uppermdd
        self.upperadd = upperadd
        self.upperCDaR = upperCDaR
        self.upperEDaR = upperEDaR
        self.upperflpm = upperflpm
        self.upperslpm = upperslpm
        self.upperuci = upperuci
        self.uppergmd = uppergmd
        self.uppertg = uppertg
        self.upperrg = upperrg
        self.uppercvrg = uppercvrg
        self.uppertgrg = uppertgrg

        self.allowTO = allowTO
        self.turnover = turnover
        self.allowTE = allowTE
        self.TE = TE

        # Inputs of Optimization Models

        self.mu = None
        self.cov = None
        self.mu_f = None
        self.cov_f = None
        self._B = None
        self.mu_fm = None
        self.cov_fm = None
        self.mu_bl = None
        self.cov_bl = None
        self.mu_bl_fm = None
        self.cov_bl_fm = None
        self.returns_fm = None
        self.nav_fm = None
        self.z_EVaR = None
        self.z_EDaR = None

        # Inputs of Worst Case Optimization Models

        self.cov_l = None
        self.cov_u = None
        self.cov_mu = None
        self.cov_sigma = None
        self.d_mu = None
        self.k_mu = None
        self.k_sigma = None

        # Optimal portfolios
        self.optimal = None
        self.rp_optimal = None
        self.wc_optimal = None
        self.limits = None
        self.frontier = None

        # Solver params

        self.solvers = ["ECOS", "SCS", "OSQP", "CVXOPT"]
        self.sol_params = {
            # 'ECOS': {"max_iters": 500, "abstol": 1e-8},
            # 'SCS': {"max_iters": 2500, "eps": 1e-5},
            # 'OSQP': {"max_iter": 10000, "eps_abs": 1e-8},
            # 'CVXOPT': {"max_iters": 500, "abstol": 1e-8},
        }

    @property
    def returns(self):
        if self._returns is not None and isinstance(self._returns, pd.DataFrame):
            return self._returns
        else:
            raise NameError("returns must be a DataFrame")

    @returns.setter
    def returns(self, value):
        if value is not None and isinstance(value, pd.DataFrame):
            self._returns = value
        else:
            raise NameError("returns must be a DataFrame")

    @property
    def nav(self):
        if self._returns is not None and isinstance(self._returns, pd.DataFrame):
            return self._returns.cumsum()

    @property
    def assetslist(self):
        if self._returns is not None and isinstance(self._returns, pd.DataFrame):
            return self._returns.columns.tolist()
        elif self._returns is None:
            return None

    @property
    def numassets(self):
        if self._returns is not None and isinstance(self._returns, pd.DataFrame):
            return self._returns.shape[1]

    @property
    def factors(self):
        return self._factors

    @factors.setter
    def factors(self, value):
        a = value
        if a is not None and isinstance(a, pd.DataFrame):
            if self.returns.index.equals(a.index):
                self._factors = a
        else:
            raise NameError("factors must be a DataFrame")

    @property
    def factorslist(self):
        if self._factors is not None and isinstance(self._factors, pd.DataFrame):
            return self._factors.columns.tolist()
        elif self._factors is None:
            return None

    @property
    def B(self):
        return self._B

    @B.setter
    def B(self, value):
        a = value
        if a is not None and isinstance(a, pd.DataFrame):
            self._B = a
        else:
            raise NameError("loadings matrix must be a DataFrame")

    @property
    def benchweights(self):
        n = self.numassets
        if self._benchweights is not None:
            if self._benchweights.shape[0] == n and self._benchweights.shape[1] == 1:
                a = self._benchweights
            else:
                raise NameError("Weights must have a size of shape (n_assets,1)")
        else:
            a = np.array(np.ones((n, 1)) / n)
        return a

    @benchweights.setter
    def benchweights(self, value):
        a = value
        n = self.numassets
        if a is not None:
            if a.shape[0] == n and a.shape[1] == 1:
                a = a
            else:
                raise NameError("Weights must have a size of shape (n_assets,1)")
        else:
            a = np.array(np.ones((n, 1)) / n)
        self._benchweights = a

    @property
    def ainequality(self):
        a = self._ainequality
        if a is not None:
            if a.shape[1] == self.numassets:
                a = a
            else:
                raise NameError(
                    "The array ainequality must have the same number of columns that assets' number"
                )
        return a

    @ainequality.setter
    def ainequality(self, value):
        a = value
        if a is not None:
            if a.shape[1] == self.numassets:
                a = a
            else:
                raise NameError(
                    "The matrix ainequality must have the same number of columns that assets' number"
                )
        self._ainequality = a

    @property
    def binequality(self):
        a = self._binequality
        if a is not None:
            if a.shape[1] == 1:
                a = a
            else:
                raise NameError("The matrix binequality must have one column")
        return a

    @binequality.setter
    def binequality(self, value):
        a = value
        if a is not None:
            if a.shape[1] == 1:
                a = a
            else:
                raise NameError("The matrix binequality must have one column")
        self._binequality = a

    def assets_stats(self, method_mu="hist", method_cov="hist", d=0.94, **kwargs):
        r"""
        Calculate the inputs that will be used by the optimization method when
        we select the input model='Classic'.

        Parameters
        ----------
        method_mu : str, optional
            The method used to estimate the expected returns.
            The default value is 'hist'. Posible values are:

            - 'hist': use historical estimates.
            - 'ewma1'': use ewma with adjust=True, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.
            - 'ewma2': use ewma with adjust=False, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.

        method_cov : str, optional
            The method used to estimate the covariance matrix:
            The default is 'hist'. Posible values are:

            - 'hist': use historical estimates.
            - 'ewma1'': use ewma with adjust=True, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.
            - 'ewma2': use ewma with adjust=False, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.
            - 'ledoit': use the Ledoit and Wolf Shrinkage method.
            - 'oas': use the Oracle Approximation Shrinkage method.
            - 'shrunk': use the basic Shrunk Covariance method.
            - 'gl': use the basic Graphical Lasso Covariance method.
            - 'jlogo': use the j-LoGo Covariance method. For more information see: :cite:`a-jLogo`.
            - 'fixed': denoise using fixed method. For more information see chapter 2 of :cite:`a-MLforAM`.
            - 'spectral': denoise using spectral method. For more information see chapter 2 of :cite:`a-MLforAM`.
            - 'shrink': denoise using shrink method. For more information see chapter 2 of :cite:`a-MLforAM`.

        **kwargs : dict
            All aditional parameters of mean_vector and covar_matrix functions.

        See Also
        --------
        riskfolio.ParamsEstimation.mean_vector
        riskfolio.ParamsEstimation.covar_matrix

        """

        self.mu = pe.mean_vector(self.returns, method=method_mu, d=d)
        self.cov = pe.covar_matrix(self.returns, method=method_cov, **kwargs)
        value = af.is_pos_def(self.cov, threshold=1e-8)
        if value == False:
            try:
                self.cov = af.cov_fix(self.cov, method="clipped", threshold=1e-5)
                value = af.is_pos_def(self.cov, threshold=1e-8)
                if value == False:
                    print("You must convert self.cov to a positive definite matrix")
            except:
                print("You must convert self.cov to a positive definite matrix")

    def blacklitterman_stats(
        self,
        P,
        Q,
        rf=0,
        w=None,
        delta=None,
        eq=True,
        method_mu="hist",
        method_cov="hist",
        **kwargs,
    ):
        r"""
        Calculate the inputs that will be used by the optimization method when
        we select the input model='BL'.

        Parameters
        ----------
        P : DataFrame of shape (n_views, n_assets)
            Analyst's views matrix, can be relative or absolute.
        Q: DataFrame of shape (n_views, 1)
            Expected returns of analyst's views.
        delta: float
            Risk aversion factor. The default value is 1.
        rf: scalar, optional
            Risk free rate. The default is 0.
        w : DataFrame of shape (n_assets, 1)
            Weights matrix, where n_assets is the number of assets.
            The default is None.
        eq: bool, optional
            Indicates if use equilibrum or historical excess returns.
            The default is True.
        method_mu : str, optional
            The method used to estimate the expected returns.
            The default value is 'hist'. Posible values are:

            - 'hist': use historical estimates.
            - 'ewma1'': use ewma with adjust=True, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.
            - 'ewma2': use ewma with adjust=False, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.

        method_cov : str, optional
            The method used to estimate the covariance matrix:
            The default is 'hist'. Posible values are:

            - 'hist': use historical estimates.
            - 'ewma1'': use ewma with adjust=True, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.
            - 'ewma2': use ewma with adjust=False, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.
            - 'ledoit': use the Ledoit and Wolf Shrinkage method.
            - 'oas': use the Oracle Approximation Shrinkage method.
            - 'shrunk': use the basic Shrunk Covariance method.
            - 'gl': use the basic Graphical Lasso Covariance method.
            - 'jlogo': use the j-LoGo Covariance method. For more information see: :cite:`a-jLogo`.
            - 'fixed': denoise using fixed method. For more information see chapter 2 of :cite:`a-MLforAM`.
            - 'spectral': denoise using spectral method. For more information see chapter 2 of :cite:`a-MLforAM`.
            - 'shrink': denoise using shrink method. For more information see chapter 2 of :cite:`a-MLforAM`.

        **kwargs : dict
            Other variables related to the covariance estimation.

        See Also
        --------
        riskfolio.ParamsEstimation.black_litterman

        """
        X = self.returns
        if w is None:
            w = np.array(self.benchweights, ndmin=2)

        if delta is None:
            a = np.array(self.mu, ndmin=2) @ np.array(w, ndmin=2)
            delta = (a - rf) / (
                np.array(w, ndmin=2).T
                @ np.array(self.cov, ndmin=2)
                @ np.array(w, ndmin=2)
            )
            delta = delta.item()

        mu, cov, w = pe.black_litterman(
            X=X,
            w=w,
            P=P,
            Q=Q,
            delta=delta,
            rf=rf,
            eq=eq,
            method_mu=method_mu,
            method_cov=method_cov,
            **kwargs,
        )
        self.mu_bl = mu
        self.cov_bl = cov

        value = af.is_pos_def(self.cov_bl, threshold=1e-8)
        if value == False:
            try:
                self.cov_bl = af.cov_fix(self.cov_bl, method="clipped", threshold=1e-5)
                value = af.is_pos_def(self.cov_bl, threshold=1e-8)
                if value == False:
                    print("You must convert self.cov_bl to a positive definite matrix")
            except:
                print("You must convert self.cov_bl to a positive definite matrix")

    def factors_stats(
        self,
        method_mu="hist",
        method_cov="hist",
        d=0.94,
        B=None,
        dict_cov={},
        dict_risk={},
    ):
        r"""
        Calculate the inputs that will be used by the optimization method when
        we select the input model='FM'.

        Parameters
        ----------
        method_mu : str, optional
            The method used to estimate the expected returns.
            The default value is 'hist'. Posible values are:

            - 'hist': use historical estimates.
            - 'ewma1'': use ewma with adjust=True, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.
            - 'ewma2': use ewma with adjust=False, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.

        method_cov : str, optional
            The method used to estimate the covariance matrix:
            The default is 'hist'. Posible values are:

            - 'hist': use historical estimates.
            - 'ewma1'': use ewma with adjust=True, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.
            - 'ewma2': use ewma with adjust=False, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.
            - 'ledoit': use the Ledoit and Wolf Shrinkage method.
            - 'oas': use the Oracle Approximation Shrinkage method.
            - 'shrunk': use the basic Shrunk Covariance method.
            - 'gl': use the basic Graphical Lasso Covariance method.
            - 'jlogo': use the j-LoGo Covariance method. For more information see: :cite:`a-jLogo`.
            - 'fixed': denoise using fixed method. For more information see chapter 2 of :cite:`a-MLforAM`.
            - 'spectral': denoise using spectral method. For more information see chapter 2 of :cite:`a-MLforAM`.
            - 'shrink': denoise using shrink method. For more information see chapter 2 of :cite:`a-MLforAM`.

        dict_cov : dict
            Other variables related to the covariance estimation.
        dict_risk : dict
            Other variables related of risk_factors function.

        See Also
        --------
        riskfolio.ParamsEstimation.forward_regression
        riskfolio.ParamsEstimation.backward_regression
        riskfolio.ParamsEstimation.loadings_matrix
        riskfolio.ParamsEstimation.risk_factors

        """
        X = self.factors
        Y = self.returns

        mu_f = pe.mean_vector(self.returns, method=method_mu, d=d)
        cov_f = pe.covar_matrix(self.returns, method=method_cov, d=d, **dict_cov)

        self.mu_f = mu_f
        self.cov_f = cov_f

        value = af.is_pos_def(self.cov_f, threshold=1e-8)
        if value == False:
            try:
                self.cov = af.cov_fix(self.cov, method="clipped", threshold=1e-5)
                value = af.is_pos_def(self.cov, threshold=1e-8)
                if value == False:
                    print("You must convert self.cov to a positive definite matrix")
            except:
                print("You must convert self.cov to a positive definite matrix")

        mu, cov, returns, nav = pe.risk_factors(
            X, Y, B=B, method_mu=method_mu, method_cov=method_cov, **dict_risk
        )

        self.mu_fm = mu
        self.cov_fm = cov
        self.returns_fm = returns
        self.nav_fm = nav

        value = af.is_pos_def(self.cov_fm, threshold=1e-8)
        if value == False:
            try:
                self.cov_fm = af.cov_fix(self.cov_fm, method="clipped", threshold=1e-5)
                value = af.is_pos_def(self.cov_fm, threshold=1e-8)
                if value == False:
                    print("You must convert self.cov_fm to a positive definite matrix")
            except:
                print("You must convert self.cov_fm to a positive definite matrix")

    def blfactors_stats(
        self,
        flavor="BLB",
        B=None,
        P=None,
        Q=None,
        P_f=None,
        Q_f=None,
        rf=0,
        w=None,
        delta=None,
        eq=True,
        const=False,
        diag=False,
        method_mu="hist",
        method_cov="hist",
        kwargs_1=None,
        kwargs_2=None,
    ):
        r"""
        Calculate the inputs that will be used by the optimization method when
        we select the input model='BL'.

        Parameters
        ----------
        flavor : str
            Model used, can be 'BLB' for Black Litterman Bayesian or 'ABL' for
            Augmented Black Litterman. The default value is 'BLB'.
        B : DataFrame of shape (n_assets, n_features)
            Loadings matrix. The default value is None.
        P : DataFrame of shape (n_views, n_assets)
            Analyst's views matrix, can be relative or absolute.
        Q: DataFrame of shape (n_views, 1)
            Expected returns of analyst's views.
        P_f : DataFrame of shape (n_views, n_assets)
            Analyst's factors views matrix, can be relative or absolute.
        Q_f: DataFrame of shape (n_views, 1)
            Expected returns of analyst's factors views.
        delta: float
            Risk aversion factor. The default value is 1.
        rf: scalar, optional
            Risk free rate. The default is 0.
        w : DataFrame of shape (n_assets, 1)
            Weights matrix, where n_assets is the number of assets.
            The default is None.
        eq: bool, optional
            Indicates if use equilibrum or historical excess returns.
            The default is True.
        const : bool, optional
            Indicate if the loadings matrix has a constant.
            The default is False.
        diag : bool, optional
            Indicate if we use the diagonal matrix to calculate covariance matrix
            of factor model, only useful when we work with a factor model based on
            a regresion model (only equity portfolio).
            The default is False.
        method_mu : str, optional
            The method used to estimate the expected returns.
            The default value is 'hist'. Posible values are:

            - 'hist': use historical estimates.
            - 'ewma1'': use ewma with adjust=True, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.
            - 'ewma2': use ewma with adjust=False, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.

        method_cov : str, optional
            The method used to estimate the covariance matrix:
            The default is 'hist'. Posible values are:

            - 'hist': use historical estimates.
            - 'ewma1'': use ewma with adjust=True, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.
            - 'ewma2': use ewma with adjust=False, see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/computation.html#exponentially-weighted-windows>`_ for more details.
            - 'ledoit': use the Ledoit and Wolf Shrinkage method.
            - 'oas': use the Oracle Approximation Shrinkage method.
            - 'shrunk': use the basic Shrunk Covariance method.
            - 'gl': use the basic Graphical Lasso Covariance method.
            - 'jlogo': use the j-LoGo Covariance method. For more information see: :cite:`a-jLogo`.
            - 'fixed': denoise using fixed method. For more information see chapter 2 of :cite:`a-MLforAM`.
            - 'spectral': denoise using spectral method. For more information see chapter 2 of :cite:`a-MLforAM`.
            - 'shrink': denoise using shrink method. For more information see chapter 2 of :cite:`a-MLforAM`.

        kwargs_1 : dict
            Other variables related to the loadings matrix estimation.
        kwargs_2 : dict
            Other variables related to the factors Black Litterman model selected.

        See Also
        --------
        riskfolio.ParamsEstimation.augmented_black_litterman
        riskfolio.ParamsEstimation.black_litterman_bayesian

        """
        X = self.returns
        F = self.factors

        if w is None:
            w = np.array(self.benchweights, ndmin=2)

        if delta is None:
            a = np.array(self.mu, ndmin=2) @ np.array(w, ndmin=2)
            delta = (a - rf) / (
                np.array(w, ndmin=2).T
                @ np.array(self.cov, ndmin=2)
                @ np.array(w, ndmin=2)
            )
            delta = delta.item()

        if B is None:
            if self.B is None:
                self.B = pe.loadings_matrix(X=F, Y=X, **kwargs_1)
                const = True
            elif self.B is not None:
                pass
        elif B is not None:
            self.B = B

        if flavor == "BLB":
            if isinstance(kwargs_1, dict):
                mu, cov, w = pe.black_litterman_bayesian(
                    X=X,
                    F=F,
                    B=self.B,
                    P_f=P_f,
                    Q_f=Q_f,
                    delta=delta,
                    rf=rf,
                    eq=eq,
                    const=const,
                    diag=diag,
                    method_mu=method_mu,
                    method_cov=method_cov,
                    **kwargs_2,
                )
            else:
                mu, cov, w = pe.black_litterman_bayesian(
                    X=X,
                    F=F,
                    B=self.B,
                    P_f=P_f,
                    Q_f=Q_f,
                    delta=delta,
                    rf=rf,
                    eq=eq,
                    const=const,
                    diag=diag,
                    method_mu=method_mu,
                    method_cov=method_cov,
                )

        elif flavor == "ABL":
            if isinstance(kwargs_1, dict):
                mu, cov, w = pe.augmented_black_litterman(
                    X=X,
                    w=w,
                    F=F,
                    B=self.B,
                    P=P,
                    Q=Q,
                    P_f=P_f,
                    Q_f=Q_f,
                    delta=delta,
                    rf=rf,
                    eq=eq,
                    const=const,
                    method_mu=method_mu,
                    method_cov=method_cov,
                    **kwargs_2,
                )
            else:
                mu, cov, w = pe.augmented_black_litterman(
                    X=X,
                    w=w,
                    F=F,
                    B=self.B,
                    P=P,
                    Q=Q,
                    P_f=P_f,
                    Q_f=Q_f,
                    delta=delta,
                    rf=rf,
                    eq=eq,
                    const=const,
                    method_mu=method_mu,
                    method_cov=method_cov,
                )

        self.mu_bl_fm = mu
        self.cov_bl_fm = cov

        value = af.is_pos_def(self.cov_bl_fm, threshold=1e-8)
        if value == False:
            try:
                self.cov_bl_fm = af.cov_fix(
                    self.cov_bl_fm, method="clipped", threshold=1e-5
                )
                value = af.is_pos_def(self.cov_bl_fm, threshold=1e-8)
                if value == False:
                    print(
                        "You must convert self.cov_bl_fm to a positive definite matrix"
                    )
            except:
                print("You must convert self.cov_bl_fm to a positive definite matrix")

    def wc_stats(
        self,
        box="s",
        ellip="s",
        q=0.05,
        n_sim=3000,
        window=3,
        dmu=0.1,
        dcov=0.1,
        seed=0,
    ):
        r"""
        Calculate the inputs that will be used by the wc_optimization method.

        Parameters
        ----------
        box : string
            The method used to estimate the box uncertainty sets. The default is 's'. Posible values are:

            - 's': stationary bootstrapping method.
            - 'c': circular bootstrapping method.
            - 'm': moving bootstrapping method.
            - 'n': assuming normal returns to calculate confidence levels.
            - 'd': delta method, this method increase and decrease by a percentage.

        ellip : string
            The method used to estimate the elliptical uncertainty sets. The default is 's'. Posible values are:

            - 's': stationary bootstrapping method.
            - 'c': circular bootstrapping method.
            - 'm': moving bootstrapping method.
            - 'n': assuming normal returns to calculate confidence levels.

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
        dmu : scalar
            Percentage used by delta method to increase and decrease the mean vector in box constraints.
            The default is 0.1.
        dcov : scalar
            Percentage used by delta method to increase and decrease the covariance matrix in box constraints.
            The default is 0.1.

        See Also
        --------
        riskfolio.ParamsEstimation.bootstrapping

        """

        if box not in list("scmdn"):
            raise ValueError("box only can be 's', 'c', 'm', 'd' or 'n'")
        if ellip not in list("scmn"):
            raise ValueError("box only can be 's', 'c', 'm' or 'n'")

        X = self.returns
        cols = X.columns.tolist()
        cols_2 = [i + "-" + j for i in cols for j in cols]
        (n, m) = X.shape
        mu = X.mean().to_frame().T
        cov = X.cov()

        if box == "s":
            mu_l, mu_u, cov_l, cov_u, _, _ = pe.bootstrapping(
                X, kind="stationary", q=q, n_sim=n_sim, window=window, seed=seed
            )
            d_mu = (mu_u - mu_l) / 2
        elif box == "c":
            mu_l, mu_u, cov_l, cov_u, _, _ = pe.bootstrapping(
                X, kind="circular", q=q, n_sim=n_sim, window=window, seed=seed
            )
            d_mu = (mu_u - mu_l) / 2
        elif box == "m":
            mu_l, mu_u, cov_l, cov_u, _, _ = pe.bootstrapping(
                X, kind="moving", q=q, n_sim=n_sim, window=window, seed=seed
            )
            d_mu = (mu_u - mu_l) / 2
        elif box == "n":
            # Defining confidence level of mean vector assuming normal returns
            mu_u = mu + st.norm.ppf(1 - q / 2) * np.diag(cov) / n**2
            mu_l = mu - st.norm.ppf(1 - q / 2) * np.diag(cov) / n**2
            d_mu = (mu_u - mu_l) / 2
            d_mu = pd.DataFrame(d_mu, index=[0], columns=cols)

            # Defining confidence level of covariance matrix assuming normal returns
            rs = np.random.RandomState(seed=seed)
            A = st.wishart.rvs(n, cov / n, size=10000, random_state=rs)
            cov_l = np.percentile(A, q=q, axis=0)
            cov_u = np.percentile(A, q=1 - q / 2, axis=0)

            cov_l = pd.DataFrame(cov_l, index=cols, columns=cols)
            cov_u = pd.DataFrame(cov_u, index=cols, columns=cols)

            if af.is_pos_def(cov_l) == False:
                cov_l = af.cov_fix(cov_l, method="clipped", threshold=1e-3)

            if af.is_pos_def(cov_u) == False:
                cov_u = af.cov_fix(cov_u, method="clipped", threshold=1e-3)

        elif box == "d":
            d_mu = dmu * np.abs(mu)
            cov_l = cov - dcov * np.abs(cov)
            cov_u = cov + dcov * np.abs(cov)
            d_mu = pd.DataFrame(d_mu, index=[0], columns=cols)
            cov_l = pd.DataFrame(cov_l, index=cols, columns=cols)
            cov_u = pd.DataFrame(cov_u, index=cols, columns=cols)

        if ellip == "s":
            _, _, _, _, cov_mu, cov_sigma = pe.bootstrapping(
                X, kind="stationary", q=q, n_sim=n_sim, window=window, seed=seed
            )
        elif ellip == "c":
            _, _, _, _, cov_mu, cov_sigma = pe.bootstrapping(
                X, kind="circular", q=q, n_sim=n_sim, window=window, seed=seed
            )
        elif ellip == "m":
            _, _, _, _, cov_mu, cov_sigma = pe.bootstrapping(
                X, kind="moving", q=q, n_sim=n_sim, window=window, seed=seed
            )
        elif ellip == "n":
            # Covariance of mean returns
            cov_mu = cov / n
            cov_mu = np.diag(np.diag(cov_mu))
            cov_mu = pd.DataFrame(cov_mu, index=cols, columns=cols)
            # Covariance of covariance matrix
            K = af.commutation_matrix(cov)
            I = np.identity(m * m)
            cov_sigma = n * (I + K) @ np.kron(cov_mu, cov_mu)
            cov_sigma = np.diag(np.diag(cov_sigma))
            cov_sigma = pd.DataFrame(cov_sigma, index=cols_2, columns=cols_2)

        k_mu = st.chi2.ppf(1 - q, df=m) ** 0.5
        k_sigma = st.chi2.ppf(1 - q, df=m * m) ** 0.5

        self.cov_l = cov_l
        self.cov_u = cov_u
        self.cov_mu = cov_mu
        self.cov_sigma = cov_sigma
        self.d_mu = d_mu
        self.k_mu = k_mu
        self.k_sigma = k_sigma

    def optimization(
        self, model="Classic", rm="MV", obj="Sharpe", kelly=False, rf=0, l=2, hist=True
    ):
        r"""
        This method that calculates the optimal portfolio according to the
        optimization model selected by the user. The general problem that
        solves is:
        
        .. math::
            \begin{align}
            &\underset{w}{\text{optimize}} & & F(w)\\
            &\text{s. t.} & & Aw \geq B\\
            & & & \phi_{i}(w) \leq c_{i}\\
            \end{align}
        
        Where:
            
        :math:`F(w)` is the objective function.
    
        :math:`Aw \geq B` is a set of linear constraints.
    
        :math:`\phi_{i}(w) \leq c_{i}` are constraints on maximum values of
        several risk measures.
        
        Parameters
        ----------
        model : str can be {'Classic', 'BL', 'FM' or 'BLFM'}
            The model used for optimize the portfolio.
            The default is 'Classic'. Posible values are:

            - 'Classic': use estimates of expected return vector and covariance matrix that depends on historical data.
            - 'BL': use estimates of expected return vector and covariance matrix based on the Black Litterman model.
            - 'FM': use estimates of expected return vector and covariance matrix based on a Risk Factor model specified by the user.
            - 'BLFM': use estimates of expected return vector and covariance matrix based on Black Litterman applied to a Risk Factor model specified by the user.
            
        rm : str, optional
            The risk measure used to optimze the portfolio.
            The default is 'MV'. Posible values are:
            
            - 'MV': Standard Deviation.
            - 'MAD': Mean Absolute Deviation.
            - 'GMD': Gini Mean Difference.
            - 'MSV': Semi Standard Deviation.
            - 'FLPM': First Lower Partial Moment (Omega Ratio).
            - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
            - 'CVaR': Conditional Value at Risk.
            - 'TG': Tail Gini.
            - 'EVaR': Entropic Value at Risk.
            - 'WR': Worst Realization (Minimax).
            - 'RG': Range of returns.
            - 'CVRG': CVaR range of returns.
            - 'TGRG': Tail Gini range of returns.
            - 'MDD': Maximum Drawdown of uncompounded cumulative returns (Calmar Ratio).
            - 'ADD': Average Drawdown of uncompounded cumulative returns.
            - 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
            - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
            - 'UCI': Ulcer Index of uncompounded cumulative returns.
            
        obj : str can be {'MinRisk', 'Utility', 'Sharpe' or 'MaxRet'}.
            Objective function of the optimization model.
            The default is 'Sharpe'. Posible values are:

            - 'MinRisk': Minimize the selected risk measure.
            - 'Utility': Maximize the Utility function :math:`\mu w - l \phi_{i}(w)`.
            - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
            - 'MaxRet': Maximize the expected return of the portfolio.
                
        kelly : str, optional
            Method used to calculate mean return. Posible values are False for
            arithmetic mean return, "approx" for approximate mean logarithmic 
            return using first and second moment and "exact" for mean logarithmic
            return. The default is False.
        rf : float, optional
            Risk free rate, must be in the same period of assets returns.
            The default is 0.
        l : scalar, optional
            Risk aversion factor of the 'Utility' objective function.
            The default is 2.
        hist : bool, optional
            Indicate what kind of returns are used to calculate risk measures
            that depends on scenarios (All except 'MV' risk measure).
            If model = 'BL', True means historical covariance and returns and
            False Black Litterman covariance and historical returns.
            If model = 'FM', True means historical covariance and returns and
            False Risk Factor model for covariance and returns.
            If model = 'BL_FM', True means historical covariance and returns,
            False Black Litteram with Risk Factor model for covariance and
            Risk Factor model for returns, and '2' Risk Factor model for
            covariance and returns. The default is True.

        Returns
        -------
        w : DataFrame
            The weights of optimal portfolio.

        """

        # General model Variables

        mu = None
        sigma = None
        returns = None
        if model == "Classic":
            mu = np.array(self.mu, ndmin=2)
            sigma = np.array(self.cov, ndmin=2)
            returns = np.array(self.returns, ndmin=2)
            nav = np.array(self.nav, ndmin=2)
        elif model == "FM":
            mu = np.array(self.mu_fm, ndmin=2)
            if hist == False:
                sigma = np.array(self.cov_fm, ndmin=2)
                returns = np.array(self.returns_fm, ndmin=2)
                nav = np.array(self.nav_fm, ndmin=2)
            elif hist == True:
                sigma = np.array(self.cov, ndmin=2)
                returns = np.array(self.returns, ndmin=2)
                nav = np.array(self.nav, ndmin=2)
        elif model == "BL":
            mu = np.array(self.mu_bl, ndmin=2)
            if hist == False:
                sigma = np.array(self.cov_bl, ndmin=2)
            elif hist == True:
                sigma = np.array(self.cov, ndmin=2)
            returns = np.array(self.returns, ndmin=2)
            nav = np.array(self.nav, ndmin=2)
        elif model == "BL_FM":
            mu = np.array(self.mu_bl_fm, ndmin=2)
            if hist == False:
                sigma = np.array(self.cov_bl_fm, ndmin=2)
                returns = np.array(self.returns_fm, ndmin=2)
                nav = np.array(self.nav_fm, ndmin=2)
            elif hist == True:
                sigma = np.array(self.cov, ndmin=2)
                returns = np.array(self.returns, ndmin=2)
                nav = np.array(self.nav, ndmin=2)
            elif hist == 2:
                sigma = np.array(self.cov_fm, ndmin=2)
                returns = np.array(self.returns_fm, ndmin=2)
                nav = np.array(self.nav_fm, ndmin=2)

        # General Model Variables

        returns = np.array(returns, ndmin=2)
        w = cv.Variable((mu.shape[1], 1))
        k = cv.Variable((1, 1))
        rf0 = rf
        n = returns.shape[0]
        gr = cv.Variable((n, 1))

        # MV Model Variables

        g = cv.Variable(nonneg=True)
        G = sqrtm(sigma)
        risk1 = g**2
        devconstraints = [cv.SOC(g, G.T @ w)]

        # Return Variables

        if model == "Classic":
            if kelly == "exact":
                if obj == "Sharpe":
                    ret = 1 / n * cv.sum(gr) - rf0 * k
                else:
                    ret = 1 / n * cv.sum(cv.log(1 + returns @ w))
            elif kelly == "approx":
                if obj == "Sharpe":
                    ret = mu @ w - 0.5 * cv.quad_over_lin(g, k)
                else:
                    ret = mu @ w - 0.5 * g**2
            elif kelly == False:
                ret = mu @ w
        else:
            ret = mu @ w

        # MAD Model Variables

        madmodel = False
        Y = cv.Variable((returns.shape[0], 1))
        u = np.ones((returns.shape[0], 1)) * mu
        a = returns - u
        risk2 = cv.sum(Y) / n
        # madconstraints=[a @ w >= -Y, a @ w <= Y, Y >= 0]
        madconstraints = [a @ w >= -Y, Y >= 0]

        # Semi Variance Model Variables

        risk3 = cv.norm(Y, "fro") / cv.sqrt(n - 1)

        # CVaR Model Variables

        VaR = cv.Variable((1, 1))
        alpha = self.alpha
        X = returns @ w
        Z = cv.Variable((returns.shape[0], 1))
        risk4 = VaR + 1 / (alpha * n) * cv.sum(Z)
        cvarconstraints = [Z >= 0, Z >= -X - VaR]

        # Worst Realization (Minimax) Model Variables

        M = cv.Variable((1, 1))
        risk5 = M
        wrconstraints = [-X <= M]

        # Lower Partial Moment Variables

        lpmmodel = False
        lpm = cv.Variable((returns.shape[0], 1))
        lpmconstraints = [lpm >= 0]

        if obj == "Sharpe":
            lpmconstraints += [lpm >= rf0 * k - X]
        else:
            lpmconstraints += [lpm >= rf0 - X]

        # First Lower Partial Moment (Omega) Model Variables

        risk6 = cv.sum(lpm) / n

        # Second Lower Partial Moment (Sortino) Model Variables

        risk7 = cv.norm(lpm, "fro") / cv.sqrt(n - 1)

        # Drawdown Model Variables

        drawdown = False
        if obj == "Sharpe":
            X1 = k + nav @ w
        else:
            X1 = 1 + nav @ w

        U = cv.Variable((nav.shape[0] + 1, 1))
        ddconstraints = [U[1:] * 1000 >= X1 * 1000, U[1:] * 1000 >= U[:-1] * 1000]

        if obj == "Sharpe":
            ddconstraints += [U[1:] * 1000 >= k * 1000, U[0] * 1000 == k * 1000]
        else:
            ddconstraints += [U[1:] * 1000 >= 1 * 1000, U[0] * 1000 == 1 * 1000]

        # Maximum Drawdown Model Variables

        MDD = cv.Variable((1, 1))
        risk8 = MDD
        mddconstraints = [MDD >= U[1:] - X1]

        # Average Drawdown Model Variables

        risk9 = 1 / n * cv.sum(U[1:] - X1)

        # Conditional Drawdown Model Variables

        CDaR = cv.Variable((1, 1))
        Zd = cv.Variable((nav.shape[0], 1))
        risk10 = CDaR + 1 / (alpha * n) * cv.sum(Zd)
        cdarconstraints = [
            Zd * 1000 >= U[1:] * 1000 - X1 * 1000 - CDaR * 1000,
            Zd * 1000 >= 0,
        ]

        # Ulcer Index Model Variables

        risk11 = cv.norm(U[1:] * 1000 - X1 * 1000, "fro") / np.sqrt(n)

        # Entropic Value at Risk Model Variables

        t1 = cv.Variable((1, 1))
        s1 = cv.Variable((1, 1), nonneg=True)
        ui = cv.Variable((n, 1))
        risk12 = t1 + s1 * np.log(1 / (alpha * n))

        if obj == "Sharpe":
            evarconstraints = [cv.sum(ui) * 1000 <= s1 * 1000]
            evarconstraints += [
                cv.constraints.ExpCone(
                    -X * 1000 - t1 * 1000, np.ones((n, 1)) @ s1 * 1000, ui * 1000
                )
            ]
        else:
            evarconstraints = [cv.sum(ui) <= s1]
            evarconstraints += [
                cv.constraints.ExpCone(-X - t1, np.ones((n, 1)) @ s1, ui)
            ]

        # Entropic Drawdown at Risk Model Variables

        t2 = cv.Variable((1, 1))
        s2 = cv.Variable((1, 1), nonneg=True)
        uj = cv.Variable((n, 1))
        risk13 = t2 + s2 * np.log(1 / (alpha * n))

        if obj == "Sharpe":
            edarconstraints = [cv.sum(uj) * 1000 <= s2 * 1000]
            edarconstraints += [
                cv.constraints.ExpCone(
                    U[1:] * 1000 - X1 * 1000 - t2 * 1000,
                    np.ones((n, 1)) @ s2 * 1000,
                    uj * 1000,
                )
            ]
        else:
            edarconstraints = [cv.sum(uj) <= s2]
            edarconstraints += [
                cv.constraints.ExpCone(U[1:] - X1 - t2, np.ones((n, 1)) @ s2, uj)
            ]

        # Gini Mean Difference Model Variables

        owamodel = False
        a1 = cv.Variable((n, 1))
        b1 = cv.Variable((n, 1))
        y = cv.Variable((n, 1))
        risk14 = cv.sum(a1 + b1)

        owaconstraints = [returns @ w == y]
        gmd_w = owa.owa_gmd(n) / 2
        onesvec = np.ones((n, 1))
        gmdconstraints = [y @ gmd_w.T <= onesvec @ a1.T + b1 @ onesvec.T]

        # Tail Gini Model Variables

        a2 = cv.Variable((n, 1))
        b2 = cv.Variable((n, 1))
        risk15 = cv.sum(a2 + b2)
        a_sim = self.a_sim

        tg_w = owa.owa_tg(n, alpha=alpha)
        tgconstraints = [y @ tg_w.T <= onesvec @ a2.T + b2 @ onesvec.T]

        # Range Model Variables

        a3 = cv.Variable((n, 1))
        b3 = cv.Variable((n, 1))
        risk16 = cv.sum(a3 + b3)

        rg_w = owa.owa_rg(n)
        rgconstraints = [y @ rg_w.T <= onesvec @ a3.T + b3 @ onesvec.T]

        # CVaR Range Model Variables

        a4 = cv.Variable((n, 1))
        b4 = cv.Variable((n, 1))
        risk17 = cv.sum(a4 + b4)

        if self.beta is None:
            beta = alpha
        else:
            beta = self.beta

        cvrg_w = owa.owa_cvrg(n, alpha=alpha, beta=beta)
        cvrgconstraints = [y @ cvrg_w.T <= onesvec @ a4.T + b4 @ onesvec.T]

        # Tail Gini Range Model Variables

        a5 = cv.Variable((n, 1))
        b5 = cv.Variable((n, 1))
        risk18 = cv.sum(a5 + b5)

        if self.b_sim is None:
            b_sim = a_sim
        else:
            b_sim = self.b_sim

        tgrg_w = owa.owa_tgrg(n, alpha=alpha, a_sim=a_sim, beta=beta, b_sim=b_sim)
        tgrgconstraints = [y @ tgrg_w.T <= onesvec @ a5.T + b5 @ onesvec.T]

        # Cardinal Boolean Variables

        if self.card is not None:
            if obj == "Sharpe":
                e = cv.Variable((mu.shape[1], 1), boolean=True)
                e1 = cv.Variable((mu.shape[1], 1))
            else:
                e = cv.Variable((mu.shape[1], 1), boolean=True)

        # Problem Weight Constraints

        if obj == "Sharpe":
            constraints = [cv.sum(w) == self.budget * k, k * 1000 >= 0]
            if self.sht == False:
                constraints += [w <= self.upperlng * k, w * 1000 >= 0]
                if self.card is not None:
                    constraints += [
                        cv.sum(e) <= self.card,
                        e1 <= k,
                        e1 >= 0,
                        e1 <= 100000 * e,
                        e1 >= k - 100000 * (1 - e),
                        w <= self.upperlng * e1,
                    ]
            elif self.sht == True:
                constraints += [
                    cv.sum(cv.pos(w)) * 1000 <= self.upperlng * k * 1000,
                    cv.sum(cv.neg(w)) * 1000 <= self.uppersht * k * 1000,
                ]
                if self.card is not None:
                    constraints += [
                        cv.sum(e) <= self.card,
                        e1 <= k,
                        e1 >= 0,
                        e1 <= 100000 * e,
                        e1 >= k - 100000 * (1 - e),
                        w >= -self.uppersht * e1,
                        w <= self.upperlng * e1,
                    ]

        else:
            constraints = [cv.sum(w) == self.budget]
            if self.sht == False:
                constraints += [w <= self.upperlng, w * 1000 >= 0]
                if self.card is not None:
                    constraints += [
                        cv.sum(e) <= self.card,
                        w <= self.upperlng * e,
                    ]

            elif self.sht == True:
                constraints += [
                    cv.sum(cv.pos(w)) * 1000 <= self.upperlng * 1000,
                    cv.sum(cv.neg(w)) * 1000 <= self.uppersht * 1000,
                ]
                if self.card is not None:
                    constraints += [
                        cv.sum(e) <= self.card,
                        w >= -self.uppersht * e,
                        w <= self.upperlng * e,
                    ]

        # Problem Linear Constraints

        if self.ainequality is not None and self.binequality is not None:
            A = np.array(self.ainequality, ndmin=2) * 1000
            B = np.array(self.binequality, ndmin=2) * 1000
            if obj == "Sharpe":
                constraints += [A @ w - B @ k >= 0]
            else:
                constraints += [A @ w - B >= 0]

        # Number of Effective Assets Constraints

        if self.nea is not None:
            if obj == "Sharpe":
                constraints += [cv.norm(w, "fro") <= 1 / self.nea**0.5 * k]
            else:
                constraints += [cv.norm(w, "fro") <= 1 / self.nea**0.5]

        # Tracking Error Model Variables

        c = np.array(self.benchweights, ndmin=2)
        if self.kindbench == True:
            bench = returns @ c
        elif self.kindbench == False:
            bench = np.array(self.benchindex, ndmin=2)

        # Tracking error Constraints

        if obj == "Sharpe":
            if self.allowTE == True:
                TE_1 = cv.norm(returns @ w - bench @ k, "fro") / cv.sqrt(n - 1)
                constraints += [TE_1 * 1000 <= self.TE * k * 1000]
        else:
            if self.allowTE == True:
                TE_1 = cv.norm(returns @ w - bench, "fro") / cv.sqrt(n - 1)
                constraints += [TE_1 * 1000 <= self.TE * 1000]

        # Turnover Constraints

        if obj == "Sharpe":
            if self.allowTO == True:
                TO_1 = cv.abs(w - c @ k) * 1000
                constraints += [TO_1 <= self.turnover * k * 1000]
        else:
            if self.allowTO == True:
                TO_1 = cv.abs(w - c) * 1000
                constraints += [TO_1 <= self.turnover * 1000]

        # Problem return Constraints

        if self.lowerret is not None:
            if obj == "Sharpe":
                constraints += [ret >= self.lowerret * k]
            else:
                constraints += [ret >= self.lowerret]

        # Problem risk Constraints

        if self.upperdev is not None:
            if obj == "Sharpe":
                constraints += [g <= self.upperdev * k]
            else:
                constraints += [g <= self.upperdev]
            constraints += devconstraints

        if self.uppermad is not None:
            if obj == "Sharpe":
                constraints += [risk2 <= self.uppermad * k / 2]
            else:
                constraints += [risk2 <= self.uppermad / 2]
            madmodel = True

        if self.uppersdev is not None:
            if obj == "Sharpe":
                constraints += [risk3 <= self.uppersdev * k]
            else:
                constraints += [risk3 <= self.uppersdev]
            madmodel = True

        if self.upperCVaR is not None:
            if obj == "Sharpe":
                constraints += [risk4 <= self.upperCVaR * k]
            else:
                constraints += [risk4 <= self.upperCVaR]
            constraints += cvarconstraints

        if self.upperwr is not None:
            if obj == "Sharpe":
                constraints += [-X <= self.upperwr * k]
            else:
                constraints += [-X <= self.upperwr]
            constraints += wrconstraints

        if self.upperflpm is not None:
            if obj == "Sharpe":
                constraints += [risk6 <= self.upperflpm * k]
            else:
                constraints += [risk6 <= self.upperflpm]
            lpmmodel = True

        if self.upperslpm is not None:
            if obj == "Sharpe":
                constraints += [risk7 <= self.upperslpm * k]
            else:
                constraints += [risk7 <= self.upperslpm]
            lpmmodel = True

        if self.uppermdd is not None:
            if obj == "Sharpe":
                constraints += [U[1:] - X1 <= self.uppermdd * k]
            else:
                constraints += [U[1:] - X1 <= self.uppermdd]
            constraints += mddconstraints
            drawdown = True

        if self.upperadd is not None:
            if obj == "Sharpe":
                constraints += [risk9 <= self.upperadd * k]
            else:
                constraints += [risk9 <= self.upperadd]
            drawdown = True

        if self.upperCDaR is not None:
            if obj == "Sharpe":
                constraints += [risk10 <= self.upperCDaR * k]
            else:
                constraints += [risk10 <= self.upperCDaR]
            constraints += cdarconstraints
            drawdown = True

        if self.upperuci is not None:
            if obj == "Sharpe":
                constraints += [risk11 <= self.upperuci * 1000 * k]
            else:
                constraints += [risk11 <= self.upperuci * 1000]
            drawdown = True

        if self.upperEVaR is not None:
            if obj == "Sharpe":
                constraints += [risk12 <= self.upperEVaR * k]
            else:
                constraints += [risk12 <= self.upperEVaR]
            constraints += evarconstraints

        if self.upperEDaR is not None:
            if obj == "Sharpe":
                constraints += [risk13 <= self.upperEDaR * k]
            else:
                constraints += [risk13 <= self.upperEDaR]
            constraints += edarconstraints

        if self.uppergmd is not None:
            if obj == "Sharpe":
                constraints += [risk14 <= self.uppergmd * k / 2]
            else:
                constraints += [risk14 <= self.uppergmd / 2]
            constraints += gmdconstraints
            owamodel = True

        if self.uppertg is not None:
            if obj == "Sharpe":
                constraints += [risk15 <= self.uppertg * k]
            else:
                constraints += [risk15 <= self.uppertg]
            constraints += tgconstraints
            owamodel = True

        if self.upperrg is not None:
            if obj == "Sharpe":
                constraints += [risk16 <= self.upperrg * k]
            else:
                constraints += [risk16 <= self.upperrg]
            constraints += rgconstraints
            owamodel = True

        if self.uppercvrg is not None:
            if obj == "Sharpe":
                constraints += [risk17 <= self.uppercvrg * k]
            else:
                constraints += [risk17 <= self.uppercvrg]
            constraints += cvrgconstraints
            owamodel = True

        if self.uppertgrg is not None:
            if obj == "Sharpe":
                constraints += [risk18 <= self.uppertgrg * k]
            else:
                constraints += [risk18 <= self.uppertgrg]
            constraints += tgrgconstraints
            owamodel = True

        # Defining risk function

        if rm == "MV":
            risk = risk1
            if self.upperdev is None:
                constraints += devconstraints
        elif rm == "MAD":
            risk = risk2
            madmodel = True
        elif rm == "MSV":
            risk = risk3
            madmodel = True
        elif rm == "CVaR":
            risk = risk4
            if self.upperCVaR is None:
                constraints += cvarconstraints
        elif rm == "WR":
            risk = risk5
            if self.upperwr is None:
                constraints += wrconstraints
        elif rm == "FLPM":
            risk = risk6
            lpmmodel = True
        elif rm == "SLPM":
            risk = risk7
            lpmmodel = True
        elif rm == "MDD":
            risk = risk8
            drawdown = True
            if self.uppermdd is None:
                constraints += mddconstraints
        elif rm == "ADD":
            risk = risk9
            drawdown = True
        elif rm == "CDaR":
            risk = risk10
            drawdown = True
            if self.upperCDaR is None:
                constraints += cdarconstraints
        elif rm == "UCI":
            risk = risk11
            drawdown = True
            l = l / 1000
        elif rm == "EVaR":
            risk = risk12
            if self.upperEVaR is None:
                constraints += evarconstraints
        elif rm == "EDaR":
            risk = risk13
            drawdown = True
            if self.upperEDaR is None:
                constraints += edarconstraints
        elif rm == "GMD":
            risk = risk14
            owamodel = True
            if self.uppergmd is None:
                constraints += gmdconstraints
        elif rm == "TG":
            risk = risk15
            owamodel = True
            if self.uppertg is None:
                constraints += tgconstraints
        elif rm == "RG":
            risk = risk16
            owamodel = True
            if self.upperrg is None:
                constraints += rgconstraints
        elif rm == "CVRG":
            risk = risk17
            owamodel = True
            if self.uppertgrg is None:
                constraints += cvrgconstraints
        elif rm == "TGRG":
            risk = risk18
            owamodel = True
            if self.uppertg is None:
                constraints += tgrgconstraints

        if madmodel == True:
            constraints += madconstraints
        if lpmmodel == True:
            constraints += lpmconstraints
        if drawdown == True:
            constraints += ddconstraints
        if owamodel == True:
            constraints += owaconstraints

        # Frontier Variables

        portafolio = {}

        for i in self.assetslist:
            portafolio.update({i: []})

        # Optimization Process

        # Defining objective function
        if obj == "Sharpe":
            if model == "Classic":
                if kelly == "exact":
                    constraints += [risk <= 1]
                    constraints += [
                        cv.constraints.ExpCone(gr, np.ones((n, 1)) @ k, k + returns @ w)
                    ]
                    objective = cv.Maximize(ret * 1000)
                elif kelly == "approx":
                    constraints += [risk <= 1]
                    if rm != "MV":
                        constraints += devconstraints
                    objective = cv.Maximize(ret)
                elif kelly == False:
                    constraints += [mu @ w - rf0 * k == 1]
                    objective = cv.Minimize(risk * 1000)
            else:
                constraints += [mu @ w - rf0 * k == 1]
                objective = cv.Minimize(risk * 1000)
        elif obj == "MinRisk":
            objective = cv.Minimize(risk * 1000)
        elif obj == "Utility":
            objective = cv.Maximize(ret - l * risk)
        elif obj == "MaxRet":
            objective = cv.Maximize(ret * 1000)

        try:
            prob = cv.Problem(objective, constraints)
            for solver in self.solvers:
                try:
                    if len(self.sol_params) == 0:
                        prob.solve(solver=solver)
                    else:
                        prob.solve(solver=solver, **self.sol_params[solver])
                except:
                    pass
                if w.value is not None:
                    break

            if obj == "Sharpe":
                weights = np.array(w.value / k.value, ndmin=2).T
                if rm == "EVaR" or self.upperEVaR is not None:
                    self.z_EVaR = s1.value / k.value
                if rm == "EDaR" or self.upperEDaR is not None:
                    self.z_EDaR = s2.value / k.value
            else:
                weights = np.array(w.value, ndmin=2).T
                if rm == "EVaR" or self.upperEVaR is not None:
                    self.z_EVaR = s1.value
                if rm == "EDaR" or self.upperEDaR is not None:
                    self.z_EDaR = s2.value

            if self.sht == False:
                weights = np.abs(weights) / np.sum(np.abs(weights)) * self.budget

            for j in self.assetslist:
                portafolio[j].append(weights[0, self.assetslist.index(j)])

        except:
            pass

        try:
            self.optimal = pd.DataFrame(
                portafolio, index=["weights"], dtype=np.float64
            ).T
        except:
            self.optimal = None
            print("The problem doesn't have a solution with actual input parameters")

        return self.optimal

    def rp_optimization(self, model="Classic", rm="MV", rf=0, b=None, hist=True):
        r"""
        This method that calculates the risk parity portfolio using the risk
        budgeting approach :cite:`a-Roncalli` :cite:`a-RichardRoncalli`,
        according to the optimization model selected by the user. The general
        problem that solves is:
        
        .. math::
            \begin{aligned}
            &\underset{w}{\min} & & \phi(w)\\
            &\text{s.t.} & & b \log(w) \geq c\\
            & & & \mu w \geq \overline{\mu} \\
            & & & Aw \geq B \\
            & & & w \geq 0 \\
            \end{aligned}
        
        Where:
        
        :math:`w` are the weights of the portfolio.
        
        :math:`\mu`: is the vector of expected returns.
    
        :math:`b` is a vector of risk constraints.
        
        :math:`Aw \geq B`: is a set of linear constraints.
        
        :math:`\phi(w)`: is a risk measure.
        
        :math:`c`: is an arbitrary constant.
        
        Parameters
        ----------
        model : str can be 'Classic' or 'FM'
            The model used for optimize the portfolio.
            The default is 'Classic'. Posible values are:

            - 'Classic': use estimates of expected return vector and covariance matrix that depends on historical data.
            - 'FM': use estimates of expected return vector and covariance matrix based on a Risk Factor model specified by the user.
            
        rm : str, optional
            The risk measure used to optimze the portfolio.
            The default is 'MV'. Posible values are:
            
            - 'MV': Standard Deviation.
            - 'MAD': Mean Absolute Deviation.
            - 'GMD': Gini Mean Difference.
            - 'MSV': Semi Standard Deviation.
            - 'FLPM': First Lower Partial Moment (Omega Ratio).
            - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
            - 'CVaR': Conditional Value at Risk.
            - 'TG': Tail Gini.
            - 'EVaR': Entropic Value at Risk.
            - 'CVRG': CVaR range of returns.
            - 'TGRG': Tail Gini range of returns.
            - 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
            - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
            - 'UCI': Ulcer Index of uncompounded cumulative returns.

        rf : float, optional
            Risk free rate, must be in the same period of assets returns.
            Used for 'FLPM' and 'SLPM'.
            The default is 0.                
        b : float, optional
            The vector of risk constraints per asset.
            The default is 1/n (number of assets).
        hist : bool, optional
            Indicate what kind of returns are used to calculate risk measures
            that depends on scenarios (All except 'MV' risk measure). 
            If model = 'FM', True means historical covariance and returns and
            False means Risk Factor model for covariance and returns. The
            default is True.
            
        Returns
        -------
        w : DataFrame
            The weights of optimal portfolio.

        """

        # General model Variables

        mu = None
        sigma = None
        returns = None
        if model == "Classic":
            mu = np.array(self.mu, ndmin=2)
            sigma = np.array(self.cov, ndmin=2)
            returns = np.array(self.returns, ndmin=2)
            nav = np.array(self.nav, ndmin=2)
        elif model == "FM":
            mu = np.array(self.mu_fm, ndmin=2)
            if hist == False:
                sigma = np.array(self.cov_fm, ndmin=2)
                returns = np.array(self.returns_fm, ndmin=2)
                nav = np.array(self.nav_fm, ndmin=2)
            elif hist == True:
                sigma = np.array(self.cov, ndmin=2)
                returns = np.array(self.returns, ndmin=2)
                nav = np.array(self.nav, ndmin=2)

        # General Model Variables

        if b is None:
            b = np.ones((1, mu.shape[1]))
            b = b / mu.shape[1]

        returns = np.array(returns, ndmin=2)
        w = cv.Variable((mu.shape[1], 1))
        k = cv.Variable((1, 1))
        rf0 = rf
        n = returns.shape[0]
        ret = mu @ w
        constraints = []

        # MV Model Variables

        g = cv.Variable(nonneg=True)
        G = sqrtm(sigma)
        risk1 = g**2
        devconstraints = [cv.SOC(g, G.T @ w)]

        # MAD Model Variables

        Y = cv.Variable((returns.shape[0], 1))
        u = np.ones((returns.shape[0], 1)) * mu
        a = returns - u
        risk2 = cv.sum(Y) / n
        # madconstraints=[a @ w >= -Y, a @ w <= Y, Y >= 0]
        madconstraints = [a @ w >= -Y, Y >= 0]

        # Semi Variance Model Variables

        risk3 = cv.norm(Y, "fro") / cv.sqrt(n - 1)

        # CVaR Model Variables

        VaR = cv.Variable((1, 1))
        alpha = self.alpha
        X = returns @ w
        Z = cv.Variable((returns.shape[0], 1))
        risk4 = VaR + 1 / (alpha * n) * cv.sum(Z)
        cvarconstraints = [Z >= 0, Z >= -X - VaR]

        # Lower Partial Moment Variables

        lpm = cv.Variable((returns.shape[0], 1))
        lpmconstraints = [lpm >= 0, lpm >= rf0 * k - X]

        # First Lower Partial Moment (Omega) Model Variables

        risk6 = cv.sum(lpm) / n

        # Second Lower Partial Moment (Sortino) Model Variables

        risk7 = cv.norm(lpm, "fro") / cv.sqrt(n - 1)

        # Drawdown Model Variables

        X1 = k + nav @ w
        U = cv.Variable((nav.shape[0] + 1, 1))
        ddconstraints = [
            U[1:] * 1000 >= X1 * 1000,
            U[1:] * 1000 >= U[:-1] * 1000,
            U[1:] * 1000 >= 1 * 1000 * k,
            U[0] * 1000 == 1 * 1000 * k,
        ]

        # Conditional Drawdown Model Variables

        CDaR = cv.Variable((1, 1))
        Zd = cv.Variable((nav.shape[0], 1))
        risk10 = CDaR + 1 / (alpha * n) * cv.sum(Zd)
        cdarconstraints = [
            Zd * 1000 >= U[1:] * 1000 - X1 * 1000 - CDaR * 1000,
            Zd * 1000 >= 0,
        ]

        # Ulcer Index Model Variables

        risk11 = cv.norm(U[1:] - X1, "fro") / np.sqrt(n)

        # Entropic Value at Risk Model Variables

        t1 = cv.Variable((1, 1))
        s1 = cv.Variable((1, 1), nonneg=True)
        ui = cv.Variable((n, 1))
        risk12 = t1 + s1 * np.log(1 / (alpha * n))
        evarconstraints = [cv.sum(ui) * 1000 <= s1 * 1000]
        evarconstraints += [
            cv.constraints.ExpCone(
                -X * 1000 - t1 * 1000, np.ones((n, 1)) @ s1 * 1000, ui * 1000
            )
        ]

        # Entropic Drawdown at Risk Model Variables

        t2 = cv.Variable((1, 1))
        s2 = cv.Variable((1, 1), nonneg=True)
        uj = cv.Variable((n, 1))
        risk13 = t2 + s2 * np.log(1 / (alpha * n))
        edarconstraints = [cv.sum(uj) * 1000 <= s2 * 1000]
        edarconstraints += [
            cv.constraints.ExpCone(
                U[1:] * 1000 - X1 * 1000 - t2 * 1000,
                np.ones((n, 1)) @ s2 * 1000,
                uj * 1000,
            )
        ]

        # Gini Mean Difference Model Variables

        a1 = cv.Variable((n, 1))
        b1 = cv.Variable((n, 1))
        y = cv.Variable((n, 1))
        risk14 = cv.sum(a1 + b1)

        owaconstraints = [returns @ w == y]
        gmd_w = owa.owa_gmd(n) / 2

        onesvec = np.ones((n, 1))
        gmdconstraints = [y @ gmd_w.T <= onesvec @ a1.T + b1 @ onesvec.T]

        # Tail Gini Model Variables

        a2 = cv.Variable((n, 1))
        b2 = cv.Variable((n, 1))
        risk15 = cv.sum(a2 + b2)
        a_sim = self.a_sim

        tg_w = owa.owa_tg(n, alpha=alpha, a_sim=a_sim)
        tgconstraints = [y @ tg_w.T <= onesvec @ a2.T + b2 @ onesvec.T]

        # CVaR Range Model Variables

        a4 = cv.Variable((n, 1))
        b4 = cv.Variable((n, 1))
        risk17 = cv.sum(a4 + b4)

        if self.beta is None:
            beta = alpha
        else:
            beta = self.beta

        cvrg_w = owa.owa_cvrg(n, alpha=alpha, beta=beta)
        cvrgconstraints = [y @ cvrg_w.T <= onesvec @ a4.T + b4 @ onesvec.T]

        # Tail Gini Range Model Variables

        a5 = cv.Variable((n, 1))
        b5 = cv.Variable((n, 1))
        risk18 = cv.sum(a5 + b5)

        if self.b_sim is None:
            b_sim = a_sim
        else:
            b_sim = self.b_sim

        tgrg_w = owa.owa_tgrg(n, alpha=alpha, a_sim=a_sim, beta=beta, b_sim=b_sim)
        tgrgconstraints = [y @ tgrg_w.T <= onesvec @ a5.T + b5 @ onesvec.T]

        # Problem Linear Constraints

        if self.ainequality is not None and self.binequality is not None:
            A = np.array(self.ainequality, ndmin=2) * 1000
            B = np.array(self.binequality, ndmin=2) * 1000
            constraints += [A @ w - B @ k >= 0]

        # Problem Return Constraint

        if self.lowerret is not None:
            constraints += [ret >= self.lowerret * k]

        # Defining risk function

        if rm == "MV":
            risk = risk1
            constraints += devconstraints
        elif rm == "MAD":
            risk = risk2
            constraints += madconstraints
        elif rm == "MSV":
            risk = risk3
            constraints += madconstraints
        elif rm == "CVaR":
            risk = risk4
            constraints += cvarconstraints
        elif rm == "FLPM":
            risk = risk6
            constraints += lpmconstraints
        elif rm == "SLPM":
            risk = risk7
            constraints += lpmconstraints
        elif rm == "CDaR":
            risk = risk10
            constraints += ddconstraints
            constraints += cdarconstraints
        elif rm == "UCI":
            risk = risk11
            constraints += ddconstraints
        elif rm == "EVaR":
            risk = risk12
            constraints += evarconstraints
        elif rm == "EDaR":
            risk = risk13
            constraints += ddconstraints
            constraints += edarconstraints
        elif rm == "GMD":
            risk = risk14
            constraints += owaconstraints
            constraints += gmdconstraints
        elif rm == "TG":
            risk = risk15
            constraints += owaconstraints
            constraints += tgconstraints
        elif rm == "CVRG":
            risk = risk17
            constraints += owaconstraints
            constraints += cvrgconstraints
        elif rm == "TGRG":
            risk = risk18
            constraints += owaconstraints
            constraints += tgrgconstraints

        # Risk budgeting constraint

        constraints += [
            b @ cv.log(w) >= 1,
            w * 1000 >= 0,
            cv.sum(w) == k,
        ]

        # Frontier Variables

        portafolio = {}

        for i in self.assetslist:
            portafolio.update({i: []})

        # Optimization Process

        # Defining objective function

        objective = cv.Minimize(risk * 1000)

        try:
            prob = cv.Problem(objective, constraints)
            for solver in self.solvers:
                try:
                    if len(self.sol_params) == 0:
                        prob.solve(solver=solver)
                    else:
                        prob.solve(solver=solver, **self.sol_params[solver])
                except:
                    pass
                if w.value is not None:
                    break

            weights = np.array(w.value, ndmin=2).T
            weights = np.abs(weights) / np.sum(np.abs(weights))

            for j in self.assetslist:
                portafolio[j].append(weights[0, self.assetslist.index(j)])

        except:
            pass

        try:
            self.rp_optimal = pd.DataFrame(
                portafolio, index=["weights"], dtype=np.float64
            ).T
        except:
            self.rp_optimal = None
            print("The problem doesn't have a solution with actual input parameters")

        return self.rp_optimal

    def rrp_optimization(self, model="Classic", version="A", l=1, b=None, hist=True):
        r"""
        This method that calculates the relaxed risk parity portfolio according
        to the optimization model and version selected by the user
        :cite:`a-RichardRoncalli`. The general problem that solves is:
        
        .. math::
            \begin{aligned}
            &\underset{w}{\min} & & \psi - \gamma & \\
            &\text{s.t.} & & \zeta = \Sigma w \\
            & & & w^{T} \Sigma w \leq N \left ( \psi^{2} - \rho^{2} \right ) & \\
            & & & w_{i} \zeta_{i} \geq \gamma^{2} & \forall i=1 , \ldots , N \\
            & & & \lambda x^{T} \Theta x \leq \rho^{2} & \\
            & & & \mu w \geq \overline{\mu} & \\
            & & & Aw \geq B & \\
            & & & \sum^{N}_{i=1} w_{i} = 1 & \\
            & & & \psi, \gamma, \rho, w  \geq 0 & \\
            \end{aligned}
        
        Where:
    
        :math:`w`: is the vector of weights of the optimum portfolio.
        
        :math:`\mu`: is the vector of expected returns.
        
        :math:`\Sigma`: is the covariance matrix of assets returns.
        
        :math:`\psi`: is the average risk of the portfolio.
        
        :math:`\gamma`: is the lower bound of each asset risk constribution.
        
        :math:`\zeta_{i}`: is the marginal risk of asset :math:`i`.
        
        :math:`\rho`: is a regularization variable.
        
        :math:`\lambda`: is a penalty parameter of :math:`\rho`.
        
        :math:`\Theta = \text{diag}(\Sigma)`
        
        :math:`Aw \geq B`: is a set of linear constraints.
        
        Parameters
        ----------
        model : str can be 'Classic' or 'FM'
            The model used for optimize the portfolio.
            The default is 'Classic'. Posible values are:

            - 'Classic': use estimates of expected return vector and covariance matrix that depends on historical data.
            - 'FM': use estimates of expected return vector and covariance matrix based on a Risk Factor model specified by the user.
            
        version : str can be 'A', 'B' or 'C'
            Relaxed risk parity model version proposed in :cite:`a-RichardRoncalli`.
            The default is 'A'. Posible values are:
                
            - 'A': without regularization and penalization constraints.
            - 'B': with regularization constraint but without penalization constraint.
            - 'C': with regularization and penalization constraints.
            
        l : float, optional
            The penalization factor of penalization constraints. Only used with
            version 'C'. The default is 1.
        b : float, optional
            The vector of risk constraints per asset.
            The default is 1/n (number of assets).
        hist : bool, optional
            Indicate what kind of covariance matrix is used. 
            If model = 'FM', True means historical covariance and
            False means Risk Factor model for covariance. The default is
            True.
            
        Returns
        -------
        w : DataFrame
            The weights of optimal portfolio.

        """

        # General model Variables

        mu = None
        sigma = None
        returns = None
        if model == "Classic":
            mu = np.array(self.mu, ndmin=2)
            sigma = np.array(self.cov, ndmin=2)
            returns = np.array(self.returns, ndmin=2)
            nav = np.array(self.nav, ndmin=2)
        elif model == "FM":
            mu = np.array(self.mu_fm, ndmin=2)
            if hist == False:
                sigma = np.array(self.cov_fm, ndmin=2)
                returns = np.array(self.returns_fm, ndmin=2)
                nav = np.array(self.nav_fm, ndmin=2)
            elif hist == True:
                sigma = np.array(self.cov, ndmin=2)
                returns = np.array(self.returns, ndmin=2)
                nav = np.array(self.nav, ndmin=2)

        # General Model Variables

        if b is None:
            b = np.ones((1, mu.shape[1]))
            b = b / mu.shape[1]

        returns = np.array(returns, ndmin=2)
        w = cv.Variable((mu.shape[1], 1))
        n = returns.shape[1]
        ret = mu @ w

        # RRP Model Variables

        G = sqrtm(sigma)
        Theta = np.diag(np.sqrt(np.diag(sigma)))
        psi = cv.Variable(nonneg=True)
        rho = cv.Variable(nonneg=True)
        gamma = cv.Variable(nonneg=True)
        zeta = cv.Variable((mu.shape[1], 1))
        risk = psi - gamma

        # General Model Constraints

        constraints = []
        constraints += [
            zeta == sigma @ w,
            cv.sum(w) == 1,
            gamma >= 0,
            psi >= 0,
            zeta >= 0,
            w >= 0,
        ]

        for i in range(mu.shape[1]):
            constraints += [
                cv.SOC(
                    w[i, 0] + zeta[i, 0], cv.vstack([2 * gamma, w[i, 0] - zeta[i, 0]])
                )
            ]

        # Specific Model Constraints

        if version == "A":
            constraints += [cv.SOC(n**0.5 * psi, G.T @ w)]
        elif version == "B":
            constraints += [
                cv.SOC(
                    2 * n**0.5 * psi,
                    cv.vstack([2 * G.T @ w, -2 * n**0.5 * rho * np.ones((1, 1))]),
                )
            ]
            constraints += [cv.SOC(rho, G.T @ w)]
            constraints += [rho >= 0]
        elif version == "C":
            constraints += [
                cv.SOC(
                    2 * n**0.5 * psi,
                    cv.vstack([2 * G.T @ w, -2 * n**0.5 * rho * np.ones((1, 1))]),
                )
            ]
            constraints += [cv.SOC(rho, l**0.5 * Theta.T @ w)]
            constraints += [rho >= 0]

        # Problem Linear Constraints

        if self.ainequality is not None and self.binequality is not None:
            A = np.array(self.ainequality, ndmin=2) * 1000
            B = np.array(self.binequality, ndmin=2) * 1000
            constraints += [A @ w - B >= 0]

        # Problem Return Constraint

        if self.lowerret is not None:
            constraints += [ret >= self.lowerret]

        # Frontier Variables

        portafolio = {}

        for i in self.assetslist:
            portafolio.update({i: []})

        # Optimization Process

        # Defining objective function

        objective = cv.Minimize(risk * 1000)

        try:
            prob = cv.Problem(objective, constraints)
            for solver in self.solvers:
                try:
                    if len(self.sol_params) == 0:
                        prob.solve(solver=solver)
                    else:
                        prob.solve(solver=solver, **self.sol_params[solver])
                except:
                    pass
                if w.value is not None:
                    break

            weights = np.array(w.value, ndmin=2).T
            weights = np.abs(weights) / np.sum(np.abs(weights))

            for j in self.assetslist:
                portafolio[j].append(weights[0, self.assetslist.index(j)])

        except:
            pass

        try:
            self.rp_optimal = pd.DataFrame(
                portafolio, index=["weights"], dtype=np.float64
            ).T
        except:
            self.rp_optimal = None
            print("The problem doesn't have a solution with actual input parameters")

        return self.rp_optimal

    def wc_optimization(self, obj="Sharpe", rf=0, l=2, Umu="box", Ucov="box"):
        r"""
        This method that calculates the worst case mean variance portfolio
        according to the objective function and uncertainty sets selected by
        the user.

        Parameters
        ----------
        obj : str can be {'MinRisk', 'Utility', 'Sharpe' or 'MaxRet'}.
            Objective function of the optimization model.
            The default is 'Sharpe'. Posible values are:

            - 'MinRisk': Minimize the worst case formulation of the selected risk measure.
            - 'Utility': Maximize the worst case formulation of the Utility function :math:`\mu w - l \phi_{i}(w)`.
            - 'Sharpe': Maximize the worst case formulation of the risk adjusted return ratio based on the selected risk measure.
            - 'MaxRet': Maximize the worst case formulation of the expected return of the portfolio.

        rf : float, optional
            Risk free rate, must be in the same period of assets returns.
            The default is 0.
        l : scalar, optional
            Risk aversion factor of the 'Utility' objective function.
            The default is 2.
        Umu : str, optional
            The type of uncertainty set for the mean vector used in the model.
            The default is 'box'. Posible values are:

            - 'box': Use a box uncertainty set for the mean vector.
            - 'ellip': Use a elliptical uncertainty set for the mean vector.
            - None: Don't use an uncertainty set for mean vector.

        Ucov : str, optional
            The type of uncertainty set for the covariance matrix used in the model.
            The default is 'box'. Posible values are:

            - 'box': Use a box uncertainty set for the covariance matrix.
            - 'ellip': Use a elliptical uncertainty set for the covariance matrix.
            - None: Don't use an uncertainty set for covariance matrix.

        Returns
        -------
        w : DataFrame
            The weights of optimal portfolio.

        """

        # General model Variables

        mu = self.mu.to_numpy()
        sigma = self.cov.to_numpy()
        returns = self.returns.to_numpy()

        cov_l = self.cov_l.to_numpy()
        cov_u = self.cov_u.to_numpy()
        cov_mu = self.cov_mu.to_numpy()
        cov_sigma = self.cov_sigma.to_numpy()
        d_mu = self.d_mu.to_numpy()
        k_mu = self.k_mu
        k_sigma = self.k_sigma

        n = mu.shape[1]
        w = cv.Variable((n, 1))
        Au = cv.Variable((n, n), symmetric=True)
        Al = cv.Variable((n, n), symmetric=True)
        X = cv.Variable((n, n), symmetric=True)
        Z = cv.Variable((n, n), symmetric=True)

        k = cv.Variable((1, 1))
        rf0 = rf
        g = cv.Variable(nonneg=True)

        constraints = []

        # Uncertainty Sets for Mean Vector

        if Umu == "box":
            if obj == "Sharpe":
                constraints += [mu @ w - d_mu @ cv.abs(w) - rf0 * k >= 1]
            else:
                ret = mu @ w - d_mu @ cv.abs(w)
        elif Umu == "ellip":
            if obj == "Sharpe":
                constraints += [
                    mu @ w - k_mu * cv.pnorm(sqrtm(cov_mu) @ w, 2) - rf0 * k >= 1
                ]
            else:
                ret = mu @ w - k_mu * cv.pnorm(sqrtm(cov_mu) @ w, 2)
        else:
            if obj == "Sharpe":
                constraints += [mu @ w - rf0 * k >= 1]
            else:
                ret = mu @ w

        # Uncertainty Sets for Covariance Matrix

        if Ucov == "box":
            M1 = cv.vstack([Au - Al, w.T])
            if obj == "Sharpe":
                M2 = cv.vstack([w, k])
            else:
                M2 = cv.vstack([w, np.ones((1, 1))])
            M = cv.hstack([M1, M2])
            risk = cv.trace(Au @ cov_u) - cv.trace(Al @ cov_l)
            constraints += [M >> 0, Au >= 0, Al >= 0]
        elif Ucov == "ellip":
            M1 = cv.vstack([X, w.T])
            if obj == "Sharpe":
                M2 = cv.vstack([w, k])
            else:
                M2 = cv.vstack([w, np.ones((1, 1))])
            M = cv.hstack([M1, M2])
            risk = cv.trace(sigma @ (X + Z))
            risk += k_sigma * cv.pnorm(sqrtm(cov_sigma) @ (cv.vec(X) + cv.vec(Z)), 2)
            constraints += [M >> 0, Z >> 0]
        else:
            G = sqrtm(sigma)
            risk = g**2
            constraints += [cv.SOC(g, G.T @ w)]

        # Cardinal Boolean Variables

        if self.card is not None:
            if obj == "Sharpe":
                e = cv.Variable((mu.shape[1], 1), boolean=True)
                e1 = cv.Variable((mu.shape[1], 1))
            else:
                e = cv.Variable((mu.shape[1], 1), boolean=True)

        # Problem Weight Constraints

        if obj == "Sharpe":
            constraints += [cv.sum(w) == self.budget * k, k >= 0]
            if self.sht == False:
                constraints += [w <= self.upperlng * k, w >= 0]
                if self.card is not None:
                    constraints += [
                        cv.sum(e) <= self.card,
                        e1 <= k,
                        e1 >= 0,
                        e1 <= 100000 * e,
                        e1 >= k - 100000 * (1 - e),
                        w <= self.upperlng * e1,
                    ]
            elif self.sht == True:
                constraints += [
                    cv.sum(cv.pos(w)) * 1000 <= self.upperlng * k * 1000,
                    cv.sum(cv.neg(w)) * 1000 <= self.uppersht * k * 1000,
                ]
                if self.card is not None:
                    constraints += [
                        cv.sum(e) <= self.card,
                        e1 <= k,
                        e1 >= 0,
                        e1 <= 100000 * e,
                        e1 >= k - 100000 * (1 - e),
                        w >= -self.uppersht * e1,
                        w <= self.upperlng * e1,
                    ]

        else:
            constraints += [cv.sum(w) == self.budget]
            if self.sht == False:
                constraints += [w <= self.upperlng, w >= 0]
                if self.card is not None:
                    constraints += [
                        cv.sum(e) <= self.card,
                        w <= self.upperlng * e,
                    ]

            elif self.sht == True:
                constraints += [
                    cv.sum(cv.pos(w)) * 1000 <= self.upperlng * 1000,
                    cv.sum(cv.neg(w)) * 1000 <= self.uppersht * 1000,
                ]
                if self.card is not None:
                    constraints += [
                        cv.sum(e) <= self.card,
                        w >= -self.uppersht * e,
                        w <= self.upperlng * e,
                    ]

        # Number of effective assets constraints

        if self.nea is not None:
            if obj == "Sharpe":
                constraints += [cv.sum_squares(w) * 1000 <= 1 / self.nea * k * 1000]
            else:
                constraints += [cv.sum_squares(w) * 1000 <= 1 / self.nea * 1000]

        # Tracking Error Model Variables

        c = np.array(self.benchweights, ndmin=2)
        if self.kindbench == True:
            bench = returns @ c
        elif self.kindbench == False:
            bench = np.array(self.benchindex, ndmin=2)

        # Problem aditional linear constraints

        if self.ainequality is not None and self.binequality is not None:
            A = np.array(self.ainequality, ndmin=2) * 1000
            B = np.array(self.binequality, ndmin=2) * 1000
            if obj == "Sharpe":
                constraints += [A @ w - B @ k >= 0]
            else:
                constraints += [A @ w - B >= 0]

        # Tracking error Constraints

        if obj == "Sharpe":
            if self.allowTE == True:
                TE_1 = cv.norm(returns @ w - bench @ k, "fro") / np.sqrt(n - 1)
                constraints += [TE_1 <= self.TE * k]
        else:
            if self.allowTE == True:
                TE_1 = cv.norm(returns @ w - bench, "fro") / np.sqrt(n - 1)
                constraints += [TE_1 <= self.TE]

        # Turnover Constraints

        if obj == "Sharpe":
            if self.allowTO == True:
                TO_1 = cv.abs(w - c @ k) * 1000
                constraints += [TO_1 <= self.turnover * k * 1000]
        else:
            if self.allowTO == True:
                TO_1 = cv.abs(w - c) * 1000
                constraints += [TO_1 <= self.turnover * 1000]

        # Frontier Variables

        portafolio = {}

        for i in self.assetslist:
            portafolio.update({i: []})

        # Optimization Process

        # Defining objective function
        if obj == "Sharpe":
            objective = cv.Minimize(risk)
        elif obj == "MinRisk":
            objective = cv.Minimize(risk)
        elif obj == "Utility":
            objective = cv.Maximize(ret - l * risk)
        elif obj == "MaxRet":
            objective = cv.Maximize(ret)

        try:
            prob = cv.Problem(objective, constraints)
            for solver in self.solvers:
                try:
                    if len(self.sol_params) == 0:
                        prob.solve(solver=solver)
                    else:
                        prob.solve(solver=solver, **self.sol_params[solver])
                except:
                    pass
                if w.value is not None:
                    break

            if obj == "Sharpe":
                weights = np.array(w.value / k.value, ndmin=2).T
            else:
                weights = np.array(w.value, ndmin=2).T

            if self.sht == False:
                weights = np.abs(weights) / np.sum(np.abs(weights)) * self.budget

            for j in self.assetslist:
                portafolio[j].append(weights[0, self.assetslist.index(j)])

        except:
            pass

        try:
            self.wc_optimal = pd.DataFrame(
                portafolio, index=["weights"], dtype=np.float64
            ).T
        except:
            self.wc_optimal = None
            print("The problem doesn't have a solution with actual input parameters")

        return self.wc_optimal

    def owa_optimization(self, obj="Sharpe", owa_w=None, kelly=False, rf=0, l=2):
        r"""
        This method that calculates the owa optimal portfolio according to the
        weight vector given by the user. The general problem that
        solves is:
        
        .. math::
            \begin{align}
            &\underset{w}{\text{optimize}} & & F(w)\\
            &\text{s. t.} & & Aw \geq B\\
            \end{align}
        
        Where:
            
        :math:`F(w)` is the objective function based on an owa risk measure.
    
        :math:`Aw \geq B` is a set of linear constraints.
        
        Parameters
        ----------
        obj : str can be {'MinRisk', 'Utility', 'Sharpe' or 'MaxRet'}.
            Objective function of the optimization model.
            The default is 'Sharpe'. Posible values are:

            - 'MinRisk': Minimize the selected risk measure.
            - 'Utility': Maximize the Utility function :math:`\mu w - l \phi_{i}(w)`.
            - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
            
        owa_w : 1darray, optional
            The owa weight used to define the owa risk measure.
            The default is 'MV'. Posible values are:
        kelly : str, optional
            Method used to calculate mean return. Posible values are False for
            arithmetic mean return, "approx" for approximate mean logarithmic 
            return using first and second moment and "exact" for mean logarithmic
            return. The default is False.
        rf : float, optional
            Risk free rate, must be in the same period of assets returns.
            The default is 0.
        l : scalar, optional
            Risk aversion factor of the 'Utility' objective function.
            The default is 2.

        Returns
        -------
        w : DataFrame
            The weights of optimal portfolio.

        """

        # General model Variables

        mu = self.mu.to_numpy()
        sigma = self.cov.to_numpy()
        returns = self.returns.to_numpy()
        w = cv.Variable((mu.shape[1], 1))
        k = cv.Variable((1, 1))
        rf0 = rf
        n = returns.shape[0]
        gr = cv.Variable((n, 1))

        # MV Model Variables (for approx log returns)

        g = cv.Variable(nonneg=True)
        G = sqrtm(sigma)
        devconstraints = [cv.SOC(g, G.T @ w)]

        # Return Variables

        if kelly == "exact":
            if obj == "Sharpe":
                ret = 1 / n * cv.sum(gr) - rf0 * k
            else:
                ret = 1 / n * cv.sum(cv.log(1 + returns @ w))
        elif kelly == "approx":
            if obj == "Sharpe":
                ret = mu @ w - 0.5 * cv.quad_over_lin(g, k)
            else:
                ret = mu @ w - 0.5 * g**2
        elif kelly == False:
            ret = mu @ w

        # OWA Model Variables

        a = cv.Variable((n, 1))
        b = cv.Variable((n, 1))
        y = cv.Variable((n, 1))
        risk = cv.sum(a + b)

        constraints = []
        constraints += [returns @ w == y]
        if owa_w is None:
            owa_w = owa.owa_gmd(n) / 2

        onesvec = np.ones((n, 1))
        constraints += [y @ owa_w.T <= onesvec @ a.T + b @ onesvec.T]

        # Cardinal Boolean Variables

        if self.card is not None:
            if obj == "Sharpe":
                e = cv.Variable((mu.shape[1], 1), boolean=True)
                e1 = cv.Variable((mu.shape[1], 1))
            else:
                e = cv.Variable((mu.shape[1], 1), boolean=True)

        # Problem Weight Constraints

        if obj == "Sharpe":
            constraints += [cv.sum(w) == self.budget * k, k * 1000 >= 0]
            if self.sht == False:
                constraints += [w <= self.upperlng * k, w * 1000 >= 0]
                if self.card is not None:
                    constraints += [
                        cv.sum(e) <= self.card,
                        e1 <= k,
                        e1 >= 0,
                        e1 <= 100000 * e,
                        e1 >= k - 100000 * (1 - e),
                        w <= self.upperlng * e1,
                    ]
            elif self.sht == True:
                constraints += [
                    cv.sum(cv.pos(w)) * 1000 <= self.upperlng * k * 1000,
                    cv.sum(cv.neg(w)) * 1000 <= self.uppersht * k * 1000,
                ]
                if self.card is not None:
                    constraints += [
                        cv.sum(e) <= self.card,
                        e1 <= k,
                        e1 >= 0,
                        e1 <= 100000 * e,
                        e1 >= k - 100000 * (1 - e),
                        w >= -self.uppersht * e1,
                        w <= self.upperlng * e1,
                    ]

        else:
            constraints += [cv.sum(w) == self.budget]
            if self.sht == False:
                constraints += [w <= self.upperlng, w * 1000 >= 0]
                if self.card is not None:
                    constraints += [
                        cv.sum(e) <= self.card,
                        w <= self.upperlng * e,
                    ]

            elif self.sht == True:
                constraints += [
                    cv.sum(cv.pos(w)) * 1000 <= self.upperlng * 1000,
                    cv.sum(cv.neg(w)) * 1000 <= self.uppersht * 1000,
                ]
                if self.card is not None:
                    constraints += [
                        cv.sum(e) <= self.card,
                        w >= -self.uppersht * e,
                        w <= self.upperlng * e,
                    ]

        # Problem Linear Constraints

        if self.ainequality is not None and self.binequality is not None:
            A = np.array(self.ainequality, ndmin=2) * 1000
            B = np.array(self.binequality, ndmin=2) * 1000
            if obj == "Sharpe":
                constraints += [A @ w - B @ k >= 0]
            else:
                constraints += [A @ w - B >= 0]

        # Number of Effective Assets Constraints

        if self.nea is not None:
            if obj == "Sharpe":
                constraints += [cv.norm(w, "fro") <= 1 / self.nea**0.5 * k]
            else:
                constraints += [cv.norm(w, "fro") <= 1 / self.nea**0.5]

        # Tracking Error Model Variables

        c = np.array(self.benchweights, ndmin=2)
        if self.kindbench == True:
            bench = returns @ c
        elif self.kindbench == False:
            bench = np.array(self.benchindex, ndmin=2)

        # Tracking error Constraints

        if obj == "Sharpe":
            if self.allowTE == True:
                TE_1 = cv.norm(returns @ w - bench @ k, "fro") / cv.sqrt(n - 1)
                constraints += [TE_1 * 1000 <= self.TE * k * 1000]
        else:
            if self.allowTE == True:
                TE_1 = cv.norm(returns @ w - bench, "fro") / cv.sqrt(n - 1)
                constraints += [TE_1 * 1000 <= self.TE * 1000]

        # Turnover Constraints

        if obj == "Sharpe":
            if self.allowTO == True:
                TO_1 = cv.abs(w - c @ k) * 1000
                constraints += [TO_1 <= self.turnover * k * 1000]
        else:
            if self.allowTO == True:
                TO_1 = cv.abs(w - c) * 1000
                constraints += [TO_1 <= self.turnover * 1000]

        # Problem return Constraints

        if self.lowerret is not None:
            if obj == "Sharpe":
                constraints += [ret >= self.lowerret * k]
            else:
                constraints += [ret >= self.lowerret]

        # Frontier Variables

        portafolio = {}

        for i in self.assetslist:
            portafolio.update({i: []})

        # Optimization Process

        # Defining objective function
        if obj == "Sharpe":
            if kelly == "exact":
                constraints += [risk <= 1]
                constraints += [
                    cv.constraints.ExpCone(gr, np.ones((n, 1)) @ k, k + returns @ w)
                ]
                objective = cv.Maximize(ret * 1000)
            elif kelly == "approx":
                constraints += [risk <= 1]
                constraints += devconstraints
                objective = cv.Maximize(ret)
            elif kelly == False:
                constraints += [mu @ w - rf0 * k == 1]
                objective = cv.Minimize(risk * 1000)
        elif obj == "MinRisk":
            objective = cv.Minimize(risk * 1000)
        elif obj == "Utility":
            objective = cv.Maximize(ret - l * risk)
        elif obj == "MaxRet":
            objective = cv.Maximize(ret * 1000)

        try:
            prob = cv.Problem(objective, constraints)
            for solver in self.solvers:
                try:
                    if len(self.sol_params) == 0:
                        prob.solve(solver=solver)
                    else:
                        prob.solve(solver=solver, **self.sol_params[solver])
                except:
                    pass
                if w.value is not None:
                    break

            if obj == "Sharpe":
                weights = np.array(w.value / k.value, ndmin=2).T
            else:
                weights = np.array(w.value, ndmin=2).T

            if self.sht == False:
                weights = np.abs(weights) / np.sum(np.abs(weights)) * self.budget

            for j in self.assetslist:
                portafolio[j].append(weights[0, self.assetslist.index(j)])

        except:
            pass

        try:
            self.owa_optimal = pd.DataFrame(
                portafolio, index=["weights"], dtype=np.float64
            ).T
        except:
            self.owa_optimal = None
            print("The problem doesn't have a solution with actual input parameters")

        return self.owa_optimal

    def frontier_limits(self, model="Classic", rm="MV", kelly=False, rf=0, hist=True):
        r"""
        Method that calculates the minimum risk and maximum return portfolios
        available with current assets and constraints.

        Parameters
        ----------
        model : str, optional
            Methodology used to estimate input parameters.
            The default is 'Classic'.
        rm : str, optional
            The risk measure used to optimze the portfolio.
            The default is 'MV'. Posible values are:

            - 'MV': Standard Deviation.
            - 'MAD': Mean Absolute Deviation.
            - 'GMD': Gini Mean Difference.
            - 'MSV': Semi Standard Deviation.
            - 'FLPM': First Lower Partial Moment (Omega Ratio).
            - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
            - 'CVaR': Conditional Value at Risk.
            - 'TG': Tail Gini.
            - 'EVaR': Entropic Value at Risk.
            - 'WR': Worst Realization (Minimax).
            - 'RG': Range of returns.
            - 'CVRG': CVaR range of returns.
            - 'TGRG': Tail Gini range of returns.
            - 'MDD': Maximum Drawdown of uncompounded cumulative returns (Calmar Ratio).
            - 'ADD': Average Drawdown of uncompounded cumulative returns.
            - 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
            - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
            - 'UCI': Ulcer Index of uncompounded cumulative returns.

        kelly : str, optional
            Method used to calculate mean return. Posible values are False for
            arithmetic mean return, "approx" for approximate mean logarithmic
            return using first and second moment and "exact" for mean logarithmic
            return. The default is False.
        rf : scalar, optional
            Risk free rate. The default is 0.
        hist : bool, optional
            Indicate what kind of returns are used to calculate risk measures
            that depends on scenarios (All except 'MV' risk measure).
            If model = 'BL', True means historical covariance and returns and
            False Black Litterman covariance and historical returns.
            If model = 'FM', True means historical covariance and returns and
            False Risk Factor model for covariance and returns.
            If model = 'BL_FM', True means historical covariance and returns,
            False Black Litteram with Risk Factor model for covariance and
            Risk Factor model for returns, and '2' Risk Factor model for
            covariance and returns. The default is True.

        Returns
        -------
        limits : DataFrame
            A dataframe that containts the weights of the portfolios.

        Notes
        -----
        This method is preferable (faster) to use instead of efficient_frontier
        method to know the range of expected return and expected risk.

        """

        w_min = self.optimization(
            model=model, rm=rm, obj="MinRisk", kelly=kelly, rf=rf, l=0, hist=hist
        )
        w_max = self.optimization(
            model=model, rm=rm, obj="MaxRet", kelly=kelly, rf=rf, l=0, hist=hist
        )

        if w_min is not None and w_max is not None:
            self.limits = pd.concat([w_min, w_max], axis=1)
            self.limits.columns = ["w_min", "w_max"]
            return self.limits
        else:
            raise NameError("The limits of the frontier can't be found")

    def efficient_frontier(
        self, model="Classic", rm="MV", kelly=False, points=20, rf=0, hist=True
    ):
        r"""
        Method that calculates several portfolios in the efficient frontier
        of the selected risk measure, available with current assets and
        constraints.

        Parameters
        ----------
        model : str, optional
            Methodology used to estimate input parameters.
            The default is 'Classic'.
        rm : str, optional
            The risk measure used to optimze the portfolio.
            The default is 'MV'. Posible values are:

            - 'MV': Standard Deviation.
            - 'MAD': Mean Absolute Deviation.
            - 'GMD': Gini Mean Difference.
            - 'MSV': Semi Standard Deviation.
            - 'FLPM': First Lower Partial Moment (Omega Ratio).
            - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
            - 'CVaR': Conditional Value at Risk.
            - 'TG': Tail Gini.
            - 'EVaR': Entropic Value at Risk.
            - 'WR': Worst Realization (Minimax).
            - 'RG': Range of returns.
            - 'CVRG': CVaR range of returns.
            - 'TGRG': Tail Gini range of returns.
            - 'MDD': Maximum Drawdown of uncompounded cumulative returns (Calmar Ratio).
            - 'ADD': Average Drawdown of uncompounded cumulative returns.
            - 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
            - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
            - 'UCI': Ulcer Index of uncompounded cumulative returns.

        kelly : str, optional
            Method used to calculate mean return. Posible values are False for
            arithmetic mean return, "approx" for approximate mean logarithmic
            return using first and second moment and "exact" for mean logarithmic
            return. The default is False.
        points : scalar, optional
            Number of point calculated from the efficient frontier.
            The default is 50.
        rf : scalar, optional
            Risk free rate. The default is 0.
        hist : bool, optional
            Indicate what kind of returns are used to calculate risk measures
            that depends on scenarios (All except 'MV' risk measure).
            If model = 'BL', True means historical covariance and returns and
            False Black Litterman covariance and historical returns.
            If model = 'FM', True means historical covariance and returns and
            False Risk Factor model for covariance and returns.
            If model = 'BL_FM', True means historical covariance and returns,
            False Black Litteram with Risk Factor model for covariance and
            Risk Factor model for returns, and '2' Risk Factor model for
            covariance and returns. The default is True.

        Returns
        -------
        frontier : DataFrame
            A dataframe that containts the weights of the portfolios.

        Notes
        -----
        It's recommendable that don't use this method when there are too many
        assets (more than 100) and you are using a scenario based risk measure
        (all except standard deviation). It's preferable to use frontier_limits
        method (faster) to know the range of expected return and expected risk.
        """

        mu = None
        sigma = None
        returns = None
        if model == "Classic":
            mu = np.array(self.mu, ndmin=2)
            sigma = np.array(self.cov, ndmin=2)
            returns = np.array(self.returns, ndmin=2)
            nav = np.array(self.nav, ndmin=2)
        elif model == "FM":
            mu = np.array(self.mu_fm, ndmin=2)
            if hist == False:
                sigma = np.array(self.cov_fm, ndmin=2)
                returns = np.array(self.returns_fm, ndmin=2)
                nav = np.array(self.nav_fm, ndmin=2)
            elif hist == True:
                sigma = np.array(self.cov, ndmin=2)
                returns = np.array(self.returns, ndmin=2)
                nav = np.array(self.nav, ndmin=2)
        elif model == "BL":
            mu = np.array(self.mu_bl, ndmin=2)
            if hist == False:
                sigma = np.array(self.cov_bl, ndmin=2)
            elif hist == True:
                sigma = np.array(self.cov, ndmin=2)
            returns = np.array(self.returns, ndmin=2)
            nav = np.array(self.nav, ndmin=2)
        elif model == "BL_FM":
            mu = np.array(self.mu_bl_fm, ndmin=2)
            if hist == False:
                sigma = np.array(self.cov_bl_fm, ndmin=2)
                returns = np.array(self.returns_fm, ndmin=2)
                nav = np.array(self.nav_fm, ndmin=2)
            elif hist == True:
                sigma = np.array(self.cov, ndmin=2)
                returns = np.array(self.returns, ndmin=2)
                nav = np.array(self.nav, ndmin=2)
            elif hist == 2:
                sigma = np.array(self.cov_fm, ndmin=2)
                returns = np.array(self.returns_fm, ndmin=2)
                nav = np.array(self.nav_fm, ndmin=2)

        alpha = self.alpha
        a_sim = self.a_sim

        if self.beta is None:
            beta = alpha
        else:
            beta = self.beta

        if self.b_sim is None:
            b_sim = a_sim
        else:
            b_sim = self.b_sim

        limits = self.frontier_limits(model=model, rm=rm, kelly=kelly, rf=rf, hist=hist)

        w_min = np.array(limits.iloc[:, 0], ndmin=2).T
        w_max = np.array(limits.iloc[:, 1], ndmin=2).T

        ret_min = (mu @ w_min).item()
        ret_max = (mu @ w_max).item()

        if rm == "MV":
            risk_min = np.sqrt(w_min.T @ sigma @ w_min).item()
            risk_max = np.sqrt(w_max.T @ sigma @ w_max).item()
        elif rm == "MAD":
            risk_min = rk.MAD(returns @ w_min)
            risk_max = rk.MAD(returns @ w_max)
        elif rm == "MSV":
            risk_min = rk.SemiDeviation(returns @ w_min)
            risk_max = rk.SemiDeviation(returns @ w_max)
        elif rm == "CVaR":
            risk_min = rk.CVaR_Hist(returns @ w_min, alpha)
            risk_max = rk.CVaR_Hist(returns @ w_max, alpha)
        elif rm == "WR":
            risk_min = rk.WR(returns @ w_min)
            risk_max = rk.WR(returns @ w_max)
        elif rm == "FLPM":
            risk_min = rk.LPM(returns @ w_min, rf, 1)
            risk_max = rk.LPM(returns @ w_max, rf, 1)
        elif rm == "SLPM":
            risk_min = rk.LPM(returns @ w_min, rf, 2)
            risk_max = rk.LPM(returns @ w_max, rf, 2)
        elif rm == "MDD":
            risk_min = rk.MDD_Abs(returns @ w_min)
            risk_max = rk.MDD_Abs(returns @ w_max)
        elif rm == "ADD":
            risk_min = rk.ADD_Abs(returns @ w_min)
            risk_max = rk.ADD_Abs(returns @ w_max)
        elif rm == "CDaR":
            risk_min = rk.CDaR_Abs(returns @ w_min, alpha)
            risk_max = rk.CDaR_Abs(returns @ w_max, alpha)
        elif rm == "UCI":
            risk_min = rk.UCI_Abs(returns @ w_min)
            risk_max = rk.UCI_Abs(returns @ w_max)
        elif rm == "EVaR":
            risk_min = rk.EVaR_Hist(returns @ w_min, alpha)[0]
            risk_max = rk.EVaR_Hist(returns @ w_max, alpha)[0]
        elif rm == "EDaR":
            risk_min = rk.EDaR_Abs(returns @ w_min, alpha)[0]
            risk_max = rk.EDaR_Abs(returns @ w_max, alpha)[0]
        elif rm == "GMD":
            risk_min = rk.GMD(returns @ w_min)
            risk_max = rk.GMD(returns @ w_max)
        elif rm == "TG":
            risk_min = rk.TG(returns @ w_min, alpha, a_sim)
            risk_max = rk.TG(returns @ w_max, alpha, a_sim)
        elif rm == "RG":
            risk_min = rk.RG(returns @ w_min)
            risk_max = rk.RG(returns @ w_max)
        elif rm == "CVRG":
            risk_min = rk.CVRG(returns @ w_min, alpha, beta)
            risk_max = rk.CVRG(returns @ w_max, alpha, beta)
        elif rm == "TGRG":
            risk_min = rk.TGRG(returns @ w_min, alpha, a_sim, beta, b_sim)
            risk_max = rk.TGRG(returns @ w_max, alpha, a_sim, beta, b_sim)

        mus = np.linspace(ret_min, ret_max, points)

        risks = np.linspace(risk_min, risk_max, points)

        risk_lims = [
            "upperdev",
            "uppermad",
            "uppergmd",
            "uppersdev",
            "upperCVaR",
            "uppertg",
            "upperEVaR",
            "upperwr",
            "upperrg",
            "uppercvrg",
            "uppertgrg",
            "upperflpm",
            "upperslpm",
            "uppermdd",
            "upperadd",
            "upperCDaR",
            "upperEDaR",
            "upperuci",
        ]

        risk_names = [
            "MV",
            "MAD",
            "GMD",
            "MSV",
            "CVaR",
            "TG",
            "EVaR",
            "WR",
            "RG",
            "CVRG",
            "TGRG",
            "FLPM",
            "SLPM",
            "MDD",
            "ADD",
            "CDaR",
            "EDaR",
            "UCI",
        ]

        item = risk_names.index(rm)

        frontier = []
        n = 0
        for i in range(len(risks)):
            try:
                if n == 0:
                    w = self.optimization(
                        model=model,
                        rm=rm,
                        obj="MinRisk",
                        kelly=kelly,
                        rf=rf,
                        l=0,
                        hist=hist,
                    )
                else:
                    setattr(self, risk_lims[item], risks[i])
                    w = self.optimization(
                        model=model,
                        rm=rm,
                        obj="MaxRet",
                        kelly=kelly,
                        rf=rf,
                        l=0,
                        hist=hist,
                    )
                if w is not None:
                    n += 1
                    frontier.append(w)
            except:
                pass

        setattr(self, risk_lims[item], None)
        self.frontier = pd.concat(frontier, axis=1)
        self.frontier.columns = list(range(n))

        return self.frontier

    def reset_risk_constraints(self):
        r"""
        Reset all risk constraints.

        """
        cons = [
            "lowerret",
            "upperdev",
            "uppermad",
            "uppersdev",
            "upperCVaR",
            "upperEVaR",
            "upperwr",
            "upperflpm",
            "upperslpm",
            "uppermdd",
            "upperadd",
            "upperCDaR",
            "upperEDaR",
            "upperuci",
            "uppergmd",
            "uppertg",
            "upperrg",
            "uppercvrg",
            "uppertgrg",
        ]

        for i in cons:
            setattr(self, i, None)

    def reset_linear_constraints(self):
        r"""
        Reset all linear constraints.

        """

        self.ainequality = None
        self.binequality = None

    def reset_inputs(self):
        r"""
        Reset all inputs parameters of optimization models.

        """

        cons = [
            "mu",
            "cov",
            "mu_fm",
            "cov_fm",
            "mu_bl",
            "cov_bl",
            "mu_bl_fm",
            "cov_bl_fm",
            "returns_fm",
            "nav_fm",
            "cov_l",
            "cov_u",
            "cov_mu",
            "cov_sigma",
            "d_mu",
            "k_mu",
            "k_sigma",
        ]

        for i in cons:
            setattr(self, i, None)

    def reset_all(self):
        r"""
        Reset portfolio object to defatult values.

        """

        self.sht = False
        self.uppersht = 0.2
        self.upperlng = 1
        self.budget = 1
        self.nea = None
        self.card = None
        self._factors = None
        self.B = None
        self.alpha = 0.05
        self.kindbench = True
        self.benchindex = None
        self._benchweights = None
        self.allowTO = False
        self.turnover = 0.05
        self.allowTE = False
        self.TE = 0.05

        self.reset_risk_constraints()
        self.reset_linear_constraints()
        self.reset_inputs()
