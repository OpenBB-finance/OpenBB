"""计量经济学路由器。"""

# pylint: disable=too-many-lines

from itertools import combinations
from typing import Any, Literal

from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from pydantic import BaseModel, PositiveInt, model_serializer

router = Router(prefix="", description="计量经济学分析工具。")


class OLSRegressionResults(BaseModel):
    """OLS Regression Results that serializes statsmodels objects."""

    model: Any
    results: Any

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True

    @model_serializer
    def serialize_model(self) -> dict:
        """Serialize statsmodels objects to a dictionary."""
        results = self.results
        conf_int = results.conf_int()
        conf_int_dict = (
            conf_int.to_dict()
            if hasattr(conf_int, "to_dict")
            else conf_int.to_dict("index")
        )
        return {
            "params": (
                results.params.to_dict()
                if hasattr(results.params, "to_dict")
                else dict(results.params)
            ),
            "rsquared": float(results.rsquared),
            "rsquared_adj": float(results.rsquared_adj),
            "fvalue": float(results.fvalue) if results.fvalue is not None else None,
            "f_pvalue": (
                float(results.f_pvalue) if results.f_pvalue is not None else None
            ),
            "aic": float(results.aic),
            "bic": float(results.bic),
            "llf": float(results.llf),
            "nobs": int(results.nobs),
            "df_model": float(results.df_model),
            "df_resid": float(results.df_resid),
            "pvalues": (
                results.pvalues.to_dict()
                if hasattr(results.pvalues, "to_dict")
                else dict(results.pvalues)
            ),
            "tvalues": (
                results.tvalues.to_dict()
                if hasattr(results.tvalues, "to_dict")
                else dict(results.tvalues)
            ),
            "bse": (
                results.bse.to_dict()
                if hasattr(results.bse, "to_dict")
                else dict(results.bse)
            ),
            "conf_int": conf_int_dict,
        }


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="获取数据集的相关矩阵。",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                "obb.econometrics.correlation_matrix(data=stock_data)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def correlation_matrix(
    data: list[Data], method: Literal["pearson", "kendall", "spearman"] = "pearson"
) -> OBBject[list[Data]]:
    """获取输入数据集的相关矩阵。

    相关矩阵提供了数据集不同变量之间关系的视图。
    通过量化变量之间相互变动的程度，该矩阵有助于识别模式、
    趋势和进行更深入分析的潜在领域。相关系数的范围从 -1 到 1，
    其中 -1 表示完全负相关，0 表示无相关，1 表示完全正相关。

    Parameters
    ----------
    data : list[Data]
        输入数据集。
    method : Literal["pearson", "kendall", "spearman"]
        用于计算相关性的方法。默认为 "pearson"。
            pearson : 标准相关系数
            kendall : Kendall Tau 相关系数
            spearman : Spearman 秩相关

    Returns
    -------
    OBBject[list[Data]]
        相关矩阵。
    """
    # pylint: disable=import-outside-toplevel
    import numpy as np
    from openbb_core.app.utils import basemodel_to_df

    df = basemodel_to_df(data)
    # remove non float columns from the dataframe to perform the correlation

    if "symbol" in df.columns and len(df.symbol.unique()) > 1 and "close" in df.columns:
        df = df.pivot(
            columns="symbol",
            values="close",
        )

    corr = df.corr(method=method, numeric_only=True)

    # replace nan values with None to allow for json serialization
    corr = corr.replace(np.nan, None)

    ret = []
    for k, v in corr.items():
        v["comp_to"] = k
        ret.append(Data(**v))
    return OBBject(results=ret)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="执行普通最小二乘法 (OLS) 回归。",
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
    data: list[Data],
    y_column: str,
    x_columns: list[str],
) -> OBBject[dict]:
    """执行普通最小二乘法 (OLS) 回归。

    OLS 回归是一种基本的统计方法，用于探索和建模因变量
    与一个或多个自变量之间的关系。通过将最佳线性方程拟合到数据，
    它有助于揭示自变量的变化如何与因变量的变化相关联。
    这将返回 statsmodels 库中的模型和结果对象。

    Parameters
    ----------
    data: list[Data]
        输入数据集。
    y_column: str
        目标列。
    x_columns: list[str]
        用作外生变量的列列表。

    Returns
    -------
    OBBject[dict]
        带有作为模型和结果对象的 OBBject。
    """
    # pylint: disable=import-outside-toplevel
    import statsmodels.api as sm
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
        get_target_columns,
    )

    X = sm.add_constant(get_target_columns(basemodel_to_df(data), x_columns))
    y = get_target_column(basemodel_to_df(data), y_column)
    model = sm.OLS(y, X)
    results = model.fit()
    return OBBject(results=OLSRegressionResults(model=model, results=results))


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="执行普通最小二乘法 (OLS) 回归并返回摘要。",
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
    data: list[Data],
    y_column: str,
    x_columns: list[str],
) -> OBBject[Data]:
    """执行普通最小二乘法 (OLS) 回归。

    这将返回 statsmodels 中的摘要对象。

    Parameters
    ----------
    data: list[Data]
        输入数据集。
    y_column: str
        目标列。
    x_columns: list[str]
        用作外生变量的列列表。

    Returns
    -------
    OBBject[Data]
        OBBject，结果为摘要对象。
    """
    # pylint: disable=import-outside-toplevel
    import re  # noqa
    import statsmodels.api as sm  # noqa
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
        get_target_columns,
    )

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
            description="执行杜宾-沃森 (Durbin-Watson) 自相关检验。",
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
    data: list[Data],
    y_column: str,
    x_columns: list[str],
) -> OBBject[Data]:
    """执行杜宾-沃森 (Durbin-Watson) 自相关检验。

    杜宾-沃森检验是一种广泛用于检测统计或计量经济模型残差中是否存在自相关的方法。
    当数据系列中的过去值影响未来值时，就会发生自相关，
    这可能是时间序列分析中的一个关键问题，会影响模型预测的可靠性。
    该检验提供一个范围从 0 到 4 的统计量，其中约 2 的值表明
    无自相关，接近 0 的值表明正自相关，接近 4 的值表明
    负自相关。了解自相关程度有助于改进模型以更好地捕捉
    数据的潜在动态，确保更准确和值得信赖的结果。

    Parameters
    ----------
    data: list[Data]
        输入数据集。
    y_column: str
        目标列。
    x_columns: list[str]
        用作外生变量的列列表。

    Returns
    -------
    OBBject[dict]
        OBBject，结果为检验得分。
    """
    # pylint: disable=import-outside-toplevel
    import statsmodels.api as sm
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
        get_target_columns,
    )
    from statsmodels.stats.stattools import durbin_watson

    X = sm.add_constant(get_target_columns(basemodel_to_df(data), x_columns))
    y = get_target_column(basemodel_to_df(data), y_column)
    results = sm.OLS(y, X).fit()
    return OBBject(results=Data(score=durbin_watson(results.resid)))


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="对残差自相关执行布罗施-戈弗雷 (Breusch-Godfrey) 拉格朗日乘数检验。",
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
    data: list[Data],
    y_column: str,
    x_columns: list[str],
    lags: PositiveInt = 1,
) -> OBBject[Data]:
    """对残差自相关执行布罗施-戈弗雷 (Breusch-Godfrey) 拉格朗日乘数检验。

    布罗施-戈弗雷拉格朗日乘数检验是一种用于揭示回归模型残差内自相关的复杂工具。
    残差中的自相关可能表明模型未能捕捉到底层数据结构的某些方面，
    可能导致有偏或低效的估计。
    通过指定滞后数，您可以控制检查自相关的检验深度，
    允许进行与数据特定特征相匹配的定制分析。
    此检验在计量经济学和时间序列分析中特别有价值，其中理解误差的独立性
    对于模型有效性至关重要。

    Parameters
    ----------
    data: list[Data]
        输入数据集。
    y_column: str
        目标列。
    x_columns: list[str]
        用作外生变量的列列表。
    lags: PositiveInt
        用于检验的滞后数。

    Returns
    -------
    OBBject[Data]
    from statsmodels.stats.diagnostic import (
        acorr_breusch_godfrey,  # type: ignore # pylint: disable=import-outside-toplevel
    )
    """
    # pylint: disable=import-outside-toplevel
    import statsmodels.api as sm
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
        get_target_columns,
    )
    from statsmodels.stats.diagnostic import (
        acorr_breusch_godfrey,
    )

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
            description="执行两个时间序列之间的协整检验。",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                'obb.econometrics.cointegration(data=stock_data, columns=["open", "close"])',
            ],
        ),
    ],
)
def cointegration(
    data: list[Data],
    columns: list[str],
) -> OBBject[Data]:
    """使用两步恩格尔-格兰杰 (Engle-Granger) 检验显示两个时间序列之间的协整关系。

    两步恩格尔-格兰杰检验是一种旨在检测两个时间序列之间协整关系的方法。
    协整是一种统计属性，表明两个或多个时间序列在长期内一起移动，
    即使它们单独是非平稳的。这个概念在经济学和金融学中至关重要，识别
    共享共同随机趋势的资产对或组可以为长期投资策略
    和风险管理实践提供信息。恩格尔-格兰杰检验首先通过
    通过将一个时间序列对另一个进行回归来检查稳定的长期关系，然后测试残差的平稳性。
    如果发现残差是平稳的，则表明尽管有任何短期偏差，
    这些系列随时间推移受均衡关系约束。

    Parameters
    ----------
    data: list[Data]
        输入数据集。
    columns: list[str]
        要检查协整的数据列。
    maxlag: PositiveInt
        用于检验的滞后数。

    Returns
    -------
    OBBject[Data]
        OBBject，结果为检验得分。
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.utils import basemodel_to_df, get_target_columns  # noqa
    from openbb_econometrics.utils import (  # noqa
        get_engle_granger_two_step_cointegration_test,
    )

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
            description="执行格兰杰因果关系检验以确定 X 是否“导致” y。",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()",  # noqa: E501
                'obb.econometrics.causality(data=stock_data, y_column="close", x_column="open")',
            ],
        ),
        APIEx(
            description="模拟数据示例。",
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
    data: list[Data],
    y_column: str,
    x_column: str,
    lag: PositiveInt = 3,
) -> OBBject[Data]:
    """执行格兰杰因果关系检验以确定 X 是否“导致” y。

    格兰杰因果关系检验是一种统计假设检验，用于确定一个时间序列是否有助于
    预测另一个。虽然在这种背景下的“因果关系”并不意味着哲学意义上的
    因果关系，但它确实检验了一个变量的变化是否系统地跟随着
    另一个变量的变化，表明存在预测关系。通过指定滞后，您可以设置
    在时间序列中回顾的周期数以评估此关系。此检验在经济和
    金融数据分析中特别有用，理解指标之间的超前-滞后关系可以为投资
    决策和政策制定提供信息。

    Parameters
    ----------
    data: list[Data]
        输入数据集。
    y_column: str
        目标列。
    x_column: str
        用作外生变量的列。
    lag: PositiveInt
        用于检验的滞后数。

    Returns
    -------
    OBBject[Data]
        OBBject，结果为检验得分。
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from pandas import DataFrame, concat
    from statsmodels.tsa.stattools import grangercausalitytests

    X = get_target_column(basemodel_to_df(data), x_column)
    y = get_target_column(basemodel_to_df(data), y_column)

    granger = grangercausalitytests(concat([y, X], axis=1), [lag], verbose=False)

    for test in granger[lag][0]:
        # As ssr_chi2test and lrtest have one less value in the tuple, we fill
        # this value with a '-' to allow the conversion to a DataFrame
        if len(granger[lag][0][test]) != 4:
            pars = granger[lag][0][test]
            granger[lag][0][test] = (pars[0], pars[1], "-", pars[2])

    df = DataFrame(granger[lag][0], index=["F-test", "P-value", "Count", "Lags"]).T
    results = df.to_dict()

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="执行增强迪基-福勒 (ADF) 单位根检验。",
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
    data: list[Data],
    column: str,
    regression: Literal["c", "ct", "ctt"] = "c",
) -> OBBject[Data]:
    """执行增强迪基-福勒 (ADF) 单位根检验。

    ADF 检验是一种用于测试时间序列中是否存在单位根的流行方法。
    单位根表明序列可能是非平稳的，这意味着其统计属性（如均值、
    方差和自相关）可能会随时间变化。单位根的存在表明时间序列可能
    受随机游走过程影响，使其不可预测且难以建模和预测。
    'regression' 参数允许您指定测试中使用的模型：'c' 表示常数项，
    'ct' 表示常数和趋势项，'ctt' 表示常数、线性和二次趋势。
    这种灵活性有助于根据数据的特定特征定制测试，提供更准确的
    平稳性评估。

    Parameters
    ----------
    data: list[Data]
        输入数据集。
    column: str
        要检查单位根的数据列。
    regression: Literal["c", "ct", "ctt"]
        测试中使用的回归类型。"c" 表示仅常数，"ct" 表示常数和趋势，"ctt" 表示
        常数、趋势和趋势的平方。

    Returns
    -------
    OBBject[Data]
        OBBject，结果为检验得分。
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.utils import basemodel_to_df, get_target_column
    from statsmodels.tsa.stattools import adfuller

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
    data: list[Data],
    y_column: str,
    x_columns: list[str],
) -> OBBject[dict]:
    """对面版数据执行单向随机效应模型。

    面板数据的单向随机效应模型为分析跨越时间和实体（如个人、公司、国家等）的数据提供了一种细致的方法。
    通过承认和建模这些实体内部存在的随机变化，该方法提供了对数据集出现的
    一般模式的见解。

    Parameters
    ----------
    data: list[Data]
        输入数据集。
    y_column: str
        目标列。
    x_columns: list[str]
        用作外生变量的列列表。

    Returns
    -------
    OBBject[dict]
        OBBject，返回拟合模型。
    """
    # pylint: disable=import-outside-toplevel
    import statsmodels.api as sm
    from linearmodels.panel import RandomEffects
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
        get_target_columns,
    )

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
    data: list[Data],
    y_column: str,
    x_columns: list[str],
) -> OBBject[dict]:
    """对面板数据执行组间估计量回归。

    面板数据回归分析的组间估计量侧重于实体（如个人、公司或国家）
    随时间推移的差异。通过聚合每个实体的数据并分析平均结果，
    该方法提供了有关解释变量 (x_columns) 对所有实体的因变量 (y_column)
    的总体影响的见解。

    Parameters
    ----------
    data: list[Data]
        输入数据集。
    y_column: str
        目标列。
    x_columns: list[str]
        用作外生变量的列列表。

    Returns
    -------
    OBBject[dict]
        OBBject，返回拟合模型。
    """
    # pylint: disable=import-outside-toplevel
    import statsmodels.api as sm
    from linearmodels.panel import BetweenOLS
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
        get_target_columns,
    )

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
    data: list[Data],
    y_column: str,
    x_columns: list[str],
) -> OBBject[dict]:
    """对面板数据执行混合系数估计量回归。

    面板数据回归分析的混合系数估计量将数据视为大型横截面，
    而不区分时间或实体（如个人、公司或国家）的变化。
    通过假设解释变量 (x_columns) 对所有实体和时间段的因变量 (y_column)
    具有统一的影响，该方法简化了分析并提供了数据内关系的广义视图。

    Parameters
    ----------
    data: list[Data]
        输入数据集。
    y_column: str
        目标列。
    x_columns: list[str]
        用作外生变量的列列表。

    Returns
    -------
    OBBject[dict]
        OBBject，返回拟合模型。
    """
    # pylint: disable=import-outside-toplevel
    import statsmodels.api as sm
    from linearmodels.panel import PooledOLS
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
        get_target_columns,
    )

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
    data: list[Data],
    y_column: str,
    x_columns: list[str],
) -> OBBject[dict]:
    """面板数据的一种和两种固定效应估计量。

    面板数据的固定效应估计量能够专注于实体（如个人、公司或国家）
    和/或时间段的独特特征。通过控制实体特定和/或时间特定的影响，
    该方法隔离了解释变量 (x_columns) 对因变量 (y_column) 的影响，
    假设这些实体或时间效应捕捉到了未观察到的异质性。

    Parameters
    ----------
    data: list[Data]
        输入数据集。
    y_column: str
        目标列。
    x_columns: list[str]
        用作外生变量的列列表。

    Returns
    -------
    OBBject[dict]
        OBBject，返回拟合模型。
    """
    # pylint: disable=import-outside-toplevel
    import statsmodels.api as sm
    from linearmodels.panel import PanelOLS
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
        get_target_columns,
    )

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
    data: list[Data],
    y_column: str,
    x_columns: list[str],
) -> OBBject[dict]:
    """对面板数据执行一阶差分估计。

    面板数据分析的一阶差分估计量侧重于每个实体（如个人、公司或国家）
    连续观察值之间的变化。通过对数据进行差分，该方法有效地
    消除了随时间不变的实体特定效应，允许检查解释变量 (x_columns)
    的变化对因变量 (y_column) 变化的影响。

    Parameters
    ----------
    Parameters
    ----------
    data: list[Data]
        输入数据集。
    y_column: str
        目标列。
    x_columns: list[str]
        用作外生变量的列列表。

    Returns
    -------
    OBBject[dict]
        OBBject，返回拟合模型。
    """
    # pylint: disable=import-outside-toplevel
    from linearmodels.panel import FirstDifferenceOLS
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
        get_target_columns,
    )

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
    data: list[Data],
    y_column: str,
    x_columns: list[str],
) -> OBBject[dict]:
    """面板数据的 Fama-MacBeth 估计量。

    Fama-MacBeth 估计量是一种两步过程，因其在金融领域用于估计风险溢价
    和评估资本资产定价模型而闻名。通过首先估计每个时间段的横截面回归，
    然后随时间平均回归系数，该方法提供了有关不同实体（如个人、公司或国家）
    之间因变量 (y_column) 和解释变量 (x_columns) 之间关系的见解。

    Parameters
    ----------
    Parameters
    ----------
    data: list[Data]
        输入数据集。
    y_column: str
        目标列。
    x_columns: list[str]
        用作外生变量的列列表。

    Returns
    -------
    OBBject[dict]
        OBBject，返回拟合模型。
    """
    # pylint: disable=import-outside-toplevel
    import statsmodels.api as sm
    from linearmodels.panel import FamaMacBeth
    from openbb_core.app.utils import (
        basemodel_to_df,
        get_target_column,
        get_target_columns,
    )

    X = get_target_columns(basemodel_to_df(data), x_columns)
    y = get_target_column(basemodel_to_df(data), y_column)
    exogenous = sm.add_constant(X)
    results = FamaMacBeth(y, exogenous).fit()
    return OBBject(results={"results": results})


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="计算方差膨胀因子。",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='yfinance').to_df()",  # noqa: E501  pylint: disable= C0301
                'obb.econometrics.variance_inflation_factor(data=stock_data, columns=["open", "high", "low", "close"])',  # noqa: E501  pylint: disable= C0301
            ],
        ),
        APIEx(
            parameters={
                "columns": ["open", "high", "low"],
                "data": APIEx.mock_data("timeseries"),
            }
        ),
    ],
)
def variance_inflation_factor(
    data: list[Data], columns: list[str] | None = None
) -> OBBject[list[Data]]:
    """计算 VIF（方差膨胀因子），用于检验共线性。

    它量化了普通最小二乘回归分析中多重共线性的严重程度。
    方差膨胀因子的平方根表明，与如果该变量与模型中其他预测变量的相关性为 0 相比，
    标准误差增加了多少。

    其定义为：

    $ VIF_i = 1 / (1 - R_i^2) $
    其中 $ R_i $ 是回归方程的决定系数，第 i 列作为外生变量的结果。

    VIF 超过 5 表明存在高共线性和相关性。超过 10 的值表明会导致问题，
    而值为 1 表明无相关性。因此，1 到 5 之间的 VIF 值通常被认为是可接受的。
    为了改善结果，通常可以删除具有高 VIF 的列。

    有关更多信息，请参阅：https://en.wikipedia.org/wiki/Variance_inflation_factor

    Parameters
    ----------
    dataset: list[Data]
        要计算 VIF 的数据集
    columns: Optional[list]
        要计算以测试共线性的列

    Returns
    -------
    OBBject[list[Data]]
        所选列的结果 VIF 值
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.utils import (
        basemodel_to_df,
        df_to_basemodel,
    )
    from pandas import DataFrame
    from statsmodels.stats.outliers_influence import variance_inflation_factor as vif
    from statsmodels.tools.tools import add_constant

    # Convert to pandas dataframe
    dataset = basemodel_to_df(data)

    # Add a constant
    df = add_constant(dataset if columns is None else dataset[columns])

    # Remove date and string type because VIF doesn't work for these types
    df = df.select_dtypes(exclude=["object", "datetime", "timedelta"])  # type: ignore

    # Calculate the VIF values
    vif_values: dict = {}
    for i in range(len(df.columns))[1:]:
        vif_values[f"{df.columns[i]}"] = vif(df.values, i)

    results = df_to_basemodel(DataFrame(vif_values, index=[0]))
    return OBBject(results=results)
