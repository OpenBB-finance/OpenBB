"""Dataflow, structure, and taxonomy loading mixin for OecdMetadata."""

import json
import re
import warnings

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_oecd.utils.metadata._constants import (
    _STRUCTURE_ACCEPT,
    BASE_URL,
)
from openbb_oecd.utils.metadata._helpers import (
    _extract_codelist_id_from_urn,
    _extract_concept_id_from_urn,
    _make_request,
    _parse_sdmx_json_codelists,
)
from openbb_oecd.utils.metadata._typing import _MixinBase


class LoaderMixin(_MixinBase):
    """Methods for lazy-loading dataflows, structures, taxonomy from SDMX API."""

    _full_catalogue_loaded: bool
    _taxonomy_loaded: bool

    def _ensure_dataflows(self) -> None:
        """Lazy-load the full dataflow catalogue if not yet populated."""
        if self._full_catalogue_loaded:
            _first = next(iter(self.dataflows.values()), None)
            if self.dataflows and _first is not None and not _first.get("annotations"):
                self._backfill_annotations()
            return

        url = f"{BASE_URL}/structure/dataflow"
        resp = _make_request(url, headers={"Accept": _STRUCTURE_ACCEPT})

        try:
            raw = resp.json()
        except (json.JSONDecodeError, AttributeError) as exc:
            raise OpenBBError(
                f"Failed to parse OECD dataflow catalogue from {url}"
            ) from exc

        raw_dfs = raw.get("data", raw).get("dataflows", [])

        for df in raw_dfs:
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
            short_id = full_id.split("@")[-1] if "@" in full_id else full_id
            annotations: dict[str, str] = {}
            for ann in df.get("annotations", []):
                ann_type = ann.get("type", "")
                if ann_type:
                    ann_text = ann.get("title", "") or ann.get("text", "")
                    if isinstance(ann_text, dict):
                        ann_text = ann_text.get("en", next(iter(ann_text.values()), ""))
                    annotations[ann_type] = str(ann_text) if ann_text else ""
            self.dataflows[full_id] = {
                "id": full_id,
                "short_id": short_id,
                "agency_id": agency_id,
                "version": version,
                "name": name,
                "description": description,
                "structure_ref": struct_ref,
                "annotations": annotations,
            }
            self._short_id_map[short_id] = full_id

        if self.dataflows:
            self._full_catalogue_loaded = True
            self._cache_dirty = True
            self._save_cache()

    def _backfill_annotations(self) -> None:
        """Fetch dataflow catalogue and merge annotations into existing entries."""
        url = f"{BASE_URL}/structure/dataflow"
        try:
            resp = _make_request(url, headers={"Accept": _STRUCTURE_ACCEPT})
            raw = resp.json()
        except Exception:  # noqa: BLE001
            return

        for df in raw.get("data", raw).get("dataflows", []):
            full_id = df.get("id", "")
            if full_id not in self.dataflows:
                continue
            annotations: dict[str, str] = {}
            for ann in df.get("annotations", []):
                ann_type = ann.get("type", "")
                if ann_type:
                    ann_text = ann.get("title", "") or ann.get("text", "")
                    if isinstance(ann_text, dict):
                        ann_text = ann_text.get("en", next(iter(ann_text.values()), ""))
                    annotations[ann_type] = str(ann_text) if ann_text else ""
            if annotations:
                self.dataflows[full_id]["annotations"] = annotations

        self._cache_dirty = True
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
        """Lazy-load the OECD topic taxonomy (category scheme + categorisations)."""
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
        """Recursively parse the category scheme into a tree + flat name map."""
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
            children, child_names = LoaderMixin._parse_category_tree(subcats, path)
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
        """Parse categorisation records into df<->category mappings."""
        from collections import defaultdict

        df_re = self._CATEGORISATION_DF_RE
        cat_re = self._CATEGORISATION_CAT_RE

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

        df_to_cats: dict[str, list[str]] = defaultdict(list)
        cat_to_dfs: dict[str, list[str]] = defaultdict(list)

        for (ext_id, cat_path), _ver in seen.items():
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
        """Resolve a short or full dataflow id to the canonical full id."""
        if dataflow_id in self.dataflows:
            return dataflow_id

        full_id = self._short_id_map.get(dataflow_id)

        if full_id:
            return full_id

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
        """Fetch and cache the narrative description for a single dataflow."""
        if getattr(self, "_descriptions_baked", False):
            return

        if not hasattr(self, "_description_fetched"):
            self._description_fetched: set = set()

        if full_id in self._description_fetched:
            return
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

    def _fetch_external_dsd(
        self,
        raw_data: dict,
        full_id: str,  # noqa: ARG002
    ) -> tuple[list[dict], dict]:
        """Follow the external link for dataflows whose DSD isn't on the main API."""
        for df in raw_data.get("dataflows", []):
            if not df.get("isExternalReference"):
                continue
            for link in df.get("links", []):
                href = link.get("href", "")
                if not href:
                    continue
                ext_url = f"{href}?references=all&detail=referencepartial"
                try:
                    ext_resp = _make_request(
                        ext_url, headers={"Accept": _STRUCTURE_ACCEPT}, timeout=30
                    )
                    ext_raw = ext_resp.json()
                    ext_data = ext_raw.get("data", ext_raw)
                    ext_dsds = ext_data.get("dataStructures", [])
                    if ext_dsds:
                        return ext_dsds, ext_data
                except Exception:  # noqa: S112
                    continue
        return [], raw_data

    def _ensure_structure(self, dataflow_id: str, *, force: bool = False) -> None:
        """Lazy-load the DSD, codelists and concept schemes for *dataflow_id*."""
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

        if not raw_dsds:
            raw_dsds, raw_data = self._fetch_external_dsd(raw_data, full_id)
            self._dataflow_parameters_cache.pop(full_id, None)

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
            break

        raw_dfs = raw_data.get("dataflows", [])

        for df in raw_dfs:
            desc_raw = df.get("descriptions", {})
            desc = (
                desc_raw.get("en", "") if isinstance(desc_raw, dict) else ""
            ) or df.get("description", "")

            if desc and desc != self.dataflows.get(full_id, {}).get("description", ""):
                desc_clean = re.sub(r"<[^>]+>", "", desc)
                desc_clean = re.sub(r"[ \t]+", " ", desc_clean).strip()
                self.dataflows.setdefault(full_id, {})["description"] = desc_clean
            break

        parsed_cls, parsed_parents = _parse_sdmx_json_codelists({"data": raw_data})

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

            raw_cls = raw_data.get("codelists", [])

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

        raw_constraints = raw_data.get("contentConstraints", [])

        if raw_constraints:
            constraints: dict[str, list[str]] = {}

            for cc in raw_constraints:
                for region in cc.get("cubeRegions", []):
                    for kv in region.get("keyValues", []):
                        dim_id = kv.get("id", "")
                        vals = kv.get("values", [])

                        if dim_id and vals:
                            if dim_id in constraints:
                                existing = set(constraints[dim_id])
                                constraints[dim_id] = sorted(existing | set(vals))
                            else:
                                constraints[dim_id] = sorted(vals)
            if constraints:
                self._dataflow_constraints[full_id] = constraints

        self._cache_dirty = True

    @staticmethod
    def _parse_dimension_list(dsd: dict) -> list[dict]:
        """Return ordered dimension descriptors from a DSD JSON object."""
        dims: list[dict] = []
        components = dsd.get("dataStructureComponents", {})
        dim_list = components.get("dimensionList", {}).get("dimensions", [])

        for dim in dim_list:
            dim_id = dim.get("id", "")
            position = dim.get("position", len(dims))
            local_repr = dim.get("localRepresentation", {})
            enum_ref = local_repr.get("enumeration", "")
            cl_id = _extract_codelist_id_from_urn(enum_ref) if enum_ref else ""
            concept_identity = dim.get("conceptIdentity", "")
            concept_id = (
                _extract_concept_id_from_urn(concept_identity)
                if concept_identity
                else dim_id
            )
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
