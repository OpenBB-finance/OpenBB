"""IMF Router."""

import re
from typing import Annotated, Any, Literal

from fastapi import Query
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OBBQuery
from openbb_core.app.router import Router
from openbb_core.app.service.system_service import SystemService

from openbb_imf.models.indicator_metadata import ImfTableMetadata
from openbb_imf.utils.constants import (
    PRESENTATION_TABLES,
    table_dataflow_choices,
    table_dataflow_map,
    table_name_map,
)
from openbb_imf.utils.metadata import ImfMetadata, ImfMetadataDependency

router = Router(prefix="", description="IMF provider router.")
api_prefix = SystemService().system_settings.api_settings.prefix


def _render_dataflows_markdown(metadata: ImfMetadata) -> str:
    """Render the full dataflow catalog as a markdown summary."""
    dataflows = metadata.dataflows
    all_tables = metadata.list_all_dataflow_tables()
    md_parts: list[str] = []

    for dataflow_id in sorted(dataflows.keys()):
        details = dataflows[dataflow_id]
        try:
            indicators = metadata.get_indicators_in(dataflow_id)
        except KeyError:
            indicators = []
        params = metadata.get_dataflow_parameters(dataflow_id)
        md_parts.append(f"## `{dataflow_id}` - {details.get('name', '')}\n\n")

        if indicators:
            md_parts.append(f"**Number of Series:** {len(indicators)}\n\n")
        if params:
            escaped = [f"`{p}`" for p in list(params)]
            md_parts.append(f"**Dimensions:** {', '.join(escaped)}\n\n")

        presentations = all_tables.get(dataflow_id, [])
        if presentations:
            md_parts.append("### Presentation Tables\n\n")
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
                md_parts.append(f"#### {pres_name}\n\n")
                if friendly_name:
                    md_parts.append(f"**Friendly Name:** `{friendly_name}`\n\n")
                md_parts.append(f"**Symbol:** `{symbol}`\n\n")
                if pres_desc and pres_desc != pres_name:
                    md_parts.append(f"{pres_desc}\n\n")

        md_parts.append(f"{details.get('description', '').strip()}\n\n")
        md_parts.append("---\n\n")

    return "".join(md_parts)


def _dump_economic_indicator_rows(results: Any) -> list[dict[str, Any]]:
    """Normalize fetcher output to a list of JSON-mode pydantic dumps."""
    rows: Any = results.result if hasattr(results, "result") else results
    if not rows:
        return []
    out: list[dict[str, Any]] = []
    for r in rows:
        if hasattr(r, "model_dump"):
            out.append(r.model_dump(mode="json", exclude_none=True))
        else:
            out.append(dict(r))
    return out


def _render_parameters_markdown(parameters: dict[str, list[dict]]) -> str:
    """Render dataflow parameters as a per-dimension code list."""
    parts: list[str] = []
    for dim, options in parameters.items():
        parts.append(f"### `{dim}`\n\n")
        for option in options:
            parts.append(f"- `{option.get('value', '')}` : {option.get('label')}\n\n")
        parts.append("---\n\n")
    return "".join(parts)


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
                "imf_dataflows = obb.imf.list_dataflows()",
                "print(imf_dataflows)",
            ],
        ),
    ],
)
async def list_dataflows(
    metadata: ImfMetadataDependency,
    output_format: Literal["json", "markdown"] = "json",
) -> OBBject:
    """List all available IMF dataflows."""
    if output_format == "markdown":
        return OBBject(results=_render_dataflows_markdown(metadata))
    return OBBject(results=metadata.dataflows)


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
                "optionsEndpoint": f"{api_prefix}/imf/list_dataflow_choices",
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
                "imf_params = obb.imf.get_dataflow_dimensions('CPI')",
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
    metadata: ImfMetadataDependency,
    dataflow_id: Annotated[
        str,
        Query(
            title="Dataflow",
            description="The IMF dataflow ID. Use `list_dataflows()` to see available dataflows.",
        ),
    ],
    output_format: Literal["json", "markdown"] = "json",
) -> OBBject:
    """Dataflow parameters and their possible values."""
    parameters = metadata.get_dataflow_parameters(dataflow_id)
    if output_format == "json":
        return OBBject(results=parameters)
    return OBBject(results=_render_parameters_markdown(parameters))


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
async def list_tables(
    metadata: ImfMetadataDependency,
) -> OBBject[list[ImfTableMetadata]]:
    """Get the list of presentation tables available from the IMF."""
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
async def list_table_choices(
    metadata: ImfMetadataDependency,
) -> list[dict[str, str]]:
    """Get presentation table choices for IMF data retrieval."""
    return [
        {"label": pres.get("name", ""), "value": f"{dataflow_id}::{pres.get('id', '')}"}
        for dataflow_id, presentations in metadata.list_all_dataflow_tables().items()
        for pres in presentations
    ]


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
async def list_dataflow_choices(
    metadata: ImfMetadataDependency,
) -> list[dict[str, str]]:
    """Get dataflow choices for IMF data retrieval."""
    choices = [
        {"label": details.get("name", ""), "value": dataflow_id}
        for dataflow_id, details in metadata.dataflows.items()
    ]
    return sorted(choices, key=lambda x: x["label"])


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get country choices for the IMF Balance of Payments dataflow.",
            parameters={},
        )
    ],
)
async def list_bop_country_choices(
    metadata: ImfMetadataDependency,
) -> list[dict[str, str]]:
    """Get country choices (label, ISO3 value) for the IMF Balance of Payments dataflow."""
    params = metadata.get_dataflow_parameters("BOP")
    choices: list[dict[str, str]] = []
    for entry in params.get("COUNTRY", []):
        code = entry.get("value")
        if not code:
            continue
        choices.append({"label": entry.get("label", code), "value": code.upper()})
    return sorted(choices, key=lambda x: x["label"])


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get country choices for the IMF Consumer Price Index dataflow.",
            parameters={},
        )
    ],
)
async def list_cpi_country_choices(
    metadata: ImfMetadataDependency,
) -> list[dict[str, str]]:
    """Get country choices (label, ISO3 value) for the IMF Consumer Price Index dataflow."""
    params = metadata.get_dataflow_parameters("CPI")
    choices: list[dict[str, str]] = []
    for entry in params.get("COUNTRY", []):
        code = entry.get("value")
        if not code:
            continue
        choices.append({"label": entry.get("label", code), "value": code.upper()})
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
    metadata: ImfMetadataDependency,
    dataflow_group: str | None = None,
    table: str | None = None,
    country: str | None = None,
    frequency: str | None = None,
) -> list[dict[str, str]]:
    """Get presentation table choices for IMF data retrieval.

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
    """
    from openbb_imf.utils.progressive_helper import ImfParamsBuilder

    choices: list[dict[str, str]] = []

    if dataflow_group is None:
        return table_dataflow_choices

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
            else "JURISDICTION"
            if "JURISDICTION" in params
            else "REF_AREA"
        )
        countries = params.get(country_dim, [])

        return sorted(countries, key=lambda x: x["label"])

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

    if dataflow_group is not None and table is not None and country is not None:
        table_id = PRESENTATION_TABLES.get(table, "")
        dataflow_id = table_id.split("::")[0]
        hierarchy_id = table_id.split("::", 1)[1] if "::" in table_id else None
        params = metadata.get_dataflow_parameters(dataflow_id)
        country_dim = "COUNTRY" if "COUNTRY" in params else "REF_AREA"
        freq_dim = "FREQUENCY" if "FREQUENCY" in params else "FREQ"

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

        options = pb.get_options_for_dimension(freq_dim) if freq_dim else []

        return options

    return choices  # pragma: no cover -- unreachable: all four branches above are exhaustive


_INDENT_UNIT = ">\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0"


def _indent_title(title: str, level: int) -> str:
    """Prepend ``>``-prefixed indent markers proportional to ``level``."""
    if not isinstance(title, str):
        return title
    if level <= 0:
        return title
    return _INDENT_UNIT * level + title


def _rewrap_indent(title: str) -> str:
    """Replace leading whitespace with ``_INDENT_UNIT`` markers per 3-space step."""
    if not isinstance(title, str):
        return title
    stripped = title.lstrip(" ")
    leading = len(title) - len(stripped)
    if leading == 0:
        return stripped
    level = leading // 3
    return _INDENT_UNIT * level + stripped


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@router.command(
    methods=["GET"],
    widget_config={
        "params": [
            {
                "paramName": "dataflow_group",
                "label": "Dataflow",
                "value": None,
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/imf/presentation_table_choices",
                "description": "The IMF dataflow group.",
            },
            {
                "paramName": "table",
                "label": "Table",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/imf/presentation_table_choices",
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
                "multiSelect": False,
                "optionsEndpoint": f"{api_prefix}/imf/presentation_table_choices",
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
                "optionsEndpoint": f"{api_prefix}/imf/presentation_table_choices",
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
        ],
        "runButton": True,
        "refetchInterval": False,
        "name": "IMF Presentation Table",
        "description": "Presentation tables from the IMF database.",
        "source": ["IMF"],
        "category": "IMF Data",
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
) -> list[dict[str, Any]]:
    """Get a presentation table from the IMF database as native AG Grid rows."""
    from openbb_imf.models.economic_indicators import ImfEconomicIndicatorsFetcher

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
    rows = _dump_economic_indicator_rows(results)

    keep_country = len({c.strip() for c in re.split(r"[+,]", country) if c.strip()}) > 1

    out: list[dict[str, Any]] = []
    for row in rows:
        level = row.get("level")
        title = row.get("title", "")
        if level is None:
            title = _rewrap_indent(title)
        else:
            try:
                lvl = int(level)
            except (TypeError, ValueError):
                lvl = 0
            title = _indent_title(title, lvl)

        ordered: dict[str, Any] = {}
        if keep_country and "country" in row:
            ordered["country"] = row["country"]
        ordered["title"] = title
        date_pairs: list[tuple[str, Any]] = []
        trailing: list[tuple[str, Any]] = []
        for k, v in row.items():
            if k in ("country", "title", "level"):
                continue
            if isinstance(k, str) and _DATE_RE.match(k):
                date_pairs.append((k, v))
            else:
                trailing.append((k, v))
        date_pairs.sort(key=lambda kv: kv[0], reverse=True)
        for k, v in date_pairs:
            ordered[k] = v
        for k, v in trailing:
            ordered[k] = v
        out.append(ordered)

    return out


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
    metadata: ImfMetadataDependency,
    symbol: str | None = None,
    country: str | None = None,
    frequency: str | None = None,
    transform: str | None = None,
    dimension_values: list[str] | None = None,
) -> list[dict[str, str]]:
    """Get progressive indicator choices for IMF data retrieval.

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
    from urllib.parse import unquote

    from openbb_imf.utils.helpers import detect_transform_dimension

    if symbol is None:
        return []

    symbol = unquote(symbol)

    symbols = [s.strip() for s in symbol.split(",") if s.strip()]
    if not symbols:
        return []

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
            dataflows_seen.add(sym.strip())

    dataflow_id = list(dataflows_seen)[0] if dataflows_seen else None
    indicator_code = "+".join(indicator_codes) if indicator_codes else None

    if not dataflow_id:
        return []

    df_obj = metadata.dataflows.get(dataflow_id, {})

    if not df_obj:
        return []

    dsd_id = df_obj.get("structureRef", {}).get("id")
    dsd = metadata.datastructures.get(dsd_id, {})
    dimensions = dsd.get("dimensions", [])

    sorted_dims = sorted(
        [d for d in dimensions if d.get("id") != "TIME_PERIOD"],
        key=lambda x: int(x.get("position", 0)),
    )
    dim_order = [d["id"] for d in sorted_dims]

    params = metadata.get_dataflow_parameters(dataflow_id)

    country_dim = "COUNTRY" if "COUNTRY" in dim_order else "REF_AREA"
    freq_dim = "FREQUENCY" if "FREQUENCY" in dim_order else "FREQ"
    transform_dim, unit_dim, _, _ = detect_transform_dimension(dataflow_id)
    effective_transform_dim = transform_dim or unit_dim

    extra_dimensions: dict[str, str] = {}
    if dimension_values:
        for dv in dimension_values:
            if not dv or not isinstance(dv, str):
                continue
            if ":" in dv:
                dim_id, dim_value = dv.split(":", 1)
                extra_dimensions[dim_id.strip().upper()] = dim_value.strip().upper()

    for cdim in ("COUNTRY", "REF_AREA", "JURISDICTION", "AREA"):
        if cdim in extra_dimensions:
            country = extra_dimensions.pop(cdim)
            break
    for fdim in ("FREQUENCY", "FREQ"):
        if fdim in extra_dimensions:
            frequency = extra_dimensions.pop(fdim)
            break
    for tdim in ("UNIT_MEASURE", "UNIT", "TRANSFORMATION"):
        if tdim in extra_dimensions:
            transform = extra_dimensions.pop(tdim)
            break

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

    indicator_dim = None
    first_indicator = indicator_code.split("+")[0] if indicator_code else None
    if first_indicator:
        for dim_id in indicator_dims:
            if dim_id in dim_order:
                dim_values = {p.get("value") for p in params.get(dim_id, [])}
                if first_indicator in dim_values:
                    indicator_dim = dim_id
                    break

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

    if indicator_dim is None:
        indicator_dim = next((d for d in indicator_dims if d in dim_order), None)

    def build_key_with_indicator(target_dim: str) -> str:
        """Build constraint key with indicator always set, targeting a specific dimension."""
        key_parts: list[str] = []
        for dim_id in dim_order:
            if dim_id == target_dim:
                key_parts.append("*")
            elif dim_id == country_dim:
                key_parts.append(str(country).replace(",", "+") if country else "*")
            elif dim_id == indicator_dim:
                key_parts.append(indicator_code if indicator_code else "*")
            elif dim_id == freq_dim:
                key_parts.append(str(frequency) if frequency else "*")
            elif dim_id in (transform_dim, unit_dim):
                key_parts.append(
                    str(transform) if transform and transform != "true" else "*"
                )
            elif dim_id in extra_dimensions:
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
        labels = {opt["value"]: opt["label"] for opt in params.get(dim_id, [])}
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
                    label = labels.get(value) or codelist_labels.get(value) or value
                    choices.append({"label": label, "value": value})

        return choices

    if country == "true" and country_dim:
        choices = get_choices_for_dim(country_dim)
        choices = sorted(choices, key=lambda x: x["label"])
        choices.insert(0, {"label": "All Countries", "value": "*"})
        return choices

    if frequency == "true" and freq_dim:
        return get_choices_for_dim(freq_dim)

    if transform == "true" and effective_transform_dim:
        choices = get_choices_for_dim(effective_transform_dim)
        if choices:
            choices.insert(0, {"label": "All", "value": "all"})
        return choices

    return []


from openbb_imf import ECONOMY_INSTALLED  # noqa: E402

if not ECONOMY_INSTALLED:

    @router.command(
        model="AvailableImfIndicators",
        examples=[
            APIEx(
                description="Search the full IMF indicator catalog.",
                parameters={"provider": "imf"},
            ),
            APIEx(
                description="Filter the catalog to specific dataflows.",
                parameters={"provider": "imf", "dataflows": "CPI,PCPS"},
            ),
        ],
    )
    async def available_indicators(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Search the IMF SDMX indicator catalog by query, dataflow, or keyword."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="ImfIndicators",
        examples=[
            APIEx(
                description="Fetch a single indicator series by ``dataflow::code`` symbol.",
                parameters={
                    "provider": "imf",
                    "symbol": "IL::RGV_REVS",
                    "country": "*",
                    "frequency": "month",
                    "limit": 1,
                    "start_date": "2025-09-30",
                },
            ),
            APIEx(
                description="Fetch a full presentation table for a country.",
                parameters={
                    "provider": "imf",
                    "symbol": "DIP::H_DIP_INDICATOR",
                    "country": "BRA",
                    "frequency": "annual",
                    "limit": 2,
                    "pivot": True,
                },
            ),
        ],
    )
    async def indicators(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Fetch IMF economic indicators or presentation tables by ``dataflow::code`` symbol."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="ImfConsumerPriceIndex",
        examples=[
            APIEx(
                description="Latest CPI basket weightings reported by the IMF.",
                parameters={
                    "provider": "imf",
                    "country": "CAN",
                    "transform": "weight_percent",
                    "expenditure": "all",
                    "limit": 1,
                },
            ),
        ],
    )
    async def cpi(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Consumer Price Index (CPI) data from the IMF."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="ImfBalanceOfPayments",
        examples=[
            APIEx(parameters={"provider": "imf"}),
            APIEx(parameters={"provider": "imf", "country": "BRA"}),
        ],
    )
    async def balance_of_payments(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Balance of Payments reports from the IMF BOP dataflow."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="ImfDirectionOfTrade",
        examples=[
            APIEx(
                parameters={
                    "provider": "imf",
                    "country": "all",
                    "counterpart": "china",
                },
            ),
            APIEx(
                description="Select multiple countries or counterparts by entering a comma-separated list.",
                parameters={
                    "provider": "imf",
                    "country": "us",
                    "counterpart": "world,eu",
                    "frequency": "annual",
                    "direction": "exports",
                },
            ),
        ],
    )
    async def direction_of_trade(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Direction Of Trade Statistics (DOTS) from the IMF database."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="ImfPortInfo",
        examples=[
            APIEx(parameters={"provider": "imf"}),
            APIEx(parameters={"provider": "imf", "continent": "asia_pacific"}),
        ],
    )
    async def port_info(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """General metadata and statistics for all IMF Port Watch ports."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="ImfPortVolume",
        examples=[
            APIEx(
                description="Daily port calls and estimated trading volumes for specific ports.",
                parameters={
                    "provider": "imf",
                    "port_code": "rotterdam,singapore",
                },
            ),
            APIEx(
                description="All ports in a specific country (ISO3 code).",
                parameters={"provider": "imf", "country": "GBR"},
            ),
        ],
    )
    async def port_volume(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Daily port calls and estimated trading volumes from IMF Port Watch."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="ImfMaritimeChokePointInfo",
        examples=[APIEx(parameters={"provider": "imf"})],
    )
    async def chokepoint_info(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Metadata and statistics for all IMF Port Watch maritime chokepoints."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="ImfMaritimeChokePointVolume",
        examples=[
            APIEx(parameters={"provider": "imf"}),
            APIEx(
                parameters={
                    "provider": "imf",
                    "chokepoint": "suez_canal,panama_canal",
                }
            ),
        ],
    )
    async def chokepoint_volume(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Daily transit calls and estimated trade volumes for shipping chokepoints."""
        return await OBBject.from_query(OBBQuery(**locals()))


from openbb_imf.portwatch_router import portwatch_router  # noqa: E402

router.include_router(portwatch_router, prefix="/portwatch")


_APPS_WIDGET_ID_FALLBACK_MAP = {
    "economy_available_indicators_imf_obb": "imf_available_indicators_imf_obb",
    "economy_indicators_imf_obb": "imf_indicators_imf_obb",
    "economy_balance_of_payments_imf_obb": "imf_balance_of_payments_imf_obb",
    "economy_cpi_imf_obb": "imf_cpi_imf_obb",
    "economy_direction_of_trade_imf_obb": "imf_direction_of_trade_imf_obb",
    "economy_shipping_chokepoint_volume_imf_obb": "imf_chokepoint_volume_imf_obb",
    "economy_shipping_port_info_imf_obb": "imf_port_info_imf_obb",
    "economy_shipping_port_volume_imf_obb": "imf_port_volume_imf_obb",
}


def _rewrite_widget_ids(apps_json: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Swap ``economy_*_imf_obb`` widget IDs for their ``imf_*_imf_obb`` fallbacks."""
    for app in apps_json:
        tabs = app.get("tabs", {}) or {}
        for tab in tabs.values():
            for widget in tab.get("layout", []) or []:
                widget_id = widget.get("i")
                if widget_id in _APPS_WIDGET_ID_FALLBACK_MAP:
                    widget["i"] = _APPS_WIDGET_ID_FALLBACK_MAP[widget_id]
    return apps_json


async def get_imf_apps_json() -> list[dict[str, Any]]:
    """Get the IMF apps.json file.

    Returns
    -------
    list[dict[str, Any]]
        A list of OpenBB Workspace app configurations.
    """
    import json
    from pathlib import Path

    apps_file = Path(__file__).parent / "apps.json"

    try:
        with apps_file.open("r", encoding="utf-8") as f:
            apps_json = json.load(f)
    except Exception:
        return []

    if not ECONOMY_INSTALLED:
        apps_json = _rewrite_widget_ids(apps_json)

    return apps_json


router._api_router.add_api_route(
    path="/apps.json",
    endpoint=get_imf_apps_json,
    methods=["GET"],
    include_in_schema=False,
)
