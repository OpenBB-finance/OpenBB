"""Indicator enumeration mixin."""

from __future__ import annotations

from openbb_imf.utils.metadata._constants import (
    INDICATOR_DIMENSION_CANDIDATES,
    INDICATOR_DIMENSION_SUBSTRINGS,
)
from openbb_imf.utils.metadata._typing import _MixinBase

_STANDARD_DIMS = frozenset(
    {
        "COUNTRY",
        "REF_AREA",
        "JURISDICTION",
        "AREA",
        "FREQUENCY",
        "FREQ",
        "INDICATOR",
        "TIME_PERIOD",
    }
)


class IndicatorMixin(_MixinBase):
    """Enumerate every indicator available in a dataflow."""

    def get_indicators_in(self: _MixinBase, dataflow_id: str) -> list:
        """Return the flat list of indicator entries for ``dataflow_id``."""
        cache = getattr(self, "_dataflow_indicators_cache", None)
        if cache is not None and dataflow_id in cache:
            return cache[dataflow_id]

        if dataflow_id not in self.dataflows:
            raise ValueError(f"Dataflow '{dataflow_id}' not found.")

        dataflow_obj = self.dataflows[dataflow_id]
        dataflow_name = dataflow_obj.get("name", "").replace("\\xa0", "").strip()
        structure_ref = dataflow_obj.get("structureRef", {})
        structure_id = structure_ref.get("id", "")
        agency_id = dataflow_obj.get("agencyID", structure_ref.get("agencyID", "IMF"))
        dsd_id = structure_ref.get("id", "")

        if not dsd_id or dsd_id not in self.datastructures:
            raise ValueError(f"Data structure not found for dataflow '{dataflow_id}'.")

        dsd = self.datastructures[dsd_id]
        all_dims = dsd.get("dimensions", [])

        try:
            params = self.get_dataflow_parameters(dataflow_id)
        except Exception:  # noqa: BLE001
            params = {}

        indicator_dim_ids = {
            d.get("id")
            for d in all_dims
            if d.get("id") and _is_indicator_dimension(d.get("id"))
        }
        extra_dimensions = sorted(
            d.get("id")
            for d in all_dims
            if d.get("id")
            and d.get("id") not in _STANDARD_DIMS
            and d.get("id") not in indicator_dim_ids
        )

        full_indicator_list: list = []

        for dim in all_dims:
            dim_id = dim.get("id")
            if not _is_indicator_dimension(dim_id):
                continue

            dim_params = params.get(dim_id, [])
            if not dim_params:
                continue

            codelist_id = self._resolve_codelist_id(dataflow_id, dsd_id, dim_id, dim)
            descriptions_map: dict = {}
            if codelist_id:
                descriptions_map = self._codelist_descriptions.get(codelist_id, {})
                if not descriptions_map and codelist_id not in self._codelist_cache:
                    try:
                        self._get_codelist_map(codelist_id, agency_id, dataflow_id)
                        descriptions_map = self._codelist_descriptions.get(
                            codelist_id, {}
                        )
                    except Exception:  # noqa: BLE001, S110
                        pass

            for param in dim_params:
                code_id = param["value"]
                full_indicator_list.append(
                    _make_indicator_entry(
                        dataflow_id=dataflow_id,
                        dataflow_name=dataflow_name,
                        structure_id=structure_id,
                        agency_id=agency_id,
                        dim_id=dim_id,
                        code_id=code_id,
                        label=param.get("label", code_id),
                        description=descriptions_map.get(code_id, ""),
                        extra_dimensions=extra_dimensions,
                    )
                )

        dim_ids = {d.get("id") for d in all_dims if d.get("id")}
        if "ACTIVITY" in dim_ids:
            activity_codelist_id = f"CL_{dataflow_id}_ACTIVITY"
            if activity_codelist_id in self._codelist_cache:
                codes_map = self._get_codelist_map(
                    activity_codelist_id, agency_id, dataflow_id
                )
                descriptions_map = self._codelist_descriptions.get(
                    activity_codelist_id, {}
                )
                for code_id, code_name in codes_map.items():
                    full_indicator_list.append(
                        _make_indicator_entry(
                            dataflow_id=dataflow_id,
                            dataflow_name=dataflow_name,
                            structure_id=structure_id,
                            agency_id=agency_id,
                            dim_id="ACTIVITY",
                            code_id=code_id,
                            label=code_name,
                            description=descriptions_map.get(code_id, ""),
                            extra_dimensions=extra_dimensions,
                        )
                    )

        if not full_indicator_list:
            raise KeyError(
                f"Could not find an indicator-like dimension for dataflow "
                f"'{dataflow_id}'."
            )

        if cache is not None:
            cache[dataflow_id] = full_indicator_list

        return full_indicator_list


def _is_indicator_dimension(dim_id: str | None) -> bool:
    """Return True if ``dim_id`` matches the indicator dimension whitelist."""
    if not dim_id:
        return False
    if dim_id in INDICATOR_DIMENSION_CANDIDATES:
        return True
    return any(token in dim_id for token in INDICATOR_DIMENSION_SUBSTRINGS)


def _make_indicator_entry(
    *,
    dataflow_id: str,
    dataflow_name: str,
    structure_id: str,
    agency_id: str,
    dim_id: str,
    code_id: str,
    label: str,
    description: str,
    extra_dimensions: list[str] | None = None,
) -> dict:
    """Build a single indicator dict."""
    return {
        "dataflow_id": dataflow_id,
        "dataflow_name": dataflow_name,
        "structure_id": structure_id,
        "agency_id": agency_id,
        "dimension_id": dim_id,
        "indicator": code_id,
        "label": label,
        "description": description,
        "series_id": f"{dataflow_id}::{code_id}",
        "extra_dimensions": list(extra_dimensions) if extra_dimensions else [],
    }
