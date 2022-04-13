""""""  #
"""
Copyright (c) 2020-2022, Dany Cajas
All rights reserved.
This work is licensed under BSD 3-Clause "New" or "Revised" License.
License available at https://github.com/dcajasn/Riskfolio-Lib/blob/master/LICENSE.txt
"""

import numpy as np


def owa_gmd(T):
    r"""
    Calculate the OWA weights to calculate the Gini mean difference (GMD)
    of a returns series.

    Parameters
    ----------
    T : int
        Number of observations of the returns series.

    Returns
    -------
    value : 1d-array
        An OWA weights vector of size Tx1.
    """

    w_ = []
    for i in range(1, T + 1):
        w_.append(2 * i - 1 - T)
    w_ = 2 * np.array(w_) / (T * (T - 1))
    w_ = w_.reshape(-1, 1)

    return w_


def owa_cvar(T, alpha=0.05):
    r"""
    Calculate the OWA weights to calculate the Conditional Value at Risk (CVaR)
    of a returns series.

    Parameters
    ----------
    T : int
        Number of observations of the returns series.
    alpha : float, optional
        Significance level of CVaR. The default is 0.05.

    Returns
    -------
    value : 1d-array
        An OWA weights vector of size Tx1.
    """

    k = int(np.ceil(T * alpha)) - 1
    w_ = np.zeros((T, 1))
    w_[:k, :] = -1 / (T * alpha)
    w_[k, :] = -1 - np.sum(w_[:k, :])

    return w_


def owa_wcvar(T, alphas, weights):
    r"""
    Calculate the OWA weights to calculate the Weighted Conditional Value at
    Risk (WCVaR) of a returns series.

    Parameters
    ----------
    T : int
        Number of observations of the returns series.
    alphas : list
        List of significance levels of each CVaR model.
    weights : list
        List of weights of each CVaR model.

    Returns
    -------
    value : 1d-array
        An OWA weights vector of size Tx1.
    """

    w_ = 0
    for i, j in zip(alphas, weights):
        w_ += owa_cvar(T, i) * j

    return w_


def owa_tg(T, alpha=0.05, a_sim=100):
    r"""
    Calculate the OWA weights to calculate the Tail Gini of a returns series.

    Parameters
    ----------
    T : int
        Number of observations of the returns series.
    alpha : float, optional
        Significance level of TaiL Gini. The default is 0.05.
    a_sim : float, optional
        Number of CVaRs used to approximate the Tail Gini. The default is 100.

    Returns
    -------
    value : 1d-array
        A OWA weights vector of size Tx1.
    """

    alphas = np.linspace(alpha, 0.0001, a_sim)[::-1]
    w_ = [(alphas[1] - 0) * alphas[0] / alphas[-1] ** 2]
    for i in range(1, len(alphas) - 1):
        w_.append((alphas[i + 1] - alphas[i - 1]) * alphas[i] / alphas[-1] ** 2)
    w_.append((alphas[-1] - alphas[-2]) / alphas[-1])
    w_ = owa_wcvar(T, alphas, w_)

    return w_


def owa_wr(T):
    r"""
    Calculate the OWA weights to calculate the Worst realization (minimum) of a returns series.

    Parameters
    ----------
    T : int
        Number of observations of the returns series.

    Returns
    -------
    value : 1d-array
        A OWA weights vector of size Tx1.
    """

    w_ = np.zeros((T, 1))
    w_[0, :] = -1

    return w_


def owa_rg(T):
    r"""
    Calculate the OWA weights to calculate the range of a returns series.

    Parameters
    ----------
    T : int
        Number of observations of the returns series.

    Returns
    -------
    value : 1d-array
        A OWA weights vector of size Tx1.
    """

    w_ = np.zeros((T, 1))
    w_[0, :] = -1
    w_[-1, :] = 1

    return w_


def owa_cvrg(T, alpha=0.05, beta=None):
    r"""
    Calculate the OWA weights to calculate the CVaR range of a returns series.

    Parameters
    ----------
    T : int
        Number of observations of the returns series.
    alpha : float, optional
        Significance level of CVaR of losses. The default is 0.05.
    beta : float, optional
        Significance level of CVaR of gains. If None it duplicates alpha.
        The default is None.

    Returns
    -------
    value : 1d-array
        A OWA weights vector of size Tx1.
    """

    if beta is None:
        beta = alpha

    w_ = owa_cvar(T, alpha) - owa_cvar(T, beta)[::-1]

    return w_


def owa_wcvrg(T, alphas, weights_a, betas=None, weights_b=None):
    r"""
    Calculate the OWA weights to calculate the WCVaR range of a returns series.

    Parameters
    ----------
    T : int
        Number of observations of the returns series.
    alphas : list
        List of significance levels of each CVaR of losses model.
    weights_a : list
        List of weights of each CVaR of losses model.
    betas : list, optional
        List of significance levels of each CVaR of gains model. If None it duplicates alpha.
        The default is None.
    weights_b : list, optional
        List of weights of each CVaR of gains model. If None it duplicates weights_a.
        The default is None.

    Returns
    -------
    value : 1d-array
        A OWA weights vector of size Tx1.
    """

    if betas is None or weights_b is None:
        betas = alphas
        weights_b = weights_a

    w_ = owa_wcvar(T, alphas, weights_a) - owa_wcvar(T, betas, weights_b)[::-1]

    return w_


def owa_tgrg(T, alpha=0.05, a_sim=100, beta=None, b_sim=None):
    r"""
    Calculate the OWA weights to calculate the Tail Gini range of a returns
    series.

    Parameters
    ----------
    T : int
        Number of observations of the returns series.
    alpha : float, optional
        Significance level of Tail Gini of losses. The default is 0.05.
    a_sim : float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default is 100.
    beta : float, optional
        Significance level of Tail Gini of gains. If None it duplicates alpha value.
        The default is None.
    b_sim : float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
        The default is None.

    Returns
    -------
    value : 1d-array
        A OWA weights vector of size Tx1.
    """

    if beta is None:
        beta = alpha
    if b_sim is None:
        b_sim = a_sim

    w_ = owa_tg(T, alpha, a_sim) - owa_tg(T, beta, b_sim)[::-1]

    return w_
