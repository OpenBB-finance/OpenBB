"""Rekt view"""
import logging
import os
from typing import Optional, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.alternative.oss import runa_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_rossindex(
    limit: int = 10,
    sortby: str = "Stars AGR [%]",
    ascend: bool = False,
    show_chart: bool = False,
    show_growth: bool = True,
    chart_type: str = "stars",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plots list of startups from ross index [Source: https://runacap.com/]

    Parameters
    ----------
    limit: int
        Number of startups to search
    sortby: str
        Key by which to sort data. Default: Stars AGR [%]
    ascend: bool
        Flag to sort data descending
    show_chart: bool
        Flag to show chart with startups
    show_growth: bool
        Flag to show growth line chart
    chart_type: str
        Chart type {stars,forks}
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = runa_model.get_startups()

    if df.empty:
        console.print("\nError in runa request\n")
    else:
        if sortby in runa_model.SORT_COLUMNS:
            df = df.sort_values(by=sortby, ascending=ascend)
        df = df.head(limit)
        if show_chart:
            fig = OpenBBFigure.create_subplots(
                1,
                3,
                specs=[[{"type": "domain"}, {"type": "bar", "colspan": 2}, None]],
                column_widths=[0.1, 0.8, 0.1],
            )
            fig.update_layout(
                xaxis_title=chart_type.title(), yaxis=dict(title="Company", side="left")
            )

            fig.set_title(f"ROSS Index - Total {chart_type.title()}")

            fig.add_bar(
                x=df[chart_type.title()],
                y=df["GitHub"],
                orientation="h",
                name=chart_type.title(),
                text=df[chart_type.title()],
                textposition="auto",
                row=1,
                col=2,
            )

        if show_growth:
            fig = OpenBBFigure.create_subplots(
                1,
                3,
                specs=[[{"type": "domain"}, {"type": "bar", "colspan": 2}, None]],
                column_widths=[0.1, 0.8, 0.1],
            )
            fig.update_layout(
                xaxis_title="Annual Growth [times]",
                yaxis=dict(title="Company", side="left"),
            )
            fig.set_title(f"ROSS Index - {chart_type.title()} Annual Growth")
            fig.add_bar(
                x=df["FG" if chart_type == "forks" else "SG"],
                y=df["GitHub"],
                orientation="h",
                name="Annual Growth [times]",
                text=df["FG" if chart_type == "forks" else "SG"],
                textposition="auto",
                row=1,
                col=2,
            )

        show_df = df.drop(["SG", "FG"], axis=1)
        show_df = show_df.fillna("")
        show_df["GitHub"] = show_df["GitHub"].str.wrap(10)
        print_rich_table(
            show_df,
            headers=list(show_df.columns),
            floatfmt=".1f",
            show_index=False,
            title="ROSS Index - the fastest-growing open-source startups",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "runaidx",
            df,
            sheet_name,
        )

        if show_chart or show_growth:
            return fig.show(external=external_axes)

    return None
