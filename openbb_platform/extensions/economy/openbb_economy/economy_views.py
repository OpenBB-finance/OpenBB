"""经济扩展的视图。"""

# flake8: noqa: PLR0912
# pylint: disable=too-many-branches

from typing import TYPE_CHECKING, Any
from warnings import warn

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import (
        OpenBBFigure,
    )


class EconomyViews:
    """经济视图。"""

    @staticmethod
    def economy_fred_series(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """FRED 系列图表。"""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.generic_charts import bar_chart
        from openbb_charting.charts.helpers import (
            z_score_standardization,
        )
        from openbb_charting.core.chart_style import ChartStyle
        from openbb_charting.core.openbb_figure import OpenBBFigure
        from openbb_charting.styles.colors import LARGE_CYCLER
        from openbb_core.app.utils import basemodel_to_df
        from pandas import DataFrame

        ytitle_dict = {
            "chg": "Change",
            "ch1": "Change From Year Ago",
            "pch": "Percent Change",
            "pc1": "Percent Change From Year Ago",
            "pca": "Compounded Annual Rate Of Change",
            "cch": "Continuously Compounded Rate Of Change",
            "cca": "Continuously Compounded Annual Rate Of Change",
            "log": "Natural Log",
        }

        provider = kwargs.get("provider")

        if provider != "fred":
            raise RuntimeError(
                f"此图表方法不支持 {provider}. 支持的提供商: fred."
            )

        columns = basemodel_to_df(kwargs["obbject_item"], index=None).columns.to_list()  # type: ignore

        allow_unsafe = kwargs.get("allow_unsafe", False)
        dropnan = kwargs.get("dropna", True)
        normalize = kwargs.get("normalize", False)

        data_cols = []
        data = kwargs.get("data")

        if isinstance(data, DataFrame) and not data.empty:
            data_cols = data.columns.to_list()
            df_ta = data

        else:
            df_ta = basemodel_to_df(kwargs["obbject_item"], index="date")  # type: ignore

        # Check for unsupported external data injection.
        if allow_unsafe is False and data_cols:
            for data_col in data_cols:
                if data_col not in columns:
                    raise RuntimeError(
                        f"在原始数据中未找到列 '{data_col}'。"
                        + " 除非 `allow_unsafe = True`，否则不支持外部数据注入。"
                    )

        # Align the data so each column has the same index and length.
        if dropnan:
            df_ta = df_ta.dropna(how="any")

        if df_ta.empty or len(df_ta) < 2:
            raise ValueError(
                "删除 NaN 值后没有剩余数据。尝试设置 `dropnan = False`，"
                + " 或在请求中使用 `frequency` 参数。"
            )

        columns = df_ta.columns.to_list()

        metadata = kwargs["extra"].get("results_metadata", {})  # type: ignore

        # Check if the request was transformed by the FRED API.
        params = kwargs["extra_params"] if kwargs.get("extra_params") else {}
        has_params = hasattr(params, "transform") and params.transform is not None  # type: ignore

        # Get a unique list of all units of measurement in the DataFrame.
        y_units = list({metadata.get(col).get("units") for col in columns if col in metadata})  # type: ignore
        if has_params is True and not y_units:
            y_units = [ytitle_dict.get(params.transform)]  # type: ignore

        if normalize or (
            kwargs.get("bar") is True
            and len(y_units) > 1
            and (
                has_params is False
                or not any(i in params.transform for i in ["pc1", "pch", "pca", "cch", "cca", "log"])  # type: ignore
            )
        ):
            normalize = True
            df_ta = df_ta.apply(z_score_standardization)

        if len(y_units) > 2 and has_params is False and allow_unsafe is False:
            raise RuntimeError(
                "此方法最多支持 2 个 y 轴单位。"
                + " 请在数据请求中使用 'transform' 参数，"
                + " 以相同的比例比较所有序列，或设置 `normalize = True`。"
                + " 通过设置 `allow_unsafe = True` 覆盖此错误。"
            )

        y1_units = y_units[0] if y_units else None
        y1title = y1_units
        y2title = y_units[1] if len(y_units) > 1 else None
        xtitle = str(kwargs.get("xtitle", ""))

        # If the request was transformed, the y-axis will be shared under these conditions.
        if has_params and any(i in params.transform for i in ["pc1", "pch", "pca", "cch", "cca", "log"]):  # type: ignore
            y1title = "Log" if params.transform == "Log" else "Percent"  # type: ignore
            y2title = None

        # Set the title for the chart.
        title: str = ""
        if isinstance(kwargs, dict) and title in kwargs:
            title = kwargs["title"]  # type: ignore
        else:
            if metadata.get(columns[0]):  # type: ignore
                title = metadata.get(columns[0]).get("title") if len(columns) == 1 else "FRED Series"  # type: ignore
            else:
                title = "FRED Series"
            transform_title = ytitle_dict.get(params.transform) if has_params is True else ""  # type: ignore
            title = f"{title} - {transform_title}" if transform_title else title

        # Define this to use as a check.
        y3title: str | None = ""

        if kwargs.get("plot_bar") is True or len(df_ta.index) < 100:
            margin = dict(l=10, r=5, b=75 if xtitle else 30)
            try:
                if normalize:
                    y1title = None
                    title = f"{title} - Normalized" if title else "Normalized"
                bar_mode = kwargs.get("barmode", "group")
                fig = bar_chart(
                    df_ta.reset_index(),
                    "date",
                    df_ta.columns.to_list(),
                    title=title,
                    xtitle=xtitle,
                    ytitle=y1title,
                    barmode=bar_mode,  # type: ignore
                    layout_kwargs=dict(margin=margin),  # type: ignore
                )
                if kwargs.get("layout_kwargs"):
                    fig.update_layout(kwargs.get("layout_kwargs"))

                if kwargs.get("title"):
                    fig.set_title(str(kwargs.get("title")))  # type: ignore

                content = fig.to_plotly_json()

                return fig, content  # type: ignore
            except Exception as _:
                warn("条形图失败。尝试折线图。")

        # Create the figure object with subplots.
        fig = OpenBBFigure().create_subplots(
            rows=1, cols=1, shared_xaxes=True, shared_yaxes=False
        )
        fig.update_layout(ChartStyle().plotly_template.get("layout", {}))
        text_color = "white" if ChartStyle().plt_style == "dark" else "black"
        # For each series in the DataFrame, add a scatter plot.
        for i, col in enumerate(df_ta.columns):
            # Check if the y-axis should be shared for this series.
            on_y1 = (
                (
                    metadata.get(col).get("units") == y1_units  # type: ignore
                    or y2title is None  # type: ignore
                    or kwargs.get("same_axis") is True
                )
                if metadata.get(col)  # type: ignore
                else False
            )
            if normalize:
                on_y1 = True

            yaxes = "y2" if not on_y1 else "y1"
            on_y3 = not metadata.get(col) and normalize is False  # type: ignore
            if on_y3:
                yaxes = "y3"
                y3title = df_ta[col].name  # type: ignore
            fig.add_scatter(
                x=df_ta.index,
                y=df_ta[col],
                name=df_ta[col].name,
                mode="lines",
                hovertemplate=f"{df_ta[col].name}: %{{y}}<extra></extra>",
                line=dict(width=2, color=LARGE_CYCLER[i % len(LARGE_CYCLER)]),
                yaxis="y1" if kwargs.get("same_axis") is True else yaxes,
            )

        # Set the y-axis titles, if supplied.
        if kwargs.get("y1title"):
            y1title = kwargs.get("y1title")
        if kwargs.get("y2title") and y2title is not None:
            y2title = kwargs.get("y2title")
        # Set the x-axis title, if suppiled.
        if isinstance(kwargs, dict) and "xtitle" in kwargs:
            xtitle = kwargs["xtitle"]
        # If the data was normalized, set the title to reflect this.
        if normalize:
            y1title = None
            y2title = None
            y3title = None
            title = f"{title} - Normalized" if title else "Normalized"

        # Now update the layout of the complete figure.
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                xanchor="right",
                y=1.02,
                x=0.95,
                bgcolor=(
                    "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
                ),
                font=dict(size=12),
            ),
            yaxis=(
                dict(
                    ticklen=0,
                    side="right",
                    showline=True,
                    mirror=True,
                    title=dict(text=y1title, standoff=30, font=dict(size=16)),
                    tickfont=dict(size=14),
                    anchor="x",
                    gridcolor="rgba(128,128,128,0.3)",
                )
                if y1title
                else None
            ),
            yaxis2=(
                dict(
                    overlaying="y",
                    side="left",
                    ticklen=0,
                    showgrid=False,
                    title=dict(
                        text=y2title if y2title else None,
                        standoff=10,
                        font=dict(size=16),
                    ),
                    tickfont=dict(size=14),
                    anchor="x",
                )
                if y2title
                else None
            ),
            yaxis3=(
                dict(
                    overlaying="y",
                    side="left",
                    ticklen=0,
                    position=0,
                    showgrid=False,
                    showticklabels=True,
                    title=(
                        dict(text=y3title, standoff=10, font=dict(size=16))
                        if y3title
                        else None
                    ),
                    tickfont=dict(size=12, color="rgba(128,128,128,0.9)"),
                    anchor="free",
                )
                if y3title
                else None
            ),
            xaxis=dict(
                ticklen=0,
                showgrid=True,
                showline=True,
                mirror=True,
                title=(
                    dict(text=xtitle, standoff=30, font=dict(size=16))
                    if xtitle
                    else None
                ),
                gridcolor="rgba(128,128,128,0.3)",
                domain=[0.095, 0.95] if y3title else None,
            ),
            margin=(
                dict(r=25, l=25, b=75 if xtitle else 30) if normalize is False else None
            ),
            font=dict(color=text_color),
            autosize=True,
            dragmode="pan",
        )
        if kwargs.get("layout_kwargs"):
            fig.update_layout(kwargs.get("layout_kwargs"))
        if kwargs.get("title"):
            fig.set_title(str(kwargs.get("title")))

        content = fig.to_plotly_json()

        return fig, content

    @staticmethod
    def economy_survey_bls_series(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """经济调查 BLS 系列图表。

        Parameters
        ----------
        data: Optional[Union[DataFrame, List[Data]]]
            父级结果的筛选子集。
        target_symbol: Optional[str]
            要绘制的目标代码。通过用逗号分隔来绘制多个代码。最多 10 个代码。
        target_col: Optional[str]
            要绘制的目标列。默认值为 'value'。
        plot_type: Literal["line", "bar"]
            要显示的图表类型。默认值为 'line'，除非数据非常小。
        normalize: bool
            在显示之前归一化数据。默认值为 False。
        title: Optional[str]
            图表的标题。
        xtitle: Optional[str]
            x 轴的标题。
        ytitle: Optional[str]
            y 轴的标题。
        bar_kwargs: Optional[dict]
            应用于 `fig.add_bar` 的其他关键字参数。
        scatter_kwargs: Optional[dict]
            应用于 `fig.add_scatter` 的其他关键字参数。
        layout_kwargs: Optional[dict]
            应用于 `fig.update_layout` 的其他关键字参数。
        """
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.generic_charts import bar_chart, line_chart
        from openbb_charting.charts.helpers import (
            z_score_standardization,
        )
        from openbb_core.app.utils import basemodel_to_df
        from pandas import DataFrame

        provider = kwargs.get("provider")

        if provider != "bls":
            raise RuntimeError(
                f"此图表方法不支持 {provider}. 支持的提供商: bls."
            )

        _data = (
            kwargs.pop("data", None)
            if "data" in kwargs and kwargs["data"] is not None
            else kwargs.get("obbject_item")
        )
        df = DataFrame()

        if isinstance(_data, DataFrame) and not _data.empty:
            df = _data.reset_index() if _data.index.name == "date" else _data
        else:
            try:
                df = basemodel_to_df(_data, index=None)  # type: ignore
            except Exception as e:
                raise RuntimeError("无法处理提供的数据。") from e

        if df.empty or len(df) < 2:
            raise RuntimeError("未找到要绘制的数据。")

        cols = df.columns.to_list()
        target_col = kwargs.get("target_col", "value")
        if target_col not in cols:
            raise RuntimeError(f"数据中未找到列 '{target_col}'。")

        new_df = df.pivot(columns="symbol", values=target_col, index="date")
        target_symbols = kwargs.get("target_symbol", "").split(",")[:10]  # type: ignore

        if not target_symbols or len(target_symbols) == 0 or target_symbols[0] == "":
            target_symbols = new_df.columns.to_list()[:10]

        metadata = kwargs["extra"].get("results_metadata", {})  # type: ignore
        ytitle = kwargs.get("ytitle", "")

        new_df = new_df.filter(target_symbols, axis=1)

        if "percent" in target_col.lower():  # type: ignore
            ytitle = (
                ytitle
                if ytitle
                else target_col.replace("change_percent_", "").replace("M", " Month") + " Change (%)"  # type: ignore
            )
            new_df = new_df.apply(lambda x: x * 100)
        elif "change" in target_col.lower() and "percent" not in target_col.lower():  # type: ignore
            ytitle = (
                ytitle if ytitle else target_col.replace("change_", "").replace("M", " Month") + " Change"  # type: ignore
            )

        title_map: dict = {}
        for symbol in target_symbols:
            if symbol not in new_df.columns:
                continue
            survey_name = metadata.get(symbol, {}).get("survey_name", symbol)  # type: ignore
            series_title = metadata.get(symbol, {}).get("series_title", symbol)  # type: ignore

            if survey_name != series_title:
                title_map[symbol] = f"{survey_name} \n    {series_title}"

        normalize = kwargs.get("normalize", False)
        same_axis = kwargs.get("same_axis", False)

        if normalize:
            new_df = new_df.apply(z_score_standardization)
            same_axis = True
            if ytitle:
                ytitle = f"Normalized {ytitle.replace('(%)', '')}"  # type: ignore

        plot_type = kwargs.get("plot_type")

        if plot_type is None:
            plot_type = (
                "line" if (len(new_df.index) > 36 and len(new_df.columns.to_list()) >= 1) else "bar"  # type: ignore
            )

        layout_kwargs: dict = kwargs.pop("layout_kwargs", {})  # type: ignore
        scatter_kwargs: dict = kwargs.pop("scatter_kwargs", {})  # type: ignore
        bar_kwargs: dict = kwargs.pop("bar_kwargs", {})  # type: ignore
        hovertemplate = scatter_kwargs.pop("hovertemplate", None)  # type: ignore
        trace_titles = {
            symbol: metadata.get(symbol, {})
            .get("series_title", symbol)
            .replace(",", " -")
            for symbol in target_symbols
        }
        new_df.columns = [trace_titles.get(col, col) for col in new_df.columns]
        scatter_kwargs["hovertemplate"] = (  # type: ignore
            hovertemplate if hovertemplate else "%{fullData.name}:%{y}<extra></extra>"
        )

        if len(target_symbols) == 1:
            title = title_map.get(target_symbols[0], target_symbols[0])
            fig = (
                line_chart(
                    data=new_df,
                    title=title,
                    ytitle=ytitle,
                    y=list(trace_titles.values()),
                    scatter_kwargs=scatter_kwargs,
                    layout_kwargs=layout_kwargs,
                    **kwargs,
                )
                if plot_type == "line"
                else bar_chart(
                    data=new_df,
                    title=title,
                    ytitle=ytitle,
                    x=new_df.index,  # type: ignore
                    y=list(trace_titles.values()),
                    layout_kwargs=layout_kwargs,
                    bar_kwargs=bar_kwargs,
                    **kwargs,
                )
            )
        else:
            survey_name = metadata.get(target_symbols[0], {}).get("survey_name", target_symbols[0]).split("\n")[0].strip()  # type: ignore
            _t = kwargs.pop("title", None)
            title = _t if _t else f"{survey_name} - {ytitle}" if ytitle else survey_name
            fig = (
                line_chart(
                    data=new_df,
                    y=list(trace_titles.values()),
                    title=title,
                    ytitle=ytitle,
                    same_axis=same_axis,
                    normalize=False,
                    scatter_kwargs=scatter_kwargs,
                    layout_kwargs=layout_kwargs,
                    **kwargs,
                )
                if plot_type == "line"
                else bar_chart(
                    data=new_df,
                    title=title,
                    ytitle=ytitle,
                    x=new_df.index,  # type: ignore
                    y=list(trace_titles.values()),
                    layout_kwargs=layout_kwargs,
                    bar_kwargs=bar_kwargs,
                    **kwargs,
                )
            )

        fig.update_layout(
            margin=dict(b=20),
            legend=dict(
                orientation="h",
                yanchor="top",
                xanchor="left",
                y=-0.075,
                x=0,
                font=dict(size=12),
            ),
        )
        content = fig.to_plotly_json()

        return fig, content  # type: ignore

    @staticmethod
    def economy_shipping_chokepoint_info(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """海上咽喉要道信息图表。"""
        # pylint: disable=import-outside-toplevel

        provider = kwargs.get("provider")

        if provider != "imf":
            raise RuntimeError(
                f"此图表方法不支持 {provider}. 支持的提供商: imf."
            )

        try:
            from openbb_imf.views.maritime_chokepoint_info import (
                plot_chokepoint_annual_avg_vessels,
            )
        except Exception as e:
            raise RuntimeError("无法导入所需的模块。") from e

        theme = (
            kwargs.get("extra_params", {}).get("theme")
            or kwargs.get("theme")
            or getattr(kwargs["charting_settings"], "chart_style", "dark")
        )
        data = (
            kwargs.pop("data", None)
            if "data" in kwargs and kwargs["data"] is not None
            else kwargs.get("obbject_item")
        )
        fig = plot_chokepoint_annual_avg_vessels(data, theme=theme)  # type: ignore
        fig.update_layout(
            margin=dict(l=25, r=25, t=50, b=0),
        )
        content = fig.to_plotly_json()

        content["config"] = dict(responsive=False)

        return fig, content

    @staticmethod
    def economy_shipping_port_info(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """港口信息图表。"""
        # pylint: disable=import-outside-toplevel

        provider = kwargs.get("provider")

        if provider != "imf":
            raise RuntimeError(
                f"此图表方法不支持 {provider}. 支持的提供商: imf."
            )

        try:
            from openbb_imf.views.port_info import (
                plot_port_info_map,
            )
        except Exception as e:
            raise RuntimeError("无法导入所需的模块。") from e

        data = (
            kwargs.pop("data", None)
            if "data" in kwargs and kwargs["data"] is not None
            else kwargs.get("obbject_item")
        )
        fig = plot_port_info_map(data)  # type: ignore
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
        )
        content = fig.to_plotly_json()

        content["config"] = dict(
            responsive=False,
            displayModeBar=False,
            dragMode="pan",
            doubleClick="reset",
        )

        return fig, content
