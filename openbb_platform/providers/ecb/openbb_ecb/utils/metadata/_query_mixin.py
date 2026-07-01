"""Dataflow / dimension / codelist resolution against the cached catalog."""

from __future__ import annotations

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_ecb.utils.metadata._constants import AGENCY, MAX_DIMENSION_VALUES
from openbb_ecb.utils.metadata._typing import MetadataBase


class QueryMixin(MetadataBase):
    """Resolve dataflows, DSDs, dimensions and codelists."""

    def get_dataflow(self, dataflow_id: str) -> dict:
        """Return the cached dataflow record or raise."""
        df = self.dataflows.get(dataflow_id)
        if df is None:
            raise OpenBBError(
                f"Unknown ECB dataflow '{dataflow_id}'. "
                "Use `list_dataflows` to see available dataflows."
            )
        return df

    def get_dsd_for_dataflow(self, dataflow_id: str) -> dict:
        """Return the Data Structure Definition for a dataflow."""
        df = self.get_dataflow(dataflow_id)
        dsd_id = df.get("dsd_id")
        dsd = self.datastructures.get(dsd_id) if dsd_id else None
        if dsd is None:
            raise OpenBBError(
                f"No data structure found for ECB dataflow '{dataflow_id}'."
            )
        return dsd

    def concept_name(self, concept_id: str | None) -> str:
        """Return the human label for a concept id."""
        if not concept_id:
            return ""
        return self.concepts.get(concept_id, concept_id)

    def get_codelist(self, codelist_id: str, agency: str = AGENCY) -> dict[str, str]:
        """Return ``{code: label}`` for a codelist, fetching live if needed."""
        if not codelist_id:
            return {}
        codes = self.codelists.get(codelist_id)
        if codes:
            return codes
        return self._fetch_codelist_live(codelist_id, agency=agency)

    def get_dataflow_dimensions(self, dataflow_id: str) -> list[dict]:
        """Return ordered queryable dimensions with their valid values."""
        dsd = self.get_dsd_for_dataflow(dataflow_id)
        constraints = self.dataflow_constraints.get(dataflow_id, {})
        result: list[dict] = []
        for dim in dsd.get("dimensions", []):
            dim_id = dim.get("id")
            codelist_id = dim.get("codelist_id")
            codes = self.get_codelist(codelist_id) if codelist_id else {}
            allowed = constraints.get(dim_id)
            if allowed:
                items = [
                    {"value": code, "label": codes.get(code, code)} for code in allowed
                ]
            else:
                items = [
                    {"value": code, "label": label} for code, label in codes.items()
                ]
            truncated = len(items) > MAX_DIMENSION_VALUES
            result.append(
                {
                    "id": dim_id,
                    "name": self.concept_name(dim.get("concept_id")) or dim_id,
                    "position": dim.get("position"),
                    "codelist_id": codelist_id,
                    "n_values": len(items),
                    "values": items[:MAX_DIMENSION_VALUES],
                    "truncated": truncated,
                }
            )
        return result

    def get_dataflow_parameters(self, dataflow_id: str) -> dict[str, list[dict]]:
        """Return ``{dimension_id: [{label, value}]}`` for every dimension."""
        if dataflow_id in self._dataflow_parameters_cache:
            return self._dataflow_parameters_cache[dataflow_id]
        params: dict[str, list[dict]] = {}
        for dim in self.get_dataflow_dimensions(dataflow_id):
            params[dim["id"]] = [
                {"label": v["label"], "value": v["value"]} for v in dim["values"]
            ]
        self._dataflow_parameters_cache[dataflow_id] = params
        return params

    def resolve_dimension_values(
        self, dataflow_id: str, dimension_id: str
    ) -> list[dict]:
        """Return ``[{label, value}]`` for one dimension of a dataflow."""
        return self.get_dataflow_parameters(dataflow_id).get(dimension_id, [])
