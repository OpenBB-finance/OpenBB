"""Tests for the USDA ERS commodity costs and returns utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_us.usda.models.commodity_costs_and_returns import (
    CommodityCostsAndReturnsFetcher,
    CommodityCostsAndReturnsQueryParams,
)
from openbb_government_us.usda.utils import ers_commodity_costs_and_returns
from openbb_government_us.usda.utils.ers_commodity_costs_and_returns import (
    CATEGORY_CHOICES,
    COMMODITY_FILES,
    COMMODITY_REGIONS,
    build_url,
    category_order,
    clean_item,
    media_path,
    parse_rows,
)

SAMPLE_CSV = (
    '"Commodity","Category","Item","Units","Size","Region","Country","Year",'
    '"Value","Survey base year"\n'
    '"Corn","Operating costs","Fertilizer  ","dollars per planted acre",'
    '"No specific size","U.S. total","United States",2024,152.41,'
    '"Base survey of 2021"\n'
    '"Corn","Operating costs","Fertilizer  ","dollars per planted acre",'
    '"No specific size","U.S. total","United States",2025,158.88,'
    '"Base survey of 2021"\n'
    '"Corn","Gross value of production","Total, gross value of production",'
    '"dollars per planted acre","No specific size","U.S. total",'
    '"United States",2025,782.44,"Base survey of 2021"\n'
    '"Corn","Supporting information","Yield","bushels per planted acre",'
    '"No specific size","Heartland","United States",2025,198,'
    '"Base survey of 2021"\n'
    '"Corn","Net value","Value of production less total costs listed",'
    '"dollars per planted acre","No specific size","U.S. total",'
    '"United States",2023,,"Base survey of 2021"\n'
)


def make_record(**overrides) -> dict:
    """Build a parsed row record with optional field overrides."""
    record = {
        "commodity_key": "corn",
        "commodity": "Corn",
        "category": "Operating costs",
        "item": "Fertilizer",
        "units": "dollars per planted acre",
        "region": "U.S. total",
        "year": 2024,
        "value": 152.41,
        "survey_base_year": "Base survey of 2021",
    }
    record.update(overrides)
    return record


class TestErsCommodityCostsAndReturnsUtils:
    """Tests for the ers_commodity_costs_and_returns utils module."""

    def test_catalog_contents(self):
        """The catalog holds 17 commodities with unique ids, slugs, labels."""
        assert len(COMMODITY_FILES) == 17
        media_ids = [entry["media_id"] for entry in COMMODITY_FILES.values()]
        assert len(set(media_ids)) == 17
        slugs = [entry["slug"] for entry in COMMODITY_FILES.values()]
        assert len(set(slugs)) == 17
        labels = [entry["label"] for entry in COMMODITY_FILES.values()]
        assert len(set(labels)) == 17

    def test_region_catalog(self):
        """Every commodity has a region list led by the U.S. total aggregate."""
        assert set(COMMODITY_REGIONS) == set(COMMODITY_FILES)
        for regions in COMMODITY_REGIONS.values():
            assert regions[0] == "U.S. total"
            assert len(regions) == len(set(regions))
        assert COMMODITY_REGIONS["hogs_farrow_weanling"] == ["U.S. total"]
        assert "Southern Seaboard (AL, GA)" in COMMODITY_REGIONS["peanuts"]

    def test_category_choices(self):
        """The category map covers the nine published budget sections."""
        assert len(CATEGORY_CHOICES) == 9
        assert len(set(CATEGORY_CHOICES.values())) == 9
        assert CATEGORY_CHOICES["operating_costs"] == "Operating costs"

    def test_category_order(self):
        """Known categories rank in budget order and unknowns sort last."""
        assert category_order("Gross value of production") == 0
        assert category_order("Operating costs") == 1
        assert category_order("Production practices") == 8
        assert category_order("Something else") == 99

    def test_media_path(self):
        """media_path builds the commodity's media path."""
        assert media_path("corn") == "/media/4962/corn.csv"
        assert media_path("cow_calf") == "/media/4982/cow-calf.csv"
        assert (
            media_path("hogs_weanling_feeder") == "/media/4994/hogs-weanling-feeder.csv"
        )

    def test_build_url(self):
        """URLs follow the /media/{media_id}/{slug}.csv pattern."""
        assert build_url("corn") == "https://www.ers.usda.gov/media/4962/corn.csv"
        assert build_url("cow_calf") == (
            "https://www.ers.usda.gov/media/4982/cow-calf.csv"
        )

    def test_clean_item(self):
        """Trailing whitespace, footnote superscripts, and runs are stripped."""
        assert clean_item("Fertilizer  ") == "Fertilizer"
        assert clean_item("Custom services  ") == "Custom services"
        assert (
            clean_item("Capital recovery of machinery and equipment ³ ")
            == "Capital recovery of machinery and equipment"
        )
        assert clean_item("Total,  operating costs") == "Total, operating costs"
        assert clean_item("Seed") == "Seed"

    def test_parse_rows(self):
        """Rows parse to typed records, cleaning items and skipping blanks."""
        rows = parse_rows(SAMPLE_CSV, "corn")
        assert len(rows) == 4
        assert rows[0] == {
            "commodity_key": "corn",
            "commodity": "Corn",
            "category": "Operating costs",
            "item": "Fertilizer",
            "units": "dollars per planted acre",
            "region": "U.S. total",
            "year": 2024,
            "value": 152.41,
            "survey_base_year": "Base survey of 2021",
        }
        assert rows[3]["region"] == "Heartland"
        assert rows[3]["value"] == 198.0
        assert all(isinstance(row["year"], int) for row in rows)
        assert all(row["value"] != "" for row in rows)

    def test_afetch_commodity(self, monkeypatch):
        """afetch_commodity fetches through the ERS cache client and parses."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return SAMPLE_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        rows = asyncio.run(ers_commodity_costs_and_returns.afetch_commodity("corn"))
        assert calls == [
            ("/media/4962/corn.csv", ers_commodity_costs_and_returns.PRODUCT_PAGE)
        ]
        assert len(rows) == 4
        assert rows[0]["item"] == "Fertilizer"


class TestCommodityCostsAndReturns:
    """Tests for the CommodityCostsAndReturns model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = CommodityCostsAndReturnsFetcher.transform_query(
            {"commodity": "soybeans", "region": "U.S. total", "start_year": 2020}
        )
        assert isinstance(query, CommodityCostsAndReturnsQueryParams)
        assert query.commodity == "soybeans"
        assert query.region == "U.S. total"
        assert query.start_year == 2020

    def test_commodity_defaults_to_corn(self):
        """The commodity defaults to corn."""
        assert CommodityCostsAndReturnsQueryParams().commodity == "corn"

    def test_commodity_accepts_list_and_blank(self):
        """A list commodity takes the first element, blanks fall back to corn."""
        assert CommodityCostsAndReturnsQueryParams(commodity=["wheat"]).commodity == (
            "wheat"
        )
        assert CommodityCostsAndReturnsQueryParams(commodity="").commodity == "corn"

    def test_unknown_commodity_raises(self):
        """Unknown commodities raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid commodity: turnips.*corn"):
            CommodityCostsAndReturnsQueryParams(commodity="turnips")

    def test_region_blank_and_list(self):
        """Blank regions normalize to None and a list region takes the first."""
        assert CommodityCostsAndReturnsQueryParams(region="  ").region is None
        assert CommodityCostsAndReturnsQueryParams(region=None).region is None
        query = CommodityCostsAndReturnsQueryParams(region=["U.S. total"])
        assert query.region == "U.S. total"

    def test_category_blank_list_and_unknown(self):
        """Category normalizes lists, blanks to None, and rejects unknowns."""
        assert CommodityCostsAndReturnsQueryParams(category="").category is None
        assert (
            CommodityCostsAndReturnsQueryParams(category=["operating_costs"]).category
            == "operating_costs"
        )
        with pytest.raises(OpenBBError, match="Invalid category: bogus.*operating"):
            CommodityCostsAndReturnsQueryParams(category="bogus")

    def test_invalid_region_for_commodity_raises(self):
        """A region outside the commodity's set raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid region 'California'.*corn"):
            CommodityCostsAndReturnsQueryParams(commodity="corn", region="California")

    def test_valid_region_for_commodity(self):
        """A region within the commodity's set validates cleanly."""
        query = CommodityCostsAndReturnsQueryParams(
            commodity="rice", region="California"
        )
        assert query.region == "California"

    def test_aextract_fetches_selected_commodity(self, monkeypatch):
        """aextract_data fetches only the selected commodity's CSV."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return SAMPLE_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        query = CommodityCostsAndReturnsFetcher.transform_query({"commodity": "corn"})
        records = asyncio.run(
            CommodityCostsAndReturnsFetcher.aextract_data(query, None)
        )
        assert calls == [
            ("/media/4962/corn.csv", ers_commodity_costs_and_returns.PRODUCT_PAGE)
        ]
        assert len(records) == 4

    def test_transform_data_pivots_years_into_columns(self):
        """Each budget line is one row with a value column per year."""
        records = [
            make_record(year=2022, value=225.73),
            make_record(year=2023, value=178.94),
        ]
        query = CommodityCostsAndReturnsFetcher.transform_query({})
        data = CommodityCostsAndReturnsFetcher.transform_data(query, records)
        assert len(data) == 1
        dumped = data[0].model_dump()
        assert dumped["2022"] == 225.73
        assert dumped["2023"] == 178.94
        assert dumped["region"] == "U.S. total"
        assert dumped["item"] == "Fertilizer"
        assert not any(key.startswith("_") for key in dumped)

    def test_transform_data_filters_region(self):
        """The region filter keeps only the selected region's lines."""
        records = [
            make_record(region="U.S. total", item="Seed"),
            make_record(region="Heartland", item="Seed"),
        ]
        query = CommodityCostsAndReturnsFetcher.transform_query(
            {"commodity": "corn", "region": "Heartland"}
        )
        data = CommodityCostsAndReturnsFetcher.transform_data(query, records)
        assert [row.region for row in data] == ["Heartland"]

    def test_transform_data_filters_category(self):
        """The category filter keeps only the selected budget section."""
        records = [
            make_record(category="Operating costs", item="Seed"),
            make_record(
                category="Gross value of production",
                item="Total, gross value of production",
            ),
        ]
        query = CommodityCostsAndReturnsFetcher.transform_query(
            {"category": "gross_value_of_production"}
        )
        data = CommodityCostsAndReturnsFetcher.transform_data(query, records)
        assert [(row.category, row.item) for row in data] == [
            ("Gross value of production", "Total, gross value of production")
        ]

    def test_transform_data_filters_years(self):
        """start_year and end_year select which year columns appear."""
        records = [make_record(year=year) for year in (2021, 2022, 2023, 2024)]
        query = CommodityCostsAndReturnsFetcher.transform_query(
            {"start_year": 2022, "end_year": 2023}
        )
        data = CommodityCostsAndReturnsFetcher.transform_data(query, records)
        assert len(data) == 1
        dumped = data[0].model_dump()
        assert sorted(k for k in dumped if k.isdigit()) == ["2022", "2023"]

    def test_transform_data_survey_base_year_from_latest_year(self):
        """The survey base is taken from the most recent year in the row."""
        records = [
            make_record(year=2025, survey_base_year="Base survey of 2021"),
            make_record(year=2010, survey_base_year="Base survey of 2005"),
        ]
        query = CommodityCostsAndReturnsFetcher.transform_query({})
        data = CommodityCostsAndReturnsFetcher.transform_data(query, records)
        assert data[0].survey_base_year == "Base survey of 2021"

    def test_transform_data_orders_regions_categories_totals_last(self):
        """Rows sort by region, then budget section, with totals last."""
        records = [
            make_record(region="Heartland", category="Operating costs", item="Seed"),
            make_record(
                region="U.S. total",
                category="Operating costs",
                item="Total, operating costs",
            ),
            make_record(region="U.S. total", category="Operating costs", item="Seed"),
            make_record(
                region="U.S. total",
                category="Gross value of production",
                item="Primary product, grain",
            ),
        ]
        query = CommodityCostsAndReturnsFetcher.transform_query({"commodity": "corn"})
        data = CommodityCostsAndReturnsFetcher.transform_data(query, records)
        assert [(row.region, row.category, row.item) for row in data] == [
            ("U.S. total", "Gross value of production", "Primary product, grain"),
            ("U.S. total", "Operating costs", "Seed"),
            ("U.S. total", "Operating costs", "Total, operating costs"),
            ("Heartland", "Operating costs", "Seed"),
        ]

    def test_transform_data_unknown_region_sorts_last(self):
        """A region outside the commodity's order sorts after the known ones."""
        records = [
            make_record(region="Neptune", item="Seed"),
            make_record(region="U.S. total", item="Seed"),
        ]
        query = CommodityCostsAndReturnsFetcher.transform_query({"commodity": "corn"})
        data = CommodityCostsAndReturnsFetcher.transform_data(query, records)
        assert [row.region for row in data] == ["U.S. total", "Neptune"]

    def test_transform_data_empty_raises(self):
        """No records surviving the filters raises EmptyDataError."""
        query = CommodityCostsAndReturnsFetcher.transform_query({"start_year": 2030})
        with pytest.raises(EmptyDataError, match="No records match"):
            CommodityCostsAndReturnsFetcher.transform_data(
                query, [make_record(year=2024)]
            )
