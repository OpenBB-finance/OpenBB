"""Generate the EIA dataset catalog asset and the checked-in model modules from the APIv2 metadata tree."""

import argparse
import json
import lzma
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


def _catalog_helpers():
    """Load ``utils/catalog.py`` directly, without importing the package ``__init__``."""
    import importlib.util

    module = globals().get("_CATALOG_HELPERS")
    if module is None:
        spec = importlib.util.spec_from_file_location(
            "_eia_catalog_helpers", Path(__file__).parent / "catalog.py"
        )
        if spec is None or spec.loader is None:
            raise ImportError("Unable to load openbb_us_eia/utils/catalog.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        globals()["_CATALOG_HELPERS"] = module
    return module


def attach_params(choices: list[dict]) -> list[dict]:
    """Attach param slugs via the runtime catalog helper."""
    return _catalog_helpers().attach_params(choices)


API_BASE = "https://api.eia.gov/v2"
PACKAGE_ROOT = Path(__file__).parent.parent
ASSET_PATH = PACKAGE_ROOT / "assets" / "eia_catalog.json.xz"

CHOICES_LIMIT = 1000

FACET_CANONICAL: dict[str, dict[str, str]] = {
    "coal": {
        "censusRegionId": "census_region",
        "coalRankId": "coal_rank",
        "coalSupplier": "coal_supplier",
        "coalType": "coal_rank",
        "contractType": "contract_type",
        "countryId": "country",
        "customsDistrictId": "customs_district",
        "exportImportType": "export_import_type",
        "location": "state_region",
        "marketTypeId": "market_type",
        "mineBasinId": "mine_basin",
        "mineCountyId": "mine_county",
        "mineMSHAId": "mine",
        "mineStateId": "mine_state",
        "mineStatusId": "mine_status",
        "mineTypeId": "mine_type",
        "mississippiRegionId": "mississippi_region",
        "plant": "plant",
        "plantId": "plant",
        "plantStateId": "plant_state",
        "rank": "coal_rank",
        "regionId": "mine_region",
        "sector": "sector",
        "stateId": "state_region",
        "stateRegionId": "state_region",
        "supplyRegionId": "supply_region",
        "transportationMode": "transportation_mode",
    },
    "petroleum": {
        "duoarea": "region",
        "product": "product",
        "process": "process",
        "series": "series",
    },
    "natural_gas": {
        "duoarea": "region",
        "product": "product",
        "process": "process",
        "series": "series",
    },
    "electricity": {
        "balancing_authority_code": "balancing_authority",
        "energy_source_code": "energy_source",
        "entityid": "entity",
        "fuel2002": "fuel",
        "fuelType": "fuel_type",
        "fueltypeid": "fuel",
        "generatorid": "generator",
        "location": "state",
        "plantCode": "plant",
        "plantid": "plant",
        "primeMover": "prime_mover",
        "prime_mover_code": "prime_mover",
        "sector": "sector",
        "sectorid": "sector",
        "state": "state",
        "stateid": "state",
        "status": "status",
        "technology": "technology",
        "unit": "unit",
    },
    "electricity_grid": {
        "fromba": "from_ba",
        "fueltype": "fuel_type",
        "parent": "parent",
        "respondent": "respondent",
        "subba": "subregion",
        "timezone": "timezone",
        "toba": "to_ba",
        "type": "series_type",
    },
    "state_electricity_profiles": {
        "energysourceid": "energy_source",
        "fuelid": "fuel",
        "producertypeid": "producer_type",
        "sector": "sector",
        "state": "state",
        "stateID": "state",
        "stateId": "state",
        "stateid": "state",
        "technology": "technology",
        "timePeriod": "time_period",
    },
    "crude_oil_imports": {
        "destinationId": "destination",
        "destinationType": "destination_type",
        "gradeId": "grade",
        "originId": "origin",
        "originType": "origin_type",
    },
    "international": {
        "activityId": "activity",
        "countryRegionId": "country",
        "countryRegionTypeId": "country_type",
        "dataFlagId": "data_flag",
        "productId": "product",
        "unit": "unit",
    },
    "seds": {
        "seriesId": "series",
        "stateId": "state",
    },
    "total_energy": {
        "msn": "msn",
    },
    "densified_biomass": {
        "fuelTypeId": "fuel_type",
        "region": "region",
        "respondent": "respondent",
        "stateId": "state",
        "status": "status",
    },
    "nuclear_outages": {
        "facility": "facility",
        "generator": "generator",
    },
    "aeo": {
        "history": "history",
        "regionId": "region",
        "scenario": "scenario",
        "seriesId": "series",
        "tableId": "table",
    },
    "ieo": {
        "history": "history",
        "regionId": "region",
        "scenario": "scenario",
        "seriesId": "series",
        "tableId": "table",
    },
}

LITERAL_FACETS: dict[str, set[str]] = {
    "coal": {
        "census_region",
        "contract_type",
        "export_import_type",
        "market_type",
        "mine_basin",
        "mine_region",
        "mine_status",
        "mine_type",
        "mississippi_region",
        "supply_region",
        "transportation_mode",
    },
    "electricity": {"status"},
    "electricity_grid": {"series_type", "timezone"},
    "state_electricity_profiles": {"fuel", "producer_type", "time_period"},
    "crude_oil_imports": {"destination_type", "grade", "origin_type"},
    "international": {"activity", "country_type", "unit"},
    "densified_biomass": {"fuel_type", "region", "status"},
    "nuclear_outages": {"generator"},
    "aeo": {"history"},
    "ieo": {"history"},
}

NON_FILTER_FACETS: set[tuple[str, str]] = {
    ("international", "data_flag"),
}

PETROLEUM_DUPLICATE_PATHS = {
    "petroleum/move/imc1",
    "petroleum/move/imc2",
    "petroleum/move/imc3",
    "petroleum/move/ipct",
    "petroleum/move/land1",
    "petroleum/move/land2",
    "petroleum/move/land3",
}

GRID_DATASETS: dict[str, dict[str, str]] = {
    "demand": {
        "hourly": "electricity/rto/region-data",
        "daily": "electricity/rto/daily-region-data",
    },
    "generation_by_fuel": {
        "hourly": "electricity/rto/fuel-type-data",
        "daily": "electricity/rto/daily-fuel-type-data",
    },
    "interchange": {
        "hourly": "electricity/rto/interchange-data",
        "daily": "electricity/rto/daily-interchange-data",
    },
    "demand_by_subregion": {
        "hourly": "electricity/rto/region-sub-ba-data",
        "daily": "electricity/rto/daily-region-sub-ba-data",
    },
}

ELECTRICITY_DATASETS = {
    "electricity/electric-power-operational-data",
    "electricity/facility-fuel",
    "electricity/operating-generator-capacity",
    "electricity/retail-sales",
}

STRING_DATA_COLUMNS = {
    "county",
    "operating_company",
    "operating_company_address",
    "operating_year_month",
    "planned_derate_year_month",
    "planned_retirement_year_month",
    "planned_uprate_year_month",
    "prime_source",
    "refuse_flag",
}

SLUG_REPLACEMENTS = [
    ("f.o.b.", "fob"),
    ("u.s.", "us"),
    ("no. 2", "no2"),
    ("no. 4", "no4"),
]

SLUG_MAX_LENGTH = 60

SLUG_OVERRIDES: dict[str, str] = {
    "natural-gas/enr/adng": "associated_dissolved_proved_reserves",
    "natural-gas/enr/nang": "nonassociated_proved_reserves",
    "natural-gas/enr/ngpl": "plant_liquids_in_proved_reserves",
    "natural-gas/pri/rescom": "residential_and_commercial_prices_selected_states",
    "natural-gas/stor/lng": "lng_storage_additions_and_withdrawals",
    "petroleum/crd/cplc": "crude_plus_lease_condensate_proved_reserves",
    "petroleum/move/netr": "net_receipts_between_pad_districts",
    "petroleum/move/ptb": "movements_between_pad_districts",
    "petroleum/move/rail": "movements_by_rail_between_pad_districts",
    "petroleum/move/wimpc": "weekly_crude_imports_by_top_10_origins",
    "petroleum/pnp/feedng": "natural_gas_feedstock_for_hydrogen",
    "petroleum/pri/dfp2": "crude_first_purchase_prices_selected_streams",
    "petroleum/stoc/ts": "stocks_of_selected_products",
    "electricity/state-electricity-profiles/emissions-by-state-by-fuel": (
        "emissions_by_state_by_fuel"
    ),
}


_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


def snake_case(name: str) -> str:
    """Convert an API identifier to snake_case."""
    return _CAMEL_RE.sub("_", name.replace("-", "_")).lower()


def slugify(name: str) -> str:
    """Build a snake_case dataset slug from a display name."""
    text = name.lower()
    text = re.sub(r"\(.*?\)", "", text)
    text = text.split(" - deprecated", 1)[0]
    text = text.split(" - discontinued", 1)[0]
    for old, new in SLUG_REPLACEMENTS:
        text = text.replace(old, new)
    text = re.sub(r"[^0-9a-z]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def fetch_tree(api_key: str) -> dict[str, Any]:
    """Crawl the EIA APIv2 metadata tree.

    Parameters
    ----------
    api_key : str
        EIA Open Data API key.

    Returns
    -------
    dict[str, Any]
        Mapping with ``root``, ``nodes`` and ``facet_values`` keys matching the
        structure consumed by ``build_catalog``.
    """
    import requests  # noqa: PLC0415

    session = requests.Session()
    lock = threading.Lock()
    count = {"n": 0}

    def get(url: str) -> dict:
        for attempt in range(6):
            try:
                response = session.get(url, params={"api_key": api_key}, timeout=30)
            except requests.RequestException:
                time.sleep(2**attempt)
                continue
            if response.status_code == 200:
                with lock:
                    count["n"] += 1
                return response.json().get("response", {})
            if response.status_code in (409, 429, 500, 502, 503, 504):
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"HTTP {response.status_code} for {url}")
        raise RuntimeError(f"Retries exhausted for {url}")

    root = get(API_BASE)
    nodes: dict[str, dict] = {}
    to_visit = [route["id"] for route in root.get("routes", [])]

    while to_visit:
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {
                pool.submit(get, f"{API_BASE}/{path}"): path for path in to_visit
            }
            next_visit: list[str] = []
            for future in as_completed(futures):
                path = futures[future]
                node = future.result()
                nodes[path] = node
                for child in node.get("routes", []) or []:
                    next_visit.append(f"{path}/{child['id']}")
        to_visit = next_visit

    facet_values: dict[str, dict[str, dict]] = {}
    jobs = [
        (path, facet["id"])
        for path, node in nodes.items()
        if not node.get("routes")
        for facet in node.get("facets", []) or []
    ]
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {
            pool.submit(get, f"{API_BASE}/{path}/facet/{facet_id}"): (path, facet_id)
            for path, facet_id in jobs
        }
        for future in as_completed(futures):
            path, facet_id = futures[future]
            try:
                result = future.result()
            except RuntimeError as exc:
                sys.stderr.write(f"facet fetch failed for {path}/{facet_id}: {exc}\n")
                continue
            facet_values.setdefault(path, {})[facet_id] = {
                "total": result.get("totalFacets", 0),
                "values": result.get("facets", []) or [],
            }

    return {"root": root, "nodes": nodes, "facet_values": facet_values}


def _child_meta(tree: dict[str, Any]) -> dict[str, dict]:
    """Map each node path to the name/description its parent advertises for it."""
    meta: dict[str, dict] = {}
    for route in tree["root"].get("routes", []):
        meta[route["id"]] = route
    for path, node in tree["nodes"].items():
        for child in node.get("routes", []) or []:
            meta[f"{path}/{child['id']}"] = child
    return meta


def _frequency_spec(node: dict, path: str) -> dict[str, dict]:
    """Build the frequency specification for one API route node."""
    return {
        freq["id"]: {
            "format": freq.get("format", ""),
            "description": freq.get("description", ""),
            "path": path,
        }
        for freq in node.get("frequency", []) or []
    }


def _data_columns(node: dict) -> dict[str, dict]:
    """Build the data column specification for one API route node."""
    columns: dict[str, dict] = {}
    for data_id, spec in (node.get("data") or {}).items():
        detail = spec if isinstance(spec, dict) else {}
        snake = snake_case(data_id)
        columns[snake] = {
            "id": data_id,
            "alias": detail.get("alias"),
            "units": detail.get("units"),
            "numeric": snake not in STRING_DATA_COLUMNS,
        }
    return columns


def _is_placeholder(value_id: str, label: str) -> bool:
    """Detect placeholder vocabulary values the API cannot filter on."""
    return (
        value_id.strip().upper() == "(NA)" or label.strip().lower() == "not applicable"
    )


def _facet_spec(
    group: str,
    node: dict,
    path: str,
    facet_values: dict[str, dict[str, dict]],
) -> dict[str, dict]:
    """Map one node's facets onto canonical parameter names."""
    canonical_map = FACET_CANONICAL[group]
    spec: dict[str, dict] = {}
    for facet in node.get("facets", []) or []:
        facet_id = facet["id"]
        if facet_id not in canonical_map:
            raise KeyError(
                f"Unmapped facet id '{facet_id}' for group '{group}' at {path}"
            )
        canonical = canonical_map[facet_id]
        totals = facet_values.get(path, {}).get(facet_id, {})
        entry: dict[str, Any] = {
            "id": facet_id,
            "description": facet.get("description") or facet.get("name") or facet_id,
            "n_values": totals.get("total", 0),
        }
        if (group, canonical) in NON_FILTER_FACETS:
            entry["filterable"] = False
        values = totals.get("values", []) or []
        if values and len(values) <= CHOICES_LIMIT:
            deduped: dict[str, dict] = {}
            for value in values:
                code = str(value.get("id"))
                label = str(value.get("name") or value.get("alias") or value.get("id"))
                if _is_placeholder(code, label):
                    continue
                deduped.setdefault(code, {"value": code, "label": label})
            entry["choices"] = attach_params(
                sorted(deduped.values(), key=lambda choice: choice["label"])
            )
        spec[canonical] = entry
    return spec


def _merge_choices(
    accumulator: dict[str, dict[str, str]],
    group: str,
    node: dict,
    path: str,
    facet_values: dict[str, dict[str, dict]],
) -> None:
    """Accumulate facet value choices for one node into the group union."""
    canonical_map = FACET_CANONICAL[group]
    for facet in node.get("facets", []) or []:
        canonical = canonical_map[facet["id"]]
        entry = facet_values.get(path, {}).get(facet["id"], {})
        union = accumulator.setdefault(canonical, {})
        for value in entry.get("values", []):
            value_id = str(value.get("id"))
            label = str(value.get("name") or value.get("alias") or value_id)
            if _is_placeholder(value_id, label):
                continue
            union.setdefault(value_id, label)


def _dataset_entry(
    group: str,
    path: str,
    tree: dict[str, Any],
    child_meta: dict[str, dict],
) -> dict[str, Any]:
    """Build one dataset specification from an API route node."""
    node = tree["nodes"][path]
    meta = child_meta.get(path, {})
    name = node.get("name") or meta.get("name") or path
    description = node.get("description") or meta.get("description") or ""
    category_path = path.rsplit("/", 1)[0]
    category = None
    if "/" in path:
        category = (child_meta.get(category_path) or {}).get("name")
    return {
        "path": path,
        "name": re.sub(r"\s+", " ", str(name)).strip(),
        "description": re.sub(r"\s+", " ", str(description)).strip(),
        "category": category,
        "category_slug": slugify(category) if category else None,
        "frequencies": _frequency_spec(node, path),
        "default_frequency": node.get("defaultFrequency"),
        "start_period": node.get("startPeriod"),
        "end_period": node.get("endPeriod"),
        "data_columns": _data_columns(node),
        "facets": _facet_spec(group, node, path, tree["facet_values"]),
    }


def _leaves_under(tree: dict[str, Any], prefix: str) -> list[str]:
    """List leaf route paths under a prefix, sorted."""
    return sorted(
        path
        for path, node in tree["nodes"].items()
        if (path == prefix or path.startswith(prefix + "/")) and not node.get("routes")
    )


def _named_group(
    group: str,
    tree: dict[str, Any],
    child_meta: dict[str, dict],
    paths: list[str],
    slug_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a catalog group whose dataset slugs derive from display names."""
    datasets: dict[str, dict] = {}
    choices: dict[str, dict[str, str]] = {}
    for path in paths:
        entry = _dataset_entry(group, path, tree, child_meta)
        slug = (
            (slug_overrides or {}).get(path)
            or SLUG_OVERRIDES.get(path)
            or slugify(entry["name"])
        )
        if len(slug) > SLUG_MAX_LENGTH:
            raise ValueError(
                f"Slug '{slug}' for {path} exceeds {SLUG_MAX_LENGTH} chars;"
                " add a SLUG_OVERRIDES entry."
            )
        if slug in datasets:
            raise ValueError(f"Duplicate dataset slug '{slug}' for {path} in '{group}'")
        datasets[slug] = entry
        _merge_choices(choices, group, tree["nodes"][path], path, tree["facet_values"])
    return {"datasets": dict(sorted(datasets.items())), "choices": choices}


def _grid_group(tree: dict[str, Any], child_meta: dict[str, dict]) -> dict[str, Any]:
    """Build the electricity grid group, merging hourly and daily route pairs."""
    datasets: dict[str, dict] = {}
    choices: dict[str, dict[str, str]] = {}
    for slug, paths in GRID_DATASETS.items():
        hourly = _dataset_entry("electricity_grid", paths["hourly"], tree, child_meta)
        daily = _dataset_entry("electricity_grid", paths["daily"], tree, child_meta)
        entry = hourly
        entry["frequencies"].update(daily["frequencies"])
        for canonical, facet in daily["facets"].items():
            if canonical not in entry["facets"]:
                facet["frequencies"] = sorted(daily["frequencies"])
                entry["facets"][canonical] = facet
        entry["start_period"] = min(
            filter(None, [hourly["start_period"], daily["start_period"]]), default=None
        )
        entry["end_period"] = max(
            filter(None, [hourly["end_period"], daily["end_period"]]), default=None
        )
        datasets[slug] = entry
        for path in paths.values():
            _merge_choices(
                choices,
                "electricity_grid",
                tree["nodes"][path],
                path,
                tree["facet_values"],
            )
    return {"datasets": dict(sorted(datasets.items())), "choices": choices}


def build_catalog(tree: dict[str, Any]) -> dict[str, Any]:
    """Assemble the full catalog from a crawled metadata tree.

    Parameters
    ----------
    tree : dict[str, Any]
        Crawl output with ``root``, ``nodes`` and ``facet_values``.

    Returns
    -------
    dict[str, Any]
        The catalog document written to ``assets/eia_catalog.json.xz``.
    """
    child_meta = _child_meta(tree)
    groups: dict[str, dict] = {}

    groups["coal"] = _named_group("coal", tree, child_meta, _leaves_under(tree, "coal"))
    groups["petroleum"] = _named_group(
        "petroleum",
        tree,
        child_meta,
        [
            path
            for path in _leaves_under(tree, "petroleum")
            if path not in PETROLEUM_DUPLICATE_PATHS
        ],
    )
    groups["natural_gas"] = _named_group(
        "natural_gas", tree, child_meta, _leaves_under(tree, "natural-gas")
    )
    groups["electricity"] = _named_group(
        "electricity", tree, child_meta, sorted(ELECTRICITY_DATASETS)
    )
    groups["electricity_grid"] = _grid_group(tree, child_meta)
    groups["state_electricity_profiles"] = _named_group(
        "state_electricity_profiles",
        tree,
        child_meta,
        _leaves_under(tree, "electricity/state-electricity-profiles"),
    )
    groups["crude_oil_imports"] = _named_group(
        "crude_oil_imports",
        tree,
        child_meta,
        ["crude-oil-imports"],
        slug_overrides={"crude-oil-imports": "crude_oil_imports"},
    )
    groups["international"] = _named_group(
        "international",
        tree,
        child_meta,
        ["international"],
        slug_overrides={"international": "international"},
    )
    groups["seds"] = _named_group(
        "seds", tree, child_meta, ["seds"], slug_overrides={"seds": "seds"}
    )
    groups["total_energy"] = _named_group(
        "total_energy",
        tree,
        child_meta,
        ["total-energy"],
        slug_overrides={"total-energy": "total_energy"},
    )
    groups["densified_biomass"] = _named_group(
        "densified_biomass", tree, child_meta, _leaves_under(tree, "densified-biomass")
    )
    groups["nuclear_outages"] = _named_group(
        "nuclear_outages", tree, child_meta, _leaves_under(tree, "nuclear-outages")
    )
    groups["aeo"] = _named_group(
        "aeo",
        tree,
        child_meta,
        _leaves_under(tree, "aeo"),
        slug_overrides={
            path: path.split("/", 1)[1] for path in _leaves_under(tree, "aeo")
        },
    )
    groups["ieo"] = _named_group(
        "ieo",
        tree,
        child_meta,
        _leaves_under(tree, "ieo"),
        slug_overrides={
            path: path.split("/", 1)[1] for path in _leaves_under(tree, "ieo")
        },
    )

    for group in groups.values():
        group["choices"] = {
            canonical: attach_params(
                [
                    {"value": value, "label": label}
                    for value, label in sorted(values.items(), key=lambda kv: kv[1])
                ]
            )
            for canonical, values in sorted(group["choices"].items())
            if len(values) <= CHOICES_LIMIT
        }

    return {"groups": groups}


MODELS_ROOT = PACKAGE_ROOT / "models"

CHOICE_TYPE_LIMIT = 100

SCHEMA_CHOICES_LIMIT = 100

FLAT_GROUPS = (
    "crude_oil_imports",
    "international",
    "seds",
    "total_energy",
)

RELEASE_GROUPS = ("aeo", "ieo")

EXTRA_DATA_FIELDS: dict[str, dict[str, str]] = {
    "petroleum": {"units": "Unit of the value."},
    "natural_gas": {"units": "Unit of the value."},
    "aeo": {"unit": "Unit of the value."},
    "ieo": {"unit": "Unit of the value."},
    "seds": {"unit": "Unit of the value."},
    "total_energy": {"unit": "Unit of the value."},
    "international": {},
}


def _pascal(name: str) -> str:
    """Convert a snake_case name to PascalCase."""
    return "".join(part.capitalize() for part in name.split("_"))


def _base_name(group: str, dataset: str) -> str:
    """Build the model class base name for one dataset."""
    if group in FLAT_GROUPS or group in RELEASE_GROUPS:
        return f"Eia{_pascal(group)}"
    return f"Eia{_pascal(group)}{_pascal(dataset)}"


def _literal_annotation(values: list[str]) -> str:
    """Render a ``Literal[...] | None`` annotation source string."""
    unique = list(dict.fromkeys(values))
    body = ", ".join(json.dumps(value) for value in unique)
    return f"Literal[{body}] | None"


def _field(name: str, annotation: str, description: str) -> str:
    """Render one optional pydantic field definition."""
    return (
        f"    {name}: {annotation} = Field(\n"
        f"        default=None,\n"
        f"        description={json.dumps(description)},\n"
        f"    )\n"
    )


def _dataset_summary(spec: dict) -> str:
    """Build the one-line summary for a dataset, safe for CLI rendering."""
    name = (
        spec["name"]
        .replace("U.S.", "US")
        .replace("F.O.B.", "FOB")
        .replace("No. ", "No ")
        .replace("\\", "/")
        .rstrip(".")
    )
    description = spec.get("description") or ""
    return f"{name}." + (f" {description}" if description else "")


def _data_type_description(spec: dict) -> str:
    """Spell out every data column with its alias and units."""
    parts = []
    for column, detail in spec["data_columns"].items():
        label = detail.get("alias") or column.replace("_", " ")
        entry = (
            column
            if label.lower() == column.replace("_", " ")
            else f"{column} = {label}"
        )
        if detail.get("units"):
            entry += f" ({detail['units']})"
        parts.append(entry)
    return (
        "Data column(s) to return, comma-separated."
        " The default returns every column."
        f" Choices: {'; '.join(parts)}."
    )


def _is_filter(facet: dict) -> bool:
    """Return True when a facet is a real filter, not a single fixed value."""
    if facet.get("filterable") is False:
        return False
    return len(facet.get("choices") or []) != 1


def _facet_query_field(group: str, canonical: str, facet: dict) -> str:
    """Render one facet filter field for a query params class."""
    choices = facet.get("choices") or []
    single_select = canonical in LITERAL_FACETS.get(group, set())
    if choices and single_select and len(choices) <= CHOICE_TYPE_LIMIT:
        annotation = _literal_annotation(
            [choice.get("param") or choice["value"] for choice in choices]
        )
        description = f"{facet['description']} filter."
    else:
        annotation = "str | None"
        description = (
            f"{facet['description']} filter. Accepts a comma-separated list of values."
        )
        if not choices:
            description += " Use the `facet_options` endpoint for the valid values."
        elif len(choices) > SCHEMA_CHOICES_LIMIT:
            description += (
                f" There are {len(choices)} valid values -"
                " use the `facet_options` endpoint to list them."
            )
    restricted = facet.get("frequencies")
    if restricted:
        description += f" Only applies to frequency: {', '.join(restricted)}."
    return _field(canonical, annotation, description)


def _schema_extra_source(spec: dict, dataset_field: str | None = None) -> str:
    """Render the ``__json_schema_extra__`` literal for a query params class."""
    lines = ["    __json_schema_extra__ = {"]
    if len(spec["data_columns"]) > 1:
        data_choices = json.dumps(list(spec["data_columns"]))
        lines.append(
            f'        "data_type": {{"multiple_items_allowed": True,'
            f' "choices": {data_choices}}},'
        )
    for canonical, facet in spec["facets"].items():
        if not _is_filter(facet):
            continue
        choices = facet.get("choices") or []
        entry = '{"multiple_items_allowed": True'
        if choices and len(choices) <= SCHEMA_CHOICES_LIMIT:
            params = list(
                dict.fromkeys(
                    choice.get("param") or choice["value"] for choice in choices
                )
            )
            entry += f', "choices": {json.dumps(params)}'
        entry += "}"
        lines.append(f'        "{canonical}": {entry},')
    _ = dataset_field
    lines.append("    }")
    return "\n".join(lines) + "\n"


def _query_params_source(
    group: str,
    dataset: str,
    spec: dict,
    release_datasets: list[str] | None = None,
) -> str:
    """Render the query params class for one dataset."""
    base = _base_name(group, dataset)
    summary = _dataset_summary(spec)
    lines = [
        f"class {base}QueryParams(EiaApiQueryParams):",
        f'    """{summary}',
        "",
        f"    Source: https://www.eia.gov/opendata/browser/{spec['path']}",
        '    """',
        "",
        f'    __group__ = "{group}"',
    ]
    releases = list(release_datasets or [])
    if release_datasets is None:
        lines.append(f'    __dataset__ = "{dataset}"')
    elif len(releases) == 1:
        lines.append(f'    __dataset__ = "{releases[0]}"')
    lines.append(_schema_extra_source(spec).rstrip("\n"))
    lines.append("")
    body: list[str] = []
    if len(releases) > 1:
        annotation = _literal_annotation(releases).removesuffix(" | None")
        default = json.dumps(sorted(releases)[-1])
        body.append(
            f"    release: {annotation} = Field(\n"
            f"        default={default},\n"
            f'        description="The {spec["category"] or group} release."\n'
            '        " Facet values vary by release;'
            ' use the `facet_options` endpoint to list them.",\n'
            "    )\n"
        )
    frequencies = list(spec["frequencies"])
    if len(frequencies) > 1:
        default_frequency = spec.get("default_frequency") or frequencies[0]
        body.append(
            _field(
                "frequency",
                _literal_annotation(frequencies),
                f"The data frequency. The default is '{default_frequency}'.",
            )
        )
    if len(spec["data_columns"]) > 1:
        body.append(_field("data_type", "str | None", _data_type_description(spec)))
    for canonical, facet in spec["facets"].items():
        if not _is_filter(facet):
            continue
        body.append(_facet_query_field(group, canonical, facet))
    lines.append("".join(body).rstrip("\n"))
    return "\n".join(lines) + "\n"


def _data_source(group: str, dataset: str, spec: dict) -> str:
    """Render the data class for one dataset."""
    base = _base_name(group, dataset)
    lines = [
        f"class {base}Data(EiaApiData):",
        f'    """{_dataset_summary(spec)}"""',
        "",
    ]
    body: list[str] = []
    for canonical, facet in spec["facets"].items():
        body.append(_field(canonical, "str | None", f"{facet['description']} code."))
        body.append(
            _field(f"{canonical}_name", "str | None", f"{facet['description']} name.")
        )
    for column, detail in spec["data_columns"].items():
        if any(part.startswith(f"    {column}:") for part in body):
            raise ValueError(
                f"Data column '{column}' collides with a facet field"
                f" in '{spec['path']}'."
            )
        label = detail.get("alias") or column.replace("_", " ").capitalize()
        description = label + (f" ({detail['units']})" if detail.get("units") else "")
        annotation = "float | None" if detail.get("numeric", True) else "str | None"
        if detail.get("numeric", True):
            description += ". Withheld or unavailable values return as null."
        body.append(_field(column, annotation, description))
    for extra_name, extra_description in EXTRA_DATA_FIELDS.get(group, {}).items():
        body.append(_field(extra_name, "str | None", extra_description))
    lines.append("".join(body).rstrip("\n"))
    return "\n".join(lines) + "\n"


def _fetcher_source(group: str, dataset: str, spec: dict) -> str:
    """Render the fetcher class for one dataset."""
    base = _base_name(group, dataset)
    summary = _dataset_summary(spec).split(". ")[0].rstrip(".")
    return f'''class {base}Fetcher(Fetcher[{base}QueryParams, list[{base}Data]]):
    """{summary} fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> {base}QueryParams:
        """Transform the query parameters."""
        return transform_dataset_query({base}QueryParams, params)

    @staticmethod
    async def aextract_data(
        query: {base}QueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: {base}QueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[{base}Data]:
        """Transform the data."""
        return transform_dataset_data({base}Data, query, data)
'''


def render_dataset_module(
    group: str,
    dataset: str,
    spec: dict,
    release_datasets: list[str] | None = None,
) -> str:
    """Render one complete dataset model module.

    Parameters
    ----------
    group : str
        Catalog group name.
    dataset : str
        Dataset slug; for release groups, the spec's release used as template.
    spec : dict
        Dataset specification.
    release_datasets : list[str] | None
        Release keys when rendering an aeo/ieo-style release module.

    Returns
    -------
    str
        The module source code.
    """
    header = (
        f'"""{_dataset_summary(spec).split(". ")[0].rstrip(".")} model."""\n\n'
        "from typing import Any, Literal\n\n"
        "from openbb_core.provider.abstract.fetcher import Fetcher\n"
        "from pydantic import Field\n\n"
        "from openbb_us_eia.utils.api_query import (\n"
        "    EiaApiData,\n"
        "    EiaApiQueryParams,\n"
        "    extract_dataset_data,\n"
        "    transform_dataset_data,\n"
        "    transform_dataset_query,\n"
        ")\n\n\n"
    )
    return (
        header
        + _query_params_source(group, dataset, spec, release_datasets)
        + "\n\n"
        + _data_source(group, dataset, spec)
        + "\n\n"
        + _fetcher_source(group, dataset, spec)
    )


def render_registry(catalog: dict[str, Any]) -> str:
    """Render the generated fetcher registry module."""
    imports: list[str] = []
    entries: list[str] = []
    for group in DATASET_GROUPS_EMIT:
        datasets = catalog["groups"][group]["datasets"]
        if group in RELEASE_GROUPS:
            base = _base_name(group, "")
            imports.append(f"from openbb_us_eia.models.{group} import {base}Fetcher")
            entries.append(f'    "{base}": {base}Fetcher,')
            continue
        if group in FLAT_GROUPS:
            base = _base_name(group, group)
            imports.append(f"from openbb_us_eia.models.{group} import {base}Fetcher")
            entries.append(f'    "{base}": {base}Fetcher,')
            continue
        for dataset in datasets:
            base = _base_name(group, dataset)
            imports.append(
                f"from openbb_us_eia.models.{group}.{dataset} import {base}Fetcher"
            )
            entries.append(f'    "{base}": {base}Fetcher,')
    imports.sort()
    entries.sort()
    return (
        '"""Registry of EIA dataset fetchers."""\n\n'
        + "\n".join(imports)
        + "\n\nDATASET_FETCHERS = {\n"
        + "\n".join(entries)
        + "\n}\n"
    )


def _release_template(group: str, group_doc: dict) -> dict:
    """Build the spec describing a release-keyed report as a whole."""
    datasets = group_doc["datasets"]
    latest = datasets[sorted(datasets)[-1]]
    template = dict(latest)
    template["name"] = latest.get("category") or group.upper()
    template["description"] = (
        "Long-term energy projections by release year and scenario."
        " Select the report vintage with the `release` parameter."
    )
    template["path"] = group
    template["start_period"] = min(
        filter(None, (spec.get("start_period") for spec in datasets.values())),
        default=None,
    )
    template["end_period"] = max(
        filter(None, (spec.get("end_period") for spec in datasets.values())),
        default=None,
    )
    facets: dict = {}
    for canonical, detail in latest["facets"].items():
        entry = dict(detail)
        union = group_doc["choices"].get(canonical)
        if union:
            entry["choices"] = union
            entry["n_values"] = len(union)
        else:
            entry.pop("choices", None)
        facets[canonical] = entry
    template["facets"] = facets
    return template


DATASET_GROUPS_EMIT = (
    "coal",
    "petroleum",
    "natural_gas",
    "electricity",
    "electricity_grid",
    "state_electricity_profiles",
    "densified_biomass",
    "nuclear_outages",
    "crude_oil_imports",
    "international",
    "seds",
    "total_energy",
    "aeo",
    "ieo",
)

MULTI_DATASET_GROUPS = tuple(
    group
    for group in DATASET_GROUPS_EMIT
    if group not in FLAT_GROUPS and group not in RELEASE_GROUPS
)


def write_models(catalog: dict[str, Any]) -> int:
    """Write every generated model module and the registry.

    Parameters
    ----------
    catalog : dict[str, Any]
        The catalog document.

    Returns
    -------
    int
        Number of model modules written.
    """
    import shutil

    written = 0
    for group in MULTI_DATASET_GROUPS:
        group_dir = MODELS_ROOT / group
        shutil.rmtree(group_dir, ignore_errors=True)
        group_dir.mkdir(parents=True)
        title = group.replace("_", " ").title()
        (group_dir / "__init__.py").write_text(
            f'"""EIA {title} models."""\n', encoding="utf-8"
        )
        for dataset, spec in catalog["groups"][group]["datasets"].items():
            module = render_dataset_module(group, dataset, spec)
            (group_dir / f"{dataset}.py").write_text(module, encoding="utf-8")
            written += 1
    for group in FLAT_GROUPS:
        datasets = catalog["groups"][group]["datasets"]
        slug, spec = next(iter(datasets.items()))
        module = render_dataset_module(group, slug, spec)
        (MODELS_ROOT / f"{group}.py").write_text(module, encoding="utf-8")
        written += 1
    for group in RELEASE_GROUPS:
        datasets = catalog["groups"][group]["datasets"]
        releases = list(datasets)
        template = _release_template(group, catalog["groups"][group])
        module = render_dataset_module(
            group, group, template, release_datasets=releases
        )
        (MODELS_ROOT / f"{group}.py").write_text(module, encoding="utf-8")
        written += 1
    (MODELS_ROOT / "registry.py").write_text(render_registry(catalog), encoding="utf-8")
    lint_generated(MODELS_ROOT)
    return written


def lint_generated(target: Path) -> None:
    """Run ruff lint fixes and formatting on the generated modules.

    Parameters
    ----------
    target : Path
        Directory holding the generated modules.

    Raises
    ------
    RuntimeError
        If ruff reports unfixable findings or fails to format.
    """
    for argv in (
        [sys.executable, "-m", "ruff", "check", "--fix", str(target)],
        [sys.executable, "-m", "ruff", "format", str(target)],
    ):
        completed = subprocess.run(argv, check=False)  # noqa: S603
        if completed.returncode != 0:
            raise RuntimeError(
                f"ruff {argv[3]} failed for the generated modules in {target}"
            )


def main() -> int:
    """Run the catalog generator."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tree",
        type=Path,
        default=None,
        help="Path to a saved crawl JSON. When omitted, the EIA API is crawled live.",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="EIA API key for a live crawl. Defaults to the EIA_API_KEY"
        " environment variable, then the OpenBB 'eia_api_key' credential.",
    )
    parser.add_argument(
        "--asset-only",
        action="store_true",
        help="Write only the catalog asset, leaving the generated model source"
        " untouched. Used by the package build hook.",
    )
    args = parser.parse_args()

    if args.tree:
        tree = json.loads(args.tree.read_text(encoding="utf-8"))
    else:
        api_key = args.api_key or os.environ.get("EIA_API_KEY")
        if not api_key:
            from openbb_core.app.service.user_service import (
                UserService,  # noqa: PLC0415
            )

            credentials = UserService().default_user_settings.credentials.model_dump()
            api_key = credentials.get("eia_api_key")
            api_key = (
                api_key.get_secret_value()
                if hasattr(api_key, "get_secret_value")
                else api_key
            )
        if not api_key:
            sys.stderr.write("An EIA API key is required for a live crawl.\n")
            return 1
        tree = fetch_tree(api_key)

    catalog = build_catalog(tree)
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        catalog, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )
    ASSET_PATH.write_bytes(lzma.compress(payload.encode("utf-8"), preset=9))
    n_datasets = sum(len(group["datasets"]) for group in catalog["groups"].values())

    if args.asset_only:
        sys.stdout.write(
            f"Wrote {ASSET_PATH} ({ASSET_PATH.stat().st_size / 1024:.0f} KiB)"
            f" covering {n_datasets} datasets.\n"
        )
        return 0

    written = write_models(catalog)
    completed = subprocess.run(  # noqa: S603
        [
            sys.executable,
            "-m",
            "ty",
            "check",
            "--python",
            sys.executable,
            str(MODELS_ROOT),
        ],
        cwd=PACKAGE_ROOT.parent,
        check=False,
    )
    if completed.returncode != 0:
        sys.stderr.write("ty check failed for the generated modules.\n")
        return completed.returncode
    sys.stdout.write(
        f"Wrote {ASSET_PATH} ({ASSET_PATH.stat().st_size / 1024:.0f} KiB),"
        f" {written} model modules, and the registry"
        f" covering {n_datasets} datasets.\n"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
