"""Indicator enumeration, codelist lookup, and country resolution mixin."""

import re

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_oecd.utils.metadata._constants import (
    _COUNTRY_DIMENSION_CANDIDATES,
    _INDICATOR_DIMENSION_CANDIDATES,
    _NON_INDICATOR_DIMENSIONS,
)
from openbb_oecd.utils.metadata._helpers import (
    _build_code_tree,
    _normalize_label,
    _parse_sdmx_json_codelists,
)
from openbb_oecd.utils.metadata._typing import _MixinBase


class IndicatorMixin(_MixinBase):
    """Indicator enumeration, codelist lookup, and country resolution."""

    def _get_indicator_dim(self, full_id: str) -> str | None:
        """Return the indicator dimension for *full_id* using cached data only."""
        if full_id in self._indicator_dim_cache:
            return self._indicator_dim_cache[full_id]

        dsd = self.datastructures.get(full_id, {})
        dim_ids = {d["id"] for d in dsd.get("dimensions", [])}

        _indicator_set = set(_INDICATOR_DIMENSION_CANDIDATES)
        layout_row = (
            self.dataflows.get(full_id, {}).get("annotations", {}).get("LAYOUT_ROW", "")
        )
        if layout_row:
            for lr_dim in (d.strip() for d in layout_row.split(",") if d.strip()):
                if lr_dim in dim_ids and lr_dim in _indicator_set:
                    self._indicator_dim_cache[full_id] = lr_dim
                    return lr_dim

        for candidate in _INDICATOR_DIMENSION_CANDIDATES:
            if candidate in dim_ids:
                self._indicator_dim_cache[full_id] = candidate
                return candidate

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
        """Find the indicator dimension ID for *dataflow_id*."""
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
                    cl = dict(self._get_codelist(cl_id, dataflow_id))
                    constraints = self._dataflow_constraints.get(full_id, {})
                    constrained_codes = constraints.get(dim_id, [])
                    if constrained_codes and any(
                        c not in cl for c in constrained_codes
                    ):
                        self._ensure_structure(full_id, force=True)
                        cl = dict(self._get_codelist(cl_id, dataflow_id))
                    return cl

                return {}

        return {}

    def resolve_country_codes(self, dataflow_id: str, country_input: str) -> list[str]:
        """Resolve user-supplied country string to a list of ISO codes."""
        if not country_input or country_input.strip().lower() in ("all", "*"):
            return []

        country_cl = self._get_country_codelist(dataflow_id)

        if not country_cl:
            return [c.strip().upper() for c in country_input.split(",") if c.strip()]

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
                    f"{', '.join(sample)}" + (" ..." if len(available) > 20 else "")
                )

        return resolved

    def _get_country_codelist(self, dataflow_id: str) -> dict[str, str]:
        """Return the country/ref-area codelist for *dataflow_id*, or {}."""
        full_id = self._resolve_dataflow_id(dataflow_id)
        if full_id in self.datastructures:
            dsd = self.datastructures[full_id]
            for dim in dsd.get("dimensions", []):
                if dim["id"] in _COUNTRY_DIMENSION_CANDIDATES:
                    cl_id = dim.get("codelist_id", "")
                    if cl_id:
                        return dict(self._get_codelist(cl_id, None))
        with self._codelist_lock:
            for key, codes in self.codelists.items():
                if ":CL_AREA(" in key and codes:
                    return dict(codes)
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
        """Enumerate all series-producing codes across ALL content dimensions."""
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

        _skip = (
            set(_COUNTRY_DIMENSION_CANDIDATES)
            | _NON_INDICATOR_DIMENSIONS
            | {"FREQ", "TIME_PERIOD"}
        )

        ind_dim = self._get_indicator_dim(full_id)
        content_dims: list[str] = []
        if ind_dim and ind_dim in params and params[ind_dim]:
            content_dims = [ind_dim]
        else:
            for d in self.get_dimension_order(full_id):
                if d not in _skip and d in params and params[d]:
                    content_dims.append(d)

        if not content_dims:
            self._dataflow_indicators_cache[full_id] = []
            return []

        constraints = self._dataflow_constraints.get(full_id, {})
        avail_cache: dict[str, set[str] | None] = {}
        for dim_id in content_dims:
            if dim_id in constraints:
                avail_cache[dim_id] = set(constraints[dim_id])
            else:
                avail_cache[dim_id] = None

        if all(v is None for v in avail_cache.values()):
            try:
                avail = self.fetch_availability(full_id)
                for dim_id in content_dims:
                    codes = avail.get(dim_id)
                    if codes is not None:
                        avail_cache[dim_id] = set(codes)
            except Exception:  # noqa: BLE001, S110
                pass

        dsd = self.datastructures.get(full_id, {})
        dim_codelist_map: dict[str, str] = {}
        for dim in dsd.get("dimensions", []):
            dim_codelist_map[dim["id"]] = dim.get("codelist_id", "")

        indicators: list[dict] = []
        seen_codes: set[str] = set()

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
        """Return all dataflow IDs that contain *indicator_code*."""
        result: list[str] = []

        for full_id, inds in self._dataflow_indicators_cache.items():
            for ind in inds:
                if ind.get("indicator") == indicator_code:
                    result.append(ind.get("dataflow_id", full_id))
                    break

        return result

    def get_codelist_hierarchy(self, codelist_id: str) -> dict[str, str]:
        """Return {code: parent_code} for a codelist with parent hierarchy."""
        return dict(self._codelist_parents.get(codelist_id, {}))

    def get_indicator_tree(self, dataflow_id: str) -> list[dict]:
        """Return indicators for *dataflow_id* as a hierarchical tree."""
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

        available_codes = {e["value"]: e["label"] for e in params.get(dim_id, [])}

        constraints = self._dataflow_constraints.get(full_id, {})

        if dim_id in constraints:
            constrained = set(constraints[dim_id])
            available_codes = {
                k: v for k, v in available_codes.items() if k in constrained
            }

        if not available_codes:
            return []

        return _build_code_tree(available_codes, parents, descriptions)

    _CL_KEY_RE = re.compile(r"^(.+):(.+)\((.+)\)$")

    def _find_codelist_by_prefix(self, codelist_id: str) -> dict[str, str] | None:
        """Find a codelist by id, merging all versions with the same bare ID."""
        m = self._CL_KEY_RE.match(codelist_id)

        if not m:
            return None

        agency = m.group(1)
        bare_id = m.group(2)
        prefixes = [f"{agency}:{bare_id}("]
        parts = agency.split(".")

        while len(parts) > 1:
            parts = parts[:-1]
            prefixes.append(f"{'.'.join(parts)}:{bare_id}(")

        merged: dict[str, str] = {}
        for prefix in prefixes:
            for key, codes in self.codelists.items():
                if key.startswith(prefix) and codes:
                    for code, label in codes.items():
                        if code not in merged:
                            merged[code] = label

        return merged or None

    def _get_codelist(
        self, codelist_id: str, _dataflow_id: str | None = None
    ) -> dict[str, str]:
        """Return {code: label} for *codelist_id*, fetching if needed."""
        with self._codelist_lock:
            exact = self.codelists.get(codelist_id)
            prefix_match = self._find_codelist_by_prefix(codelist_id)

            if exact and prefix_match and prefix_match is not exact:
                if len(prefix_match) > len(exact):
                    merged = dict(prefix_match)
                    merged.update(exact)
                    return merged
                return exact
            if exact:
                return exact
            if prefix_match:
                return prefix_match

        return self._fetch_single_codelist(codelist_id, _dataflow_id)

    def _fetch_single_codelist(
        self, codelist_id: str, _dataflow_id: str | None = None
    ) -> dict[str, str]:
        """Fetch a single codelist from the OECD structure API."""
        from openbb_oecd.utils.metadata._constants import (
            _STRUCTURE_ACCEPT,
            BASE_URL,
        )
        from openbb_oecd.utils.metadata._helpers import (
            _make_request,
        )

        _cl_key_re = re.compile(r"^([^:]+):([^(]+)\(([^)]+)\)$")
        m = _cl_key_re.match(codelist_id)
        if m:
            agency = m.group(1)
            bare_id = m.group(2)
            version = m.group(3)
        else:
            bare_id = codelist_id
            version = ""
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
            self._cache_dirty = True
            return self.codelists.get(codelist_id, {})
        except Exception:  # noqa: BLE001
            return {}
