"""Cboe open-interest and volume statistics chart."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from openbb_core.app.model.obbject import OBBject
    from openbb_core.provider.standard_models.options_chains import OptionsChainsData


def create_stats(
    data: OptionsChainsData,
    by: Literal["strike", "expiration"] = "expiration",
    metric: Literal["oi", "volume"] = "oi",
    date: str | None = None,
    unit: Literal["value", "percent", "pcr"] = "value",
    **kwargs,
) -> OBBject:
    """Chart open interest or volume by strike or expiration.

    Parameters
    ----------
    data : OptionsChainsData
        The loaded Cboe options chain.
    by : Literal["strike", "expiration"]
        The axis to aggregate over.
    metric : Literal["oi", "volume"]
        Open interest or contract volume.
    date : str | None
        Restrict to a single expiration, which forces the strike axis.
    unit : Literal["value", "percent", "pcr"]
        Raw values, share of total, or the put/call ratio.

    Returns
    -------
    OBBject
        The aggregated rows, with the Plotly figure attached to ``chart``.
    """
    from openbb_core.app.model.obbject import OBBject
    from openbb_core.app.utils import df_to_basemodel

    from openbb_cboe.utils.options.theme import finalize, new_figure

    stat = "open_interest" if metric == "oi" else metric

    if date is not None:
        date = data._get_nearest_expiration(date)
        stats = data.filter_data(by=by, date=date, stat=stat)
    else:
        stats = data.filter_data(by=by, stat=stat)

    symbol = data.underlying_symbol[-1]
    stat_type = stat.replace("_", " ").title()
    index_name = "Expiration" if by == "expiration" and not date else "Strike"
    stats = stats.set_index(index_name)
    stats.Puts = stats.Puts * (-1)
    title = (
        f"{symbol} {stat_type} (%)"
        if unit == "percent"
        else f"{symbol} {stat_type} By {index_name}"
    )
    theme = kwargs.get("theme") or "dark"
    fig, text_color, background = new_figure(theme)
    xtick_vals = (
        [
            round(d) if "." in str(d) and str(d).endswith(".0") else round(d, 2)
            for d in stats.index.tolist()
        ]
        if by == "strike"
        else stats.index
    )

    if unit == "percent":
        stats = stats.dropna(subset=["Net Percent"])
        fig.add_bar(
            x=stats.index,
            y=stats["Net Percent"],
            name="% of Total",
            orientation="v",
            hovertemplate="%{y:.4f}%",
        )
    elif unit == "pcr":
        title = f"{symbol} {stat_type} Put/Call Ratio"
        fig.add_bar(
            x=xtick_vals,
            y=stats.PCR,
            orientation="v",
            name="Put/Call Ratio",
            hovertemplate="%{y:.4f}",
        )
    else:
        fig.add_bar(
            x=xtick_vals,
            y=stats.Calls,
            name="Calls",
            orientation="v",
            marker=dict(color="royalblue"),
            hovertemplate="%{y:.0f}",
        )
        fig.add_bar(
            x=xtick_vals,
            y=stats.Puts,
            name="Puts",
            orientation="v",
            marker=dict(color="red"),
            hovertemplate="%{y:.0f}",
        )

    fig.update_traces(width=0.95, selector=dict(type="bar"))
    fig.set_title(title, x=0.5, font=dict(size=16))
    fig.update_layout(
        paper_bgcolor=background,
        plot_bgcolor=background,
        barmode="relative",
        yaxis=dict(
            ticklen=0,
            showgrid=True,
            tickfont=dict(size=12),
            automargin=True,
            linecolor=text_color,
            showline=True,
        ),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=11),
            ticklen=0,
            type="category",
            linecolor=text_color,
            showline=True,
            nticks=10,
            tickprefix="$" if by == "strike" else "",
            showspikes=False,
        ),
        legend=dict(orientation="v", yanchor="top", y=0.90, xanchor="right", x=-0.01),
        font=dict(color=text_color),
        margin=dict(l=10, r=10, t=10, b=10),
        hovermode="x unified",
    )
    stats.Puts = stats.Puts * (-1)
    output: Any = OBBject(results=df_to_basemodel(stats))

    return finalize(output, fig, theme)
