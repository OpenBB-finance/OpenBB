"""Tests for the USDA ERS SNAP policy data sets utils and model."""

import asyncio
import csv
import io
import zipfile
from io import StringIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.snap_policy_data_sets import (
    SnapPolicyDataSetsData,
    SnapPolicyDataSetsFetcher,
    SnapPolicyDataSetsQueryParams,
    _policy,
)
from openbb_government_us.usda.utils import ers_snap_policy_data_sets as snap
from openbb_government_us.usda.utils.ers_snap_policy_data_sets import (
    CSV_MEMBER,
    FIELD_TO_CSV,
    MEDIA_ZIP,
    POLICY_FIELDS,
    PRODUCT_PAGE,
    STATE_CODES,
    STATE_LABELS,
    csv_column,
    extract_csv_text,
    parse_rows,
    policy_value,
    state_options,
)

CSV_POLICY_COLUMNS = [csv_column(field) for field in POLICY_FIELDS]
CSV_HEADER = ["state_fips", "state_pc", "statename", "yearmonth"] + CSV_POLICY_COLUMNS


def make_row(state_pc: str, statename: str, yearmonth: str, **overrides) -> dict:
    """Build a full-width CSV row with policy columns defaulting to '0'."""
    row = {
        "state_fips": "0",
        "state_pc": state_pc,
        "statename": statename,
        "yearmonth": yearmonth,
    }
    for column in CSV_POLICY_COLUMNS:
        row[column] = "0"
    row.update(overrides)
    return row


SAMPLE_ROWS = [
    make_row(
        "CA",
        "California",
        "199601",
        bbce="0",
        bbce_asset="-9",
        bbce_a_amt="-9",
        bbce_inclmt="-9",
        bbce_elddisinclmt="-9",
        certearnavg="13.41084",
        certeldavg="11.96339",
        fingerprint="2",
        noncitchildfull="1",
    ),
    make_row(
        "CA",
        "California",
        "201001",
        bbce="1",
        bbce_asset="1",
        bbce_a_amt="-9",
        bbce_inclmt="130",
        certearnavg="11.90194",
        outreach="393.2917",
        oapp="2",
        vehexclall="1",
        noncitchildfull="1",
    ),
    make_row(
        "CA",
        "California",
        "202010",
        bbce="",
        bbce_asset="",
        bbce_a_amt="",
        bbce_inclmt="",
        certearnavg="",
        outreach="",
        oapp="",
        cap="0",
        ebtissuance="1",
        noncitchildfull="1",
    ),
    make_row(
        "TX",
        "Texas",
        "201901",
        bbce="1",
        bbce_asset="0",
        bbce_a_amt="5",
        bbce_a_veh="1",
        bbce_inclmt="165",
        certearn0406="0.9641814",
        certearnavg="5.977258",
        outreach="509.6838",
        vehexclamt="1",
        noncitchildfull="1",
    ),
]


def build_csv(rows: list[dict]) -> str:
    """Build CSV text from the SNAP header and full-width row dicts."""
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_HEADER)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def build_zip(csv_text: str, member: str = CSV_MEMBER) -> bytes:
    """Zip one CSV member into raw archive bytes."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member, csv_text.encode("utf-8-sig"))
    return buffer.getvalue()


SAMPLE_CSV = build_csv(SAMPLE_ROWS)
SAMPLE_ZIP = build_zip(SAMPLE_CSV)


class TestErsSnapPolicyDataSetsUtils:
    """Tests for the ers_snap_policy_data_sets utils module."""

    def test_catalog_constants(self):
        """The catalog pins the product page, media zip, and CSV member."""
        assert PRODUCT_PAGE == "data-products/snap-policy-data-sets"
        assert MEDIA_ZIP == "/media/6473/snap-policy-database.zip"
        assert CSV_MEMBER == "SNAPPolicyDatabase.csv"

    def test_state_catalog(self):
        """The state map covers the fifty states and the District of Columbia."""
        assert len(STATE_LABELS) == 51
        assert STATE_LABELS["CA"] == "California"
        assert STATE_LABELS["DC"] == "District of Columbia"
        assert tuple(STATE_LABELS) == STATE_CODES

    def test_policy_fields_catalog(self):
        """There are forty-five policy fields and twelve carry split digits."""
        assert len(POLICY_FIELDS) == 45
        assert len(FIELD_TO_CSV) == 12
        assert POLICY_FIELDS[0] == "bbce"
        assert "certearn_0103" in POLICY_FIELDS
        assert "certnonearn_1399" in POLICY_FIELDS

    def test_csv_column_maps_split_and_identity(self):
        """Split fields map to the un-split CSV header; others are identity."""
        assert csv_column("certearn_0103") == "certearn0103"
        assert csv_column("certeld_1399") == "certeld1399"
        assert csv_column("certnonearn_0712") == "certnonearn0712"
        assert csv_column("bbce_a_amt") == "bbce_a_amt"
        assert csv_column("certearnavg") == "certearnavg"

    def test_state_options(self):
        """State options are fifty-one label/value pairs."""
        options = state_options()
        assert len(options) == 51
        assert {"label": "California", "value": "CA"} in options
        assert {"label": "District of Columbia", "value": "DC"} in options

    def test_extract_csv_text(self):
        """The CSV member is extracted and decoded from the zip."""
        text = extract_csv_text(SAMPLE_ZIP)
        assert text.splitlines()[0].startswith("state_fips,state_pc,statename")
        assert "California" in text

    def test_parse_rows_filters_state(self):
        """Only the chosen state's rows are kept, keyed by field names."""
        rows = parse_rows(SAMPLE_CSV, "CA")
        assert len(rows) == 3
        assert all(row["state"] == "California" for row in rows)
        assert {row["yearmonth"] for row in rows} == {199601, 201001, 202010}
        assert all(isinstance(row["yearmonth"], int) for row in rows)
        assert "certearn_0103" in rows[0]
        assert "certearn0103" not in rows[0]

    def test_parse_rows_coerces_missing_and_not_applicable(self):
        """The -9 not-applicable BBCE sentinel and blank cells become None."""
        rows = parse_rows(SAMPLE_CSV, "CA")
        by_ym = {row["yearmonth"]: row for row in rows}
        assert by_ym[199601]["bbce_asset"] is None
        assert by_ym[199601]["bbce_a_amt"] is None
        assert by_ym[199601]["bbce"] == "0"
        assert by_ym[202010]["bbce"] is None
        assert by_ym[202010]["outreach"] is None
        assert by_ym[201001]["outreach"] == "393.2917"
        assert by_ym[201001]["bbce_asset"] == "1"

    def test_policy_value_scopes_sentinel_to_bbce_fields(self):
        """policy_value blanks -9 only on BBCE fields and keeps -8 and -7."""
        assert policy_value("bbce_asset", "-9") is None
        assert policy_value("bbce_elddisinclmt", "-9") is None
        assert policy_value("bbce_elddisinclmt", "-8") == "-8"
        assert policy_value("bbce_elddisinclmt", "-7") == "-7"
        assert policy_value("outreach", "-9") == "-9"
        assert policy_value("bbce_asset", "  ") is None
        assert policy_value("bbce_asset", None) is None
        assert policy_value("bbce_inclmt", " 130 ") == "130"

    def test_parse_rows_other_state(self):
        """A different state's slice keeps only that state's rows."""
        rows = parse_rows(SAMPLE_CSV, "TX")
        assert len(rows) == 1
        assert rows[0]["state"] == "Texas"
        assert rows[0]["bbce_a_amt"] == "5"
        assert rows[0]["certearn_0406"] == "0.9641814"

    def test_afetch_dataset(self, monkeypatch):
        """afetch_dataset fetches the zip and decodes the CSV member."""

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            assert media_path == MEDIA_ZIP
            assert product == PRODUCT_PAGE
            return SAMPLE_ZIP

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        text = asyncio.run(snap.afetch_dataset())
        assert "California" in text

    def test_afetch_state(self, monkeypatch):
        """afetch_state parses only the requested state's rows."""

        async def fake_dataset():
            return SAMPLE_CSV

        monkeypatch.setattr(snap, "afetch_dataset", fake_dataset)
        rows = asyncio.run(snap.afetch_state("TX"))
        assert len(rows) == 1
        assert rows[0]["state"] == "Texas"


class TestSnapPolicyDataSets:
    """Tests for the SnapPolicyDataSets model."""

    def test_policy_helper(self):
        """The policy helper builds a number-typed column config."""
        config = _policy("Uses BBCE")["x-widget_config"]
        assert config["headerName"] == "Uses BBCE"
        assert config["cellDataType"] == "number"

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = SnapPolicyDataSetsFetcher.transform_query(
            {"state": "TX", "start_year": 2019, "end_year": 2020}
        )
        assert isinstance(query, SnapPolicyDataSetsQueryParams)
        assert query.state == "TX"
        assert query.start_year == 2019
        assert query.end_year == 2020

    def test_state_defaults_and_normalizes(self):
        """State defaults to CA, uppercases, and takes the first of a list."""
        assert SnapPolicyDataSetsQueryParams().state == "CA"
        assert SnapPolicyDataSetsQueryParams(state="").state == "CA"
        assert SnapPolicyDataSetsQueryParams(state="tx").state == "TX"
        assert SnapPolicyDataSetsQueryParams(state=["ny"]).state == "NY"

    def test_unknown_state_raises(self):
        """An unknown state code raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid state: ZZ"):
            SnapPolicyDataSetsQueryParams(state="ZZ")

    def test_aextract_data_forwards_state(self, monkeypatch):
        """aextract_data forwards the state to afetch_state."""
        calls = []

        async def fake_afetch_state(state):
            calls.append(state)
            return parse_rows(SAMPLE_CSV, state)

        monkeypatch.setattr(snap, "afetch_state", fake_afetch_state)
        query = SnapPolicyDataSetsFetcher.transform_query({"state": "CA"})
        records = asyncio.run(SnapPolicyDataSetsFetcher.aextract_data(query, None))
        assert calls == ["CA"]
        assert all(record["state"] == "California" for record in records)

    def test_transform_data_builds_month_rows(self):
        """Each record becomes one row keyed by a first-of-month date."""
        records = parse_rows(SAMPLE_CSV, "CA")
        query = SnapPolicyDataSetsFetcher.transform_query({"state": "CA"})
        data = SnapPolicyDataSetsFetcher.transform_data(query, records)
        assert len(data) == 3
        dumped = data[0].model_dump(by_alias=True)
        assert dumped["date"].isoformat() == "2020-10-01"
        assert dumped["state"] == "California"

    def test_transform_data_chronological_newest_first(self):
        """Rows are emitted newest-first regardless of input order."""
        records = parse_rows(SAMPLE_CSV, "CA")
        query = SnapPolicyDataSetsFetcher.transform_query({"state": "CA"})
        data = SnapPolicyDataSetsFetcher.transform_data(query, records)
        dates = [row.model_dump(by_alias=True)["date"].isoformat() for row in data]
        assert dates == ["2020-10-01", "2010-01-01", "1996-01-01"]

    def test_transform_data_coerces_not_applicable_to_none(self):
        """The -9 not-applicable BBCE sentinel is null in the validated rows."""
        records = parse_rows(SAMPLE_CSV, "CA")
        query = SnapPolicyDataSetsFetcher.transform_query({"state": "CA"})
        data = SnapPolicyDataSetsFetcher.transform_data(query, records)
        first = next(
            row.model_dump(by_alias=True)
            for row in data
            if row.model_dump(by_alias=True)["date"].isoformat() == "1996-01-01"
        )
        assert first["bbce"] == 0.0
        assert first["bbce_asset"] is None
        assert first["bbce_a_amt"] is None
        assert first["bbce_inclmt"] is None

    def test_transform_data_blank_to_none(self):
        """Blank cells are coerced to None by the null-token mixin."""
        records = parse_rows(SAMPLE_CSV, "CA")
        query = SnapPolicyDataSetsFetcher.transform_query({"state": "CA"})
        data = SnapPolicyDataSetsFetcher.transform_data(query, records)
        gap = next(
            row.model_dump(by_alias=True)
            for row in data
            if row.model_dump(by_alias=True)["date"].isoformat() == "2020-10-01"
        )
        assert gap["bbce"] is None
        assert gap["outreach"] is None
        assert gap["certearnavg"] is None
        assert gap["ebtissuance"] == 1.0

    def test_transform_data_filters_years(self):
        """start_year and end_year select which months appear."""
        records = parse_rows(SAMPLE_CSV, "CA")
        query = SnapPolicyDataSetsFetcher.transform_query(
            {"state": "CA", "start_year": 2010, "end_year": 2010}
        )
        data = SnapPolicyDataSetsFetcher.transform_data(query, records)
        assert len(data) == 1
        assert data[0].model_dump(by_alias=True)["date"].isoformat() == "2010-01-01"

    def test_transform_data_empty_raises(self):
        """No records surviving the filters raises EmptyDataError."""
        records = parse_rows(SAMPLE_CSV, "CA")
        query = SnapPolicyDataSetsFetcher.transform_query(
            {"state": "CA", "start_year": 2100}
        )
        with pytest.raises(EmptyDataError, match="No records match"):
            SnapPolicyDataSetsFetcher.transform_data(query, records)

    def test_split_recert_fields_serialize_split(self):
        """The digit-suffixed recert fields serialize with a split alias."""
        records = parse_rows(SAMPLE_CSV, "TX")
        query = SnapPolicyDataSetsFetcher.transform_query({"state": "TX"})
        data = SnapPolicyDataSetsFetcher.transform_data(query, records)
        dumped = data[0].model_dump(by_alias=True)
        assert dumped["certearn_0406"] == 0.9641814
        assert "certearn0406" not in dumped

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served row key."""
        records = parse_rows(SAMPLE_CSV, "CA")
        query = SnapPolicyDataSetsFetcher.transform_query({"state": "CA"})
        data = SnapPolicyDataSetsFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        schema = SnapPolicyDataSetsData.model_json_schema(
            by_alias=True, mode="serialization"
        )
        column_fields = {to_snake(key) for key in schema["properties"]}
        assert column_fields, "no column definitions generated"
        assert served == column_fields
        assert len(served) == 47

    def test_widget_config_metadata(self):
        """The whole-widget config carries the ERS category and source."""
        config = SnapPolicyDataSetsData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]
