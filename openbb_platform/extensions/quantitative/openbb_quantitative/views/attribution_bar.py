"""Stacked horizontal bar chart for the attribution endpoint."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure  # noqa


_ALPHA_LABEL = "Alpha"
_RESIDUAL_LABEL = "Residual"


def attribution_bar(
    **kwargs,
) -> tuple["OpenBBFigure", dict[str, Any]]:
    """Stacked horizontal bars of per-factor return share per period.

    Consumes the row schema produced by `POST /quantitative/attribution`:
    rows of (`period`, `factor`, `contribution`, `share`). Bars use `share`
    so every period spans roughly -100% to +100% on the same x-axis;
    the absolute contribution is shown in the segment text and hover.
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

    required = {"period", "factor", "contribution", "share"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"attribution_bar requires columns {sorted(required)};"
            f" missing {sorted(missing)}."
        )

    periods = list(dict.fromkeys(df["period"].tolist()))
    all_factors = list(dict.fromkeys(df["factor"].tolist()))
    fixed_tail = [f for f in (_ALPHA_LABEL, _RESIDUAL_LABEL) if f in all_factors]
    leading = [f for f in all_factors if f not in fixed_tail]
    factor_order = leading + fixed_tail

    share_wide = (
        df.pivot_table(index="period", columns="factor", values="share", sort=False)
        .reindex(index=periods)
        .reindex(columns=factor_order)
        .fillna(0.0)
    )
    contrib_wide = (
        df.pivot_table(
            index="period", columns="factor", values="contribution", sort=False
        )
        .reindex(index=periods)
        .reindex(columns=factor_order)
        .fillna(0.0)
    )

    title = kwargs.get("title") or "Return Attribution (Share of Period Return)"
    traces = []
    for factor in factor_order:
        shares = share_wide[factor].to_numpy()
        contribs = contrib_wide[factor].to_numpy()
        # Show the absolute contribution as cell text when it's a meaningful slice.
        text = [f"{c:+.4f}" if abs(s) > 0.03 else "" for s, c in zip(shares, contribs)]
        traces.append(
            Bar(
                name=factor,
                x=shares,
                y=periods,
                orientation="h",
                text=text,
                textposition="inside",
                insidetextanchor="middle",
                customdata=contribs.reshape(-1, 1),
                hovertemplate=(
                    f"{factor}<br>Period: %{{y}}<br>"
                    "Share: %{x:.1%}<br>"
                    "Contribution: %{customdata[0]:+.6f}<extra></extra>"
                ),
            )
        )

    layout = Layout(
        title_text=title,
        title_x=0.5,
        barmode="relative",
        xaxis=dict(
            tickformat=".0%",
            zeroline=True,
            zerolinewidth=2,
            showgrid=False,
            title="Share of Period Return",
        ),
        yaxis=dict(autorange="reversed", showgrid=False, title=""),
        legend=dict(
            orientation="h",
            y=-0.15,
            yanchor="top",
            x=0.5,
            xanchor="center",
        ),
        margin=dict(t=60, b=80, l=80, r=40),
        dragmode="pan",
    )

    fig = Figure(data=traces, layout=layout)
    figure = OpenBBFigure(fig=fig)

    layout_kwargs = kwargs.get("layout_kwargs") or {}
    if layout_kwargs:
        figure.update_layout(**layout_kwargs)

    content = figure.show(external=True).to_plotly_json()
    return figure, content
