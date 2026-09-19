"""Query mixin."""

from __future__ import annotations

import json

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_imf.utils.metadata._constants import (
    BASE_URL,
    COUNTRY_CONCEPT_CANDIDATES,
    COUNTRY_DIMENSION_CANDIDATES,
)
from openbb_imf.utils.metadata._typing import _MixinBase

_COMMON_CODELIST_ALIASES: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("REF_AREA", "AREA", "COUNTRY", "JURISDICTION", "GEOGRAPHICAL_AREA"), ("AREA",)),
    (("COUNTERPART_COUNTRY",), ("COUNTRY",)),
    (
        ("COMPOSITE_BREAKDOWN", "COMP_BREAKDOWN"),
        ("COMP_BREAKDOWN", "COMPOSITE_BREAKDOWN"),
    ),
    (("DISABILITY_STATUS", "DISABILITY"), ("DISABILITY",)),
    (("INCOME_WEALTH_QUANTILE", "QUANTILE"), ("QUANTILE",)),
    (("TYPE_OF_TRANSFORMATION", "TRANSFORMATION"), ("TRANSFORMATION",)),
    (("WGT_TYPE", "WEIGHT_TYPE", "CTOT_WEIGHT_TYPE"), ("WEIGHT_TYPE",)),
    (("INDICATOR", "INDICATORS"), ("INDICATOR",)),
    (("UNIT", "UNIT_MEASURE", "UNIT_MULT"), ("UNIT",)),
    (("REF_SECTOR", "SECTOR"), ("SECTOR",)),
    (("COUNTERPART_SECTOR",), ("SECTOR", "COUNTERPART_SECTOR")),
    (("INSTR_ASSET", "INSTRUMENT_ASSET"), ("INSTR_ASSET",)),
    (("ACCOUNTING_ENTRY",), ("ACCOUNTING_ENTRY",)),
    (
        ("EXPENDITURE",),
        ("COFOG", "COICOP_2018", "COICOP_1999", "COICOP"),
    ),
)

_ACTIVITY_FALLBACK_CODELISTS: tuple[str, ...] = (
    "CL_PPI_ACTIVITY",
    "CL_MCDREO_ACTIVITY",
    "CL_ACTIVITY_ISIC4",
    "CL_NEA_ACTIVITY",
    "CL_ACTIVITY",
)
_COICOP_FALLBACK_CODELISTS: tuple[str, ...] = ("CL_COICOP_1999", "CL_COICOP_2018")


class QueryMixin(_MixinBase):
    """Parameter derivation, constraint fetching, codelist resolution."""

    def get_dataflow_parameters(
        self: _MixinBase, dataflow_id: str
    ) -> dict[str, list[dict]]:
        """Return ``{dim_id: [{label, value}]}`` for every queryable dimension."""
        if dataflow_id not in self.dataflows:
            raise ValueError(f"Dataflow '{dataflow_id}' not found.")

        if (
            hasattr(self, "_dataflow_parameters_cache")
            and dataflow_id in self._dataflow_parameters_cache
        ):
            return self._dataflow_parameters_cache[dataflow_id]

        df_obj = self.dataflows[dataflow_id]
        agency_id = df_obj.get("agencyID")
        dsd_id = df_obj.get("structureRef", {}).get("id")
        dsd = self.datastructures.get(dsd_id, {})
        if not dsd:
            return {}

        dimensions_metadata = {
            dim["id"]: dim for dim in dsd.get("dimensions", []) if dim.get("id")
        }

        constraints_response = self.get_available_constraints(
            dataflow_id=dataflow_id,
            key="all",
            component_id="all",
            mode="available",
            references="all",
        )
        key_values = constraints_response.get("key_values", [])
        constrained_values_map = {kv["id"]: kv.get("values", []) for kv in key_values}

        parameters: dict[str, list[dict]] = {}

        for dim_id in dimensions_metadata:
            if dim_id == "TIME_PERIOD":
                continue

            dim_meta = dimensions_metadata.get(dim_id, {})
            codelist_id = self._resolve_codelist_id(
                dataflow_id, dsd_id, dim_id, dim_meta
            )
            if not codelist_id:
                continue

            full_codes = self._codelist_cache.get(codelist_id, {})
            if not full_codes and agency_id:
                full_codes = (
                    self._get_codelist_map(
                        codelist_id,
                        agency_id,
                        dataflow_id,
                        include_descriptions=False,
                    )
                    or {}
                )
            if not full_codes:
                continue

            value_ids_to_use = (
                constrained_values_map[dim_id]
                if dim_id in constrained_values_map
                else list(full_codes.keys())
            )

            options: list = []
            for val_id in value_ids_to_use:
                label = full_codes.get(val_id, val_id)
                if isinstance(label, dict):
                    label = label.get("name", val_id)
                if not label or label == val_id:
                    label = val_id
                options.append({"label": label, "value": val_id.strip()})

            if options:
                parameters[dim_id] = options

        time_period_options, _ = self._build_time_period_parameters(
            constraints_response
        )
        if time_period_options:
            parameters["TIME_PERIOD"] = time_period_options

        if hasattr(self, "_dataflow_parameters_cache"):
            self._dataflow_parameters_cache[dataflow_id] = parameters

        return parameters

    def get_available_constraints(
        self: _MixinBase,
        dataflow_id: str,
        key: str,
        component_id: str | None = None,
        mode: str | None = None,
        references: str | None = None,
        **kwargs,
    ) -> dict:
        """Fetch availability constraints for a given dataflow and key."""
        from openbb_core.provider.utils.helpers import make_request
        from requests.exceptions import RequestException

        if dataflow_id not in self.dataflows:
            raise ValueError(f"Dataflow '{dataflow_id}' not found.")

        kwargs_tuple = tuple(sorted(kwargs.items()))
        cache_key = (
            f"{dataflow_id}:{key}:{component_id}:{mode}:{references}:{kwargs_tuple}"
        )

        with self._constraints_lock:
            if cached := self._constraints_cache.get(cache_key):
                return cached

        df = self.dataflows[dataflow_id]
        agency_id = df.get("agencyID")
        if not agency_id:
            raise ValueError(f"Agency ID not found for dataflow '{dataflow_id}'.")

        base_url = (
            f"{BASE_URL}/availability/dataflow/"
            f"{agency_id}/{dataflow_id}/%2B/{key}/{component_id or 'all'}"
        )
        query_params = {"mode": mode, "references": references}
        query_params.update({f"c[{k}]": v for k, v in kwargs.items() if v})
        query_params = {k: v for k, v in query_params.items() if v is not None}
        url = (
            base_url + "?" + "&".join(f"{k}={v}" for k, v in query_params.items())
            if query_params
            else base_url
        )

        headers = {
            "Accept": "application/json",
            "User-Agent": "Open Data Platform - IMF Metadata Utility",
        }
        try:
            response = make_request(url, headers=headers)
            response.raise_for_status()
            json_response = response.json()
        except json.JSONDecodeError as e:
            raise OpenBBError(
                f"Unexpected response format when fetching constraints "
                f"{dataflow_id}: {e} -> {url}"
            ) from None
        except RequestException as e:
            raise OpenBBError(
                f"An error occurred while fetching constraints "
                f"{dataflow_id}: {e} -> {url}"
            ) from None

        extracted: dict[str, list] = {}
        for constraint in json_response.get("data", {}).get("dataConstraints", []):
            for region in constraint.get("cubeRegions", []):
                _collect_constraint_values(region.get("keyValues", []), extracted)
                _collect_constraint_values(region.get("components", []), extracted)

        for dim_id, values in list(extracted.items()):
            extracted[dim_id] = list({v for v in values if v})

        result = {
            "key_values": [{"id": k, "values": v} for k, v in extracted.items()],
            "full_response": json_response,
        }
        with self._constraints_lock:
            self._constraints_cache[cache_key] = result
        return result

    def _resolve_codelist_id(
        self: _MixinBase,
        dataflow_id: str,
        dsd_id: str | None,
        dim_id: str,
        dim_meta: dict,
    ) -> str | None:
        """Find the cached codelist id for a dimension on a dataflow."""
        if not dim_id:
            return None

        representation = dim_meta.get("representation", {})
        codelist_ref = representation.get("codelist")
        if isinstance(codelist_ref, dict):
            return codelist_ref.get("id")
        if isinstance(codelist_ref, str):
            return codelist_ref

        concept_ref = dim_meta.get("conceptRef") or {}
        concept_id = concept_ref.get("id")
        scheme_id = concept_ref.get("maintainableParentID")
        if concept_id and scheme_id:
            scheme = self.conceptschemes.get(scheme_id, {})
            for concept in scheme.get("concepts", []):
                if concept.get("id") == concept_id:
                    cl_id = concept.get("codelist_id")
                    if cl_id:
                        return cl_id
                    break

        candidates: list[str] = []
        seen: set[str] = set()

        def add(candidate: str) -> None:
            if candidate and candidate not in seen:
                candidates.append(candidate)
                seen.add(candidate)

        is_country_dim = dim_id.upper() in COUNTRY_DIMENSION_CANDIDATES or (
            concept_id and concept_id.upper() in COUNTRY_CONCEPT_CANDIDATES
        )

        if is_country_dim and dataflow_id:
            base_dataflow = dataflow_id.split("_", maxsplit=1)[0]
            add(f"CL_{base_dataflow}_ISO_COUNTRY")
            add(f"CL_{dataflow_id}_COUNTRY")
            add(f"CL_{base_dataflow}_COUNTRY")

        if dataflow_id:
            add(f"CL_{dataflow_id}_{dim_id}")
            add(f"CL_{dataflow_id}_{dim_id}_PUB")
            df_tokens = dataflow_id.split("_")
            dim_tokens = dim_id.split("_")
            shared = 0
            while (
                shared < len(df_tokens)
                and shared < len(dim_tokens)
                and df_tokens[shared] == dim_tokens[shared]
            ):
                shared += 1
            if 0 < shared < len(dim_tokens):
                trimmed = "_".join(dim_tokens[shared:])
                add(f"CL_{dataflow_id}_{trimmed}")
                add(f"CL_{dataflow_id}_{trimmed}_PUB")
            if "COUNTRY" in dim_id:
                add(f"CL_{dataflow_id}_COUNTRY")
                add(f"CL_{dataflow_id}_COUNTRY_PUB")
            if "_" in dataflow_id:
                base_dataflow = dataflow_id.split("_", maxsplit=1)[0]
                add(f"CL_{base_dataflow}_{dim_id}")
                add(f"CL_{base_dataflow}_{dim_id}_PUB")

        if dsd_id:
            add(f"CL_{dsd_id.replace('DSD_', '')}_{dim_id}")

        parent_scheme_id = concept_ref.get("maintainableParentID")
        if parent_scheme_id:
            scheme_base = parent_scheme_id.replace("CS_", "CL_", 1)
            add(f"{scheme_base}_{dim_id}")
            add(scheme_base)

        add(f"CL_{dim_id}")
        if concept_id:
            add(f"CL_{concept_id}")

        for candidate in candidates:
            if candidate in self._codelist_cache:
                return candidate

        cache_keys_upper = {k.upper(): k for k in self._codelist_cache}
        for candidate in candidates:
            actual = cache_keys_upper.get(candidate.upper())
            if actual:
                return actual

        for patterns, base_names in _COMMON_CODELIST_ALIASES:
            if any(p in dim_id.upper() for p in patterns):
                for base_name in base_names:
                    specific_cl = f"CL_{dataflow_id}_{base_name}"
                    if specific_cl in self._codelist_cache:
                        return specific_cl
                    generic_cl = f"CL_{base_name}"
                    if generic_cl in self._codelist_cache:
                        return generic_cl

        if "COUNTERPART_" in dim_id:
            base_dim_id = dim_id.replace("COUNTERPART_", "")
            if dsd_id and dsd_id in self.datastructures:
                dsd = self.datastructures[dsd_id]
                for d in dsd.get("dimensions", []):
                    if d.get("id") == base_dim_id:
                        return self._resolve_codelist_id(
                            dataflow_id, dsd_id, base_dim_id, d
                        )

        dim_upper = dim_id.upper()
        if "ACTIVITY" in dim_upper or "PRODUCTION_INDEX" in dim_upper:
            for candidate in _ACTIVITY_FALLBACK_CODELISTS:
                if candidate in self._codelist_cache:
                    return candidate
        if "COICOP" in dim_upper:
            for candidate in _COICOP_FALLBACK_CODELISTS:
                if candidate in self._codelist_cache:
                    return candidate

        for cache_key in self._codelist_cache:
            if cache_key.startswith("CL_MASTER"):
                continue
            if dim_upper in cache_key.upper():
                return cache_key

        dim_parts = [p for p in dim_id.split("_") if len(p) > 2]
        if len(dim_parts) > 1:
            for cache_key in self._codelist_cache:
                if cache_key.startswith("CL_MASTER"):
                    continue
                cache_key_upper = cache_key.upper()
                if all(part.upper() in cache_key_upper for part in dim_parts):
                    return cache_key

        return candidates[0] if candidates else None


def _collect_constraint_values(items: list, into: dict[str, list]) -> None:
    """Extract dimension values from ``keyValues`` / ``components`` entries."""
    for item in items:
        dim_id = item.get("id")
        if not dim_id:
            continue
        into.setdefault(dim_id, [])
        for val in item.get("values", []):
            if isinstance(val, dict):
                into[dim_id].append(val.get("value"))
            else:
                into[dim_id].append(val)
