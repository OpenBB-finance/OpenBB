"""Tests for the served column presentation of the Congress table models."""

import json
from pathlib import Path

from fastapi import FastAPI
from openbb_platform_api.utils.widgets import build_json

import openbb_government_us
from openbb_government_us.congress.models.congress_amendments import (
    CongressAmendmentsData,
    CongressAmendmentsFetcher,
)
from openbb_government_us.congress.models.congress_bills import CongressBillsData
from openbb_government_us.congress.models.congress_committee_documents import (
    CongressCommitteeDocumentsData,
)
from openbb_government_us.congress.models.member_legislation import (
    CongressMemberLegislationData,
)

APPS_JSON = (
    Path(openbb_government_us.__file__).parent / "congress" / "assets" / "apps.json"
)

LIVE_FIELDS = {
    "uscongress_bills_congress_gov_obb": CongressBillsData,
    "uscongress_amendments_congress_gov_obb": CongressAmendmentsData,
}


def _columns_defs(widget_id: str) -> list[dict]:
    """Build the widget JSON and return one widget's columnsDefs."""
    widget = _widgets()[widget_id]

    return (widget.get("data") or {}).get("table", {}).get("columnsDefs") or []


def _widgets() -> dict[str, dict]:
    """Build the full congress widget JSON."""
    from openbb_government_us.congress import congress_router

    app = FastAPI()
    app.include_router(congress_router.router.api_router, prefix="/api/v1/uscongress")

    return build_json(app.openapi(), [])


def _column_states() -> list[tuple[str, dict]]:
    """Return every ``(widget_id, state)`` pair holding a saved columnState."""
    found: list[tuple[str, dict]] = []

    def walk(node, widget_id=None):
        if isinstance(node, dict):
            widget_id = node.get("i", widget_id)
            for key, value in node.items():
                if key == "columnState":
                    for state in value.values():
                        found.append((widget_id, state))
                else:
                    walk(value, widget_id)
        elif isinstance(node, list):
            for value in node:
                walk(value, widget_id)

    walk(json.loads(APPS_JSON.read_text(encoding="utf-8")))

    return found


class TestCongressColumnOrder:
    """The row label leads and observation dates precede record-update dates."""

    def test_bills_lead_with_id_then_action_date(self):
        """Bills lead with the bill id, then the sorted-on latest action date."""
        assert list(CongressBillsData.model_fields)[:3] == [
            "bill_id",
            "latest_action_date",
            "update_date",
        ]

    def test_amendments_lead_with_id_then_submitted_date(self):
        """Amendments lead with the id and the fully-populated submitted date."""
        assert list(CongressAmendmentsData.model_fields)[:3] == [
            "amendment_id",
            "submitted_date",
            "latest_action_date",
        ]

    def test_amendments_sparse_columns_trail_dense_ones(self):
        """The sparse description/purpose columns sit behind the dense ones."""
        order = list(CongressAmendmentsData.model_fields)
        for sparse in ("description", "purpose", "latest_action_time"):
            for dense in ("sponsor", "amended_bill", "number"):
                assert order.index(sparse) > order.index(dense)

    def test_member_legislation_leads_with_id_then_dates(self):
        """Member legislation leads with the bill id then the introduced date."""
        assert list(CongressMemberLegislationData.model_fields)[:3] == [
            "bill_id",
            "introduced_date",
            "latest_action_date",
        ]

    def test_committee_documents_lead_with_citation_not_doc_type(self):
        """Committee documents lead with the citation label, not the doc type."""
        order = list(CongressCommitteeDocumentsData.model_fields)
        assert order[:2] == ["citation", "date"]
        assert order.index("doc_type") > order.index("date")


AMENDMENT_RECORDS = [
    {
        "amendment_id": "119-samdt-1",
        "congress": 119,
        "type": "SAMDT",
        "number": "1",
        "submittedDate": "2026-01-05T04:00:00Z",
        "updateDate": "2026-07-20",
    },
    {
        "amendment_id": "119-samdt-2",
        "congress": 119,
        "type": "SAMDT",
        "number": "2",
        "submittedDate": "2026-06-11T04:00:00Z",
        "updateDate": "2026-07-01",
    },
    {
        "amendment_id": "119-samdt-3",
        "congress": 119,
        "type": "SAMDT",
        "number": "3",
        "submittedDate": "2026-03-02T04:00:00Z",
        "updateDate": "2026-07-10",
    },
]


class TestCongressRowOrder:
    """Rows are ordered by the date column the table leads with."""

    def test_amendments_sort_newest_submitted_first(self):
        """The default order is newest-first on the leading submitted date."""
        query = CongressAmendmentsFetcher.transform_query({})
        rows = CongressAmendmentsFetcher.transform_data(
            query, [dict(r) for r in AMENDMENT_RECORDS]
        )
        assert [r.number for r in rows] == ["2", "3", "1"]

    def test_amendments_sort_ascending_reverses_the_order(self):
        """An ascending sort orders the same rows oldest-submitted first."""
        query = CongressAmendmentsFetcher.transform_query({"sort_by": "asc"})
        rows = CongressAmendmentsFetcher.transform_data(
            query, [dict(r) for r in AMENDMENT_RECORDS]
        )
        assert [r.number for r in rows] == ["1", "3", "2"]

    def test_amendments_fall_back_to_update_date(self):
        """Records without a submitted date fall back to the update date."""
        records = [
            {k: v for k, v in r.items() if k != "submittedDate"}
            for r in AMENDMENT_RECORDS
        ]
        query = CongressAmendmentsFetcher.transform_query({})
        rows = CongressAmendmentsFetcher.transform_data(query, records)
        assert [r.number for r in rows] == ["1", "3", "2"]


class TestCongressPinnedRowLabels:
    """Every congress table pins a readable row label to the left."""

    def test_member_legislation_pins_bill_id(self):
        """The member legislation table pins its bill id column."""
        extra = CongressMemberLegislationData.model_fields["bill_id"].json_schema_extra
        assert extra["x-widget_config"]["pinned"] == "left"

    def test_committee_documents_pins_citation(self):
        """The committee documents table pins its citation column."""
        extra = CongressCommitteeDocumentsData.model_fields[
            "citation"
        ].json_schema_extra
        assert extra["x-widget_config"]["pinned"] == "left"

    def test_served_columns_defs_pin_the_leading_label(self):
        """The built widgets serve the pinned label as the first column."""
        for widget_id, field in (
            ("uscongress_bills_congress_gov_obb", "bill_id"),
            ("uscongress_amendments_congress_gov_obb", "amendment_id"),
            ("uscongress_member_legislation_congress_gov_obb", "bill_id"),
        ):
            columns = _columns_defs(widget_id)
            assert columns, widget_id
            assert columns[0]["field"] == field
            assert columns[0]["pinned"] == "left"

    def test_served_columns_defs_match_field_order(self):
        """Served columnsDefs follow the model field declaration order."""
        for widget_id, model in LIVE_FIELDS.items():
            columns = [c["field"] for c in _columns_defs(widget_id)]
            assert columns == list(model.model_fields)


class TestCongressSavedColumnState:
    """The apps.json saved states agree with the served columns."""

    def test_saved_states_are_discovered(self):
        """The apps.json walk finds the saved states the other tests assert on."""
        assert {w for w, _ in _column_states()} == set(LIVE_FIELDS)

    def test_no_dead_column_references(self):
        """Every saved colId exists as a field on the widget's model."""
        for widget_id, state in _column_states():
            model = LIVE_FIELDS.get(widget_id)
            assert model is not None, widget_id
            ids = (state.get("columnOrder") or {}).get("orderedColIds", [])
            hidden = (state.get("columnVisibility") or {}).get("hiddenColIds", [])
            unknown = [c for c in ids + hidden if c not in model.model_fields]
            assert not unknown, f"{widget_id}: {unknown}"

    def test_saved_order_covers_every_column(self):
        """A saved order lists all of the model's columns, leaving none to drift."""
        for widget_id, state in _column_states():
            model = LIVE_FIELDS[widget_id]
            ids = (state.get("columnOrder") or {}).get("orderedColIds", [])
            assert ids == list(model.model_fields), widget_id

    def test_saved_order_does_not_lead_with_update_date(self):
        """No saved state leads with a record-update date ahead of the row label."""
        for widget_id, state in _column_states():
            ids = (state.get("columnOrder") or {}).get("orderedColIds", [])
            assert ids[0] != "update_date", widget_id
            assert ids[0].endswith("_id"), widget_id


class TestCongressColumnHeaders:
    """Column headers are declared with the key the widget builder reads."""

    def test_amendments_serve_no_label_column_key(self):
        """`label` is a param key, never a columnDef key, so none may be served."""
        columns = _columns_defs("uscongress_amendments_congress_gov_obb")
        stray = [c["field"] for c in columns if "label" in c]
        assert not stray

    def test_amendment_custom_headers_are_served(self):
        """The amendment columns wanting a custom header serve it as headerName."""
        headers = {
            c["field"]: c["headerName"]
            for c in _columns_defs("uscongress_amendments_congress_gov_obb")
        }
        assert headers["submitted_date"] == "Submitted"
        assert headers["amendment_type"] == "Type"
        assert headers["number"] == "Amendment No."
        assert headers["amended_bill_title"] == "Bill Title"

    def test_amendment_derived_headers_are_not_redeclared(self):
        """Columns whose derived header already reads well declare no override."""
        for field in ("amended_bill", "sponsor"):
            extra = CongressAmendmentsData.model_fields[field].json_schema_extra
            assert extra is None


class TestCommitteeDocumentsFeed:
    """Committee documents back the document viewer instead of their own table."""

    def test_committee_documents_serve_no_table_widget(self):
        """The endpoint is excluded; the viewer is the served committee surface."""
        widgets = _widgets()
        assert "uscongress_committee_documents_congress_gov_obb" not in widgets
        assert "uscongress_committee_document_viewer_congress_gov_obb" in widgets

    def test_document_viewer_selects_documents_without_a_package_id(self):
        """The viewer drives its file selector from the committee hierarchy."""
        widget = _widgets()["uscongress_committee_document_viewer_congress_gov_obb"]
        params = {p["paramName"] for p in widget["params"]}
        assert {
            "chamber",
            "committee",
            "subcommittee",
            "doc_type",
            "congress",
        } <= params
        assert "package_id" not in params

    def test_package_id_declares_no_group_by_render(self):
        """No column offers a groupBy the document viewer cannot consume."""
        extra = CongressCommitteeDocumentsData.model_fields[
            "package_id"
        ].json_schema_extra
        assert extra is None
