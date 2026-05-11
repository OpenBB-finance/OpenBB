"""Unit tests for openbb_oecd.models.economic_indicators."""

from __future__ import annotations

import datetime as _dt
from math import nan
from unittest.mock import patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_oecd.models.economic_indicators import (
    OecdEconomicIndicatorsData,
    OecdEconomicIndicatorsFetcher,
    OecdEconomicIndicatorsQueryParams,
    _apply_transform,
)

_FULL_ID = "DSD_TEST@DF_TEST"
_SHORT_ID = "DF_TEST"


class TestValidateCountry:
    """Branches in the country validator."""

    def test_none_passthrough(self, seeded_meta):
        """None country returns None."""
        q = OecdEconomicIndicatorsQueryParams(symbol=f"{_SHORT_ID}::CPI", country=None)
        assert q.country is None

    def test_normalizes_spaces_and_case(self, seeded_meta):
        """Spaces become underscores and value is lowercased."""
        q = OecdEconomicIndicatorsQueryParams(
            symbol=f"{_SHORT_ID}::CPI", country="United States"
        )
        assert q.country == "united_states"


class TestValidateDimensionValues:
    """Branches in the dimension_values validator."""

    def test_none_passthrough(self, seeded_meta):
        """None passes through unchanged."""
        q = OecdEconomicIndicatorsQueryParams(
            symbol=f"{_SHORT_ID}::CPI", dimension_values=None
        )
        assert q.dimension_values is None

    def test_string_split_into_list(self, seeded_meta):
        """Comma-separated string is split."""
        q = OecdEconomicIndicatorsQueryParams(
            symbol=f"{_SHORT_ID}::CPI",
            dimension_values="SECTOR:S1, UNIT:USD",
        )
        assert q.dimension_values == ["SECTOR:S1", "UNIT:USD"]

    def test_string_all_whitespace_yields_none(self, seeded_meta):
        """Whitespace-only input returns None."""
        q = OecdEconomicIndicatorsQueryParams(
            symbol=f"{_SHORT_ID}::CPI", dimension_values="   ,  "
        )
        assert q.dimension_values is None

    def test_list_input_coerced(self, seeded_meta):
        """Iterable input is converted to a list."""
        q = OecdEconomicIndicatorsQueryParams(
            symbol=f"{_SHORT_ID}::CPI",
            dimension_values=("SECTOR:S1",),
        )
        assert q.dimension_values == ["SECTOR:S1"]


class TestParseAndValidateSymbols:
    """Branches in the model_validator for symbol parsing."""

    def test_empty_symbol_raises(self, seeded_meta):
        """Empty string symbol raises ValueError."""
        with pytest.raises(ValueError, match="Symbol is required"):
            OecdEconomicIndicatorsQueryParams(symbol="")

    def test_bare_identifier_without_dataflow(self, seeded_meta):
        """Bare identifier (no '::') results in no dataflow and indicator codes only."""
        q = OecdEconomicIndicatorsQueryParams(symbol="LOOSE_CODE")
        assert q._dataflow is None
        assert q._indicator_codes == ["LOOSE_CODE"]

    def test_mixed_dataflows_raises(self, seeded_meta):
        """Two different dataflows in one symbol input is rejected."""
        with pytest.raises(ValueError, match="same dataflow"):
            OecdEconomicIndicatorsQueryParams(symbol="DF_A::X,DF_B::Y")

    def test_only_separators_raises(self, seeded_meta):
        """Symbol containing only commas/whitespace raises 'No valid symbols'."""
        with pytest.raises(ValueError, match="No valid symbols"):
            OecdEconomicIndicatorsQueryParams(symbol=" , , ")

    def test_table_mode_detected(self, seeded_meta, monkeypatch):
        """When the identifier matches a hierarchy table id, table mode is set."""
        from openbb_oecd.utils.metadata import OecdMetadata

        monkeypatch.setattr(
            OecdMetadata,
            "get_dataflow_hierarchies",
            lambda self, dataflow: [{"id": "T01", "name": "Table One"}],
        )
        q = OecdEconomicIndicatorsQueryParams(symbol=f"{_SHORT_ID}::T01")
        assert q._is_table is True
        assert q._table_id == "T01"
        assert q._dataflow == _SHORT_ID

    def test_indicator_mode_when_not_table(self, seeded_meta, monkeypatch):
        """When identifier is not a table id, indicator mode is used."""
        from openbb_oecd.utils.metadata import OecdMetadata

        monkeypatch.setattr(
            OecdMetadata, "get_dataflow_hierarchies", lambda self, dataflow: []
        )
        q = OecdEconomicIndicatorsQueryParams(symbol=f"{_SHORT_ID}::CPI")
        assert q._is_table is False
        assert q._indicator_codes == ["CPI"]
        assert q._indicators_by_dataflow == {_SHORT_ID: ["CPI"]}


class TestDataNanValidators:
    """Branches in the OecdEconomicIndicatorsData field validators."""

    def test_falsy_returns_none(self):
        """Empty string / 0 / None / False return None."""
        d = OecdEconomicIndicatorsData(
            date=_dt.date(2024, 1, 1),
            symbol="X",
            value=1.0,
            unit="",
            scale="",
        )
        assert d.unit is None
        assert d.scale is None

    def test_float_nan_returns_none(self):
        """A float NaN is converted to None by the field validator."""
        assert OecdEconomicIndicatorsData.nan_to_none(float("nan")) is None

    def test_string_nan_returns_none(self):
        """The string 'nan' returns None."""
        d = OecdEconomicIndicatorsData(
            date=_dt.date(2024, 1, 1),
            symbol="X",
            value=1.0,
            unit="NaN",
        )
        assert d.unit is None

    def test_extra_nan_replaced(self):
        """Extra/dynamic NaN fields are scrubbed to None."""
        d = OecdEconomicIndicatorsData.model_validate(
            {
                "date": _dt.date(2024, 1, 1),
                "symbol": "X",
                "value": 1.0,
                "extra_dyn": nan,
            }
        )
        dumped = d.model_dump()
        assert dumped["extra_dyn"] is None


class TestTransformQuery:
    """transform_query simply builds the params model."""

    def test_round_trip(self, seeded_meta):
        """transform_query returns a validated query model."""
        q = OecdEconomicIndicatorsFetcher.transform_query(
            {"symbol": f"{_SHORT_ID}::CPI"}
        )
        assert isinstance(q, OecdEconomicIndicatorsQueryParams)


def _build_query(monkeypatch, seeded_meta, **overrides):
    """Helper that builds a query while stubbing hierarchies to be empty."""
    from openbb_oecd.utils.metadata import OecdMetadata

    monkeypatch.setattr(
        OecdMetadata, "get_dataflow_hierarchies", lambda self, dataflow: []
    )
    params = {"symbol": f"{_SHORT_ID}::CPI"}
    params.update(overrides)
    return OecdEconomicIndicatorsQueryParams(**params)


class TestExtractDataDataflowRequired:
    """extract_data must reject queries without a dataflow."""

    def test_missing_dataflow_raises(self, seeded_meta):
        """A bare-identifier symbol has no dataflow -> OpenBBError."""
        query = OecdEconomicIndicatorsQueryParams(symbol="LOOSE")
        with pytest.raises(OpenBBError, match="dataflow"):
            OecdEconomicIndicatorsFetcher.extract_data(query=query, credentials=None)


class TestExtractDataIndicatorMode:
    """extract_data branches when running in indicator mode."""

    def test_dimension_values_parsed_and_applied(self, seeded_meta, monkeypatch):
        """User-specified dimension_values map to canonical DSD dim keys."""
        captured = {}

        class _StubQB:
            def __init__(self):
                self.metadata = seeded_meta

            def fetch_data(self, **kwargs):
                captured.update(kwargs)
                return {
                    "data": [
                        {
                            "TIME_PERIOD": "2024",
                            "OBS_VALUE": "1.0",
                            "REF_AREA": "USA",
                        }
                    ],
                    "metadata": {},
                }

        monkeypatch.setattr("openbb_oecd.utils.query_builder.OecdQueryBuilder", _StubQB)
        monkeypatch.setattr(
            "openbb_oecd.utils.helpers.detect_indicator_dimensions",
            lambda *a, **k: {"MEASURE": ["CPI", "PPI"]},
        )
        query = _build_query(
            monkeypatch,
            seeded_meta,
            country="united_states",
            frequency="annual",
            dimension_values=["measure:cpi"],
        )
        result = OecdEconomicIndicatorsFetcher.extract_data(
            query=query, credentials=None
        )
        assert captured["MEASURE"] == "CPI+PPI"
        assert captured.get("REF_AREA") == "USA"
        assert captured.get("FREQ") == "A"
        assert result["mode"] == "indicator"

    def test_invalid_dimension_keys_raise(self, seeded_meta, monkeypatch):
        """Invalid dim keys produce a clear OpenBBError."""

        class _StubQB:
            def __init__(self):
                self.metadata = seeded_meta

            def fetch_data(self, **kwargs):
                return {"data": []}

        monkeypatch.setattr("openbb_oecd.utils.query_builder.OecdQueryBuilder", _StubQB)
        query = _build_query(
            monkeypatch,
            seeded_meta,
            dimension_values=["NOPE:VAL"],
        )
        with pytest.raises(OpenBBError, match="Invalid dimension"):
            OecdEconomicIndicatorsFetcher.extract_data(query=query, credentials=None)

    def test_skips_non_string_dimension_value_entries(self, seeded_meta, monkeypatch):
        """Empty/non-string entries inside dimension_values are skipped."""

        class _StubQB:
            def __init__(self):
                self.metadata = seeded_meta

            def fetch_data(self, **kwargs):
                return {
                    "data": [{"TIME_PERIOD": "2024", "OBS_VALUE": "1.0"}],
                    "metadata": {},
                }

        monkeypatch.setattr("openbb_oecd.utils.query_builder.OecdQueryBuilder", _StubQB)
        monkeypatch.setattr(
            "openbb_oecd.utils.helpers.detect_indicator_dimensions",
            lambda *a, **k: {},
        )
        query = OecdEconomicIndicatorsQueryParams.model_construct(
            symbol=f"{_SHORT_ID}::CPI",
            dimension_values=["", None, "MEASURE:CPI"],
            pivot=False,
            country=None,
            frequency=None,
            transform=None,
            limit=None,
            start_date=None,
            end_date=None,
        )
        query._dataflow = _SHORT_ID
        query._is_table = False
        query._indicator_codes = ["CPI"]
        query._indicators_by_dataflow = {_SHORT_ID: ["CPI"]}
        out = OecdEconomicIndicatorsFetcher.extract_data(query=query, credentials=None)
        assert out["mode"] == "indicator"

    def test_transform_dispatched_in_indicator_mode(self, seeded_meta, monkeypatch):
        """A transform arg goes through _apply_transform in indicator mode."""
        captured = {}

        class _StubQB:
            def __init__(self):
                self.metadata = seeded_meta

            def fetch_data(self, **kwargs):
                captured.update(kwargs)
                return {
                    "data": [{"TIME_PERIOD": "2024", "OBS_VALUE": "1.0"}],
                    "metadata": {},
                }

        def _fake_detect_transform(df, *_a, **_k):
            return ("TRANSFORMATION", None, {"index": "IX"}, {})

        monkeypatch.setattr("openbb_oecd.utils.query_builder.OecdQueryBuilder", _StubQB)
        monkeypatch.setattr(
            "openbb_oecd.utils.helpers.detect_transform_dimension",
            _fake_detect_transform,
        )
        monkeypatch.setattr(
            "openbb_oecd.utils.helpers.detect_indicator_dimensions",
            lambda *a, **k: {},
        )
        query = _build_query(
            monkeypatch,
            seeded_meta,
            transform="index",
        )
        OecdEconomicIndicatorsFetcher.extract_data(query=query, credentials=None)
        assert captured.get("TRANSFORMATION") == "IX"

    def test_content_dims_fallback_on_metadata_error(self, seeded_meta, monkeypatch):
        """If get_dimension_order raises, content_dims defaults to empty list."""

        class _BrokenMeta:
            def resolve_country_codes(self, *_a, **_k):
                return []

            def get_dimension_order(self, *_a, **_k):
                raise RuntimeError("boom")

        class _StubQB:
            def __init__(self):
                self.metadata = _BrokenMeta()

            def fetch_data(self, **kwargs):
                return {
                    "data": [{"TIME_PERIOD": "2024", "OBS_VALUE": "1.0"}],
                    "metadata": {},
                }

        monkeypatch.setattr("openbb_oecd.utils.query_builder.OecdQueryBuilder", _StubQB)
        monkeypatch.setattr(
            "openbb_oecd.utils.helpers.detect_indicator_dimensions",
            lambda *a, **k: {},
        )
        query = _build_query(monkeypatch, seeded_meta)
        out = OecdEconomicIndicatorsFetcher.extract_data(query=query, credentials=None)
        assert out["content_dims"] == []

    def test_fetch_data_exception_wrapped(self, seeded_meta, monkeypatch):
        """An exception raised by fetch_data is wrapped in OpenBBError."""

        class _StubQB:
            def __init__(self):
                self.metadata = seeded_meta

            def fetch_data(self, **kwargs):
                raise RuntimeError("network exploded")

        monkeypatch.setattr("openbb_oecd.utils.query_builder.OecdQueryBuilder", _StubQB)
        monkeypatch.setattr(
            "openbb_oecd.utils.helpers.detect_indicator_dimensions",
            lambda *a, **k: {},
        )
        query = _build_query(monkeypatch, seeded_meta)
        with pytest.raises(OpenBBError, match="OECD data fetch failed"):
            OecdEconomicIndicatorsFetcher.extract_data(query=query, credentials=None)

    def test_empty_records_raises(self, seeded_meta, monkeypatch):
        """An empty data list yields EmptyDataError."""

        class _StubQB:
            def __init__(self):
                self.metadata = seeded_meta

            def fetch_data(self, **kwargs):
                return {"data": [], "metadata": {}}

        monkeypatch.setattr("openbb_oecd.utils.query_builder.OecdQueryBuilder", _StubQB)
        monkeypatch.setattr(
            "openbb_oecd.utils.helpers.detect_indicator_dimensions",
            lambda *a, **k: {},
        )
        query = _build_query(monkeypatch, seeded_meta)
        with pytest.raises(EmptyDataError):
            OecdEconomicIndicatorsFetcher.extract_data(query=query, credentials=None)


class TestExtractDataTableMode:
    """extract_data branches when running in table mode."""

    def test_table_mode_happy_path(self, seeded_meta, monkeypatch):
        """Table mode dispatches to OecdTableBuilder with all parsed params."""
        from openbb_oecd.utils.metadata import OecdMetadata

        monkeypatch.setattr(
            OecdMetadata,
            "get_dataflow_hierarchies",
            lambda self, dataflow: [{"id": "T01", "name": "Table One"}],
        )
        captured = {}

        class _StubTB:
            def get_table(self, **kwargs):
                captured.update(kwargs)
                return {
                    "data": [{"time_period": "2024", "value": 1.0}],
                    "table_metadata": {"fixed_dimensions": {}},
                    "structure": {"indicators": []},
                    "series_metadata": {},
                }

        monkeypatch.setattr("openbb_oecd.utils.table_builder.OecdTableBuilder", _StubTB)

        def _fake_detect_transform(df, *_a, **_k):
            return ("TRANSFORMATION", None, {"index": "IX"}, {})

        monkeypatch.setattr(
            "openbb_oecd.utils.helpers.detect_transform_dimension",
            _fake_detect_transform,
        )

        query = OecdEconomicIndicatorsQueryParams(
            symbol=f"{_SHORT_ID}::T01",
            country="united_states",
            frequency="annual",
            transform="index",
            dimension_values="SECTOR:S1",
        )
        out = OecdEconomicIndicatorsFetcher.extract_data(query=query, credentials=None)
        assert out["mode"] == "table"
        assert captured["REF_AREA"] == "USA"
        assert captured["FREQ"] == "A"
        assert captured["SECTOR"] == "S1"
        assert captured["TRANSFORMATION"] == "IX"
        assert captured["table_id"] == "T01"

    def test_table_mode_builder_error_wrapped(self, seeded_meta, monkeypatch):
        """OecdTableBuilder errors are re-raised as OpenBBError."""
        from openbb_oecd.utils.metadata import OecdMetadata

        monkeypatch.setattr(
            OecdMetadata,
            "get_dataflow_hierarchies",
            lambda self, dataflow: [{"id": "T01", "name": "Table One"}],
        )

        class _BoomTB:
            def get_table(self, **kwargs):
                raise ValueError("bad table")

        monkeypatch.setattr("openbb_oecd.utils.table_builder.OecdTableBuilder", _BoomTB)
        query = OecdEconomicIndicatorsQueryParams(symbol=f"{_SHORT_ID}::T01")
        with pytest.raises(OpenBBError, match="bad table"):
            OecdEconomicIndicatorsFetcher.extract_data(query=query, credentials=None)


class TestTransformDataIndicatorMode:
    """transform_data branches for indicator mode results."""

    def _q(self, **overrides):
        """Build a minimal validated query without metadata lookups."""
        q = OecdEconomicIndicatorsQueryParams.model_construct(
            symbol=f"{_SHORT_ID}::CPI",
            country=None,
            frequency=None,
            transform=None,
            dimension_values=None,
            limit=None,
            start_date=overrides.pop("start_date", None),
            end_date=overrides.pop("end_date", None),
            pivot=overrides.pop("pivot", False),
        )
        q._dataflow = _SHORT_ID
        q._is_table = False
        q._indicator_codes = ["CPI"]
        return q

    def test_empty_rows_raise(self):
        """An entirely empty data dict raises EmptyDataError immediately."""
        with pytest.raises(EmptyDataError, match="No data returned"):
            OecdEconomicIndicatorsFetcher.transform_data(
                query=self._q(), data={"mode": "indicator", "data": []}
            )

    def test_skips_unparsable_dates(self):
        """Rows without a parsable TIME_PERIOD are skipped."""
        data = {
            "mode": "indicator",
            "data": [
                {"TIME_PERIOD": "", "OBS_VALUE": "1.0"},
                {"TIME_PERIOD": "2024", "OBS_VALUE": "2.0"},
            ],
            "metadata": {},
            "content_dims": [],
        }
        out = OecdEconomicIndicatorsFetcher.transform_data(query=self._q(), data=data)
        assert len(out.result) == 1

    def test_start_date_filter_drops_old_rows(self):
        """Rows older than start_date are filtered out."""
        data = {
            "mode": "indicator",
            "data": [
                {"TIME_PERIOD": "2010", "OBS_VALUE": "1.0"},
                {"TIME_PERIOD": "2024", "OBS_VALUE": "2.0"},
            ],
            "metadata": {},
            "content_dims": [],
        }
        out = OecdEconomicIndicatorsFetcher.transform_data(
            query=self._q(start_date=_dt.date(2020, 1, 1)),
            data=data,
        )
        assert len(out.result) == 1
        assert out.result[0].date.year == 2024

    def test_end_date_filter_drops_future_rows(self):
        """Rows newer than end_date are filtered out."""
        data = {
            "mode": "indicator",
            "data": [
                {"TIME_PERIOD": "2010", "OBS_VALUE": "1.0"},
                {"TIME_PERIOD": "2024", "OBS_VALUE": "2.0"},
            ],
            "metadata": {},
            "content_dims": [],
        }
        out = OecdEconomicIndicatorsFetcher.transform_data(
            query=self._q(end_date=_dt.date(2015, 1, 1)),
            data=data,
        )
        assert len(out.result) == 1
        assert out.result[0].date.year == 2010

    def test_missing_or_nan_values_skipped(self):
        """OBS_VALUE empty/None/'nan' and non-numeric strings are skipped."""
        data = {
            "mode": "indicator",
            "data": [
                {"TIME_PERIOD": "2024", "OBS_VALUE": ""},
                {"TIME_PERIOD": "2024", "OBS_VALUE": None},
                {"TIME_PERIOD": "2024", "OBS_VALUE": "nan"},
                {"TIME_PERIOD": "2024", "OBS_VALUE": "not-a-number"},
                {"TIME_PERIOD": "2024", "OBS_VALUE": "1.5"},
            ],
            "metadata": {},
            "content_dims": [],
        }
        out = OecdEconomicIndicatorsFetcher.transform_data(query=self._q(), data=data)
        assert len(out.result) == 1

    def test_all_rows_filtered_raises(self):
        """When every row is filtered out, EmptyDataError mentions date filters."""
        data = {
            "mode": "indicator",
            "data": [{"TIME_PERIOD": "", "OBS_VALUE": "1.0"}],
            "metadata": {},
            "content_dims": [],
        }
        with pytest.raises(EmptyDataError, match="No data remaining"):
            OecdEconomicIndicatorsFetcher.transform_data(query=self._q(), data=data)

    def test_skip_title_dims_and_skip_values(self):
        """Labels that are skip values or skip dim ids do not enter the title."""
        data = {
            "mode": "indicator",
            "data": [
                {
                    "TIME_PERIOD": "2024",
                    "OBS_VALUE": "1.0",
                    "REF_AREA": "USA",
                    "REF_AREA_label": "United States",
                    "MEASURE": "CPI",
                    "MEASURE_label": "Consumer Price Index",
                    "SECTOR": "_Z",
                    "SECTOR_label": "Not applicable",
                    "UNIT_MEASURE": "IX",
                    "UNIT_MEASURE_label": "Index",
                    "UNIT_MULT_label": "Units",
                }
            ],
            "metadata": {},
            "content_dims": ["MEASURE"],
        }
        out = OecdEconomicIndicatorsFetcher.transform_data(query=self._q(), data=data)
        assert len(out.result) == 1
        row = out.result[0]
        assert "Not applicable" not in (row.title or "")
        assert row.title == "Consumer Price Index"

    def test_nan_string_unit_and_scale_become_none(self):
        """String 'nan' values for unit/scale labels are dropped."""
        data = {
            "mode": "indicator",
            "data": [
                {
                    "TIME_PERIOD": "2024",
                    "OBS_VALUE": "1.0",
                    "REF_AREA": "USA",
                    "UNIT_MEASURE_label": "nan",
                    "UNIT_MULT_label": "nan",
                }
            ],
            "metadata": {},
            "content_dims": [],
        }
        out = OecdEconomicIndicatorsFetcher.transform_data(query=self._q(), data=data)
        assert out.result[0].unit is None
        assert out.result[0].scale is None


class TestTransformDataTableMode:
    """transform_data branches for table mode results."""

    def _q(self, **overrides):
        """Build a minimal table-mode query."""
        q = OecdEconomicIndicatorsQueryParams.model_construct(
            symbol=f"{_SHORT_ID}::T01",
            country=None,
            frequency=None,
            transform=None,
            dimension_values=None,
            limit=None,
            start_date=overrides.pop("start_date", None),
            end_date=overrides.pop("end_date", None),
            pivot=overrides.pop("pivot", False),
        )
        q._dataflow = _SHORT_ID
        q._is_table = True
        q._table_id = "T01"
        return q

    def test_basic_row(self):
        """A single table-mode row is mapped to the output model."""
        data = {
            "mode": "table",
            "data": [
                {
                    "time_period": "2024",
                    "code": "X",
                    "value": 1.0,
                    "ref_area": "USA",
                    "unit_measure": "IX",
                    "unit_mult": 0,
                    "scale": None,
                    "order": 1,
                    "level": 0,
                    "parent_code": None,
                    "label": "Indicator X",
                    "description": "Desc",
                }
            ],
            "table_metadata": {"fixed_dimensions": {}},
            "structure": {"indicators": []},
            "series_metadata": {},
        }
        out = OecdEconomicIndicatorsFetcher.transform_data(query=self._q(), data=data)
        assert len(out.result) == 1
        assert out.result[0].country == "USA"

    def test_fixed_country_pulled_from_metadata(self):
        """When REF_AREA is a fixed dimension, country is filled from metadata."""
        data = {
            "mode": "table",
            "data": [
                {
                    "time_period": "2024",
                    "code": "X",
                    "value": 1.0,
                    "order": 1,
                }
            ],
            "table_metadata": {
                "fixed_dimensions": {
                    "REF_AREA": {"label": "United States", "code": "USA"}
                }
            },
            "structure": {"indicators": []},
            "series_metadata": {},
        }
        out = OecdEconomicIndicatorsFetcher.transform_data(query=self._q(), data=data)
        assert out.result[0].country == "United States"
        assert out.result[0].country_code == "USA"

    def test_order_to_code_fallback(self):
        """Rows without 'code' fall back to the structure's order map."""
        data = {
            "mode": "table",
            "data": [
                {"time_period": "2024", "value": 1.0, "order": 7},
            ],
            "table_metadata": {"fixed_dimensions": {}},
            "structure": {
                "indicators": [
                    {"order": 7, "code": "X7"},
                    {"order": None, "code": "ZZZ"},
                ]
            },
            "series_metadata": {},
        }
        out = OecdEconomicIndicatorsFetcher.transform_data(query=self._q(), data=data)
        assert out.result[0].symbol == f"{_SHORT_ID}::X7"

    def test_date_filters_in_table_mode(self):
        """start_date / end_date filters apply in table mode."""
        data = {
            "mode": "table",
            "data": [
                {"time_period": "2010", "value": 1.0, "order": 1},
                {"time_period": "2024", "value": 2.0, "order": 1},
            ],
            "table_metadata": {"fixed_dimensions": {}},
            "structure": {"indicators": []},
            "series_metadata": {},
        }
        out = OecdEconomicIndicatorsFetcher.transform_data(
            query=self._q(start_date=_dt.date(2020, 1, 1)),
            data=data,
        )
        assert len(out.result) == 1
        out2 = OecdEconomicIndicatorsFetcher.transform_data(
            query=self._q(end_date=_dt.date(2015, 1, 1)),
            data=data,
        )
        assert len(out2.result) == 1


class TestTransformDataNonPivotFilter:
    """The non-pivot tail filter for rows missing a date."""

    def test_row_missing_date_and_not_header_skipped(self):
        """Rows missing date that aren't headers are dropped during emission."""
        q = OecdEconomicIndicatorsQueryParams.model_construct(
            symbol=f"{_SHORT_ID}::T01",
            country=None,
            frequency=None,
            transform=None,
            dimension_values=None,
            limit=None,
            start_date=None,
            end_date=None,
            pivot=False,
        )
        q._dataflow = _SHORT_ID
        q._is_table = True
        q._table_id = "T01"
        data = {
            "mode": "table",
            "data": [
                {"time_period": "2024", "value": 1.0, "code": "X", "order": 1},
                {"time_period": "2024", "value": 2.0, "code": "Y", "order": 2},
            ],
            "table_metadata": {"fixed_dimensions": {}},
            "structure": {"indicators": []},
            "series_metadata": {},
        }
        with patch(
            "openbb_oecd.models.economic_indicators.OecdEconomicIndicatorsData.model_validate",
            wraps=OecdEconomicIndicatorsData.model_validate,
        ):
            out = OecdEconomicIndicatorsFetcher.transform_data(query=q, data=data)
        out.result[0].__dict__["date"] = None
        original_rows = data["data"]
        original_rows.append({"time_period": "", "value": 3.0, "order": 3})
        out2 = OecdEconomicIndicatorsFetcher.transform_data(query=q, data=data)
        assert all(r.date is not None for r in out2.result)


class TestTransformDataPivot:
    """Pivot-mode transform_data branches."""

    def _build(self, **overrides):
        """Build a pivot-mode query."""
        q = OecdEconomicIndicatorsQueryParams.model_construct(
            symbol=f"{_SHORT_ID}::CPI",
            country=None,
            frequency=None,
            transform=None,
            dimension_values=None,
            limit=None,
            start_date=overrides.pop("start_date", None),
            end_date=overrides.pop("end_date", None),
            pivot=True,
        )
        q._dataflow = _SHORT_ID
        q._is_table = False
        q._indicator_codes = ["CPI"]
        return q

    def _indicator_data(self, rows):
        """Wrap rows in the indicator-mode dict shape."""
        return {
            "mode": "indicator",
            "data": rows,
            "metadata": {},
            "content_dims": ["MEASURE"],
        }

    def test_single_country_pivot_by_title(self):
        """Single country: pivot index is title only."""
        rows = [
            {
                "TIME_PERIOD": "2023",
                "OBS_VALUE": "1.0",
                "REF_AREA": "USA",
                "REF_AREA_label": "United States",
                "MEASURE": "CPI",
                "MEASURE_label": "Consumer Price Index",
            },
            {
                "TIME_PERIOD": "2024",
                "OBS_VALUE": "2.0",
                "REF_AREA": "USA",
                "REF_AREA_label": "United States",
                "MEASURE": "CPI",
                "MEASURE_label": "Consumer Price Index",
            },
        ]
        out = OecdEconomicIndicatorsFetcher.transform_data(
            query=self._build(), data=self._indicator_data(rows)
        )
        assert len(out.result) == 1

    def test_multi_country_single_symbol_pivot_by_country(self):
        """Multiple countries, single symbol -> pivot index is country."""
        rows = [
            {
                "TIME_PERIOD": "2024",
                "OBS_VALUE": "1.0",
                "REF_AREA": "USA",
                "REF_AREA_label": "United States",
                "MEASURE": "CPI",
                "MEASURE_label": "Consumer Price Index",
            },
            {
                "TIME_PERIOD": "2024",
                "OBS_VALUE": "2.0",
                "REF_AREA": "GBR",
                "REF_AREA_label": "United Kingdom",
                "MEASURE": "CPI",
                "MEASURE_label": "Consumer Price Index",
            },
        ]
        out = OecdEconomicIndicatorsFetcher.transform_data(
            query=self._build(), data=self._indicator_data(rows)
        )
        countries = {r.country for r in out.result}
        assert countries == {"United States", "United Kingdom"}

    def test_multi_country_multi_symbol_pivot_by_title_and_country(self):
        """Multiple countries + multiple symbols -> pivot index = (title, country)."""
        rows = [
            {
                "TIME_PERIOD": "2024",
                "OBS_VALUE": "1.0",
                "REF_AREA": "USA",
                "REF_AREA_label": "United States",
                "MEASURE": "CPI",
                "MEASURE_label": "Consumer Price Index",
            },
            {
                "TIME_PERIOD": "2024",
                "OBS_VALUE": "2.0",
                "REF_AREA": "GBR",
                "REF_AREA_label": "United Kingdom",
                "MEASURE": "PPI",
                "MEASURE_label": "Producer Price Index",
            },
        ]
        out = OecdEconomicIndicatorsFetcher.transform_data(
            query=self._build(), data=self._indicator_data(rows)
        )
        assert len(out.result) == 2

    def test_pivot_empty_dataframe_raises(self, monkeypatch):
        """An empty DataFrame post-construction raises EmptyDataError."""
        rows = [
            {
                "TIME_PERIOD": "2024",
                "OBS_VALUE": "1.0",
                "REF_AREA": "USA",
                "REF_AREA_label": "United States",
                "MEASURE": "CPI",
                "MEASURE_label": "Consumer Price Index",
            }
        ]
        from pandas import DataFrame as _RealDF

        class _EmptyDF(_RealDF):
            @property
            def empty(self):
                return True

        with patch(
            "pandas.DataFrame",
            side_effect=lambda data=None, *a, **k: _EmptyDF(data or []),
        ):
            with pytest.raises(EmptyDataError, match="No data for pivot"):
                OecdEconomicIndicatorsFetcher.transform_data(
                    query=self._build(), data=self._indicator_data(rows)
                )

    def test_pivot_fallback_when_pivot_table_raises(self, monkeypatch):
        """A pivot_table exception triggers the unpivoted fallback path."""
        rows = [
            {
                "TIME_PERIOD": "2024",
                "OBS_VALUE": "1.0",
                "REF_AREA": "USA",
                "REF_AREA_label": "United States",
                "MEASURE": "CPI",
                "MEASURE_label": "Consumer Price Index",
            }
        ]
        from pandas import DataFrame as _RealDF

        original_pivot = _RealDF.pivot_table

        def _broken_pivot(self, *args, **kwargs):
            raise RuntimeError("pivot fail")

        monkeypatch.setattr(_RealDF, "pivot_table", _broken_pivot)
        try:
            out = OecdEconomicIndicatorsFetcher.transform_data(
                query=self._build(), data=self._indicator_data(rows)
            )
            assert len(out.result) == 1
        finally:
            monkeypatch.setattr(_RealDF, "pivot_table", original_pivot)


class TestApplyTransformHelper:
    """Direct tests for the module-level _apply_transform helper."""

    def test_transform_wildcard_uses_transform_dim(self):
        """'all' or '*' on a transform_dim becomes a wildcard value."""
        params: dict = {}
        _apply_transform(
            "all",
            "DF",
            params,
            lambda df: ("TRANSFORMATION", None, {"index": "IX"}, {}),
        )
        assert params == {"TRANSFORMATION": "*"}

    def test_transform_match_applied(self):
        """A known transform value is mapped to its code."""
        params: dict = {}
        _apply_transform(
            "index",
            "DF",
            params,
            lambda df: ("TRANSFORMATION", None, {"index": "IX"}, {}),
        )
        assert params == {"TRANSFORMATION": "IX"}

    def test_unit_wildcard_when_no_transform_match(self):
        """Falls back to unit_dim wildcard when transform_dim doesn't match."""
        params: dict = {}
        _apply_transform(
            "all",
            "DF",
            params,
            lambda df: (None, "UNIT_MEASURE", {}, {"usd": "USD"}),
        )
        assert params == {"UNIT_MEASURE": "*"}

    def test_unit_lookup_match(self):
        """Falls back to unit lookup when transform lookup misses."""
        params: dict = {}
        _apply_transform(
            "usd",
            "DF",
            params,
            lambda df: (None, "UNIT_MEASURE", {}, {"usd": "USD"}),
        )
        assert params == {"UNIT_MEASURE": "USD"}

    def test_no_dim_raises_unsupported(self):
        """Neither transform_dim nor unit_dim present -> 'does not support'."""
        with pytest.raises(OpenBBError, match="does not support"):
            _apply_transform("index", "DF", {}, lambda df: (None, None, {}, {}))

    def test_invalid_value_lists_transform_options(self):
        """An invalid value lists the available transform options."""
        with pytest.raises(OpenBBError, match="Invalid transform value"):
            _apply_transform(
                "bogus",
                "DF",
                {},
                lambda df: ("TRANSFORMATION", None, {"index": "IX"}, {}),
            )

    def test_invalid_value_lists_unit_options(self):
        """An invalid value also surfaces unit_lookup options."""
        with pytest.raises(OpenBBError, match="usd"):
            _apply_transform(
                "bogus",
                "DF",
                {},
                lambda df: (
                    "TRANSFORMATION",
                    "UNIT_MEASURE",
                    {"index": "IX"},
                    {"usd": "USD"},
                ),
            )

    def test_invalid_value_with_no_options(self):
        """When no friendly options exist, the message says 'none'."""
        with pytest.raises(OpenBBError, match="none"):
            _apply_transform(
                "bogus",
                "DF",
                {},
                lambda df: ("TRANSFORMATION", "UNIT_MEASURE", {}, {}),
            )
