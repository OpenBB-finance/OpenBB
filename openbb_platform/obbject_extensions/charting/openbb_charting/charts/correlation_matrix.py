"""Correlation Matrix Chart."""

from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from plotly.graph_objs import Figure  # noqa
    from openbb_charting.core.openbb_figure import OpenBBFigure  # noqa


def correlation_matrix(  # noqa: PLR0912
    **kwargs,
) -> tuple[Union["OpenBBFigure", "Figure"], dict[str, Any]]:
    """Correlation Matrix Chart."""
    # pylint: disable=import-outside-toplevel
    from numpy import ones_like, triu  # noqa
    from openbb_core.app.utils import basemodel_to_df  # noqa
    from openbb_charting.core.openbb_figure import OpenBBFigure
    from openbb_charting.core.chart_style import ChartStyle
    from plotly.graph_objs import Figure, Heatmap, Layout
    from pandas import DataFrame

    if "data" in kwargs and isinstance(kwargs["data"], DataFrame):
        corr = kwargs["data"]
    elif "data" in kwargs and isinstance(kwargs["data"], list):
        corr = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))  # type: ignore
    else:
        corr = basemodel_to_df(
            kwargs["obbject_item"], index=kwargs.get("index", "date")  # type: ignore
        )
    if (
        "symbol" in corr.columns
        and len(corr.symbol.unique()) > 1
        and "close" in corr.columns
    ):
        corr = corr.pivot(
            columns="symbol",
            values="close",
        )

    method = kwargs.get("method") or "pearson"
    corr = corr.corr(method=method, numeric_only=True)

    X = corr.columns.to_list()
    x_replace = X[-1]
    Y = X.copy()
    y_replace = Y[0]
    X = [x if x != x_replace else "" for x in X]
    Y = [y if y != y_replace else "" for y in Y]
    mask = triu(ones_like(corr, dtype=bool))
    df = corr.mask(mask)
    title = kwargs.get("title") or "Asset Correlation Matrix"
    text_color = "white" if ChartStyle().plt_style == "dark" else "black"
    colorscale = kwargs.get("colorscale") or "RdBu"

    heatmap = Heatmap(
        z=df,
        x=X,
        y=Y,
        xgap=1,
        ygap=1,
        colorscale=colorscale,
        colorbar=dict(
            orientation="v",
            x=0.8,
            y=0.5,
            xanchor="left",
            yanchor="middle",
            xref="container",
            yref="paper",
            len=0.66,
            bgcolor="rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)",
        ),
        text=df.fillna(""),
        texttemplate="%{text:.4f}",
        hoverongaps=False,
        hovertemplate="%{x} - %{y} : %{z:.4f}<extra></extra>",
    )
    layout = Layout(
        title=title,
        title_x=0.5,
        xaxis=dict(
            showgrid=False,
            showline=False,
            ticklen=0,
            domain=[0.03, 1],
            tickangle=90,
            automargin=False,
        ),
        yaxis=dict(
            showgrid=False,
            side="left",
            autorange="reversed",
            showline=False,
            ticklen=0,
            automargin="height+width+left",
            tickmode="auto",
        ),
        margin=dict(l=10, r=0, t=0, b=10),
        dragmode="pan",
    )
    fig = Figure(data=[heatmap], layout=layout)
    figure = OpenBBFigure(fig=fig)
    figure.update_layout(
        font=dict(color=text_color),
        paper_bgcolor=(
            "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
        ),
        plot_bgcolor=(
            "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
        ),
    )
    layout_kwargs = kwargs.get("layout_kwargs", {})

    if layout_kwargs:
        figure.update_layout(**layout_kwargs)

    content = figure.show(external=True).to_plotly_json()  # type: ignore

    return figure, content
