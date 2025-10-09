"""Price performance charting implementation."""

from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from plotly.graph_objs import Figure  # noqa
    from openbb_charting.core.openbb_figure import OpenBBFigure  # noqa


def price_performance(
    **kwargs,
) -> tuple[Union["OpenBBFigure", "Figure"], dict[str, Any]]:  # noqa: PLR0912
    """Equity Price Performance Chart."""
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame  # noqa
    from openbb_core.app.utils import basemodel_to_df  # noqa
    from openbb_charting.charts.generic_charts import bar_chart  # noqa

    if "data" in kwargs and isinstance(kwargs["data"], DataFrame):
        data = kwargs["data"]
    elif "data" in kwargs and isinstance(kwargs["data"], list):
        data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "symbol"))  # type: ignore
    else:
        data = basemodel_to_df(
            kwargs["obbject_item"],
            index=kwargs.get("index", "symbol"),  # type: ignore
        )

    cols = [
        "one_day",
        "one_week",
        "one_month",
        "three_month",
        "six_month",
        "ytd",
        "one_year",
        "two_year",
        "three_year",
        "four_year",
        "five_year",
    ]

    df = DataFrame()
    chart_df = DataFrame()

    if "symbol" in data.columns:
        data = data.set_index("symbol")
    chart_cols = []

    if len(data) == 0:
        raise ValueError("No data was found in the DataFrame.")

    data = data.drop_duplicates(keep="first")

    for col in cols:
        if col in data.columns and data[col].notnull().any():
            df[col.replace("_", " ").title() if col != "ytd" else col.upper()] = data[
                col
            ].apply(lambda x: round(x * 100, 4) if x is not None else None)

    if df.empty:
        raise ValueError(f"No columns matching, {cols}, were found in the data.")

    chart_df = df.T
    chart_cols = chart_df.columns.to_list()

    if "limit" in kwargs and isinstance(kwargs.get("limit"), int):
        limit = kwargs.pop("limit", 10)
        chart_df = chart_df.head(limit)  # type: ignore

    layout_kwargs: dict[str, Any] = kwargs.get("layout_kwargs", {})

    title = (
        f"{kwargs.pop('title')}" if "title" in kwargs else "Equity Price Performance"
    )
    orientation = (
        kwargs.pop("orientation")
        if "orientation" in kwargs and kwargs.get("orientation") is not None
        else "v"
    )

    ytitle = "Performance (%)"
    xtitle = None

    if orientation == "h":
        xtitle = ytitle  # type: ignore
        ytitle = None  # type: ignore

    fig = bar_chart(
        chart_df.reset_index(),
        x="index",
        y=chart_cols,
        title=title,
        xtitle=xtitle,
        ytitle=ytitle,
        orientation=orientation,  # type: ignore
    )
    fig.update_traces(
        hovertemplate=(
            "%{fullData.name}:%{y:.2f}%<extra></extra>"
            if orientation == "v"
            else "%{fullData.name}:%{x:.2f}%<extra></extra>"
        )
    )

    fig.update_layout(**layout_kwargs)
    content = fig.show(external=True).to_plotly_json()  # type: ignore

    return fig, content
