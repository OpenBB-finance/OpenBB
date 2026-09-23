"""Tests for the USDA ERS major land uses utils and model."""

import asyncio
from io import BytesIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.major_land_uses import (
    MajorLandUsesFetcher,
    MajorLandUsesQueryParams,
)
from openbb_government_us.usda.utils import ers_major_land_uses
from openbb_government_us.usda.utils.ers_major_land_uses import (
    CROPLAND_VARIABLES,
    GEOGRAPHIES,
    LAND_USE_CATEGORIES,
    MAJOR_LAND_USES_FILES,
    PRODUCT_PAGE,
    parse_cropland_xlsx,
    parse_land_use_csv,
)

SAMPLE_LAND_USE_CSV = (
    "ID,Region,Region or State,Year,Land use,Value,Units,Release date,Source\n"
    '0,Northeast total,Northeast,1945,Total land,112402,"1,000 acres",r,s\n'
    '1,Northeast,  Maine ,1945,Cropland used for crops,1331,"1,000 acres",r,s\n'
    '2,AK and HI,Alaska,1945,Cropland used for crops,N.A.,"1,000 acres",r,s\n'
    '3,48 States,48 States,1945,Grazed forest-use land grazed,344399,"1,000 acres",r,s\n'
    '4,U.S. total,U.S. total,2017,Miscellaneous other land,196994,"1,000 acres",r,s\n'
    '5,U.S. total,U.S. total,2017,Newly added  category,5,"1,000 acres",r,s\n'
)


def build_cropland_workbook(headers=None, data_rows=None) -> bytes:
    """Build a small summary-table-3 style workbook as XLSX bytes."""
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Summary table 3—Total cropland used for crops"])
    sheet.append(
        headers
        or [
            "Year 1/",
            "Total crops harvested (million acres) 2/",
            "Double cropped (million acres) 3/",
            "Cropland harvested (million acres) 4/",
            "Crop failure (million acres)",
            "Cultivated summer fallow (million acres)",
            "Total cropland used for crops (million acres) 4/",
        ]
    )
    for row in data_rows or [
        ["1910", None, None, 317, 9, 4, 330],
        [
            "2025 5/",
            312.80963763,
            7.990656479,
            304.81898115,
            7.9362802019,
            15.455789303,
            328.21105066,
        ],
    ]:
        sheet.append(row)
    sheet.append([None])
    sheet.append(["1/ Estimates prior to 1949 do not include Alaska and Hawaii."])
    sheet.append(["5/ Data are preliminary and subject to revision."])
    sheet.append(["Sources: USDA, Economic Research Service."])
    sheet.append(["Last updated: March 13, 2026"])
    sheet.append(["Contact: USDA, Economic Research Service."])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


class TestErsMajorLandUsesUtils:
    """Tests for the ers_major_land_uses utils module."""

    def test_catalog_contents(self):
        """The catalog holds the two datasets with their media paths."""
        assert sorted(MAJOR_LAND_USES_FILES) == [
            "cropland_used_for_crops",
            "land_use",
        ]
        assert MAJOR_LAND_USES_FILES["land_use"]["media_path"].startswith(
            "/media/5639/"
        )
        assert MAJOR_LAND_USES_FILES["cropland_used_for_crops"][
            "media_path"
        ].startswith("/media/5647/")
        assert len(LAND_USE_CATEGORIES) == 16
        assert len(GEOGRAPHIES) == 63
        assert len(CROPLAND_VARIABLES) == 6

    def test_parse_land_use_csv(self):
        """Rows parse to tidy records with slugs, acres, and aggregate flags."""
        records = parse_land_use_csv(SAMPLE_LAND_USE_CSV)
        assert len(records) == 6
        assert records[0] == {
            "year": 1945,
            "geography": "Northeast",
            "region": None,
            "is_aggregate": True,
            "land_use": "total_land",
            "value": 112402000.0,
            "is_preliminary": None,
        }
        assert records[1] == {
            "year": 1945,
            "geography": "Maine",
            "region": "Northeast",
            "is_aggregate": False,
            "land_use": "cropland_used_for_crops",
            "value": 1331000.0,
            "is_preliminary": None,
        }

    def test_parse_land_use_csv_missing_values(self):
        """'N.A.' values parse to None."""
        records = parse_land_use_csv(SAMPLE_LAND_USE_CSV)
        assert records[2]["geography"] == "Alaska"
        assert records[2]["region"] == "AK and HI"
        assert records[2]["value"] is None

    def test_parse_land_use_csv_national_aggregates(self):
        """'48 States' and 'U.S. total' rows are aggregates with no region."""
        records = parse_land_use_csv(SAMPLE_LAND_USE_CSV)
        assert records[3]["geography"] == "48 States"
        assert records[3]["is_aggregate"] is True
        assert records[3]["region"] is None
        assert records[3]["land_use"] == "grazed_forest_use_land"
        assert records[4]["geography"] == "U.S. total"
        assert records[4]["is_aggregate"] is True
        assert records[4]["region"] is None

    def test_parse_land_use_csv_unknown_label_passes_through(self):
        """Unmapped land-use labels pass through whitespace-normalized."""
        records = parse_land_use_csv(SAMPLE_LAND_USE_CSV)
        assert records[5]["land_use"] == "Newly added category"

    def test_parse_cropland_xlsx(self):
        """The workbook melts to one record per year and variable."""
        records = parse_cropland_xlsx(build_cropland_workbook())
        assert len(records) == 12
        assert records[0] == {
            "year": 1910,
            "geography": "United States",
            "region": None,
            "is_aggregate": True,
            "land_use": "total_crops_harvested",
            "value": None,
            "is_preliminary": False,
        }
        assert records[3] == {
            "year": 1910,
            "geography": "United States",
            "region": None,
            "is_aggregate": True,
            "land_use": "crop_failure",
            "value": 9000000.0,
            "is_preliminary": False,
        }
        assert records[6]["year"] == 2025
        assert records[6]["is_preliminary"] is True
        assert records[6]["value"] == 312.80963763 * 1_000_000
        assert [record["land_use"] for record in records[:6]] == list(
            CROPLAND_VARIABLES
        )

    def test_parse_cropland_xlsx_stops_at_footnotes(self):
        """No footnote or metadata rows leak into the records."""
        records = parse_cropland_xlsx(build_cropland_workbook())
        assert {record["year"] for record in records} == {1910, 2025}

    def test_parse_cropland_xlsx_rejects_unexpected_layout(self):
        """A workbook without seven columns raises OpenBBError."""
        content = build_cropland_workbook(
            headers=["Year 1/", "Only column (million acres)"],
            data_rows=[["1910", 317]],
        )
        with pytest.raises(OpenBBError, match="Unexpected column layout"):
            parse_cropland_xlsx(content)

    def test_afetch_land_use(self, monkeypatch):
        """afetch_land_use fetches through the ERS cache client."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return SAMPLE_LAND_USE_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(ers_major_land_uses.afetch_land_use())
        assert calls == [
            (MAJOR_LAND_USES_FILES["land_use"]["media_path"], PRODUCT_PAGE)
        ]
        assert len(records) == 6
        assert records[0]["land_use"] == "total_land"

    def test_afetch_cropland_used_for_crops(self, monkeypatch):
        """afetch_cropland_used_for_crops fetches through the ERS cache client."""
        calls = []
        content = build_cropland_workbook()

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return content

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(ers_major_land_uses.afetch_cropland_used_for_crops())
        assert calls == [
            (
                MAJOR_LAND_USES_FILES["cropland_used_for_crops"]["media_path"],
                PRODUCT_PAGE,
            )
        ]
        assert len(records) == 12


class TestMajorLandUses:
    """Tests for the MajorLandUses model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = MajorLandUsesFetcher.transform_query(
            {"land_use": "total_land", "start_year": 2002}
        )
        assert isinstance(query, MajorLandUsesQueryParams)
        assert query.table == "land_use"
        assert query.land_use == "total_land"
        assert query.start_year == 2002

    def test_land_use_accepts_list_and_comma_string(self):
        """land_use accepts a list or a comma-separated string of slugs."""
        query = MajorLandUsesQueryParams(land_use=["total_land", "urban_areas"])
        assert query.land_use == "total_land,urban_areas"
        query = MajorLandUsesQueryParams(land_use=" total_land , urban_areas ")
        assert query.land_use == "total_land,urban_areas"

    def test_land_use_blank_returns_none(self):
        """Empty or whitespace-only land_use values normalize to None."""
        assert MajorLandUsesQueryParams(land_use=None).land_use is None
        assert MajorLandUsesQueryParams(land_use="").land_use is None
        assert MajorLandUsesQueryParams(land_use=" , ").land_use is None

    def test_unknown_land_use_raises(self):
        """Unknown land_use slugs raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid land_use.*bogus.*total_land"):
            MajorLandUsesQueryParams(land_use="total_land,bogus")

    def test_geography_accepts_list_and_normalizes_case(self):
        """geography accepts lists and case-insensitive names."""
        query = MajorLandUsesQueryParams(geography=["maine", "U.S. TOTAL"])
        assert query.geography == "Maine,U.S. total"
        query = MajorLandUsesQueryParams(geography="corn belt , Iowa")
        assert query.geography == "Corn Belt,Iowa"

    def test_geography_blank_returns_none(self):
        """Empty or whitespace-only geography values normalize to None."""
        assert MajorLandUsesQueryParams(geography=None).geography is None
        assert MajorLandUsesQueryParams(geography="").geography is None
        assert MajorLandUsesQueryParams(geography=" , ").geography is None

    def test_unknown_geography_raises(self):
        """Unknown geography names raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid geography.*Narnia.*Maine"):
            MajorLandUsesQueryParams(geography="Maine,Narnia")

    def test_aextract_land_use_table(self, monkeypatch):
        """aextract_data fetches the all-data CSV for table='land_use'."""
        fetched = []

        async def fake_afetch_land_use():
            fetched.append("land_use")
            return [{"land_use": "total_land"}]

        monkeypatch.setattr(
            ers_major_land_uses, "afetch_land_use", fake_afetch_land_use
        )
        query = MajorLandUsesFetcher.transform_query({})
        records = asyncio.run(MajorLandUsesFetcher.aextract_data(query, None))
        assert fetched == ["land_use"]
        assert records == [{"land_use": "total_land"}]

    def test_aextract_cropland_table(self, monkeypatch):
        """aextract_data fetches summary table 3 for the annual table."""
        fetched = []

        async def fake_afetch_cropland():
            fetched.append("cropland_used_for_crops")
            return [{"land_use": "crop_failure"}]

        monkeypatch.setattr(
            ers_major_land_uses,
            "afetch_cropland_used_for_crops",
            fake_afetch_cropland,
        )
        query = MajorLandUsesFetcher.transform_query(
            {"table": "cropland_used_for_crops"}
        )
        records = asyncio.run(MajorLandUsesFetcher.aextract_data(query, None))
        assert fetched == ["cropland_used_for_crops"]
        assert records == [{"land_use": "crop_failure"}]

    @staticmethod
    def make_record(**overrides) -> dict:
        """Build a tidy land-use record with overridable fields."""
        record = {
            "year": 2017,
            "geography": "Maine",
            "region": "Northeast",
            "is_aggregate": False,
            "land_use": "total_land",
            "value": 1000.0,
            "is_preliminary": None,
        }
        record.update(overrides)
        return record

    def test_transform_data_filters_years(self):
        """start_year and end_year select which year columns appear."""
        records = [self.make_record(year=year) for year in (1997, 2002, 2007, 2012)]
        query = MajorLandUsesFetcher.transform_query(
            {"start_year": 2002, "end_year": 2007}
        )
        data = MajorLandUsesFetcher.transform_data(query, records)
        assert len(data) == 1
        dumped = data[0].model_dump()
        assert sorted(k for k in dumped if k.isdigit()) == ["2002", "2007"]

    def test_transform_data_filters_land_use_and_geography(self):
        """land_use and geography selections filter the records."""
        records = [
            self.make_record(land_use="total_land", geography="Maine"),
            self.make_record(land_use="urban_areas", geography="Maine"),
            self.make_record(land_use="total_land", geography="Iowa"),
        ]
        query = MajorLandUsesFetcher.transform_query(
            {"land_use": "total_land", "geography": "Maine"}
        )
        data = MajorLandUsesFetcher.transform_data(query, records)
        assert len(data) == 1
        assert data[0].land_use == "total_land"
        assert data[0].geography == "Maine"

    def test_transform_data_ignores_filters_for_annual_table(self):
        """land_use and geography do not filter the annual table."""
        records = [
            {
                "year": 2025,
                "geography": "United States",
                "region": None,
                "is_aggregate": True,
                "land_use": "crop_failure",
                "value": 7936280.2019,
                "is_preliminary": True,
            }
        ]
        query = MajorLandUsesFetcher.transform_query(
            {
                "table": "cropland_used_for_crops",
                "land_use": "total_land",
                "geography": "Maine",
            }
        )
        data = MajorLandUsesFetcher.transform_data(query, records)
        assert len(data) == 1
        assert data[0].land_use == "crop_failure"
        assert data[0].model_dump()["2025"] == 7936280.2019

    def test_transform_data_keeps_missing_values(self):
        """A None value becomes a None year cell in the pivoted row."""
        records = [self.make_record(geography="Alaska", region=None, value=None)]
        query = MajorLandUsesFetcher.transform_query({})
        data = MajorLandUsesFetcher.transform_data(query, records)
        assert data[0].model_dump()["2017"] is None

    def test_transform_data_pivots_years_into_columns(self):
        """Each land_use and geography is one row with a value column per year."""
        records = [
            self.make_record(land_use="urban_areas", geography="Iowa", year=2012),
            self.make_record(land_use="total_land", geography="Maine", year=2012),
            self.make_record(
                land_use="total_land", geography="Maine", year=2017, value=1100.0
            ),
        ]
        query = MajorLandUsesFetcher.transform_query({})
        data = MajorLandUsesFetcher.transform_data(query, records)
        assert [(row.land_use, row.geography) for row in data] == [
            ("urban_areas", "Iowa"),
            ("total_land", "Maine"),
        ]
        maine = data[1].model_dump()
        assert maine["2012"] == 1000.0
        assert maine["2017"] == 1100.0
