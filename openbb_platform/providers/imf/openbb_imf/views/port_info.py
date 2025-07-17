"""Plotting functions for IMF Maritime Chokepoint Information"""

from openbb_imf.models.port_info import ImfPortInfoData


def plot_port_info_map(data: list[ImfPortInfoData]):
    """Plot the port information on a map showing regional geography with gradient-colored markers."""
    # pylint: disable=import-outside-toplevel
    from numpy import nan
    from openbb_core.app.model.abstract.error import OpenBBError
    from pandas import DataFrame

    try:
        import plotly.express as px
        from openbb_charting.core.openbb_figure import OpenBBFigure
    except Exception as e:
        raise OpenBBError(
            "Could not import Charting modules. Install with `pip install openbb-charting`."
            + f" -> {e}"
        ) from e

    if (
        data is not None
        and not isinstance(data, list)
        or not all(isinstance(item, ImfPortInfoData) for item in data)
    ):
        raise OpenBBError("Invalid data format. Expected a list of ImfPortInfoData.")
    if len(data) == 0:
        raise OpenBBError("No data to plot.")

    df = DataFrame([item.model_dump() for item in data]).query("vessel_count_total > 0")

    min_size, max_size = 4, 10

    if "country" in df.columns and df["country"].nunique() == 1:
        share_import = df["share_country_maritime_import"].fillna(0)
        share_export = df["share_country_maritime_export"].fillna(0)
        df["import_export_share"] = share_import + share_export
        share_values = df["import_export_share"]

        if share_values.nunique() > 1:
            df["marker_size"] = (
                (share_values - share_values.min())
                / (share_values.max() - share_values.min() + 1e-9)
            ) * (max_size - min_size) + min_size
        else:
            df["marker_size"] = (min_size + max_size) / 2

    elif "vessel_count_total" in df.columns and df["vessel_count_total"].nunique() > 1:
        vessel_counts = df["vessel_count_total"].astype(float)
        df["marker_size"] = (
            (vessel_counts - vessel_counts.min())
            / (vessel_counts.max() - vessel_counts.min() + 1e-9)
        ) * (max_size - min_size) + min_size
    else:
        df["marker_size"] = min_size

    if "port_full_name" in df.columns:
        df["port_full_name"] = df["port_full_name"].fillna("Unknown Port")
    else:
        df["port_full_name"] = "Unknown Port"

    map_zoom = 2
    if "continent" in df.columns and df["continent"].nunique() > 1:
        map_zoom = 0
        map_center = None
    else:
        center_lat = df["latitude"].mean()
        center_lon = df["longitude"].mean()
        map_center = {"lat": center_lat, "lon": center_lon}

    df = df.replace({nan: None})

    def generate_hover_html(row):
        """Generate HTML content for hover tooltip."""
        html_parts: list = []

        port_name = row.get("port_full_name", "Unknown Port")
        html_parts.append(f"<b>{port_name}</b><br>")

        # Share of Country's Maritime Traffic
        share_import = row.get("share_country_maritime_import")
        share_export = row.get("share_country_maritime_export")

        traffic_lines_content: list = []
        if share_import is not None:
            traffic_lines_content.append(
                f"&nbsp;&nbsp;&nbsp;&nbsp;Imports:&nbsp;&nbsp;&nbsp;&nbsp;{share_import:.2%}<br>"
            )
        if share_export is not None:
            traffic_lines_content.append(
                f"&nbsp;&nbsp;&nbsp;&nbsp;Exports:&nbsp;&nbsp;&nbsp;&nbsp;{share_export:.2%}<br>"
            )

        if traffic_lines_content:
            html_parts.append("<br><b>Share of Country's Maritime Traffic</b>:<br>")
            html_parts.extend(traffic_lines_content)

        # Avg Annual Vessels
        vessel_labels = [
            "Total",
            "Containers",
            "Tankers",
            "Dry Bulk",
            "General Cargo",
            "Ro-Ro",
        ]
        vessel_cols = [
            "vessel_count_total",
            "vessel_count_container",
            "vessel_count_tanker",
            "vessel_count_dry_bulk",
            "vessel_count_general_cargo",
            "vessel_count_roro",
        ]
        spaces_after_colon = {
            "Total": 17,
            "Containers": 7,
            "Tankers": 12,
            "Dry Bulk": 11,
            "General Cargo": 1,
            "Ro-Ro": 14,
        }

        vessel_lines_content: list = []
        for label, col_name in zip(vessel_labels, vessel_cols):
            count = row.get(col_name)
            if count is not None:
                num_spaces = spaces_after_colon.get(label, 1)
                space_str = "&nbsp;" * num_spaces
                vessel_lines_content.append(
                    f"&nbsp;&nbsp;&nbsp;&nbsp;{label}:{space_str}{count:,}<br>"
                )

        if vessel_lines_content:
            html_parts.append("<br><b>Avg Annual Vessels</b>:<br>")
            html_parts.extend(vessel_lines_content)

        industry_lines_content: list = []
        for i in [1, 2, 3]:
            industry = row.get(f"industry_top{i}")
            if industry and isinstance(industry, str) and industry.strip():
                industry_lines_content.append(f"&nbsp;&nbsp;&nbsp;&nbsp;{industry}<br>")

        if industry_lines_content:
            html_parts.append("<br><b>Top Industries</b>:<br>")
            html_parts.extend(industry_lines_content)

        return "".join(html_parts)

    df.loc[:, "hover_html"] = df.apply(generate_hover_html, axis=1)

    fig = px.scatter_map(
        df,
        lat="latitude",
        lon="longitude",
        custom_data=df[["hover_html"]],
        size="marker_size",
        size_max=max_size,
        color_discrete_sequence=["fuchsia"],
        opacity=0.4,
        height=600,
        width=600,
    )

    fig.update_traces(hovertemplate="%{customdata[0]}<extra></extra>")

    layout_map_config = {
        "style": "carto-voyager",
        "zoom": map_zoom,
    }
    if map_center:
        layout_map_config["center"] = map_center

    fig.update_layout(
        autosize=False, map=layout_map_config, margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    return OpenBBFigure(fig).show(external=True)
