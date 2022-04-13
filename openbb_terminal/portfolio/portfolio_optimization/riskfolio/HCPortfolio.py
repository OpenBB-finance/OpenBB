""""""  #
"""
Copyright (c) 2020-2022, Dany Cajas
All rights reserved.
This work is licensed under BSD 3-Clause "New" or "Revised" License.
License available at https://github.com/dcajasn/Riskfolio-Lib/blob/master/LICENSE.txt
"""

import numpy as np
import pandas as pd
import scipy.cluster.hierarchy as hr
from scipy.spatial.distance import squareform
import openbb_terminal.portfolio.portfolio_optimization.riskfolio.Portfolio as pf
import openbb_terminal.portfolio.portfolio_optimization.riskfolio.RiskFunctions as rk
import openbb_terminal.portfolio.portfolio_optimization.riskfolio.AuxFunctions as af
import openbb_terminal.portfolio.portfolio_optimization.riskfolio.ParamsEstimation as pe
import openbb_terminal.portfolio.portfolio_optimization.riskfolio.DBHT as db


class HCPortfolio(object):
    r"""
    Class that creates a portfolio object with all properties needed to
    calculate optimal portfolios.

    Parameters
    ----------
    returns : DataFrame, optional
        A dataframe that containts the returns of the assets.
        The default is None.
    alpha : float, optional
        Significance level of VaR, CVaR, EVaR, DaR, CDaR, EDaR and Tail Gini of losses.
        The default is 0.05.
    a_sim : float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default is 100.
    beta : float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
        The default is None.
    b_sim : float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
        The default is None.
    w_max : Series, optional
        Upper bound constraint for hierarchical risk parity weights :cite:`c-Pfitzinger`.
    w_min : Series, optional
        Lower bound constraint for hierarchical risk parity weights :cite:`c-Pfitzinger`.
    """

    def __init__(
        self,
        returns=None,
        alpha=0.05,
        a_sim=100,
        beta=None,
        b_sim=None,
        w_max=None,
        w_min=None,
        alpha_tail=0.05,
        bins_info=None,
    ):
        self._returns = returns
        self.alpha = alpha
        self.a_sim = a_sim
        self.beta = beta
        self.b_sim = b_sim
        self.alpha_tail = alpha_tail
        self.bins_info = bins_info
        self.asset_order = None
        self.clusters = None
        self.cov = None
        self.mu = None
        self.codep = None
        self.codep_sorted = None
        self.w_max = w_max
        self.w_min = w_min

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
    def assetslist(self):
        if self._returns is not None and isinstance(self._returns, pd.DataFrame):
            return self._returns.columns.tolist()

    # get naive-risk weights
    def _naive_risk(self, returns, cov, rm="MV", rf=0):
        assets = returns.columns.tolist()
        n = len(assets)

        if rm == "equal":
            weight = np.ones((n, 1)) * 1 / n
        else:
            inv_risk = np.zeros((n, 1))
            for i in assets:
                k = assets.index(i)
                w = np.zeros((n, 1))
                w[k, 0] = 1
                w = pd.DataFrame(w, columns=["weights"], index=assets)
                if rm == "vol":
                    risk = rk.Sharpe_Risk(
                        w,
                        cov=cov,
                        returns=returns,
                        rm="MV",
                        rf=rf,
                        alpha=self.alpha,
                        a_sim=self.a_sim,
                        beta=self.beta,
                        b_sim=self.b_sim,
                    )
                else:
                    risk = rk.Sharpe_Risk(
                        w,
                        cov=cov,
                        returns=returns,
                        rm=rm,
                        rf=rf,
                        alpha=self.alpha,
                        a_sim=self.a_sim,
                        beta=self.beta,
                        b_sim=self.b_sim,
                    )
                inv_risk[k, 0] = risk

            if rm == "MV":
                inv_risk = 1 / np.power(inv_risk, 2)
            else:
                inv_risk = 1 / inv_risk
            weight = inv_risk * (1 / np.sum(inv_risk))

        weight = weight.reshape(-1, 1)

        return weight

    # get optimal weights
    def _opt_w(self, returns, mu, cov, obj="MinRisk", rm="MV", rf=0, l=2):
        if returns.shape[1] == 1:
            weight = np.array([1]).reshape(-1, 1)
        else:
            if obj in {"MinRisk", "Utility", "Sharpe"}:
                port = pf.Portfolio(returns=returns)
                port.assets_stats(method_mu="hist", method_cov="hist", d=0.94)
                port.cov = cov
                if mu is not None:
                    port.mu = mu
                weight = port.optimization(
                    model="Classic", rm=rm, obj=obj, rf=rf, l=l, hist=True
                ).to_numpy()
            elif obj in {"ERC"}:
                port = pf.Portfolio(returns=returns)
                port.assets_stats(method_mu="hist", method_cov="hist", d=0.94)
                port.cov = cov
                weight = port.rp_optimization(
                    model="Classic", rm=rm, rf=rf, b=None, hist=True
                ).to_numpy()

        weight = weight.reshape(-1, 1)

        return weight

    # Create hierarchical clustering
    def _hierarchical_clustering(
        self,
        model="HRP",
        linkage="ward",
        codependence="pearson",
        max_k=10,
        leaf_order=True,
    ):

        # Calculating distance
        if codependence in {"pearson", "spearman", "custom_cov"}:
            dist = np.sqrt(np.clip((1 - self.codep) / 2, a_min=0.0, a_max=1.0))
        elif codependence in {"abs_pearson", "abs_spearman", "distance"}:
            dist = np.sqrt(np.clip((1 - self.codep), a_min=0.0, a_max=1.0))
        elif codependence in {"mutual_info"}:
            dist = af.var_info_matrix(self.returns, self.bins_info).astype(float)
        elif codependence in {"tail"}:
            dist = -np.log(self.codep).astype(float)

        # Hierarchcial clustering
        dist = dist.to_numpy()
        dist = pd.DataFrame(dist, columns=self.codep.columns, index=self.codep.index)
        if linkage == "DBHT":
            # different choices for D, S give different outputs!
            D = dist.to_numpy()  # dissimilatity matrix
            if codependence in {"pearson", "spearman", "custom_cov"}:
                codep = 1 - dist**2
                S = codep.to_numpy()  # similarity matrix
            else:
                S = self.codep.to_numpy()  # similarity matrix
            (_, _, _, _, _, clustering) = db.DBHTs(
                D, S, leaf_order=leaf_order
            )  # DBHT clustering
        else:
            p_dist = squareform(dist, checks=False)
            clustering = hr.linkage(p_dist, method=linkage, optimal_ordering=leaf_order)

        if model in {"HERC", "HERC2", "NCO"}:
            # optimal number of clusters
            k = af.two_diff_gap_stat(self.codep, dist, clustering, max_k)
        else:
            k = None

        return clustering, k

    # sort clustered items by distance
    def _seriation(self, clusters):
        return hr.leaves_list(clusters)

    # compute HRP weight allocation through recursive bisection
    def _recursive_bisection(self, sort_order, rm="MV", rf=0):

        if isinstance(self.w_max, pd.Series) and isinstance(self.w_min, pd.Series):
            if (self.w_max.all() >= self.w_min.all()).item():
                flag = True
            else:
                raise NameError("All upper bounds must be higher than lower bounds")
        else:
            flag = False

        weight = pd.Series(1, index=sort_order)  # set initial weights to 1
        items = [sort_order]

        while len(items) > 0:  # loop while weights is under 100%
            items = [
                i[j:k]
                for i in items
                for j, k in (
                    (0, len(i) // 2),
                    (len(i) // 2, len(i)),
                )  # get cluster indi
                if len(i) > 1
            ]

            # allocate weight to left and right cluster
            for i in range(0, len(items), 2):
                left_cluster = items[i]
                right_cluster = items[i + 1]

                # Left cluster
                left_cov = self.cov.iloc[left_cluster, left_cluster]
                left_returns = self.returns.iloc[:, left_cluster]
                left_weight = self._naive_risk(left_returns, left_cov, rm=rm, rf=rf)

                if rm == "vol":
                    left_risk = rk.Sharpe_Risk(
                        left_weight,
                        cov=left_cov,
                        returns=left_returns,
                        rm="MV",
                        rf=rf,
                        alpha=self.alpha,
                        a_sim=self.a_sim,
                        beta=self.beta,
                        b_sim=self.b_sim,
                    )
                else:
                    left_risk = rk.Sharpe_Risk(
                        left_weight,
                        cov=left_cov,
                        returns=left_returns,
                        rm=rm,
                        rf=rf,
                        alpha=self.alpha,
                        a_sim=self.a_sim,
                        beta=self.beta,
                        b_sim=self.b_sim,
                    )
                    if rm == "MV":
                        left_risk = np.power(left_risk, 2)

                # Right cluster
                right_cov = self.cov.iloc[right_cluster, right_cluster]
                right_returns = self.returns.iloc[:, right_cluster]
                right_weight = self._naive_risk(right_returns, right_cov, rm=rm, rf=rf)

                if rm == "vol":
                    right_risk = rk.Sharpe_Risk(
                        right_weight,
                        cov=right_cov,
                        returns=right_returns,
                        rm="MV",
                        rf=rf,
                        alpha=self.alpha,
                        a_sim=self.a_sim,
                        beta=self.beta,
                        b_sim=self.b_sim,
                    )
                else:
                    right_risk = rk.Sharpe_Risk(
                        right_weight,
                        cov=right_cov,
                        returns=right_returns,
                        rm=rm,
                        rf=rf,
                        alpha=self.alpha,
                        a_sim=self.a_sim,
                        beta=self.beta,
                        b_sim=self.b_sim,
                    )
                    if rm == "MV":
                        right_risk = np.power(right_risk, 2)

                # Allocate weight to clusters
                alpha_1 = 1 - left_risk / (left_risk + right_risk)

                # Weights constraints
                if flag:
                    a1 = np.sum(self.w_max[left_cluster]) / weight[left_cluster[0]]
                    a2 = np.max(
                        [
                            np.sum(self.w_min[left_cluster]) / weight[left_cluster[0]],
                            alpha_1,
                        ]
                    )
                    alpha_1 = np.min([a1, a2])
                    a1 = np.sum(self.w_max[right_cluster]) / weight[right_cluster[0]]
                    a2 = np.max(
                        [
                            np.sum(self.w_min[right_cluster])
                            / weight[right_cluster[0]],
                            1 - alpha_1,
                        ]
                    )
                    alpha_1 = 1 - np.min([a1, a2])

                weight[left_cluster] *= alpha_1  # weight 1
                weight[right_cluster] *= 1 - alpha_1  # weight 2

        weight.index = self.asset_order

        return weight

    # compute HRP weight allocation through cluster-based bisection
    def _hierarchical_recursive_bisection(
        self, Z, rm="MV", rf=0, linkage="ward", model="HERC"
    ):

        # Transform linkage to tree and reverse order
        root, nodes = hr.to_tree(Z, rd=True)
        nodes = np.array(nodes)
        nodes_1 = np.array([i.dist for i in nodes])
        idx = np.argsort(nodes_1)
        nodes = nodes[idx][::-1].tolist()

        weight = pd.Series(1, index=self.cov.index)  # Set initial weights to 1

        clustering_inds = hr.fcluster(Z, self.k, criterion="maxclust")
        clusters = {
            i: [] for i in range(min(clustering_inds), max(clustering_inds) + 1)
        }
        for i, v in enumerate(clustering_inds):
            clusters[v].append(i)

        # Loop through k clusters
        for i in nodes[: self.k - 1]:
            if i.is_leaf() == False:  # skip leaf-nodes
                left = i.get_left().pre_order()  # lambda i: i.id) # get left cluster
                right = i.get_right().pre_order()  # lambda i: i.id) # get right cluster
                left_set = set(left)
                right_set = set(right)
                left_risk = 0
                right_risk = 0

                # Allocate weight to clusters
                if rm == "equal":
                    alpha_1 = 0.5

                else:
                    for j in clusters.keys():
                        if set(clusters[j]).issubset(left_set):
                            # Left cluster
                            left_cov = self.cov.iloc[clusters[j], clusters[j]]
                            left_returns = self.returns.iloc[:, clusters[j]]
                            left_weight = self._naive_risk(
                                left_returns, left_cov, rm=rm, rf=rf
                            )

                            if rm == "vol":
                                left_risk_ = rk.Sharpe_Risk(
                                    left_weight,
                                    cov=left_cov,
                                    returns=left_returns,
                                    rm="MV",
                                    rf=rf,
                                    alpha=self.alpha,
                                    a_sim=self.a_sim,
                                    beta=self.beta,
                                    b_sim=self.b_sim,
                                )
                            else:
                                left_risk_ = rk.Sharpe_Risk(
                                    left_weight,
                                    cov=left_cov,
                                    returns=left_returns,
                                    rm=rm,
                                    rf=rf,
                                    alpha=self.alpha,
                                    a_sim=self.a_sim,
                                    beta=self.beta,
                                    b_sim=self.b_sim,
                                )
                                if rm == "MV":
                                    left_risk_ = np.power(left_risk_, 2)

                            left_risk += left_risk_

                        elif set(clusters[j]).issubset(right_set):
                            # Right cluster
                            right_cov = self.cov.iloc[clusters[j], clusters[j]]
                            right_returns = self.returns.iloc[:, clusters[j]]
                            right_weight = self._naive_risk(
                                right_returns, right_cov, rm=rm, rf=rf
                            )

                            if rm == "vol":
                                right_risk_ = rk.Sharpe_Risk(
                                    right_weight,
                                    cov=right_cov,
                                    returns=right_returns,
                                    rm="MV",
                                    rf=rf,
                                    alpha=self.alpha,
                                    a_sim=self.a_sim,
                                    beta=self.beta,
                                    b_sim=self.b_sim,
                                )
                            else:
                                right_risk_ = rk.Sharpe_Risk(
                                    right_weight,
                                    cov=right_cov,
                                    returns=right_returns,
                                    rm=rm,
                                    rf=rf,
                                    alpha=self.alpha,
                                    a_sim=self.a_sim,
                                    beta=self.beta,
                                    b_sim=self.b_sim,
                                )
                                if rm == "MV":
                                    right_risk_ = np.power(right_risk_, 2)

                            right_risk += right_risk_

                    alpha_1 = 1 - left_risk / (left_risk + right_risk)

                weight[left] *= alpha_1  # weight 1
                weight[right] *= 1 - alpha_1  # weight 2

        # Get constituents of k clusters
        clustered_assets = pd.Series(
            hr.cut_tree(Z, n_clusters=self.k).flatten(), index=self.cov.index
        )
        # Multiply within-cluster weight with inter-cluster weight
        for i in range(self.k):
            cluster = clustered_assets.loc[clustered_assets == i]
            cluster_cov = self.cov.loc[cluster.index, cluster.index]
            cluster_returns = self.returns.loc[:, cluster.index]
            if model == "HERC":
                cluster_weights = pd.Series(
                    self._naive_risk(
                        cluster_returns, cluster_cov, rm=rm, rf=rf
                    ).flatten(),
                    index=cluster_cov.index,
                )
            elif model == "HERC2":
                cluster_weights = pd.Series(
                    self._naive_risk(
                        cluster_returns, cluster_cov, rm="equal", rf=rf
                    ).flatten(),
                    index=cluster_cov.index,
                )
            weight.loc[cluster_weights.index] *= cluster_weights

        return weight

    # compute intra-cluster weights
    def _intra_weights(self, Z, obj="MinRisk", rm="MV", rf=0, l=2):
        # Get constituents of k clusters
        clustered_assets = pd.Series(
            hr.cut_tree(Z, n_clusters=self.k).flatten(), index=self.cov.index
        )

        # get covariance matrices for each cluster
        intra_weights = pd.DataFrame(index=clustered_assets.index)
        for i in range(self.k):
            cluster = clustered_assets.loc[clustered_assets == i]
            if self.mu is not None:
                cluster_mu = self.mu.loc[:, cluster.index]
            else:
                cluster_mu = None
            cluster_cov = self.cov.loc[cluster.index, cluster.index]
            cluster_returns = self.returns.loc[:, cluster.index]
            weights = pd.Series(
                self._opt_w(
                    cluster_returns, cluster_mu, cluster_cov, obj=obj, rm=rm, rf=rf, l=l
                ).flatten(),
                index=cluster_cov.index,
            )
            intra_weights[i] = weights

        intra_weights = intra_weights.fillna(0)
        return intra_weights

    def _inter_weights(self, intra_weights, obj="MinRisk", rm="MV", rf=0, l=2):
        # inter-cluster mean vector
        if self.mu is not None:
            tot_mu = self.mu @ intra_weights
        else:
            tot_mu = None
        # inter-cluster covariance matrix
        tot_cov = intra_weights.T.dot(np.dot(self.cov, intra_weights))
        # inter-cluster returns matrix
        tot_ret = self.returns @ intra_weights

        # inter-cluster weights
        inter_weights = pd.Series(
            self._opt_w(tot_ret, tot_mu, tot_cov, obj=obj, rm=rm, rf=rf, l=l).flatten(),
            index=intra_weights.columns,
        )
        # determine the weight on each cluster by multiplying the intra-cluster weight with the inter-cluster weight
        weights = intra_weights.mul(inter_weights, axis=1).sum(axis=1).sort_index()
        return weights

    # Allocate weights
    def optimization(
        self,
        model="HRP",
        codependence="pearson",
        covariance="hist",
        obj="MinRisk",
        rm="MV",
        rf=0,
        l=2,
        custom_cov=None,
        custom_mu=None,
        linkage="single",
        k=None,
        max_k=10,
        bins_info="KN",
        alpha_tail=0.05,
        leaf_order=True,
        d=0.94,
        **kwargs,
    ):
        r"""
        This method calculates the optimal portfolio according to the
        optimization model selected by the user.

        Parameters
        ----------
        model : str, can be {'HRP', 'HERC' or 'HERC2'}
            The hierarchical cluster portfolio model used for optimize the
            portfolio. The default is 'HRP'. Posible values are:

            - 'HRP': Hierarchical Risk Parity.
            - 'HERC': Hierarchical Equal Risk Contribution.
            - 'HERC2': HERC but splitting weights equally within clusters.
            - 'NCO': Nested Clustered Optimization.

        codependence : str, optional
            The codependence or similarity matrix used to build the distance
            metric and clusters. The default is 'pearson'. Posible values are:

            - 'pearson': pearson correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{0.5(1-\rho^{pearson}_{i,j})}`.
            - 'spearman': spearman correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{0.5(1-\rho^{spearman}_{i,j})}`.
            - 'abs_pearson': absolute value pearson correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{(1-|\rho^{pearson}_{i,j}|)}`.
            - 'abs_spearman': absolute value spearman correlation matrix. Distance formula: :math:`D_{i,j} = \sqrt{(1-|\rho^{spearman}_{i,j}|)}`.
            - 'distance': distance correlation matrix. Distance formula :math:`D_{i,j} = \sqrt{(1-\rho^{distance}_{i,j})}`.
            - 'mutual_info': mutual information matrix. Distance used is variation information matrix.
            - 'tail': lower tail dependence index matrix. Dissimilarity formula :math:`D_{i,j} = -\log{\lambda_{i,j}}`.
            - 'custom_cov': use custom correlation matrix based on the custom_cov parameter. Distance formula: :math:`D_{i,j} = \sqrt{0.5(1-\rho^{pearson}_{i,j})}`.

        covariance : str, optional
            The method used to estimate the covariance matrix:
            The default is 'hist'. Posible values are:

            - 'hist': use historical estimates.
            - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
            - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`_.
            - 'ledoit': use the Ledoit and Wolf Shrinkage method.
            - 'oas': use the Oracle Approximation Shrinkage method.
            - 'shrunk': use the basic Shrunk Covariance method.
            - 'gl': use the basic Graphical Lasso Covariance method.
            - 'jlogo': use the j-LoGo Covariance method. For more information see: :cite:`c-jLogo`.
            - 'fixed': denoise using fixed method. For more information see chapter 2 of :cite:`c-MLforAM`.
            - 'spectral': denoise using spectral method. For more information see chapter 2 of :cite:`c-MLforAM`.
            - 'shrink': denoise using shrink method. For more information see chapter 2 of :cite:`c-MLforAM`.
            - 'custom_cov': use custom covariance matrix.

        obj : str can be {'MinRisk', 'Utility', 'Sharpe' or 'ERC'}.
            Objective function used by the NCO model.
            The default is 'MinRisk'. Posible values are:

            - 'MinRisk': Minimize the selected risk measure.
            - 'Utility': Maximize the Utility function :math:`\mu w - l \phi_{i}(w)`.
            - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
            - 'ERC': Equally risk contribution portfolio of the selected risk measure.

        rm : str, optional
            The risk measure used to optimze the portfolio. If model is 'NCO',
            the risk measures available depends on the objective functon.
            The default is 'MV'. Posible values are:

            - 'equal': Equally weighted.
            - 'vol': Standard Deviation.
            - 'MV': Variance.
            - 'MAD': Mean Absolute Deviation.
            - 'MSV': Semi Standard Deviation.
            - 'FLPM': First Lower Partial Moment (Omega Ratio).
            - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
            - 'VaR': Value at Risk.
            - 'CVaR': Conditional Value at Risk.
            - 'TG': Tail Gini.
            - 'EVaR': Entropic Value at Risk.
            - 'WR': Worst Realization (Minimax).
            - 'RG': Range of returns.
            - 'CVRG': CVaR range of returns.
            - 'TGRG': Tail Gini range of returns.
            - 'MDD': Maximum Drawdown of uncompounded cumulative returns (Calmar Ratio).
            - 'ADD': Average Drawdown of uncompounded cumulative returns.
            - 'DaR': Drawdown at Risk of uncompounded cumulative returns.
            - 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
            - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
            - 'UCI': Ulcer Index of uncompounded cumulative returns.
            - 'MDD_Rel': Maximum Drawdown of compounded cumulative returns (Calmar Ratio).
            - 'ADD_Rel': Average Drawdown of compounded cumulative returns.
            - 'DaR_Rel': Drawdown at Risk of compounded cumulative returns.
            - 'CDaR_Rel': Conditional Drawdown at Risk of compounded cumulative returns.
            - 'EDaR_Rel': Entropic Drawdown at Risk of compounded cumulative returns.
            - 'UCI_Rel': Ulcer Index of compounded cumulative returns.

        rf : float, optional
            Risk free rate, must be in the same period of assets returns.
            The default is 0.
        l : scalar, optional
            Risk aversion factor of the 'Utility' objective function.
            The default is 2.
        custom_cov : DataFrame or None, optional
            Custom covariance matrix, used when codependence or covariance
            parameters have value 'custom_cov'. The default is None.
        custom_mu : DataFrame or None, optional
            Custom mean vector when NCO objective is 'Utility' or 'Sharpe'.
            The default is None.
        linkage : string, optional
            Linkage method of hierarchical clustering. For more information see `linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html>`_.
            The default is 'single'. Posible values are:

            - 'single'.
            - 'complete'.
            - 'average'.
            - 'weighted'.
            - 'centroid'.
            - 'median'.
            - 'ward'.
            - 'DBHT': Direct Bubble Hierarchical Tree.

        k : int, optional
            Number of clusters. This value is took instead of the optimal number
            of clusters calculated with the two difference gap statistic.
            The default is None.
        max_k : int, optional
            Max number of clusters used by the two difference gap statistic
            to find the optimal number of clusters. The default is 10.
        bins_info: int or str
            Number of bins used to calculate variation of information. The default
            value is 'KN'. Posible values are:

            - 'KN': Knuth's choice method. See more in `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`_.
            - 'FD': Freedman–Diaconis' choice method. See more in `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`_.
            - 'SC': Scotts' choice method. See more in `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`_.
            - 'HGR': Hacine-Gharbi and Ravier' choice method.
            - int: integer value choice by user.

        alpha_tail : float, optional
            Significance level for lower tail dependence index. The default is 0.05.
        leaf_order : bool, optional
            Indicates if the cluster are ordered so that the distance between
            successive leaves is minimal. The default is True.
        d : scalar
            The smoothing factor of ewma methods.
            The default is 0.94.
        **kwargs:
            Other variables related to covariance estimation. See
            `Scikit Learn <https://scikit-learn.org/stable/modules/covariance.html>`_
            and chapter 2 of :cite:`d-MLforAM` for more details.

        Returns
        -------
        w : DataFrame
            The weights of optimal portfolio.

        """

        # Covariance matrix
        if covariance == "custom_cov":
            self.cov = custom_cov.copy()
        else:
            self.cov = pe.covar_matrix(
                self.returns, method=covariance, d=0.94, **kwargs
            )

        # Custom mean vector
        if custom_mu is not None:
            if isinstance(custom_mu, pd.Series) == True:
                self.mu = custom_mu.to_frame().T
            elif isinstance(custom_mu, pd.DataFrame) == True:
                if custom_mu.shape[0] > 1 and custom_mu.shape[1] == 1:
                    self.mu = custom_mu.T
                elif custom_mu.shape[0] == 1 and custom_mu.shape[1] > 1:
                    self.mu = custom_mu
                else:
                    raise NameError("custom_mu must be a column DataFrame")
            else:
                raise NameError("custom_mu must be a column DataFrame or Series")

        self.alpha_tail = alpha_tail
        self.bins_info = bins_info

        # Codependence matrix
        if codependence in {"pearson", "spearman"}:
            self.codep = self.returns.corr(method=codependence).astype(float)
        elif codependence in {"abs_pearson", "abs_spearman"}:
            self.codep = np.abs(self.returns.corr(method=codependence[4:])).astype(
                float
            )
        elif codependence in {"distance"}:
            self.codep = af.dcorr_matrix(self.returns).astype(float)
        elif codependence in {"mutual_info"}:
            self.codep = af.mutual_info_matrix(self.returns, self.bins_info).astype(
                float
            )
        elif codependence in {"tail"}:
            self.codep = af.ltdi_matrix(self.returns, alpha=self.alpha_tail).astype(
                float
            )
        elif codependence in {"custom_cov"}:
            self.codep = af.cov2corr(custom_cov).astype(float)

        # Step-1: Tree clustering
        self.clusters, self.k = self._hierarchical_clustering(
            model, linkage, codependence, max_k, leaf_order=leaf_order
        )
        if k is not None:
            self.k = int(k)

        # Step-2: Seriation (Quasi-Diagnalization)
        self.sort_order = self._seriation(self.clusters)
        asset_order = self.assetslist
        asset_order[:] = [self.assetslist[i] for i in self.sort_order]
        self.asset_order = asset_order.copy()
        self.codep_sorted = self.codep.reindex(
            index=self.asset_order, columns=self.asset_order
        )

        if isinstance(self.w_max, pd.Series) and isinstance(self.w_min, pd.Series):
            self.w_max = self.w_max.reindex(index=self.asset_order)
            self.w_max.index = self.sort_order
            self.w_min = self.w_min.reindex(index=self.asset_order)
            self.w_min.index = self.sort_order

        # Step-3: Recursive bisection
        if model == "HRP":
            # Recursive bisection
            weights = self._recursive_bisection(self.sort_order, rm=rm, rf=rf)
        elif model in ["HERC", "HERC2"]:
            # Cluster-based Recursive bisection
            weights = self._hierarchical_recursive_bisection(
                self.clusters, rm=rm, rf=rf, linkage=linkage, model=model
            )
        elif model == "NCO":
            # Step-3.1: Determine intra-cluster weights
            intra_weights = self._intra_weights(
                self.clusters, obj=obj, rm=rm, rf=rf, l=l
            )

            # Step-3.2: Determine inter-cluster weights and multiply with 􏰁→ intra-cluster weights
            weights = self._inter_weights(intra_weights, obj=obj, rm=rm, rf=rf, l=l)

        if isinstance(self.w_max, pd.Series) and isinstance(self.w_min, pd.Series):
            self.w_max = self.w_max.sort_index()
            self.w_max.index = self.assetslist
            self.w_min = self.w_min.sort_index()
            self.w_max.index = self.assetslist

        weights = weights.loc[self.assetslist].to_frame()
        weights.columns = ["weights"]

        return weights
