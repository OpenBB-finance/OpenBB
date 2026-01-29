"""绘图类实现。"""

# pylint: disable=too-many-arguments,unused-argument,too-many-positional-arguments

from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Literal,
    Union,
)
from warnings import warn

from importlib_metadata import entry_points
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.charts.chart import Chart
from openbb_core.app.model.obbject import OBBject
from openbb_core.provider.abstract.data import Data

from openbb_charting.charts.helpers import (
    get_charting_functions,
    get_charting_functions_list,
)

if TYPE_CHECKING:
    from numpy import ndarray  # noqa
    from pandas import DataFrame, Series
    from plotly.graph_objs import Figure
    from openbb_charting.core.openbb_figure import OpenBBFigure
    from openbb_charting.query_params import ChartParams
    from openbb_charting.core.backend import Backend


class Charting:
    """绘图扩展。

    Methods
    -------
    show
        显示图表并将其保存到 OBBject 中。
    to_chart
        重绘图表并将其保存到 OBBject 中，带有可选的数据入口点。
    functions
        返回带有绘图功能的平台命令列表。
    get_params
        返回创建 OBBject 的函数的绘图参数。
    indicators
        返回可用于 `to_chart` 方法和 OHLC+V 数据的可用技术指标列表。
    table
        显示交互式表格。
    create_line_chart
        从外部数据创建折线图。
    create_bar_chart
        从外部数据创建一个条形图，在单个 x 轴上具有一个或多个 y 轴值。
    create_correlation_matrix
        从外部数据创建相关矩阵。
    toggle_chart_style
        在明亮和黑暗模式之间切换现有图表的图表样式。
    """

    _extension_views: ClassVar[list[type]] = [
        entry_point.load()
        for entry_point in entry_points(group="openbb_charting_extension")
    ]
    _format = "plotly"  # the charts computed by this extension will be in plotly format

    def __init__(self, obbject):
        """初始化绘图扩展。"""
        # pylint: disable=import-outside-toplevel
        import importlib  # noqa

        charting_settings_module = importlib.import_module(
            "openbb_core.app.model.charts.charting_settings", "ChartingSettings"
        )
        ChartingSettings = charting_settings_module.ChartingSettings

        self._obbject: OBBject = obbject
        self._charting_settings = ChartingSettings(
            user_settings=self._obbject._user_settings,  # type: ignore
            system_settings=self._obbject._system_settings,  # type: ignore
        )
        self._backend = self._handle_backend()
        self._functions: dict[str, Callable] = self._get_functions()

    @classmethod
    def indicators(cls):
        """返回 IndicatorsParams 类的一个实例，其中包含所有可用的指标及其参数。

        如果不分配给变量，它将把信息打印到控制台。
        """
        # pylint: disable=import-outside-toplevel
        from openbb_charting.query_params import IndicatorsParams

        return IndicatorsParams()

    @classmethod
    def functions(cls) -> list[str]:
        """返回可用函数的列表。"""
        functions: list[str] = []
        for view in cls._extension_views:
            functions.extend(get_charting_functions_list(view))

        return functions

    def _get_functions(self) -> dict[str, Callable]:
        """返回包含可用函数的字典。"""
        functions: dict[str, Callable] = {}
        for view in self._extension_views:
            functions.update(get_charting_functions(view))

        return functions

    def _handle_backend(self) -> "Backend":
        """创建并启动后端。"""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.core.backend import create_backend, get_backend

        create_backend(self._charting_settings)
        backend = get_backend()
        backend.start(debug=self._charting_settings.debug_mode)  # type: ignore
        return backend  # type: ignore

    def _get_chart_function(self, route: str) -> Callable:
        """给定路由，返回图表函数。模块必须包含给定的路由。"""
        if route is None:
            raise ValueError("OBBject was initialized with no function route.")
        adjusted_route = route.replace("/", "_")[1:]
        if adjusted_route not in self._functions:
            raise ValueError(
                f"Could not find the route `{adjusted_route}` in the charting functions."
            )
        return self._functions[adjusted_route]

    def get_params(self) -> Union["ChartParams", None]:
        """返回创建 OBBject 的函数的 ChartQueryParams 类。

        如果不分配给变量，它将把文档字符串打印到控制台。
        如果未定义该类，将返回该函数的帮助信息。
        """
        # pylint: disable=import-outside-toplevel
        from openbb_charting.query_params import ChartParams

        if self._obbject._route is None:  # pylint: disable=protected-access
            raise ValueError("OBBject was initialized with no function route.")
        charting_function = (
            self._obbject._route  # pylint: disable=protected-access
        ).replace("/", "_")[1:]
        if hasattr(ChartParams, charting_function):
            return getattr(ChartParams, charting_function)()

        return help(  # type: ignore
            self._get_chart_function(  # pylint: disable=protected-access
                self._obbject.extra[
                    "metadata"
                ].route  # pylint: disable=protected-access
            )
        )

    def _prepare_data_as_df(
        self, data: Union["DataFrame", "Series"] | None
    ) -> tuple["DataFrame", bool]:
        """将提供的数据转换为 DataFrame。"""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.utils import basemodel_to_df, convert_to_basemodel
        from pandas import DataFrame, Series

        has_data = (isinstance(data, (Data, DataFrame, Series)) and not data.empty) or (bool(data))  # type: ignore
        index = (
            data.index.name
            if has_data and isinstance(data, (DataFrame, Series))
            else None
        )
        data_as_df: DataFrame = (
            basemodel_to_df(convert_to_basemodel(data), index=index)  # type: ignore
            if has_data
            else self._obbject.to_dataframe(index=index)  # type: ignore
        )
        if "date" in data_as_df.columns:
            data_as_df = data_as_df.set_index("date")
        if "provider" in data_as_df.columns:
            data_as_df.drop(columns="provider", inplace=True)
        return data_as_df, has_data

    # pylint: disable=too-many-locals
    def create_line_chart(
        self,
        data: Union[
            list,
            dict,
            "DataFrame",
            list["DataFrame"],
            "Series",
            list["Series"],
            "ndarray",
            Data,
        ],
        index: str | None = None,
        target: str | None = None,
        title: str | None = None,
        x: str | None = None,
        xtitle: str | None = None,
        y: str | list[str] | None = None,
        ytitle: str | None = None,
        y2: str | list[str] | None = None,
        y2title: str | None = None,
        layout_kwargs: dict | None = None,
        scatter_kwargs: dict | None = None,
        normalize: bool = False,
        returns: bool = False,
        same_axis: bool = False,
        render: bool = True,
        **kwargs,
    ) -> Union["OpenBBFigure", "Figure", None]:
        """从外部数据创建折线图并渲染图表或返回 OpenBBFigure。

        Parameters
        ----------
        data : Union[Data, DataFrame, Series]
            要绘制的数据 (OHLCV 数据)。
        index : Optional[str], optional
            索引列，默认为 None
        target : Optional[str], optional
            要绘制的目标列，默认为 None
        title : Optional[str], optional
            图表标题，默认为 None
        x : Optional[str], optional
            X 轴列，默认为 None
        xtitle : Optional[str], optional
            X 轴标题，默认为 None
        y : Optional[Union[str, List[str]]], optional
            Y 轴列，默认为 None
            如果未提供，则针对数据内容优化布局。
            当存在许多单位/刻度时，
            它将尝试根据值的范围进行分割。
        ytitle : Optional[str], optional
            Y 轴标题，默认为 None
        y2 : Optional[Union[str, List[str]]], optional
            Y2 轴列，默认为 None
        y2title : Optional[str], optional
            Y2 轴标题，默认为 None
        layout_kwargs : Optional[dict], optional
            用于 `fig.update_layout` 的其他 Plotly 布局参数，默认为 None
        scatter_kwargs : Optional[dict], optional
            创建每个散点图时应用的其他 Plotly 参数，默认为 None
        normalize : bool, optional
            使用 Z-Score 标准化对数据进行标准化，默认为 False
        returns : bool, optional
            将数据转换为累积收益率，默认为 False
        same_axis: bool, optional
            如果为 True，强制所有数据位于同一 Y 轴上，默认为 False
        render: bool, optional
            如果为 True，将渲染图表，默认为 True
        **kwargs: Dict[str, Any]
            要传递给 `figure.show()` 的额外参数
        """
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.generic_charts import line_chart

        fig = line_chart(
            data=data,
            index=index,
            target=target,
            title=title,
            x=x,
            xtitle=xtitle,
            y=y,
            ytitle=ytitle,
            y2=y2,
            y2title=y2title,
            layout_kwargs=layout_kwargs,
            scatter_kwargs=scatter_kwargs,
            normalize=normalize,
            returns=returns,
            same_axis=same_axis,
            **kwargs,
        )
        fig = self._set_chart_style(fig)
        if render:
            return fig.show(**kwargs)

        return fig

    def create_bar_chart(
        self,
        data: Union[
            list,
            dict,
            "DataFrame",
            list["DataFrame"],
            "Series",
            list["Series"],
            "ndarray",
            Data,
        ],
        x: str,
        y: str | list[str],
        barmode: Literal["group", "stack", "relative", "overlay"] = "group",
        xtype: Literal[
            "category", "multicategory", "date", "log", "linear"
        ] = "category",
        title: str | None = None,
        xtitle: str | None = None,
        ytitle: str | None = None,
        orientation: Literal["h", "v"] = "v",
        colors: list[str] | None = None,
        layout_kwargs: dict[str, Any] | None = None,
        bar_kwargs: dict[str, Any] | None = None,
        render: bool = True,
        **kwargs,
    ) -> Union["OpenBBFigure", "Figure", None]:
        """在单个 x 轴上创建一个具有一个或多个 y 轴值的条形图。

        Parameters
        ----------
        data : Union[list, dict, DataFrame, List[DataFrame], Series, List[Series], ndarray, Data]
            要绘制的数据。
        x : str
            x 轴列名。
        y : Union[str, List[str]]
            y 轴列名。
        barmode : Literal["group", "stack", "relative", "overlay"], optional
            条形图模式，默认为 "group"。
        xtype : Literal["category", "multicategory", "date", "log", "linear"], optional
            x 轴类型，默认为 "category"。
        title : str, optional
            图表标题，默认为 None。
        xtitle : str, optional
            x 轴标题，默认为 None。
        ytitle : str, optional
            y 轴标题，默认为 None。
        colors: List[str], optional
            手动设置 'y' 中每一列循环使用的颜色，默认为 None。
        bar_kwargs : Dict[str, Any], optional
            与 figure.add_bar() 一起应用的其他关键字参数，默认为 None。
        layout_kwargs : Dict[str, Any], optional
            与 figure.update_layout() 一起应用的其他关键字参数，默认为 None。
        Returns
        -------
        OpenBBFigure
            OpenBBFigure 对象。
        """
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.generic_charts import bar_chart

        fig = bar_chart(
            data=data,
            x=x,
            y=y,
            barmode=barmode,
            xtype=xtype,
            title=title,
            xtitle=xtitle,
            ytitle=ytitle,
            orientation=orientation,
            colors=colors,
            bar_kwargs=bar_kwargs,
            layout_kwargs=layout_kwargs,
        )
        fig = self._set_chart_style(fig)
        if render:
            return fig.show(**kwargs)

        return fig

    def create_3d_surface(
        self,
        X: "Series",
        Y: "Series",
        Z: "Series",
        xtitle: str | None = "DTE",
        ytitle: str | None = "Strike",
        ztitle: str | None = "IV",
        colorscale: str | list | None = None,
        title: str | None = None,
        layout_kwargs: dict[str, Any] | None = None,
        theme: Literal["dark", "light"] | None = None,
    ) -> Union["OpenBBFigure", "Figure"]:
        """创建 3D 曲面图。

        Parameters
        ----------
        X : pd.Series
            x 轴数据。
        Y : pd.Series
            y 轴数据。
        Z : pd.Series
            z 轴数据。
        xtitle : str, optional
            x 轴标题，默认为 "DTE"。
        ytitle : str, optional
            y 轴标题，默认为 "Strike"。
        ztitle : str, optional
            z 轴标题，默认为 "IV"。
        colorscale : Union[str, list], optional
            用于曲面的色标，默认为 None。
        title : str, optional
            图表标题，默认为 None。
        layout_kwargs : Optional[dict[str, Any]], optional
            与 figure.update_layout() 一起应用的其他关键字参数，默认为 None。

        Returns
        -------
        OpenBBFigure
            OpenBBFigure 对象。
        """
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.generic_charts import surface3d

        fig = surface3d(
            X=X,
            Y=Y,
            Z=Z,
            xtitle=xtitle,
            ytitle=ytitle,
            ztitle=ztitle,
            colorscale=colorscale,
            title=title,
            layout_kwargs=layout_kwargs,
            theme=theme,
        )
        fig = self._set_chart_style(fig)
        return fig

    def create_correlation_matrix(
        self,
        data: Union[
            list[Data],
            "DataFrame",
        ],
        method: Literal["pearson", "kendall", "spearman"] = "pearson",
        colorscale: str = "RdBu",
        title: str = "Asset Correlation Matrix",
        layout_kwargs: dict[str, Any] | None = None,
    ):
        """从外部数据创建相关矩阵。

        Parameters
        ----------
        data : Union[list[Data], DataFrame]
            输入数据集。
        method : Literal["pearson", "kendall", "spearman"]
            用于相关计算的方法。默认为 "pearson"。
                pearson : 标准相关系数
                kendall : Kendall Tau 相关系数
                spearman : Spearman 等级相关
        colorscale : str
            用于热图的 Plotly 色标。默认为 "RdBu"。
        title : str
            图表标题。默认为 "Asset Correlation Matrix"。
        layout_kwargs : Dict[str, Any]
            与 figure.update_layout() 一起应用的其他关键字参数，默认为 None。

        Returns
        -------
        OpenBBFigure
            OpenBBFigure 对象。
        """
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.correlation_matrix import correlation_matrix

        kwargs = {
            "data": data,
            "method": method,
            "colorscale": colorscale,
            "title": title,
            "layout_kwargs": layout_kwargs,
        }
        fig, _ = correlation_matrix(**kwargs)
        fig = self._set_chart_style(fig)
        return fig

    def show(self, render: bool = True, **kwargs):
        """显示图表并将其保存到 OBBject。"""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.core.openbb_figure import OpenBBFigure

        try:
            charting_function = self._get_chart_function(
                self._obbject._route  # pylint: disable=protected-access   # type: ignore
            )
            kwargs["obbject_item"] = self._obbject.results
            kwargs["charting_settings"] = self._charting_settings
            kwargs["standard_params"] = (
                self._obbject._standard_params  # pylint: disable=protected-access
            )
            # If the provider interface isn't used, endpoint kwargs are already here.
            # Don't overwrite them.
            obb_kwargs = (
                self._obbject._extra_params or {}  # pylint: disable=protected-access
            )
            if obb_kwargs:
                for k, v in obb_kwargs.items():
                    kwargs["extra_params"].update({k: v})

            kwargs["provider"] = self._obbject.provider
            kwargs["extra"] = self._obbject.extra

            # Handle different types of output from the charting endpoint.
            chart_response: Any = charting_function(**kwargs)

            # If returned a Chart object, set as-is.
            if isinstance(chart_response, Chart):
                self._obbject.chart = chart_response
            # If just an OpenBBFigure gets returned, create the serialized version for the API.
            elif isinstance(chart_response, OpenBBFigure):
                fig = chart_response
                content = fig.show(external=True, **kwargs).to_plotly_json()
                self._obbject.chart = Chart(
                    fig=fig, content=content, format=self._format
                )
            # Current functions return this.
            elif isinstance(chart_response, tuple) and len(chart_response) == 2:
                fig, content = chart_response

                if isinstance(fig, OpenBBFigure):
                    content = fig.show(external=True, **kwargs).to_plotly_json()  # type: ignore
                    self._obbject.chart = Chart(
                        fig=fig, content=content, format=self._format
                    )
                else:
                    self._obbject.chart = Chart(
                        fig=fig, content=content, format=type(fig).__name__
                    )

            else:
                self._obbject.chart = Chart(
                    fig=chart_response, content=None, format="unknown"
                )

            if render and hasattr(fig, "show"):
                fig.show(**kwargs)

        except (RuntimeError, OpenBBError) as e:
            raise e from e

        except Exception:  # pylint: disable=W0718
            try:
                fig = self.create_line_chart(data=self._obbject.results, render=False, **kwargs)  # type: ignore
                fig = self._set_chart_style(fig)  # type: ignore
                content = fig.show(external=True, **kwargs).to_plotly_json()  # type: ignore
                self._obbject.chart = Chart(
                    fig=fig, content=content, format=self._format
                )
                if render:
                    fig.show(**kwargs)  # type: ignore
            except Exception as e:
                raise RuntimeError(
                    "Failed to automatically create a generic chart with the data provided."
                    + f" -> {e} -> {e.args}"
                ) from e

    # pylint: disable=too-many-locals,inconsistent-return-statements
    def to_chart(
        self,
        data: (
            Union[
                list,
                dict,
                "DataFrame",
                list["DataFrame"],
                "Series",
                list["Series"],
                "ndarray",
                Data,
            ]
            | None
        ) = None,
        target: str | None = None,
        index: str | None = None,
        indicators: dict[str, dict[str, Any]] | None = None,
        symbol: str = "",
        candles: bool = True,
        volume: bool = True,
        volume_ticks_x: int = 7,
        render: bool = True,
        **kwargs,
    ):
        """创建带有用户自定义设置（如果有）的 OpenBBFigure 并将其保存到 OBBject 中。

        此函数用于使用 OBBject 中的数据或通过 `data` 参数提供的外部数据填充或重新填充 OBBject 的图表。
        此函数通过覆盖现有图表来修改原始 OBBject。

        Parameters
        ----------
        data : Union[Data, DataFrame, Series]
            要绘制的数据。
        indicators : Dict[str, Dict[str, Any]], optional
            要绘制的指标，默认为 None
        symbol : str, optional
            要绘制的符号。用于标签和标题，默认为 ""
        candles : bool, optional
            如果为 True，将绘制蜡烛图，默认为 True
        volume : bool, optional
            如果为 True，将绘制成交量，默认为 True
        volume_ticks_x : int, optional
            成交量刻度，默认为 7
        render : bool, optional
            如果为 True，将渲染图表，默认为 True
        kwargs: Dict[str, Any]
            要传递给图表构造函数的额外参数。

        Examples
        --------
        绘制带有 TA 指标的时间序列

        >>> from openbb import obb
        >>> res = obb.equity.price.historical("AAPL")
        >>> indicators = dict(
        >>>    sma=dict(length=[20,30,50]),
        >>>    adx=dict(length=14),
        >>>    rsi=dict(length=14),
        >>>    macd=dict(fast=12, slow=26, signal=9),
        >>>    bbands=dict(length=20, std=2),
        >>>    stoch=dict(length=14),
        >>>    ema=dict(length=[20,30,50]),
        >>> )
        >>> res.charting.to_chart(**{"indicators": indicators})

        获取所有可用指标

        >>> res = obb.equity.price.historical("AAPL")
        >>> indicators = res.charting.indicators()
        >>> indicators?
        """
        data_as_df, has_data = self._prepare_data_as_df(data)  # type: ignore
        if target is not None:
            data_as_df = data_as_df[[target]]
        kwargs["candles"] = candles
        kwargs["volume"] = volume
        kwargs["volume_ticks_x"] = volume_ticks_x
        kwargs["indicators"] = indicators if indicators else {}
        kwargs["symbol"] = symbol
        kwargs["target"] = target
        kwargs["index"] = index
        kwargs["obbject_item"] = self._obbject.results
        kwargs["charting_settings"] = self._charting_settings
        kwargs["standard_params"] = (
            self._obbject._standard_params  # pylint: disable=protected-access
        )
        kwargs["extra_params"] = (
            self._obbject._extra_params  # pylint: disable=protected-access
        )
        kwargs["provider"] = self._obbject.provider  # pylint: disable=protected-access
        kwargs["extra"] = self._obbject.extra  # pylint: disable=protected-access
        try:
            if has_data:
                self.show(data=data_as_df, render=render, **kwargs)
            else:
                self.show(**kwargs, render=render)
        except Exception:  # pylint: disable=W0718
            try:
                fig = self.create_line_chart(data=data_as_df, render=False, **kwargs)
                fig = self._set_chart_style(fig)  # type: ignore
                content = fig.show(external=True, **kwargs).to_plotly_json()  # type: ignore
                self._obbject.chart = Chart(
                    fig=fig, content=content, format=self._format
                )
                if render:
                    return fig.show(**kwargs)  # type: ignore
            except Exception as e:  # pylint: disable=W0718
                raise RuntimeError(
                    "Failed to automatically create a generic chart with the data provided."
                ) from e

    def _set_chart_style(self, figure: "Figure"):
        """设置浅色或深色模式的用户首选项。"""
        style = self._charting_settings.chart_style
        font_color = "black" if style == "light" else "white"
        paper_bgcolor = "white" if style == "light" else "black"
        plot_bgcolor = "white" if style == "light" else "black"
        figure = figure.update_layout(
            dict(
                font_color=font_color,
                paper_bgcolor=paper_bgcolor,
                plot_bgcolor=plot_bgcolor,
            )
        )  # pylint: disable=R1735
        return figure

    def toggle_chart_style(self):
        """在浅色和深色模式之间切换图表样式。"""
        if not hasattr(self._obbject.chart, "fig"):
            raise ValueError(
                "Error: No chart has been created. Please create a chart first."
            )
        current = self._charting_settings.chart_style
        new = "light" if current == "dark" else "dark"
        self._charting_settings.chart_style = new
        figure = self._obbject.chart.fig  # type: ignore[union-attr]
        updated_figure = self._set_chart_style(figure)  # type: ignore[union-attr]
        self._obbject.chart.fig = updated_figure  # type: ignore[union-attr]
        self._obbject.chart.content = updated_figure.show(  # type: ignore[union-attr]
            external=True
        ).to_plotly_json()  # type: ignore[union-attr]

    @staticmethod
    def _convert_to_string(x):
        """清理表格数据。"""
        # pylint: disable=import-outside-toplevel
        from numpy import isnan

        if isinstance(x, (float, int)) and not isnan(x):
            return x
        if isinstance(x, dict):
            return ", ".join([str(v) for v in x.values()])
        if isinstance(x, list):
            if all(isinstance(i, dict) for i in x):
                return ", ".join(
                    str(", ".join([str(v) for v in i.values()])) for i in x
                )
            return ", ".join([str(i) for i in x])

        return (
            str(x)
            .replace("[", "")
            .replace("]", "")
            .replace("'{", "")
            .replace("}'", "")
            .replace("nan", "")
        )

    def table(
        self,
        data: Union["DataFrame", "Series"] | None = None,
        title: str = "",
    ):
        """显示交互式表格。

        Parameters
        ----------
        data : Optional[Union[DataFrame, Series]], optional
            要绘制的数据，默认为 None。
            如果未提供数据，将使用 OBBject 结果。
        title : str, optional
            表格标题，默认为 ""。
        """
        # pylint: disable=import-outside-toplevel
        from pandas import RangeIndex

        data_as_df, _ = self._prepare_data_as_df(data)
        if isinstance(data_as_df.index, RangeIndex):
            data_as_df.reset_index(inplace=True, drop=True)
        else:
            data_as_df.reset_index(inplace=True)
        for col in data_as_df.columns:
            data_as_df[col] = data_as_df[col].apply(self._convert_to_string)
        if self._backend.isatty:
            try:
                self._backend.send_table(
                    df_table=data_as_df,
                    title=title
                    or ""
                    or self._obbject._route,  # pylint: disable=protected-access  # type: ignore
                    theme=self._charting_settings.table_style,  # pylint: disable=protected-access
                )
            except Exception as e:  # pylint: disable=W0718
                warn(f"Failed to show figure with backend. {e}")

        else:
            from plotly import optional_imports

            ipython_display = optional_imports.get_module("IPython.display")
            if ipython_display:
                ipython_display.display(ipython_display.HTML(data_as_df.to_html()))
            else:
                warn("IPython.display is not available.")

    def url(
        self,
        url: str,
        title: str = "",
        width: int | None = None,
        height: int | None = None,
    ):
        """返回图表的 URL。"""
        try:
            self._backend.send_url(url=url, title=title, width=width, height=height)
        except Exception as e:  # pylint: disable=W0718
            warn(f"Failed to show figure with backend. {e}")
