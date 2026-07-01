"""Tests for the St. Louis Fed regional models."""

from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.st_louis_fred_panel import (
    FederalReserveStLouisFredMdData,
    FederalReserveStLouisFredMdFetcher,
    FederalReserveStLouisFredQdData,
    FederalReserveStLouisFredQdFetcher,
)
from openbb_federal_reserve.models.regional.st_louis_indexes import (
    FederalReserveStLouisNationalIndexData,
    FederalReserveStLouisNationalIndexFetcher,
)
from openbb_federal_reserve.regional import st_louis

_FRED_MD = (
    "sasdate,INDPRO,UNRATE\nTransform:,5,2\n1/1/2026,102.5,4.0\n2/1/2026,103.1,.\n"
)

_FRED_QD = (
    "sasdate,GDPC1,PCECC96\nfactors,0,0\ntransform,5,5\n3/1/2026,23000.1,16000.2\n,,\n"
)

_FRED_MD_GAPS = (
    "sasdate,INDPRO,UNRATE\n"
    "Transform:,5,2\n"
    "1/1/2026,.,.\n"
    "2/1/2026,.,4.1\n"
    "3/1/2026,103.1,4.0\n"
)

_FRED_MD_ALL_NONE = (
    "sasdate,INDPRO,UNRATE\nTransform:,5,2\n1/1/2026,.,.\n2/1/2026,.,.\n"
)

_FRED_QD_ALL_NONE = "sasdate,GDPC1,PCECC96\nfactors,0,0\ntransform,5,5\n3/1/2026,.,.\n"

_FRED_MD_TRANSFORMS = (
    "sasdate,C1,C2,C3,C4,C5,C6,C7,CBAD\n"
    "Transform:,1,2,3,4,5,6,7,xx\n"
    "1/1/2026,100,100,100,100,100,100,100,1\n"
    "2/1/2026,110,110,110,110,110,110,110,2\n"
    "3/1/2026,121,121,121,121,121,121,121,3\n"
)

_FREDGRAPH = "observation_date,STLFSI4\n2026-06-12,-0.95\n2026-06-19,.\n"


class TestFredMd:
    """Tests for the FRED-MD panel fetcher."""

    def test_drops_transform_pivots_and_filters(self, monkeypatch):
        """The ``Transform:`` row drops, the panel pivots wide, series filter applies.

        The 2/1/2026 row is ``.`` for the only requested series, so it is an
        all-None value row and is dropped.
        """
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.st_louis.fetch_fred_panel",
            lambda freq: _FRED_MD,
        )
        query = FederalReserveStLouisFredMdFetcher.transform_query({"series": "UNRATE"})
        rows = FederalReserveStLouisFredMdFetcher.extract_data(query, None)
        result = FederalReserveStLouisFredMdFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveStLouisFredMdData) for r in result)
        assert len(result) == 1
        first = result[0].model_dump()
        assert set(first) == {"date", "UNRATE"}
        assert result[0].date == date(2026, 1, 1)
        assert first["UNRATE"] == 4.0

    def test_drops_all_none_rows_keeps_partial(self, monkeypatch):
        """All-None value rows drop; a row with one populated series is kept."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.st_louis.fetch_fred_panel",
            lambda freq: _FRED_MD_GAPS,
        )
        query = FederalReserveStLouisFredMdFetcher.transform_query({})
        rows = FederalReserveStLouisFredMdFetcher.extract_data(query, None)
        result = FederalReserveStLouisFredMdFetcher.transform_data(query, rows)
        dates = [r.date for r in result]
        # 1/1/2026 (both ``.``) drops; 2/1/2026 (UNRATE only) and 3/1/2026 keep.
        assert dates == [date(2026, 2, 1), date(2026, 3, 1)]
        partial = result[0].model_dump()
        assert partial["INDPRO"] is None
        assert partial["UNRATE"] == 4.1

    def test_all_none_raises(self, monkeypatch):
        """A panel whose value rows are all None raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.st_louis.fetch_fred_panel",
            lambda freq: _FRED_MD_ALL_NONE,
        )
        query = FederalReserveStLouisFredMdFetcher.transform_query({})
        rows = FederalReserveStLouisFredMdFetcher.extract_data(query, None)
        with pytest.raises(EmptyDataError):
            FederalReserveStLouisFredMdFetcher.transform_data(query, rows)

    def test_all_series_and_date_filters(self, monkeypatch):
        """Without a series filter every column becomes a row field; dates filter."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.st_louis.fetch_fred_panel",
            lambda freq: _FRED_MD,
        )
        query = FederalReserveStLouisFredMdFetcher.transform_query(
            {"start_date": "2026-01-01", "end_date": "2026-01-31"}
        )
        rows = FederalReserveStLouisFredMdFetcher.extract_data(query, None)
        result = FederalReserveStLouisFredMdFetcher.transform_data(query, rows)
        assert len(result) == 1
        row = result[0].model_dump()
        assert set(row) == {"date", "INDPRO", "UNRATE"}
        assert result[0].date == date(2026, 1, 1)

    def test_applies_every_transform_code(self, monkeypatch):
        """``transform=True`` applies each stationarity code 1-7; bad codes pass through."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.st_louis.fetch_fred_panel",
            lambda freq: _FRED_MD_TRANSFORMS,
        )
        query = FederalReserveStLouisFredMdFetcher.transform_query({"transform": True})
        rows = FederalReserveStLouisFredMdFetcher.extract_data(query, None)
        result = FederalReserveStLouisFredMdFetcher.transform_data(query, rows)
        latest = next(r for r in result if r.date == date(2026, 3, 1)).model_dump()
        # Code 1 (level) is unchanged; code 2 (first difference) is 121 - 110.
        assert latest["C1"] == 121.0
        assert latest["C2"] == pytest.approx(11.0)
        # Code 4 (log level) is log(121); code 7 carries a finite value.
        from math import log

        assert latest["C4"] == pytest.approx(log(121))
        assert latest["C7"] is not None
        # A non-numeric transform code leaves the series untransformed.
        assert latest["CBAD"] == 3.0

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.st_louis.fetch_fred_panel",
            lambda freq: "",
        )
        query = FederalReserveStLouisFredMdFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveStLouisFredMdFetcher.extract_data(query, None)


class TestFredQd:
    """Tests for the FRED-QD panel fetcher."""

    def test_drops_two_rows_and_blank_dates(self, monkeypatch):
        """Both header rows and the trailing blank-date row drop."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.st_louis.fetch_fred_panel",
            lambda freq: _FRED_QD,
        )
        query = FederalReserveStLouisFredQdFetcher.transform_query({"series": "GDPC1"})
        rows = FederalReserveStLouisFredQdFetcher.extract_data(query, None)
        result = FederalReserveStLouisFredQdFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveStLouisFredQdData) for r in result)
        assert len(result) == 1
        row = result[0].model_dump()
        assert set(row) == {"date", "GDPC1"}
        assert result[0].date == date(2026, 3, 1)
        assert row["GDPC1"] == 23000.1

    def test_all_none_raises(self, monkeypatch):
        """A panel whose value rows are all None raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.st_louis.fetch_fred_panel",
            lambda freq: _FRED_QD_ALL_NONE,
        )
        query = FederalReserveStLouisFredQdFetcher.transform_query({})
        rows = FederalReserveStLouisFredQdFetcher.extract_data(query, None)
        with pytest.raises(EmptyDataError):
            FederalReserveStLouisFredQdFetcher.transform_data(query, rows)

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.st_louis.fetch_fred_panel",
            lambda freq: "",
        )
        query = FederalReserveStLouisFredQdFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveStLouisFredQdFetcher.extract_data(query, None)


class TestNationalIndex:
    """Tests for the national index fetcher."""

    def test_parses_and_filters(self, monkeypatch):
        """The two-column CSV parses, ``.`` is missing, and dates filter."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.st_louis.fetch_fred_graph_csv",
            lambda sid: _FREDGRAPH,
        )
        query = FederalReserveStLouisNationalIndexFetcher.transform_query(
            {"index": "financial_stress_index", "start_date": "2026-06-15"}
        )
        rows = FederalReserveStLouisNationalIndexFetcher.extract_data(query, None)
        result = FederalReserveStLouisNationalIndexFetcher.transform_data(query, rows)
        assert all(
            isinstance(r, FederalReserveStLouisNationalIndexData) for r in result
        )
        assert len(result) == 1
        assert result[0].date == date(2026, 6, 19)
        assert result[0].index == "financial_stress_index"
        assert result[0].value is None

    def test_end_date_filter(self, monkeypatch):
        """The end_date filter returns earlier observations only."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.st_louis.fetch_fred_graph_csv",
            lambda sid: _FREDGRAPH,
        )
        query = FederalReserveStLouisNationalIndexFetcher.transform_query(
            {"index": "price_pressures", "end_date": "2026-06-12"}
        )
        rows = FederalReserveStLouisNationalIndexFetcher.extract_data(query, None)
        result = FederalReserveStLouisNationalIndexFetcher.transform_data(query, rows)
        assert len(result) == 1
        assert result[0].value == -0.95

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.st_louis.fetch_fred_graph_csv",
            lambda sid: "",
        )
        query = FederalReserveStLouisNationalIndexFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveStLouisNationalIndexFetcher.extract_data(query, None)


def _load_st_louis_module():
    """Re-execute the St. Louis subrouter with ``Router.command`` stubbed.

    The model-backed commands bind only when their fetchers are registered in
    the live provider registry; replacing ``Router.command`` with a passthrough
    lets them bind unconditionally so their bodies can be exercised in isolation.
    """
    import importlib.util
    from pathlib import Path

    from openbb_core.app.router import Router

    spec = importlib.util.spec_from_file_location(
        "openbb_federal_reserve_st_louis_standalone", Path(st_louis.__file__)
    )
    module = importlib.util.module_from_spec(spec)
    original_command = Router.command

    def _passthrough_command(self, func=None, **_kwargs):
        """Bind ``func`` without touching the underlying FastAPI router."""
        if func is None:
            return lambda f: _passthrough_command(self, f, **_kwargs)
        return func

    Router.command = _passthrough_command
    try:
        spec.loader.exec_module(module)
    finally:
        Router.command = original_command
    return module


class TestModelCommandBodies:
    """Each model-backed command delegates to ``OBBject.from_query``."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "name", ["fred_md", "fred_qd", "national_index", "publications"]
    )
    async def test_delegates_to_from_query(self, name):
        """The command awaits ``OBBject.from_query``."""
        from unittest.mock import AsyncMock, MagicMock, patch

        module = _load_st_louis_module()
        sentinel = object()
        with (
            patch.object(module, "Query", new=MagicMock()),
            patch.object(
                module.OBBject, "from_query", new=AsyncMock(return_value=sentinel)
            ) as mock_from_query,
        ):
            out = await getattr(module, name)(
                cc=MagicMock(),
                provider_choices=MagicMock(),
                standard_params=MagicMock(),
                extra_params=MagicMock(),
            )
        assert out is sentinel
        mock_from_query.assert_awaited_once()
