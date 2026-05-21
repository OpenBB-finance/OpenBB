"""Stacked-area chart for the rolling factors endpoint."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure  # noqa


_PALETTE = [
    "#4c78a8",
    "#f58518",
    "#54a24b",
    "#e45756",
    "#72b7b2",
    "#eeca3b",
    "#b279a2",
    "#ff9da6",
    "#9d755d",
    "#bab0ac",
    "#a3cce9",
    "#ffbf79",
    "#88d27a",
    "#ff9d97",
    "#a0cbe8",
    "#d4a6c8",
    "#b8b0aa",
    "#cad6d4",
]
# Bands smaller than this fraction of the final-period total are unlabeled
# to prevent overlapping annotations on hairline-thin slivers.
_LABEL_MIN_SHARE = 0.015


def rolling_factors_line(
    **kwargs,
) -> tuple["OpenBBFigure", dict[str, Any]]:
    """Stacked-area chart of rolling factor betas over time.

    Consumes the row schema produced by `POST /quantitative/rolling/factors`:
    rows of (`date`, `factor`, `coefficient`, `t_statistic`). Each factor is
    drawn as a colored band; the total height at a date is the sum of factor
    betas. Factors are sorted by mean absolute beta with the dominant
    exposure at the base. Bands are labeled inline at the right edge of the
    chart, so there is no separate legend cluttering the layout.

    The intercept (`const`) is dropped by default; pass ``include_intercept=True``
    to keep it.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_charting.core.openbb_figure import OpenBBFigure
    from openbb_core.app.utils import basemodel_to_df
    from pandas import DataFrame
    from plotly.graph_objs import Figure, Layout, Scatter

    if "data" in kwargs and isinstance(kwargs["data"], DataFrame):
        df = kwargs["data"]
    elif "data" in kwargs and isinstance(kwargs["data"], list):
        df = basemodel_to_df(kwargs["data"], index=None)
    else:
        df = basemodel_to_df(kwargs["obbject_item"], index=None)

    required = {"date", "factor", "coefficient"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"rolling_factors_line requires columns {sorted(required)};"
            f" missing {sorted(missing)}."
        )

    include_intercept = bool(kwargs.get("include_intercept", False))
    if not include_intercept:
        df = df[df["factor"] != "const"]

    wide = df.pivot_table(
        index="date", columns="factor", values="coefficient", sort=False
    ).sort_index()
    order = wide.abs().mean(axis=0).sort_values(ascending=False).index.tolist()
    wide = wide[order]

    title = kwargs.get("title") or "Rolling Factor Betas (Stacked)"

    last_values = wide.iloc[-1]
    total_at_last = float(last_values.abs().sum()) or 1.0
    cum = 0.0
    annotations = []
    for i, factor in enumerate(order):
        val = float(last_values[factor])
        midpoint = cum + val / 2.0
        cum += val
        if abs(val) / total_at_last < _LABEL_MIN_SHARE:
            continue
        annotations.append(
            dict(
                x=wide.index[-1],
                y=midpoint,
                xref="x",
                yref="y",
                text=f"<b>{'Intercept' if factor == 'const' else factor}</b>",
                font=dict(color=_PALETTE[i % len(_PALETTE)], size=12),
                xanchor="left",
                yanchor="middle",
                xshift=8,
                showarrow=False,
            )
        )

    traces = []
    for i, factor in enumerate(order):
        traces.append(
            Scatter(
                name="Intercept" if factor == "const" else factor,
                x=wide.index.to_numpy(),
                y=wide[factor].to_numpy(),
                mode="lines",
                stackgroup="one",
                line=dict(width=0.5, color=_PALETTE[i % len(_PALETTE)]),
                fillcolor=_PALETTE[i % len(_PALETTE)],
                hovertemplate=(
                    f"{factor}<br>%{{x|%Y-%m-%d}}<br>Beta: %{{y:.4f}}<extra></extra>"
                ),
                showlegend=False,
            )
        )

    layout = Layout(
        title_text=title,
        title_x=0.5,
        hovermode="x unified",
        showlegend=False,
        xaxis=dict(showgrid=False, title="Window End"),
        yaxis=dict(
            title="Cumulative Beta",
            showgrid=True,
            gridcolor="rgba(128,128,128,0.2)",
            zeroline=True,
            zerolinewidth=1,
        ),
        margin=dict(t=70, b=60, l=80, r=110),
        annotations=annotations,
        dragmode="pan",
    )

    fig = Figure(data=traces, layout=layout)
    figure = OpenBBFigure(fig=fig)

    layout_kwargs = kwargs.get("layout_kwargs") or {}
    if layout_kwargs:
        figure.update_layout(**layout_kwargs)

    content = figure.show(external=True).to_plotly_json()
    return figure, content
