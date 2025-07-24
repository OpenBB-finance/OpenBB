"""Views for the Fixed Income Extension."""

from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from openbb_core.provider.abstract.data import Data

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import (
        OpenBBFigure,
    )


class FixedIncomeViews:
    """FixedIncome Views."""

    @staticmethod
    def fixedincome_government_yield_curve(  # noqa: PLR0912
        **kwargs,
    ) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Government Yield Curve Chart."""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.helpers import (
            duration_sorter,
        )
        from openbb_charting.core.chart_style import ChartStyle
        from openbb_charting.core.openbb_figure import OpenBBFigure
        from openbb_charting.styles.colors import LARGE_CYCLER
        from openbb_core.app.utils import basemodel_to_df
        from pandas import DataFrame

        data = kwargs.get("data")
        df: DataFrame = DataFrame()
        if data:
            if isinstance(data, DataFrame) and not data.empty:  # noqa: SIM108
                df = data
            elif isinstance(data, (list, Data)):
                df = basemodel_to_df(data, index=None)  # type: ignore
            else:
                pass
        else:
            df = DataFrame([d.model_dump() for d in kwargs["obbject_item"]])  # type: ignore

        if df.empty:
            raise ValueError("Error: No data to plot.")

        if "maturity" not in df.columns:
            raise ValueError("Error: Maturity column not found in the data.")

        if "rate" not in df.columns:
            raise ValueError("Error: Rate column not found in the data.")

        if "date" not in df.columns:
            raise ValueError("Error: Date column not found in the data.")

        provider = kwargs.get("provider")
        df["date"] = df["date"].astype(str)
        maturities = duration_sorter(df["maturity"].unique().tolist())
        countries: list = (
            df["country"].unique().tolist() if "country" in df.columns else []
        )

        # Use the supplied colors, if any.
        colors = kwargs.get("colors", [])
        if not colors:
            colors = LARGE_CYCLER
        color_count = 0

        figure = OpenBBFigure().create_subplots(shared_xaxes=True)
        figure.update_layout(ChartStyle().plotly_template.get("layout", {}))
        text_color = "white" if ChartStyle().plt_style == "dark" else "black"

        def create_fig(
            figure, dataframe, dates, color_count, country: Optional[str] = None
        ):
            """Create a scatter for each date in the data."""
            for date in dates:
                color = colors[color_count % len(colors)]
                plot_df = dataframe[dataframe["date"] == date].copy()
                plot_df.rate = plot_df.rate.astype(float).multiply(100).round(4)
                plot_df = plot_df.rename(columns={"rate": "Yield"})
                plot_df = (
                    plot_df.drop(columns=["date"])
                    .set_index("maturity")
                    .filter(items=maturities, axis=0)
                    .reset_index()
                )
                plot_df = plot_df.rename(columns={"index": "Maturity"})
                plot_df["Maturity"] = [
                    (d.split("_")[1] + " " + d.split("_")[0].title())
                    for d in plot_df["Maturity"]
                ]

                figure.add_scatter(
                    x=plot_df["Maturity"],
                    y=plot_df["Yield"],
                    mode="lines+markers",
                    name=(
                        f"{country.replace('_', ' ').title().replace('Ecb', 'ECB')} {date}"
                        if country
                        else date
                    ),
                    line=dict(width=3, color=color),
                    marker=dict(size=10, color=color),
                    hovertemplate=(
                        "Maturity: %{x}<br>Yield: %{y}<extra></extra>"
                        if len(dates) == 1 and not countries
                        else "%{fullData.name}<br>Maturity: %{x}<br>Yield: %{y}<extra></extra>"
                    ),
                )
                color_count += 1
            return figure, color_count

        if countries:
            for _country in countries:
                _df = df[df["country"] == _country]
                dates = _df.date.unique().tolist()
                figure, color_count = create_fig(
                    figure, _df, dates, color_count, _country
                )

        else:
            dates = df.date.unique().tolist()
            figure, color_count = create_fig(figure, df, dates, color_count)

        extra_params = kwargs.get("extra_params", {})
        extra_params = (
            extra_params if isinstance(extra_params, dict) else extra_params.__dict__
        )
        # Set the title for the chart
        country: str = ""
        if provider in ("federal_reserve", "fmp"):
            country = "United States"
        elif provider == "ecb":
            curve_type = (
                extra_params.get("yield_curve_type", "").replace("_", " ").title()
            )
            grade = extra_params.get("rating", "").replace("_", " ")
            grade = grade.upper() if grade == "aaa" else "All Ratings"
            country = f"Euro Area ({grade}) {curve_type}"
        elif provider == "fred":
            curve_type = extra_params.get("yield_curve_type", "")
            curve_type = (
                "Real Rates"
                if curve_type == "real"
                else curve_type.replace("_", " ").title()
            )
            country = f"United States {curve_type}"
        elif provider == "econdb":
            country = (
                ""
                if countries
                else (
                    extra_params.get("country", "")
                    .replace("_", " ")
                    .title()
                    .replace("Ecb", "ECB")
                    or "United States"
                )
            )

        country = country + " " if country else ""
        title = kwargs.get("title", "")
        if not title:
            title = f"{country}Yield Curve"
            if len(dates) == 1 and len(countries) == 1:
                title = f"{country} Yield Curve - {dates[0]}"
            elif countries:
                title = f"Yield Curve - {', '.join(countries).replace('_', ' ').title().replace('Ecb', 'ECB')}"

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
                title="Maturity",
                ticklen=10,
                ticks="outside",
                showgrid=False,
                type="category",
                categoryorder="array",
                categoryarray=(
                    [
                        (d.split("_")[1] + " " + d.split("_")[0].title())
                        for d in maturities
                    ]
                ),
                ticklabeloverflow="hide past domain",
            ),
            yaxis=dict(
                ticklen=0,
                showgrid=True,
                gridcolor="rgba(128,128,128,0.3)",
                side="left",
                ticklabelstandoff=10,
                ticksuffix=" %",
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
                t=20,
                l=30,
                r=0,
            ),
        )

        layout_kwargs = kwargs.get("layout_kwargs", {})
        if layout_kwargs:
            figure.update_layout(layout_kwargs)

        content = figure.show(external=True).to_plotly_json()

        return figure, content
