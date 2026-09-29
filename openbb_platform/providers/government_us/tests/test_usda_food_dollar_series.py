"""Tests for the USDA ERS food dollar series utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import to_snake_case

from openbb_government_us.usda.models.food_dollar_series import (
    FoodDollarSeriesData,
    FoodDollarSeriesFetcher,
    FoodDollarSeriesQueryParams,
)
from openbb_government_us.usda.utils import ers_food_dollar_series
from openbb_government_us.usda.utils.ers_food_dollar_series import (
    COMPONENT_COLUMNS,
    COMPONENT_LABELS,
    FOOD_DOLLAR_FILES,
    SERIES_COMPONENTS,
    TABLE_NAMES,
    build_url,
    media_path,
    parse_rows,
    to_float,
)

NOMINAL_CSV = (
    "Table_num,Table_name,Category_num,Category_desc,Year,Units,"
    "Salary_and_benefits,Property_income,Output_taxes,Imports,Total\n"
    "1,Food dollar,1,Total,2022,Cents per Domestic Food Dollar,50,30,10,10,100\n"
    "1,Food dollar,3,Farm production,2022,Cents per Domestic Food Dollar,3,4,1,1,9\n"
    "1,Food dollar,3,Farm production,1994,Cents per Domestic Food Dollar,"
    "Not available,Not available,Not available,1,9\n"
    "1,Food dollar,16,Farm share,2022,Cents per Domestic Food Dollar,"
    "Not available,Not available,Not available,Not available,17.5\n"
    "1,Food dollar,3,Farm production,2022,million dollars,100,200,50,50,400\n"
)

REAL_CSV = (
    "Table_num,Table_name,Category_num,Category_desc,Year,Units,"
    "Value_added,Imports,Total\n"
    "1,Food dollar,3,Farm production,2013,million 2017 dollars,83865.2,100,83965.2\n"
    "1,Food dollar,3,Farm production,1993,million 2017 dollars,,90,90\n"
    "1,Food dollar,14,Total food dollar,2013,million 2017 dollars,,50,116.7\n"
)


def make_nominal(**overrides) -> dict:
    """Build a parsed nominal record with optional field overrides."""
    record = {
        "table_num": 1,
        "category_num": 3,
        "industry_group": "Farm production",
        "year": 2022,
        "units": "Cents per Domestic Food Dollar",
        "Salary_and_benefits": 3.0,
        "Property_income": 4.0,
        "Output_taxes": 1.0,
        "Imports": 1.0,
        "Total": 9.0,
    }
    record.update(overrides)
    return record


def make_real(**overrides) -> dict:
    """Build a parsed real record with optional field overrides."""
    record = {
        "table_num": 1,
        "category_num": 3,
        "industry_group": "Farm production",
        "year": 2013,
        "units": "million 2017 dollars",
        "Value_added": 83865.2,
        "Imports": 100.0,
        "Total": 83965.2,
    }
    record.update(overrides)
    return record


class TestErsFoodDollarSeriesUtils:
    """Tests for the ers_food_dollar_series utils module."""

    def test_catalog_contents(self):
        """The catalog holds the nominal and real files with their scopes."""
        assert set(FOOD_DOLLAR_FILES) == {"nominal", "real"}
        assert FOOD_DOLLAR_FILES["nominal"]["media_id"] == 7055
        assert FOOD_DOLLAR_FILES["real"]["media_id"] == 7057
        assert FOOD_DOLLAR_FILES["nominal"]["tables"] == list(range(1, 23))
        assert FOOD_DOLLAR_FILES["real"]["tables"] == list(range(1, 7))
        assert FOOD_DOLLAR_FILES["nominal"]["value_columns"][-1] == "Total"
        assert FOOD_DOLLAR_FILES["real"]["value_columns"] == [
            "Value_added",
            "Imports",
            "Total",
        ]

    def test_units_labels(self):
        """Each series maps share and level to its published unit strings."""
        assert FOOD_DOLLAR_FILES["nominal"]["units"] == {
            "share": "Cents per Domestic Food Dollar",
            "level": "million dollars",
        }
        assert FOOD_DOLLAR_FILES["real"]["units"] == {
            "share": "Cents per Domestic Real Food Dollar",
            "level": "million 2017 dollars",
        }

    def test_table_names(self):
        """The table catalog names all 22 nominal variants."""
        assert len(TABLE_NAMES) == 22
        assert TABLE_NAMES[1] == "Food dollar"
        assert TABLE_NAMES[7] == "Food at home: Cereals"
        assert TABLE_NAMES[22] == "Home food and beverage: Alcoholic beverages"

    def test_component_maps(self):
        """Component keys map to source columns and display labels."""
        assert COMPONENT_COLUMNS["total"] == "Total"
        assert COMPONENT_COLUMNS["salary_and_benefits"] == "Salary_and_benefits"
        assert COMPONENT_COLUMNS["value_added"] == "Value_added"
        assert COMPONENT_LABELS["output_taxes"] == "Output taxes"
        assert set(COMPONENT_LABELS) == set(COMPONENT_COLUMNS)

    def test_series_components(self):
        """Each series lists only the components it publishes."""
        assert SERIES_COMPONENTS["nominal"] == [
            "total",
            "salary_and_benefits",
            "property_income",
            "output_taxes",
            "imports",
        ]
        assert SERIES_COMPONENTS["real"] == ["total", "value_added", "imports"]

    def test_media_path(self):
        """media_path builds the series' media path."""
        assert media_path("nominal") == (
            "/media/7055/food-dollar-nominal-data-2011-model-1993-2023.csv"
        )
        assert media_path("real") == (
            "/media/7057/food-dollar-real-data-2011-model-1993-2023.csv"
        )

    def test_build_url(self):
        """URLs follow the /media/{media_id}/{slug}.csv pattern."""
        assert build_url("nominal") == (
            "https://www.ers.usda.gov/media/7055/"
            "food-dollar-nominal-data-2011-model-1993-2023.csv"
        )

    def test_to_float(self):
        """Null tokens and blanks coerce to None; numbers parse to float."""
        assert to_float("3.9") == 3.9
        assert to_float("Not available") is None
        assert to_float("") is None
        assert to_float("  ") is None
        assert to_float(None) is None

    def test_parse_rows_nominal(self):
        """Nominal rows parse to typed records with float-or-None values."""
        rows = parse_rows(NOMINAL_CSV, "nominal")
        assert len(rows) == 5
        assert rows[0] == {
            "table_num": 1,
            "category_num": 1,
            "industry_group": "Total",
            "year": 2022,
            "units": "Cents per Domestic Food Dollar",
            "Salary_and_benefits": 50.0,
            "Property_income": 30.0,
            "Output_taxes": 10.0,
            "Imports": 10.0,
            "Total": 100.0,
        }
        assert rows[2]["Salary_and_benefits"] is None
        assert rows[2]["Imports"] == 1.0
        assert rows[3]["Total"] == 17.5
        assert all(isinstance(row["year"], int) for row in rows)

    def test_parse_rows_real(self):
        """Real rows parse with the value-added columns and empty-cell nulls."""
        rows = parse_rows(REAL_CSV, "real")
        assert len(rows) == 3
        assert set(rows[0]) == {
            "table_num",
            "category_num",
            "industry_group",
            "year",
            "units",
            "Value_added",
            "Imports",
            "Total",
        }
        assert rows[0]["Value_added"] == 83865.2
        assert rows[1]["Value_added"] is None
        assert rows[2]["Value_added"] is None

    def test_afetch_series(self, monkeypatch):
        """afetch_series fetches through the ERS cache client and parses."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return NOMINAL_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        rows = asyncio.run(ers_food_dollar_series.afetch_series("nominal"))
        assert calls == [
            (
                "/media/7055/food-dollar-nominal-data-2011-model-1993-2023.csv",
                ers_food_dollar_series.PRODUCT_PAGE,
            )
        ]
        assert len(rows) == 5
        assert rows[0]["industry_group"] == "Total"


class TestFoodDollarSeries:
    """Tests for the FoodDollarSeries model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = FoodDollarSeriesFetcher.transform_query(
            {"series": "real", "units": "level", "component": "value_added", "table": 6}
        )
        assert isinstance(query, FoodDollarSeriesQueryParams)
        assert query.series == "real"
        assert query.units == "level"
        assert query.component == "value_added"
        assert query.table == 6

    def test_defaults(self):
        """The params default to the fully-populated nominal share slice."""
        query = FoodDollarSeriesQueryParams()
        assert query.series == "nominal"
        assert query.units == "share"
        assert query.component == "total"
        assert query.table == 1
        assert query.start_year is None
        assert query.end_year is None

    def test_series_blank_list_and_case(self):
        """Series normalizes blanks to nominal, lists, and casing."""
        assert FoodDollarSeriesQueryParams(series="").series == "nominal"
        assert FoodDollarSeriesQueryParams(series=["real"]).series == "real"
        assert FoodDollarSeriesQueryParams(series="NOMINAL").series == "nominal"

    def test_units_blank_and_list(self):
        """Units normalizes blanks to share and takes the first of a list."""
        assert FoodDollarSeriesQueryParams(units="").units == "share"
        assert FoodDollarSeriesQueryParams(units=["level"]).units == "level"

    def test_component_blank_list_and_case(self):
        """Component normalizes blanks to total, lists, and casing."""
        assert FoodDollarSeriesQueryParams(component="").component == "total"
        assert FoodDollarSeriesQueryParams(component=["Imports"]).component == "imports"

    def test_table_blank_list_and_int(self):
        """Table normalizes None and blanks to 1, lists, and numeric strings."""
        assert FoodDollarSeriesQueryParams(table=None).table == 1
        assert FoodDollarSeriesQueryParams(table="").table == 1
        assert FoodDollarSeriesQueryParams(table=["7"]).table == 7
        assert FoodDollarSeriesQueryParams(table="5").table == 5

    def test_table_non_numeric_raises(self):
        """A non-numeric table raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            FoodDollarSeriesQueryParams(table="bogus")

    def test_invalid_component_for_series_raises(self):
        """A component outside the series' set raises OpenBBError."""
        with pytest.raises(
            OpenBBError, match="Invalid component 'value_added' for series 'nominal'"
        ):
            FoodDollarSeriesQueryParams(series="nominal", component="value_added")

    def test_invalid_table_for_series_raises(self):
        """A table outside the series' range raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table 10 for series 'real'"):
            FoodDollarSeriesQueryParams(series="real", table=10)

    def test_valid_real_scope(self):
        """A real value-added request within scope validates cleanly."""
        query = FoodDollarSeriesQueryParams(
            series="real", component="value_added", table=6
        )
        assert query.component == "value_added"
        assert query.table == 6

    def test_aextract_fetches_selected_series(self, monkeypatch):
        """aextract_data fetches only the selected series' CSV."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return REAL_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        query = FoodDollarSeriesFetcher.transform_query({"series": "real"})
        records = asyncio.run(FoodDollarSeriesFetcher.aextract_data(query, None))
        assert calls == [
            (
                "/media/7057/food-dollar-real-data-2011-model-1993-2023.csv",
                ers_food_dollar_series.PRODUCT_PAGE,
            )
        ]
        assert len(records) == 3

    def test_transform_data_pivots_years_into_columns(self):
        """Each industry group is one row with a value column per year."""
        records = [
            make_nominal(year=2022, Total=9.0),
            make_nominal(year=2023, Total=9.1),
        ]
        query = FoodDollarSeriesFetcher.transform_query({})
        data = FoodDollarSeriesFetcher.transform_data(query, records)
        assert len(data) == 1
        dumped = data[0].model_dump(by_alias=True)
        assert dumped["2022"] == 9.0
        assert dumped["2023"] == 9.1
        assert dumped["industry_group"] == "Farm production"
        assert not any(key.startswith("_") for key in dumped)

    def test_transform_data_component_selects_column(self):
        """The component selects which source column fills the cells."""
        query = FoodDollarSeriesFetcher.transform_query({"component": "imports"})
        data = FoodDollarSeriesFetcher.transform_data(query, [make_nominal()])
        assert data[0].model_dump(by_alias=True)["2022"] == 1.0

    def test_transform_data_full_precision(self):
        """Cell values pass through at full precision, unrounded."""
        query = FoodDollarSeriesFetcher.transform_query(
            {"series": "real", "units": "level", "component": "value_added"}
        )
        data = FoodDollarSeriesFetcher.transform_data(query, [make_real()])
        assert data[0].model_dump(by_alias=True)["2013"] == 83865.2

    def test_transform_data_filters_units(self):
        """The units filter keeps only the matching unit rows."""
        records = [
            make_nominal(units="Cents per Domestic Food Dollar", Total=9.0),
            make_nominal(units="million dollars", Total=400.0),
        ]
        query = FoodDollarSeriesFetcher.transform_query({"units": "share"})
        data = FoodDollarSeriesFetcher.transform_data(query, records)
        assert len(data) == 1
        assert data[0].model_dump(by_alias=True)["2022"] == 9.0

    def test_transform_data_filters_table(self):
        """The table filter keeps only the selected table number."""
        records = [
            make_nominal(table_num=1, Total=9.0),
            make_nominal(table_num=7, category_num=1, industry_group="Total"),
        ]
        query = FoodDollarSeriesFetcher.transform_query({"table": 1})
        data = FoodDollarSeriesFetcher.transform_data(query, records)
        assert [row.industry_group for row in data] == ["Farm production"]

    def test_transform_data_filters_years(self):
        """start_year and end_year select which year columns appear."""
        records = [make_nominal(year=year) for year in (2020, 2021, 2022, 2023)]
        query = FoodDollarSeriesFetcher.transform_query(
            {"start_year": 2021, "end_year": 2022}
        )
        data = FoodDollarSeriesFetcher.transform_data(query, records)
        dumped = data[0].model_dump(by_alias=True)
        assert sorted(k for k in dumped if k.isdigit()) == ["2021", "2022"]

    def test_transform_data_drops_all_null_rows(self):
        """A row whose component is null for every year is dropped."""
        records = [
            make_nominal(category_num=3, industry_group="Farm production"),
            make_nominal(
                category_num=16,
                industry_group="Farm share",
                Salary_and_benefits=None,
            ),
        ]
        query = FoodDollarSeriesFetcher.transform_query(
            {"component": "salary_and_benefits"}
        )
        data = FoodDollarSeriesFetcher.transform_data(query, records)
        assert [row.industry_group for row in data] == ["Farm production"]

    def test_transform_data_orders_by_category(self):
        """Rows sort by category number regardless of input order."""
        records = [
            make_nominal(category_num=16, industry_group="Farm share", Total=17.5),
            make_nominal(category_num=3, industry_group="Farm production", Total=9.0),
            make_nominal(category_num=1, industry_group="Total", Total=100.0),
        ]
        query = FoodDollarSeriesFetcher.transform_query({})
        data = FoodDollarSeriesFetcher.transform_data(query, records)
        assert [row.industry_group for row in data] == [
            "Total",
            "Farm production",
            "Farm share",
        ]

    def test_transform_data_year_columns_chronological(self):
        """Year columns emit in chronological order even from shuffled input."""
        records = [
            make_nominal(year=2023, Total=9.1),
            make_nominal(year=2021, Total=8.9),
            make_nominal(year=2022, Total=9.0),
        ]
        query = FoodDollarSeriesFetcher.transform_query({})
        data = FoodDollarSeriesFetcher.transform_data(query, records)
        dumped = data[0].model_dump(by_alias=True)
        year_keys = [key for key in dumped if key.isdigit()]
        assert year_keys == ["2021", "2022", "2023"]

    def test_transform_data_empty_raises(self):
        """No records surviving the filters raises EmptyDataError."""
        query = FoodDollarSeriesFetcher.transform_query({"start_year": 3000})
        with pytest.raises(EmptyDataError, match="No records match"):
            FoodDollarSeriesFetcher.transform_data(query, [make_nominal()])

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column field binds to a served row key."""
        query = FoodDollarSeriesFetcher.transform_query({})
        data = FoodDollarSeriesFetcher.transform_data(
            query,
            [make_nominal(year=2022, Total=9.0), make_nominal(year=2023, Total=9.1)],
        )
        served: set = set()
        for row in data:
            served.update(row.model_dump(by_alias=True))
        schema = FoodDollarSeriesData.model_json_schema(mode="serialization")
        declared = [
            to_snake_case(key)
            for key, prop in schema["properties"].items()
            if not prop.get("x-widget_config", {}).get("exclude")
        ]
        assert declared == ["industry_group"]
        assert all(field in served for field in declared)
        assert all(to_snake_case(key) == key for key in served)

    def test_widget_config_metadata(self):
        """The whole-widget config carries the catalog placement."""
        config = FoodDollarSeriesData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.name"] == "USDA ERS Food Dollar Series"
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]
