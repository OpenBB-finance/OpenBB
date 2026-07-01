"""ECB presentation tables sourced from the data-portal publications."""

from __future__ import annotations

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_ecb.utils.metadata._typing import MetadataBase


class TableMixin(MetadataBase):
    """List and resolve ECB data-portal presentation tables."""

    def _table_label(self, table: dict) -> str:
        """Build a readable dropdown label: ``Category — Title``."""
        title = table.get("title") or table.get("id") or ""
        category = table.get("category") or ""
        return f"{category} — {title}" if category else title

    def list_tables(self) -> list[dict]:
        """Return ``[{value, label, title, category, subcategory}]`` per table."""
        out = [
            {
                "value": table_id,
                "label": self._table_label(table),
                "title": table.get("title") or table_id,
                "category": table.get("category") or "",
                "subcategory": table.get("subcategory") or "",
            }
            for table_id, table in self.presentation_tables.items()
        ]
        return sorted(out, key=lambda t: (t["category"], t["title"]))

    def list_tables_for_dataflow(self, dataflow_id: str) -> list[dict]:
        """Return the presentation tables that publish a series from ``dataflow_id``."""
        ids = {
            table_id
            for table_id, table in self.presentation_tables.items()
            if any(row.get("flow") == dataflow_id for row in table.get("rows", []))
        }
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
        """Return the table's ordered ``[{flow, key}]`` published series rows."""
        return self.get_table(table_id).get("rows") or []
