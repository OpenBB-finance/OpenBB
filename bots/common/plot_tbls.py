from math import floor
from typing import List, Optional, Tuple, Union

import pandas as pd
import plotly


# pylint: disable=R0913
def plot_df(
    df: Union[pd.Series, pd.DataFrame],
    print_index: bool = True,
    title: Optional[dict] = None,
    tbl_header_visible: bool = True,
    tbl_header: Optional[dict] = None,
    tbl_cells: Optional[dict] = None,
    row_fill_color: Optional[Tuple[str, str]] = None,
    col_width: Optional[Union[int, float, List[Union[int, float]]]] = None,
    fig_size: Optional[Tuple[int, int]] = None,
    **layout_kwargs,
) -> plotly.graph_objects.Figure:
    """Plots a pd.Series or pd.DataFrame.

    Parameters
    ----------
    df : Union[pd.Series, pd.DataFrame]
        Series or dataframe to be plotted.
    print_index : bool, default True
        If `True`, prints the dataframe's index. `df.index.name` will become the index
        column header.
    title : dict, default None
        A dict possibly containing `plotly` key/value pairs:
        https://plotly.com/python/reference/layout/#layout-title

        More relevant key/value pairs:

        - font_color : color
        - font_family : str
        - font_size : number greater than or equal to 1
        - text : str
        - x : number between or equal to 0 and 1, default 0.5

          Sets the x position with respect to `xref` in normalized coordinates
          from "0" (left) to "1" (right).
        - xanchor : enumerated, one of ("auto", "left", "center", "right"),
          default "auto"

          Sets the title's horizontal alignment with respect to its x position.
          "left" means that the title starts at x, "right" means that the title ends
          at x and "center" means that the title's center is at x. "auto" divides
          `xref` by three and calculates the `xanchor` value automatically based on
          the value of `x`.
    tbl_header_visible : bool, default True,
        If `False`, table header will be invisible. Takes precedence over `tbl_header`
        argument.
    tbl_header, tbl_cells : dict, default None
        A dict possibly containing `plotly` key/value pairs:
        https://plotly.com/python/reference/table/#table-header
        https://plotly.com/python/reference/table/#table-cells

        More relevant key/value pairs:

        - align : enumerated or array of enumerateds,
          one of ("left", "center", "right"), default "center"
        - fill_color : color, default "white"
        - font_color : color or array of colors
        - font_family : str or array of str
        - font_size : number or array of numbers greater than or equal to 1
        - height : number, default 28
        - line_width : number or array of numbers, default 1
    row_fill_color : Tuple[str, str], default None
        Tuple of colors that will be used to alternate row colors. Takes precedence
        over `tbl_cells["fill_color"]`.
    col_width : number or array of numbers, default None
        The width of columns expressed as a ratio. Columns fill the available width
        in proportion of their specified column widths.
    fig_size : Tuple[int, int], default None
        Tuple specifying the `width` and `height` of the figure.
    **layout_kwargs
        Plotly accepts a large number of layout-related keyword arguments.
        A detailed descriptions is available at
        https://plotly.com/python-api-reference/generated/plotly.graph_objects.Layout.html.

    Returns
    -------
    plotly.graph_objects.Figure
        Returns a figure object.

    """

    def _alternate_row_colors() -> Optional[List[str]]:
        color_list = None
        # alternate row colors
        row_count = len(df)
        if row_fill_color is not None:
            # determine how many rows in `df` and then create a list with alternating
            # row colors
            row_odd_count = floor(row_count / 2) + row_count % 2
            row_even_count = floor(row_count / 2)
            odd_list = [row_fill_color[0]] * row_odd_count
            even_list = [row_fill_color[1]] * row_even_count
            color_list = [x for y in zip(odd_list, even_list) for x in y]
            if row_odd_count > row_even_count:
                color_list.append(row_fill_color[0])

        return color_list

    def _tbl_values():
        if print_index:
            header_values = [
                "<b>" + x + "<b>"
                for x in [
                    df.index.name if df.index.name is not None else "",
                    *df.columns,
                ]
            ]
            cell_values = [df.index, *[df[col] for col in df]]
        else:
            header_values = ["<b>" + x + "<b>" for x in df.columns.to_list()]
            cell_values = [df[col] for col in df]

        return header_values, cell_values

    row_color_list = _alternate_row_colors()
    header_vals, cell_vals = _tbl_values()

    if not tbl_header:
        tbl_header = dict()
    tbl_header.update(values=header_vals)

    if not tbl_header_visible:
        tbl_header.update(
            fill_color="white", font_color="white", line_color="white", height=1
        )

    if not tbl_cells:
        tbl_cells = dict()
    tbl_cells.update(
        values=cell_vals,
        fill_color=[row_color_list] * len(df)
        if row_color_list
        else tbl_cells.get("fill_color"),
    )

    fig = plotly.graph_objs.Figure(
        data=[plotly.graph_objs.Table(header=tbl_header, cells=tbl_cells)]
    )

    fig.data[0]["columnwidth"] = col_width if col_width else None

    if not title:
        title = dict()
    title.update(
        x=0.01 if title.get("x") is None else title.get("x"),
        xanchor="left" if title.get("xanchor") is None else title.get("xanchor"),
    )

    fig.update_layout(
        title=title,
        margin=dict(autoexpand=False, b=5, l=5, r=5, t=40 if title.get("text") else 5),
        width=fig_size[0] if fig_size else None,
        height=fig_size[1] if fig_size else None,
        autosize=False if col_width else None,
        **layout_kwargs,
    )

    return fig
