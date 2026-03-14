"""OECD SDMX structural metadata singleton.

Provides dynamic discovery of all OECD dataflows, dimensions, codelists,
and constraints via the OECD SDMX REST API v2.

API Reference (OECD Data API documentation, July 2024):
  - Structure queries (v2):
      https://sdmx.oecd.org/public/rest/v2/structure/dataflow/{agency}/{dataflow}/{version}
        ?references=all&detail=referencepartial
  - Data queries (v2):
      https://sdmx.oecd.org/public/rest/v2/data/dataflow/{agency}/{dataflow}/{version}/{filter}
        ?lastNObservations=N&dimensionAtObservation=TIME_PERIOD
  - Format negotiation via Accept header (no format query param in v2).
  - Structure JSON: Accept: application/vnd.sdmx.structure+json; version=1.0; charset=utf-8
  - Data CSV:       Accept: application/vnd.sdmx.data+csv; charset=utf-8
  - Data CSV+labels: Accept: application/vnd.sdmx.data+csv; charset=utf-8; labels=both
  - v2 allowed data query params: dimensionAtObservation, detail, lastNObservations,
    firstNObservations, updatedAfter, attributes, measures, includeHistory, asOf.
  - Dataflow IDs in v2 use the full structural form: DSD_PRICES@DF_PRICES_ALL
    (not just DF_PRICES_ALL).
  - Dimension filter must include ALL dimensions (use * for wildcard).
"""

# pylint: disable=C0302, R0902, R0904, R0914, R0917

import json
import lzma
import pickle
import re
import threading
import warnings
from pathlib import Path
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError

BASE_URL = "https://sdmx.oecd.org/public/rest/v2"
_STRUCTURE_ACCEPT = "application/vnd.sdmx.structure+json; version=1.0; charset=utf-8"
_DATA_ACCEPT_CSV = "application/vnd.sdmx.data+csv; charset=utf-8"
_DATA_ACCEPT_CSV_LABELS = "application/vnd.sdmx.data+csv; charset=utf-8; labels=both"
# Shipped (read-only) cache bundled with the package.
_SHIPPED_CACHE_DIR = Path(__file__).resolve().parent.parent / "assets"
_SHIPPED_CACHE_FILE = _SHIPPED_CACHE_DIR / "oecd_cache.pkl.xz"


def _get_user_cache_file() -> Path:
    """Resolve the user-writable cache path via OpenBB core settings."""
    # pylint: disable=import-outside-toplevel
    try:
        from openbb_core.app.utils import get_user_cache_directory

        return Path(get_user_cache_directory()) / "oecd_cache.pkl.xz"
    except Exception:  # noqa: BLE001
        return Path.home() / ".openbb_platform" / "cache" / "oecd_cache.pkl.xz"


# Dimension IDs commonly used as "indicator" across dataflows.
_INDICATOR_DIMENSION_CANDIDATES = (
    "MEASURE",
    "INDICATOR",
    "SUBJECT",
    "TRANSACTION",
    "ACTIVITY",
    "PRODUCT",
    "SERIES",
    "ITEM",
    "ACCOUNTING_ENTRY",
    "SECTOR",
)
# Dimension IDs commonly used as "country / reference area".
_COUNTRY_DIMENSION_CANDIDATES = (
    "REF_AREA",
    "COUNTERPART_AREA",
    "JURISDICTION",
    "COUNTRY",
    "AREA",
)
# Dimension IDs used to group observations into conceptual "tables".
# TABLE_IDENTIFIER is the standard; CHAPTER is used by NAAG and similar.
_TABLE_GROUP_CANDIDATES = (
    "TABLE_IDENTIFIER",
    "CHAPTER",
)
# Dimensions that are NEVER indicators — they describe how data is
# measured, adjusted, or transformed, not what is being measured.
_NON_INDICATOR_DIMENSIONS = frozenset(
    {
        "FREQ",
        "ADJUSTMENT",
        "TRANSFORMATION",
        "UNIT_MEASURE",
        "UNIT_MULT",
        "CURRENCY_DENOM",
        "CURRENCY",
        "VALUATION",
        "PRICE_BASE",
        "CONSOLIDATION",
        "MATURITY",
        "METHODOLOGY",
        "TABLE_IDENTIFIER",
        "TIME_PERIOD",
        "COUNTERPART_AREA",
        "DEBT_BREAKDOWN",
    }
)


def _make_request(url: str, headers: dict | None = None, timeout: int = 30) -> Any:
    """Make a HTTP GET request with retries on 429 Too Many Requests."""
    # pylint: disable=import-outside-toplevel
    import time  # noqa
    from openbb_core.provider.utils.helpers import make_request

    max_retries = 5

    for attempt in range(max_retries):
        resp = make_request(url, headers=headers, timeout=timeout)

        if resp.status_code == 429 and attempt < max_retries - 1:
            retry_after = int(resp.headers.get("Retry-After", 15 * (attempt + 1)))
            time.sleep(min(max(retry_after, 15), 90))
            continue

        break

    resp.raise_for_status()

    return resp


def _normalize_label(label: str) -> str:
    """Normalise a country / concept label to lower_snake_case."""
    # Remove parenthetical content.
    label = re.sub(r"\s*\(.*?\)\s*", "", label)
    # Remove comma-delimited suffixes.
    label = label.split(",")[0]
    # Replace separators.
    label = label.strip().lower().replace("-", "_").replace(" ", "_")
    # Collapse multiple underscores.
    label = re.sub(r"_+", "_", label)

    return label.strip("_")


def _build_code_tree(
    codes: dict[str, str],
    parents: dict[str, str],
    descriptions: dict[str, str],
) -> list[dict]:
    """Build a tree from a flat mapping of codes → labels using parent refs.

    Parameters
    ----------
    codes : dict[str, str]
        {code: label} for every code that should appear in the tree.
    parents : dict[str, str]
        {code: parent_code} for codes that have a parent.
    descriptions : dict[str, str]
        {code: description} for extended descriptions.

    Returns
    -------
    list[dict]
        Tree of {'code', 'label', 'description', 'children': [...]} dicts.
    """
    nodes: dict[str, dict] = {}

    for code, label in codes.items():
        nodes[code] = {
            "code": code,
            "label": label,
            "description": descriptions.get(code, label),
            "children": [],
        }

    roots: list[dict] = []

    for code in list(nodes):
        parent = parents.get(code)

        if parent and parent in nodes:
            nodes[parent]["children"].append(nodes[code])
        else:
            roots.append(nodes[code])

    def _sort(items: list[dict]):
        items.sort(key=lambda n: n["label"])

        for item in items:
            if item["children"]:
                _sort(item["children"])

    _sort(roots)

    return roots


def _parse_sdmx_json_codelists(
    raw: dict,
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    """Extract codelists and parent hierarchies from an SDMX-JSON structure response.

    The SDMX-JSON response nests codelists under data → codelists (an array).
    Each element has id, name (or names), and codes (array of {id, name/names}).
    Codes may have a 'parent' field referencing the parent code id.

    Returns
    -------
    tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]
        (codelists, codelist_parents) where:
        - codelists: {cl_id: {code: label}}
        - codelist_parents: {cl_id: {code: parent_code}}  (only codes that have a parent)
    """
    codelists: dict[str, dict[str, str]] = {}
    codelist_parents: dict[str, dict[str, str]] = {}
    raw_cls = raw.get("data", raw).get("codelists", [])

    for cl in raw_cls:
        bare_id = cl.get("id", "")
        agency = cl.get("agencyID", "")
        version = cl.get("version", "")
        cl_id = f"{agency}:{bare_id}({version})" if agency and version else bare_id
        codes: dict[str, str] = {}
        parents: dict[str, str] = {}

        for code in cl.get("codes", []):
            code_id = code.get("id", "")
            # Label resolution: names dict → name string → id fallback.
            names = code.get("names", {})
            code_label = (
                names.get("en", "") if isinstance(names, dict) else ""
            ) or code.get("name", code_id)
            codes[code_id] = code_label
            # Parent hierarchy.
            parent = code.get("parent", "")

            if parent:
                parents[code_id] = parent

        if cl_id:
            codelists[cl_id] = codes

            if parents:
                codelist_parents[cl_id] = parents

    return codelists, codelist_parents


class OecdMetadata:
    """Thread-safe singleton that lazily loads and caches OECD SDMX metadata.

    Public API
    ----------
    list_dataflows(topic=None)                → list[dict]
    list_topics()                             → list[dict]
    list_dataflows_by_topic()                 → list[dict]
    get_dataflow_info(dataflow_id)            → dict
    get_dataflow_parameters(dataflow_id)      → dict[str, list[dict]]
    resolve_country_codes(dataflow_id, input) → list[str]
    get_codelist_for_dimension(df_id, dim_id) → dict[str, str]
    get_indicators_in(dataflow_id)            → list[dict]
    search_indicators(query, dataflows, …)    → list[dict]
    get_dimension_order(dataflow_id)          → list[str]

    All public methods are safe to call from any thread.
    """

    _instance: "OecdMetadata | None" = None
    _lock = threading.Lock()
    _codelist_lock = threading.Lock()
    _initialized: bool = False
    _search_index: list[tuple[str, dict]] | None = None

    def __new__(cls) -> "OecdMetadata":
        """Ensure only one instance of OecdMetadata exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    cls._instance = inst
        return cls._instance  # type: ignore[return-value]

    def __init__(self) -> None:
        """Initialize the OecdMetadata class."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            # Primary stores (populated from cache or API).
            self.dataflows: dict[str, dict] = {}
            self.datastructures: dict[str, dict] = {}
            self.codelists: dict[str, dict[str, str]] = {}
            # Reverse lookup: short_id (e.g. "DF_PRICES_ALL") → full_id
            # ("DSD_PRICES@DF_PRICES_ALL").
            self._short_id_map: dict[str, str] = {}
            # Secondary caches.
            self._codelist_descriptions: dict[str, dict[str, str]] = {}
            self._codelist_parents: dict[str, dict[str, str]] = {}
            self._codelist_comp_rules: dict[str, dict[str, str]] = {}
            self._dataflow_constraints: dict[str, dict[str, list[str]]] = {}
            self._dataflow_parameters_cache: dict[str, dict] = {}
            self._dataflow_indicators_cache: dict[str, list] = {}
            self._availability_cache: dict[str, dict[str, list[str]]] = {}
            # Per-dataflow indicator dimension: full_id → dim_id.
            self._indicator_dim_cache: dict[str, str | None] = {}
            # Table map: TABLE_IDENTIFIER code → {name, description, dataflows}.
            self._table_map: dict[str, dict] = {}
            self._full_catalogue_loaded: bool = False
            # Topic taxonomy (topic→subtopic→dataflow hierarchy).
            self._taxonomy_tree: list[dict] = []
            self._df_to_categories: dict[str, list[str]] = {}
            self._category_to_dfs: dict[str, list[str]] = {}
            self._category_names: dict[str, str] = {}
            self._taxonomy_loaded: bool = False
            # Load persisted cache (ships with the package).
            self._load_from_cache()
            self.__class__._initialized = True

    @staticmethod
    def _read_cache_file(path: Path) -> dict | None:
        """Read and return a cache blob, or *None* on any failure."""
        try:
            if not path.exists():
                return None
            with lzma.open(path, "rb") as fh:
                return pickle.load(fh)  # noqa: S301
        except Exception:  # noqa: BLE001
            return None

    def _apply_blob(self, blob: dict) -> None:
        """Merge a cache *blob* into the current metadata stores."""
        self.dataflows.update(blob.get("dataflows", {}))
        self.datastructures.update(blob.get("datastructures", {}))
        self.codelists.update(blob.get("codelists", {}))
        self._codelist_descriptions.update(blob.get("codelist_descriptions", {}))
        self._codelist_parents.update(blob.get("codelist_parents", {}))
        self._codelist_comp_rules.update(blob.get("codelist_comp_rules", {}))
        # Infer parents for orphan codes using COMP_RULE annotations.
        self._infer_orphan_parents()
        self._dataflow_constraints.update(blob.get("dataflow_constraints", {}))
        self._table_map.update(blob.get("table_map", {}))
        self._dataflow_parameters_cache.update(blob.get("dataflow_parameters", {}))
        # Indicators: support both compact formats from the shipped cache.
        # New multi-dim: {full_id: {"dims": [{"dim_id": str, "codes": [...]}, ...]}}
        # Legacy single-dim: {full_id: {"dim_id": str, "codes": [...]}}
        # Expanded: {full_id: [{dataflow_id, dataflow_name, dimension_id, indicator, label, description, symbol}, ...]}
        raw_indicators = blob.get("dataflow_indicators", {})

        for full_id, val in raw_indicators.items():
            if isinstance(val, dict) and "dims" in val:
                # New multi-dimension format.
                df_meta = self.dataflows.get(full_id, {})
                short_id = df_meta.get(
                    "short_id", full_id.split("@")[-1] if "@" in full_id else full_id
                )
                df_name = df_meta.get("name", short_id)
                expanded: list[dict] = []
                seen: set[str] = set()

                for dim_block in val["dims"]:
                    dim_id = dim_block.get("dim_id", "")
                    for c in dim_block.get("codes", []):
                        code = c["indicator"]
                        if code in seen:
                            continue
                        seen.add(code)
                        entry = {
                            "dataflow_id": short_id,
                            "dataflow_name": df_name,
                            "dimension_id": dim_id,
                            "indicator": code,
                            "label": c["label"],
                            "description": c.get("description", c["label"]),
                            "symbol": f"{short_id}::{code}",
                        }
                        if "parent" in c:
                            entry["parent"] = c["parent"]
                        expanded.append(entry)

                self._dataflow_indicators_cache[full_id] = expanded
            elif isinstance(val, dict) and "codes" in val:
                # Legacy single-dimension format.
                df_meta = self.dataflows.get(full_id, {})
                short_id = df_meta.get(
                    "short_id", full_id.split("@")[-1] if "@" in full_id else full_id
                )
                df_name = df_meta.get("name", short_id)
                dim_id = val.get("dim_id", "")
                expanded = []

                for c in val["codes"]:
                    entry = {
                        "dataflow_id": short_id,
                        "dataflow_name": df_name,
                        "dimension_id": dim_id,
                        "indicator": c["indicator"],
                        "label": c["label"],
                        "description": c.get("description", c["label"]),
                        "symbol": f"{short_id}::{c['indicator']}",
                    }

                    if "parent" in c:
                        entry["parent"] = c["parent"]

                    expanded.append(entry)

                self._dataflow_indicators_cache[full_id] = expanded
            else:
                self._dataflow_indicators_cache[full_id] = val

        self._short_id_map.update(blob.get("short_id_map", {}))
        # Taxonomy: only overwrite if the blob has it.
        tax = blob.get("taxonomy_tree", [])

        if tax:
            self._taxonomy_tree = tax
            self._df_to_categories.update(blob.get("df_to_categories", {}))
            self._category_to_dfs.update(blob.get("category_to_dfs", {}))
            self._category_names.update(blob.get("category_names", {}))
            self._taxonomy_loaded = True

    def _infer_orphan_parents(self) -> None:
        """Infer parent for orphan codes using COMP_RULE annotations.

        Some OECD codelist codes lack an explicit ``parent`` field but carry a
        ``COMP_RULE`` annotation (e.g. "CP041+CP042+CP043") that lists the
        component codes.  For each such orphan, we walk the ancestor chains of
        every listed component and select the closest common ancestor as the
        inferred parent.
        """
        for cl_id, comp_rules in self._codelist_comp_rules.items():
            parents = self._codelist_parents.get(cl_id)
            if parents is None:
                continue
            for code, rule in comp_rules.items():
                if code in parents:
                    # Already has an explicit parent.
                    continue
                components = [c.strip() for c in rule.split("+") if c.strip()]
                if not components:
                    continue
                ancestor = self._closest_common_ancestor(components, parents)
                if ancestor is not None:
                    parents[code] = ancestor

    @staticmethod
    def _closest_common_ancestor(
        codes: list[str], parents: dict[str, str]
    ) -> str | None:
        """Return the nearest ancestor shared by all *codes*, or ``None``."""
        if not codes:
            return None

        def _chain(code: str) -> list[str]:
            chain: list[str] = []
            visited: set[str] = set()
            cur = parents.get(code)
            while cur and cur not in visited:
                chain.append(cur)
                visited.add(cur)
                cur = parents.get(cur)
            return chain

        ancestor_sets: list[set[str]] = []
        ordered_chains: list[list[str]] = []
        for c in codes:
            ch = _chain(c)
            ancestor_sets.append(set(ch))
            ordered_chains.append(ch)

        if not ancestor_sets:
            return None

        common = ancestor_sets[0]
        for s in ancestor_sets[1:]:
            common = common & s

        if not common:
            return None

        # Pick the common ancestor that appears earliest (deepest) in any chain.
        best: str | None = None
        best_depth = float("inf")
        for ch in ordered_chains:
            for depth, ancestor in enumerate(ch):
                if ancestor in common and depth < best_depth:
                    best_depth = depth
                    best = ancestor
        return best

    def _load_from_cache(self) -> bool:
        """Load metadata from the shipped cache, then layer user cache on top."""
        loaded = False
        # 1. Shipped (read-only) cache bundled with the package.
        shipped = self._read_cache_file(_SHIPPED_CACHE_FILE)
        if shipped:
            self._apply_blob(shipped)
            loaded = True
        # 2. User cache with runtime updates (may be newer / more complete).
        user = self._read_cache_file(_get_user_cache_file())
        if user:
            self._apply_blob(user)
            loaded = True
        if loaded:
            if not self._short_id_map and self.dataflows:
                self._rebuild_short_id_map()
            if self.dataflows:
                self._full_catalogue_loaded = True
        else:
            warnings.warn(
                "No OECD metadata cache found; will fetch from API.",
                stacklevel=2,
            )
        return loaded

    def _save_cache(self) -> None:
        """Persist current metadata to the user-writable cache."""
        try:
            cache_file = _get_user_cache_file()
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            blob = {
                "dataflows": self.dataflows,
                "datastructures": self.datastructures,
                "codelists": self.codelists,
                "codelist_descriptions": self._codelist_descriptions,
                "codelist_parents": self._codelist_parents,
                "codelist_comp_rules": self._codelist_comp_rules,
                "dataflow_constraints": self._dataflow_constraints,
                "table_map": self._table_map,
                "dataflow_parameters": self._dataflow_parameters_cache,
                "dataflow_indicators": self._dataflow_indicators_cache,
                "short_id_map": self._short_id_map,
                "taxonomy_tree": self._taxonomy_tree,
                "df_to_categories": self._df_to_categories,
                "category_to_dfs": self._category_to_dfs,
                "category_names": self._category_names,
            }
            with lzma.open(cache_file, "wb", format=lzma.FORMAT_XZ, preset=6) as fh:
                pickle.dump(blob, fh, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:  # noqa: BLE001
            warnings.warn(
                "Failed to persist OECD metadata cache.",
                stacklevel=2,
            )

    def _ensure_dataflows(self) -> None:
        """Lazy-load the full dataflow catalogue if not yet populated."""
        if self._full_catalogue_loaded:
            return

        # SDMX API v2 structure query:
        #   GET /structure/dataflow
        url = f"{BASE_URL}/structure/dataflow"
        resp = _make_request(url, headers={"Accept": _STRUCTURE_ACCEPT})

        try:
            raw = resp.json()
        except (json.JSONDecodeError, AttributeError) as exc:
            raise OpenBBError(
                f"Failed to parse OECD dataflow catalogue from {url}"
            ) from exc

        # Parse dataflows.
        raw_dfs = raw.get("data", raw).get("dataflows", [])

        for df in raw_dfs:
            # In v2 the id is the full structural form, e.g.
            # DSD_PRICES@DF_PRICES_ALL.  The short form (after @)
            # is also stored for backward-compatible lookups.
            full_id = df.get("id", "")
            agency_id = df.get("agencyID", "")
            version = df.get("version", "")
            names = df.get("names", {})
            name = (names.get("en", "") if isinstance(names, dict) else "") or df.get(
                "name", full_id
            )
            descriptions = df.get("descriptions", {})
            description = (
                descriptions.get("en", "") if isinstance(descriptions, dict) else ""
            ) or df.get("description", "")
            struct_ref = df.get("structure", "")
            # Derive the short id (part after "@", or the full id if no @).
            short_id = full_id.split("@")[-1] if "@" in full_id else full_id
            self.dataflows[full_id] = {
                "id": full_id,
                "short_id": short_id,
                "agency_id": agency_id,
                "version": version,
                "name": name,
                "description": description,
                "structure_ref": struct_ref,
            }
            self._short_id_map[short_id] = full_id

        # Persist immediately so subsequent runs are faster.
        if self.dataflows:
            self._full_catalogue_loaded = True
            self._save_cache()

    def _rebuild_short_id_map(self) -> None:
        """Rebuild _short_id_map from dataflows."""
        self._short_id_map.clear()

        for full_id, meta in self.dataflows.items():
            short_id = meta.get("short_id", full_id.split("@")[-1])
            self._short_id_map[short_id] = full_id

    _CATEGORISATION_DF_RE = re.compile(r"Dataflow=([^:]+):([^(]+)\(([^)]+)\)")
    _CATEGORISATION_CAT_RE = re.compile(r"OECDCS1\([^)]+\)\.(.+)")

    def _ensure_taxonomy(self) -> None:
        """Lazy-load the OECD topic taxonomy (category scheme + categorisations).

        Fetches two SDMX v2 structure endpoints:
        * /structure/categoryscheme/OECD/OECDCS1 — the topic tree.
        * /structure/categorisation — mappings from dataflows to categories.

        Results are cached alongside other metadata.
        """
        if self._taxonomy_loaded:
            return

        self._ensure_dataflows()
        cs_url = f"{BASE_URL}/structure/categoryscheme/OECD/OECDCS1"

        try:
            resp = _make_request(
                cs_url, headers={"Accept": _STRUCTURE_ACCEPT}, timeout=30
            )
            cs_raw = resp.json()
        except Exception as exc:
            warnings.warn(
                f"Failed to fetch OECD category scheme: {exc}",
                stacklevel=2,
            )
            self._taxonomy_loaded = True
            return

        schemes = cs_raw.get("data", cs_raw).get("categorySchemes", [])

        if not schemes:
            self._taxonomy_loaded = True
            return

        tree, names = self._parse_category_tree(schemes[0].get("categories", []))
        self._taxonomy_tree = tree
        self._category_names = names
        cat_url = f"{BASE_URL}/structure/categorisation"

        try:
            resp2 = _make_request(
                cat_url, headers={"Accept": _STRUCTURE_ACCEPT}, timeout=30
            )
            cat_raw = resp2.json()
        except Exception as exc:
            warnings.warn(
                f"Failed to fetch OECD categorisations: {exc}",
                stacklevel=2,
            )
            self._taxonomy_loaded = True
            return

        raw_cats = cat_raw.get("data", cat_raw).get("categorisations", [])
        self._parse_categorisations(raw_cats)
        self._taxonomy_loaded = True
        self._save_cache()

    @staticmethod
    def _parse_category_tree(
        categories: list[dict],
        prefix: str = "",
    ) -> tuple[list[dict], dict[str, str]]:
        """Recursively parse the category scheme into a tree + flat name map.

        Returns
        -------
        tree : list[dict]
            [{id, name, path, children: [...]}, ...]
        names : dict[str, str]
            Flat map of category_path → name for all levels.
        """
        tree: list[dict] = []
        names: dict[str, str] = {}

        for cat in categories:
            cid = cat.get("id", "")
            cnames = cat.get("names", {})
            name = (
                cnames.get("en", "") if isinstance(cnames, dict) else ""
            ) or cat.get("name", cid)
            path = f"{prefix}.{cid}" if prefix else cid
            names[path] = name
            subcats = cat.get("categories", [])
            children, child_names = OecdMetadata._parse_category_tree(subcats, path)
            names.update(child_names)
            tree.append(
                {
                    "id": cid,
                    "name": name,
                    "path": path,
                    "children": children,
                }
            )

        return tree, names

    def _parse_categorisations(self, raw_cats: list[dict]) -> None:
        """Parse categorisation records into df↔category mappings.

        Each categorisation has a source URN (dataflow) and target
        URN (category path).  Multiple versions of the same dataflow may
        exist; we keep only the latest version per (dataflow, category) pair.
        """
        # pylint: disable=import-outside-toplevel
        from collections import defaultdict

        df_re = self._CATEGORISATION_DF_RE
        cat_re = self._CATEGORISATION_CAT_RE

        # Temporary: (agency:dsd@df, cat_path) → version string
        seen: dict[tuple[str, str], str] = {}

        for entry in raw_cats:
            src = entry.get("source", "")
            tgt = entry.get("target", "")

            m_df = df_re.search(src)
            m_cat = cat_re.search(tgt)

            if not m_df or not m_cat:
                continue

            agency = m_df.group(1)
            dsd_df = m_df.group(2)
            version = m_df.group(3)
            cat_path = m_cat.group(1)

            full_id = f"{agency}:{dsd_df}"
            key = (full_id, cat_path)
            prev_ver = seen.get(key, "")

            if version >= prev_ver:
                seen[key] = version

        # Now build the final mappings using only canonical full_ids
        # that are present in our dataflow catalogue.
        # Categorisation agency:dsd@df → our catalogue dsd@df form
        df_to_cats: dict[str, list[str]] = defaultdict(list)
        cat_to_dfs: dict[str, list[str]] = defaultdict(list)

        for (ext_id, cat_path), _ver in seen.items():
            # ext_id is "AGENCY:DSD@DF"; our dataflows dict keys are "DSD@DF"
            dsd_df = ext_id.split(":", 1)[-1] if ":" in ext_id else ext_id

            if dsd_df not in self.dataflows:
                continue

            if cat_path not in df_to_cats[dsd_df]:
                df_to_cats[dsd_df].append(cat_path)

            if dsd_df not in cat_to_dfs[cat_path]:
                cat_to_dfs[cat_path].append(dsd_df)

        self._df_to_categories = dict(df_to_cats)
        self._category_to_dfs = dict(cat_to_dfs)

    def _resolve_dataflow_id(self, dataflow_id: str) -> str:
        """Resolve a short or full dataflow id to the canonical full id.

        Parameters
        ----------
        dataflow_id : str
            Full id ("DSD_PRICES@DF_PRICES_ALL", returned as-is) or
            short id ("DF_PRICES_ALL", resolved via lookup).

        Returns
        -------
        str
            The canonical full dataflow id.

        Notes
        -----
        Priority dataflows resolve instantly (no network call).  Non-priority
        ids trigger a full catalogue fetch on first miss.
        """
        # Direct match (full id) — works for both priority and cached.
        if dataflow_id in self.dataflows:
            return dataflow_id

        # Short id lookup.
        full_id = self._short_id_map.get(dataflow_id)

        if full_id:
            return full_id

        # Not in priority set or cache — fetch the full catalogue.
        self._ensure_dataflows()

        if dataflow_id in self.dataflows:
            return dataflow_id

        full_id = self._short_id_map.get(dataflow_id)

        if full_id:
            return full_id

        raise OpenBBError(
            f"Unknown OECD dataflow: '{dataflow_id}'. Use list_dataflows() to see available dataflows."
        )

    def _ensure_description(self, full_id: str) -> None:
        """Fetch and cache the narrative description for a single dataflow.

        The bulk /structure/dataflow catalogue omits the descriptions field;
        only the per-dataflow endpoint returns it.  This method fetches it
        lazily and stores it in self.dataflows[full_id]['description'].
        """
        if not hasattr(self, "_description_fetched"):
            self._description_fetched: set = set()  # pylint: disable=W0201

        if full_id in self._description_fetched:
            return
        # Already have a non-empty description.
        if self.dataflows.get(full_id, {}).get("description"):
            self._description_fetched.add(full_id)
            return

        df_meta = self.dataflows.get(full_id, {})
        agency = df_meta.get("agency_id", "")
        version = df_meta.get("version", "")

        if not agency or not version:
            self._description_fetched.add(full_id)
            return

        try:
            url = f"{BASE_URL}/structure/dataflow/{agency}/{full_id}/{version}"
            resp = _make_request(url, headers={"Accept": _STRUCTURE_ACCEPT})
            raw_dfs = resp.json().get("data", {}).get("dataflows", [])

            for df in raw_dfs:
                desc_raw = df.get("descriptions", {})
                desc = (
                    desc_raw.get("en", "") if isinstance(desc_raw, dict) else ""
                ) or df.get("description", "")

                if desc:
                    desc_clean = re.sub(r"<[^>]+>", "", desc)
                    desc_clean = (
                        desc_clean.replace("&nbsp;", " ")
                        .replace("&amp;", "&")
                        .replace("&lt;", "<")
                        .replace("&gt;", ">")
                    )
                    desc_clean = re.sub(r"[ \t]+", " ", desc_clean).strip()
                    self.dataflows.setdefault(full_id, {})["description"] = desc_clean
                break
        except Exception:  # noqa: S110
            pass
        self._description_fetched.add(full_id)

    def _ensure_structure(self, dataflow_id: str, *, force: bool = False) -> None:
        """Lazy-load the DSD, codelists and concept schemes for *dataflow_id*.

        Uses the SDMX v2 structure query with references=all and
        detail=referencepartial so that the response embeds the DSD
        and all referenced codelists + concept schemes.

        Parameters
        ----------
        dataflow_id : str
            Short or full dataflow ID.
        force : bool
            Re-fetch even if the structure is already present (used to
            upgrade a partial structure to a full one with all codelists).

        Notes
        -----
        SDMX v2 structure query::

            GET /structure/dataflow/{agency}/{dataflow}/{version}
              ?references=all&detail=referencepartial
        """
        full_id = self._resolve_dataflow_id(dataflow_id)

        if full_id in self.datastructures and not force:
            return

        df_meta = self.dataflows[full_id]
        agency = df_meta["agency_id"]
        version = df_meta["version"]
        url = f"{BASE_URL}/structure/dataflow/{agency}/{full_id}/{version}?references=all&detail=referencepartial"
        resp = _make_request(url, headers={"Accept": _STRUCTURE_ACCEPT})

        try:
            raw = resp.json()
        except (json.JSONDecodeError, AttributeError) as exc:
            raise OpenBBError(
                f"Failed to parse OECD structure for {full_id} from {url}"
            ) from exc

        raw_data = raw.get("data", raw)
        raw_dsds = raw_data.get("dataStructures", [])

        for dsd in raw_dsds:
            dsd_id = dsd.get("id", "")
            dsd_agency = dsd.get("agencyID", "")
            dsd_version = dsd.get("version", "")
            dimensions = self._parse_dimension_list(dsd)
            attributes = self._parse_attribute_list(dsd)
            components = dsd.get("dataStructureComponents", {})
            time_dims = components.get("dimensionList", {}).get("timeDimensions", [])
            has_time_dimension = bool(time_dims)
            self.datastructures[full_id] = {
                "dsd_id": dsd_id,
                "agency_id": dsd_agency,
                "version": dsd_version,
                "dimensions": dimensions,
                "attributes": attributes,
                "has_time_dimension": has_time_dimension,
            }
            # Only take the first DSD (there should be exactly one).
            break

        # Also save the dataflow description from the per-dataflow response.
        # The bulk /structure/dataflow endpoint omits this; the per-flow fetch has it.
        raw_dfs = raw_data.get("dataflows", [])

        for df in raw_dfs:
            desc_raw = df.get("descriptions", {})
            desc = (
                desc_raw.get("en", "") if isinstance(desc_raw, dict) else ""
            ) or df.get("description", "")

            if desc and desc != self.dataflows.get(full_id, {}).get("description", ""):
                # Strip HTML tags and collapse whitespace for clean display.
                desc_clean = re.sub(r"<[^>]+>", "", desc)
                desc_clean = re.sub(r"[ \t]+", " ", desc_clean).strip()
                self.dataflows.setdefault(full_id, {})["description"] = desc_clean
            break

        parsed_cls, parsed_parents = _parse_sdmx_json_codelists(raw)

        with self._codelist_lock:
            for cl_id, codes in parsed_cls.items():
                if cl_id in self.codelists:
                    self.codelists[cl_id].update(codes)
                else:
                    self.codelists[cl_id] = codes

            for cl_id, parents in parsed_parents.items():
                if cl_id in self._codelist_parents:
                    self._codelist_parents[cl_id].update(parents)
                else:
                    self._codelist_parents[cl_id] = parents

            # Also extract descriptions where available.
            raw_cls = raw.get("data", raw).get("codelists", [])

            for cl in raw_cls:
                bare_id = cl.get("id", "")
                agency = cl.get("agencyID", "")
                version = cl.get("version", "")
                cl_id = (
                    f"{agency}:{bare_id}({version})" if agency and version else bare_id
                )
                descs: dict[str, str] = {}

                for code in cl.get("codes", []):
                    code_id = code.get("id", "")
                    d = code.get("descriptions", {})
                    desc = (d.get("en", "") if isinstance(d, dict) else "") or code.get(
                        "description", ""
                    )
                    descs[code_id] = desc or self.codelists.get(cl_id, {}).get(
                        code_id, ""
                    )

                if cl_id:
                    existing_descs = self._codelist_descriptions.get(cl_id, {})
                    existing_descs.update(descs)
                    self._codelist_descriptions[cl_id] = existing_descs

        raw_constraints = raw.get("data", raw).get("contentConstraints", [])

        if raw_constraints:
            constraints: dict[str, list[str]] = {}

            for cc in raw_constraints:
                for region in cc.get("cubeRegions", []):
                    for kv in region.get("keyValues", []):
                        dim_id = kv.get("id", "")
                        vals = kv.get("values", [])

                        if dim_id and vals:
                            # Merge: keep the intersection if already present,
                            # or store the new values.
                            if dim_id in constraints:
                                existing = set(constraints[dim_id])
                                constraints[dim_id] = sorted(existing | set(vals))
                            else:
                                constraints[dim_id] = sorted(vals)
            if constraints:
                self._dataflow_constraints[full_id] = constraints

        self._save_cache()

    @staticmethod
    def _parse_dimension_list(dsd: dict) -> list[dict]:
        """Return ordered dimension descriptors from a DSD JSON object.

        Returns
        -------
        list[dict]
            Each entry has keys: id, position, codelist_id, concept_id, name.
        """
        dims: list[dict] = []
        # SDMX-JSON puts dimensions under
        #   dataStructureComponents → dimensionList → dimensions
        components = dsd.get("dataStructureComponents", {})
        dim_list = components.get("dimensionList", {}).get("dimensions", [])

        for dim in dim_list:
            dim_id = dim.get("id", "")
            position = dim.get("position", len(dims))
            # Codelist reference.
            local_repr = dim.get("localRepresentation", {})
            enum_ref = local_repr.get("enumeration", "")
            # enumeration is a URN string; extract the codelist id.
            cl_id = _extract_codelist_id_from_urn(enum_ref) if enum_ref else ""
            # Concept identity.
            concept_identity = dim.get("conceptIdentity", "")
            concept_id = (
                _extract_concept_id_from_urn(concept_identity)
                if concept_identity
                else dim_id
            )
            # Label
            names = dim.get("names", {})
            name = (names.get("en", "") if isinstance(names, dict) else "") or dim.get(
                "name", dim_id
            )
            dims.append(
                {
                    "id": dim_id,
                    "position": position,
                    "codelist_id": cl_id,
                    "concept_id": concept_id,
                    "name": name,
                }
            )

        dims.sort(key=lambda d: d["position"])

        return dims

    @staticmethod
    def _parse_attribute_list(dsd: dict) -> list[dict]:
        """Return attribute descriptors from a DSD JSON object."""
        attrs: list[dict] = []
        components = dsd.get("dataStructureComponents", {})
        attr_list = components.get("attributeList", {}).get("attributes", [])

        for attr in attr_list:
            attr_id = attr.get("id", "")
            local_repr = attr.get("localRepresentation", {})
            enum_ref = local_repr.get("enumeration", "")
            cl_id = _extract_codelist_id_from_urn(enum_ref) if enum_ref else ""
            attrs.append({"id": attr_id, "codelist_id": cl_id})

        return attrs

    def list_dataflows(self, topic: str | None = None) -> list[dict]:
        """Return OECD dataflows as [{label, value, topic, subtopic, all_subtopics}, …].

        Parameters
        ----------
        topic : str, optional
            Filter to a specific topic ID (e.g. "ECO", "HEA").
            When *None*, all dataflows are returned.

        Returns a flat list sorted by id.  Each entry includes topic
        and subtopic fields when taxonomy data is available.
        ``all_subtopics`` lists every subtopic the dataflow belongs to
        under the selected (or primary) topic.
        """
        self._ensure_dataflows()
        self._ensure_taxonomy()

        topic_upper = topic.upper() if topic else ""

        result: list[dict] = []
        for full_id, v in self.dataflows.items():
            cats = self._df_to_categories.get(full_id, [])

            # Determine the primary topic and all subtopics under it.
            primary_topic = ""
            primary_subtopic = ""
            all_subtopics: list[str] = []

            if cats:
                # Collect (topic, subtopic) pairs from all category paths.
                for cat_path in cats:
                    parts = cat_path.split(".")
                    t = parts[0] if parts else ""
                    s = parts[1] if len(parts) > 1 else ""
                    if not primary_topic:
                        primary_topic = t
                    if topic_upper:
                        # When filtering by topic, only consider matching paths.
                        if t == topic_upper and s:
                            all_subtopics.append(s)
                            if not primary_subtopic:
                                primary_subtopic = s
                    else:
                        if s and not primary_subtopic:
                            primary_subtopic = s
                        if s:
                            all_subtopics.append(s)

            # Topic filter: include if any category path starts with the topic.
            if topic_upper:
                if not any(c.split(".")[0] == topic_upper for c in cats):
                    continue

            # Deduplicate.
            all_subtopics = sorted(set(all_subtopics))

            result.append(
                {
                    "label": v["name"],
                    "value": full_id,
                    "topic": topic_upper if topic_upper else primary_topic,
                    "topic_name": self._category_names.get(
                        topic_upper or primary_topic, ""
                    ),
                    "subtopic": primary_subtopic,
                    "subtopic_name": (
                        self._category_names.get(
                            f"{topic_upper or primary_topic}.{primary_subtopic}", ""
                        )
                        if primary_subtopic
                        else ""
                    ),
                    "all_subtopics": all_subtopics,
                }
            )

        return sorted(result, key=lambda d: d["value"])

    def list_topics(self) -> list[dict]:
        """Return the OECD topic taxonomy as a hierarchical tree.

        Returns
        -------
        list[dict]
            [{id, name, subtopics: [{id, name, subtopics: [...]}]}]
            Each topic and subtopic includes a dataflow_count field.
        """
        self._ensure_taxonomy()

        def _annotate(node: dict) -> dict:
            """Add dataflow_count to a category tree node."""
            path = node["path"]
            # Direct dataflows in this category.
            direct = len(self._category_to_dfs.get(path, []))
            # Recurse into children.
            children = [_annotate(c) for c in node.get("children", [])]
            # Drop empty subtopics (no dataflows at any depth).
            children = [c for c in children if c["dataflow_count"] > 0]
            child_total = sum(c["dataflow_count"] for c in children)

            return {
                "id": node["id"],
                "name": node["name"],
                "dataflow_count": direct + child_total,
                "subtopics": children,
            }

        return [_annotate(t) for t in self._taxonomy_tree]

    def list_dataflows_by_topic(self) -> list[dict]:
        """Return all dataflows organised by topic → subtopic hierarchy.

        Returns
        -------
        list[dict]
            [{id, name, subtopics: [{id, name, dataflows: [{label, value}]}]}]
        """
        self._ensure_dataflows()
        self._ensure_taxonomy()

        def _df_entry(full_id: str) -> dict:
            v = self.dataflows.get(full_id, {})

            return {"label": v.get("name", full_id), "value": full_id}

        def _build(node: dict) -> dict:
            path = node["path"]
            dfs = [
                _df_entry(fid) for fid in sorted(self._category_to_dfs.get(path, []))
            ]
            children = [_build(c) for c in node.get("children", [])]
            # Drop empty subtopics.
            children = [c for c in children if c["dataflows"] or c["subtopics"]]

            return {
                "id": node["id"],
                "name": node["name"],
                "dataflows": dfs,
                "subtopics": children,
            }

        return [_build(t) for t in self._taxonomy_tree]

    def get_dataflow_info(self, dataflow_id: str) -> dict:
        """Return metadata dict for a single dataflow."""
        full_id = self._resolve_dataflow_id(dataflow_id)
        return self.dataflows[full_id]

    _COUNTRY_SUFFIX_RE = re.compile(r"^_?([A-Z]{2,3})$")

    def _detect_country_families(self) -> dict[str, dict]:
        """Detect dataflow families that are per-country splits of the same table.

        Returns
        -------
        dict[str, dict]
            {member_full_id: family_info} where family_info is::

                {
                    "dsd":            "DSD_REV_OECD",
                    "representative": "DSD_REV_OECD@DF_REV_ALL",
                    "rep_short_id":   "DF_REV_ALL",
                    "family_name":    "Tax revenues (OECD)",
                    "member_count":   39,
                }

        Notes
        -----
        Only per-country splits are collapsed — thematic splits within a DSD
        (e.g. GDP by expenditure vs income) are NOT affected.
        """
        # pylint: disable=import-outside-toplevel
        from collections import defaultdict

        dsd_groups: dict[str, list[str]] = defaultdict(list)

        for full_id in self.dataflows:
            dsd = full_id.split("@")[0] if "@" in full_id else full_id
            dsd_groups[dsd].append(full_id)

        family_map: dict[str, dict] = {}

        for dsd, fids in dsd_groups.items():
            if len(fids) < 5:
                continue

            shorts = {
                fid: self.dataflows[fid].get("short_id", fid.split("@")[-1])
                for fid in fids
            }
            # Find longest common prefix of all short IDs (at least 4 chars).
            prefix = min(shorts.values(), key=len)

            for sid in shorts.values():
                while prefix and not sid.startswith(prefix):
                    prefix = prefix[:-1]

            if len(prefix) < 4:
                continue

            suffixes = {fid: sid[len(prefix) :] for fid, sid in shorts.items()}
            country_members = {
                fid
                for fid, sfx in suffixes.items()
                if self._COUNTRY_SUFFIX_RE.match(sfx)
            }

            if len(country_members) / len(fids) < 0.7:
                continue

            # This is a country family.
            # Find the representative: prefer "ALL" variant, then base (empty suffix).
            representative = None

            for fid, sfx in suffixes.items():
                if sfx.upper() in ("ALL", "_ALL"):
                    representative = fid
                    break

            if not representative:
                for fid, sfx in suffixes.items():
                    if sfx == "":
                        representative = fid
                        break

            if not representative:
                # Pick the non-country member or shortest short_id.
                non_country = [fid for fid in fids if fid not in country_members]
                representative = (
                    non_country[0]
                    if non_country
                    else min(fids, key=lambda f: shorts[f])  # pylint: disable=W0640
                )

            # Build a clean family name from the representative.
            rep_name = self.dataflows[representative].get("name", "")
            info = {
                "dsd": dsd,
                "representative": representative,
                "rep_short_id": shorts.get(
                    representative,
                    representative.split("@")[-1],
                ),
                "family_name": rep_name,
                "member_count": len(fids),
                "members": sorted(fids),
            }

            for fid in fids:
                family_map[fid] = info

        return family_map

    def table_map(self, *, include_empty: bool = False) -> list[dict]:
        """Return a flat, navigable map of every OECD presentation table.

        Per-country dataflow splits (e.g. 159 DF_REV{CC} entries for
        "tax revenues") are collapsed into a single row pointing at the
        _ALL or representative dataflow.  Use REF_AREA in the
        QueryBuilder to pick countries.

        Returns
        -------
        list[dict]
            Sorted by topic path then table name.  Each dict::

                {
                    "topic":        "Economy",
                    "subtopic":     "Prices",
                    "sub_subtopic": "",
                    "path":         "Economy > Prices",
                    "table":        "Consumer price indices (CPIs, HICPs), COICOP 1999",
                    "dataflow_id":  "DSD_PRICES@DF_PRICES_ALL",
                    "short_id":     "DF_PRICES_ALL",
                    "countries":    0,          # 0 = not a family
                }
        """
        self._ensure_dataflows()
        self._ensure_taxonomy()
        family_map = self._detect_country_families()

        # Track which representatives we've already emitted per category path.
        emitted: set[tuple[str, str]] = set()  # (cat_path, representative_fid)
        rows: list[dict] = []

        def _walk(nodes: list[dict], breadcrumb: list[str]) -> None:
            for node in nodes:
                crumb = breadcrumb + [node["name"]]
                cat_path = node["path"]

                for fid in sorted(self._category_to_dfs.get(cat_path, [])):
                    entry = self.dataflows.get(fid)

                    if not entry:
                        continue

                    family = family_map.get(fid)

                    if family:
                        rep = family["representative"]
                        key = (cat_path, rep)

                        if key in emitted:
                            continue  # already collapsed

                        emitted.add(key)
                        self.dataflows.get(rep, entry)
                        rows.append(
                            {
                                "topic": crumb[0] if crumb else "",
                                "subtopic": crumb[1] if len(crumb) > 1 else "",
                                "sub_subtopic": (
                                    " > ".join(crumb[2:]) if len(crumb) > 2 else ""
                                ),
                                "path": " > ".join(crumb),
                                "table": family["family_name"],
                                "dataflow_id": rep,
                                "short_id": family["rep_short_id"],
                                "countries": family["member_count"],
                            }
                        )
                    else:
                        rows.append(
                            {
                                "topic": crumb[0] if crumb else "",
                                "subtopic": crumb[1] if len(crumb) > 1 else "",
                                "sub_subtopic": (
                                    " > ".join(crumb[2:]) if len(crumb) > 2 else ""
                                ),
                                "path": " > ".join(crumb),
                                "table": entry.get("name", fid),
                                "dataflow_id": fid,
                                "short_id": entry.get("short_id", fid.split("@")[-1]),
                                "countries": 0,
                            }
                        )

                _walk(node.get("children", []), crumb)

        _walk(self._taxonomy_tree, [])

        if include_empty:
            categorised = set(self._df_to_categories.keys())

            for fid, entry in sorted(self.dataflows.items()):
                if fid not in categorised and fid not in family_map:
                    rows.append(
                        {
                            "topic": "(Uncategorised)",
                            "subtopic": "",
                            "sub_subtopic": "",
                            "path": "(Uncategorised)",
                            "table": entry.get("name", fid),
                            "dataflow_id": fid,
                            "short_id": entry.get("short_id", fid.split("@")[-1]),
                            "countries": 0,
                        }
                    )

        rows.sort(key=lambda r: (r["path"], r["table"]))

        return rows

    def find_tables(self, query: str) -> list[dict]:
        """Search the table map by keyword.

        Space-separated words are AND-ed; | within a word means OR.

        Examples
        --------
        >>> meta.find_tables("GDP")
        >>> meta.find_tables("prices CPI")
        >>> meta.find_tables("trade services")
        >>> meta.find_tables("health expenditure")
        """
        full_map = self.table_map()
        tokens = [t.lower() for t in query.strip().split() if t.strip()]

        if not tokens:
            return full_map

        def _tok(token: str, text: str) -> bool:
            return any(alt in text for alt in token.split("|"))

        # Collect matches, then deduplicate by dataflow_id (keep deepest path).
        matched: dict[str, dict] = {}

        for row in full_map:
            text = " ".join(
                [
                    row["topic"],
                    row["subtopic"],
                    row["sub_subtopic"],
                    row["path"],
                    row["table"],
                    row["dataflow_id"],
                    row["short_id"],
                ]
            ).lower()

            if all(_tok(t, text) for t in tokens):
                fid = row["dataflow_id"]
                prev = matched.get(fid)

                if prev is None or len(row["path"]) > len(prev["path"]):
                    matched[fid] = row

        results = sorted(matched.values(), key=lambda r: (r["path"], r["table"]))

        return results

    def print_table_map(
        self,
        query: str | None = None,
        *,
        topic: str | None = None,
    ) -> str:
        """Return a human-readable string of the table map.

        Parameters
        ----------
        query
            Optional search filter (same as find_tables).
        topic
            Optional topic filter (e.g. "Economy" or "ECO").
        """
        # pylint: disable=import-outside-toplevel
        from collections import OrderedDict

        rows = self.find_tables(query) if query else self.table_map()

        if topic:
            t = topic.lower()
            rows = [
                r for r in rows if t in r["topic"].lower() or t in r["path"].lower()
            ]

        if not rows:
            return "(no matching tables)"

        groups: OrderedDict[str, list[dict]] = OrderedDict()

        for row in rows:
            groups.setdefault(row["path"], []).append(row)

        lines: list[str] = []
        current_topic = ""

        for group_rows in groups.values():
            top = group_rows[0]["topic"]

            if top != current_topic:
                if current_topic:
                    lines.append("")

                lines.append(f"{'=' * 60}")
                lines.append(f" {top}")
                lines.append(f"{'=' * 60}")
                current_topic = top

            sub_parts = [group_rows[0]["subtopic"]]

            if group_rows[0]["sub_subtopic"]:
                sub_parts.append(group_rows[0]["sub_subtopic"])

            sub_label = " > ".join(p for p in sub_parts if p)

            if sub_label:
                lines.append(f"  [{sub_label}]")

            for row in group_rows:
                ccount = row.get("countries", 0)
                suffix = f"  ({ccount} countries)" if ccount else ""
                lines.append(f"    {row['table']:<60s}  {row['short_id']}{suffix}")

        return "\n".join(lines)

    def get_dimension_order(self, dataflow_id: str) -> list[str]:
        """Return the DSD-defined dimension IDs in position order.

        Excludes TIME_PERIOD (which is always the observation dimension).
        """
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})

        return [d["id"] for d in dsd.get("dimensions", []) if d["id"] != "TIME_PERIOD"]

    def get_dataflow_parameters(self, dataflow_id: str) -> dict[str, list[dict]]:
        """Return queryable parameters for *dataflow_id*.

        Parameters
        ----------
        dataflow_id : str
            Short or full dataflow ID.

        Returns
        -------
        dict[str, list[dict]]
            {dim_id: [{label, value}, ...]} where each dimension's
            values come from its DSD-referenced codelist.

        Notes
        -----
        If the DSD for this dataflow has not been loaded yet, it will be
        fetched automatically.
        """
        if dataflow_id in self._dataflow_parameters_cache:
            return self._dataflow_parameters_cache[dataflow_id]

        full_id = self._resolve_dataflow_id(dataflow_id)
        # Also check cache under full_id.
        if full_id in self._dataflow_parameters_cache:
            return self._dataflow_parameters_cache[full_id]

        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})
        params: dict[str, list[dict]] = {}

        for dim in dsd.get("dimensions", []):
            dim_id = dim["id"]

            if dim_id == "TIME_PERIOD":
                continue

            cl_id = dim.get("codelist_id", "")

            if cl_id:
                cl = self._get_codelist(cl_id, dataflow_id)
                params[dim_id] = [
                    {"label": label, "value": code}
                    for code, label in sorted(cl.items())
                ]
            else:
                params[dim_id] = []

        self._dataflow_parameters_cache[dataflow_id] = params

        return params

    def _get_indicator_dim(self, full_id: str) -> str | None:
        """Return the indicator dimension for *full_id* using cached data only.

        Tries ``_INDICATOR_DIMENSION_CANDIDATES`` against the DSD dims,
        then falls back to the first non-skip dimension.  The result is
        cached in ``_indicator_dim_cache``.
        """
        if full_id in self._indicator_dim_cache:
            return self._indicator_dim_cache[full_id]

        dsd = self.datastructures.get(full_id, {})
        dim_ids = {d["id"] for d in dsd.get("dimensions", [])}

        # First: check the well-known indicator candidates.
        for candidate in _INDICATOR_DIMENSION_CANDIDATES:
            if candidate in dim_ids:
                self._indicator_dim_cache[full_id] = candidate
                return candidate

        # Fallback: first content dimension in DSD order.
        _skip = (
            set(_COUNTRY_DIMENSION_CANDIDATES)
            | _NON_INDICATOR_DIMENSIONS
            | {"FREQ", "TIME_PERIOD"}
        )
        for d in sorted(dsd.get("dimensions", []), key=lambda x: x.get("position", 0)):
            if d["id"] not in _skip:
                self._indicator_dim_cache[full_id] = d["id"]
                return d["id"]

        self._indicator_dim_cache[full_id] = None
        return None

    def _find_indicator_dimension(
        self, dataflow_id: str, indicator_code: str | None = None
    ) -> str | None:
        """Find the indicator dimension ID for *dataflow_id*.

        Checks _INDICATOR_DIMENSION_CANDIDATES in order, optionally
        verifying that *indicator_code* exists in the codelist.
        """
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)
        params = self.get_dataflow_parameters(full_id)

        for candidate in _INDICATOR_DIMENSION_CANDIDATES:
            if candidate in params and params[candidate]:
                if indicator_code:
                    codes = {e["value"] for e in params[candidate]}
                    if indicator_code in codes:
                        return candidate
                else:
                    return candidate

        # Fallback: first dimension that isn't country, non-indicator, etc.
        for d in self.get_dimension_order(full_id):
            if (
                d not in _COUNTRY_DIMENSION_CANDIDATES
                and d not in _NON_INDICATOR_DIMENSIONS
                and d in params
                and params[d]
            ):
                if indicator_code:
                    codes = {e["value"] for e in params[d]}
                    if indicator_code in codes:
                        return d
                else:
                    return d
        return None

    def get_codelist_for_dimension(
        self, dataflow_id: str, dim_id: str
    ) -> dict[str, str]:
        """Return {code: label} for a specific dimension in a dataflow."""
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})

        for dim in dsd.get("dimensions", []):
            if dim["id"] == dim_id:
                cl_id = dim.get("codelist_id", "")

                if cl_id:
                    return dict(self._get_codelist(cl_id, dataflow_id))

                return {}

        return {}

    def resolve_country_codes(self, dataflow_id: str, country_input: str) -> list[str]:
        """Resolve user-supplied country string to a list of ISO codes.

        Parameters
        ----------
        dataflow_id : str
            Short or full dataflow ID.
        country_input : str
            One of:

            * "all" / "" → returns empty list (unfiltered).
            * Comma-separated codes: "USA,GBR,DEU".
            * Comma-separated names: "united_states,germany".
            * Mixed: "USA,germany".

        Returns
        -------
        list[str]
            Resolved ISO country codes.

        Raises
        ------
        OpenBBError
            If a country cannot be matched.  The error message includes
            available options from the codelist.
        """
        if not country_input or country_input.strip().lower() in ("all", "*"):
            return []

        # Find the country dimension and its codelist.
        country_cl = self._get_country_codelist(dataflow_id)

        if not country_cl:
            return [c.strip().upper() for c in country_input.split(",") if c.strip()]

        # Build reverse lookup: normalized_label → code, and code → code.
        code_lookup: dict[str, str] = {}

        for code, label in country_cl.items():
            code_lookup[code.upper()] = code
            code_lookup[code.lower()] = code
            code_lookup[_normalize_label(label)] = code

        resolved: list[str] = []
        parts = [p.strip() for p in country_input.split(",") if p.strip()]

        for part in parts:
            key = part.strip()
            match = (
                code_lookup.get(key)
                or code_lookup.get(key.upper())
                or code_lookup.get(key.lower())
                or code_lookup.get(_normalize_label(key))
            )

            if match:
                resolved.append(match)
            else:
                available = sorted(country_cl.keys())
                sample = available[:20]
                raise OpenBBError(
                    f"Invalid country '{part}' for dataflow '{dataflow_id}'. "
                    f"Available codes ({len(available)} total): "
                    f"{', '.join(sample)}" + (" …" if len(available) > 20 else "")
                )

        return resolved

    def _get_country_codelist(self, dataflow_id: str) -> dict[str, str]:
        """Return the country/ref-area codelist for *dataflow_id*, or {}."""
        full_id = self._resolve_dataflow_id(dataflow_id)
        # Fast path: DSD already loaded — use it to find the exact codelist.
        if full_id in self.datastructures:
            dsd = self.datastructures[full_id]
            for dim in dsd.get("dimensions", []):
                if dim["id"] in _COUNTRY_DIMENSION_CANDIDATES:
                    cl_id = dim.get("codelist_id", "")
                    if cl_id:
                        return dict(self._get_codelist(cl_id, None))
        # Fallback: scan bundled codelists for a shared country codelist
        # (e.g. CL_AREA) so we avoid a live structure API call when the DSD
        # is not yet in the local cache.
        with self._codelist_lock:
            for key, codes in self.codelists.items():
                if ":CL_AREA(" in key and codes:
                    return dict(codes)
        # Last resort: fetch the structure and retry.
        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})

        for dim in dsd.get("dimensions", []):
            if dim["id"] in _COUNTRY_DIMENSION_CANDIDATES:
                cl_id = dim.get("codelist_id", "")
                if cl_id:
                    return dict(self._get_codelist(cl_id, dataflow_id))

        return {}

    def _filter_indicators_by_constraints(
        self,
        dataflow_id: str,
        indicators: list[dict],
    ) -> list[dict]:
        """Filter cached indicator list against embedded constraints."""
        full_id = self._resolve_dataflow_id(dataflow_id)
        constraints = self._dataflow_constraints.get(full_id, {})
        if not constraints or not indicators:
            return indicators

        filtered: list[dict] = []
        for ind in indicators:
            dim_id = ind.get("dimension_id", "")
            if (
                not dim_id
                or dim_id not in constraints
                or ind.get("indicator") in set(constraints[dim_id])
            ):
                filtered.append(ind)
        return filtered

    def get_indicators_in(self, dataflow_id: str) -> list[dict]:
        """Enumerate all series-producing codes across ALL content dimensions.

        Every code in every content dimension (i.e. not country, not
        frequency, not pure-metadata dims like UNIT_MEASURE) is a
        choosable parameter that creates distinct time series.  This
        method returns them all so they are individually searchable.

        Returns
        -------
        list[dict]
            Each entry has keys: dataflow_id, dataflow_name, dimension_id,
            indicator, label, description, symbol.
        """
        if dataflow_id in self._dataflow_indicators_cache:
            return self._filter_indicators_by_constraints(
                dataflow_id, self._dataflow_indicators_cache[dataflow_id]
            )

        full_id = self._resolve_dataflow_id(dataflow_id)

        if full_id in self._dataflow_indicators_cache:
            return self._filter_indicators_by_constraints(
                full_id, self._dataflow_indicators_cache[full_id]
            )

        self._ensure_structure(full_id)
        params = self.get_dataflow_parameters(full_id)
        df_meta = self.dataflows.get(full_id, {})
        df_name = df_meta.get("name", dataflow_id)
        short_df_id = (
            dataflow_id.rsplit("@", 1)[-1] if "@" in dataflow_id else dataflow_id
        )

        # Identify ALL content dimensions — everything that is not a
        # country/geo dim, not a non-indicator metadata dim, and has values.
        _skip = (
            set(_COUNTRY_DIMENSION_CANDIDATES)
            | _NON_INDICATOR_DIMENSIONS
            | {"FREQ", "TIME_PERIOD"}
        )
        content_dims: list[str] = []
        for d in self.get_dimension_order(full_id):
            if d not in _skip and d in params and params[d]:
                content_dims.append(d)

        if not content_dims:
            self._dataflow_indicators_cache[full_id] = []
            return []

        # Fetch constraints / availability once for all dimensions.
        constraints = self._dataflow_constraints.get(full_id, {})
        avail_cache: dict[str, set[str] | None] = {}
        for dim_id in content_dims:
            if dim_id in constraints:
                avail_cache[dim_id] = set(constraints[dim_id])
            else:
                avail_cache[dim_id] = None  # No constraint info.

        # If no constraints cached at all, try live availability once.
        if all(v is None for v in avail_cache.values()):
            try:
                avail = self.fetch_availability(full_id)
                for dim_id in content_dims:
                    codes = avail.get(dim_id)
                    if codes is not None:
                        avail_cache[dim_id] = set(codes)
            except Exception:  # noqa: BLE001, S110
                pass  # Fall back to full codelists.

        dsd = self.datastructures.get(full_id, {})
        dim_codelist_map: dict[str, str] = {}
        for dim in dsd.get("dimensions", []):
            dim_codelist_map[dim["id"]] = dim.get("codelist_id", "")

        indicators: list[dict] = []
        seen_codes: set[str] = set()  # Avoid duplicates across dims.

        for dim_id in content_dims:
            cl_id = dim_codelist_map.get(dim_id, "")
            descriptions = self._codelist_descriptions.get(cl_id, {})
            parents = self._codelist_parents.get(cl_id, {})
            available_codes = avail_cache.get(dim_id)

            for entry in params[dim_id]:
                code = entry["value"]

                if available_codes is not None and code not in available_codes:
                    continue
                if code in seen_codes:
                    continue
                seen_codes.add(code)

                ind: dict = {
                    "dataflow_id": short_df_id,
                    "dataflow_name": df_name,
                    "dimension_id": dim_id,
                    "indicator": code,
                    "label": entry["label"],
                    "description": descriptions.get(code, entry["label"]),
                    "symbol": f"{short_df_id}::{code}",
                }

                if code in parents:
                    ind["parent"] = parents[code]

                indicators.append(ind)

        self._dataflow_indicators_cache[full_id] = indicators

        return indicators

    def get_indicator_dataflows(self, indicator_code: str) -> list[str]:
        """Return all dataflow IDs that contain *indicator_code*.

        Scans the full shipped indicator cache.  Returns short IDs
        (e.g. ``"DF_KEI"``) when available.
        """
        result: list[str] = []

        for full_id, inds in self._dataflow_indicators_cache.items():
            for ind in inds:
                if ind.get("indicator") == indicator_code:
                    # Prefer the short ID stored inside the indicator dict.
                    result.append(ind.get("dataflow_id", full_id))
                    break

        return result

    def get_codelist_hierarchy(self, codelist_id: str) -> dict[str, str]:
        """Return {code: parent_code} for a codelist with parent hierarchy.

        Only codes that have a parent are included.  Root-level codes
        (no parent) are absent from the returned dict.
        """
        return dict(self._codelist_parents.get(codelist_id, {}))

    def get_indicator_tree(self, dataflow_id: str) -> list[dict]:
        """Return indicators for *dataflow_id* as a hierarchical tree.

        Uses the codelist's parent-child relationships to group indicators.
        Codes without a parent become root nodes.

        Returns
        -------
        list[dict]
            Tree of indicator nodes::

                [{
                    "code": "B1GQ",
                    "label": "Gross domestic product",
                    "description": "...",
                    "children": [
                        {"code": "P3", "label": "Final consumption expenditure",
                         "description": "P3=P31+P32", "children": [...]},
                        ...
                    ]
                }, ...]

            Nodes are sorted by the ORDER annotation when available,
            otherwise alphabetically.
        """
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)
        params = self.get_dataflow_parameters(full_id)
        dim_id = self._find_indicator_dimension(full_id)

        if not dim_id:
            return []

        dsd = self.datastructures.get(full_id, {})
        cl_id = ""

        for dim in dsd.get("dimensions", []):
            if dim["id"] == dim_id:
                cl_id = dim.get("codelist_id", "")
                break

        parents = self._codelist_parents.get(cl_id, {})
        descriptions = self._codelist_descriptions.get(cl_id, {})

        # Filter to only codes that exist in this dataflow's parameters.
        available_codes = {e["value"]: e["label"] for e in params.get(dim_id, [])}

        # Also filter by constraints if available.
        constraints = self._dataflow_constraints.get(full_id, {})

        if dim_id in constraints:
            constrained = set(constraints[dim_id])
            available_codes = {
                k: v for k, v in available_codes.items() if k in constrained
            }

        if not available_codes:
            return []

        # Build the tree.
        return _build_code_tree(available_codes, parents, descriptions)

    def get_constrained_values(self, dataflow_id: str) -> dict[str, list[dict]]:
        """Return dimension values filtered by embedded content constraints.

        Unlike ``fetch_availability()`` (which makes a live API call),
        this uses the constraints embedded in the structure response
        (fetched once and cached).

        Returns
        -------
        dict[str, list[dict]]
            {dim_id: [{value, label, description}, ...]} for each dimension.
            If no constraints were found for a dimension, the full codelist
            is returned.
        """
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)
        constraints = self._dataflow_constraints.get(full_id, {})
        params = self.get_dataflow_parameters(full_id)

        result: dict[str, list[dict]] = {}
        dsd = self.datastructures.get(full_id, {})

        for dim in dsd.get("dimensions", []):
            dim_id = dim["id"]

            if dim_id == "TIME_PERIOD":
                continue

            cl_id = dim.get("codelist_id", "")
            descriptions = self._codelist_descriptions.get(cl_id, {})
            entries = params.get(dim_id, [])

            if dim_id in constraints:
                allowed = set(constraints[dim_id])
                entries = [e for e in entries if e["value"] in allowed]

            result[dim_id] = [
                {
                    "value": e["value"],
                    "label": e["label"],
                    "description": descriptions.get(e["value"], e["label"]),
                }
                for e in entries
            ]

        return result

    def get_dimension_info(self, dataflow_id: str) -> list[dict]:
        """Return rich metadata for every dimension in a dataflow.

        Combines DSD structure, codelist labels, descriptions, parent
        hierarchies, and content constraints into a single comprehensive
        view of the dataflow's dimensions.

        Returns
        -------
        list[dict]
            Each entry (in DSD order)::

                {
                    "id": "TRANSACTION",
                    "position": 3,
                    "name": "Transaction",
                    "codelist_id": "CL_TRANSACTION",
                    "total_codes": 308,
                    "constrained_codes": 7,
                    "has_hierarchy": True,
                    "values": [{value, label, description, parent?}, ...],
                }
        """
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})
        constraints = self._dataflow_constraints.get(full_id, {})
        params = self.get_dataflow_parameters(full_id)

        result: list[dict] = []

        for dim in dsd.get("dimensions", []):
            dim_id = dim["id"]

            if dim_id == "TIME_PERIOD":
                continue

            cl_id = dim.get("codelist_id", "")
            codelist = self._get_codelist(cl_id, dataflow_id) if cl_id else {}
            cl_size = len(codelist)
            parents = self._codelist_parents.get(cl_id, {})

            if not parents:
                # Try prefix match for parents too.
                m_pref = self._CL_KEY_RE.match(cl_id) if cl_id else None

                if m_pref:
                    prefix = f"{m_pref.group(1)}:{m_pref.group(2)}("
                    for pk, pv in self._codelist_parents.items():
                        if pk.startswith(prefix) and pv:
                            parents = pv
                            break

            descriptions = self._codelist_descriptions.get(cl_id, {})

            if not descriptions:
                m_pref = self._CL_KEY_RE.match(cl_id) if cl_id else None

                if m_pref:
                    prefix = f"{m_pref.group(1)}:{m_pref.group(2)}("

                    for dk, dv in self._codelist_descriptions.items():
                        if dk.startswith(prefix) and dv:
                            descriptions = dv
                            break

            entries = params.get(dim_id, [])

            if dim_id in constraints:
                allowed = set(constraints[dim_id])
                # Filter params first; if that yields nothing (constraint
                # codes aren't in the params list), build entries directly
                # from the codelist so we always show labels.
                constrained_entries = [e for e in entries if e["value"] in allowed]

                if not constrained_entries and allowed:
                    constrained_entries = [
                        {"value": code, "label": codelist.get(code, code)}
                        for code in sorted(allowed)
                    ]
            else:
                constrained_entries = entries

            values = []

            for e in constrained_entries:
                v: dict = {
                    "value": e["value"],
                    "label": e["label"],
                    "description": descriptions.get(e["value"], e["label"]),
                }

                if e["value"] in parents:
                    v["parent"] = parents[e["value"]]

                values.append(v)

            result.append(
                {
                    "id": dim_id,
                    "position": dim["position"],
                    "name": dim.get("name", dim_id),
                    "codelist_id": cl_id,
                    "total_codes": cl_size,
                    "constrained_codes": len(constrained_entries),
                    "has_hierarchy": bool(parents),
                    "values": values,
                }
            )

        return result

    def get_table_groups(self, dataflow_id: str) -> list[dict]:
        """Return table groups within a dataflow.

        Checks ``_TABLE_GROUP_CANDIDATES`` in order (TABLE_IDENTIFIER,
        CHAPTER, …) and returns entries from the first matching dimension.

        Returns
        -------
        list[dict]
            [{value, label, description}, ...]  One per table group.
            Empty list if no recognised table-grouping dimension exists.
        """
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})
        table_dim = None

        for candidate in _TABLE_GROUP_CANDIDATES:
            for dim in dsd.get("dimensions", []):
                if dim["id"] == candidate:
                    table_dim = dim
                    break
            if table_dim is not None:
                break

        if table_dim is None:
            return []

        dim_id = table_dim["id"]
        cl_id = table_dim.get("codelist_id", "")
        params = self.get_dataflow_parameters(full_id)
        entries = params.get(dim_id, [])
        # Filter by constraints if available.
        constraints = self._dataflow_constraints.get(full_id, {})

        if dim_id in constraints:
            allowed = set(constraints[dim_id])
            entries = [e for e in entries if e["value"] in allowed]

        descriptions = self._codelist_descriptions.get(cl_id, {})

        return [
            {
                "value": e["value"],
                "label": e["label"],
                "description": descriptions.get(e["value"], e["label"]),
            }
            for e in entries
        ]

    # ------------------------------------------------------------------
    # New methods matching IMF interface (for migration parity)
    # ------------------------------------------------------------------

    def get_dataflow_hierarchies(self, dataflow_id: str) -> list[dict]:
        """Return available table / hierarchy identifiers for a dataflow.

        Checks ``_TABLE_GROUP_CANDIDATES`` for a grouping dimension and
        returns each of its codelist entries as a hierarchy.

        Returns
        -------
        list[dict]
            ``[{id, name, description, codelist_id}, ...]``
        """
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})

        table_dim = None
        for candidate in _TABLE_GROUP_CANDIDATES:
            for dim in dsd.get("dimensions", []):
                if dim["id"] == candidate:
                    table_dim = dim
                    break
            if table_dim is not None:
                break

        if table_dim is None:
            return []

        cl_id = table_dim.get("codelist_id", "")
        table_groups = self.get_table_groups(dataflow_id)

        return [
            {
                "id": g["value"],
                "name": g["label"],
                "description": g.get("description", g["label"]),
                "codelist_id": cl_id,
            }
            for g in table_groups
        ]

    def get_dataflow_table_structure(self, dataflow_id: str, table_id: str) -> dict:
        """Return the hierarchy structure for a specific table.

        Filters the indicator tree to codes belonging to the given
        ``TABLE_IDENTIFIER`` value, then returns the hierarchy with
        order / level / parent metadata.

        Parameters
        ----------
        dataflow_id : str
            Short or full dataflow ID.
        table_id : str
            A ``TABLE_IDENTIFIER`` value (e.g. ``"T101"``).

        Returns
        -------
        dict
            ``{hierarchy_id, hierarchy_name, indicators}`` where
            ``indicators`` is a flat list of entries::

                {code, label, order, level, parent, children}
        """
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)

        # Get the TABLE_IDENTIFIER label for the hierarchy name.
        groups = self.get_table_groups(dataflow_id)
        table_meta = next((g for g in groups if g["value"] == table_id), None)
        hierarchy_name = table_meta["label"] if table_meta else table_id

        # Build the indicator tree (full hierarchy for this dataflow).
        tree = self.get_indicator_tree(dataflow_id)

        # Flatten the tree into a structured list.
        flat: list[dict] = []
        counter = [0]

        def _walk(nodes: list[dict], level: int, parent: str | None) -> None:
            for node in nodes:
                children_codes = [c["code"] for c in node.get("children", [])]
                flat.append(
                    {
                        "code": node["code"],
                        "label": node.get("label", node["code"]),
                        "order": counter[0],
                        "level": level,
                        "parent": parent,
                        "children": children_codes,
                    }
                )
                counter[0] += 1
                _walk(node.get("children", []), level + 1, node["code"])

        _walk(tree, 0, None)

        return {
            "hierarchy_id": table_id,
            "hierarchy_name": hierarchy_name,
            "indicators": flat,
        }

    def search_dataflows(self, query: str) -> list[dict]:
        """Search dataflows by keyword.

        Parameters
        ----------
        query : str
            Space-separated search terms (AND logic).

        Returns
        -------
        list[dict]
            Matching dataflow entries from :attr:`dataflows`.
        """
        self._ensure_dataflows()
        terms = [t.lower() for t in query.strip().split() if t.strip()]
        if not terms:
            return list(self.dataflows.values())

        results: list[dict] = []
        for fid, entry in self.dataflows.items():
            text = " ".join(
                [
                    fid,
                    entry.get("name", ""),
                    entry.get("description", ""),
                    entry.get("short_id", ""),
                ]
            ).lower()
            if all(t in text for t in terms):
                results.append(entry)
        return results

    def describe_dataflow(self, dataflow_id: str) -> dict:
        """Return a comprehensive description of a dataflow and its parameters.

        Combines dataflow metadata, dimension info (with hierarchies and
        constraints), table groups, and indicator tree into one object.

        Returns
        -------
        dict
            {
                "dataflow_id": "DSD_NASU@DF_INDICATOR",
                "short_id": "DF_INDICATOR",
                "name": "SUT Indicators ...",
                "description": "...",
                "dimensions": [... from get_dimension_info ...],
                "table_groups": [... from get_table_groups ...],
                "indicator_dimension": "TRANSACTION",
                "indicator_count": 7,
                "indicator_tree": [... from get_indicator_tree ...],
            }
        """
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_description(full_id)
        df_meta = self.dataflows.get(full_id, {})
        dim_info = self.get_dimension_info(full_id)
        table_groups = self.get_table_groups(full_id)
        indicator_dim = self._find_indicator_dimension(full_id)
        indicator_tree = self.get_indicator_tree(full_id)

        # Count leaf indicators.
        def _count_leaves(nodes: list[dict]) -> int:
            total = 0

            for n in nodes:
                children = n.get("children", [])
                if children:
                    total += _count_leaves(children)
                else:
                    total += 1

            return total

        return {
            "dataflow_id": full_id,
            "short_id": df_meta.get("short_id", full_id.split("@")[-1]),
            "name": df_meta.get("name", full_id),
            "description": df_meta.get("description", ""),
            "dimensions": dim_info,
            "table_groups": table_groups,
            "indicator_dimension": indicator_dim or "",
            "indicator_count": _count_leaves(indicator_tree) if indicator_tree else 0,
            "indicator_tree": indicator_tree,
        }

    def search_indicators(
        self,
        query: str | None = None,
        dataflows: str | list[str] | None = None,
        keywords: str | list[str] | None = None,
    ) -> list[dict]:
        """Full-text search across dataflow indicators.

        Parameters
        ----------
        query : str, optional
            Search text.  Supports | (OR) within terms and implicit AND
            between space-separated words.  Semicolon ; separates
            alternative phrases (OR at the phrase level).
        dataflows : str or list[str], optional
            Restrict to specific dataflow(s).
        keywords : str or list[str], optional
            Post-filter keywords (prefix not  to exclude).

        Returns
        -------
        list[dict]
            Matching indicators with fields: dataflow_id, dataflow_name,
            dimension_id, indicator, label, description, symbol.
        """
        self._ensure_dataflows()

        # Determine target dataflows.
        scoped = False
        if dataflows:
            if isinstance(dataflows, str):
                dataflows = [d.strip() for d in dataflows.split(",")]
            target_ids = dataflows
            scoped = True
        elif not query and not keywords:
            raise OpenBBError(
                "At least one of 'query', 'dataflows', or 'keywords' is required."
            )
        else:
            target_ids = None  # Will use full search index.

        # -- Scoped search (specific dataflows) --
        _table_dims = set(_TABLE_GROUP_CANDIDATES)
        if scoped:
            all_indicators: list[dict] = []
            for df_id in target_ids:  # type: ignore[union-attr]
                full_id = None
                if df_id in self._dataflow_indicators_cache:
                    full_id = df_id
                else:
                    resolved = self._short_id_map.get(df_id)
                    if resolved and resolved in self._dataflow_indicators_cache:
                        full_id = resolved
                if full_id is None:
                    continue
                cached = self._dataflow_indicators_cache[full_id]
                constraints = self._dataflow_constraints.get(full_id, {})
                if constraints and cached:
                    allowed_sets: dict[str, set[str]] = {
                        k: set(v) for k, v in constraints.items()
                    }
                    for ind in cached:
                        dim_id = ind.get("dimension_id", "")
                        if dim_id in _table_dims:
                            continue
                        if (
                            not dim_id
                            or dim_id not in allowed_sets
                            or ind.get("indicator") in allowed_sets[dim_id]
                        ):
                            all_indicators.append(ind)
                else:
                    all_indicators.extend(
                        ind
                        for ind in cached
                        if ind.get("dimension_id", "") not in _table_dims
                    )

            if query:
                phrases = _parse_search_query(query)
                all_indicators = [
                    ind
                    for ind in all_indicators
                    if _matches_query(
                        f"{ind.get('label', '')} {ind.get('description', '')} "
                        f"{ind.get('dataflow_name', '')} {ind.get('dataflow_id', '')} "
                        f"{ind.get('indicator', '')}".lower(),
                        phrases,
                    )
                ]
        else:
            # -- Broad search (all cached dataflows) --
            # Use the pre-built search index for performance.
            search_index = self._get_search_index()
            phrases = _parse_search_query(query) if query else []
            all_indicators = []

            for search_text, ind in search_index:
                if phrases and not _matches_query(search_text, phrases):
                    continue
                all_indicators.append(ind)

        # Apply keyword post-filter.
        if keywords:
            if isinstance(keywords, str):
                keywords = [keywords]

            for raw_kw in keywords:
                kw = raw_kw.strip()

                if kw.lower().startswith("not "):
                    exclude_word = kw[4:].strip().lower()
                    all_indicators = [
                        i
                        for i in all_indicators
                        if exclude_word
                        not in f"{i.get('label', '')} {i.get('description', '')} {i.get('indicator', '')}".lower()
                    ]
                else:
                    include_word = kw.lower()
                    all_indicators = [
                        i
                        for i in all_indicators
                        if include_word
                        in f"{i.get('label', '')} {i.get('description', '')} {i.get('indicator', '')}".lower()
                    ]

        return all_indicators

    def _get_search_index(self) -> list[tuple[str, dict]]:
        """Return a lazily-built search index: [(search_text, indicator_dict), ...].

        The index covers ALL indicators in ``_dataflow_indicators_cache``,
        filtered by constraints.  The search_text is pre-lowered for fast
        substring matching.
        """
        if hasattr(self, "_search_index") and self._search_index is not None:
            return self._search_index

        _table_dims = set(_TABLE_GROUP_CANDIDATES)
        index: list[tuple[str, dict]] = []
        for full_id, cached in self._dataflow_indicators_cache.items():
            constraints = self._dataflow_constraints.get(full_id, {})
            allowed_sets: dict[str, set[str]] = (
                {k: set(v) for k, v in constraints.items()} if constraints else {}
            )
            for ind in cached:
                dim_id = ind.get("dimension_id", "")
                # Skip table-grouping dimensions (TABLE_IDENTIFIER, CHAPTER).
                if dim_id in _table_dims:
                    continue
                if (
                    allowed_sets
                    and dim_id
                    and dim_id in allowed_sets
                    and ind.get("indicator") not in allowed_sets[dim_id]
                ):
                    continue
                text = (
                    f"{ind.get('label', '')} {ind.get('description', '')} "
                    f"{ind.get('dataflow_name', '')} {ind.get('dataflow_id', '')} "
                    f"{ind.get('indicator', '')}"
                ).lower()
                index.append((text, ind))

        self._search_index = index

        return index

    def list_tables(
        self, query: str | None = None, topic: str | None = None
    ) -> list[dict]:
        """List all OECD tables (dataflows) with names and topics.

        Every OECD dataflow is a table.  Use ``query`` for keyword search
        and ``topic`` to filter by topic code (e.g. ``"ECO"``).

        Parameters
        ----------
        query : str, optional
            Keyword search (space-separated AND, ``|`` for OR within a
            word).  Matches table name, topic, dataflow ID.
        topic : str, optional
            Topic code filter (e.g. ``"ECO"``, ``"HEA"``).

        Returns
        -------
        list[dict]
            Each entry::

                {
                    "table_id":   "DF_T725R_Q",
                    "name":       "Quarterly Financial Balance Sheets ...",
                    "topic":      "Economy",
                    "subtopic":   "National accounts",
                    "dataflow_id": "DSD_NASEC20@DF_T725R_Q",
                }
        """
        rows = self.find_tables(query) if query else self.table_map()

        if topic:
            t = topic.upper()
            rows = [
                r
                for r in rows
                if r["topic"].upper() == t or r.get("path", "").upper().startswith(t)
            ]

        return [
            {
                "table_id": row["short_id"],
                "name": row["table"],
                "topic": row["topic"],
                "subtopic": row.get("subtopic", ""),
                "dataflow_id": row["dataflow_id"],
            }
            for row in rows
        ]

    def get_table(self, table_id: str) -> dict:
        """Get full metadata for a single table (dataflow).

        Returns the table name, description, and all queryable dimensions
        with their allowed values — everything needed to construct a data
        request.

        Parameters
        ----------
        table_id : str
            Dataflow short ID (e.g. ``"DF_T725R_Q"``) or full ID.

        Returns
        -------
        dict
            ``describe_dataflow()`` output::

                {
                    "dataflow_id":  "DSD_NASEC20@DF_T725R_Q",
                    "short_id":     "DF_T725R_Q",
                    "name":         "Quarterly Financial Balance Sheets ...",
                    "description":  "...",
                    "dimensions":   [{id, name, values: [{value, label}, ...]}, ...],
                    "indicator_dimension": "INSTR_ASSET",
                    "indicator_count": 42,
                    "indicator_tree": [...],
                }

        Raises
        ------
        KeyError
            If the dataflow is not found.
        """
        return self.describe_dataflow(table_id)

    _CL_KEY_RE = re.compile(r"^(.+):(.+)\((.+)\)$")

    def _find_codelist_by_prefix(self, codelist_id: str) -> dict[str, str] | None:
        """Find a codelist by id, handling version and parent-agency mismatches.

        DSDs may reference ``OECD.SDD.STES:CL_AREA(4.0)`` but the bulk
        codelist endpoint publishes shared codelists under the root agency:
        ``OECD:CL_AREA(1.1)``.  Climb the agency hierarchy to find them.

        Search order:
          1. Exact agency:id prefix (same agency, any version).
          2. Parent agencies in order (e.g. OECD.SDD → OECD) — handles
             sub-agency DSDs referencing root-agency published codelists.

        Must be called while holding ``_codelist_lock``.
        """
        m = self._CL_KEY_RE.match(codelist_id)

        if not m:
            return None

        agency = m.group(1)
        bare_id = m.group(2)
        # Pass 1: same agency:id, any version.
        prefix = f"{agency}:{bare_id}("

        for key, codes in self.codelists.items():
            if key.startswith(prefix) and codes:
                return codes
        # Pass 2: walk up the agency hierarchy (strip trailing .SEGMENT).
        parts = agency.split(".")

        while len(parts) > 1:
            parts = parts[:-1]
            parent = ".".join(parts)
            prefix = f"{parent}:{bare_id}("

            for key, codes in self.codelists.items():
                if key.startswith(prefix) and codes:
                    return codes

        return None

    def _get_codelist(
        self, codelist_id: str, _dataflow_id: str | None = None
    ) -> dict[str, str]:
        """Return {code: label} for *codelist_id*, fetching if needed.

        The codelist should already be present from the structure query with
        references=all.  If not — and the requesting dataflow's structure
        was seeded from the priority constant — upgrade to a full structural
        fetch (which pulls all agency-specific codelists).  Otherwise fall
        back to a standalone codelist fetch.

        Codelist IDs are fully-qualified (``agency:id(version)``).  When an
        exact match isn't found, a prefix match (same ``agency:id``,
        different version) is tried — SDMX versions are backwards-compatible.
        """
        with self._codelist_lock:
            if codelist_id in self.codelists and self.codelists[codelist_id]:
                return self.codelists[codelist_id]
            # Version mismatch fallback: DSD may reference v1.0 but the bulk
            # codelist fetch returned v1.2 from the same agency.
            prefix_match = self._find_codelist_by_prefix(codelist_id)

            if prefix_match:
                return prefix_match

        # If the dataflow has a partial structure (from the constant) or
        # was loaded from cache without codelists, force a full DSD fetch.
        if _dataflow_id:
            resolved = (
                self._resolve_dataflow_id(_dataflow_id)
                if "@" not in _dataflow_id
                else _dataflow_id
            )
            # Force-fetch whenever the codelist is missing, not just for
            # explicitly-tracked partial structures.
            if resolved in self.datastructures:
                self._ensure_structure(resolved, force=True)

                with self._codelist_lock:
                    if codelist_id in self.codelists and self.codelists[codelist_id]:
                        return self.codelists[codelist_id]

                    prefix_match = self._find_codelist_by_prefix(codelist_id)

                    if prefix_match:
                        return prefix_match

        # Standalone fetch as last resort.
        return self._fetch_single_codelist(codelist_id, _dataflow_id)

    def _fetch_single_codelist(
        self, codelist_id: str, _dataflow_id: str | None = None
    ) -> dict[str, str]:
        """Fetch a single codelist from the OECD structure API.

        Notes
        -----
        SDMX v2 URL pattern::

            GET /structure/codelist/{agency}/{codelist_id}

        ``codelist_id`` may be fully-qualified (``agency:id(version)``) or
        a bare name (``CL_FREQ``).
        """
        # Parse the fully-qualified key if present.
        _cl_key_re = re.compile(r"^([^:]+):([^(]+)\(([^)]+)\)$")
        m = _cl_key_re.match(codelist_id)
        if m:
            agency = m.group(1)
            bare_id = m.group(2)
            version = m.group(3)
        else:
            bare_id = codelist_id
            version = ""
            # Determine the agency from the dataflow if available.
            agency = "all"

            if _dataflow_id:
                resolved = (
                    self._resolve_dataflow_id(_dataflow_id)
                    if "@" not in _dataflow_id
                    else _dataflow_id
                )
                df_meta = self.dataflows.get(resolved, {})

                if df_meta.get("agency_id"):
                    agency = df_meta["agency_id"]

        # Try with the resolved agency.
        version_part = f"/{version}" if version else ""
        url = f"{BASE_URL}/structure/codelist/{agency}/{bare_id}{version_part}?references=none"
        try:
            resp = _make_request(url, headers={"Accept": _STRUCTURE_ACCEPT}, timeout=15)
            raw = resp.json()
            parsed, parsed_parents = _parse_sdmx_json_codelists(raw)

            with self._codelist_lock:
                for cl_id, codes in parsed.items():
                    if cl_id in self.codelists:
                        self.codelists[cl_id].update(codes)
                    else:
                        self.codelists[cl_id] = codes

                for cl_id, parents in parsed_parents.items():
                    if cl_id in self._codelist_parents:
                        self._codelist_parents[cl_id].update(parents)
                    else:
                        self._codelist_parents[cl_id] = parents
            # Return the target codelist.
            return self.codelists.get(codelist_id, {})
        except Exception:  # noqa: BLE001
            return {}

    def resolve_dataflow_triplet(self, dataflow_id: str) -> tuple[str, str, str]:
        """Resolve a dataflow id to (agency, full_id, version) for v2 URLs.

        Parameters
        ----------
        dataflow_id : str
            Short dataflow id ("DF_PRICES_ALL") or full v2 id
            ("DSD_PRICES@DF_PRICES_ALL").

        Returns
        -------
        tuple[str, str, str]
            (agency, full_id, version) where full_id is the v2
            structural form.
        """
        full_id = self._resolve_dataflow_id(dataflow_id)
        info = self.dataflows[full_id]

        return info["agency_id"], full_id, info["version"]

    def build_data_url(
        self,
        dataflow_id: str,
        dimension_filter: str = "*",
        last_n: int | None = None,
        first_n: int | None = None,
        detail: str = "dataonly",
    ) -> str:
        """Build a fully-qualified SDMX v2 data query URL.

        API docs §Data queries (v2):
            GET /data/dataflow/{agency}/{dataflow}/{version}/{filter}
              [?lastNObservations=N&dimensionAtObservation=TIME_PERIOD&…]

        v2 does NOT support startPeriod/endPeriod or format
        as query parameters.  Time filtering uses lastNObservations
        / firstNObservations.  Response format is negotiated via
        the Accept header at request time.

        Parameters
        ----------
        dataflow_id
            Short id ("DF_PRICES_ALL") or full v2 id.
        dimension_filter
            Dot-separated dimension values including TIME_PERIOD as the
            last position.  Use "*" for fully unfiltered.
            Empty positions are **not** allowed in v2; use * per
            dimension for wildcard.
        last_n
            lastNObservations parameter.
        first_n
            firstNObservations parameter.
        detail
            "full" / "dataonly" / "serieskeysonly" / "nodata".
        """
        agency, full_id, version = self.resolve_dataflow_triplet(dataflow_id)
        path = (
            f"{BASE_URL}/data/dataflow/{agency}/{full_id}/{version}/{dimension_filter}"
        )
        qp: list[str] = []

        # Only request TIME_PERIOD at observation level when the DSD
        # actually contains a time dimension.  Cross-sectional DSDs
        # (e.g. DF_FDI_BMD4) don't have one and the API rejects it.
        resolved = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(resolved)
        dsd = self.datastructures.get(resolved, {})
        if dsd.get("has_time_dimension", True):
            qp.append("dimensionAtObservation=TIME_PERIOD")

        if last_n is not None:
            qp.append(f"lastNObservations={last_n}")

        if first_n is not None:
            qp.append(f"firstNObservations={first_n}")

        qp.append(f"detail={detail}")

        return f"{path}?{'&'.join(qp)}"

    def build_dimension_filter(self, dataflow_id: str, **dimension_values: str) -> str:
        """Build the dot-separated dimension filter string for v2.

        In v2, ALL dimensions must be present (including TIME_PERIOD as the
        last position).  Unsupplied dimensions default to * (wildcard).
        TIME_PERIOD defaults to * unless explicitly provided.

        Examples
        --------
        >>> meta.build_dimension_filter(
        ...     "DF_KEI", REF_AREA="GBR", FREQ="M", MEASURE="IRLT"
        ... )
        'GBR.M.IRLT.*.*.*.*.*'
        """
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})

        # Get ALL dimensions in order (including TIME_PERIOD).
        all_dims = [
            d["id"]
            for d in sorted(dsd.get("dimensions", []), key=lambda d: d["position"])
        ]

        parts: list[str] = []
        for dim_id in all_dims:
            val = dimension_values.get(dim_id, "*")
            parts.append(val if val else "*")
        return ".".join(parts)

    # ---- dimension role classification -------------------------------------

    # Codelist size thresholds for role classification.
    _SELECTOR_MAX = 50  # ≤50 values → SELECTOR (defines table variants)

    def classify_dimensions(self, dataflow_id: str) -> dict[str, list[dict]]:
        """Classify all dimensions of *dataflow_id* into functional roles.

        Returns
        -------
        dict[str, list[dict]]
            Keys: "country", "freq", "fixed", "selector",
            "axis".

            * country – reference-area dimensions (REF_AREA, etc.).
            * freq – frequency dimension (FREQ).
            * fixed – dimensions with exactly 1 codelist value (pinned).
            * selector – small dimensions (2–50 values) that define table
              variants.  Each entry includes embedded values if available.
            * axis – large dimensions (>50 values) that serve as data axes
              or heavy filters.  Wildcarded in a default table query.

            Each entry is {id, position, name, codelist_id, codelist_size,
            role, values}.  values is {code: label} for fixed
            and selector roles; empty dict otherwise.
        """
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})
        classified: dict[str, list[dict]] = {
            "country": [],
            "freq": [],
            "fixed": [],
            "selector": [],
            "axis": [],
        }

        for dim in dsd.get("dimensions", []):
            dim_id = dim["id"]

            if dim_id == "TIME_PERIOD":
                continue

            # Get codelist size and values from loaded codelists.
            cl_id = dim.get("codelist_id", "")
            cl_size = 0
            cl_values: dict[str, str] = {}

            if cl_id and cl_id in self.codelists:
                cl_size = len(self.codelists[cl_id])
                cl_values = dict(self.codelists[cl_id])

            entry = {
                "id": dim_id,
                "position": dim["position"],
                "name": dim.get("name", dim_id),
                "codelist_id": dim.get("codelist_id", ""),
                "codelist_size": cl_size,
                "values": cl_values,
            }

            # Classify.
            if dim_id in _COUNTRY_DIMENSION_CANDIDATES:
                entry["role"] = "country"
                classified["country"].append(entry)
            elif dim_id == "FREQ":
                entry["role"] = "freq"
                classified["freq"].append(entry)
            elif cl_size <= 1:
                entry["role"] = "fixed"
                classified["fixed"].append(entry)
            elif cl_size <= self._SELECTOR_MAX:
                entry["role"] = "selector"
                classified["selector"].append(entry)
            else:
                entry["role"] = "axis"
                classified["axis"].append(entry)

        return classified

    def get_table_parameters(self, dataflow_id: str) -> dict[str, dict]:
        """Return the queryable dimensions for building table queries.

        Returns
        -------
        dict[str, dict]
            Keyed by dimension ID, where each value contains:

            * role - one of "country", "freq", "selector",
              "fixed", "axis".
            * values - {code: label} for dimensions with loaded
              codelists (selectors, fixed, freq).  Empty for large axes.
            * default - the default value when not explicitly specified:
              fixed uses the single available value; selector uses "*";
              country uses "*"; freq uses "A" if available, else
              first value; axis uses "*".
        """
        classified = self.classify_dimensions(dataflow_id)
        params: dict[str, dict] = {}

        for role, dims in classified.items():
            for dim in dims:
                default = "*"

                if role == "fixed":
                    # Pin to the only value.
                    default = next(iter(dim["values"])) if dim["values"] else "*"
                elif role == "freq":
                    vals = dim.get("values", {})
                    if "A" in vals:
                        default = "A"
                    elif vals:
                        default = next(iter(vals))
                # selector, country, axis all default to "*".

                params[dim["id"]] = {
                    "role": role,
                    "position": dim["position"],
                    "name": dim["name"],
                    "codelist_id": dim["codelist_id"],
                    "codelist_size": dim["codelist_size"],
                    "values": dim["values"],
                    "default": default,
                }

        return params

    def build_table_query(
        self,
        dataflow_id: str,
        country: str | list[str] | None = None,
        frequency: str | None = None,
        **selector_overrides: str,
    ) -> str:
        """Build a dimension filter string optimized for fetching a full table.

        Automatically pins fixed dimensions, defaults selectors to *,
        and applies the supplied overrides.  The result is a valid v2
        dimension filter suitable for build_data_url().

        Parameters
        ----------
        dataflow_id
            Short or full dataflow ID.
        country
            Country code(s).  None / "all" → "*" (all countries).
            A list like ["USA", "GBR"] is joined with +.
        frequency
            "A", "Q", "M", or None (default from metadata).
        **selector_overrides
            Dimension ID → value overrides.  Use "+"-separated codes
            for multi-select (e.g. MEASURE="CPI+IT_W").

        Returns
        -------
        str
            Dot-separated dimension filter with all positions filled.

        Example::

            build_table_query("DF_PRICES_ALL", country="USA+GBR", frequency="A",
                              METHODOLOGY="N", MEASURE="CPI", TRANSFORMATION="GY")
            # → "USA+GBR.A.N.CPI.*.*.N.GY"
        """
        full_id = self._resolve_dataflow_id(dataflow_id)
        table_params = self.get_table_parameters(full_id)
        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})
        # Get dimension order.
        all_dims = sorted(dsd.get("dimensions", []), key=lambda d: d["position"])
        # Resolve country input.
        country_val = "*"

        if country and str(country).strip().lower() not in ("", "all"):
            country_val = (
                "+".join(country) if isinstance(country, list) else str(country)
            )

        # Only apply country value to the primary country dimension
        # (first one, typically REF_AREA).  Secondary country dims
        # (e.g. COUNTERPART_AREA) stay as "*" unless explicitly overridden.
        primary_country_set = False
        parts: list[str] = []

        for dim in all_dims:
            dim_id = dim["id"]
            info = table_params.get(dim_id, {})
            role = info.get("role", "")

            if dim_id in selector_overrides:
                parts.append(selector_overrides[dim_id])
            elif dim_id == "TIME_PERIOD":
                parts.append("*")
            elif role == "country":
                if not primary_country_set:
                    parts.append(country_val)
                    primary_country_set = True
                else:
                    parts.append("*")
            elif role == "freq":
                parts.append(frequency if frequency else info.get("default", "*"))
            elif role == "fixed":
                parts.append(info.get("default", "*"))
            else:
                # selector or axis — use default ("*").
                parts.append(info.get("default", "*"))

        return ".".join(parts)

    def describe_table_dimensions(self, dataflow_id: str) -> list[dict]:
        """Return a human-readable summary of dimensions and their roles.

        Returns
        -------
        list[dict]
            Each entry has keys: id, name, role, codelist_size, default,
            sample_values.  sample_values shows up to 8 representative
            values for selectors.
        """
        table_params = self.get_table_parameters(dataflow_id)
        result: list[dict] = []

        for dim_id, info in sorted(
            table_params.items(), key=lambda x: x[1]["position"]
        ):
            sample = []

            if info["values"]:
                items = list(info["values"].items())[:8]
                sample = [{"code": k, "label": v} for k, v in items]

            result.append(
                {
                    "id": dim_id,
                    "name": info["name"],
                    "role": info["role"],
                    "codelist_size": info["codelist_size"],
                    "default": info["default"],
                    "sample_values": sample,
                }
            )
        return result

    def fetch_availability(
        self,
        dataflow_id: str,
        pinned: dict[str, str] | None = None,
    ) -> dict[str, list[str]]:
        """Query the OECD availability endpoint for valid dimension values.

        Given a set of already-pinned dimensions, returns the available
        values for every dimension in the DSD — reflecting the cross-
        dimensional constraints imposed by the pinned selections.

        Parameters
        ----------
        dataflow_id
            Short or full dataflow ID.
        pinned
            {dim_id: value} for already-selected dimensions.
            Supports "+"-separated multi-select (e.g. "USA+GBR").
            Omitted dimensions default to "*" (all values).

        Returns
        -------
        dict[str, list[str]]
            {dim_id: [available_codes, …]} for every dimension
            (excluding TIME_PERIOD), sorted alphabetically.
        """
        agency, full_id, version = self.resolve_dataflow_triplet(dataflow_id)
        dims = self.get_dimension_order(full_id)
        pinned = pinned or {}
        # Check cache (keyed by full_id + frozen pinned dict).
        cache_key = (
            f"{full_id}::{'|'.join(f'{k}={v}' for k, v in sorted(pinned.items()))}"
        )

        if cache_key in self._availability_cache:
            return self._availability_cache[cache_key]

        # Build the key filter in DSD dimension order.
        parts: list[str] = []

        for dim_id in dims:
            parts.append(pinned.get(dim_id, "*"))

        key_filter = ".".join(parts)
        url = f"{BASE_URL}/availability/dataflow/{agency}/{full_id}/{version}/{key_filter}"

        try:
            resp = _make_request(
                url,
                headers={"Accept": _STRUCTURE_ACCEPT},
                timeout=30,
            )
            raw = resp.json()
        except Exception as exc:
            raise OpenBBError(
                f"Failed to fetch availability for '{dataflow_id}': {exc}"
            ) from exc

        # Parse contentConstraints → cubeRegions → keyValues.
        available: dict[str, list[str]] = {}

        for cc in raw.get("data", raw).get("contentConstraints", []):
            for region in cc.get("cubeRegions", []):
                for member in region.get("keyValues", []):
                    dim_id = member.get("id", "")
                    if dim_id and dim_id != "TIME_PERIOD":
                        available[dim_id] = sorted(member.get("values", []))

        # Dimensions not returned by the endpoint still exist — they're
        # unconstrained (all codelist values remain valid).  Fill them in
        # from the codelist so callers always get a complete picture.
        for dim_id in dims:
            if dim_id not in available:
                cl = self.get_codelist_for_dimension(full_id, dim_id)
                available[dim_id] = sorted(cl.keys()) if cl else []

        # Intersect with DSD content constraints so that codelist-
        # fallback dimensions are narrowed to codes the dataflow actually
        # supports.  Multi-country ("+"-separated) availability queries
        # can cause the API to omit per-dimension constraints, resulting
        # in full-codelist fallback for dims like FREQ.
        constraints = self._dataflow_constraints.get(full_id, {})
        if constraints:
            for dim_id in dims:
                if dim_id in constraints and dim_id in available:
                    allowed = set(constraints[dim_id])
                    available[dim_id] = [c for c in available[dim_id] if c in allowed]

        self._availability_cache[cache_key] = available

        return available

    @classmethod
    def _reset(cls) -> None:
        """Destroy the singleton (for testing only)."""
        with cls._lock:
            cls._instance = None
            cls._initialized = False


def _extract_codelist_id_from_urn(urn: str) -> str:
    """Extract the fully-qualified codelist key from an SDMX URN string.

    Parameters
    ----------
    urn : str
        SDMX URN, e.g.::

            urn:sdmx:org.sdmx.infomodel.codelist.Codelist=OECD.SDD.TPS:CL_REF_AREA(3.0)
            urn:sdmx:org.sdmx.infomodel.codelist.Codelist=OECD:CL_FREQ(2.1)

    Returns
    -------
    str
        The fully-qualified key, e.g.
        ``"OECD.SDD.TPS:CL_REF_AREA(3.0)"`` or ``"OECD:CL_FREQ(2.1)"``.
    """
    # Pattern: ...=agency:id(version)
    match = re.search(r"=([^=]+:[^(]+\([^)]+\))", urn)
    if match:
        return match.group(1)
    # Fallback: between last ':' and '('.
    match2 = re.search(r":([^:(]+)\(", urn)

    if match2:
        return match2.group(1)

    if ":" in urn:
        return urn.rsplit(":", 1)[-1].split("(")[0]

    return urn


def _extract_concept_id_from_urn(urn: str) -> str:
    """Extract the concept ID from an SDMX concept identity URN.

    Parameters
    ----------
    urn : str
        SDMX concept URN, e.g.::

            urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept=OECD:CS_COMMON(2.0).FREQ

    Returns
    -------
    str
        The concept ID, e.g. "FREQ".
    """
    if "." in urn:
        return urn.rsplit(".", 1)[-1]

    return urn


def _parse_search_query(query: str) -> list[list[str]]:
    """Parse a search query into OR-groups of AND-terms.

    Semicolon ; separates phrases (OR at phrase level).
    Space within a phrase is implicit AND.
    Pipe | within a term is OR at term level.

    Returns
    -------
    list[list[str]]
        [[term1, term2], [term3]] where outer list is OR,
        inner lists are AND.
    """
    if not query:
        return []

    phrases = [p.strip() for p in query.split(";") if p.strip()]
    result: list[list[str]] = []

    for phrase in phrases:
        # Normalise operators before splitting on whitespace:
        #   |  (with optional surrounding spaces) → | with no spaces so that
        #      "CPI | inflation" becomes the single OR-term "cpi|inflation".
        #   +  is the AND operator — replace with a space so that
        #      "balance+trade" and "balance +trade" both become two AND-terms.
        words = re.sub(r"\s*\|\s*", "|", phrase)
        words = words.replace("+", " ")

        terms = [t.strip().lower() for t in words.split() if t.strip()]

        if terms:
            result.append(terms)

    return result


def _matches_query(text: str, phrases: list[list[str]]) -> bool:
    """Check if *text* matches any phrase (OR) where all terms match (AND).

    Within a single term, | is an OR: "gdp|gross" matches if
    *either* "gdp" or "gross" is in *text*.
    """
    if not phrases:
        return True

    return any(
        all(_term_matches(text, term) for term in and_terms) for and_terms in phrases
    )


def _term_matches(text: str, term: str) -> bool:
    """Check if *term* matches *text*, supporting | as intra-term OR."""
    alternatives = [t.strip() for t in term.split("|") if t.strip()]

    return any(alt in text for alt in alternatives)
