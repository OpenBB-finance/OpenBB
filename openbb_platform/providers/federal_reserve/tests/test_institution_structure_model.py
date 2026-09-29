"""Tests for the NIC Institution Structure fetcher model."""

from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.institution_structure import (
    FederalReserveInstitutionStructureData,
    FederalReserveInstitutionStructureFetcher,
)

_RELATIONSHIPS = [
    {
        "#ID_RSSD_PARENT": "1039502",
        "ID_RSSD_OFFSPRING": "852218",
        "RELN_LVL": "1",
        "CTRL_IND": "1",
        "EQUITY_IND": "1",
        "REG_IND": "1",
        "REASON_TERM_RELN": "0",
        "PCT_EQUITY": "100.00",
        "PCT_OTHER": "0.00",
        "PCT_EQUITY_BRACKET": "100",
        "DT_RELN_EST": "20040701",
        "DT_START": "20040701",
        "DT_END": "99991231",
    },
    {
        "#ID_RSSD_PARENT": "999",
        "ID_RSSD_OFFSPRING": "888",
        "RELN_LVL": "2",
        "CTRL_IND": "2",
        "REASON_TERM_RELN": "3",
        "DT_START": "20100101",
        "DT_END": "20120101",
    },
]
_TRANSFORMATIONS = [
    {
        "#ID_RSSD_PREDECESSOR": "111",
        "ID_RSSD_SUCCESSOR": "1039502",
        "TRNSFM_CD": "1",
        "ACCT_METHOD": "2",
        "DT_TRANS": "19911231",
    },
]


_NAMES = {
    "1039502": "JPMORGAN CHASE & CO",
    "852218": "JPMORGAN CHASE BK NA",
    "999": "PARENT CO",
    "888": "OFFSPRING CO",
    "111": "PREDECESSOR CO",
}


def _patch(monkeypatch):
    """Patch both NIC structure downloads and the RSSD name index."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ffiec.fetch_relationships",
        lambda: list(_RELATIONSHIPS),
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ffiec.fetch_transformations",
        lambda: list(_TRANSFORMATIONS),
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ffiec.rssd_names",
        lambda: dict(_NAMES),
    )


class TestExtractData:
    """Tests for ``extract_data``."""

    def test_relationships_filtered_by_rssd(self, monkeypatch):
        """Relationships referencing the RSSD are kept and keys normalized."""
        _patch(monkeypatch)
        query = FederalReserveInstitutionStructureFetcher.transform_query(
            {"kind": "relationships", "rssd_id": "1039502"}
        )
        rows = FederalReserveInstitutionStructureFetcher.extract_data(query, None)
        assert len(rows) == 1
        assert rows[0]["id_rssd_parent"] == "1039502"

    def test_transformations_kind(self, monkeypatch):
        """The transformations file is used when kind is transformations."""
        _patch(monkeypatch)
        query = FederalReserveInstitutionStructureFetcher.transform_query(
            {"kind": "transformations", "rssd_id": "1039502"}
        )
        rows = FederalReserveInstitutionStructureFetcher.extract_data(query, None)
        assert rows[0]["id_rssd_successor"] == "1039502"

    def test_no_match_raises(self, monkeypatch):
        """A non-matching RSSD raises ``EmptyDataError``."""
        _patch(monkeypatch)
        query = FederalReserveInstitutionStructureFetcher.transform_query(
            {"kind": "relationships", "rssd_id": "000"}
        )
        with pytest.raises(EmptyDataError):
            FederalReserveInstitutionStructureFetcher.extract_data(query, None)


class TestTransformData:
    """Tests for ``transform_data``."""

    def test_decodes_relationship_records(self, monkeypatch):
        """Relationship coded fields decode and dates parse to ``date``."""
        _patch(monkeypatch)
        query = FederalReserveInstitutionStructureFetcher.transform_query(
            {"kind": "relationships"}
        )
        rows = FederalReserveInstitutionStructureFetcher.extract_data(query, None)
        result = FederalReserveInstitutionStructureFetcher.transform_data(query, rows)
        assert all(
            isinstance(r, FederalReserveInstitutionStructureData) for r in result
        )
        first = result[0]
        assert first.parent_rssd_id == "1039502"
        assert first.offspring_rssd_id == "852218"
        assert first.parent_name == "JPMORGAN CHASE & CO"
        assert first.offspring_name == "JPMORGAN CHASE BK NA"
        assert first.relationship_level == "Direct"
        assert first.control_indicator == "Controlled"
        assert first.equity_indicator.startswith("Ownership/control in a BHC")
        assert first.regulated_indicator == "Regulated"
        assert first.reason_relationship_terminated.startswith("Not applicable")
        assert first.percent_equity == 100.0
        assert first.percent_equity_bracket == "100"
        assert first.relationship_established_date == date(2004, 7, 1)
        assert first.start_date == date(2004, 7, 1)
        assert first.end_date is None
        second = result[1]
        assert second.relationship_level == "Indirect"
        assert second.control_indicator == "Non-controlled"
        assert second.reason_relationship_terminated == "Offspring liquidated or merged"
        assert second.end_date == date(2012, 1, 1)

    def test_decodes_transformation_records(self, monkeypatch):
        """Transformation coded fields decode and the date parses to ``date``."""
        _patch(monkeypatch)
        query = FederalReserveInstitutionStructureFetcher.transform_query(
            {"kind": "transformations"}
        )
        rows = FederalReserveInstitutionStructureFetcher.extract_data(query, None)
        result = FederalReserveInstitutionStructureFetcher.transform_data(query, rows)
        record = result[0]
        assert record.predecessor_rssd_id == "111"
        assert record.successor_rssd_id == "1039502"
        assert record.predecessor_name == "PREDECESSOR CO"
        assert record.successor_name == "JPMORGAN CHASE & CO"
        assert record.transformation_type.startswith("Charter Discontinued")
        assert record.accounting_method == "Purchase/Acquisition"
        assert record.transformation_date == date(1991, 12, 31)

    def test_only_curated_fields_returned(self, monkeypatch):
        """No leftover raw NIC columns leak into the validated model."""
        _patch(monkeypatch)
        query = FederalReserveInstitutionStructureFetcher.transform_query(
            {"kind": "relationships"}
        )
        rows = FederalReserveInstitutionStructureFetcher.extract_data(query, None)
        result = FederalReserveInstitutionStructureFetcher.transform_data(query, rows)
        allowed = set(FederalReserveInstitutionStructureData.model_fields)
        for item in result:
            assert set(item.model_dump()) <= allowed
