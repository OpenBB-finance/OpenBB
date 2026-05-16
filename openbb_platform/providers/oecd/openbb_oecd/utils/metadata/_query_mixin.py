"""Dataflow triplet resolution, URL building, dimension classification, and query construction mixin."""

from openbb_oecd.utils.metadata._constants import (
    _COUNTRY_DIMENSION_CANDIDATES,
    _STRUCTURE_ACCEPT,
    BASE_URL,
)
from openbb_oecd.utils.metadata._helpers import _make_request
from openbb_oecd.utils.metadata._typing import _MixinBase


class QueryMixin(_MixinBase):
    """Dataflow triplet resolution, URL building, dimension filter, availability."""

    _SELECTOR_MAX = 50

    def resolve_dataflow_triplet(self, dataflow_id: str) -> tuple[str, str, str]:
        """Resolve a dataflow id to (agency, full_id, version) for v2 URLs."""
        full_id = self._resolve_dataflow_id(dataflow_id)
        info = self.dataflows[full_id]

        return info["agency_id"], full_id, info["version"]

    _LASTN_BLOCKED_DATAFLOWS = frozenset(
        {
            "DF_BATIS",
            "DF_BIMTS_HS2017_2D",
            "DF_BIMTS_CPA_2_1",
            "DF_EXTREME_TEMP_DDOWN",
            "DF_POP_AGE_DDOWN",
            "DF_SDBS_ISIC4",
            "DF_STES_REVISIONS",
            "DF_TIM_2023",
            "DF_TIM_2021",
            "DF_TIMBC_2023",
            "DF_UOE_FIN_INDIC_SOURCE_NATURE",
            "EXT_TEMP_P",
        }
    )

    _LASTN_BLOCKED_AGENCIES = frozenset(
        {
            "OECD.STI",
            "OECD.DCD",
        }
    )

    def build_data_url(
        self,
        dataflow_id: str,
        dimension_filter: str = "*",
        last_n: int | None = None,
        first_n: int | None = None,
        detail: str = "dataonly",
    ) -> str:
        """Build a fully-qualified SDMX v2 data query URL."""
        agency, full_id, version = self.resolve_dataflow_triplet(dataflow_id)
        url_id = full_id.replace("@", "%40")
        path = (
            f"{BASE_URL}/data/dataflow/{agency}/{url_id}/{version}/{dimension_filter}"
        )
        qp: list[str] = []

        resolved = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(resolved)
        dsd = self.datastructures.get(resolved, {})
        if dsd.get("has_time_dimension", True):
            qp.append("dimensionAtObservation=TIME_PERIOD")

        short_id = full_id.split("@")[-1] if "@" in full_id else full_id
        agency_prefix = ".".join(agency.split(".")[:2])
        _lastn_ok = (
            short_id not in self._LASTN_BLOCKED_DATAFLOWS
            and agency_prefix not in self._LASTN_BLOCKED_AGENCIES
        )

        if last_n is not None and _lastn_ok:
            qp.append(f"lastNObservations={last_n}")

        if first_n is not None and _lastn_ok:
            qp.append(f"firstNObservations={first_n}")

        qp.append(f"detail={detail}")

        return f"{path}?{'&'.join(qp)}"

    def build_dimension_filter(self, dataflow_id: str, **dimension_values: str) -> str:
        """Build the dot-separated dimension filter string for v2."""
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})

        all_dims = [
            d["id"]
            for d in sorted(dsd.get("dimensions", []), key=lambda d: d["position"])
        ]

        parts: list[str] = []
        for dim_id in all_dims:
            val = dimension_values.get(dim_id, "*")
            parts.append(val if val else "*")
        return ".".join(parts)

    def classify_dimensions(self, dataflow_id: str) -> dict[str, list[dict]]:
        """Classify all dimensions of *dataflow_id* into functional roles."""
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
        """Return the queryable dimensions for building table queries."""
        classified = self.classify_dimensions(dataflow_id)
        params: dict[str, dict] = {}

        for role, dims in classified.items():
            for dim in dims:
                default = "*"

                if role == "fixed":
                    default = next(iter(dim["values"])) if dim["values"] else "*"
                elif role == "freq":
                    vals = dim.get("values", {})
                    if "A" in vals:
                        default = "A"
                    elif vals:
                        default = next(iter(vals))

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
        """Build a dimension filter string optimized for fetching a full table."""
        full_id = self._resolve_dataflow_id(dataflow_id)
        table_params = self.get_table_parameters(full_id)
        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})
        all_dims = sorted(dsd.get("dimensions", []), key=lambda d: d["position"])
        country_val = "*"

        if country and str(country).strip().lower() not in ("", "all"):
            country_val = (
                "+".join(country) if isinstance(country, list) else str(country)
            )

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
                parts.append(info.get("default", "*"))

        return ".".join(parts)

    def describe_table_dimensions(self, dataflow_id: str) -> list[dict]:
        """Return a human-readable summary of dimensions and their roles."""
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
        """Query the OECD availability endpoint for valid dimension values."""
        agency, full_id, version = self.resolve_dataflow_triplet(dataflow_id)
        dims = self.get_dimension_order(full_id)
        pinned = pinned or {}
        cache_key = (
            f"{full_id}::{'|'.join(f'{k}={v}' for k, v in sorted(pinned.items()))}"
        )

        if cache_key in self._availability_cache:
            return self._availability_cache[cache_key]

        parts: list[str] = []

        for dim_id in dims:
            parts.append(pinned.get(dim_id, "*"))

        key_filter = ".".join(parts)
        url_id = full_id.replace("@", "%40")
        url = (
            f"{BASE_URL}/availability/dataflow/{agency}/{url_id}/{version}/{key_filter}"
        )

        try:
            resp = _make_request(
                url,
                headers={"Accept": _STRUCTURE_ACCEPT},
                timeout=30,
            )
            raw = resp.json()
        except Exception:
            fallback: dict[str, list[str]] = {}
            for dim_id in dims:
                cl = self.get_codelist_for_dimension(full_id, dim_id)
                fallback[dim_id] = sorted(cl.keys()) if cl else []
            self._availability_cache[cache_key] = fallback
            return fallback

        available: dict[str, list[str]] = {}

        for cc in raw.get("data", raw).get("contentConstraints", []):
            for region in cc.get("cubeRegions", []):
                for member in region.get("keyValues", []):
                    dim_id = member.get("id", "")
                    if dim_id and dim_id != "TIME_PERIOD":
                        available[dim_id] = sorted(member.get("values", []))

        for dim_id in dims:
            if dim_id not in available:
                cl = self.get_codelist_for_dimension(full_id, dim_id)
                available[dim_id] = sorted(cl.keys()) if cl else []

        constraints = self._dataflow_constraints.get(full_id, {})
        if constraints:
            for dim_id in dims:
                if dim_id in constraints and dim_id in available:
                    allowed = set(constraints[dim_id])
                    available[dim_id] = [c for c in available[dim_id] if c in allowed]

        self._availability_cache[cache_key] = available

        return available
