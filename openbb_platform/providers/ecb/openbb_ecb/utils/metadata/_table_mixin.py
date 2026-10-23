"""ECB presentation tables: JDF hierarchies and data-portal publications."""

from __future__ import annotations

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_ecb.utils.metadata._typing import MetadataBase

ROW_LABEL_CODELIST = "JDF_ROW_LABELS"

_TABLE_DESCRIPTIONS: dict[str, str] = {
    "BSI_MFI_BALANCE_SHEET": "MFI balance sheet",
    "BSI_MFI_DOMESTIC_CROSS_BORDER": "MFI domestic and cross-border positions",
    "BSI_MFI_GROWTH_RATES": "MFI balance sheet growth rates",
    "EXR_HCI_CPI": "Harmonised competitiveness indicators, CPI-deflated",
    "EXR_HCI_GDP": "Harmonised competitiveness indicators, GDP-deflated",
    "EXR_HCI_ULCT": "Harmonised competitiveness indicators, unit labour costs",
    "ICP_COICOP_ANR": "HICP by COICOP, annual rate of change",
    "ICP_COICOP_INW": "HICP by COICOP, index weights",
    "ICP_COICOP_INX": "HICP by COICOP, index",
    "ICP_ECONOMIC_ACTIVITIES_ANR": "HICP by economic activity, annual rate of change",
    "ICP_ECONOMIC_ACTIVITIES_INW": "HICP by economic activity, index weights",
    "ICP_ECONOMIC_ACTIVITIES_INX": "HICP by economic activity, index",
    "IVF_ASSETS_LIABILITIES": "Investment fund assets and liabilities",
    "IVF_SHARES": "Investment fund shares/units issued",
    "MFI_MFI_LIST": "List of monetary financial institutions",
    "MFI_MFI_LIST_NEA": "List of MFIs, non-euro area",
    "MIR_MFI_INTEREST_RATES": "MFI interest rates on loans and deposits",
    "PSS_PAYMENTS_N": "Payments, number of transactions",
    "PSS_PAYMENTS_N_NEA": "Payments, number of transactions, non-euro area",
    "PSS_PAYMENTS_P": "Payments, number of transactions, share",
    "PSS_PAYMENTS_P_NEA": "Payments, number of transactions share, non-euro area",
    "PSS_PAYMENTS_V": "Payments, value of transactions",
    "PSS_PAYMENTS_V_NEA": "Payments, value of transactions, non-euro area",
    "RA6_RESERVE_ASSETS": "Reserve assets",
    "SEC_OAT_DEBT_SECURITIES": "Debt securities outstanding",
    "SEC_OAT_LISTED_SHARES": "Listed shares outstanding",
    "MNA_GDP_GROWTH_QOQ": "GDP growth, quarter-on-quarter",
    "MNA_GDP_GROWTH_YOY": "GDP growth, year-on-year",
    "MNA_A_GDP_GROWTH_QOQ": "GDP growth, quarter-on-quarter",
    "MNA_B_GDP_GROWTH_YOY": "GDP growth, year-on-year",
    "MNA_GDP_CONTRIBUTIONS_QOQ": "GDP contributions, quarter-on-quarter",
    "MNA_GDP_CONTRIBUTIONS_YOY": "GDP contributions, year-on-year",
    "MNA_C_GDP_CONTRIBUTIONS_QOQ": "GDP contributions, quarter-on-quarter",
    "MNA_D_GDP_CONTRIBUTIONS_YOY": "GDP contributions, year-on-year",
    "ICPF_PENSION_FUNDS": "Pension funds assets and liabilities",
}


class TableMixin(MetadataBase):
    """List and resolve ECB presentation tables from both sources."""

    def _jdf_label(self, table_id: str, dataflow_id: str) -> str:
        """Build a readable label for a JDF hierarchical table."""
        core = table_id.split("@", 1)[0]
        if core.startswith("HCL_JDF_"):
            core = core[len("HCL_JDF_") :]
        description = _TABLE_DESCRIPTIONS.get(core)
        if description is None:
            fragment = core
            if fragment.startswith(f"{dataflow_id}_"):
                fragment = fragment[len(dataflow_id) + 1 :]
            description = fragment.replace("_", " ").title() or dataflow_id
        return f"{description} ({dataflow_id})"

    def _publication_label(self, table: dict) -> str:
        """Build a readable label for a data-portal publication table."""
        title = table.get("title") or table.get("id") or ""
        category = table.get("category") or ""
        return f"{category} — {title}" if category else title

    def list_tables(self) -> list[dict]:
        """Return ``[{value, label, category, subcategory, source}]`` per table."""
        out: list[dict] = []
        for table_id, table in self.presentation_tables.items():
            if table.get("source") == "jdf":
                dataflow_id = table.get("dataflow_id") or ""
                if dataflow_id not in self.dataflows:
                    continue
                out.append(
                    {
                        "value": table_id,
                        "label": self._jdf_label(table_id, dataflow_id),
                        "category": "Hierarchical tables",
                        "subcategory": dataflow_id,
                        "source": "jdf",
                    }
                )
            else:
                out.append(
                    {
                        "value": table_id,
                        "label": self._publication_label(table),
                        "category": table.get("category") or "",
                        "subcategory": table.get("subcategory") or "",
                        "source": "publications",
                    }
                )
        return sorted(out, key=lambda t: (t["category"], t["label"]))

    def list_tables_for_dataflow(self, dataflow_id: str) -> list[dict]:
        """Return the presentation tables that publish data from ``dataflow_id``."""
        ids: set[str] = set()
        for table_id, table in self.presentation_tables.items():
            if table.get("dataflow_id") == dataflow_id or any(
                row.get("flow") == dataflow_id for row in table.get("rows", [])
            ):
                ids.add(table_id)
        return [t for t in self.list_tables() if t["value"] in ids]

    def get_table(self, table_id: str) -> dict:
        """Return the cached presentation table or raise."""
        table = self.presentation_tables.get(table_id)
        if table is None:
            raise OpenBBError(
                f"Unknown ECB presentation table '{table_id}'. "
                "Use `list_tables` to see available tables."
            )
        return table

    def get_table_rows(self, table_id: str) -> list[dict]:
        """Return a publication table's ordered ``[{flow, key}]`` rows."""
        return self.get_table(table_id).get("rows") or []

    def resolve_node_label(self, node: dict) -> str:
        """Resolve a JDF node's label from row labels or its codelist."""
        code = node.get("code")
        if not code:
            return ""
        codelist_id = node.get("codelist_id") or ""
        if codelist_id == ROW_LABEL_CODELIST:
            return self.row_labels.get(code, code)
        return self.codelists.get(codelist_id, {}).get(code, code)

    def dimension_for_codelist(
        self, dataflow_id: str, codelist_id: str | None
    ) -> str | None:
        """Return the DSD dimension id that uses ``codelist_id``."""
        if not codelist_id or codelist_id == ROW_LABEL_CODELIST:
            return None
        try:
            dsd = self.get_dsd_for_dataflow(dataflow_id)
        except OpenBBError:
            return None
        for dim in dsd.get("dimensions", []):
            if dim.get("codelist_id") == codelist_id:
                return dim.get("id")
        return None

    def get_table_default_context(self, table_id: str) -> dict[str, str]:
        """Return a JDF table's default slice."""
        return dict(self.get_table(table_id).get("default_context") or {})

    def get_table_valid_context(self, table_id: str) -> dict[str, list[str]]:
        """Return a JDF table's ``{context_dim: [valid values]}``."""
        return self.get_table(table_id).get("valid_context") or {}

    def get_table_structure(self, table_id: str) -> list[dict]:
        """Return a JDF table's resolved nested tree with labels and dimensions."""
        table = self.get_table(table_id)
        dataflow_id = table.get("dataflow_id") or ""

        def _resolve(node: dict) -> dict:
            return {
                "label": self.resolve_node_label(node),
                "code": node.get("code"),
                "codelist_id": node.get("codelist_id"),
                "dimension_id": self.dimension_for_codelist(
                    dataflow_id, node.get("codelist_id")
                ),
                "children": [_resolve(child) for child in node.get("children", [])],
            }

        return [_resolve(node) for node in table.get("tree", [])]

    def get_table_dimensions(self, table_id: str) -> list[str]:
        """Return the dimension ids a JDF table's hierarchy controls."""
        out: list[str] = []

        def walk(nodes: list[dict]) -> None:
            for node in nodes:
                dim_id = node.get("dimension_id")
                if dim_id and dim_id not in out:
                    out.append(dim_id)
                walk(node.get("children", []))

        walk(self.get_table_structure(table_id))
        return out
