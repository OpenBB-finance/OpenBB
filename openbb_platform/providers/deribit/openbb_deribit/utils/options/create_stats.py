"""Open interest and volume across a Deribit chain."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_core.app.model.obbject import OBBject

BY = {"strike": "Strike", "expiration": "Expiration"}


def stats_rows(frame, by: str) -> list:
    """Return open interest and volume, split by side and grouped.

    Parameters
    ----------
    frame : DataFrame
        The chain.
    by : str
        Either 'strike' or 'expiration'.

    Returns
    -------
    list
        One record per group, with each side's open interest and volume.
    """
    working = frame.copy()
    working["open_interest"] = working["open_interest"].fillna(0)
    working["volume"] = working["volume"].fillna(0)
    rows: list = []

    for key in sorted(working[by].dropna().unique()):
        at = working[working[by] == key]
        calls = at[at["option_type"] == "call"]
        puts = at[at["option_type"] == "put"]
        call_oi = float(calls["open_interest"].sum())
        put_oi = float(puts["open_interest"].sum())
        call_volume = float(calls["volume"].sum())
        put_volume = float(puts["volume"].sum())
        rows.append(
            {
                by: key,
                "call_open_interest": call_oi,
                "put_open_interest": put_oi,
                "total_open_interest": call_oi + put_oi,
                "put_call_open_interest_ratio": put_oi / call_oi if call_oi else None,
                "call_volume": call_volume,
                "put_volume": put_volume,
                "total_volume": call_volume + put_volume,
                "put_call_volume_ratio": (
                    put_volume / call_volume if call_volume else None
                ),
            }
        )

    return rows


def create_stats(data: dict, theme: str = "dark", **kwargs) -> "OBBject":
    """Draw call and put open interest against the chosen grouping."""
    from openbb_core.app.model.obbject import OBBject
    from openbb_core.app.utils import df_to_basemodel
    from pandas import DataFrame

    from openbb_deribit.utils.options.theme import finalize, new_figure

    by = data.get("by", "strike")
    frame = DataFrame(data["rows"])
    figure, text_color, background = new_figure(theme)
    axis = frame[by].astype(str) if by == "expiration" else frame[by]

    for name, column, color in (
        ("Calls", "call_open_interest", "#3fb950"),
        ("Puts", "put_open_interest", "#e35d6a"),
    ):
        figure.add_bar(
            x=axis,
            y=frame[column],
            name=name,
            marker=dict(color=color),
            hovertemplate="%{x}<b> %{y:,.2f}</b><extra></extra>",
        )

    figure.set_title(
        f"{data.get('symbol', '')} open interest by {BY.get(by, by).lower()}",
        x=0.5,
        font=dict(size=15),
    )
    figure.update_layout(
        barmode="relative",
        paper_bgcolor=background,
        plot_bgcolor=background,
        font=dict(color=text_color),
        margin=dict(l=10, r=10, t=60, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0),
        xaxis=dict(title=BY.get(by, by), showgrid=False, linecolor=text_color),
        yaxis=dict(title="Open interest", showgrid=True, linecolor=text_color),
    )
    output: Any = OBBject(results=df_to_basemodel(frame))

    return finalize(output, figure, theme)
