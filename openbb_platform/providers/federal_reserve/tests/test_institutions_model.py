"""Tests for the FFIEC NIC Institutions fetcher model."""

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.institutions import (
    FederalReserveInstitutionsData,
    FederalReserveInstitutionsFetcher,
    FederalReserveInstitutionsQueryParams,
    _parse_nic_date,
)

_RECORDS = [
    {
        "#ID_RSSD": "1039502",
        "NM_LGL": "JPMORGAN CHASE & CO.   ",
        "NM_SHORT": "JPMORGAN CHASE & CO",
        "CITY": "NEW YORK ",
        "STATE_ABBR_NM": "NY",
        "CNTRY_NM": "UNITED STATES",
        "ENTITY_TYPE": "FHD",
        "CHTR_TYPE_CD": "500",
        "ORG_TYPE_CD": "1",
        "PRIM_FED_REG": "FRS",
        "BHC_IND": "1",
        "FHC_IND": "1",
        "DT_OPEN": "19681028",
        "DT_EXIST_CMNC": "19681028",
        "DT_START": "20251201",
        "ID_FDIC_CERT": "0",
        "ID_OCC": "0",
        "ID_LEI": "8I5DZWZKVSZI1NUHU748",
        "URL": "",
    },
    {
        "#ID_RSSD": "852218",
        "NM_LGL": "JPMORGAN CHASE BANK, NA",
        "NM_SHORT": "JPMORGAN CHASE BK NA",
        "CITY": "COLUMBUS",
        "STATE_ABBR_NM": "OH",
        "CNTRY_NM": "UNITED STATES",
        "ENTITY_TYPE": "NAT",
        "CHTR_TYPE_CD": "200",
        "ORG_TYPE_CD": "1",
        "PRIM_FED_REG": "OCC",
        "BHC_IND": "0",
        "FHC_IND": "0",
        "DT_OPEN": "0",
        "DT_EXIST_CMNC": "18240101",
        "DT_START": "20190126",
        "ID_FDIC_CERT": "628",
        "ID_OCC": "8",
    },
]


def _patch(monkeypatch):
    """Patch the FFIEC institutions download to the fixture records."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ffiec.fetch_institutions",
        lambda status="active": list(_RECORDS),
    )


class TestExtractData:
    """Tests for ``extract_data`` filtering."""

    def test_name_filter_matches_short_and_legal(self, monkeypatch):
        """A name query matches against legal and short names."""
        _patch(monkeypatch)
        query = FederalReserveInstitutionsFetcher.transform_query({"name": "jpmorgan"})
        rows = FederalReserveInstitutionsFetcher.extract_data(query, None)
        assert len(rows) == 2

    def test_rssd_filter(self, monkeypatch):
        """An RSSD filter narrows to one institution and strips padding."""
        _patch(monkeypatch)
        query = FederalReserveInstitutionsFetcher.transform_query(
            {"rssd_id": "1039502"}
        )
        rows = FederalReserveInstitutionsFetcher.extract_data(query, None)
        assert len(rows) == 1
        assert rows[0]["NM_LGL"] == "JPMORGAN CHASE & CO."

    def test_name_search_ignores_grouped_rssd(self, monkeypatch):
        """A name search ignores a supplied rssd_id (the hidden grouped selection).

        The rssd_id is a cross-widget selection, not a search filter, so it must
        not narrow a name search to the single clicked institution.
        """
        _patch(monkeypatch)
        query = FederalReserveInstitutionsFetcher.transform_query(
            {"name": "jpmorgan", "rssd_id": "1039502"}
        )
        rows = FederalReserveInstitutionsFetcher.extract_data(query, None)
        assert len(rows) == 2

    def test_no_match_raises(self, monkeypatch):
        """A non-matching query raises ``EmptyDataError``."""
        _patch(monkeypatch)
        query = FederalReserveInstitutionsFetcher.transform_query({"name": "zzz"})
        with pytest.raises(EmptyDataError):
            FederalReserveInstitutionsFetcher.extract_data(query, None)

    def test_ticker_resolves_to_parent(self, monkeypatch):
        """A ticker resolves to its parent holding company's RSSD."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.resolve_ticker_to_rssd",
            lambda t: "1039502",
        )
        query = FederalReserveInstitutionsFetcher.transform_query({"ticker": "JPM"})
        rows = FederalReserveInstitutionsFetcher.extract_data(query, None)
        assert all(r["#ID_RSSD"] == "1039502" for r in rows)

    def test_unresolvable_ticker_raises(self, monkeypatch):
        """An unresolvable ticker raises ``OpenBBError``."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.resolve_ticker_to_rssd",
            lambda t: None,
        )
        query = FederalReserveInstitutionsFetcher.transform_query({"ticker": "ZZZ"})
        with pytest.raises(OpenBBError):
            FederalReserveInstitutionsFetcher.extract_data(query, None)


class TestTransformData:
    """Tests for ``transform_data`` field mapping."""

    def test_maps_attribute_names(self, monkeypatch):
        """NIC attribute names map to friendly model fields, sorted by RSSD."""
        _patch(monkeypatch)
        query = FederalReserveInstitutionsFetcher.transform_query({"name": "jpmorgan"})
        rows = FederalReserveInstitutionsFetcher.extract_data(query, None)
        result = FederalReserveInstitutionsFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveInstitutionsData) for r in result)
        assert result[0].rssd_id == "1039502"
        assert result[0].legal_name == "JPMORGAN CHASE & CO."
        assert result[0].model_dump()["lei"] == "8I5DZWZKVSZI1NUHU748"

    def test_translates_coded_fields_to_labels(self, monkeypatch):
        """Coded NIC fields resolve to authoritative human-readable labels."""
        _patch(monkeypatch)
        query = FederalReserveInstitutionsFetcher.transform_query({"name": "jpmorgan"})
        rows = FederalReserveInstitutionsFetcher.extract_data(query, None)
        result = FederalReserveInstitutionsFetcher.transform_data(query, rows)
        holdco = next(r for r in result if r.rssd_id == "1039502")
        assert holdco.entity_type_description == "Financial Holding Company / BHC"
        assert holdco.charter_type == "Holding Company"
        assert holdco.organization_type == "Corporation (stock)"
        assert holdco.primary_federal_regulator == "FRS"
        assert holdco.is_bank_holding_company == "Yes"
        assert holdco.is_financial_holding_company == "Yes"
        assert holdco.country == "UNITED STATES"
        assert holdco.established_date == date(1968, 10, 28)
        bank = next(r for r in result if r.rssd_id == "852218")
        assert bank.entity_type_description == "National Bank"
        assert bank.charter_type == "Commercial Bank"
        assert bank.primary_federal_regulator == "OCC"
        assert bank.is_bank_holding_company == "No"
        assert bank.fdic_cert == "628"
        assert bank.occ_id == "8"

    def test_established_date_falls_back_to_existence(self, monkeypatch):
        """``established_date`` uses ``DT_EXIST_CMNC`` when ``DT_OPEN`` is a sentinel."""
        _patch(monkeypatch)
        query = FederalReserveInstitutionsFetcher.transform_query({"name": "jpmorgan"})
        rows = FederalReserveInstitutionsFetcher.extract_data(query, None)
        result = FederalReserveInstitutionsFetcher.transform_data(query, rows)
        bank = next(r for r in result if r.rssd_id == "852218")
        assert bank.established_date == date(1824, 1, 1)

    def test_only_curated_fields_returned(self, monkeypatch):
        """No leftover raw NIC columns leak into the validated model."""
        _patch(monkeypatch)
        query = FederalReserveInstitutionsFetcher.transform_query({"name": "jpmorgan"})
        rows = FederalReserveInstitutionsFetcher.extract_data(query, None)
        result = FederalReserveInstitutionsFetcher.transform_data(query, rows)
        allowed = set(FederalReserveInstitutionsData.model_fields)
        for item in result:
            assert set(item.model_dump()) <= allowed

    def test_drops_not_applicable_id_zeros(self, monkeypatch):
        """Id and URL fields equal to ``0`` or empty are dropped, not shown."""
        _patch(monkeypatch)
        query = FederalReserveInstitutionsFetcher.transform_query({"name": "jpmorgan"})
        rows = FederalReserveInstitutionsFetcher.extract_data(query, None)
        result = FederalReserveInstitutionsFetcher.transform_data(query, rows)
        holdco = next(r for r in result if r.rssd_id == "1039502")
        assert holdco.fdic_cert is None
        assert holdco.occ_id is None
        assert holdco.url is None


class TestParseNicDate:
    """Tests for the NIC date parser."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("19681028", date(1968, 10, 28)),
            ("10/28/1968 00:00:00", date(1968, 10, 28)),
            ("99991231", None),
            ("00000000", None),
            ("0", None),
            ("", None),
            (None, None),
            ("notadate", None),
            ("13/40/2020 00:00:00", None),
            ("20209999", None),
        ],
    )
    def test_parse_nic_date(self, value, expected):
        """NIC dates parse to ``date`` and sentinels/garbage to ``None``."""
        assert _parse_nic_date(value) == expected


class TestWidgetOptions:
    """Tests for the human-readable ``status`` dropdown labels."""

    def test_status_options_have_human_labels(self):
        """Every ``status`` code maps to a human label, not a bare code."""
        options = FederalReserveInstitutionsQueryParams.__json_schema_extra__["status"][
            "x-widget_config"
        ]["options"]
        assert {o["value"] for o in options} == {"active", "closed", "branches"}
        for option in options:
            assert option["label"] and option["label"] != option["value"]
