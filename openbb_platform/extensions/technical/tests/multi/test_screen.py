"""Tests for ``openbb_technical.multi.screen``."""

from __future__ import annotations

import pytest

from openbb_technical.multi.screen import (
    ScreenCondition,
    ScreenMatch,
    ScreenQueryParams,
    _evaluate,
    _find_column,
    _normalise_value,
    screen,
)


class TestNormaliseValue:
    def test_scalar(self):
        assert _normalise_value(50) == 50.0

    def test_tuple(self):
        assert _normalise_value((1, 2)) == (1.0, 2.0)

    def test_list_to_tuple(self):
        assert _normalise_value([3, 4]) == (3.0, 4.0)


class TestFindColumn:
    def test_exact(self):
        assert _find_column({"rsi": 1}, "rsi") == "rsi"

    def test_case_insensitive(self):
        assert _find_column({"RSI": 1}, "rsi") == "RSI"

    def test_missing(self):
        assert _find_column({"rsi": 1}, "macd") is None


class TestEvaluate:
    series = [
        ("d1", 10.0),
        ("d2", 20.0),
        ("d3", 30.0),
        ("d4", 25.0),
        ("d5", 40.0),
    ]

    @pytest.mark.parametrize(
        "op,value,fired",
        [
            ("gt", 35, True),
            ("gte", 40, True),
            ("lt", 50, True),
            ("lte", 40, True),
            ("eq", 40, True),
            ("gt", 50, False),
        ],
    )
    def test_simple_ops(self, op, value, fired):
        result, _ = _evaluate(self.series, op, float(value), len(self.series) - 1)
        assert result is fired

    def test_between(self):
        fired, observed = _evaluate(self.series, "between", (35.0, 45.0), 4)
        assert fired is True
        assert observed == 40.0

    def test_crossed_above(self):
        fired, _ = _evaluate(self.series, "crossed_above", (15.0, 5), 4)
        assert fired is True

    def test_crossed_below(self):
        fired, _ = _evaluate(self.series, "crossed_below", (28.0, 4), 4)
        assert fired is True

    def test_made_high(self):
        fired, _ = _evaluate(self.series, "made_high", (0.0, 3), 4)
        assert fired is True

    def test_made_low(self):
        fired, _ = _evaluate(
            [("d1", 10), ("d2", 5), ("d3", 4)], "made_low", (0.0, 3), 2
        )
        assert fired is True

    def test_none_latest(self):
        fired, _ = _evaluate([("d1", None)], "gt", 0.0, 0)
        assert fired is False

    def test_event_op_too_few_points(self):
        fired, _ = _evaluate(self.series, "crossed_above", (15.0, 1), 4)
        assert fired is False


class TestScreenEndpoint:
    def test_and_combine_default(self, multi_symbol_records):
        out = screen(
            ScreenQueryParams(
                data=multi_symbol_records,
                conditions=[
                    ScreenCondition(
                        indicator="rsi",
                        column="rsi",
                        operator="gt",
                        value=0,
                        indicator_params={"length": 14},
                    ),
                ],
            )
        )
        assert out.results
        assert all(isinstance(r, ScreenMatch) for r in out.results)
        assert {m.symbol for m in out.results} == {"AAA", "BBB", "CCC"}

    def test_or_combine(self, multi_symbol_records):
        out = screen(
            ScreenQueryParams(
                data=multi_symbol_records,
                combine="or",
                conditions=[
                    ScreenCondition(
                        indicator="rsi",
                        column="rsi",
                        operator="gt",
                        value=10000,
                        indicator_params={"length": 14},
                    ),
                    ScreenCondition(
                        indicator="atr",
                        column="atr",
                        operator="gt",
                        value=0,
                        indicator_params={"length": 14},
                    ),
                ],
            )
        )
        assert {m.symbol for m in out.results} == {"AAA", "BBB", "CCC"}

    def test_unknown_indicator_skipped(self, multi_symbol_records):
        out = screen(
            ScreenQueryParams(
                data=multi_symbol_records,
                conditions=[
                    ScreenCondition(
                        indicator="not_a_real_indicator",
                        column="x",
                        operator="gt",
                        value=0,
                    )
                ],
            )
        )
        assert out.results == []

    def test_unknown_column_skipped(self, multi_symbol_records):
        out = screen(
            ScreenQueryParams(
                data=multi_symbol_records,
                conditions=[
                    ScreenCondition(
                        indicator="rsi",
                        column="not_a_column",
                        operator="gt",
                        value=0,
                        indicator_params={"length": 14},
                    )
                ],
            )
        )
        assert out.results == []

    def test_as_of_date(self, multi_symbol_records):
        out = screen(
            ScreenQueryParams(
                data=multi_symbol_records,
                as_of_date="2021-06-30",
                conditions=[
                    ScreenCondition(
                        indicator="rsi",
                        column="rsi",
                        operator="gt",
                        value=0,
                        indicator_params={"length": 14},
                    )
                ],
            )
        )
        assert out.results
        assert all(str(m.as_of_date) <= "2021-06-30" for m in out.results)

    def test_as_of_before_data_skips_symbol(self, multi_symbol_records):
        out = screen(
            ScreenQueryParams(
                data=multi_symbol_records,
                as_of_date="1990-01-01",
                conditions=[
                    ScreenCondition(
                        indicator="rsi",
                        column="rsi",
                        operator="gt",
                        value=0,
                    )
                ],
            )
        )
        assert out.results == []

    def test_missing_symbol_column_errors(self, single_symbol_records):
        sym_less = [
            type(r).model_validate(
                {k: v for k, v in r.model_dump().items() if k != "symbol"}
            )
            for r in single_symbol_records[:5]
        ]
        with pytest.raises(ValueError, match="symbol"):
            screen(
                ScreenQueryParams(
                    data=sym_less,
                    conditions=[
                        ScreenCondition(
                            indicator="rsi", column="rsi", operator="gt", value=0
                        )
                    ],
                )
            )

    def test_event_op_threshold(self, multi_symbol_records):
        out = screen(
            ScreenQueryParams(
                data=multi_symbol_records,
                conditions=[
                    ScreenCondition(
                        indicator="rsi",
                        column="rsi",
                        operator="crossed_above",
                        value=(50.0, 30),
                        indicator_params={"length": 14},
                    )
                ],
            )
        )
        assert isinstance(out.results, list)

    def test_query_params_defaults(self, multi_symbol_records):
        params = ScreenQueryParams(
            data=multi_symbol_records,
            conditions=[
                ScreenCondition(indicator="rsi", column="rsi", operator="gt", value=0)
            ],
        )
        assert params.combine == "and"
        assert params.as_of_date is None
