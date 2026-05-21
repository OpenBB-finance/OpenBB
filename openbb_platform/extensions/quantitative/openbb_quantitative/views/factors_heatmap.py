"""Factor-regression coefficient/p-value heatmap chart."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure  # noqa


_PVALUE_COLORSCALE = [
    [0.0, "blue"],
    [0.05, "cyan"],
    [0.10, "orange"],
    [0.25, "red"],
    [1.0, "darkred"],
]


def factors_heatmap(
    **kwargs,
) -> tuple["OpenBBFigure", dict[str, Any]]:
    """Coefficient heatmap colored by p-value, across regression look-back periods.

    Consumes the row schema produced by `POST /quantitative/factors`:
    one row per (`period`, `factor`) with `coefficient` and `p_value` columns.
    Cells display the coefficient as text and shade by the p-value on a
    5-stop scale (low p-value = cool colors, high p-value = warm colors).
    """
    # pylint: disable=import-outside-toplevel
    from openbb_charting.core.chart_style import ChartStyle
    from openbb_charting.core.openbb_figure import OpenBBFigure
    from openbb_core.app.utils import basemodel_to_df
    from pandas import DataFrame
    from plotly.graph_objs import Figure, Heatmap, Layout

    if "data" in kwargs and isinstance(kwargs["data"], DataFrame):
        df = kwargs["data"]
    elif "data" in kwargs and isinstance(kwargs["data"], list):
        df = basemodel_to_df(kwargs["data"], index=None)
    else:
        df = basemodel_to_df(kwargs["obbject_item"], index=None)

    required = {"period", "factor", "coefficient", "p_value"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"factors_heatmap requires columns {sorted(required)}; missing"
            f" {sorted(missing)}."
        )

    pivoted = df.pivot_table(
        index="period",
        columns="factor",
        values=["coefficient", "p_value"],
        sort=False,
    )
    coef_df = pivoted["coefficient"]
    pval_df = pivoted["p_value"]

    x_labels = [str(c).replace("const", "Constant") for c in coef_df.columns]
    y_labels = list(coef_df.index)

    text_color = "white" if ChartStyle().plt_style == "dark" else "black"
    title = kwargs.get("title") or "Factor Regression Coefficients & P-Values"

    heatmap = Heatmap(
        z=pval_df.values,
        x=x_labels,
        y=y_labels,
        xgap=1,
        ygap=1,
        colorscale=_PVALUE_COLORSCALE,
        zmin=0.0,
        zmax=1.0,
        showscale=False,
        text=coef_df.values,
        texttemplate="%{text:.6f}",
        hoverongaps=False,
        hovertemplate=(
            "%{x} - %{y}<br>Coefficient: %{text:.6f}<br>"
            "P-Value: %{z:.6f}<extra></extra>"
        ),
    )
    layout = Layout(
        title_text=title,
        title_x=0.5,
        xaxis=dict(
            showgrid=False,
            showline=False,
            ticklen=5,
            tickangle=0,
            side="top",
            automargin=True,
        ),
        yaxis=dict(
            showgrid=False,
            side="left",
            autorange="reversed",
            showline=False,
            ticklen=5,
            automargin=True,
        ),
        dragmode="pan",
        font=dict(color=text_color),
        margin=dict(t=75, b=50, l=85, r=50),
    )

    fig = Figure(data=[heatmap], layout=layout)
    figure = OpenBBFigure(fig=fig)

    layout_kwargs = kwargs.get("layout_kwargs") or {}
    if layout_kwargs:
        figure.update_layout(**layout_kwargs)

    content = figure.show(external=True).to_plotly_json()

    return figure, content
