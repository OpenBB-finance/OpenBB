"""OpenBB 平台计量经济学扩展的实用函数。"""

import warnings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import Series


def get_engle_granger_two_step_cointegration_test(
    dependent_series: "Series", independent_series: "Series"
) -> tuple[float, float, float, "Series", float, float]:
    """估计序列 y 和 x 的长期和短期协整关系。
    
    然后对协整应用两步恩格尔-格兰杰 (Engle & Granger) 检验。

    使用两步过程首先估计长期关系的系数
        y_t = c + gamma * x_t + z_t

    然后是短期关系，
        y_t - y_(t-1) = alpha * z_(t-1) + epsilon_t,

    其中 z 是第一个方程的残差。

    然后在以下方程中通过 Dickey-Fuller phi=1 vs phi < 1 检验协整
        z_t = phi * z_(t-1) + eta_t

    如果这意味着 phi < 1，则得出结论 z 序列是平稳的
    是平稳的，因此得出结论序列 y 和 x 是协整的。

    Parameters
    ----------
    dependent_series : pd.Series
        要分析的一对中的第一个时间序列。
    independent_series : pd.Series
        要分析的一对中的第二个时间序列。

    Returns
    -------
    Tuple[float, float, float, pd.Series, float, float]
        c : float
            长期关系 y_t = c + gamma * x_t + z_t 中的常数项。这
            描述了 y 相对于 gamma * x 的静态偏移。

        gamma : float
            长期关系 y_t = c + gamma * x_t + z_t 中的 gamma 项。这
            描述了常数偏移后的 y 和 x 之间的比率。

        alpha : float
            短期关系 y_t - y_(t-1) = alpha * z_(t-1) + epsilon 中的 alpha 项。这
            给出了向长期均值误差修正强度的指示。

        z : pd.Series
            来自长期关系 y_t = c + gamma * x_t + z_t 的残差 z_t 序列，表示
            误差修正项的值。

        dfstat : float
            第二个方程中 phi = 1 vs phi < 1 的 Dickey Fuller 检验统计量。更
            负的值意味着存在更强的协整。

        pvalue : float
            对应于 Dickey Fuller 检验统计量的 p 值。较低的值意味着
            更强烈地拒绝无协整，即协整的证据更强。

    """
    # pylint: disable=import-outside-toplevel
    import statsmodels.api as sm
    from statsmodels.tsa.stattools import adfuller

    warnings.simplefilter(action="ignore", category=FutureWarning)
    long_run_ols = sm.OLS(dependent_series, sm.add_constant(independent_series))
    warnings.simplefilter(action="default", category=FutureWarning)

    long_run_ols_fit = long_run_ols.fit()

    c, gamma = long_run_ols_fit.params
    z = long_run_ols_fit.resid

    short_run_ols = sm.OLS(dependent_series.diff().iloc[1:], (z.shift().iloc[1:]))
    short_run_ols_fit = short_run_ols.fit()

    alpha = short_run_ols_fit.params.iloc[0]

    # NOTE: The p-value returned by the adfuller function assumes we do not estimate z
    # first, but test stationarity of an unestimated series directly. This assumption
    # should have limited effect for high N, however. Critical values taking this into
    # account more accurately are provided in e.g. McKinnon (1990) and Engle & Yoo (1987).

    adfstat, pvalue, _, _, _ = adfuller(z, maxlag=1, autolag=None)

    return c, gamma, alpha, z, adfstat, pvalue


def mock_multi_index_data():
    """创建一个用于测试目的的模拟多重索引数据框。"""
    # pylint: disable=import-outside-toplevel
    from numpy import random
    from pandas import DataFrame, MultiIndex

    arrays = [
        ["individual_" + str(i) for i in range(1, 11) for _ in range(5)],
        list(range(1, 6)) * 10,
    ]
    index = MultiIndex.from_arrays(arrays, names=("individual", "time"))

    df = DataFrame(
        {
            "income": random.randint(20000, 80000, size=50),
            "age": random.randint(25, 60, size=50),
            "education": random.randint(12, 21, size=50),
        },
        index=index,
    )

    return df
