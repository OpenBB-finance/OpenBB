"""计量经济学扩展的视图。"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import (
        OpenBBFigure,
    )


class EconometricsViews:
    """计量经济学视图。"""

    @staticmethod
    def econometrics_correlation_matrix(  # noqa: PLR0912
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """相关矩阵图表。

        Parameters
        ----------
        data : Union[list[Data], DataFrame]
            输入数据集。
        method : Literal["pearson", "kendall", "spearman"]
            用于计算相关性的方法。默认为 "pearson"。
                pearson : 标准相关系数
                kendall : Kendall Tau 相关系数
                spearman : Spearman 秩相关
        colorscale : str
            用于热图的 Plotly 色标。默认为 "RdBu"。
        title : str
            图表的标题。默认为 "Asset Correlation Matrix"。
        layout_kwargs : Dict[str, Any]
            应用于 figure.update_layout() 的其他关键字参数，默认为 None。
        """
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.correlation_matrix import correlation_matrix

        return correlation_matrix(**kwargs)  # type: ignore
