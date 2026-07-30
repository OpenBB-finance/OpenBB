"""Unit tests for the Federal Reserve Money Measures model."""

# ruff: noqa: I001

import csv
import io
from datetime import date as dateType, datetime, timedelta
from types import SimpleNamespace

from openbb_federal_reserve.models.money_measures import (
    FederalReserveMoneyMeasuresData,
    FederalReserveMoneyMeasuresFetcher,
    FederalReserveMoneyMeasuresQueryParams,
)

_COLUMNS_N = [
    "M1_N.M",
    "M2_N.M",
    "MCU_N.M",
    "MDD_N.M",
    "MMFGB_N.M",
    "MDL_N.M",
    "MDTS_N.M",
]
_COLUMNS_S = ["M1.M", "M2.M", "MCU.M", "MDD.M", "MMFGB.M", "MDL.M", "MDTS.M"]


def _csv_bytes() -> bytes:
    """Return CSV bytes mirroring the H6 download layout (5 junk rows + header)."""
    header = ["Time Period"] + _COLUMNS_N + _COLUMNS_S
    junk = [
        ["Series Description"] + ["x"] * (len(header) - 1),
        ["Unit:"] + ["Currency"] * (len(header) - 1),
        ["Multiplier:"] + ["1e+09"] * (len(header) - 1),
        ["Currency:"] + ["USD"] * (len(header) - 1),
        ["Unique Identifier:"] + ["id"] * (len(header) - 1),
    ]
    data = [
        [
            "2023-01",
            "100",
            "200",
            "30",
            "40",
            "50",
            "60",
            "70",
            "101",
            "201",
            "31",
            "41",
            "51",
            "61",
            "71",
        ],
        [
            "2023-02",
            "ND",
            "210",
            "31",
            "41",
            "51",
            "61",
            "71",
            "102",
            "202",
            "32",
            "42",
            "52",
            "62",
            "72",
        ],
        [
            "2024-01",
            "110",
            "220",
            "33",
            "43",
            "53",
            "63",
            "73",
            "111",
            "221",
            "34",
            "44",
            "54",
            "64",
            "74",
        ],
    ]
    buf = io.StringIO()
    writer = csv.writer(buf)
    for row in junk + [header] + data:
        writer.writerow(row)
    return buf.getvalue().encode("utf-8")


def _patch_make_request(monkeypatch):
    """Patch ``make_request`` to return a response object carrying the CSV bytes."""
    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(
        helpers,
        "make_request",
        lambda url, **kwargs: SimpleNamespace(content=_csv_bytes()),
    )


class TestTransformQuery:
    """Tests for ``FederalReserveMoneyMeasuresFetcher.transform_query``."""

    def test_defaults_fill_ten_year_window(self):
        """Missing dates default to a ten-year window ending today."""
        q = FederalReserveMoneyMeasuresFetcher.transform_query({})
        assert isinstance(q, FederalReserveMoneyMeasuresQueryParams)
        now = datetime.now().date()
        assert q.end_date == now
        assert q.start_date == now - timedelta(days=10 * 365)

    def test_explicit_dates_pass_through(self):
        """Explicit start and end dates are preserved unchanged."""
        q = FederalReserveMoneyMeasuresFetcher.transform_query(
            {"start_date": dateType(2020, 1, 1), "end_date": dateType(2020, 12, 31)}
        )
        assert q.start_date == dateType(2020, 1, 1)
        assert q.end_date == dateType(2020, 12, 31)


class TestExtractData:
    """Tests for ``FederalReserveMoneyMeasuresFetcher.extract_data``."""

    def test_adjusted_selects_n_columns(self, monkeypatch):
        """``adjusted=True`` reads the ``_N.M`` columns and filters by date."""
        from pandas import isna

        _patch_make_request(monkeypatch)
        q = FederalReserveMoneyMeasuresQueryParams(
            start_date=dateType(2023, 1, 1),
            end_date=dateType(2023, 12, 31),
            adjusted=True,
        )
        data = FederalReserveMoneyMeasuresFetcher.extract_data(q, None)
        assert len(data) == 2
        assert data[0]["m1"] == 100.0
        assert isna(data[1]["m1"])

    def test_unadjusted_selects_plain_columns(self, monkeypatch):
        """``adjusted=False`` reads the ``.M`` columns."""
        _patch_make_request(monkeypatch)
        q = FederalReserveMoneyMeasuresQueryParams(
            start_date=dateType(2023, 1, 1),
            end_date=dateType(2024, 12, 31),
            adjusted=False,
        )
        data = FederalReserveMoneyMeasuresFetcher.extract_data(q, None)
        assert len(data) == 3
        assert data[0]["m1"] == 101.0


class TestTransformData:
    """Tests for ``FederalReserveMoneyMeasuresFetcher.transform_data``."""

    def test_nan_values_become_none_and_expanded_to_dollars(self):
        """``NaN`` values become ``None``, rows sort, and billions expand to full dollars."""
        data = [
            {
                "month": datetime(2023, 2, 1),
                "m1": 1100.0,
                "m2": 2100.0,
                "currency": 310.0,
                "demand_deposits": 410.0,
                "retail_money_market_funds": 510.0,
                "other_liquid_deposits": float("nan"),
                "small_denomination_time_deposits": 710.0,
            },
            {
                "month": datetime(2023, 1, 1),
                "m1": 1000.0,
                "m2": 2000.0,
                "currency": 300.0,
                "demand_deposits": 400.0,
                "retail_money_market_funds": 500.0,
                "other_liquid_deposits": 600.0,
                "small_denomination_time_deposits": 700.0,
            },
        ]
        q = FederalReserveMoneyMeasuresQueryParams()
        out = FederalReserveMoneyMeasuresFetcher.transform_data(q, data)
        assert all(isinstance(r, FederalReserveMoneyMeasuresData) for r in out)
        assert out[0].month == dateType(2023, 1, 1)
        assert out[1].month == dateType(2023, 2, 1)
        assert out[0].m2 == 2_000_000_000_000
        assert out[0].currency == 300_000_000_000
        assert out[1].other_liquid_deposits is None

    def test_values_expanded_to_full_dollars(self):
        """Published billions expand to full, comma-separable integer dollars."""
        data = [
            {
                "month": datetime(2023, 1, 1),
                "m1": 15493.4,
                "m2": 21724.6,
                "currency": 2371.8,
                "demand_deposits": 5012.3,
                "retail_money_market_funds": 1843.9,
                "other_liquid_deposits": 9123.4,
                "small_denomination_time_deposits": 281.7,
            }
        ]
        q = FederalReserveMoneyMeasuresQueryParams()
        out = FederalReserveMoneyMeasuresFetcher.transform_data(q, data)
        assert out[0].m1 == 15_493_400_000_000
        assert out[0].m2 == 21_724_600_000_000
        assert out[0].currency == 2_371_800_000_000
        assert out[0].small_denomination_time_deposits == 281_700_000_000

    def test_no_money_widget_config_overrides(self):
        """The money fields render as plain numbers with no prefix/suffix overrides."""
        schema = FederalReserveMoneyMeasuresData.model_json_schema()
        for field in (
            "m1",
            "m2",
            "currency",
            "demand_deposits",
            "retail_money_market_funds",
            "other_liquid_deposits",
            "small_denomination_time_deposits",
        ):
            assert "x-widget_config" not in schema["properties"][field]

    def test_string_values_preserved(self):
        """String values are not coerced to ``None`` by the NaN check."""
        data = [
            {
                "month": datetime(2023, 1, 1),
                "m1": 1000.0,
                "m2": 2000.0,
                "currency": 300.0,
                "demand_deposits": 400.0,
                "retail_money_market_funds": 500.0,
                "other_liquid_deposits": 600.0,
                "small_denomination_time_deposits": 700.0,
            }
        ]
        q = FederalReserveMoneyMeasuresQueryParams()
        out = FederalReserveMoneyMeasuresFetcher.transform_data(q, data)
        assert out[0].m1 == 1_000_000_000_000
