"""OECD Utilities Router."""

from typing import Annotated, Any, Literal

from fastapi import Query
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.service.system_service import SystemService

from openbb_oecd.utils.metadata import OECDMetadataDependency

router = Router(prefix="", description="Utilities for OECD provider.")
api_prefix = SystemService().system_settings.api_settings.prefix
# Dimension IDs typically representing the country/reference area.
_COUNTRY_DIMS = ("REF_AREA", "COUNTERPART_AREA", "JURISDICTION", "COUNTRY", "AREA")
# Dimension IDs typically representing observation frequency.
_FREQ_DIMS = ("FREQ", "FREQUENCY")
# Dimension IDs typically representing a data transformation.
_TRANSFORM_DIMS = ("TRANSFORMATION", "UNIT_MEASURE", "ADJUSTMENT")


def _parse_annotation(text: str) -> dict[str, str]:
    """Parse a comma-separated ``DIM=VALUE`` annotation string.

    Works for both NOT_DISPLAYED and DEFAULT annotations.
    """
    result: dict[str, str] = {}
    if not text:
        return result
    for part in text.split(","):
        p = part.strip()
        if not p:
            continue
        if "=" in p:
            dim, val = p.split("=", 1)
            val = val.strip()
            if val.startswith("(") and val.endswith(")"):
                val = val[1:-1]
            result[dim.strip()] = val
        else:
            result[p] = ""
    return result


def _parse_not_displayed(annotations: dict[str, str]) -> dict[str, str]:
    """Parse NOT_DISPLAYED annotation into ``{dim_id: value}``."""
    return _parse_annotation(annotations.get("NOT_DISPLAYED", ""))


def _parse_defaults(annotations: dict[str, str]) -> dict[str, str]:
    """Parse DEFAULT annotation into ``{dim_id: value}``."""
    return _parse_annotation(annotations.get("DEFAULT", ""))


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get OECD topic choices for UI dropdowns.",
            parameters={},
        )
    ],
)
async def list_topic_choices(metadata: OECDMetadataDependency) -> list[dict[str, str]]:
    """Return [{label, value}] for every OECD topic (for dropdowns)."""
    from collections import Counter

    topics = metadata.list_topics()
    tm = metadata.table_map()
    topic_counts = Counter(r.get("topic_id", "") for r in tm)
    result = []
    for t in topics:
        count = topic_counts.get(t["id"], 0)
        if count > 0:
            result.append(
                {
                    "label": f"{t['name']} ({count})",
                    "value": t["id"],
                }
            )
    return sorted(result, key=lambda x: x["label"])


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get subtopic choices for a given topic.",
            parameters={"topic": "ECO"},
        )
    ],
)
async def list_subtopic_choices(
    metadata: OECDMetadataDependency,
    topic: Annotated[
        str | None,
        Query(
            title="Topic",
            description="Topic ID to get subtopics for (e.g. 'ECO').",
        ),
    ] = None,
) -> list[dict[str, str]]:
    """Return [{label, value}] for subtopics within a given topic (for dropdowns)."""
    from collections import Counter

    if not topic:
        return []

    t_upper = topic.upper()
    topics = metadata.list_topics()
    target = None

    for t in topics:
        if t["id"].upper() == t_upper:
            target = t
            break

    if not target:
        return []

    tm = metadata.table_map()
    sub_counts = Counter(
        r.get("subtopic_id", "") for r in tm if r.get("topic_id", "").upper() == t_upper
    )
    result = []

    for s in target.get("subtopics", []):
        count = sub_counts.get(s["id"], 0)
        if count > 0:
            result.append(
                {
                    "label": f"{s['name']} ({count})",
                    "value": s["id"],
                }
            )

    return sorted(result, key=lambda x: x["label"])


@router.command(
    methods=["GET"],
    widget_config={
        "name": "OECD Dataflows",
        "description": "All available OECD dataflows, optionally filtered by topic.",
        "params": [
            {
                "paramName": "topic",
                "label": "Topic",
                "value": None,
                "description": "Filter by topic. Leave blank to show all.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/oecd_utils/list_topic_choices",
                "style": {"popupWidth": 500},
                "optional": True,
            },
            {
                "paramName": "subtopic",
                "label": "Subtopic",
                "value": None,
                "description": "Filter by subtopic (requires a topic to be selected).",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/oecd_utils/list_subtopic_choices",
                "optionsParams": {"topic": "$topic"},
                "style": {"popupWidth": 500},
                "optional": True,
            },
        ],
        "gridData": {"w": 20, "h": 15},
        "refetchInterval": False,
        "source": ["OECD"],
        "category": "OECD Utilities",
        "subCategory": "Metadata",
    },
    examples=[
        APIEx(
            description="List all OECD dataflows.",
            parameters={},
        ),
        APIEx(
            description="Filter dataflows by topic.",
            parameters={"topic": "HEA"},
        ),
        PythonEx(
            description="List all OECD dataflows.",
            code=[
                "dataflows = obb.oecd.utils.list_dataflows()",
                "print(dataflows.results)",
            ],
        ),
    ],
)
async def list_dataflows(
    metadata: OECDMetadataDependency,
    topic: Annotated[
        str | None,
        Query(
            title="Topic",
            description=(
                "Filter dataflows by topic ID"
                " (e.g. 'ECO', 'HEA', 'ENV')."
                " Use list_topics() to see all available topics."
            ),
        ),
    ] = None,
    subtopic: Annotated[
        str | None,
        Query(
            title="Subtopic",
            description="Filter dataflows by subtopic ID within the selected topic.",
        ),
    ] = None,
) -> OBBject:
    """List all available OECD dataflows, optionally filtered by topic and subtopic."""
    dataflows = metadata.list_dataflows(topic=topic or None)

    if subtopic:
        needle = subtopic.upper()
        dataflows = [d for d in dataflows if d.get("subtopic", "").upper() == needle]

    rows = []

    for entry in dataflows:
        full_id = entry["value"]
        short_id = full_id.split("@")[-1] if "@" in full_id else full_id
        rows.append(
            {
                "dataflow_id": short_id,
                "name": entry.get("label", short_id),
                "topic": entry.get("topic_name", ""),
                "subtopic": entry.get("subtopic_name", ""),
            }
        )

    return OBBject(results=rows, provider="oecd")


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get OECD dataflow choices for UI dropdowns.",
            parameters={},
        )
    ],
)
async def list_dataflow_choices(
    metadata: OECDMetadataDependency,
) -> list[dict[str, str]]:
    """Return [{label, value}] for every OECD dataflow (for dropdowns)."""
    dataflows = metadata.list_dataflows()

    return sorted(
        [{"label": e.get("label", e["value"]), "value": e["value"]} for e in dataflows],
        key=lambda x: x["label"],
    )


@router.command(
    methods=["GET"],
    widget_config={
        "name": "OECD Topics",
        "description": "All OECD topic categories with dataflow counts.",
        "params": [
            {
                "paramName": "query",
                "label": "Search",
                "value": None,
                "description": "Filter by topic or subtopic name.",
                "optional": True,
            },
        ],
        "gridData": {"w": 30, "h": 20},
        "refetchInterval": False,
        "source": ["OECD"],
        "category": "OECD Utilities",
        "subCategory": "Metadata",
    },
    examples=[
        APIEx(description="List all OECD topics.", parameters={}),
        APIEx(description="Search topics.", parameters={"query": "health"}),
        PythonEx(
            description="Browse OECD topics and subtopics.",
            code=[
                "topics = obb.oecd.utils.list_topics()",
                "print(topics.results)",
            ],
        ),
    ],
)
async def list_topics(
    metadata: OECDMetadataDependency,
    query: Annotated[
        str | None,
        Query(
            title="Search",
            description="Filter rows by topic or subtopic name.",
        ),
    ] = None,
) -> OBBject:
    """List all OECD topic categories with dataflow counts."""
    topics = metadata.list_topics()

    rows = []

    for t in topics:
        if not t["dataflow_count"]:
            continue
        subs = t.get("subtopics", [])

        if subs:
            for s in subs:
                if not s["dataflow_count"]:
                    continue
                rows.append(
                    {
                        "topic_id": t["id"],
                        "topic": t["name"],
                        "subtopic_id": s["id"],
                        "subtopic": s["name"],
                        "dataflows": s["dataflow_count"],
                    }
                )
        else:
            rows.append(
                {
                    "topic_id": t["id"],
                    "topic": t["name"],
                    "subtopic_id": "",
                    "subtopic": "",
                    "dataflows": t["dataflow_count"],
                }
            )

    if query:
        needle = query.lower()
        rows = [
            r
            for r in rows
            if needle in r["topic"].lower() or needle in r["subtopic"].lower()
        ]

    return OBBject(results=rows, provider="oecd")


@router.command(
    methods=["GET"],
    widget_config={
        "name": "OECD Dataflow Parameters",
        "type": "markdown",
        "params": [
            {
                "paramName": "dataflow_id",
                "label": "Dataflow",
                "value": "DF_PRICES_ALL",
                "description": "The OECD dataflow to inspect.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/oecd_utils/list_dataflow_choices",
                "style": {"popupWidth": 700},
            },
            {
                "paramName": "output_format",
                "value": "markdown",
                "show": False,
            },
        ],
        "data": {"dataKey": "results"},
        "source": ["OECD"],
        "category": "OECD Utilities",
        "subCategory": "Metadata",
    },
    examples=[
        APIEx(
            description="Get parameters for the 'DF_PRICES_ALL' dataflow in markdown.",
            parameters={"dataflow_id": "DF_PRICES_ALL", "output_format": "markdown"},
        ),
        APIEx(
            description="Get parameters for the 'DF_CLI' dataflow as JSON.",
            parameters={"dataflow_id": "DF_CLI", "output_format": "json"},
        ),
        PythonEx(
            description="Inspect dimensions of the 'DF_QNA' dataflow.",
            code=[
                "params = obb.oecd.utils.get_dataflow_parameters('DF_QNA')",
                "print(params.results)",
            ],
        ),
    ],
)
async def get_dataflow_parameters(
    metadata: OECDMetadataDependency,
    dataflow_id: Annotated[
        str,
        Query(
            title="Dataflow",
            description="The OECD dataflow ID. Use list_dataflows() to see available dataflows.",
        ),
    ],
    output_format: Literal["json", "markdown"] = "json",
) -> OBBject:
    """Dataflow parameters and possible dimension values.

    Returns an OBBject with either a JSON dict or markdown string under results.
    """
    parameters = metadata.get_constrained_values(dataflow_id)

    if output_format == "json":
        return OBBject(results=parameters)

    sections: list[str] = []

    for dim_id, options in parameters.items():
        inner = "\n".join(
            f"| {opt['value']} | {opt.get('label', '')} |" for opt in options
        )
        table = f"| Code | Label |\n|---|---|\n{inner}"
        sections.append(
            f"<details>\n<summary><b>{dim_id}</b>"
            f" ({len(options)} values)</summary>"
            f"\n\n{table}\n\n</details>"
        )

    return OBBject(results="\n\n".join(sections), provider="oecd")


@router.command(
    methods=["GET"],
    widget_config={
        "name": "OECD Tables",
        "description": "Searchable map of all OECD tables, optionally filtered by topic.",
        "params": [
            {
                "paramName": "topic",
                "label": "Topic",
                "value": None,
                "description": "Filter by topic. Leave blank to show all.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/oecd_utils/list_topic_choices",
                "style": {"popupWidth": 700},
                "optional": True,
            },
            {
                "paramName": "subtopic",
                "label": "Subtopic",
                "value": None,
                "description": "Filter by subtopic (requires a topic to be selected).",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/oecd_utils/list_subtopic_choices",
                "optionsParams": {"topic": "$topic"},
                "style": {"popupWidth": 500},
                "optional": True,
            },
            {
                "paramName": "query",
                "label": "Search",
                "value": None,
                "description": "Keyword search across name, topic, and dataflow ID.",
                "optional": True,
            },
            {
                "paramName": "dataflow_id",
                "label": "Dataflow ID",
                "value": None,
                "description": "Filter by exact or partial dataflow ID (e.g. 'DF_PRICES_ALL').",
                "optional": True,
            },
        ],
        "gridData": {"w": 40, "h": 20},
        "refetchInterval": False,
        "source": ["OECD"],
        "category": "OECD Utilities",
        "subCategory": "Metadata",
    },
    examples=[
        APIEx(description="List all OECD tables.", parameters={}),
        APIEx(description="Search for GDP tables.", parameters={"query": "GDP"}),
        APIEx(description="Filter by topic.", parameters={"topic": "HEA"}),
        APIEx(
            description="Find a specific table by dataflow ID.",
            parameters={"dataflow_id": "DF_PRICES_ALL"},
        ),
        PythonEx(
            description="Search OECD tables.",
            code=[
                "tables = obb.oecd.utils.list_tables(query='prices')",
                "print(tables.results)",
            ],
        ),
    ],
)
async def list_tables(
    metadata: OECDMetadataDependency,
    query: Annotated[
        str | None,
        Query(
            title="Search",
            description=(
                "Keyword search. Space-separated terms"
                " are AND-ed; use | for OR within a word."
            ),
        ),
    ] = None,
    topic: Annotated[
        str | None,
        Query(
            title="Topic",
            description=(
                "Filter by topic ID (e.g. 'ECO', 'HEA')."
                " Use list_topics() to see all topics."
            ),
        ),
    ] = None,
    subtopic: Annotated[
        str | None,
        Query(
            title="Subtopic",
            description="Filter by subtopic ID within the selected topic.",
        ),
    ] = None,
    dataflow_id: Annotated[
        str | None,
        Query(
            title="Dataflow ID",
            description="Filter by exact or partial dataflow (table) ID (e.g. 'DF_PRICES_ALL').",
        ),
    ] = None,
) -> OBBject:
    """List all OECD tables with keyword search, topic, subtopic, and dataflow ID filtering."""
    rows = metadata.list_tables(
        query=query, topic=topic or None, subtopic=subtopic or None
    )

    if dataflow_id:
        needle = dataflow_id.upper()
        rows = [
            r
            for r in rows
            if needle in r["table_id"].upper() or needle in r["dataflow_id"].upper()
        ]

    return OBBject(results=rows, provider="oecd")


@router.command(
    methods=["GET"],
    widget_config={
        "name": "OECD Table Detail",
        "description": (
            "Full dimension breakdown for a single"
            " OECD table, including indicator hierarchy."
        ),
        "type": "markdown",
        "params": [
            {
                "paramName": "table_id",
                "label": "Table",
                "value": "DF_PRICES_ALL",
                "description": "The OECD table (dataflow) to inspect.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/oecd_utils/list_table_choices",
                "style": {"popupWidth": 950},
            },
        ],
        "data": {"dataKey": "results"},
        "gridData": {"w": 40, "h": 25},
        "refetchInterval": False,
        "source": ["OECD"],
        "category": "OECD Utilities",
        "subCategory": "Metadata",
    },
    examples=[
        APIEx(
            description="Get full detail for the DF_PRICES_ALL table.",
            parameters={"table_id": "DF_PRICES_ALL"},
        ),
        APIEx(
            description="Inspect a national accounts table.",
            parameters={"table_id": "DF_T725R_Q"},
        ),
        PythonEx(
            description="Describe a table.",
            code=[
                "detail = obb.oecd.utils.get_table_detail(table_id='DF_QNA')",
                "print(detail.results)",
            ],
        ),
    ],
)
async def get_table_detail(
    metadata: OECDMetadataDependency,
    table_id: Annotated[
        str,
        Query(
            title="Table",
            description="The OECD dataflow (table) ID. Use list_tables() to find IDs.",
        ),
    ],
) -> OBBject:
    """Full dimension and indicator breakdown for a single OECD table.

    Returns a markdown document with:
    - Table name and description
    - Each dimension as a collapsible section with allowed values
    - Table groups (TABLE_IDENTIFIER), if present
    - Indicator count and hierarchy summary
    """
    from openbb_oecd.utils.metadata import _TABLE_GROUP_CANDIDATES

    detail = metadata.describe_dataflow(table_id)
    short_id = detail.get("short_id", table_id)

    # Look up topic/subtopic/path from the table map for context
    table_row: dict = {}

    for row in metadata.table_map():
        if row["short_id"] == short_id or row["dataflow_id"] == detail.get(
            "dataflow_id"
        ):
            table_row = row
            break

    lines: list[str] = []

    # Header
    lines.append(f"# {detail.get('name', table_id)}")
    lines.append(f"**Dataflow ID:** `{short_id}`")

    path = table_row.get("path", "")

    if path:
        lines.append(f"\n**Category:** {path}")

    desc = detail.get("description", "")

    if desc:
        lines.append(f"\n{desc}")

    lines.append("")
    indicator_dim = detail.get("indicator_dimension")
    # Table groups (TABLE_IDENTIFIER) — show as the primary content with full descriptions
    table_groups = detail.get("table_groups", [])

    if table_groups:
        lines.append("## Tables\n")
        for g in table_groups:
            label = g.get("label", g["value"])
            description = g.get("description", "")
            lines.append(f"### {g['value']} — {label}")
            # Show description only if it adds something beyond the label
            if description and description != label:
                lines.append(f"\n{description}\n")
            else:
                lines.append("")

    # Identify the table-grouping dimension (if any) to skip in the dimensions section

    dimensions = detail.get("dimensions", [])
    _table_group_dim: str | None = None

    if table_groups:
        for _cand in _TABLE_GROUP_CANDIDATES:
            if any(d.get("id") == _cand for d in dimensions):
                _table_group_dim = _cand
                break

    # Dimensions — collapsible sections with code/label/description tables
    if dimensions:
        lines.append("## Dimensions\n")
        for dim in dimensions:
            dim_id = dim["id"]

            if dim_id == _table_group_dim:
                continue  # already shown above as table groups

            concept_name = dim.get("name", dim_id)
            values = dim.get("values", [])
            constrained = dim.get("constrained_codes", len(values))
            tag = " *(indicator dimension)*" if dim_id == indicator_dim else ""
            summary_label = f"`{dim_id}`"

            if concept_name and concept_name != dim_id:
                summary_label += f" — {concept_name}"

            summary_label += f"  ({constrained} values){tag}"
            lines.append(f"<details>\n<summary>{summary_label}</summary>\n")

            if values:
                lines.append("| Code | Label | Description |")
                lines.append("|---|---|---|")
                for v in values:
                    code = v.get("value", "")
                    lbl = v.get("label", "")
                    vdesc = " ".join(v.get("description", "").split())
                    desc_col = vdesc if vdesc and vdesc != lbl else ""
                    lines.append(f"| {code} | {lbl} | {desc_col} |")

            lines.append("\n</details>\n")

    # Indicator tree
    ind_count = detail.get("indicator_count", 0)

    if ind_count:
        lines.append(
            f"## Indicators\n\n**{ind_count}** indicators in dimension `{indicator_dim}`.\n"
        )
        tree = detail.get("indicator_tree", [])

        def _render_tree(nodes: list[dict], depth: int = 0) -> None:
            for node in nodes:
                indent = "  " * depth
                code = node.get("code", "")
                name = node.get("label", code)
                lines.append(f"{indent}- **{code}** — {name}")
                for child in node.get("children", []):
                    _render_tree([child], depth + 1)

        if tree:
            lines.append("<details>\n<summary>Indicator tree</summary>\n")
            _render_tree(tree)
            lines.append("\n</details>\n")

    return OBBject(results="\n".join(lines), provider="oecd")


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get table choices for dropdowns.",
            parameters={},
        )
    ],
)
async def list_table_choices(
    metadata: OECDMetadataDependency,
    topic: Annotated[
        str | None,
        Query(
            title="Topic",
            description="Filter choices by topic ID (e.g. 'ECO'). Leave blank for all.",
        ),
    ] = None,
) -> list[dict]:
    """Return [{label, value}] for OECD tables (for dropdowns), optionally filtered by topic."""
    tables = metadata.list_tables(topic=topic or None)
    seen: set[str] = set()
    choices = []

    for t in sorted(tables, key=lambda x: x["name"]):
        if t["table_id"] not in seen:
            seen.add(t["table_id"])
            choices.append(
                {
                    "label": t["name"],
                    "value": t["table_id"],
                    "extraInfo": {"description": t["table_id"]},
                }
            )

    return choices


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    include_in_schema=False,
    examples=[
        APIEx(
            description="Get country choices for the DF_CLI::LI symbol.",
            parameters={"symbol": "DF_CLI::LI", "country": "true"},
        ),
        APIEx(
            description="Get frequency choices after selecting a country.",
            parameters={"symbol": "DF_CLI::LI", "country": "AUS", "frequency": "true"},
        ),
    ],
)
async def indicator_choices(  # noqa: PLR0911,PLR0912
    metadata: OECDMetadataDependency,
    symbol: str | None = None,
    country: str | None = None,
    frequency: str | None = None,
    transform: str | None = None,
    dimension_values: list[str] | None = None,
) -> list[dict[str, str]]:
    """Progressive dimension choices for the OECD Economic Indicators widget.

    Called by the OpenBB Workspace UI in a stepped fashion:

    1. Provide symbol → returns country choices.
    2. Add country → returns frequency choices.
    3. Add frequency → returns transform choices (when the dataflow has one).

    Each step passes "true" as the value of the parameter being resolved.

    Parameters
    ----------
    symbol : str | None
        Dataflow and indicator in DATAFLOW::INDICATOR format.
        Multiple comma-separated symbols from the same dataflow are allowed.
    country : str | None
        Pass "true" to request country choices; otherwise the selected
        country code(s) used to narrow downstream options.
    frequency : str | None
        Pass "true" to request frequency choices.
    transform : str | None
        Pass "true" to request transformation choices.
    dimension_values : list[str] | None
        Already-selected extra dimension filters in DIM_ID:VALUE format,
        used to narrow choices.

    Returns
    -------
    list[dict[str, str]]
        [{label, value}] for the requested dimension.
    """
    from urllib.parse import unquote

    if not symbol:
        return []

    symbol = unquote(symbol)
    symbols = [s.strip() for s in symbol.split(",") if s.strip()]

    if not symbols:
        return []

    # Parse dataflow + indicator codes from the (possibly comma-joined) symbol.
    dataflows_seen: set[str] = set()
    indicator_codes: list[str] = []

    for sym in symbols:
        if "::" in sym:
            df_part, ind_part = sym.split("::", 1)
            dataflows_seen.add(df_part.strip())
            if ind_part.strip():
                indicator_codes.append(ind_part.strip())
        else:
            dataflows_seen.add(sym.strip())

    dataflow_id = next(iter(dataflows_seen), None)

    if not dataflow_id:
        return []

    try:
        dim_order = metadata.get_dimension_order(dataflow_id)
        # get_constrained_values uses embedded DSD constraints; no live call needed
        # as long as the dataflow structure is already cached.
        constrained = metadata.get_constrained_values(dataflow_id)
        params = metadata.get_dataflow_parameters(dataflow_id)
    except (ValueError, KeyError, AttributeError):
        return []

    # Identify each special dimension (take first matching dim in DSD order).
    country_dim = next((d for d in dim_order if d in _COUNTRY_DIMS), None)
    freq_dim = next((d for d in dim_order if d in _FREQ_DIMS), None)
    transform_dim = next((d for d in dim_order if d in _TRANSFORM_DIMS), None)
    full_id = metadata._resolve_dataflow_id(dataflow_id)
    nd_pins = _parse_not_displayed(
        metadata.dataflows.get(full_id, {}).get("annotations", {})
    )

    def _to_choices(dim_id: str) -> list[dict[str, str]]:
        """Convert constrained or full options for dim_id to label/value pairs."""
        entries = constrained.get(dim_id) or params.get(dim_id, [])
        return [
            {
                "label": e.get("label", e.get("value", "")),
                "value": str(e.get("value", "")),
            }
            for e in entries
            if e.get("value") is not None
        ]

    # Dispatch: each step passes "true" as the value of the dim being resolved.
    requesting = (
        "country"
        if country == "true"
        else (
            "frequency"
            if frequency == "true"
            else "transform"
            if transform == "true"
            else None
        )
    )

    if requesting == "country":
        if not country_dim:
            return []
        choices = sorted(_to_choices(country_dim), key=lambda x: x["label"])
        choices.insert(0, {"label": "All Countries", "value": "*"})
        return choices

    if requesting == "frequency":
        if not freq_dim or freq_dim in nd_pins:
            return []
        return _to_choices(freq_dim)

    if requesting == "transform":
        if not transform_dim or transform_dim in nd_pins:
            return []
        choices = _to_choices(transform_dim)
        if choices:
            choices.insert(0, {"label": "All", "value": "*"})
        return choices

    return []


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get the topic choices (step 0).",
            parameters={},
        ),
        APIEx(
            description="Get subtopic choices for the 'ECO' topic (step 1).",
            parameters={"topic": "ECO"},
        ),
        APIEx(
            description="Get table choices for topic and subtopic (step 2).",
            parameters={"topic": "ECO", "subtopic": "ECO.EO"},
        ),
        APIEx(
            description="Get country choices for a specific table (step 3).",
            parameters={
                "topic": "ECO",
                "subtopic": "ECO.EO",
                "table": "DF_QNA::T0101",
            },
        ),
        APIEx(
            description="Get frequency choices (step 4).",
            parameters={
                "topic": "ECO",
                "subtopic": "ECO.EO",
                "table": "DF_QNA::T0101",
                "country": "USA",
            },
        ),
    ],
)
async def presentation_table_choices(  # noqa: PLR0911,PLR0912
    metadata: OECDMetadataDependency,
    topic: str | None = None,
    subtopic: str | None = None,
    table: str | None = None,
    country: str | None = None,
    frequency: str | None = None,
) -> list[dict[str, str]]:
    """Get presentation table choices for OECD data retrieval.

    Progressive cascading selector using the OECD metadata taxonomy.
    All data is discovered dynamically from the OECD SDMX metadata —
    topics, subtopics, dataflows, and their TABLE_IDENTIFIER dimension
    values are resolved at runtime.

    Parameters
    ----------
    topic : str | None
        OECD topic code (e.g. 'ECO'). Omit to list all topics.
    subtopic : str | None
        OECD subtopic code (e.g. 'ECO.EO'). Enter a topic to see choices.
        Pure UI convenience — not required for API / Python usage.
    table : str | None
        Dataflow::table symbol (e.g. 'DF_QNA::T0101'). Enter a subtopic to see choices.
    country : str | None
        Country code. Enter a topic and table to see choices.
    frequency : str | None
        Frequency code. Enter topic, table, and country to see choices.

    Returns
    -------
    list[dict[str, str]]
        [{label, value}] choices for the current cascading step.
    """
    from collections import (
        Counter,
        defaultdict as _ddict,
    )

    from openbb_oecd.utils.progressive_helper import OecdParamsBuilder

    topic = topic if topic and topic.strip() else None
    subtopic = subtopic if subtopic and subtopic.strip() else None
    table = table if table and table.strip() else None
    country = country if country and country.strip() else None
    frequency = frequency if frequency and frequency.strip() else None

    # Step 0: No params → return topic choices from taxonomy.
    if topic is None:
        topics = metadata.list_topics()
        tm = metadata.table_map()
        topic_counts = Counter(r.get("topic_id", "") for r in tm)

        return sorted(
            [
                {
                    "label": f"{t['name']} ({topic_counts.get(t['id'], 0)})",
                    "value": t["id"],
                }
                for t in topics
                if topic_counts.get(t["id"], 0) > 0
            ],
            key=lambda x: x["label"],
        )

    # Step 1: topic selected → return subtopic choices.
    if topic is not None and subtopic is None:
        topics = metadata.list_topics()
        t_upper = topic.upper()
        tm = metadata.table_map()
        sub_counts = Counter(
            r.get("subtopic_id", "")
            for r in tm
            if r.get("topic_id", "").upper() == t_upper
        )
        for t in topics:
            if t["id"].upper() == t_upper:
                subtopics = t.get("subtopics", [])
                choices = sorted(
                    [
                        {
                            "label": f"{s['name']} ({sub_counts.get(s['id'], 0)} tables)",
                            "value": s["id"],
                        }
                        for s in subtopics
                        if sub_counts.get(s["id"], 0) > 0
                    ],
                    key=lambda x: x["label"],
                )
                # Single subtopic → auto-select.
                if len(choices) == 1:
                    return choices
                return choices

        return [{"label": "No subtopics found for this topic", "value": ""}]

    # Step 2: subtopic selected → return table choices.
    if table is None and topic is not None:
        dataflows = metadata.list_dataflows(topic=topic)
        sub_upper = subtopic.upper()
        dataflows = [
            df
            for df in dataflows
            if sub_upper in [s.upper() for s in df.get("all_subtopics", [])]
            or df.get("subtopic", "").upper() == sub_upper
        ]

        section_map = metadata._detect_section_families()
        # Remove section children — they'll be reintroduced via their
        # parent root below.
        dataflows = [df for df in dataflows if df["value"] not in section_map]
        _children_of: dict[str, list[str]] = _ddict(list)

        for _child, _parent in section_map.items():
            _children_of[_parent].append(_child)

        _expanded: list[dict] = []

        for df in dataflows:
            annots = metadata.dataflows.get(df["value"], {}).get("annotations", {})
            if (
                annots.get("NonProductionDataflow") == "true"
                and df["value"] in _children_of
            ):
                for child_id in _children_of[df["value"]]:
                    child_info = metadata.dataflows.get(child_id, {})
                    _expanded.append(
                        {
                            **df,
                            "label": child_info.get("name", df["label"]),
                            "value": child_id,
                        }
                    )
            else:
                _expanded.append(df)

        dataflows = _expanded
        country_family_map = metadata._detect_country_families()
        dataflows = [
            df
            for df in dataflows
            if df["value"] not in country_family_map
            or country_family_map[df["value"]]["representative"] == df["value"]
        ]

        # Collect candidates: for each TABLE_IDENTIFIER value, track
        # which dataflow has the most indicators.  Dataflows that are
        # just pre-filtered slices (fewer indicators) are dropped so
        # only the richest dataflow per table is shown.  Keyed by
        # (dsd_prefix, table_id) so that table IDs from different DSDs
        # (e.g. T0101 in DSD_NAMAIN10 vs DSD_NAMAIN1) don't collide.
        _best_for_table: dict[tuple[str, str], tuple[str, str, str, int]] = {}
        _no_group: list[dict[str, str]] = []
        # Minimum average indicators per table group.  Dataflows where
        # groups are just granular API slices (e.g. SUT developer tables
        # with 100+ TABLE_IDENTIFIER values and ~1 indicator each) are
        # not useful as presentation tables.
        min_indicators_per_group = 3

        for df in dataflows:
            full_id = df["value"]
            info = metadata.dataflows.get(full_id, {})
            short_id = info.get("short_id", full_id.split("@")[-1])
            # Only expand table groups when the DSD structure is already
            # cached in memory.  Calling get_table_groups / get_indicator_tree
            # on an uncached dataflow triggers _ensure_structure → network
            # fetch + LZMA cache write per dataflow, which is far too slow
            # for a dropdown endpoint that may iterate dozens of dataflows.
            structure_cached = full_id in metadata.datastructures
            groups = metadata.get_table_groups(short_id) if structure_cached else []

            if groups:
                tree = metadata.get_indicator_tree(short_id)

                def _count(nodes: list) -> int:
                    c = 0
                    for n in nodes:
                        c += 1
                        c += _count(n.get("children", []))  # noqa: B023
                    return c

                n_indicators = _count(tree)

                # When there are too many groups relative to indicators,
                # each group is a tiny slice — not a real presentation
                # table.  Offer the dataflow as a single flat entry.
                n_groups = len(groups)

                if n_groups > 1 and n_indicators / n_groups < min_indicators_per_group:
                    _no_group.append(
                        {
                            "label": df["label"],
                            "value": short_id,
                        }
                    )
                    continue

                for g in groups:
                    tid = g["value"]
                    dsd_prefix = full_id.split("@")[0] if "@" in full_id else full_id
                    key = (dsd_prefix, tid)
                    prev = _best_for_table.get(key)

                    if prev is None or n_indicators > prev[3]:
                        _best_for_table[key] = (
                            short_id,
                            df["label"],
                            g["label"],
                            n_indicators,
                        )
            else:
                _no_group.append(
                    {
                        "label": df["label"],
                        "value": short_id,
                    }
                )

        results: list[dict[str, str]] = list(_no_group)

        for (_, tid), (sid, df_label, tbl_label, _) in _best_for_table.items():
            results.append(
                {
                    "label": f"{df_label}: {tbl_label}",
                    "value": f"{sid}::{tid}",
                }
            )

        return sorted(results, key=lambda x: x["label"])

    # From here, table is a symbol like "DF_QNA::T0101" or "DF_PRICES_ALL".
    parts = table.split("::", 1)
    dataflow_id = parts[0]
    full_id = metadata._resolve_dataflow_id(dataflow_id)
    annotations = metadata.dataflows.get(full_id, {}).get("annotations", {})
    nd_pins = _parse_not_displayed(annotations)
    defaults = _parse_defaults(annotations)
    _TABLE_GROUP_DIMS = {"TABLE_IDENTIFIER", "CHAPTER"}
    # Collect single-value NOT_DISPLAYED pins for real DSD dimensions.
    _tmp_pb = OecdParamsBuilder(dataflow_id=dataflow_id)
    pb_dims = _tmp_pb.get_dimensions_in_order()
    pb_dim_set = set(pb_dims)
    nd_avail_pins: dict[str, str] = {}

    for dim_id, val in nd_pins.items():
        if (
            dim_id in pb_dim_set
            and dim_id not in _TABLE_GROUP_DIMS
            and val
            and "+" not in val
        ):
            nd_avail_pins[dim_id] = val

    # Build progressive helper with known pins applied in DSD order.
    country_dim = next((d for d in pb_dims if d in _COUNTRY_DIMS), None)
    freq_dim = next((d for d in pb_dims if d in _FREQ_DIMS), None)

    def _build_pb(
        pin_country: str | None = None,
        pin_freq: str | None = None,
    ) -> OecdParamsBuilder:
        _pb = OecdParamsBuilder(dataflow_id=dataflow_id)

        for _dim in _pb.get_dimensions_in_order():
            if _dim == country_dim and pin_country:
                _pb.set_dimension((_dim, pin_country.replace(",", "+")))
            elif (
                _dim == freq_dim and pin_freq is not None
            ):  # pragma: no cover - no caller passes pin_freq
                _pb.set_dimension(
                    (_dim, pin_freq)
                )  # pragma: no cover - body of pragma'd branch above
            elif _dim in nd_avail_pins:
                _pb.set_dimension((_dim, nd_avail_pins[_dim]))

        return _pb

    def _mark_default(
        options: list[dict[str, str]], dim_id: str
    ) -> list[dict[str, str]]:
        """Tag the option matching the DEFAULT annotation for *dim_id*."""
        default_val = defaults.get(dim_id)

        if not default_val:
            return options
        for opt in options:
            if opt["value"] == default_val:
                opt["default"] = "true"
                break

        return options

    # Step 3: table selected → return country choices (availability-filtered).
    if not country:
        if not country_dim:
            return [{"label": "Select a Table", "value": ""}]
        pb = _build_pb()
        options = pb.get_options_for_dimension(country_dim)
        return _mark_default(options, country_dim)

    # Step 4: country selected → return frequency choices.
    if frequency is None:
        if not freq_dim:
            return [{"label": "N/A (no frequency dimension)", "value": "_NA"}]
        if freq_dim in nd_pins:
            val = nd_pins[freq_dim]
            if val:
                labels = metadata.get_codelist_for_dimension(full_id, freq_dim)
                return [{"label": labels.get(val, val), "value": val}]
            return []
        pb = _build_pb(pin_country=country)
        options = pb.get_options_for_dimension(freq_dim)
        return _mark_default(options, freq_dim)

    return []


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    include_in_schema=False,
    examples=[
        APIEx(
            description="Get unit_measure choices.",
            parameters={
                "table": "DF_QNA::T0101",
                "country": "USA",
                "frequency": "Q",
                "dimension": "unit_measure",
            },
        ),
        APIEx(
            description="Get adjustment choices.",
            parameters={
                "table": "DF_QNA::T0101",
                "country": "USA",
                "frequency": "Q",
                "dimension": "adjustment",
            },
        ),
    ],
)
async def presentation_table_dim_choices(
    metadata: OECDMetadataDependency,
    table: str,
    dimension: str,
    country: str | None = None,
    frequency: str | None = None,
) -> list[dict[str, str | bool]]:
    """Return available values for a single dimension (unit, adjustment, transform).

    Independent of the other dimension selections — each dropdown queries
    this endpoint separately so they don’t block each other.

    Parameters
    ----------
    table : str
        Dataflow::table symbol (e.g. 'DF_QNA::T0101').
    country : str
        Country code(s).
    dimension : str
        Which dimension to query: 'unit_measure', 'adjustment', or 'transformation'.
    frequency : str | None
        Frequency code (optional — auto-resolved when only one exists).

    Returns
    -------
    list[dict[str, str | bool]]
        [{label, value, default?}] choices. ``default`` is a bool flag set
        on the option that matches the dataflow's DEFAULT annotation.
    """
    from openbb_oecd.utils.progressive_helper import OecdParamsBuilder

    dim_map: dict[str, str] = {
        "unit_measure": "UNIT_MEASURE",
        "adjustment": "ADJUSTMENT",
        "transformation": "TRANSFORMATION",
        "counterpart_area": "COUNTERPART_AREA",
        "counterpart": "COUNTERPART_AREA",
        "service": "SERVICE",
        "product": "PRODUCT",
        "sex": "SEX",
        "age": "AGE",
        "sector": "SECTOR",
        "education_lev": "EDUCATION_LEV",
    }
    _table: str | None = table if table and table.strip() else None
    country = country if country and country.strip() else None
    frequency = frequency if frequency and frequency.strip() else None

    if not _table:
        return []

    target_dim = dim_map.get(dimension.lower(), dimension.upper())

    parts = _table.split("::", 1)
    dataflow_id = parts[0]
    full_id = metadata._resolve_dataflow_id(dataflow_id)
    annotations = metadata.dataflows.get(full_id, {}).get("annotations", {})
    nd_pins = _parse_not_displayed(annotations)
    defaults = _parse_defaults(annotations)

    if target_dim in nd_pins:
        return []

    _TABLE_GROUP_DIMS = {"TABLE_IDENTIFIER", "CHAPTER"}
    pb = OecdParamsBuilder(dataflow_id=dataflow_id)
    dims_in_order = pb.get_dimensions_in_order()
    dims_in_order_set = set(dims_in_order)

    if target_dim not in dims_in_order_set:
        return []

    country_dim = next((d for d in dims_in_order if d in _COUNTRY_DIMS), None)
    freq_dim = next((d for d in dims_in_order if d in _FREQ_DIMS), None)

    # Pin known dimensions in DSD order to avoid clearing downstream pins.
    for dim_id in dims_in_order:
        if dim_id == country_dim and country:
            pb.set_dimension((dim_id, str(country).replace(",", "+")))
        elif dim_id == freq_dim and frequency is not None:
            pb.set_dimension((dim_id, frequency))
        elif (
            dim_id in nd_pins
            and dim_id not in _TABLE_GROUP_DIMS
            and nd_pins[dim_id]
            and "+" not in nd_pins[dim_id]
        ):
            pb.set_dimension((dim_id, nd_pins[dim_id]))

    if frequency is None and freq_dim and freq_dim in dims_in_order_set:
        freq_options = pb.get_options_for_dimension(freq_dim)

        if len(freq_options) == 1:
            pb.set_dimension((freq_dim, freq_options[0]["value"]))

    if (
        target_dim not in dims_in_order_set
    ):  # pragma: no cover - duplicate of earlier guard, dims_in_order_set is immutable
        return []  # pragma: no cover - body of pragma'd branch above

    not_applicable = {"not applicable", "not available", "n/a"}
    raw_options = pb.get_options_for_dimension(target_dim)
    options: list[dict[str, str | bool]] = [
        dict(o) for o in raw_options if o.get("label", "").lower() not in not_applicable
    ]

    if not options:
        return []

    default_val = defaults.get(target_dim)

    if default_val:
        for opt in options:
            if opt["value"] == default_val:
                opt["default"] = True
                break

    if len(options) == 1:
        return options

    options.insert(0, {"label": "All", "value": "all"})
    options.insert(0, {"label": "Auto", "value": "auto"})

    return options


@router.command(
    methods=["GET"],
    widget_config={
        "params": [
            {
                "paramName": "topic",
                "label": "Topic",
                "value": None,
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/oecd_utils/presentation_table_choices",
                "description": "The OECD topic.",
            },
            {
                "paramName": "subtopic",
                "label": "Subtopic",
                "value": None,
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/oecd_utils/presentation_table_choices",
                "optionsParams": {
                    "topic": "$topic",
                },
                "style": {"popupWidth": 500},
                "description": "Filter by subtopic. UI convenience only.",
                "show": True,
            },
            {
                "paramName": "table",
                "label": "Table",
                "type": "endpoint",
                "value": None,
                "optionsEndpoint": f"{api_prefix}/oecd_utils/presentation_table_choices",
                "optionsParams": {
                    "topic": "$topic",
                    "subtopic": "$subtopic",
                },
                "style": {"popupWidth": 950},
                "description": "The OECD presentation table (DATAFLOW::TABLE_ID).",
            },
            {
                "paramName": "country",
                "label": "Country",
                "description": "Country or region for the table.",
                "type": "endpoint",
                "multiSelect": True,
                "optionsEndpoint": f"{api_prefix}/oecd_utils/presentation_table_choices",
                "optionsParams": {
                    "topic": "$topic",
                    "subtopic": "$subtopic",
                    "table": "$table",
                },
            },
            {
                "paramName": "counterpart",
                "label": "Counterpart",
                "type": "endpoint",
                "multiSelect": True,
                "optionsEndpoint": f"{api_prefix}/oecd_utils/presentation_table_dim_choices",
                "optionsParams": {
                    "table": "$table",
                    "country": "$country",
                    "frequency": "$frequency",
                    "dimension": "counterpart_area",
                },
                "style": {"popupWidth": 400},
                "description": (
                    "Counterpart area for bilateral data."
                    " Leave blank for auto-selection (World)."
                ),
                "optional": True,
            },
            {
                "paramName": "frequency",
                "label": "Frequency",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/oecd_utils/presentation_table_choices",
                "optionsParams": {
                    "topic": "$topic",
                    "subtopic": "$subtopic",
                    "table": "$table",
                    "country": "$country",
                },
                "description": "The data frequency.",
            },
            {
                "paramName": "unit_measure",
                "label": "Unit Measure",
                "type": "endpoint",
                "value": None,
                "optionsEndpoint": f"{api_prefix}/oecd_utils/presentation_table_dim_choices",
                "optionsParams": {
                    "table": "$table",
                    "country": "$country",
                    "frequency": "$frequency",
                    "dimension": "unit_measure",
                },
                "style": {"popupWidth": 400},
                "description": "Unit of measure. Leave blank for auto-selection.",
            },
            {
                "paramName": "adjustment",
                "label": "Adjustment",
                "type": "endpoint",
                "value": None,
                "optionsEndpoint": f"{api_prefix}/oecd_utils/presentation_table_dim_choices",
                "optionsParams": {
                    "table": "$table",
                    "country": "$country",
                    "frequency": "$frequency",
                    "dimension": "adjustment",
                },
                "description": "Seasonal adjustment type. Leave blank for auto-selection.",
                "optional": True,
            },
            {
                "paramName": "transformation",
                "label": "Transformation",
                "type": "endpoint",
                "value": None,
                "optionsEndpoint": f"{api_prefix}/oecd_utils/presentation_table_dim_choices",
                "optionsParams": {
                    "table": "$table",
                    "country": "$country",
                    "frequency": "$frequency",
                    "dimension": "transformation",
                },
                "description": "Data transformation. Leave blank for auto-selection.",
                "optional": True,
            },
            {
                "paramName": "dimension_values",
                "label": "Dimension Values",
                "type": "text",
                "value": None,
                "description": "Dimension selection for filtering. Format: 'DIM_ID1:VAL1+VAL2.' "
                + "See the Metadata tab for available dimensions and values.",
                "multiple": True,
                "multiSelect": False,
            },
            {
                "paramName": "start_date",
                "label": "Start Date",
                "type": "date",
                "value": None,
                "description": "Earliest date to include (ISO format). Filters out obsolete data.",
                "optional": True,
            },
            {
                "paramName": "end_date",
                "label": "End Date",
                "type": "date",
                "value": None,
                "description": "Latest date to include (ISO format).",
                "optional": True,
            },
            {
                "paramName": "limit",
                "label": "Limit",
                "value": 5,
                "description": "Most recent N records to retrieve per series.",
                "type": "number",
            },
        ],
        "runButton": True,
        "refetchInterval": False,
        "name": "OECD Presentation Table",
        "description": "Presentation tables from the OECD database.",
        "source": ["OECD"],
        "category": "OECD Utilities",
        "subCategory": "Presentation Tables",
    },
    examples=[
        APIEx(
            description="Get quarterly GDP output table for the United States.",
            parameters={
                "topic": "ECO",
                "table": "DF_QNA::T0101",
                "country": "USA",
                "frequency": "Q",
                "limit": 4,
            },
        )
    ],
)
async def presentation_table(  # noqa: PLR0912
    topic: Annotated[
        str | None,
        Query(
            title="Topic",
            description="The OECD topic code."
            + " UI navigation aid — not required when table is provided directly.",
        ),
    ] = None,
    subtopic: Annotated[
        str | None,
        Query(
            title="Subtopic",
            description="The OECD subtopic code (e.g. 'ECO.EO')."
            + " UI navigation aid — not required when table is provided directly.",
        ),
    ] = None,
    table: Annotated[
        str | None,
        Query(
            title="Table",
            description="The OECD presentation table key."
            + " Accepts 'DATAFLOW::TABLE_ID' or bare 'DATAFLOW_ID'."
            + " See presentation_table_choices() for options.",
        ),
    ] = None,
    country: Annotated[
        str | None,
        Query(
            title="Country",
            description=(
                "Country code to filter the data."
                " Enter multiple codes by joining on '+'."
                " See presentation_table_choices() for options."
            ),
        ),
    ] = None,
    counterpart: Annotated[
        str | None,
        Query(
            title="Counterpart",
            description="Counterpart area code for bilateral data (e.g. 'W' for World, 'USA')."
            + " When omitted, auto-selected (defaults to World aggregate).",
        ),
    ] = None,
    frequency: Annotated[
        str | None,
        Query(
            title="Frequency",
            description="The data frequency. See presentation_table_choices() for options."
            + " Typical values are 'A' (annual), 'Q' (quarter), 'M' (month).",
        ),
    ] = None,
    unit_measure: Annotated[
        str | None,
        Query(
            title="Unit of Measure",
            description="Unit of measure code."
            + " E.g. 'XDC' (national currency), 'USD_EXC' (US dollars),"
            + " 'PS' (persons), 'PT_B1GQ' (% of GDP)."
            + " When omitted, auto-selected via availability.",
        ),
    ] = None,
    adjustment: Annotated[
        str | None,
        Query(
            title="Adjustment",
            description="Seasonal adjustment code."
            + " 'Y' = seasonally adjusted, 'N' = not adjusted."
            + " When omitted, prefers 'Y' where available, falls back to 'N'.",
        ),
    ] = None,
    transformation: Annotated[
        str | None,
        Query(
            title="Transformation",
            description="Data transformation code."
            + " E.g. 'N' (none), 'GY' (growth year-on-year), 'IX' (index)."
            + " When omitted, auto-selected via availability.",
        ),
    ] = None,
    dimension_values: Annotated[
        list[str] | str | None,
        Query(
            title="Dimension Values",
            description="Dimension selection for filtering. Format: 'DIM_ID1:VAL1+VAL2.'",
        ),
    ] = None,
    start_date: Annotated[
        str | None,
        Query(
            title="Start Date",
            description="Earliest date to include (ISO format, e.g. '2020-01-01')."
            + " Filters out obsolete rows that stopped reporting before this date.",
        ),
    ] = None,
    end_date: Annotated[
        str | None,
        Query(
            title="End Date",
            description="Latest date to include (ISO format, e.g. '2025-12-31').",
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(
            title="Limit",
            description="Maximum number of records to retrieve per series.",
        ),
    ] = 1,
) -> Any:
    """Get a formatted presentation table from the OECD database."""
    import re as _re_mod

    from openbb_core.app.model.abstract.error import OpenBBError
    from pandas import DataFrame

    from openbb_oecd.utils.helpers import oecd_date_to_python_date
    from openbb_oecd.utils.table_builder import OecdTableBuilder

    if table is None:
        raise OpenBBError(
            ValueError(
                "Please select a topic, subtopic, and table from the dropdown menus."
            )
        )
    if country is None:
        raise OpenBBError(
            ValueError("Please select a country and frequency from the dropdown menus.")
        )

    if frequency is not None and frequency.strip().upper() == "_NA":
        frequency = None

    # Parse dimension_values into kwargs for the table builder.
    extra_dims: dict[str, str] = {}

    # Explicit dimension parameters — handle special UI values.
    for _dim_id, _dim_val in [
        ("COUNTERPART_AREA", counterpart),
        ("UNIT_MEASURE", unit_measure),
        ("ADJUSTMENT", adjustment),
        ("TRANSFORMATION", transformation),
    ]:
        if _dim_val is not None and _dim_val.strip().lower() not in ("", "auto"):
            if _dim_val.strip().lower() == "all":
                extra_dims[_dim_id] = "*"
            else:
                extra_dims[_dim_id] = _dim_val.strip().upper()

    if dimension_values:
        dv_list = (
            [dimension_values]
            if isinstance(dimension_values, str)
            else dimension_values
        )
        for dv in dv_list:
            if not dv or not isinstance(dv, str):
                continue
            for pair in (p.strip() for p in dv.split(",") if p.strip()):
                if ":" in pair:
                    dim_id, dim_val = pair.split(":", 1)
                    extra_dims[dim_id.strip().upper()] = dim_val.strip().upper()

    # table can be "DF_QNA::T0101" or bare "DF_FDI_FLOW_AGGR"
    builder = OecdTableBuilder()
    try:
        result = builder.get_table(
            table_id=table,  # handles both "DF::TBL" and bare "DF" formats
            country=country,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            dimension_filters=extra_dims,
        )
    except (ValueError, OpenBBError) as exc:
        raise OpenBBError(str(exc)) from exc

    data_rows = result.get("data", [])

    if not data_rows:
        raise OpenBBError(ValueError("No data returned for the given parameters."))

    # Build output rows matching the expected format.
    table_meta = result.get("table_metadata", {})
    fixed_dims = table_meta.get("fixed_dimensions", {})
    # Build a subtitle describing units, currency, etc.
    # Multiplier is excluded because values are already expanded.
    skip_labels = {"not applicable", "not available", "n/a", "_z", ""}
    subtitle_parts: list[str] = []
    unit = table_meta.get("unit_measure", "")
    currency = table_meta.get("currency", "")
    price_base = table_meta.get("price_base", "")

    if unit and unit.lower() not in skip_labels:
        subtitle_parts.append(unit)

    if (
        currency
        and currency.lower() not in skip_labels
        and currency.lower() != unit.lower()
    ):
        subtitle_parts.append(currency)

    if price_base and price_base.lower() not in skip_labels:
        subtitle_parts.append(price_base)
    table_subtitle = ", ".join(subtitle_parts)
    fixed_country = ""

    for dim_key in ("REF_AREA", "COUNTRY", "AREA"):
        if dim_key in fixed_dims:
            fixed_country = fixed_dims[dim_key].get("label", "")
            break

    results_json: list[dict] = []
    # Collect per-row unit metadata to detect whether units vary.
    unit_keys = ("unit_measure", "currency_denom", "currency", "price_base")
    _row_units: list[str] = []
    _row_unit_parts: list[list[str]] = []

    for row in data_rows:
        time_str = row.get("time_period", "")
        parsed_date = oecd_date_to_python_date(time_str) if time_str else None
        country_val = row.get("ref_area", "") or row.get("country", "") or fixed_country
        # Build per-row unit description from available metadata.
        _parts: list[str] = []

        for _uk in unit_keys:
            _uv = row.get(_uk, "")
            if (
                _uv
                and str(_uv).lower() not in skip_labels
                and (not _parts or str(_uv).lower() != _parts[-1].lower())
            ):
                _parts.append(str(_uv))

        _row_unit = ", ".join(_parts)
        _row_units.append(_row_unit)
        _row_unit_parts.append(_parts)
        results_json.append(
            {
                "title": row.get("label", ""),
                "country": country_val,
                "date": str(parsed_date) if parsed_date else time_str,
                "value": row.get("value"),
                "order": row.get("order"),
                "level": row.get("level", 0),
                "_acct_sort": row.get("_acct_sort", 0),
                "_child_order": row.get("_child_order", 0),
                "_sub_order": row.get("_sub_order", 0),
                "_compound_order": row.get("_compound_order", 0),
                "code": row.get("code", ""),
                "is_header": row.get("is_category_header", False),
                "_unit_desc": _row_unit,
            }
        )

    # Determine if units vary across rows (excluding headers with no value).
    _unique_units = {
        r["_unit_desc"]
        for r in results_json
        if r.get("value") is not None and r["_unit_desc"]
    }
    _units_vary = len(_unique_units) > 1

    df = DataFrame(results_json)
    # Pivot: one row per indicator + accounting entry, dates as columns.
    _pivot_index = [
        "title",
        "country",
        "order",
        "level",
        "_acct_sort",
        "_child_order",
        "_sub_order",
        "_compound_order",
        "code",
        "is_header",
        "_unit_desc",
    ]
    if "date" in df.columns and "title" in df.columns:
        try:
            pivot_df = df.pivot_table(
                index=_pivot_index,
                columns="date",
                values="value",
                aggfunc="first",
            ).reset_index()

            pivot_df = pivot_df.sort_values(
                ["order", "_acct_sort", "_child_order", "_sub_order", "_compound_order"]
            )
            pivot_df.columns.name = None
            df = pivot_df
        except (KeyError, ValueError, TypeError):
            pass

    # When units vary per row, append the unit description to the title.
    if _units_vary and "_unit_desc" in df.columns:

        def _append_unit(row_data):
            title = str(row_data.get("title", ""))
            udesc = str(row_data.get("_unit_desc", ""))
            if udesc and row_data.get("is_header") is not True:
                return f"{title} ({udesc})"
            return title

        df["title"] = df.apply(_append_unit, axis=1)

    # Apply hierarchy indentation to titles.
    if "level" in df.columns:

        def _indent_title(row_data):
            lvl = int(row_data.get("level", 0) or 0)
            title = str(row_data.get("title", ""))
            if lvl > 0:
                return ">\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0" * lvl + title
            return title

        df["title"] = df.apply(_indent_title, axis=1)

    # Drop helper columns that shouldn't appear in the table.
    df = df.drop(
        columns=[
            "order",
            "level",
            "_acct_sort",
            "_child_order",
            "_sub_order",
            "_compound_order",
            "code",
            "is_header",
            "_unit_desc",
        ],
        errors="ignore",
    )

    # Drop country column when only one value (already in subtitle).
    if "country" in df.columns and df["country"].nunique() <= 1:
        df = df.drop(columns=["country"])

    # Reorder columns: title first, then date columns latest-first.
    def _is_date_col(c):
        return bool(_re_mod.match(r"\d{4}-\d{2}-\d{2}$", str(c)))

    _fixed_cols = [c for c in df.columns if not _is_date_col(c)]
    _date_cols = sorted(
        [c for c in df.columns if _is_date_col(c)],
        reverse=True,
    )
    df = df[_fixed_cols + _date_cols]
    records = df.to_dict(orient="records")
    # Prepend a title row with null values for all data columns.
    title_row = {"title": table_subtitle}

    for col in df.columns:
        if col != "title":
            title_row[col] = None  # type: ignore

    return [title_row] + records


async def get_oecd_utils_apps_json() -> list[dict[str, Any]]:
    """Get the OECD apps.json file.

    This endpoint serves the apps.json file containing OpenBB Workspace app configurations
    related to OECD data and utilities.

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
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


router._api_router.add_api_route(
    path="/apps.json",
    endpoint=get_oecd_utils_apps_json,
    methods=["GET"],
    include_in_schema=False,
)
