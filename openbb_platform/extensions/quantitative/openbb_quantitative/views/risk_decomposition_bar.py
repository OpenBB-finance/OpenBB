"""Stacked horizontal bar chart for the risk_decomposition endpoint."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure  # noqa


_RESIDUAL_LABEL = "Residual"


def risk_decomposition_bar(
    **kwargs,
) -> tuple["OpenBBFigure", dict[str, Any]]:
    """Stacked bars of per-factor variance share for each look-back period.

    Consumes the row schema produced by `POST /quantitative/risk_decomposition`:
    one row per (`period`, `factor`) with `share`. Renders one horizontal bar per
    period; each segment is a factor's share of Var(target), with the residual
    segment last. Bars sum to 1.0 by construction.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_charting.core.openbb_figure import OpenBBFigure
    from openbb_core.app.utils import basemodel_to_df
    from pandas import DataFrame
    from plotly.graph_objs import Bar, Figure, Layout

    if "data" in kwargs and isinstance(kwargs["data"], DataFrame):
        df = kwargs["data"]
    elif "data" in kwargs and isinstance(kwargs["data"], list):
        df = basemodel_to_df(kwargs["data"], index=None)
    else:
        df = basemodel_to_df(kwargs["obbject_item"], index=None)

    required = {"period", "factor", "share"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"risk_decomposition_bar requires columns {sorted(required)}; missing"
            f" {sorted(missing)}."
        )

    periods = list(dict.fromkeys(df["period"].tolist()))
    non_residual = [f for f in dict.fromkeys(df["factor"]) if f != _RESIDUAL_LABEL]
    factor_order = non_residual + [_RESIDUAL_LABEL]

    share = (
        df.pivot_table(index="period", columns="factor", values="share", sort=False)
        .reindex(index=periods)
        .reindex(columns=factor_order)
        .fillna(0.0)
    )

    title = kwargs.get("title") or "Risk Decomposition (Share of Variance)"
    traces = [
        Bar(
            name=factor,
            x=share[factor].to_numpy(),
            y=periods,
            orientation="h",
            hovertemplate=(
                f"{factor}<br>Period: %{{y}}<br>Share: %{{x:.2%}}<extra></extra>"
            ),
            text=[f"{v:.1%}" for v in share[factor].to_numpy()],
            textposition="inside",
            insidetextanchor="middle",
        )
        for factor in factor_order
    ]

    layout = Layout(
        title_text=title,
        title_x=0.5,
        barmode="stack",
        xaxis=dict(
            tickformat=".0%",
            range=[0, 1],
            zeroline=False,
            showgrid=False,
        ),
        yaxis=dict(autorange="reversed", showgrid=False),
        legend=dict(orientation="h", y=-0.15, yanchor="top", x=0.5, xanchor="center"),
        margin=dict(t=60, b=60, l=80, r=40),
        dragmode="pan",
    )

    fig = Figure(data=traces, layout=layout)
    figure = OpenBBFigure(fig=fig)

    layout_kwargs = kwargs.get("layout_kwargs") or {}
    if layout_kwargs:
        figure.update_layout(**layout_kwargs)

    content = figure.show(external=True).to_plotly_json()
    return figure, content
