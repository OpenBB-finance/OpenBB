"""IMF Utilities Router."""

# pylint: disable=C0302
# pylint: disable=unused-argument,protected-access,too-many-positional-arguments,too-many-locals,too-many-branches

from typing import Annotated, Any, Literal

from fastapi import Query
from fastapi.responses import HTMLResponse
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.service.system_service import SystemService
from openbb_imf.models.indicator_metadata import ImfTableMetadata
from openbb_imf.utils.constants import (
    PRESENTATION_TABLES,
    table_dataflow_choices,
    table_dataflow_map,
    table_name_map,
)
from openbb_imf.utils.metadata import ImfMetadata

router = Router(prefix="", description="Utilities for IMF provider.")
api_prefix = SystemService().system_settings.api_settings.prefix


@router.command(
    methods=["GET"],
    widget_config={
        "description": "Descriptions for all IMF dataflows.",
        "params": [
            {
                "paramName": "output_format",
                "label": "Output Format",
                "value": "markdown",
                "description": "Output format: 'json' or 'markdown'.",
                "show": False,
            }
        ],
        "type": "markdown",
        "data": {"dataKey": "results"},
        "gridData": {"w": 40, "h": 15},
        "refetchInterval": False,
        "name": "IMF Dataflows",
        "source": ["IMF"],
        "category": "IMF Utilities",
        "subCategory": "Metadata",
    },
    examples=[
        APIEx(
            description="Lists all known dataflows available from the IMF in JSON format.",
            parameters={"output_format": "json"},
        ),
        APIEx(
            description="Return the content as a markdown-formatted summary instead of a JSON table.",
            parameters={"output_format": "markdown"},
        ),
        PythonEx(
            description="Lists all known dataflows available from the IMF.",
            code=[
                "imf_dataflows = obb.imf.utils.list_dataflows()",
                "print(imf_dataflows)",
            ],
        ),
    ],
)
async def list_dataflows(
    output_format: Literal["json", "markdown"] = "json",
) -> OBBject:
    """List all available IMF dataflows.

    Returns an OBBject containing either a JSON dictionary of dataflows
    or a markdown string under the 'results' attribute.
    """
    metadata = ImfMetadata()
    dataflows = metadata.dataflows

    if output_format == "markdown":
        all_tables = metadata.list_all_dataflow_tables()
        md_text = ""

        for dataflow_id in sorted(dataflows.keys()):
            details = dataflows[dataflow_id]
            indicators = metadata.get_indicators_in(dataflow_id)
            params = metadata.get_dataflow_parameters(dataflow_id)
            md_text += f"## `{dataflow_id}` - {details.get('name', '')}\n\n"

            if indicators:
                md_text += f"**Number of Series:** {len(indicators)}\n\n"

            if params:
                escaped_params = [f"`{param}`" for param in list(params)]
                md_text += f"**Dimensions:** {', '.join(escaped_params)}\n\n"

            presentations = all_tables.get(dataflow_id, [])

            if presentations:
                md_text += "### Presentation Tables\n\n"
                seen_names: set[str] = set()

                for pres in presentations:
                    pres_name = pres.get("name", "").strip()

                    if pres_name in seen_names:
                        continue

                    seen_names.add(pres_name)

                    pres_id = pres.get("id", "")
                    pres_desc = pres.get("description", "").strip()
                    friendly_name = pres.get("friendly_name", "")
                    symbol = f"{dataflow_id}::{pres_id}"
                    md_text += f"#### {pres_name}\n\n"

                    if friendly_name:
                        md_text += f"**Friendly Name:** `{friendly_name}`\n\n"

                    md_text += f"**Symbol:** `{symbol}`\n\n"

                    if pres_desc and pres_desc != pres_name:
                        md_text += f"{pres_desc}\n\n"

            md_text += f"{details.get('description', '').strip()}\n\n"
            md_text += "---\n\n"

        return OBBject(results=md_text)

    return OBBject(results=dataflows)


@router.command(
    methods=["GET"],
    widget_config={
        "name": "IMF Dataflow Parameters",
        "type": "markdown",
        "params": [
            {
                "paramName": "dataflow_id",
                "label": "Dataflow",
                "value": "CPI",
                "description": "The IMF dataflow to display.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/imf_utils/list_dataflow_choices",
                "style": {"popupWidth": 700},
            },
            {
                "paramName": "output_format",
                "value": "markdown",
                "show": False,
            },
        ],
        "source": ["IMF"],
        "category": "IMF Utilities",
        "subCategory": "Metadata",
    },
    examples=[
        PythonEx(
            description="Get parameters for the 'CPI' dataflow.",
            code=[
                "imf_params = obb.imf.utils.get_dataflow_dimensions('CPI')",
                "print(imf_params.results)",
            ],
        ),
        APIEx(
            description="Get parameters for the 'GFS_BS' dataflow in markdown format.",
            parameters={"dataflow_id": "GFS_BS", "output_format": "markdown"},
        ),
        APIEx(
            description="Get parameters for the 'IL' dataflow in JSON format.",
            parameters={"dataflow_id": "IL", "output_format": "json"},
        ),
    ],
)
async def get_dataflow_dimensions(
    dataflow_id: Annotated[
        str,
        Query(
            title="Dataflow",
            description="The IMF dataflow ID. Use `list_dataflows()` to see available dataflows.",
        ),
    ],
    output_format: Literal["json", "markdown"] = "json",
) -> OBBject:
    """Dataflow parameters and possible values.

    Returns an OBBject containing either a JSON dictionary of parameters
    and their options, or a markdown string under the 'results' attribute.
    """
    metadata = ImfMetadata()
    params_str = ""

    try:
        parameters = metadata.get_dataflow_parameters(dataflow_id)
    except ValueError as e:
        raise e from e

    if output_format == "json":
        return OBBject(results=parameters)

    for dim, options in parameters.items():
        params_str += f"### `{dim}`\n\n"
        for option in options:
            params_str += f"- `{option.get('value', '')}` : {option.get('label')}\n\n"
        params_str += "---\n\n"

    return OBBject(results=params_str)


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get port ID choices for IMF Port Watch.",
            parameters={},
        )
    ],
)
async def list_port_id_choices() -> list[dict[str, str]]:
    """
    Get port ID choices for IMF Port Watch.

    Returns
    -------
    list[dict[str, str]]
        A list of dictionaries with 'label' and 'value' for each port ID.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_imf.utils.port_watch_helpers import get_port_id_choices

    choices = get_port_id_choices()
    return choices


@router.command(
    methods=["GET"],
    examples=[
        APIEx(
            description="Get the list of available presentation tables.",
            parameters={},
        )
    ],
    widget_config={
        "name": "IMF Presentation Tables List",
        "description": "Presentation tables from the IMF database.",
        "params": [
            {
                "paramName": "symbol",
                "label": "Table Symbol",
                "value": None,
                "description": "Dummy parameter to allow grouping in the UI.",
                "type": "text",
                "show": False,
            }
        ],
        "refetchInterval": False,
        "source": ["IMF"],
        "category": "IMF Utilities",
        "subCategory": "Metadata",
    },
)
async def list_tables() -> OBBject[list[ImfTableMetadata]]:
    """Get the list of presentation tables available from the IMF."""
    metadata = ImfMetadata()
    tables: list[ImfTableMetadata] = []
    dataflows = metadata.list_all_dataflow_tables()

    for dataflow_id, presentations in dataflows.items():
        for pres in presentations:
            table_id = pres.get("id", "")
            unique_key = f"{dataflow_id}::{table_id}"

            table: dict = {}
            table["name"] = pres.get("name", "")
            table["description"] = pres.get("description", "").strip()
            table["symbol"] = unique_key
            table["agency_id"] = pres.get("agency_id", "")
            table["dataflow_id"] = dataflow_id
            table["codelist_id"] = pres.get("codelist_id", "")
            tables.append(ImfTableMetadata(**table))

    return OBBject(results=tables)


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get presentation table choices for IMF data retrieval.",
            parameters={},
        ),
    ],
)
async def list_table_choices() -> list[dict[str, str]]:
    """Get presentation table choices for IMF data retrieval.

    Returns
    -------
    list[dict[str, str]]
        A list of dictionaries with 'label' and 'value' for each presentation table.
    """
    metadata = ImfMetadata()
    table_choices = metadata.list_all_dataflow_tables()
    choices: list[dict[str, str]] = []
    for dataflow_id, presentations in table_choices.items():
        for pres in presentations:
            table_id = pres.get("id", "")
            unique_key = f"{dataflow_id}::{table_id}"
            choices.append(
                {
                    "label": pres.get("name", ""),
                    "value": unique_key,
                }
            )

    return choices


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get dataflow choices for IMF data retrieval.",
            parameters={},
        )
    ],
)
async def list_dataflow_choices() -> list[dict[str, str]]:
    """Get dataflow choices for IMF data retrieval.

    Returns
    -------
    list[dict[str, str]]
        A list of dictionaries with 'label' and 'value' for each presentation table.
    """
    metadata = ImfMetadata()
    dataflows = metadata.dataflows
    choices: list[dict[str, str]] = []
    for dataflow_id, details in dataflows.items():
        choices.append(
            {
                "label": details.get("name", ""),
                "value": dataflow_id,
            }
        )

    return sorted(choices, key=lambda x: x["label"])


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get the dataflow group choices.",
            parameters={},
        ),
        APIEx(
            description="Get table choices for the 'cpi' dataflow group.",
            parameters={
                "dataflow_group": "cpi",
            },
        ),
        APIEx(
            description="Get country choices for the 'cpi' dataflow group and 'cpi' table.",
            parameters={
                "dataflow_group": "cpi",
                "table": "cpi",
            },
        ),
        APIEx(
            description="Get frequency choices for the 'cpi' dataflow group, 'cpi' table, and 'JPN' country.",
            parameters={
                "dataflow_group": "cpi",
                "table": "cpi",
                "country": "JPN",
            },
        ),
    ],
)
async def presentation_table_choices(
    dataflow_group: str | None = None,
    table: str | None = None,
    country: str | None = None,
    frequency: str | None = None,
) -> list[dict[str, str]]:
    """Get presentation table choices for IMF data retrieval.

    This endpoint provides dynamic choices for IMF presentation tables based on selected parameters.
    It is intended to be used by the OpenBB Workspace UI to populate dropdowns.

    For manual API calls, use `economy/indicators` instead with a `symbol` from `list_tables()`.

    Parameters
    ----------
    dataflow_group : str | None
        The IMF dataflow group. Show all groups if None.
    table : str | None
        The IMF presentation table ID. Enter a dataflow_group to see table choices.
    country : str | None
        Enter a dataflow_group and table to see country choices.
    frequency : str | None
        Enter a dataflow_group, table, and country to see frequency choices.

    Returns
    -------
    list[dict[str, str]]
        A list of dictionaries with 'label' and 'value' for each presentation table.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_imf.utils.progressive_helper import ImfParamsBuilder

    choices: list[dict[str, str]] = []

    if dataflow_group is None:
        return table_dataflow_choices

    metadata = ImfMetadata()

    if dataflow_group is not None and table is None:

        table_names = table_dataflow_map.get(dataflow_group, [])

        for t in table_names:
            choices.append(
                {
                    "label": table_name_map.get(t, t),
                    "value": t,
                }
            )

        return choices

    if dataflow_group is not None and table is not None and country is None:
        table_id = PRESENTATION_TABLES.get(table, "")
        dataflow_id = table_id.split("::")[0]
        params = metadata.get_dataflow_parameters(dataflow_id)
        country_dim = (
            "COUNTRY"
            if "COUNTRY" in params
            else "JURISDICTION" if "JURISDICTION" in params else "REF_AREA"
        )
        countries = params.get(country_dim, [])

        return sorted(countries, key=lambda x: x["label"])

    if dataflow_group is not None and table is not None and country is not None:
        table_id = PRESENTATION_TABLES.get(table, "")
        dataflow_id = table_id.split("::")[0]
        hierarchy_id = table_id.split("::", 1)[1] if "::" in table_id else None
        params = metadata.get_dataflow_parameters(dataflow_id)
        country_dim = "COUNTRY" if "COUNTRY" in params else "REF_AREA"
        freq_dim = "FREQUENCY" if "FREQUENCY" in params else "FREQ"

        # Get table structure and extract dimension codes (same as table_builder.get_table)
        table_structure = metadata.get_dataflow_table_structure(
            dataflow_id, hierarchy_id
        )
        dimension_codes: dict[str, list[str]] = {}
        for entry in table_structure.get("indicators", []):
            indicator_code = entry.get("indicator_code")
            dimension_id = entry.get("dimension_id")
            if indicator_code and dimension_id:
                if dimension_id not in dimension_codes:
                    dimension_codes[dimension_id] = []
                if indicator_code not in dimension_codes[dimension_id]:
                    dimension_codes[dimension_id].append(indicator_code)

        pb = ImfParamsBuilder(dataflow_id=dataflow_id)
        dims_in_order = pb._get_dimensions_in_order()

        # Set dimensions in order, using table's indicator codes
        for dim_id in dims_in_order:
            if dim_id in dimension_codes:
                codes = dimension_codes[dim_id]
                joined = "+".join(codes)
                if len(joined) > 800:
                    # Truncate to avoid URL length issues
                    joined = "+".join(codes[:20])
                    if len(joined) > 800:
                        joined = "*"
                pb.set_dimension((dim_id, joined))
            elif dim_id == country_dim:
                pb.set_dimension((dim_id, str(country).replace(",", "+")))

        options = pb.get_options_for_dimension(freq_dim) if freq_dim else []

        return options

    if (
        dataflow_group is not None
        and table is not None
        and country is not None
        and frequency is not None
    ):
        table_id = PRESENTATION_TABLES.get(table, "")
        dataflow_id = table_id.split("::")[0]
        hierarchy_id = table_id.split("::", 1)[1] if "::" in table_id else None
        params = metadata.get_dataflow_parameters(dataflow_id)
        country_dim = "COUNTRY" if "COUNTRY" in params else "REF_AREA"
        freq_dim = "FREQUENCY" if "FREQUENCY" in params else "FREQ"

        # Get table structure and extract dimension codes (same as table_builder.get_table)
        table_structure = metadata.get_dataflow_table_structure(
            dataflow_id, hierarchy_id
        )
        dimension_codes = {}
        for entry in table_structure.get("indicators", []):
            indicator_code = entry.get("indicator_code")
            dimension_id = entry.get("dimension_id")
            if indicator_code and dimension_id:
                if dimension_id not in dimension_codes:
                    dimension_codes[dimension_id] = []
                if indicator_code not in dimension_codes[dimension_id]:
                    dimension_codes[dimension_id].append(indicator_code)

        pb = ImfParamsBuilder(dataflow_id=dataflow_id)
        dims_in_order = pb._get_dimensions_in_order()

        # Set dimensions in order, using table's indicator codes
        for dim_id in dims_in_order:
            if dim_id in dimension_codes:
                codes = dimension_codes[dim_id]
                joined = "+".join(codes)
                if len(joined) > 800:
                    joined = "+".join(codes[:20])
                    if len(joined) > 800:
                        joined = "*"
                pb.set_dimension((dim_id, joined))
            elif dim_id == country_dim:
                pb.set_dimension((dim_id, str(country).replace(",", "+")))
            elif dim_id == freq_dim:
                pb.set_dimension((dim_id, frequency))

        transform_dim = (
            "TYPE_OF_TRANSFORMATION" if "TYPE_OF_TRANSFORMATION" in params else None
        )
        options = pb.get_options_for_dimension(transform_dim) if transform_dim else []

        return options

    return choices


@router.command(
    methods=["GET"],
    widget_config={
        "title": "IMF Presentation Table",
        "type": "html",
        "params": [
            {
                "paramName": "dataflow_group",
                "label": "Dataflow",
                "value": None,
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/imf_utils/presentation_table_choices",
                "description": "The IMF dataflow group.",
            },
            {
                "paramName": "table",
                "label": "Table",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/imf_utils/presentation_table_choices",
                "optionsParams": {
                    "dataflow_group": "$dataflow_group",
                },
                "description": "The IMF presentation table.",
            },
            {
                "paramName": "country",
                "label": "Country",
                "description": "Country or region for the table.",
                "type": "endpoint",
                "multiSelect": True,
                "optionsEndpoint": f"{api_prefix}/imf_utils/presentation_table_choices",
                "optionsParams": {
                    "dataflow_group": "$dataflow_group",
                    "table": "$table",
                    "dimension_values": "$dimension_values",
                },
            },
            {
                "paramName": "frequency",
                "label": "Frequency",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/imf_utils/presentation_table_choices",
                "optionsParams": {
                    "dataflow_group": "$dataflow_group",
                    "table": "$table",
                    "country": "$country",
                    "dimension_values": "$dimension_values",
                },
                "description": "The data frequency.",
            },
            {
                "paramName": "dimension_values",
                "label": "Dimension Values",
                "type": "text",
                "value": None,
                "description": "Dimension selection for filtering. Format: 'DIM_ID1:VAL1+VAL2.'",
                "multiple": True,
                "multiSelect": False,
            },
            {
                "paramName": "limit",
                "label": "Limit",
                "value": 3,
                "description": "Most recent N records to retrieve per series.",
                "type": "number",
            },
            {
                "paramName": "raw",
                "show": False,
            },
        ],
        "raw": True,
        "refetchInterval": False,
        "name": "IMF Presentation Table",
        "description": "Presentation tables from the IMF database.",
        "source": ["IMF"],
        "category": "IMF Utilities",
        "subCategory": "Presentation Tables",
    },
    examples=[
        APIEx(
            description="Get the most recent Balance of Payments table for Japan.",
            parameters={
                "dataflow_group": "bop",
                "table": "bop_standard",
                "country": "JPN",
                "frequency": "Q",
                "limit": 4,
            },
        )
    ],
)
async def presentation_table(
    dataflow_group: Annotated[
        str | None,
        Query(
            title="Dataflow Group",
            description="The IMF dataflow group."
            + " See presentation_table_choices() for options.",
        ),
    ] = None,
    table: Annotated[
        str | None,
        Query(
            title="Table",
            description="The IMF presentation table ID."
            + " See presentation_table_choices() for options.",
        ),
    ] = None,
    country: Annotated[
        str | None,
        Query(
            title="Country",
            description="Country code to filter the data."
            + " Enter multiple codes by joining on '+'. See presentation_table_choices() for options."
            + " Typical values are ISO3 country codes.",
        ),
    ] = None,
    frequency: Annotated[
        str | None,
        Query(
            title="Frequency",
            description="The data frequency. See presentation_table_choices() for options."
            + " Typical values are 'A' (annual), 'Q' (quarter), 'M' (month), or 'D' (day).",
        ),
    ] = None,
    dimension_values: Annotated[
        list[str] | str | None,
        Query(
            title="Dimension Values",
            description="Dimension selection for filtering. Format: 'DIM_ID1:VAL1+VAL2.'"
            + " See presentation_table_choices() and list_dataflow_choices() for available dimensions and values.",
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(
            title="Limit",
            description="Maximum number of records to retrieve per series.",
        ),
    ] = 1,
    raw: Annotated[
        bool,
        Query(
            title="Raw Output",
            description="Return presentation table as raw JSON data if True.",
        ),
    ] = False,
) -> Any:
    """Get a formatted presentation table from the IMF database. Returns as HTML or JSON list."""
    # pylint: disable=import-outside-toplevel
    import html as html_module

    from openbb_imf.models.economic_indicators import ImfEconomicIndicatorsFetcher
    from pandas import DataFrame

    if dataflow_group is None or table is None:
        raise OpenBBError(ValueError("Please enter a dataflow group and a table."))

    if country is None or frequency is None:
        raise OpenBBError(ValueError("Please enter a country and frequency."))

    freq_map = {"A": "annual", "Q": "quarter", "M": "month", "D": "day"}
    symbol = PRESENTATION_TABLES.get(table, "")
    params = {
        "symbol": symbol,
        "country": country,
        "limit": limit,
        "frequency": freq_map.get(frequency, frequency),
        "dimension_values": dimension_values,
        "pivot": True,
    }
    results = await ImfEconomicIndicatorsFetcher.fetch_data(params, {})
    results_json = [d.model_dump(mode="json", exclude_none=True) for d in results.result]  # type: ignore

    if raw is True:
        return results_json

    df = DataFrame(results_json).set_index(["title", "country"]).reset_index()
    # Preserve leading whitespace by replacing double spaces with non-breaking spaces
    df["title"] = df["title"].apply(
        lambda x: x.replace("  ", "\u00a0\u00a0") if isinstance(x, str) else x
    )

    columns = df.columns.tolist()
    header_cells = "".join(
        f"<th>{html_module.escape(str(col))}</th>" for col in columns
    )

    def format_number(value):
        """Format large numbers with K, M, B suffixes for readability."""
        if isinstance(value, (int, float)):
            abs_value = abs(value)
            if abs_value >= 1_000_000_000:
                return f"{value / 1_000_000_000:.2f}".rstrip("0").rstrip(".") + "B"
            if abs_value >= 1_000_000:
                return f"{value / 1_000_000:.2f}".rstrip("0").rstrip(".") + "M"
            if abs_value >= 1_000:
                return f"{value / 1_000:.2f}".rstrip("0").rstrip(".") + "K"
            if isinstance(value, float):
                return f"{value:.2f}".rstrip("0").rstrip(".")
            return str(value)
        return str(value)

    # Build body rows
    body_rows = ""
    for _, row in df.iterrows():
        cells = "".join(
            f"<td>{html_module.escape(format_number(row[col]))}</td>" for col in columns
        )
        body_rows += f"<tr>{cells}</tr>"

    interactive_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IMF Presentation Table</title>
    <link rel="stylesheet" href="https://rsms.me/inter/inter.css">
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Inter', sans-serif;
            margin: 0; padding: 20px; background: #1a1a2e; color: #eee;
        }}
        .table-container {{
            max-height: 85vh; overflow: auto; border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        table {{
            width: 100%; border-collapse: collapse; background: #16213e;
        }}
        thead {{ position: sticky; top: 0; z-index: 10; }}
        th {{
            background: linear-gradient(180deg, #1f4068 0%, #162447 100%);
            padding: 12px 8px; text-align: left; font-weight: 600;
            border-bottom: 2px solid #e94560; white-space: nowrap;
            resize: horizontal; overflow: hidden; min-width: 50px;
        }}
        th:first-child {{ width: 400px; }}
        td {{
            padding: 10px 8px; border-bottom: 1px solid #2a2a4a;
            overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 13px; max-width: 0;
        }}
        td:first-child {{ white-space: pre; }}
        tr:nth-child(even) {{ background: #1a1a3e; }}
        tr:nth-child(odd) {{ background: #16213e; }}
        tr:hover {{ background: #252560; }}
        /* Scrollbar styling */
        .table-container::-webkit-scrollbar {{ width: 6px; height: 10px; }}
        .table-container::-webkit-scrollbar-track {{ background: #1a1a2e; }}
        .table-container::-webkit-scrollbar-thumb {{
            background: #444; border-radius: 5px;
        }}
        .table-container::-webkit-scrollbar-thumb:hover {{ background: #555; }}
    </style>
</head>
<body>
    <div class="table-container">
        <table id="dataTable">
            <thead><tr>{header_cells}</tr></thead>
            <tbody>{body_rows}</tbody>
        </table>
    </div>
</body>
</html>"""

    return HTMLResponse(content=interactive_html)


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    include_in_schema=False,
    examples=[
        APIEx(
            description="Get progressive indicator choices for IMF data retrieval."
            + " Start with the 'symbol' parameter to get all available countries."
            + " Then progressively add parameters to narrow down choices.",
            parameters={
                "symbol": "QGFS::F4_L_T_XDC",
            },
        ),
    ],
)
async def indicator_choices(  # noqa: PLR0912
    symbol: str | None = None,
    country: str | None = None,
    frequency: str | None = None,
    transform: str | None = None,
    dimension_values: list[str] | None = None,
) -> list[dict[str, str]]:
    """Get progressive indicator choices for IMF data retrieval.

    This endpoint works progressively starting with the 'symbol' parameter,
    which is required and in the format 'dataflow::indicator'.

    Function is not intended to be used directly;
    it is used by the OpenBB Workspace for progressive parameter selection.

    For manual inspection, use the `get_dataflow_dimensions` endpoint instead.

    Parameters
    ----------
    symbol : str | None
        The IMF dataflow and indicator code in the format 'dataflow::indicator'.
        No symbol will return an empty list. Use `economy/available_indicators` to see available symbols.
    country : str | None
        Enter a symbol and leave country as None to see country choices.
    frequency : str | None
        Enter a symbol and country to see frequency choices.
    transform : str | None
        Enter a symbol, country, and frequency to see transform choices.
    dimension_values : list[str] | None
        Additional dimension filters in 'DIM_ID:VALUE' format to constrain choices.

    Returns
    -------
    list[dict[str, str]]
        A list of dictionaries with 'label' and 'value' for each choice.
    """
    # pylint: disable=import-outside-toplevel
    from urllib.parse import unquote

    from openbb_imf.utils.helpers import detect_transform_dimension

    metadata = ImfMetadata()

    # Symbol is required and in format dataflow::indicator
    if symbol is None:
        return []

    # URL-decode the symbol parameter and handle multiple comma-separated symbols
    symbol = unquote(symbol)

    # Parse multiple symbols (comma-separated): "QGFS::F4_L_T_XDC,QGFS::F12_L_T_XDC"
    symbols = [s.strip() for s in symbol.split(",") if s.strip()]
    if not symbols:
        return []

    # Extract unique dataflows and all indicator codes
    dataflows_seen: set[str] = set()
    indicator_codes: list[str] = []

    for sym in symbols:
        if "::" in sym:
            df_id = sym.split("::")[0].strip()
            ind_code = sym.split("::", 1)[1].strip()
            dataflows_seen.add(df_id)
            if ind_code:
                indicator_codes.append(ind_code)
        else:
            # Just a dataflow ID with no indicator
            dataflows_seen.add(sym.strip())

    # For now, only support single dataflow (use first one)
    dataflow_id = list(dataflows_seen)[0] if dataflows_seen else None
    indicator_code = "+".join(indicator_codes) if indicator_codes else None

    if not dataflow_id:
        return []

    # Get dimension order for this dataflow
    df_obj = metadata.dataflows.get(dataflow_id, {})

    if not df_obj:
        return []

    dsd_id = df_obj.get("structureRef", {}).get("id")
    dsd = metadata.datastructures.get(dsd_id, {})
    dimensions = dsd.get("dimensions", [])

    # Sort by position
    sorted_dims = sorted(
        [d for d in dimensions if d.get("id") != "TIME_PERIOD"],
        key=lambda x: int(x.get("position", 0)),
    )
    dim_order = [d["id"] for d in sorted_dims]

    # Get codelist labels for all dimensions
    params = metadata.get_dataflow_parameters(dataflow_id)

    # Identify dimension types
    country_dim = "COUNTRY" if "COUNTRY" in dim_order else "REF_AREA"
    freq_dim = "FREQUENCY" if "FREQUENCY" in dim_order else "FREQ"
    transform_dim, unit_dim, _, _ = detect_transform_dimension(dataflow_id)
    # Use UNIT dimension as fallback for transform if no transform dimension exists
    effective_transform_dim = transform_dim or unit_dim

    # Parse dimension_values into a dict of DIM_ID -> VALUE
    # Input format: list of "DIM_ID:VALUE" strings
    extra_dimensions: dict[str, str] = {}
    if dimension_values:
        for dv in dimension_values:
            if not dv or not isinstance(dv, str):
                continue
            if ":" in dv:
                dim_id, dim_value = dv.split(":", 1)
                extra_dimensions[dim_id.strip().upper()] = dim_value.strip().upper()

    # dimension_values OVERRIDES parameter values for country/frequency/transform
    # Check if any country dimension is in extra_dimensions
    for cdim in ("COUNTRY", "REF_AREA", "JURISDICTION", "AREA"):
        if cdim in extra_dimensions:
            country = extra_dimensions.pop(cdim)
            break
    # Check if frequency dimension is in extra_dimensions
    for fdim in ("FREQUENCY", "FREQ"):
        if fdim in extra_dimensions:
            frequency = extra_dimensions.pop(fdim)
            break
    # Check if transform dimension is in extra_dimensions
    for tdim in ("UNIT_MEASURE", "UNIT", "TRANSFORMATION"):
        if tdim in extra_dimensions:
            transform = extra_dimensions.pop(tdim)
            break

    # Find indicator dimension - check which dimension contains the indicator_code
    # This list should include all possible indicator-type dimensions across dataflows
    indicator_dims = [
        "INDICATOR",
        "INDEX_TYPE",
        "COICOP_1999",
        "SERIES",
        "ITEM",
        "BOP_ACCOUNTING_ENTRY",
        "ACCOUNTING_ENTRY",
        "PRODUCTION_INDEX",
    ]

    # If we have indicator_code(s), find which dimension they belong to
    # indicator_code may be "+" joined (e.g., "F4_L_T_XDC+F12_L_T_XDC")
    indicator_dim = None
    first_indicator = indicator_code.split("+")[0] if indicator_code else None
    if first_indicator:
        for dim_id in indicator_dims:
            if dim_id in dim_order:
                dim_values = {p.get("value") for p in params.get(dim_id, [])}
                if first_indicator in dim_values:
                    indicator_dim = dim_id
                    break

        # If still not found, search ALL dimensions for the indicator code
        if indicator_dim is None:
            for dim_id in dim_order:
                if dim_id in (
                    country_dim,
                    freq_dim,
                    transform_dim,
                    unit_dim,
                    "TIME_PERIOD",
                ):
                    continue  # Skip known non-indicator dimensions
                dim_values = {p.get("value") for p in params.get(dim_id, [])}
                if first_indicator in dim_values:
                    indicator_dim = dim_id
                    break

    # Fallback to first available indicator dimension if not found
    if indicator_dim is None:
        indicator_dim = next((d for d in indicator_dims if d in dim_order), None)

    def build_key_with_indicator(target_dim: str) -> str:
        """Build constraint key with indicator always set, targeting a specific dimension.

        This builds a full key for all dimensions, with the target dimension as wildcard
        and the indicator dimension set to the indicator code (if available).
        This allows querying for available values of the target dimension filtered by indicator.
        """
        key_parts: list[str] = []
        for dim_id in dim_order:
            if dim_id == target_dim:
                # Target dimension gets wildcard - we want to know available values
                key_parts.append("*")
            elif dim_id == country_dim:
                key_parts.append(str(country).replace(",", "+") if country else "*")
            elif dim_id == indicator_dim:
                # Always include indicator code if available
                key_parts.append(indicator_code if indicator_code else "*")
            elif dim_id == freq_dim:
                key_parts.append(str(frequency) if frequency else "*")
            elif dim_id in (transform_dim, unit_dim):
                key_parts.append(
                    str(transform) if transform and transform != "true" else "*"
                )
            elif dim_id in extra_dimensions:
                # Use value from dimension_values if provided
                key_parts.append(extra_dimensions[dim_id])
            else:
                key_parts.append("*")

        return ".".join(key_parts)

    def get_choices_for_dim(dim_id: str) -> list:
        """Get available choices for a dimension using constraints API."""
        key = build_key_with_indicator(dim_id)
        constraints = metadata.get_available_constraints(
            dataflow_id=dataflow_id,
            key=key,
            component_id=dim_id,
        )
        # Get labels from params
        labels = {opt["value"]: opt["label"] for opt in params.get(dim_id, [])}
        # Also try to get labels from codelist
        codelist_labels: dict = {}
        dim_meta: dict = next((d for d in sorted_dims if d.get("id") == dim_id), {})

        if dim_meta:
            codelist_id = metadata._resolve_codelist_id(
                dataflow_id, dsd_id, dim_id, dim_meta
            )

            if codelist_id and codelist_id in metadata._codelist_cache:
                codelist_labels = metadata._codelist_cache.get(codelist_id, {})

        choices: list = []

        for kv in constraints.get("key_values", []):
            if kv.get("id") == dim_id:
                for value in kv.get("values", []):
                    # Try params first, then codelist, then fall back to value
                    label = labels.get(value) or codelist_labels.get(value) or value
                    choices.append({"label": label, "value": value})

        return choices

    # Step 1: No country selected - return country choices filtered by indicator
    if country == "true" and country_dim:
        choices = get_choices_for_dim(country_dim)
        choices = sorted(choices, key=lambda x: x["label"])
        choices.insert(0, {"label": "All Countries", "value": "*"})
        return choices

    # Step 2: Country selected, no frequency - return frequency choices
    if frequency == "true" and freq_dim:
        return get_choices_for_dim(freq_dim)

    # Step 3: Frequency selected, no transform - return transform choices
    if transform == "true" and effective_transform_dim:
        choices = get_choices_for_dim(effective_transform_dim)
        # Add "all" option at the beginning if there are choices
        if choices:
            choices.insert(0, {"label": "All", "value": "all"})
        return choices

    # All parameters set - no more choices needed
    return []


async def get_imf_utils_apps_json() -> list[dict[str, Any]]:
    """Get the IMF apps.json file.

    This endpoint serves the apps.json file containing OpenBB Workspace app configurations
    related to IMF data and utilities.

    It is automatically merged with any existing apps.json files in the Workspace and API.

    Returns
    -------
    list[dict[str, Any]]
        A list of OpenBB Workspace app configurations.
    """
    # pylint: disable=import-outside-toplevel
    import json
    from pathlib import Path

    apps_file = Path(__file__).parent / "apps.json"

    try:
        with apps_file.open("r", encoding="utf-8") as f:
            apps_json = json.load(f)
            return apps_json
    except Exception:
        return []


router._api_router.add_api_route(
    path="/apps.json",
    endpoint=get_imf_utils_apps_json,
    methods=["GET"],
    include_in_schema=False,
)
