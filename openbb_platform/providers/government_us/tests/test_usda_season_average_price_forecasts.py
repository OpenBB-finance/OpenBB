"""Tests for the USDA ERS season-average price forecasts utils and model."""

import asyncio
import csv
from io import StringIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.season_average_price_forecasts import (
    SeasonAveragePriceForecastsData,
    SeasonAveragePriceForecastsFetcher,
    SeasonAveragePriceForecastsQueryParams,
)
from openbb_government_us.usda.utils import ers_season_average_price_forecasts
from openbb_government_us.usda.utils.ers_season_average_price_forecasts import (
    COMMODITIES,
    OUTPUT_FORECAST_COLUMNS,
    SEASON_AVERAGE_FILES,
    parse_output_forecast,
)

OUTPUT_FORECAST_CSV = (
    "model_forecast_date,commodity,futures_model_type,futures_exchange,"
    "marketing_year,mya_price_model_forecast,mya_price_wasde_forecast,"
    "wasde_forecast_date,actual_mya_price,effective_reference_price,price_unit\n"
    "2026-07-02, Corn ,Single contract,CBOT,2025,4.196194,4.15,2026-06-11,"
    "NA,4.423467,U.S. dollars per bushel\n"
    "2026-07-02,Corn,Single contract,CBOT,2027,4.679482,NA,NA,NA,,"
    "U.S. dollars per bushel\n"
    ",,,,,,,,,,\n"
)


def _full_row(**overrides) -> dict:
    """Build one output-forecast record spanning all 42 columns."""
    row = dict.fromkeys(OUTPUT_FORECAST_COLUMNS, "NA")
    row.update(
        {
            "model_forecast_date": "2026-07-02",
            "commodity": "Corn",
            "futures_model_type": "Single contract",
            "futures_exchange": "CBOT",
            "marketing_year": "2025",
            "mya_price_model_forecast": "4.196194",
            "price_unit": "U.S. dollars per bushel",
        }
    )
    row.update(overrides)
    return row


class TestErsSeasonAveragePriceForecastsUtils:
    """Tests for the ers_season_average_price_forecasts utils module."""

    def test_catalog_contents(self):
        """The catalog holds the two CSV media paths and the commodity set."""
        assert SEASON_AVERAGE_FILES == {
            "output_forecast": "/media/6497/output-forecast-csv-file.csv",
            "input_data": "/media/6498/input-data-csv-file.csv",
        }
        assert COMMODITIES == ("Corn", "Cotton", "Soybeans", "Wheat")
        assert len(OUTPUT_FORECAST_COLUMNS) == 42
        assert OUTPUT_FORECAST_COLUMNS[0] == "model_forecast_date"
        assert OUTPUT_FORECAST_COLUMNS[-1] == "price_unit"
        assert len(set(OUTPUT_FORECAST_COLUMNS)) == 42

    def test_parse_output_forecast_strips_and_skips_blank(self):
        """Values are whitespace-stripped and rows without commodity skipped."""
        records = parse_output_forecast(OUTPUT_FORECAST_CSV)
        assert len(records) == 2
        assert records[0]["commodity"] == "Corn"
        assert records[0]["marketing_year"] == "2025"
        assert records[0]["mya_price_model_forecast"] == "4.196194"
        assert records[1]["marketing_year"] == "2027"
        assert records[1]["mya_price_wasde_forecast"] == "NA"

    def test_afetch_output_forecast(self, monkeypatch):
        """afetch_output_forecast fetches the output-forecast media path."""
        calls = []

        async def fake_afetch_ers_file(path, product=None, ttl=None):
            calls.append((path, product))
            return OUTPUT_FORECAST_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            ers_season_average_price_forecasts.afetch_output_forecast()
        )
        assert calls == [
            (
                "/media/6497/output-forecast-csv-file.csv",
                ers_season_average_price_forecasts.PRODUCT_PAGE,
            )
        ]
        assert len(records) == 2
        assert records[0]["commodity"] == "Corn"


class TestSeasonAveragePriceForecasts:
    """Tests for the SeasonAveragePriceForecasts model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = SeasonAveragePriceForecastsFetcher.transform_query(
            {"commodity": "Soybeans", "start_year": 2020, "latest": True}
        )
        assert isinstance(query, SeasonAveragePriceForecastsQueryParams)
        assert query.commodity == "Soybeans"
        assert query.start_year == 2020
        assert query.latest is True

    def test_commodity_defaults_when_blank(self):
        """Empty, None, or empty-list commodity values normalize to the default."""
        assert SeasonAveragePriceForecastsQueryParams().commodity == "Corn"
        assert (
            SeasonAveragePriceForecastsQueryParams(commodity=None).commodity == "Corn"
        )
        assert SeasonAveragePriceForecastsQueryParams(commodity="").commodity == "Corn"
        assert SeasonAveragePriceForecastsQueryParams(commodity=[]).commodity == "Corn"

    def test_commodity_accepts_list_and_case(self):
        """A single-item list or mixed-case string resolves to the canonical name."""
        assert (
            SeasonAveragePriceForecastsQueryParams(commodity=["wheat"]).commodity
            == "Wheat"
        )
        assert (
            SeasonAveragePriceForecastsQueryParams(commodity=" cotton ").commodity
            == "Cotton"
        )

    def test_unknown_commodity_raises(self):
        """Unknown commodity values raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid commodity: Barley"):
            SeasonAveragePriceForecastsQueryParams(commodity="Barley")

    def test_latest_default_false(self):
        """The latest flag defaults to False."""
        assert SeasonAveragePriceForecastsQueryParams().latest is False

    def test_aextract_filters_commodity(self, monkeypatch):
        """aextract_data keeps only rows of the queried commodity."""

        async def fake_afetch_output_forecast():
            return [
                {"commodity": "Corn", "marketing_year": "2025"},
                {"commodity": "Wheat", "marketing_year": "2025"},
            ]

        monkeypatch.setattr(
            ers_season_average_price_forecasts,
            "afetch_output_forecast",
            fake_afetch_output_forecast,
        )
        query = SeasonAveragePriceForecastsFetcher.transform_query(
            {"commodity": "Corn"}
        )
        records = asyncio.run(
            SeasonAveragePriceForecastsFetcher.aextract_data(query, None)
        )
        assert [record["commodity"] for record in records] == ["Corn"]

    def test_transform_data_emits_wide_rows_sorted_and_coerced(self):
        """Rows stay wide, sort newest-first, and NA cells coerce to None."""
        records = [
            _full_row(
                model_forecast_date="2026-07-02",
                marketing_year="2027",
                mya_price_model_forecast="4.679482",
                mya_price_wasde_forecast="NA",
                actual_mya_price="",
            ),
            _full_row(
                model_forecast_date="2025-01-01",
                marketing_year="2024",
                mya_price_model_forecast="4.0",
                actual_mya_price="4.32",
            ),
            _full_row(
                model_forecast_date="2026-07-02",
                marketing_year="2025",
                mya_price_model_forecast="4.196194",
            ),
        ]
        query = SeasonAveragePriceForecastsFetcher.transform_query({})
        data = SeasonAveragePriceForecastsFetcher.transform_data(query, records)
        assert [(row.model_forecast_date, row.marketing_year) for row in data] == [
            ("2026-07-02", "2027"),
            ("2026-07-02", "2025"),
            ("2025-01-01", "2024"),
        ]
        assert isinstance(data[0], SeasonAveragePriceForecastsData)
        assert data[-1].actual_mya_price == 4.32
        assert data[-1].mya_price_model_forecast == 4.0
        assert data[0].mya_price_wasde_forecast is None
        assert data[1].actual_mya_price is None
        assert data[-1].target_price is None

    def test_transform_data_hidden_columns_keep_schema(self):
        """Hidden measure fields remain declared so column defs still generate."""
        assert "target_price" in SeasonAveragePriceForecastsData.model_fields
        assert "arc_co_price_model_forecast" in (
            SeasonAveragePriceForecastsData.model_fields
        )

    def test_pinned_row_label_columns_lead(self):
        """The pinned forecast date and marketing year lead the served columns."""
        fields = SeasonAveragePriceForecastsData.model_fields
        assert list(fields)[:2] == ["model_forecast_date", "marketing_year"]
        assert [
            name
            for name, field in fields.items()
            if field.json_schema_extra["x-widget_config"].get("pinned") == "left"
        ] == ["model_forecast_date", "marketing_year"]

    def test_transform_data_filters_years(self):
        """start_year and end_year filter on the integer marketing year."""
        records = [
            _full_row(marketing_year=str(year), model_forecast_date="2026-07-02")
            for year in ("2023", "2024", "2025", "2026")
        ]
        query = SeasonAveragePriceForecastsFetcher.transform_query(
            {"start_year": 2024, "end_year": 2025}
        )
        data = SeasonAveragePriceForecastsFetcher.transform_data(query, records)
        assert [row.marketing_year for row in data] == ["2025", "2024"]

    def test_transform_data_latest_keeps_most_recent_vintage(self):
        """The latest flag keeps only the most recent model_forecast_date."""
        records = [
            _full_row(model_forecast_date="2025-01-01", marketing_year="2024"),
            _full_row(model_forecast_date="2026-07-02", marketing_year="2025"),
            _full_row(model_forecast_date="2026-07-02", marketing_year="2026"),
        ]
        query = SeasonAveragePriceForecastsFetcher.transform_query({"latest": True})
        data = SeasonAveragePriceForecastsFetcher.transform_data(query, records)
        assert {row.model_forecast_date for row in data} == {"2026-07-02"}
        assert [row.marketing_year for row in data] == ["2026", "2025"]

    def test_transform_data_empty_returns_empty(self):
        """Empty input yields no rows without computing a latest vintage."""
        query = SeasonAveragePriceForecastsFetcher.transform_query({"latest": True})
        assert SeasonAveragePriceForecastsFetcher.transform_data(query, []) == []

    def test_full_row_round_trips_through_parse(self):
        """A full 42-column CSV row parses and validates end-to-end."""
        row = _full_row(actual_mya_price="4.32", effective_reference_price="4.42")
        buffer = StringIO()
        writer = csv.DictWriter(buffer, fieldnames=OUTPUT_FORECAST_COLUMNS)
        writer.writeheader()
        writer.writerow(row)
        parsed = parse_output_forecast(buffer.getvalue())
        query = SeasonAveragePriceForecastsFetcher.transform_query({})
        data = SeasonAveragePriceForecastsFetcher.transform_data(query, parsed)
        assert len(data) == 1
        assert data[0].commodity == "Corn"
        assert data[0].actual_mya_price == 4.32
        assert data[0].effective_reference_price == 4.42
        assert data[0].target_price is None
        assert data[0].price_unit == "U.S. dollars per bushel"
