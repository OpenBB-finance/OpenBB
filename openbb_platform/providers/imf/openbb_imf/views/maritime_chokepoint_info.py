"""Plotting functions for IMF Maritime Chokepoint Information"""

from openbb_imf.models.maritime_chokepoint_info import ImfMaritimeChokePointInfoData


def plot_chokepoint_annual_avg_vessels(
    data: list[ImfMaritimeChokePointInfoData], theme="light"
):
    """Plot the average annual vessels for each chokepoint."""
    # pylint: disable=import-outside-toplevel
    import datetime  # noqa
    from openbb_core.app.model.abstract.error import OpenBBError
    from pandas import DataFrame

    try:
        from openbb_charting.core.openbb_figure import OpenBBFigure
        from plotly import graph_objects as go
        from plotly.subplots import make_subplots
    except Exception as e:
        raise OpenBBError(
            "Could not import Charting modules. Install with `pip install openbb-charting`."
            + f" -> {e}"
        ) from e

    if (
        data is not None
        and not isinstance(data, list)
        or not all(isinstance(item, ImfMaritimeChokePointInfoData) for item in data)
    ):
        raise OpenBBError(
            "Invalid data format. Expected a list of ImfMaritimeChokePointInfoData."
        )
    if len(data) == 0:
        raise OpenBBError("No data to plot.")

    df = DataFrame([item.model_dump() for item in data])
    if theme == "dark":
        geo_bgcolor = "rgba(0,0,0,0)"
        landcolor = "#3a5d3a"
        countrycolor = "#cccccc"
        oceancolor = "#223355"
        coastlinecolor = "#cccccc"
        lakecolor = "#0d47a1"
        rivercolor = "#0d47a1"
        table_header_fill = "#222e3c"
        table_header_font = "#fff"
        table_cell_fill = ["#232323", "#181818"] * (len(df) // 2 + 1)
        font_color = "#fff"
        annotation_color = "#aaa"
        plot_bgcolor = "rgba(21,21,21,1)"
        paper_bgcolor = "rgba(21,21,21,1)"
    else:
        geo_bgcolor = "rgba(255,255,255,0)"
        landcolor = "#3a5d3a"
        countrycolor = "#cccccc"
        oceancolor = "#3a5d99"
        coastlinecolor = "#cccccc"
        lakecolor = "#0d47a1"
        rivercolor = "#0d47a1"
        table_header_fill = "#0d6efd"
        table_header_font = "white"
        table_cell_fill = ["#f5f5f5", "white"] * (len(df) // 2 + 1)
        font_color = "black"
        annotation_color = "#555"
        plot_bgcolor = "rgba(255,255,255,1)"
        paper_bgcolor = "rgba(255,255,255,1)"

    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "geo"}, {"type": "table"}]],
        column_widths=[0.33, 0.67],
        horizontal_spacing=0,
        shared_yaxes=True,
        subplot_titles=[
            "Global Maritime Chokepoints",
            "Annual Average Vessels by Chokepoint",
        ],
    )

    fig.add_trace(
        go.Scattergeo(
            lon=df["longitude"],
            lat=df["latitude"],
            text=df["name"],
            mode="markers",
            marker=dict(
                size=df["vessel_count_total"],
                sizemode="area",
                sizeref=3 * max(df["vessel_count_total"]) / 1000,
                sizemin=7,
                color="#FF3D33",
                opacity=0.6,
                line=dict(width=2, color="darkred"),
                symbol="circle",
            ),
            hovertemplate="<b>%{text}</b><br>"
            + "<br>"
            + "<b>Avg Annual Vessels</b>:<br>"
            + "    Total:                 %{customdata[0]:,}<br>"
            + "    Containers:       %{customdata[1]:,}<br>"
            + "    Tankers:            %{customdata[2]:,}<br>"
            + "    Dry Bulk:           %{customdata[3]:,}<br>"
            + "    General Cargo: %{customdata[4]:,}<br>"
            + "    Ro-Ro:              %{customdata[5]:,}<br>"
            + "<br>"
            + "<b>Top Industries</b>:<br>"
            + "    %{customdata[6]}<br>"
            + "    %{customdata[7]}<br>"
            + "    %{customdata[8]}<br>"
            + "<extra></extra>",
            customdata=df[
                [
                    "vessel_count_total",
                    "vessel_count_container",
                    "vessel_count_tanker",
                    "vessel_count_dry_bulk",
                    "vessel_count_general_cargo",
                    "vessel_count_roro",
                    "industry_top1",
                    "industry_top2",
                    "industry_top3",
                ]
            ].values,
        ),
        row=1,
        col=1,
    )

    vessel_types = [
        "vessel_count_container",
        "vessel_count_tanker",
        "vessel_count_dry_bulk",
        "vessel_count_general_cargo",
        "vessel_count_roro",
    ]
    df_table = df.copy()
    global_total_vessels = df["vessel_count_total"].sum()
    df_table["global_pct"] = df_table["vessel_count_total"] / global_total_vessels * 100
    df_table = df_table.sort_values(by="vessel_count_total", ascending=False)
    cells = []
    cells.append(df_table["name"].tolist())
    cells.append([f"{x:,}" for x in df_table["vessel_count_total"].tolist()])
    cells.append([f"{x:.1f}%" for x in df_table["global_pct"].tolist()])

    for vessel_type in vessel_types:
        cells.append([f"{x:,}" for x in df_table[vessel_type].tolist()])

    fig.add_trace(
        go.Table(
            columnwidth=[
                130,
                70,
                80,
                90,
                80,
                80,
                75,
                65,
            ],
            header=dict(
                values=[
                    "<b>Chokepoint</b>",
                    "<b>Vessels</b>",
                    "<b>% of All</b>",
                    "<b>Containers</b>",
                    "<b>Tankers</b>",
                    "<b>Dry Bulk</b>",
                    "<b>General</b>",
                    "<b>Ro-Ro</b>",
                ],
                font=dict(size=12, color=table_header_font),
                align="left",
                fill_color=table_header_fill,
                height=35,
                line=dict(color="black", width=1),
            ),
            cells=dict(
                values=cells,
                align="right",
                font=dict(size=11, color=font_color),
                height=20,
                fill_color=table_cell_fill,
                line=dict(color="black"),
            ),
            domain=dict(x=[0.30, 0.8], y=[0.1, 0.8]),
        ),
        row=1,
        col=2,
    )

    fig.update_geos(  # type: ignore
        projection=dict(type="orthographic", scale=1, rotation=dict(lon=70, lat=20)),
        showland=True,
        landcolor=landcolor,
        countrycolor=countrycolor,
        showocean=True,
        oceancolor=oceancolor,
        showcoastlines=True,
        coastlinecolor=coastlinecolor,
        showcountries=True,
        showframe=True,
        framecolor="black",
        showlakes=True,
        lakecolor=lakecolor,
        showrivers=True,
        rivercolor=rivercolor,
        resolution=110,
        domain=dict(x=[0, 0.30], y=[0.1, 0.8]),
        bgcolor=geo_bgcolor,
    )
    fig.update_layout(
        title=dict(
            text="Global Maritime Chokepoints: Annual Average Vessels",
            font=dict(size=20, color="black" if theme == "light" else "white"),
            x=0.5,
            y=0.99,
            xref="paper",
        ),
        autosize=True,
        uirevision="fixedsize",
        dragmode="pan",
        geo=dict(bgcolor=geo_bgcolor, visible=False),
        paper_bgcolor=paper_bgcolor,
        plot_bgcolor=plot_bgcolor,
        annotations=[
            dict(
                text=f"Source: IMF Port Watch - {datetime.date.today().isoformat()}",
                x=0.5,
                xref="paper",
                yref="paper",
                y=1,
                yshift=10,
                showarrow=False,
                font=dict(size=10, color=annotation_color),
                xanchor="center",
                yanchor="bottom",
                opacity=0.5,
            )
        ],
    )

    return OpenBBFigure(fig).show(external=True)
