"""Unit tests for the Federal Reserve inflation expectations model."""

# ruff: noqa: I001

from datetime import date as dateType
from io import BytesIO

import pytest
from openpyxl import Workbook

from openbb_core.app.model.abstract.error import OpenBBError
import openbb_federal_reserve.models.inflation_expectations as mod
from openbb_federal_reserve.models.inflation_expectations import (
    FederalReserveInflationExpectationsData,
    FederalReserveInflationExpectationsFetcher,
    FederalReserveInflationExpectationsQueryParams,
)


def _make_xlsx(rows: list[list]) -> bytes:
    """Build an in-memory INFLATION workbook with the given data rows."""
    wb = Workbook()
    ws = wb.active
    ws.title = "INFLATION"
    ws.append(["YEAR", "QUARTER", "INFPGDP1YR", "INFCPI1YR", "INFCPI10YR"])
    for row in rows:
        ws.append(row)
    bio = BytesIO()
    wb.save(bio)
    return bio.getvalue()


def _sample_file() -> dict:
    """Return a ``{"file": ...}`` payload with a representative sample."""
    return {
        "file": _make_xlsx(
            [
                [1970, 2, 4.5, "#N/A", "#N/A"],
                [1981, 3, 8.1, 9.2, "#N/A"],
                [2020, 1, 1.5, 1.8, 2.0],
                [2021, 4, None, None, None],
            ]
        )
    }


class TestQueryParams:
    """Tests for ``FederalReserveInflationExpectationsQueryParams``."""

    def test_defaults_are_none(self):
        """Both date bounds default to ``None``."""
        q = FederalReserveInflationExpectationsQueryParams()
        assert q.start_date is None
        assert q.end_date is None

    def test_transform_query_builds_params(self):
        """``transform_query`` constructs the params model from a dict."""
        q = FederalReserveInflationExpectationsFetcher.transform_query(
            {"start_date": dateType(2000, 1, 1), "end_date": dateType(2020, 12, 31)}
        )
        assert isinstance(q, FederalReserveInflationExpectationsQueryParams)
        assert q.start_date == dateType(2000, 1, 1)
        assert q.end_date == dateType(2020, 12, 31)


class TestDownloadInflationExcel:
    """Tests for the cached ``download_inflation_excel`` helper."""

    def test_returns_response_content(self, monkeypatch):
        """The helper returns the raw response content after a status check."""
        from openbb_core.provider.utils import helpers

        raised: dict = {}

        class _Resp:
            content = b"EXCEL-BYTES"

            def raise_for_status(self):
                """Record that the status check ran."""
                raised["checked"] = True

        monkeypatch.setattr(helpers, "make_request", lambda *a, **k: _Resp())
        out = mod.download_inflation_excel.__wrapped__()
        assert out == b"EXCEL-BYTES"
        assert raised["checked"] is True

    def test_propagates_http_error(self, monkeypatch):
        """A non-success status surfaces via ``raise_for_status``."""
        from openbb_core.provider.utils import helpers

        class _Resp:
            content = b""

            def raise_for_status(self):
                """Simulate an HTTP error."""
                raise RuntimeError("404")

        monkeypatch.setattr(helpers, "make_request", lambda *a, **k: _Resp())
        with pytest.raises(RuntimeError, match="404"):
            mod.download_inflation_excel.__wrapped__()


class TestExtractData:
    """Tests for ``FederalReserveInflationExpectationsFetcher.extract_data``."""

    def test_returns_downloaded_file(self, monkeypatch):
        """A successful download is wrapped under the ``file`` key."""
        monkeypatch.setattr(mod, "download_inflation_excel", lambda *a, **k: b"XYZ")
        out = FederalReserveInflationExpectationsFetcher.extract_data(
            FederalReserveInflationExpectationsQueryParams(), None
        )
        assert out == {"file": b"XYZ"}

    def test_download_error_wraps_to_openbb_error(self, monkeypatch):
        """A download failure is re-raised as ``OpenBBError``."""

        def _boom(*_a, **_k):
            """Raise to simulate a failed download."""
            raise RuntimeError("network down")

        monkeypatch.setattr(mod, "download_inflation_excel", _boom)
        with pytest.raises(OpenBBError, match="network down"):
            FederalReserveInflationExpectationsFetcher.extract_data(
                FederalReserveInflationExpectationsQueryParams(), None
            )


class TestTransformData:
    """Tests for ``FederalReserveInflationExpectationsFetcher.transform_data``."""

    def test_parses_rows_and_maps_quarters(self):
        """Year/quarter pairs map to the first month of each survey quarter."""
        q = FederalReserveInflationExpectationsQueryParams()
        out = FederalReserveInflationExpectationsFetcher.transform_data(
            q, _sample_file()
        )
        by_date = {r.date: r for r in out}
        assert dateType(1970, 4, 1) in by_date
        assert dateType(1981, 7, 1) in by_date
        assert dateType(2020, 1, 1) in by_date

    def test_na_values_become_none(self):
        """``#N/A`` cells are coerced to ``None``."""
        q = FederalReserveInflationExpectationsQueryParams()
        out = FederalReserveInflationExpectationsFetcher.transform_data(
            q, _sample_file()
        )
        row_1970 = next(r for r in out if r.date == dateType(1970, 4, 1))
        assert row_1970.infpgdp1yr == 4.5
        assert row_1970.infcpi1yr is None
        assert row_1970.infcpi10yr is None

    def test_all_none_rows_dropped(self):
        """Rows where every forecast is missing are dropped."""
        q = FederalReserveInflationExpectationsQueryParams()
        out = FederalReserveInflationExpectationsFetcher.transform_data(
            q, _sample_file()
        )
        assert dateType(2021, 10, 1) not in {r.date for r in out}

    def test_results_sorted_ascending(self):
        """Output rows are sorted ascending by date."""
        q = FederalReserveInflationExpectationsQueryParams()
        out = FederalReserveInflationExpectationsFetcher.transform_data(
            q, _sample_file()
        )
        dates = [r.date for r in out]
        assert dates == sorted(dates)

    def test_start_date_filter(self):
        """``start_date`` excludes earlier survey quarters."""
        q = FederalReserveInflationExpectationsQueryParams(
            start_date=dateType(2000, 1, 1)
        )
        out = FederalReserveInflationExpectationsFetcher.transform_data(
            q, _sample_file()
        )
        assert [r.date for r in out] == [dateType(2020, 1, 1)]

    def test_end_date_filter(self):
        """``end_date`` excludes later survey quarters."""
        q = FederalReserveInflationExpectationsQueryParams(
            end_date=dateType(1981, 12, 31)
        )
        out = FederalReserveInflationExpectationsFetcher.transform_data(
            q, _sample_file()
        )
        assert {r.date for r in out} == {dateType(1970, 4, 1), dateType(1981, 7, 1)}

    def test_empty_after_filter_raises(self):
        """Filtering out every row raises ``OpenBBError``."""
        q = FederalReserveInflationExpectationsQueryParams(
            start_date=dateType(2099, 1, 1)
        )
        with pytest.raises(OpenBBError, match="resulted in no data"):
            FederalReserveInflationExpectationsFetcher.transform_data(q, _sample_file())


class TestData:
    """Tests for the ``FederalReserveInflationExpectationsData`` model."""

    def test_validates_and_defaults(self):
        """Optional forecast fields default to ``None``."""
        d = FederalReserveInflationExpectationsData.model_validate(
            {"date": dateType(2020, 1, 1)}
        )
        assert d.date == dateType(2020, 1, 1)
        assert d.infpgdp1yr is None
        assert d.infcpi1yr is None
        assert d.infcpi10yr is None
