"""Views for the Derivatives Extension."""

from typing import TYPE_CHECKING, Any, Dict, Tuple

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure


class DerivativesViews:
    """Derivatives Views."""

    @staticmethod
    def derivatives_futures_historical(  # noqa: PLR0912
        **kwargs,
    ) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Get Derivatives Price Historical Chart."""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.price_historical import price_historical

        return price_historical(**kwargs)

    @staticmethod
    def derivatives_futures_curve(  # noqa: PLR0912
        **kwargs,
    ) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Futures curve chart. All parameters are optional, and are kwargs.
        Parameters can be directly accessed from the function end point by
        entering as a nested dictionary to the 'chart_params' key.

        From the API, `chart_params` must be passed as a JSON in the request body with `extra_params`.

        If using the chart post-request, the parameters are passed directly
        as `key=value` pairs in the `charting.to_chart` or `charting.show` methods.

        Parameters
        ----------
        data : Optional[Union[List[Data], DataFrame]]
            Data for the chart. Required fields are: 'expiration' and 'price'.
            Multiple dates will be plotted on the same chart.
            If not supplied, the original OBBject.results will be used.
            If a DataFrame is supplied, flat data is expected, without a set index.
        title: Optional[str]
            Title for the chart. If not supplied, a default title will be used.
        colors: Optional[List[str]]
            List of colors to use for the chart. If not supplied, the default colorway will be used.
            Colors should be in hex format, or named Plotly colors. Invalid colors will raise a Plotly error.
        layout_kwargs: Optional[Dict[str, Any]]
            Additional layout parameters for the chart, passed directly to `figure.update_layout` before output.
            See Plotly documentation for available options.

        Returns
        -------
        Tuple[OpenBBFigure, Dict[str, Any]]
            Tuple with the OpenBBFigure object, and the JSON-serialized content.
            If using the API, only the JSON content will be returned.

        Examples
        --------
        ```python
        from openbb import obb
        data = obb.derivatives.futures.curve(symbol="vx", provider="cboe", date=["2020-03-31", "2024-06-28"], chart=True)
        data.show()
        ```

        Redraw the chart, from the same data, with a custom colorway and title:

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

        data = kwargs.get("data", None)
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
                [
                    d.model_dump(exclude_none=True, exclude_unset=True)  # type: ignore
                    for d in kwargs["obbject_item"]
                ]
                if isinstance(kwargs.get("obbject_item"), list)
                else kwargs["obbject_item"].model_dump(exclude_none=True, exclude_unset=True)  # type: ignore
            )

        if df.empty:
            raise OpenBBError("Error: No data to plot.")

        if "expiration" not in df.columns:
            raise OpenBBError("Expiration field not found in the data.")

        if "price" not in df.columns:
            raise ValueError("Price field not found in the data.")

        provider = kwargs.get("provider", "")

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
        elif provider == "yfinance":
            title = f"{symbol.upper()} Futures Curve"

        # Use the supplied title, if any.
        title = kwargs.get("title", title)

        # Update the layout of the figure.
        figure.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20)),
            plot_bgcolor=(
                "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
            ),
            paper_bgcolor=(
                "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
            ),
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
