"""Tests for the additional Philadelphia Fed regional dataset models."""

import io
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.philadelphia_anxious import (
    FederalReservePhiladelphiaAnxiousData,
    FederalReservePhiladelphiaAnxiousFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_atsix import (
    FederalReservePhiladelphiaAtsixData,
    FederalReservePhiladelphiaAtsixFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_coincident import (
    FederalReservePhiladelphiaCoincidentData,
    FederalReservePhiladelphiaCoincidentFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_gdpplus import (
    FederalReservePhiladelphiaGdpPlusData,
    FederalReservePhiladelphiaGdpPlusFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_livingston import (
    FederalReservePhiladelphiaLivingstonData,
    FederalReservePhiladelphiaLivingstonFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_mbos import (
    FederalReservePhiladelphiaManufacturingData,
    FederalReservePhiladelphiaManufacturingFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_nbos import (
    FederalReservePhiladelphiaNonmanufacturingData,
    FederalReservePhiladelphiaNonmanufacturingFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_partisan import (
    FederalReservePhiladelphiaPartisanData,
    FederalReservePhiladelphiaPartisanFetcher,
)
from openbb_federal_reserve.models.regional.philadelphia_spf import (
    FederalReservePhiladelphiaSpfData,
    FederalReservePhiladelphiaSpfFetcher,
)


def _workbook(sheet_name, rows, *, with_doc_props=False):
    """Build an ``.xlsx`` workbook with one named sheet from header/value rows."""
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name
    for row in rows:
        sheet.append(row)
    if with_doc_props:
        workbook.properties.creator = "test"
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


class TestSurveyProfessionalForecasters:
    """Tests for the Survey of Professional Forecasters fetcher."""

    def _book(self):
        """Build a Median_Level SPF workbook for RGDP."""
        header = ["YEAR", "QUARTER", *[f"RGDP{i}" for i in range(1, 7)]]
        header += [f"RGDP{c}" for c in ("A", "B", "C", "D")]
        return _workbook(
            "Median_Level",
            [
                header,
                [2026, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                [2026, 2, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            ],
        )

    def test_parses_horizons_and_annuals(self, monkeypatch):
        """The workbook resolves to quarter-start dates with horizon/annual cols."""
        from openbb_federal_reserve.utils import philadelphia as utils

        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: self._book())
        query = FederalReservePhiladelphiaSpfFetcher.transform_query(
            {"variable": "RGDP", "statistic": "median", "transform": "level"}
        )
        rows = FederalReservePhiladelphiaSpfFetcher.extract_data(query, None)
        result = FederalReservePhiladelphiaSpfFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReservePhiladelphiaSpfData) for r in result)
        assert result[0].date == date(2026, 1, 1)
        assert result[1].date == date(2026, 4, 1)
        assert result[1].horizon_1 == 11
        assert result[1].annual_a == 17

    def test_growth_prefix_and_filter(self, monkeypatch):
        """A growth transform reads the D-prefixed columns and dates filter."""
        from openbb_federal_reserve.utils import philadelphia as utils

        header = ["YEAR", "QUARTER", *[f"DRGDP{i}" for i in range(1, 7)]]
        header += [f"DRGDP{c}" for c in ("A", "B", "C", "D")]
        book = _workbook(
            "Mean_Growth",
            [header, [2026, 1, *range(10)], [2026, 2, *range(10, 20)]],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaSpfFetcher.transform_query(
            {
                "variable": "RGDP",
                "statistic": "mean",
                "transform": "growth",
                "start_date": "2026-04-01",
                "end_date": "2026-06-30",
            }
        )
        result = FederalReservePhiladelphiaSpfFetcher.transform_data(
            query, FederalReservePhiladelphiaSpfFetcher.extract_data(query, None)
        )
        assert [r.date for r in result] == [date(2026, 4, 1)]

    def test_long_run_single_column(self, monkeypatch):
        """A long-run variable maps its bare column to ``long_run`` as a level."""
        from openbb_federal_reserve.utils import philadelphia as utils

        captured: dict = {}

        def _fetch(url, cache_key, cadence):
            captured["url"] = url
            return _workbook(
                "Mean_Level",
                [["YEAR", "QUARTER", "RGDP10"], [2026, 1, 2.1], [2026, 2, None]],
            )

        monkeypatch.setattr(utils, "fetch_philadelphia", _fetch)
        query = FederalReservePhiladelphiaSpfFetcher.transform_query(
            {"variable": "RGDP10", "statistic": "mean", "transform": "growth"}
        )
        rows = FederalReservePhiladelphiaSpfFetcher.extract_data(query, None)
        result = FederalReservePhiladelphiaSpfFetcher.transform_data(query, rows)
        assert captured["url"].endswith("Mean_RGDP10_Level.xlsx")
        assert len(result) == 1
        assert result[0].long_run == 2.1
        assert result[0].horizon_1 is None

    def test_drops_all_none_rows_keeps_partial(self, monkeypatch):
        """All-None value rows drop while partially-populated rows survive."""
        from openbb_federal_reserve.utils import philadelphia as utils

        header = ["YEAR", "QUARTER", *[f"RGDP{i}" for i in range(1, 7)]]
        header += [f"RGDP{c}" for c in ("A", "B", "C", "D")]
        book = _workbook(
            "Median_Level",
            [
                header,
                [2026, 1, *([None] * 10)],
                [2026, 2, 11, *([None] * 9)],
            ],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaSpfFetcher.transform_query(
            {"variable": "RGDP", "statistic": "median", "transform": "level"}
        )
        result = FederalReservePhiladelphiaSpfFetcher.transform_data(
            query, FederalReservePhiladelphiaSpfFetcher.extract_data(query, None)
        )
        assert [r.date for r in result] == [date(2026, 4, 1)]
        assert result[0].horizon_1 == 11

    def test_all_none_raises_empty(self, monkeypatch):
        """A workbook whose value rows are all None raises ``EmptyDataError``."""
        from openbb_federal_reserve.utils import philadelphia as utils

        header = ["YEAR", "QUARTER", *[f"RGDP{i}" for i in range(1, 7)]]
        header += [f"RGDP{c}" for c in ("A", "B", "C", "D")]
        book = _workbook("Median_Level", [header, [2026, 1, *([None] * 10)]])
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaSpfFetcher.transform_query(
            {"variable": "RGDP", "statistic": "median", "transform": "level"}
        )
        rows = FederalReservePhiladelphiaSpfFetcher.extract_data(query, None)
        with pytest.raises(EmptyDataError):
            FederalReservePhiladelphiaSpfFetcher.transform_data(query, rows)

    def test_empty_raises(self, monkeypatch):
        """An empty download raises ``EmptyDataError``."""
        from openbb_federal_reserve.utils import philadelphia as utils

        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: b"")
        query = FederalReservePhiladelphiaSpfFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReservePhiladelphiaSpfFetcher.extract_data(query, None)


class TestAnxiousIndex:
    """Tests for the Anxious Index fetcher."""

    def _book(self):
        """Build an Anxious Index workbook with three junk header rows."""
        return _workbook(
            "Data",
            [
                ["junk0"],
                ["junk1"],
                ["junk2"],
                ["Obs Year", "Obs Quarter", "Anxious Index", "RECESS"],
                [2026, 2, 20.5, None],
                [2026, 3, 25.05, None],
            ],
            with_doc_props=True,
        )

    def test_parses_header_offset(self, monkeypatch):
        """Header row 3 parses and the docProps part is stripped cleanly."""
        from openbb_federal_reserve.utils import philadelphia as utils

        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: self._book())
        query = FederalReservePhiladelphiaAnxiousFetcher.transform_query(
            {"start_date": "2026-07-01", "end_date": "2026-07-01"}
        )
        result = FederalReservePhiladelphiaAnxiousFetcher.transform_data(
            query, FederalReservePhiladelphiaAnxiousFetcher.extract_data(query, None)
        )
        assert all(isinstance(r, FederalReservePhiladelphiaAnxiousData) for r in result)
        assert len(result) == 1
        assert result[-1].date == date(2026, 7, 1)
        assert result[-1].anxious_index == 25.05
        assert result[-1].recession is None

    def test_drops_all_none_rows_keeps_partial(self, monkeypatch):
        """A row with no anxious_index or recession drops; a partial row stays."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook(
            "Data",
            [
                ["junk0"],
                ["junk1"],
                ["junk2"],
                ["Obs Year", "Obs Quarter", "Anxious Index", "RECESS"],
                [2026, 1, None, None],
                [2026, 2, 20.5, None],
            ],
            with_doc_props=True,
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaAnxiousFetcher.transform_query({})
        result = FederalReservePhiladelphiaAnxiousFetcher.transform_data(
            query, FederalReservePhiladelphiaAnxiousFetcher.extract_data(query, None)
        )
        assert [r.date for r in result] == [date(2026, 4, 1)]
        assert result[0].anxious_index == 20.5

    def test_all_none_raises_empty(self, monkeypatch):
        """A sheet with only all-None value rows raises ``EmptyDataError``."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook(
            "Data",
            [
                ["junk0"],
                ["junk1"],
                ["junk2"],
                ["Obs Year", "Obs Quarter", "Anxious Index", "RECESS"],
                [2026, 1, None, None],
            ],
            with_doc_props=True,
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaAnxiousFetcher.transform_query({})
        rows = FederalReservePhiladelphiaAnxiousFetcher.extract_data(query, None)
        with pytest.raises(EmptyDataError):
            FederalReservePhiladelphiaAnxiousFetcher.transform_data(query, rows)

    def test_empty_raises(self, monkeypatch):
        """An empty download raises ``EmptyDataError``."""
        from openbb_federal_reserve.utils import philadelphia as utils

        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: b"")
        query = FederalReservePhiladelphiaAnxiousFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReservePhiladelphiaAnxiousFetcher.extract_data(query, None)


class TestGdpPlus:
    """Tests for the GDPplus fetcher."""

    def test_parses_growth_rates(self, monkeypatch):
        """The GDPplus sheet resolves to quarterly growth records."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook(
            "Sheet1",
            [
                [
                    "OBS_YEAR",
                    "OBS_QUARTER",
                    "RECBARS",
                    "GRGDP_DATA",
                    "GRGDI_DATA",
                    "GDPPLUS_DATA",
                ],
                [2026, 1, 0, 1.6, 0.9, 1.5],
            ],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaGdpPlusFetcher.transform_query(
            {"start_date": "2026-01-01", "end_date": "2026-03-31"}
        )
        result = FederalReservePhiladelphiaGdpPlusFetcher.transform_data(
            query, FederalReservePhiladelphiaGdpPlusFetcher.extract_data(query, None)
        )
        assert isinstance(result[0], FederalReservePhiladelphiaGdpPlusData)
        assert result[0].date == date(2026, 1, 1)
        assert result[0].gdpplus == 1.5
        assert result[0].recession == 0

    def test_empty_raises(self, monkeypatch):
        """An empty download raises ``EmptyDataError``."""
        from openbb_federal_reserve.utils import philadelphia as utils

        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: b"")
        query = FederalReservePhiladelphiaGdpPlusFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReservePhiladelphiaGdpPlusFetcher.extract_data(query, None)


class TestPartisanConflict:
    """Tests for the Partisan Conflict Index fetcher."""

    def test_parses_named_months(self, monkeypatch):
        """Named months, including a trailing-space label, parse to dates."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook(
            "Sheet1",
            [
                ["Year", "Month", "Partisan Conflict"],
                [2025, "September ", 150.0],
                [2025, "June", 193.64],
            ],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaPartisanFetcher.transform_query(
            {"start_date": "2025-01-01", "end_date": "2025-12-31"}
        )
        result = FederalReservePhiladelphiaPartisanFetcher.transform_data(
            query, FederalReservePhiladelphiaPartisanFetcher.extract_data(query, None)
        )
        assert all(
            isinstance(r, FederalReservePhiladelphiaPartisanData) for r in result
        )
        assert result[0].date == date(2025, 6, 1)
        assert result[1].date == date(2025, 9, 1)
        assert result[0].partisan_conflict == 193.64

    def test_empty_raises(self, monkeypatch):
        """An empty download raises ``EmptyDataError``."""
        from openbb_federal_reserve.utils import philadelphia as utils

        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: b"")
        query = FederalReservePhiladelphiaPartisanFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReservePhiladelphiaPartisanFetcher.extract_data(query, None)


class TestStateCoincidentIndex:
    """Tests for the State Coincident Indexes fetcher."""

    def _book(self):
        """Build a wide state-index workbook."""
        return _workbook(
            "Indexes",
            [
                ["Date", "PA", "NJ", "US"],
                ["2026-03-01", 134.0, 200.0, 110.0],
                ["2026-04-01", 135.1549, 201.0, 111.0],
            ],
        )

    def test_melts_to_long(self, monkeypatch):
        """Wide state columns melt to long state/value records."""
        from openbb_federal_reserve.utils import philadelphia as utils

        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: self._book())
        query = FederalReservePhiladelphiaCoincidentFetcher.transform_query({})
        result = FederalReservePhiladelphiaCoincidentFetcher.transform_data(
            query, FederalReservePhiladelphiaCoincidentFetcher.extract_data(query, None)
        )
        assert all(
            isinstance(r, FederalReservePhiladelphiaCoincidentData) for r in result
        )
        assert {r.state for r in result} == {"PA", "NJ", "US"}
        assert len(result) == 6

    def test_state_filter_returns_raw_value(self, monkeypatch):
        """The state filter narrows to one state and returns the raw value."""
        from openbb_federal_reserve.utils import philadelphia as utils

        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: self._book())
        query = FederalReservePhiladelphiaCoincidentFetcher.transform_query(
            {"state": "pa", "start_date": "2026-04-01", "end_date": "2026-04-30"}
        )
        result = FederalReservePhiladelphiaCoincidentFetcher.transform_data(
            query, FederalReservePhiladelphiaCoincidentFetcher.extract_data(query, None)
        )
        assert [(r.state, r.value) for r in result] == [("PA", 135.1549)]

    def test_diffusion_dataset(self, monkeypatch):
        """The diffusion dataset melts the DI1 and DI3 series."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook(
            "Diffusion_Indexes",
            [["Date", "DI1", "DI3"], ["2026-04-01", 82.0, 90.0]],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaCoincidentFetcher.transform_query(
            {"dataset": "diffusion"}
        )
        result = FederalReservePhiladelphiaCoincidentFetcher.transform_data(
            query, FederalReservePhiladelphiaCoincidentFetcher.extract_data(query, None)
        )
        assert {(r.state, r.value) for r in result} == {("DI1", 82.0), ("DI3", 90.0)}

    def test_drops_none_value_cells(self, monkeypatch):
        """A melted cell with no value drops while populated cells survive."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook(
            "Indexes",
            [
                ["Date", "PA", "NJ"],
                ["2026-03-01", None, None],
                ["2026-04-01", 135.15, None],
            ],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaCoincidentFetcher.transform_query({})
        result = FederalReservePhiladelphiaCoincidentFetcher.transform_data(
            query, FederalReservePhiladelphiaCoincidentFetcher.extract_data(query, None)
        )
        assert [(r.date, r.state, r.value) for r in result] == [
            (date(2026, 4, 1), "PA", 135.15)
        ]

    def test_all_none_raises_empty(self, monkeypatch):
        """A workbook whose every cell is None raises ``EmptyDataError``."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook(
            "Indexes",
            [["Date", "PA", "NJ"], ["2026-03-01", None, None]],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaCoincidentFetcher.transform_query({})
        rows = FederalReservePhiladelphiaCoincidentFetcher.extract_data(query, None)
        with pytest.raises(EmptyDataError):
            FederalReservePhiladelphiaCoincidentFetcher.transform_data(query, rows)

    def test_empty_raises(self, monkeypatch):
        """An empty download raises ``EmptyDataError``."""
        from openbb_federal_reserve.utils import philadelphia as utils

        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: b"")
        query = FederalReservePhiladelphiaCoincidentFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReservePhiladelphiaCoincidentFetcher.extract_data(query, None)


class TestLivingstonSurvey:
    """Tests for the Livingston Survey fetcher."""

    def test_parses_horizon_columns(self, monkeypatch):
        """The selected variable sheet maps the horizon-suffix columns."""
        from openbb_federal_reserve.utils import philadelphia as utils

        header = [
            "Date",
            "RGDPX_BP",
            "RGDPX_ZM",
            "RGDPX_6M",
            "RGDPX_12M",
            "RGDPX_BY",
            "RGDPX_ZY",
            "RGDPX_1Y",
            "RGDPX_2Y",
            "RGDPX_10Y",
        ]
        book = _workbook(
            "RGDPX",
            [header, ["2026-06-01", 1, 2, 3, 4, 5, 6, 7, None, 2.05]],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaLivingstonFetcher.transform_query(
            {
                "variable": "RGDPX",
                "statistic": "mean",
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
            }
        )
        result = FederalReservePhiladelphiaLivingstonFetcher.transform_data(
            query,
            FederalReservePhiladelphiaLivingstonFetcher.extract_data(query, None),
        )
        assert isinstance(result[0], FederalReservePhiladelphiaLivingstonData)
        assert result[0].date == date(2026, 6, 1)
        assert result[0].base_prior == 1
        assert result[0].ten_year == 2.05
        assert result[0].two_year is None

    def _header(self):
        """Build the full RGDPX horizon-suffix header."""
        return [
            "Date",
            "RGDPX_BP",
            "RGDPX_ZM",
            "RGDPX_6M",
            "RGDPX_12M",
            "RGDPX_BY",
            "RGDPX_ZY",
            "RGDPX_1Y",
            "RGDPX_2Y",
            "RGDPX_10Y",
        ]

    def test_drops_all_none_rows_keeps_partial(self, monkeypatch):
        """An all-None horizon row drops while a partially-filled row stays."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook(
            "RGDPX",
            [
                self._header(),
                ["2026-06-01", *([None] * 9)],
                ["2026-12-01", 1, *([None] * 8)],
            ],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaLivingstonFetcher.transform_query(
            {"variable": "RGDPX", "statistic": "mean"}
        )
        result = FederalReservePhiladelphiaLivingstonFetcher.transform_data(
            query,
            FederalReservePhiladelphiaLivingstonFetcher.extract_data(query, None),
        )
        assert [r.date for r in result] == [date(2026, 12, 1)]
        assert result[0].base_prior == 1

    def test_all_none_raises_empty(self, monkeypatch):
        """A sheet whose every horizon cell is None raises ``EmptyDataError``."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook("RGDPX", [self._header(), ["2026-06-01", *([None] * 9)]])
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaLivingstonFetcher.transform_query(
            {"variable": "RGDPX", "statistic": "mean"}
        )
        rows = FederalReservePhiladelphiaLivingstonFetcher.extract_data(query, None)
        with pytest.raises(EmptyDataError):
            FederalReservePhiladelphiaLivingstonFetcher.transform_data(query, rows)

    def test_empty_raises(self, monkeypatch):
        """An empty download raises ``EmptyDataError``."""
        from openbb_federal_reserve.utils import philadelphia as utils

        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: b"")
        query = FederalReservePhiladelphiaLivingstonFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReservePhiladelphiaLivingstonFetcher.extract_data(query, None)


class TestManufacturingOutlook:
    """Tests for the Manufacturing Business Outlook (MBOS) fetcher."""

    def test_wide_columns_raw_and_map_century(self, monkeypatch):
        """The wide CSV returns raw values, drops blanks, and maps old years."""
        from openbb_federal_reserve.utils import philadelphia as utils

        csv = b"DATE,GAC,NOC\nMay-68,1.005,2.0\nJun-26,10.345,\n"
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: csv)
        query = FederalReservePhiladelphiaManufacturingFetcher.transform_query(
            {"start_date": "1900-01-01", "end_date": "2099-12-31"}
        )
        result = FederalReservePhiladelphiaManufacturingFetcher.transform_data(
            query,
            FederalReservePhiladelphiaManufacturingFetcher.extract_data(query, None),
        )
        assert all(
            isinstance(r, FederalReservePhiladelphiaManufacturingData) for r in result
        )
        assert [r.date for r in result] == [date(1968, 5, 1), date(2026, 6, 1)]
        wide = result[0].model_dump()
        assert wide["GAC"] == 1.005
        assert wide["NOC"] == 2.0
        late = result[1].model_dump()
        assert late["GAC"] == 10.345
        assert "NOC" not in late

    def test_date_filter_narrows_rows(self, monkeypatch):
        """The date bounds narrow the returned wide rows."""
        from openbb_federal_reserve.utils import philadelphia as utils

        csv = b"DATE,GAC,NOC\nMay-26,9.0,4.0\nJun-26,10.3,5.0\n"
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: csv)
        query = FederalReservePhiladelphiaManufacturingFetcher.transform_query(
            {"start_date": "2026-06-01", "end_date": "2026-06-30"}
        )
        result = FederalReservePhiladelphiaManufacturingFetcher.transform_data(
            query,
            FederalReservePhiladelphiaManufacturingFetcher.extract_data(query, None),
        )
        assert [r.date for r in result] == [date(2026, 6, 1)]
        assert result[0].model_dump()["GAC"] == 10.3

    def test_all_blank_row_drops(self, monkeypatch):
        """A survey month with no populated indicator value is dropped."""
        from openbb_federal_reserve.utils import philadelphia as utils

        csv = b"DATE,GAC,NOC\nMay-26,,\nJun-26,10.3,5.0\n"
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: csv)
        query = FederalReservePhiladelphiaManufacturingFetcher.transform_query({})
        result = FederalReservePhiladelphiaManufacturingFetcher.transform_data(
            query,
            FederalReservePhiladelphiaManufacturingFetcher.extract_data(query, None),
        )
        assert [r.date for r in result] == [date(2026, 6, 1)]

    def test_empty_raises(self, monkeypatch):
        """An empty download raises ``EmptyDataError``."""
        from openbb_federal_reserve.utils import philadelphia as utils

        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: b"")
        query = FederalReservePhiladelphiaManufacturingFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReservePhiladelphiaManufacturingFetcher.extract_data(query, None)


class TestNonmanufacturingOutlook:
    """Tests for the Nonmanufacturing Business Outlook (NBOS) fetcher."""

    def test_decodes_sa_responses_and_diffusion(self, monkeypatch):
        """The SA sheet decodes diffusion and response codes into wide columns."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook(
            "Responses_and_diffusion",
            [
                ["date", "garbndif_sa", "garbninc_sa", "gabndif_sa"],
                ["2026-06-01", -25.8, 12.0, 3.0],
            ],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaNonmanufacturingFetcher.transform_query(
            {"adjustment": "sa", "start_date": "2026-01-01", "end_date": "2026-12-31"}
        )
        result = FederalReservePhiladelphiaNonmanufacturingFetcher.transform_data(
            query,
            FederalReservePhiladelphiaNonmanufacturingFetcher.extract_data(query, None),
        )
        assert all(
            isinstance(r, FederalReservePhiladelphiaNonmanufacturingData)
            for r in result
        )
        assert len(result) == 1
        wide = result[0].model_dump()
        assert result[0].date == date(2026, 6, 1)
        assert wide["General Activity (Region) - Current - diffusion index"] == -25.8
        assert wide["General Activity (Region) - Current - increase"] == 12.0
        assert wide["General Activity (Firm) - Current - diffusion index"] == 3.0

    def test_nsa_sheet_and_wide_label(self, monkeypatch):
        """The NSA sheet is read and the decoded series becomes a wide column."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook(
            "NSA",
            [
                ["date", "nobndec"],
                ["2026-06-01", 7.5],
            ],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaNonmanufacturingFetcher.transform_query(
            {"adjustment": "nsa"}
        )
        result = FederalReservePhiladelphiaNonmanufacturingFetcher.transform_data(
            query,
            FederalReservePhiladelphiaNonmanufacturingFetcher.extract_data(query, None),
        )
        assert len(result) == 1
        assert result[0].model_dump()["New Orders - Current - decrease"] == 7.5

    def test_future_horizon_skips_unknown_and_filters_dates(self, monkeypatch):
        """A future-horizon code decodes, an unknown column drops, and dates filter."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook(
            "Responses_and_diffusion",
            [
                ["date", "garfbninc", "junkcol", "xyzbndif"],
                ["2026-05-01", 9.0, 1.0, 5.0],
                ["2026-06-01", 12.0, 2.0, 6.0],
                ["2026-07-01", 15.0, 3.0, 7.0],
            ],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaNonmanufacturingFetcher.transform_query(
            {"adjustment": "sa", "start_date": "2026-06-01", "end_date": "2026-06-30"}
        )
        result = FederalReservePhiladelphiaNonmanufacturingFetcher.transform_data(
            query,
            FederalReservePhiladelphiaNonmanufacturingFetcher.extract_data(query, None),
        )
        assert len(result) == 1
        assert result[0].date == date(2026, 6, 1)
        wide = result[0].model_dump()
        label = "General Activity (Region) - Expectations (Six Months Ahead) - increase"
        assert wide[label] == 12.0
        assert "junkcol" not in wide

    def test_empty_raises(self, monkeypatch):
        """An empty download raises ``EmptyDataError``."""
        from openbb_federal_reserve.utils import philadelphia as utils

        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: b"")
        query = FederalReservePhiladelphiaNonmanufacturingFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReservePhiladelphiaNonmanufacturingFetcher.extract_data(query, None)


class TestTermStructureInflation:
    """Tests for the ATSIX term-structure fetcher."""

    def test_horizons_pivot_to_wide_raw(self, monkeypatch):
        """Horizon columns pivot to wide ``N Months`` columns with raw values."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook(
            "InfExp",
            [
                ["_date_", "infexp3", "infexp12"],
                ["2026-05-01", 2.1049, 2.46],
            ],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaAtsixFetcher.transform_query(
            {"start_date": "2026-01-01", "end_date": "2026-12-31"}
        )
        result = FederalReservePhiladelphiaAtsixFetcher.transform_data(
            query, FederalReservePhiladelphiaAtsixFetcher.extract_data(query, None)
        )
        assert all(isinstance(r, FederalReservePhiladelphiaAtsixData) for r in result)
        assert result[0].date == date(2026, 5, 1)
        wide = result[0].model_dump()
        assert wide["3 Months"] == 2.1049
        assert wide["12 Months"] == 2.46

    def test_real_dataset(self, monkeypatch):
        """The real-rate dataset reads the ``Real`` sheet's ``real`` columns."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook(
            "Real",
            [["_date_", "real3", "real12"], ["2026-05-01", 3.2, 3.0]],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaAtsixFetcher.transform_query(
            {"dataset": "real"}
        )
        result = FederalReservePhiladelphiaAtsixFetcher.transform_data(
            query, FederalReservePhiladelphiaAtsixFetcher.extract_data(query, None)
        )
        wide = result[0].model_dump()
        assert wide["3 Months"] == 3.2
        assert wide["12 Months"] == 3.0

    def test_factors_dataset(self, monkeypatch):
        """The factors dataset pivots the named Nelson-Siegel factor columns."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook(
            "Factors",
            [
                ["_date_", "level", "slope", "curvature", "lambda"],
                ["2026-05-01", 2.3, -0.3, 0.2, 0.12],
            ],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaAtsixFetcher.transform_query(
            {"dataset": "factors"}
        )
        result = FederalReservePhiladelphiaAtsixFetcher.transform_data(
            query, FederalReservePhiladelphiaAtsixFetcher.extract_data(query, None)
        )
        assert len(result) == 1
        wide = result[0].model_dump()
        assert wide["level"] == 2.3
        assert wide["slope"] == -0.3
        assert wide["curvature"] == 0.2
        assert wide["lambda"] == 0.12

    def test_drops_all_none_rows(self, monkeypatch):
        """A vintage month with no populated horizon is dropped from the wide rows."""
        from openbb_federal_reserve.utils import philadelphia as utils

        book = _workbook(
            "InfExp",
            [
                ["_date_", "infexp3", "infexp12"],
                ["2026-04-01", None, None],
                ["2026-05-01", 2.1, 2.46],
            ],
        )
        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: book)
        query = FederalReservePhiladelphiaAtsixFetcher.transform_query({})
        result = FederalReservePhiladelphiaAtsixFetcher.transform_data(
            query, FederalReservePhiladelphiaAtsixFetcher.extract_data(query, None)
        )
        assert [r.date for r in result] == [date(2026, 5, 1)]

    def test_empty_raises(self, monkeypatch):
        """An empty download raises ``EmptyDataError``."""
        from openbb_federal_reserve.utils import philadelphia as utils

        monkeypatch.setattr(utils, "fetch_philadelphia", lambda *a, **k: b"")
        query = FederalReservePhiladelphiaAtsixFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReservePhiladelphiaAtsixFetcher.extract_data(query, None)


class TestFetchPhiladelphiaHelper:
    """Tests for the shared download and parsing helpers."""

    def test_html_error_page_raises(self, monkeypatch):
        """An HTML page served as 200 raises ``OpenBBError`` rather than parsing."""
        from unittest.mock import MagicMock

        from openbb_federal_reserve.utils import philadelphia as utils

        response = MagicMock()
        response.content = b"\r\n<!DOCTYPE html><html></html>"
        response.raise_for_status = MagicMock()
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", lambda *a, **k: response
        )
        with pytest.raises(OpenBBError):
            utils.fetch_philadelphia("https://x/bad.xlsx", "bad", "monthly")

    def test_success_path_returns_content(self, monkeypatch):
        """A spreadsheet payload served as 200 is returned and cached."""
        from unittest.mock import MagicMock

        from openbb_federal_reserve.utils import philadelphia as utils

        response = MagicMock()
        response.content = b"PK\x03\x04 fake workbook"
        response.raise_for_status = MagicMock()
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", lambda *a, **k: response
        )
        out = utils.fetch_philadelphia("https://x/good.xlsx", "good", "monthly")
        assert out == b"PK\x03\x04 fake workbook"

    def test_xls_path_uses_default_engine(self):
        """Non-ZIP content routes through the default engine via ``read_workbook``."""
        import pandas
        from pandas import DataFrame

        from openbb_federal_reserve.utils import philadelphia as utils

        called = {}

        def _fake_read_excel(buffer, **kwargs):
            called.update(kwargs)
            return DataFrame({"Date": [date(2026, 1, 1)]})

        original = pandas.read_excel
        pandas.read_excel = _fake_read_excel
        try:
            utils.read_workbook(b"\xd0\xcf\x11\xe0legacy-xls", "Indexes")
        finally:
            pandas.read_excel = original
        assert "engine" not in called
        assert called["sheet_name"] == "Indexes"
