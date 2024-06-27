"""Yield curve chart."""

from typing import Any, Dict, Tuple, Union

import pandas as pd
from openbb_core.app.utils import basemodel_to_df
from plotly.graph_objs import Figure

from openbb_charting.charts.generic_charts import line_chart
from openbb_charting.core.openbb_figure import OpenBBFigure


def futures_curve(
    **kwargs,
) -> Tuple[Union[OpenBBFigure, Figure], Dict[str, Any]]:  # noqa: PLR0912
    """Futures curve chart."""
    if "data" in kwargs and isinstance(kwargs["data"], pd.DataFrame):
        data = kwargs["data"]
    elif "data" in kwargs and isinstance(kwargs["data"], list):
        data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "symbol"))  # type: ignore
    else:
        data = basemodel_to_df(
            kwargs["obbject_item"], index=kwargs.get("index", "symbol")  # type: ignore
        )
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be a pandas DataFrame")

    # Check for required columns
    required_columns = {"expiration", "price", "symbol"}
    if not required_columns.issubset(data.columns):
        missing = required_columns - set(data.columns)
        raise ValueError(f"Missing columns in the DataFrame: {missing}")

    data["expiration"] = pd.to_datetime(data["expiration"])

    layout_kwargs: Dict[str, Any] = kwargs.get("layout_kwargs", {})
    title = kwargs.pop("title", "Futures Curve Chart")
    orientation = kwargs.pop("orientation", "v")

    ytitle = kwargs.pop("ytitle", "Price")
    xtitle = kwargs.pop("xtitle", "Expiration Date")

    fig = line_chart(
        data=data,
        x="expiration",
        y="price",
        title=title,
        xtitle=xtitle,
        ytitle=ytitle,
        orientation=orientation,
        layout_kwargs=layout_kwargs,
        **kwargs,
    )

    fig.update_traces(
        hovertemplate="Symbol: %{text}<br>Expiration: %{x|%Y-%m-%d}<br>Price: %{y:.2f}",
        text=data["symbol"],
    )
    content = {"plotly_json": fig.to_json()}

    return fig, content
