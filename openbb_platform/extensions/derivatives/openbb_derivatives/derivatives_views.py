"""衍生品扩展的视图。"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure


class DerivativesViews:
    """衍生品视图。"""

    @staticmethod
    def derivatives_futures_historical(  # noqa: PLR0912
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """获取衍生品历史价格图表。"""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.price_historical import price_historical

        kwargs.update({"candles": False, "same_axis": False})

        return price_historical(**kwargs)

    @staticmethod
    def derivatives_futures_curve(  # noqa: PLR0912
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """期货曲线图。所有参数都是可选的，并且是 kwargs。
        参数可以通过输入嵌套字典到 'chart_params' 键，直接从函数端点访问。

        从 API 中，`chart_params` 必须作为 JSON 在请求体中与 `extra_params` 一起传递。

        如果在请求后使用图表，参数直接作为 `key=value` 对传递给 `charting.to_chart` 或 `charting.show` 方法。

        Parameters
        ----------
        data : Optional[Union[List[Data], DataFrame]]
            图表数据。必填字段为：'expiration' 和 'price'。
            多个日期将绘制在同一图表上。
            如果未提供，将使用原始 OBBject.results。
            如果提供了 DataFrame，则预期为扁平数据，没有设置索引。
        title: Optional[str]
            图表标题。如果未提供，将使用默认标题。
        colors: Optional[List[str]]
            用于图表的颜色列表。如果未提供，将使用默认配色方案。
            颜色应为十六进制格式或命名的 Plotly 颜色。无效颜色将引发 Plotly 错误。
        layout_kwargs: Optional[Dict[str, Any]]
            图表的其他布局参数，直接传递给 `figure.update_layout` 以在输出前使用。
            有关可用选项，请参阅 Plotly 文档。

        Returns
        -------
        Tuple[OpenBBFigure, Dict[str, Any]]
            包含 OpenBBFigure 对象和 JSON 序列化内容的元组。
            如果使用 API，则仅返回 JSON 内容。

        Examples
        --------
        ```python
        from openbb import obb
        data = obb.derivatives.futures.curve(symbol="vx", provider="cboe", date=["2020-03-31", "2024-06-28"], chart=True)
        data.show()
        ```

        使用自定义配色方案和标题从相同数据重绘图表：

        ```python
        data.charting.to_chart(colors=["green", "red"], title="VIX Futures Curve - 2020 vs. 2024")
        ```
        """
        # pylint: disable=import-outside-toplevel
        from openbb_charting.core.chart_style import ChartStyle
        from openbb_charting.core.openbb_figure import OpenBBFigure
        from openbb_charting.styles.colors import LARGE_CYCLER
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.abstract.data import Data
        from pandas import DataFrame, to_datetime

        data = kwargs.get("data")
        symbol = kwargs.get("standard_params", {}).get("symbol", "")
        df: DataFrame = DataFrame()
        if data:
            if isinstance(data, DataFrame) and not data.empty:  # noqa: SIM108
                df = data
            elif isinstance(data, (list, Data)):
                df = DataFrame([d.model_dump(exclude_none=True, exclude_unset=True) for d in data])  # type: ignore
            else:
                pass
        else:
            df = DataFrame(
                [d.model_dump(exclude_none=True, exclude_unset=True) for d in kwargs["obbject_item"]]  # type: ignore
                if isinstance(kwargs.get("obbject_item"), list)
                else kwargs["obbject_item"].model_dump(exclude_none=True, exclude_unset=True)  # type: ignore
            )

        if df.empty:
            raise OpenBBError("错误: 没有要绘制的数据。")

        if "expiration" not in df.columns:
            raise OpenBBError("在数据中未找到 expiration 字段。")

        if "price" not in df.columns:
            raise ValueError("在数据中未找到 price 字段。")

        provider = kwargs.get("provider", "")

        if provider != "deribit":
            df["expiration"] = df["expiration"].apply(to_datetime).dt.strftime("%b-%Y")

        if (
            provider == "cboe"
            and "date" in df.columns
            and len(df["date"].unique()) > 1
            and "symbol" in df.columns
        ):
            df["expiration"] = df.symbol

        # Use a complete list of expirations to categorize the x-axis across all dates.
        expirations = df["expiration"].unique().tolist()

        # Use the supplied colors, if any.
        colors = kwargs.get("colors", [])
        if not colors:
            colors = LARGE_CYCLER
        color_count = 0

        figure = OpenBBFigure().create_subplots(shared_xaxes=True)
        figure.update_layout(ChartStyle().plotly_template.get("layout", {}))
        text_color = "white" if ChartStyle().plt_style == "dark" else "black"

        def create_fig(figure, df, dates, color_count):
            """Create a scatter for each date in the data."""
            for date in dates:
                color = colors[color_count % len(colors)]
                plot_df = (
                    df[df["date"].astype(str) == date].copy()
                    if "date" in df.columns
                    else df.copy()
                )
                plot_df = plot_df.drop(
                    columns=["date"] if "date" in plot_df.columns else []
                ).rename(columns={"expiration": "Expiration", "price": "Price"})
                figure.add_scatter(
                    x=plot_df["Expiration"],
                    y=plot_df["Price"],
                    mode="lines+markers",
                    name=date,
                    line=dict(width=3, color=color),
                    marker=dict(size=10, color=color),
                    hovertemplate=(
                        "Expiration: %{x}<br>Price: $%{y}<extra></extra>"
                        if len(dates) == 1
                        else "%{fullData.name}<br>Expiration: %{x}<br>Price: $%{y}<extra></extra>"
                    ),
                )
                color_count += 1
            return figure, color_count

        dates = (
            df.date.astype(str).unique().tolist()
            if "date" in df.columns
            else ["Current"]
        )

        if provider == "deribit" and "hours_ago" in df.columns:
            dates = [
                str(d) + " Hours Ago" if d > 0 else "Current"
                for d in df["hours_ago"].unique().tolist()
            ]
            df["date"] = df["hours_ago"].apply(
                lambda x: str(x) + " Hours Ago" if x > 0 else "Current"
            )
        figure, color_count = create_fig(figure, df, dates, color_count)

        # Set the title for the chart
        title: str = ""
        if provider == "cboe":
            vx_eod_symbols = ["vx", "vix", "vx_eod", "^vix"]
            title = (
                "VIX EOD Futures Curve"
                if symbol.lower() in vx_eod_symbols
                else "VIX Mid-Morning TWAP Futures Curve"
            )
            if len(dates) == 1 and dates[0] != "Current":
                title = f"{title} for {dates[0]}"
        else:
            title = f"{symbol.upper()} Futures Curve"

        # Use the supplied title, if any.
        title = kwargs.get("title", title)

        # Update the layout of the figure.
        figure.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20)),
            xaxis=dict(
                title="",
                ticklen=0,
                showgrid=False,
                type="category",
                categoryorder="array",
                categoryarray=expirations,
            ),
            yaxis=dict(
                title="Price ($)",
                ticklen=0,
                showgrid=True,
                gridcolor="rgba(128,128,128,0.3)",
            ),
            legend=dict(
                orientation="v",
                yanchor="top",
                xanchor="right",
                y=0.95,
                x=0,
                xref="paper",
                font=dict(size=12),
                bgcolor=(
                    "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
                ),
            ),
            margin=dict(
                b=10,
                t=10,
            ),
        )

        layout_kwargs = kwargs.get("layout_kwargs", {})
        if layout_kwargs:
            figure.update_layout(layout_kwargs)

        content = figure.show(external=True).to_plotly_json()

        return figure, content

    @staticmethod
    def derivatives_options_surface(  # noqa: PLR0912
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """期权曲面图。所有参数都是可选的，并且是 kwargs。

        数据过滤由 POST 请求函数完成。

        不建议使用 `to_chart` 方法重绘此图表，
        相反，请使用所需的参数向 `/derivatives/options/surface` 端点发布新请求。

        公开的参数有：

        - `title`: 图表的标题。
        - `xtitle`: x 轴的标题。
        - `ytitle`: y 轴的标题。
        - `ztitle`: z 轴的标题。
        - `colorscale`: 用于图表的色标。
        - `layout_kwargs`: 在输出前传递给 `fig.update_layout` 的附加字典。
        """
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.generic_charts import surface3d
        from pandas import DataFrame

        cols_map = {
            "expiration": "Expiration",
            "strike": "Strike",
            "option_type": "Type",
            "dte": "DTE",
            "implied_volatility": "IV",
            "gamma": "Gamma",
            "GEX": "GEX",
            "delta": "Delta",
            "DEX": "DEX",
            "theta": "Theta",
            "vega": "Vega",
            "rho": "Rho",
            "open_interest": "OI",
            "volume": "Volume",
        }

        data = kwargs["obbject_item"]
        df = DataFrame(data)
        df = df.rename(columns=cols_map)
        target = kwargs.get("target", "implied_volatility")
        option_type = kwargs.get("option_type", "otm").lower()
        oi = kwargs.get("oi", False)
        volume = kwargs.get("volume", False)

        label_dict = {"calls": "Call", "puts": "Put", "otm": "OTM", "itm": "ITM"}

        label = (
            f" {label_dict[option_type]} {cols_map.get(target, '')} Surface"
            if not oi
            else f"{label_dict[option_type]} {cols_map.get(target, '')} With Open Interest"
        )
        label = label + " Excluding Untraded Contracts" if volume else label

        title = kwargs.get("title") or label
        theme = kwargs.get("theme")
        colorscale = kwargs.get("colorscale")
        layout_kwargs = kwargs.get("layout_kwargs")
        z_title = kwargs.get("ztitle") or cols_map.get(target, "Value")
        x_title = kwargs.get("xtitle") or "DTE"
        y_title = kwargs.get("ytitle") or "Strike"

        X = df.DTE
        Y = df.Strike
        Z = df[cols_map[target]]

        figure = surface3d(
            X=X,
            Y=Y,
            Z=Z,  # type: ignore
            xtitle=x_title,
            ytitle=y_title,
            ztitle=z_title,
            layout_kwargs=layout_kwargs,
            colorscale=colorscale,
            theme=theme,
            title=title,
        )

        content = figure.show(external=True).to_plotly_json()  # type: ignore

        return figure, content  # type: ignore
