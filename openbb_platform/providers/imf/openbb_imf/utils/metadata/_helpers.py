"""IMF metadata helper mixin."""

from __future__ import annotations

from openbb_imf.utils.helpers import (
    build_codelist_to_hierarchies_map,
    build_hierarchy_to_codelist_map,
    build_time_period_params,
    extract_all_codelists_from_hierarchy,
    parse_agency_from_urn,
    parse_codelist_id_from_urn,
    parse_codelist_urn,
    parse_indicator_code_from_urn,
    parse_search_query,
)
from openbb_imf.utils.metadata._typing import _MixinBase


class HelpersMixin(_MixinBase):
    """URN parsing, hierarchy maps, and time-period derivation."""

    @staticmethod
    def _parse_agency_from_urn(code_urn: str) -> str | None:
        """Return the agency ID embedded in a hierarchicalCode URN."""
        return parse_agency_from_urn(code_urn)

    @staticmethod
    def _parse_codelist_urn(urn: str) -> str | None:
        """Return the codelist ID embedded in an ``owningCodelistUrn``."""
        return parse_codelist_urn(urn)

    @staticmethod
    def _parse_indicator_code_from_urn(code_urn: str) -> str | None:
        """Return the trailing code ID embedded in a hierarchicalCode URN."""
        return parse_indicator_code_from_urn(code_urn)

    @staticmethod
    def _parse_codelist_id_from_urn(code_urn: str) -> str | None:
        """Return the codelist ID embedded in a hierarchicalCode URN."""
        return parse_codelist_id_from_urn(code_urn)

    @staticmethod
    def _parse_query(query: str) -> list[list[str]]:
        """Parse a search query into OR-groups of AND-terms."""
        return parse_search_query(query)

    @staticmethod
    def _build_time_period_parameters(
        constraints_response: dict | None,
    ) -> tuple[list[dict], str | None]:
        """Derive time-period parameters from a constraints response."""
        return build_time_period_params(constraints_response)

    def _extract_all_codelists_from_hierarchy(
        self: _MixinBase, hierarchy: dict
    ) -> set[str]:
        """Return codelist IDs referenced in a hierarchy tree."""
        return extract_all_codelists_from_hierarchy(hierarchy)

    def _build_hierarchy_to_codelist_map(self: _MixinBase) -> dict[str, str]:
        """Return ``{hierarchy_id: owning_codelist_id}``."""
        return build_hierarchy_to_codelist_map(self.hierarchies)

    def _build_codelist_to_hierarchies_map(self: _MixinBase) -> dict[str, list[str]]:
        """Return ``{codelist_id: [hierarchy_id, ...]}``."""
        return build_codelist_to_hierarchies_map(self.hierarchies)

    def _get_dimension_for_codelist(
        self: _MixinBase, dataflow_id: str, codelist_id: str
    ) -> str | None:
        """Find the dimension in ``dataflow_id`` that uses ``codelist_id``."""
        if dataflow_id not in self.dataflows:
            return None

        df_obj = self.dataflows[dataflow_id]
        dsd_id = df_obj.get("structureRef", {}).get("id")
        if not dsd_id or dsd_id not in self.datastructures:
            return None

        dsd = self.datastructures[dsd_id]
        dimensions = dsd.get("dimensions", [])

        for dim in dimensions:
            dim_id = dim.get("id")
            if not dim_id:
                continue
            resolved = self._resolve_codelist_id(dataflow_id, dsd_id, dim_id, dim)
            if resolved == codelist_id:
                return dim_id

        segments = {seg.upper() for seg in codelist_id.split("_")}
        for dim in dimensions:
            dim_id = dim.get("id")
            if dim_id and dim_id.upper() in segments:
                return dim_id

        codelist_upper = codelist_id.upper()
        for dim in dimensions:
            dim_id = dim.get("id")
            if dim_id and dim_id.upper() in codelist_upper:
                return dim_id

        return None
