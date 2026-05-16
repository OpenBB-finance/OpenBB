"""Cache management mixin for OecdMetadata."""

import gzip
import json
import lzma
import warnings
from pathlib import Path

from openbb_oecd.utils.metadata._constants import _SHIPPED_CACHE_FILE
from openbb_oecd.utils.metadata._helpers import _get_user_cache_file
from openbb_oecd.utils.metadata._typing import _MixinBase

_XZ_MAGIC = b"\xfd7zXZ\x00"


class CacheMixin(_MixinBase):
    """Methods for reading, writing, and applying metadata cache blobs."""

    @staticmethod
    def _read_cache_file(path: Path) -> dict | None:
        """Read and return a cache blob, or *None* on any failure."""
        try:
            if not path.exists():
                return None
            raw = path.read_bytes()
            data = (
                lzma.decompress(raw) if raw[:6] == _XZ_MAGIC else gzip.decompress(raw)
            )
            return json.loads(data)
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
        self._infer_orphan_parents()
        self._dataflow_constraints.update(blob.get("dataflow_constraints", {}))
        self._table_map.update(blob.get("table_map", {}))
        for k, v in blob.get("dataflow_parameters", {}).items():
            if v:
                self._dataflow_parameters_cache[k] = v
        raw_indicators = blob.get("dataflow_indicators", {})

        for full_id, val in raw_indicators.items():
            if isinstance(val, dict) and "dims" in val:
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
        tax = blob.get("taxonomy_tree", [])

        if tax:
            self._taxonomy_tree = tax
            self._df_to_categories.update(blob.get("df_to_categories", {}))
            self._category_to_dfs.update(blob.get("category_to_dfs", {}))
            self._category_names.update(blob.get("category_names", {}))
            self._taxonomy_loaded = True

    def _infer_orphan_parents(self) -> None:
        """Infer parent for orphan codes using COMP_RULE annotations."""
        for cl_id, comp_rules in self._codelist_comp_rules.items():
            parents = self._codelist_parents.get(cl_id)
            if parents is None:
                continue
            for code, rule in comp_rules.items():
                if code in parents:
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

        if not ancestor_sets:  # pragma: no cover - unreachable: codes is non-empty (early-return above), so the for loop always appends at least one chain
            return None

        common = ancestor_sets[0]
        for s in ancestor_sets[1:]:
            common = common & s

        if not common:
            return None

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
        shipped = self._read_cache_file(_SHIPPED_CACHE_FILE)
        if shipped:
            self._apply_blob(shipped)
            loaded = True
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
        if not self._cache_dirty:  # type: ignore[has-type]
            return
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
            raw = json.dumps(blob, separators=(",", ":")).encode()
            cache_file.write_bytes(gzip.compress(raw, compresslevel=1))
            self._cache_dirty = False
        except Exception:  # noqa: BLE001
            warnings.warn(
                "Failed to persist OECD metadata cache.",
                stacklevel=2,
            )
