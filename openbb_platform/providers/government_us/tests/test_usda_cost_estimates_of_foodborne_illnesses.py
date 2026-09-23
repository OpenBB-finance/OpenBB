"""Tests for the USDA ERS Cost Estimates of Foodborne Illnesses utils and model."""

import asyncio
import csv
from io import StringIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.cost_estimates_of_foodborne_illnesses import (
    DEFAULT_TABLE,
    CostEstimatesOfFoodborneIllnessesData,
    CostEstimatesOfFoodborneIllnessesFetcher,
    CostEstimatesOfFoodborneIllnessesQueryParams,
)
from openbb_government_us.usda.utils import ers_cost_estimates_of_foodborne_illnesses
from openbb_government_us.usda.utils.ers_cost_estimates_of_foodborne_illnesses import (
    COST_ESTIMATES_TABLES,
    PRODUCT_PAGE,
    coerce_value,
    parse_table,
)

CASES_HEADER = [
    "Table name",
    "Pathogen classification",
    "Pathogen",
    "Mean number of cases",
    "Mean total cost (millions)",
    " Mean per-case cost",
    "Note",
    "Source",
]

HEALTH_HEADER = [
    "Table name",
    "Pathogen classification",
    "Pathogen",
    "No physician's visit mean",
    "No physician's visit CrI",
    "Physician's visit only mean",
    "Physician's visit only CrI",
    "Hospitalized, recovered",
    "Hospitalized, recovered Crl",
    "Hospitalized, died",
    "Hospitalized, died Crl",
    "Chronic outcomes",
    "Chronic outcomes Crl",
    "Total",
    "Total Crl",
    "Note",
    "Source",
]

CASES_TABLE_NAME = (
    "Cases, total cost, and per-case cost, by pathogen (2023 U.S. dollars)"
)
HEALTH_TABLE_NAME = (
    "Mean cost for specific health outcomes, by pathogen (2023 U.S. dollars, millions)"
)


def _make_csv(header, rows):
    """Serialize a header and its rows to CSV text."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


CASES_CSV = _make_csv(
    CASES_HEADER,
    [
        [
            CASES_TABLE_NAME,
            "Bacteria",
            "Bacillus cereus ",
            "63400",
            "12.4",
            "195.5835962",
            "NOTE BLOB",
            "SOURCE BLOB",
        ],
        [
            CASES_TABLE_NAME,
            "Bacteria",
            "Campylobacter spp. ",
            "845024",
            "11327.3",
            "13404.70803",
            "NOTE BLOB",
            "SOURCE BLOB",
        ],
        [
            CASES_TABLE_NAME,
            "All pathogens",
            "Total",
            "47780837",
            "74716.1",
            "1563.725223",
            "NOTE BLOB",
            "SOURCE BLOB",
        ],
        [
            CASES_TABLE_NAME,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
    ],
)

HEALTH_CSV = _make_csv(
    HEALTH_HEADER,
    [
        [
            HEALTH_TABLE_NAME,
            "Bacteria",
            "Bacillus cereus ",
            "1.7",
            "0.3-4.4",
            "10.4",
            "0.7-33.1",
            "0.3",
            "0-1.5",
            "0",
            "0-0",
            "",
            "",
            "12.4",
            "1.0-39.0",
            "NOTE BLOB",
            "SOURCE BLOB",
        ],
        [
            HEALTH_TABLE_NAME,
            "Bacteria",
            "Campylobacter spp. ",
            "72.4",
            "18.5-165.5",
            "174.5",
            "26.3-478.2",
            "144.6",
            "68.3-250.2",
            "994.5",
            "504-1,616.9",
            "9941.3",
            "3,665.1-19,067.7",
            "11327.3",
            "4,282.2-21,578.5",
            "NOTE BLOB",
            "SOURCE BLOB",
        ],
        [
            HEALTH_TABLE_NAME,
            "Bacteria",
            "S. enterica serotype Typhi",
            "0.1",
            " 0-0.4",
            "0.6",
            "0-2.5",
            "1.8",
            "0-8.3",
            "0",
            "0-0",
            "",
            "",
            "2.5",
            "0-11.3",
            "NOTE BLOB",
            "SOURCE BLOB",
        ],
        [
            HEALTH_TABLE_NAME,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
    ],
)

BLANK_CLASSIFICATION_CSV = _make_csv(
    CASES_HEADER,
    [
        [
            CASES_TABLE_NAME,
            "",
            "Orphan pathogen",
            "10",
            "1.0",
            "100.0",
            "NOTE BLOB",
            "SOURCE BLOB",
        ],
    ],
)


class TestErsCostEstimatesOfFoodborneIllnessesUtils:
    """Tests for the ers_cost_estimates_of_foodborne_illnesses utils module."""

    def test_catalog_contents(self):
        """The catalog holds the two primary tables with media paths and labels."""
        assert set(COST_ESTIMATES_TABLES) == {"cases_and_cost", "health_outcome_cost"}
        assert DEFAULT_TABLE in COST_ESTIMATES_TABLES
        for config in COST_ESTIMATES_TABLES.values():
            assert config["media_path"].startswith("/media/")
            assert config["media_path"].endswith(".csv")
            assert config["label"]
            assert isinstance(config["value_columns"], tuple)
            assert config["value_columns"]
            for column in config["value_columns"]:
                assert column["source"]
                assert column["label"]
                assert column["kind"] in {"int", "float", "text"}

    def test_coerce_value_int(self):
        """An integer-kind cell coerces to an int."""
        assert coerce_value("63400", "int") == 63400
        assert isinstance(coerce_value("63400", "int"), int)

    def test_coerce_value_float(self):
        """A float-kind cell keeps full source precision."""
        assert coerce_value("195.5835962", "float") == 195.5835962

    def test_coerce_value_text_strips(self):
        """A text-kind cell is stripped but keeps its thousands-commas."""
        assert coerce_value(" 4,282.2-21,578.5 ", "text") == "4,282.2-21,578.5"

    def test_coerce_value_empty_none(self):
        """An empty cell coerces to None regardless of kind."""
        assert coerce_value("", "float") is None
        assert coerce_value("   ", "text") is None
        assert coerce_value(None, "int") is None

    def test_coerce_value_placeholder_none(self):
        """A placeholder token coerces to None."""
        assert coerce_value("--", "float") is None
        assert coerce_value("n/a", "text") is None

    def test_parse_cases_table(self):
        """The cases table parses to one record per pathogen, dropping blanks."""
        records = parse_table(CASES_CSV, "cases_and_cost")
        assert len(records) == 3
        first = records[0]
        assert first["pathogen_classification"] == "Bacteria"
        assert first["pathogen"] == "Bacillus cereus"
        assert first["Mean number of cases"] == 63400
        assert first["Mean total cost (2023 $ millions)"] == 12.4
        assert first["Mean per-case cost (2023 $)"] == 195.5835962
        assert "Note" not in first
        assert "Source" not in first
        assert "Table name" not in first
        assert records[-1]["pathogen"] == "Total"

    def test_parse_health_table(self):
        """The health-outcome table parses the six means and their CrI columns."""
        records = parse_table(HEALTH_CSV, "health_outcome_cost")
        assert len(records) == 3
        campy = records[1]
        assert campy["pathogen"] == "Campylobacter spp."
        assert campy["No physician's visit"] == 72.4
        assert campy["Hospitalized, died (CrI)"] == "504-1,616.9"
        assert campy["Total (CrI)"] == "4,282.2-21,578.5"
        assert campy["Chronic outcomes"] == 9941.3

    def test_parse_health_blank_cells_none(self):
        """Blank outcome cells parse to None via coercion."""
        records = parse_table(HEALTH_CSV, "health_outcome_cost")
        first = records[0]
        assert first["Chronic outcomes"] is None
        assert first["Chronic outcomes (CrI)"] is None

    def test_parse_health_leading_space_cri(self):
        """A leading-space credibility interval is stripped."""
        records = parse_table(HEALTH_CSV, "health_outcome_cost")
        typhi = records[2]
        assert typhi["No physician's visit (CrI)"] == "0-0.4"

    def test_parse_strips_pathogen_whitespace(self):
        """Trailing whitespace on a pathogen name is stripped."""
        records = parse_table(CASES_CSV, "cases_and_cost")
        assert records[1]["pathogen"] == "Campylobacter spp."

    def test_parse_blank_classification_none(self):
        """A blank pathogen classification parses to None."""
        records = parse_table(BLANK_CLASSIFICATION_CSV, "cases_and_cost")
        assert len(records) == 1
        assert records[0]["pathogen_classification"] is None
        assert records[0]["pathogen"] == "Orphan pathogen"

    def test_parse_carries_temp_keys(self):
        """Records carry the temporary order and table keys for later stages."""
        records = parse_table(CASES_CSV, "cases_and_cost")
        assert records[0]["_order"] == 0
        assert records[0]["_table"] == "cases_and_cost"

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches the table's CSV through the cache and parses it."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return CASES_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            ers_cost_estimates_of_foodborne_illnesses.afetch_table("cases_and_cost")
        )
        assert calls == [
            (COST_ESTIMATES_TABLES["cases_and_cost"]["media_path"], PRODUCT_PAGE)
        ]
        assert len(records) == 3


class TestCostEstimatesOfFoodborneIllnesses:
    """Tests for the CostEstimatesOfFoodborneIllnesses model."""

    def test_transform_query_default_table(self):
        """transform_query defaults the table to the cases-and-cost table."""
        query = CostEstimatesOfFoodborneIllnessesFetcher.transform_query({})
        assert isinstance(query, CostEstimatesOfFoodborneIllnessesQueryParams)
        assert query.table == DEFAULT_TABLE

    def test_table_blank_returns_default(self):
        """A blank or None table normalizes to the default table."""
        assert (
            CostEstimatesOfFoodborneIllnessesQueryParams(table=None).table
            == DEFAULT_TABLE
        )
        assert (
            CostEstimatesOfFoodborneIllnessesQueryParams(table="").table
            == DEFAULT_TABLE
        )

    def test_table_strips_whitespace(self):
        """A padded table value is stripped before validation."""
        query = CostEstimatesOfFoodborneIllnessesQueryParams(
            table="  health_outcome_cost  "
        )
        assert query.table == "health_outcome_cost"

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            CostEstimatesOfFoodborneIllnessesQueryParams(table="bogus")

    def test_non_string_table_raises(self):
        """A non-string, non-empty table value raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table"):
            CostEstimatesOfFoodborneIllnessesQueryParams(table=123)

    def test_aextract_data_fetches_selected_table(self, monkeypatch):
        """aextract_data fetches only the selected table's rows."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"_order": 0, "_table": table}]

        monkeypatch.setattr(
            ers_cost_estimates_of_foodborne_illnesses,
            "afetch_table",
            fake_afetch_table,
        )
        query = CostEstimatesOfFoodborneIllnessesFetcher.transform_query(
            {"table": "health_outcome_cost"}
        )
        records = asyncio.run(
            CostEstimatesOfFoodborneIllnessesFetcher.aextract_data(query, None)
        )
        assert fetched == ["health_outcome_cost"]
        assert records == [{"_order": 0, "_table": "health_outcome_cost"}]

    def test_transform_data_emits_wide_rows(self):
        """Each pathogen becomes one wide row with its value columns."""
        records = parse_table(CASES_CSV, "cases_and_cost")
        query = CostEstimatesOfFoodborneIllnessesFetcher.transform_query({})
        data = CostEstimatesOfFoodborneIllnessesFetcher.transform_data(query, records)
        assert len(data) == 3
        first = data[0].model_dump()
        assert first["pathogen_classification"] == "Bacteria"
        assert first["pathogen"] == "Bacillus cereus"
        assert first["Mean number of cases"] == 63400
        assert first["Mean total cost (2023 $ millions)"] == 12.4
        assert first["Mean per-case cost (2023 $)"] == 195.5835962

    def test_transform_data_preserves_source_order(self):
        """Rows keep the source order, aggregates last."""
        records = parse_table(CASES_CSV, "cases_and_cost")
        shuffled = [records[2], records[0], records[1]]
        query = CostEstimatesOfFoodborneIllnessesFetcher.transform_query({})
        data = CostEstimatesOfFoodborneIllnessesFetcher.transform_data(query, shuffled)
        assert [row.pathogen for row in data] == [
            "Bacillus cereus",
            "Campylobacter spp.",
            "Total",
        ]

    def test_transform_data_drops_temp_keys(self):
        """Internal temp keys never leak into the validated records."""
        records = parse_table(CASES_CSV, "cases_and_cost")
        query = CostEstimatesOfFoodborneIllnessesFetcher.transform_query({})
        data = CostEstimatesOfFoodborneIllnessesFetcher.transform_data(query, records)
        dumped = data[0].model_dump()
        assert "_order" not in dumped
        assert "_table" not in dumped

    def test_transform_data_null_token_coercion(self):
        """A placeholder token in a served extra coerces to None."""
        row = {
            "_order": 0,
            "_table": "health_outcome_cost",
            "pathogen_classification": "Bacteria",
            "pathogen": "X",
            "Total (CrI)": "--",
            "Total": None,
        }
        query = CostEstimatesOfFoodborneIllnessesFetcher.transform_query({})
        data = CostEstimatesOfFoodborneIllnessesFetcher.transform_data(query, [row])
        dumped = data[0].model_dump()
        assert dumped["Total (CrI)"] is None

    def test_transform_data_health_columns(self):
        """The health table emits interleaved mean and credibility-interval columns."""
        records = parse_table(HEALTH_CSV, "health_outcome_cost")
        query = CostEstimatesOfFoodborneIllnessesFetcher.transform_query(
            {"table": "health_outcome_cost"}
        )
        data = CostEstimatesOfFoodborneIllnessesFetcher.transform_data(query, records)
        dumped = data[1].model_dump()
        assert dumped["Hospitalized, died (CrI)"] == "504-1,616.9"
        assert dumped["Total"] == 11327.3

    def test_query_params_widget_options(self):
        """The table param exposes both tables as a single-select filter."""
        config = CostEstimatesOfFoodborneIllnessesQueryParams.__json_schema_extra__[
            "table"
        ]["x-widget_config"]
        assert config["multiSelect"] is False
        assert config["multiple"] is False
        assert config["value"] == DEFAULT_TABLE
        assert len(config["options"]) == 2

    def test_widget_model_config(self):
        """The whole-widget config carries the name, category, and source."""
        config = CostEstimatesOfFoodborneIllnessesData.model_config[
            "json_schema_extra"
        ]["x-widget_config"]
        assert config["$.name"] == "USDA ERS Cost Estimates of Foodborne Illnesses"
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared field binds to a served key and dynamics are extras."""
        records = parse_table(HEALTH_CSV, "health_outcome_cost")
        query = CostEstimatesOfFoodborneIllnessesFetcher.transform_query(
            {"table": "health_outcome_cost"}
        )
        data = CostEstimatesOfFoodborneIllnessesFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        fields = CostEstimatesOfFoodborneIllnessesData.model_fields
        for name, field in fields.items():
            extra = (field.json_schema_extra or {}).get("x-widget_config", {})
            if extra.get("exclude"):
                continue
            assert name in served
        assert "_table" not in served
        assert "_order" not in served
        dynamic = served - set(fields)
        assert "No physician's visit" in dynamic
        assert "Total (CrI)" in dynamic

    def test_no_dead_constant_column(self):
        """Every served key lacking a columnDef varies across the rows."""
        records = parse_table(CASES_CSV, "cases_and_cost")
        query = CostEstimatesOfFoodborneIllnessesFetcher.transform_query({})
        data = CostEstimatesOfFoodborneIllnessesFetcher.transform_data(query, records)
        rows = [row.model_dump(by_alias=True) for row in data]
        fields = set(CostEstimatesOfFoodborneIllnessesData.model_fields)
        dynamic = set(rows[0]) - fields
        for key in dynamic:
            values = {row.get(key) for row in rows}
            assert len(values) > 1
