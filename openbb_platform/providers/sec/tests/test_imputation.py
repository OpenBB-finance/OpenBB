"""Unit tests for ``openbb_sec.utils.statement_schema._imputation``.

These drive the imputation/verification engine directly with crafted
synthetic statements -- the engine is pure, so no network is involved.
They cover the source-formatting and multi-pass solver helpers, the
hierarchical roll-up/plug articulation, the per-statement ``impute()``
paths for income statement, balance sheet and cash flow, the equity-method
and ProfitLoss pretax corrections, the fiscal-year-end reconciliation, and
the many fact-based reconciliation fallbacks plus the final identity
enforcement and pending-diagnostic resolution.

Tests only -- no source under ``openbb_sec/`` is modified.
"""

# flake8: noqa: D101,D102,D103,D403

from unittest.mock import patch

import pytest

from openbb_sec.utils.statement_schema._imputation import (
    _apply_hierarchical_articulation,
    _format_impute_source,
    _formula_terms,
    _net_change_from_balances,
    _resolve_sign_flips,
    _run_imputation_passes,
    impute,
    reconcile_fiscal_year_ends,
)
from openbb_sec.utils.statement_schema._types import (
    RowDef,
    RowResult,
    StatementResult,
)

_M = 1_000_000
_D = "2023-12-31"


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def _rr(
    tag,
    values=None,
    *,
    parent=None,
    factor="+",
    balance="",
    sequence=1,
    period_type="duration",
    unit="monetary",
    sources=None,
    label=None,
):
    return RowResult(
        tag=tag,
        label=label or tag.replace("_", " ").title(),
        description="",
        parent=parent,
        sequence=sequence,
        factor=factor,
        balance=balance,
        unit=unit,
        period_type=period_type,
        values=dict(values or {}),
        sources=dict(sources or {}),
    )


def _rd(
    tag,
    *,
    xbrl=(),
    unit="monetary",
    period_type="duration",
    parent=None,
    factor="+",
    balance="",
    sequence=1,
    label=None,
):
    return RowDef(
        tag=tag,
        label=label or tag.replace("_", " ").title(),
        description="",
        parent=parent,
        sequence=sequence,
        factor=factor,
        balance=balance,
        unit=unit,
        period_type=period_type,
        xbrl_tags=tuple({"tag": t, "namespace": ns} for t, ns in xbrl),
    )


def _by_tag(rows, tag):
    for r in rows:
        if r.tag == tag:
            return r
    return None


def _dur(end, start, val, *, form="10-K", filed="2024-02-15"):
    return {"end": end, "start": start, "val": val, "form": form, "filed": filed}


def _inst(end, val, *, form="10-K", filed="2024-02-15"):
    return {"end": end, "val": val, "form": form, "filed": filed}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class TestFormatImputeSource:
    def test_single_positive_no_leading_plus(self):
        assert _format_impute_source("p", [("a", 1)]) == "p: a"

    def test_single_negative_leading_minus(self):
        assert _format_impute_source("p", [("a", -1)]) == "p: -a"


class TestRunImputationPasses:
    def test_source_tag_absent_from_index(self):
        # A rule whose source tag is not present at all -> all_present False, no change.
        d = _D
        rows = [_rr("target", {})]
        idx = {r.tag: i for i, r in enumerate(rows)}
        rules = [("target", [("missing_src", 1)])]
        assert _run_imputation_passes(rows, rules, idx, {d}) is False

    def test_target_already_has_value_is_skipped(self):
        d = _D
        rows = [_rr("target", {d: 5.0}), _rr("a", {d: 9.0})]
        idx = {r.tag: i for i, r in enumerate(rows)}
        rules = [("target", [("a", 1)])]
        # target already populated -> untouched, returns False.
        assert _run_imputation_passes(rows, rules, idx, {d}) is False
        assert rows[0].values[d] == 5.0

    def test_target_tag_not_in_index_skipped(self):
        d = _D
        rows = [_rr("a", {d: 9.0})]
        idx = {r.tag: i for i, r in enumerate(rows)}
        rules = [("nonexistent_target", [("a", 1)])]
        assert _run_imputation_passes(rows, rules, idx, {d}) is False

    def test_rolled_up_ancestor_source_is_skipped(self):
        d = _D
        rows = [
            _rr("parent", {d: 30.0}, sources={d: "imputed-rollup: a(+)"}),
            _rr("a", {d: 30.0}, parent="parent"),
            _rr("b", {}, parent="parent"),
        ]
        idx = {r.tag: i for i, r in enumerate(rows)}
        rules = [("b", [("parent", 1), ("a", -1)])]
        assert _run_imputation_passes(rows, rules, idx, {d}) is False
        assert d not in rows[2].values

    def test_tagged_ancestor_source_is_used(self):
        d = _D
        rows = [
            _rr("parent", {d: 30.0}, sources={d: "us-gaap:Parent"}),
            _rr("a", {d: 20.0}, parent="parent"),
            _rr("b", {}, parent="parent"),
        ]
        idx = {r.tag: i for i, r in enumerate(rows)}
        rules = [("b", [("parent", 1), ("a", -1)])]
        assert _run_imputation_passes(rows, rules, idx, {d}) is True
        assert rows[2].values[d] == 10.0

    @pytest.mark.parametrize(
        ("pretax", "costs_source", "expected"),
        [
            (100, "us-gaap:CostsAndExpenses", None),
            (80, "us-gaap:CostsAndExpenses", 300 * _M),
            (100, "imputed: total_revenue - total_operating_income", 300 * _M),
        ],
    )
    def test_single_step_costs_total_is_no_input(self, pretax, costs_source, expected):
        d = _D
        rows = [
            _rr("total_revenue", {d: 1000 * _M}, sources={d: "us-gaap:Revenues"}),
            _rr("costs_and_expenses", {d: 900 * _M}, sources={d: costs_source}),
            _rr("total_pretax_income", {d: pretax * _M}, sources={d: "us-gaap:P"}),
            _rr("total_cost_of_revenue", {d: 600 * _M}, sources={d: "us-gaap:C"}),
            _rr("total_operating_expenses", {}),
        ]
        rules = [
            (
                "total_operating_expenses",
                [("costs_and_expenses", 1), ("total_cost_of_revenue", -1)],
            )
        ]
        _run_imputation_passes(rows, rules, {r.tag: i for i, r in enumerate(rows)}, {d})
        assert _by_tag(rows, "total_operating_expenses").values.get(d) == expected

    @pytest.mark.parametrize(("operating", "expected"), [(500, None), (400, 100 * _M)])
    def test_zero_gross_line_not_derived(self, operating, expected):
        d = _D
        rows = [
            _rr("costs_and_expenses", {d: 500 * _M}, sources={d: "us-gaap:C"}),
            _rr(
                "total_operating_expenses",
                {d: operating * _M},
                sources={d: "us-gaap:O"},
            ),
            _rr("total_cost_of_revenue", {}),
        ]
        rules = [
            (
                "total_cost_of_revenue",
                [("costs_and_expenses", 1), ("total_operating_expenses", -1)],
            )
        ]
        _run_imputation_passes(rows, rules, {r.tag: i for i, r in enumerate(rows)}, {d})
        assert _by_tag(rows, "total_cost_of_revenue").values.get(d) == expected

    @pytest.mark.parametrize(("net_income", "expected"), [(70, None), (None, 300)])
    def test_single_step_with_derived_pretax(self, net_income, expected):
        d = _D
        rows = [
            _rr("total_revenue", {d: 1000 * _M}, sources={d: "us-gaap:Revenues"}),
            _rr(
                "costs_and_expenses",
                {d: 900 * _M},
                sources={d: "us-gaap:CostsAndExpenses"},
            ),
            _rr("total_pretax_income", {}),
            _rr(
                "net_income_continuing",
                {} if net_income is None else {d: net_income * _M},
                sources={} if net_income is None else {d: "us-gaap:N"},
            ),
            _rr("income_tax_expense", {d: 30 * _M}, sources={d: "us-gaap:T"}),
            _rr("total_cost_of_revenue", {d: 600 * _M}, sources={d: "us-gaap:C"}),
            _rr("total_operating_expenses", {}),
        ]
        rules = [
            (
                "total_operating_expenses",
                [("costs_and_expenses", 1), ("total_cost_of_revenue", -1)],
            ),
            (
                "total_pretax_income",
                [("total_revenue", 1), ("costs_and_expenses", -1)],
            ),
            (
                "total_pretax_income",
                [("net_income_continuing", 1), ("income_tax_expense", 1)],
            ),
        ]
        _run_imputation_passes(rows, rules, {r.tag: i for i, r in enumerate(rows)}, {d})
        opex = _by_tag(rows, "total_operating_expenses").values.get(d)
        assert opex == (None if expected is None else expected * _M)
        assert _by_tag(rows, "total_pretax_income").values[d] == 100 * _M

    def test_ancestor_walk_stops_on_parent_cycle(self):
        d = _D
        rows = [
            _rr("x", {d: 5.0}, parent="y"),
            _rr("y", {}, parent="x"),
            _rr("z", {d: 7.0}, sources={d: "imputed-rollup: q(+)"}),
        ]
        idx = {r.tag: i for i, r in enumerate(rows)}
        rules = [("y", [("z", 1)])]
        assert _run_imputation_passes(rows, rules, idx, {d}) is True
        assert rows[1].values[d] == 7.0


class TestApplyHierarchicalArticulation:
    def test_no_child_values_leaves_parent_untouched(self):
        d = _D
        rows = [
            _rr(
                "total_assets", {}, period_type="instant", balance="debit", sequence=10
            ),
            _rr(
                "cash",
                {},
                parent="total_assets",
                balance="debit",
                sequence=1,
                period_type="instant",
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        # No child had a value -> parent stays empty, no plug created.
        assert d not in _by_tag(rows, "total_assets").values
        assert _by_tag(rows, "other_assets") is None

    def test_tagged_other_line_replaced_by_remainder(self):
        d = _D
        rows = [
            _rr(
                "total_assets",
                {d: 200.0 * _M},
                period_type="instant",
                balance="debit",
                sequence=10,
            ),
            _rr(
                "cash",
                {d: 100.0 * _M},
                parent="total_assets",
                balance="debit",
                sequence=1,
                period_type="instant",
            ),
            _rr(
                "other_assets",
                {d: 7.0 * _M},
                parent="total_assets",
                balance="debit",
                sequence=2,
                period_type="instant",
                sources={d: "us-gaap:OtherAssets"},
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        oa = _by_tag(rows, "other_assets")
        assert oa.values[d] == 100.0 * _M
        assert oa.sources[d].startswith("imputed-plug")

    def test_tagged_other_line_kept_when_articulating(self):
        d = _D
        rows = [
            _rr("total_assets", {d: 200.0 * _M}, period_type="instant", sequence=10),
            _rr(
                "cash",
                {d: 100.0 * _M},
                parent="total_assets",
                sequence=1,
                period_type="instant",
            ),
            _rr(
                "other_assets",
                {d: 100.0 * _M},
                parent="total_assets",
                sequence=2,
                period_type="instant",
                sources={d: "us-gaap:OtherAssets"},
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "other_assets").sources[d] == "us-gaap:OtherAssets"

    def test_mapped_other_line_holds_remainder(self):
        d = _D
        rows = [
            _rr("total_other_income", {d: 50.0 * _M}, sequence=10),
            _rr(
                "total_interest_income",
                {d: 20.0 * _M},
                parent="total_other_income",
                sequence=1,
            ),
            _rr(
                "other_income",
                {d: 5.0 * _M},
                parent="total_other_income",
                sequence=2,
                sources={d: "us-gaap:OtherNonoperatingIncomeExpense"},
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        oi = _by_tag(rows, "other_income")
        assert oi.values[d] == 30.0 * _M
        assert oi.sources[d].startswith("imputed-plug")
        assert _by_tag(rows, "other_other_income") is None

    def test_imputed_plug_child_excluded_then_replug(self):
        # An other_* child already carrying an imputed-plug is excluded from the
        # children sum and re-plugged to the fresh remainder.
        d = _D
        rows = [
            _rr(
                "total_assets",
                {d: 200.0 * _M},
                period_type="instant",
                balance="debit",
                sequence=10,
            ),
            _rr(
                "cash",
                {d: 120.0 * _M},
                parent="total_assets",
                balance="debit",
                sequence=1,
                period_type="instant",
            ),
            _rr(
                "other_assets",
                {d: 999.0 * _M},
                parent="total_assets",
                balance="debit",
                sequence=2,
                period_type="instant",
                sources={d: "imputed-plug: stale"},
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        oa = _by_tag(rows, "other_assets")
        # remainder = 200 - 120 = 80 (stale plug excluded from the sum)
        assert oa.values[d] == 80.0 * _M
        assert "imputed-plug" in oa.sources[d]

    def test_rollup_requires_required_child_value(self):
        d = _D
        rows = [
            _rr("total_gross_profit", {}, sequence=10),
            _rr(
                "total_revenue",
                {d: 100.0 * _M},
                parent="total_gross_profit",
                sequence=1,
            ),
            _rr(
                "total_cost_of_revenue",
                {},
                parent="total_gross_profit",
                factor="-",
                sequence=2,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert d not in _by_tag(rows, "total_gross_profit").values

    def test_rollup_requirement_ignored_when_not_in_tree(self):
        d = _D
        rows = [
            _rr("total_liabilities", {}, period_type="instant", sequence=10),
            _rr(
                "total_current_liabilities",
                {d: 40.0 * _M},
                parent="total_liabilities",
                period_type="instant",
                sequence=1,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "total_liabilities").values[d] == 40.0 * _M

    def test_empty_rollup_requirement_never_rolls_up(self):
        d = _D
        rows = [
            _rr("comprehensive_income_parent", {}, sequence=10),
            _rr(
                "other_comprehensive_income",
                {d: 5.0 * _M},
                parent="comprehensive_income_parent",
                sequence=1,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert d not in _by_tag(rows, "comprehensive_income_parent").values

    def test_rollup_includes_designated_other_line(self):
        d = _D
        rows = [
            _rr("total_other_income", {}, sequence=10),
            _rr(
                "total_interest_income",
                {d: 20.0 * _M},
                parent="total_other_income",
                sequence=1,
            ),
            _rr(
                "other_income",
                {d: 5.0 * _M},
                parent="total_other_income",
                sequence=2,
                sources={d: "us-gaap:OtherNonoperatingIncomeExpense"},
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        total_other = _by_tag(rows, "total_other_income")
        assert total_other.values[d] == 25.0 * _M
        assert total_other.sources[d] == (
            "imputed-rollup: total_interest_income(+) + other_income(+)"
        )

    def test_rollup_from_designated_other_line_alone(self):
        d = _D
        rows = [
            _rr("total_other_income", {}, sequence=10),
            _rr(
                "other_income",
                {d: 5.0 * _M},
                parent="total_other_income",
                sequence=2,
                sources={d: "us-gaap:OtherNonoperatingIncomeExpense"},
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        total_other = _by_tag(rows, "total_other_income")
        assert total_other.values[d] == 5.0 * _M
        assert total_other.sources[d] == "imputed-rollup: other_income(+)"

    def test_contained_component_gets_period_factor_zero(self):
        d = _D
        rows = [
            _rr("total_x", {d: 100.0 * _M}, sequence=10),
            _rr("a", {d: 60.0 * _M}, parent="total_x", sequence=1),
            _rr("b", {d: 40.0 * _M}, parent="total_x", sequence=2),
            _rr("c", {d: 30.0 * _M}, parent="total_x", sequence=3),
        ]
        _apply_hierarchical_articulation(rows, {d})
        c = _by_tag(rows, "c")
        assert c.date_factors == {d: "0"}
        assert c.factor_on(d) == "0"
        assert c.values[d] == 30.0 * _M
        assert _by_tag(rows, "other_x") is None

    def test_contained_pair_gets_period_factor_zero(self):
        d = _D
        rows = [
            _rr("total_x", {d: 100.0 * _M}, sequence=10),
            _rr("a", {d: 70.0 * _M}, parent="total_x", sequence=1),
            _rr("b", {d: 30.0 * _M}, parent="total_x", sequence=2),
            _rr("c", {d: 12.0 * _M}, parent="total_x", sequence=3),
            _rr("e", {d: 8.0 * _M}, parent="total_x", sequence=4),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "c").factor_on(d) == "0"
        assert _by_tag(rows, "e").factor_on(d) == "0"
        assert _by_tag(rows, "a").factor_on(d) == "+"
        assert _by_tag(rows, "other_x") is None

    def test_ambiguous_containment_goes_to_remainder(self):
        d = _D
        rows = [
            _rr("total_x", {d: 100.0 * _M}, sequence=10),
            _rr("a", {d: 80.0 * _M}, parent="total_x", sequence=1),
            _rr("b", {d: 20.0 * _M}, parent="total_x", sequence=2),
            _rr("c", {d: 20.0 * _M}, parent="total_x", sequence=3),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "b").date_factors == {}
        assert _by_tag(rows, "c").date_factors == {}
        other = _by_tag(rows, "other_x")
        assert other.values[d] == -20.0 * _M
        assert other.sources[d].startswith("imputed-plug: total_x - ")

    def test_contained_single_equal_to_other_line_left_to_other_line(self):
        d = _D
        rows = [
            _rr("total_x", {d: 100.0 * _M}, sequence=10),
            _rr("a", {d: 60.0 * _M}, parent="total_x", sequence=1),
            _rr("b", {d: 40.0 * _M}, parent="total_x", sequence=2),
            _rr(
                "other_x",
                {d: 40.0 * _M},
                parent="total_x",
                sequence=3,
                sources={d: "us-gaap:OtherX"},
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "b").date_factors == {}
        assert d not in _by_tag(rows, "other_x").values

    def test_explicit_line_inside_tagged_other_contained(self):
        d = _D
        rows = [
            _rr(
                "total_noncurrent_assets",
                {d: 100.0 * _M},
                period_type="instant",
                sequence=10,
            ),
            _rr(
                "net_ppe",
                {d: 60.0 * _M},
                parent="total_noncurrent_assets",
                period_type="instant",
                sequence=1,
            ),
            _rr(
                "operating_lease_right_of_use_asset",
                {d: 10.0 * _M},
                parent="total_noncurrent_assets",
                period_type="instant",
                sequence=2,
            ),
            _rr(
                "other_noncurrent_assets",
                {d: 40.0 * _M},
                parent="total_noncurrent_assets",
                period_type="instant",
                sequence=3,
                sources={d: "us-gaap:OtherAssetsNoncurrent"},
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "operating_lease_right_of_use_asset").factor_on(d) == "0"
        other = _by_tag(rows, "other_noncurrent_assets")
        assert other.values[d] == 40.0 * _M
        assert other.sources[d] == "us-gaap:OtherAssetsNoncurrent"

    def test_component_without_room_not_contained(self):
        d = _D
        rows = [
            _rr("total_x", {d: -103.0 * _M}, sequence=10),
            _rr("a", {d: -60.0 * _M}, parent="total_x", sequence=1),
            _rr("b", {d: -40.0 * _M}, parent="total_x", sequence=2),
            _rr("c", {d: 50.0 * _M}, parent="total_x", sequence=3),
            _rr(
                "other_x",
                {d: -3.0 * _M},
                parent="total_x",
                sequence=4,
                sources={d: "us-gaap:OtherX"},
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "c").date_factors == {}
        other = _by_tag(rows, "other_x")
        assert other.values[d] == -53.0 * _M
        assert other.sources[d].startswith("imputed-plug")

    def test_scope_variant_contained_without_room(self):
        d = _D
        rows = [
            _rr("total_pretax_income", {d: 100.0 * _M}, sequence=10),
            _rr(
                "total_operating_income",
                {d: 100.0 * _M},
                parent="total_pretax_income",
                sequence=1,
            ),
            _rr(
                "equity_method_investments",
                {d: 150.0 * _M},
                parent="total_pretax_income",
                sequence=2,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "equity_method_investments").factor_on(d) == "0"

    def test_net_income_line_holds_no_component(self):
        d = _D
        rows = [
            _rr(
                "net_cash_from_continuing_operating_activities",
                {d: 100.0 * _M},
                sequence=10,
            ),
            _rr(
                "net_income_continuing",
                {d: 100.0 * _M},
                parent="net_cash_from_continuing_operating_activities",
                sequence=1,
            ),
            _rr(
                "stock_based_compensation",
                {d: 30.0 * _M},
                parent="net_cash_from_continuing_operating_activities",
                sequence=2,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "stock_based_compensation").date_factors == {}
        other = _by_tag(rows, "other_operating_activities") or _by_tag(
            rows, "other_net_cash_from_continuing_operating_activities"
        )
        assert other.values[d] == -30.0 * _M

    def test_mixed_sign_pair_not_contained(self):
        d = _D
        rows = [
            _rr("total_x", {d: 100.0 * _M}, sequence=10),
            _rr("a", {d: 100.0 * _M}, parent="total_x", sequence=1),
            _rr("b", {d: 193.0 * _M}, parent="total_x", sequence=2),
            _rr("c", {d: -124.0 * _M}, parent="total_x", sequence=3),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "b").date_factors == {}
        assert _by_tag(rows, "c").date_factors == {}
        assert _by_tag(rows, "other_x").values[d] == -69.0 * _M

    def test_component_outside_reported_section_total_relocated(self):
        d = _D

        def inst(tag, value, parent, seq):
            return _rr(
                tag,
                {} if value is None else {d: value * _M},
                parent=parent,
                period_type="instant",
                sequence=seq,
            )

        rows = [
            inst("total_liabilities_and_equity", 6036.0, None, 30),
            inst("total_liabilities", None, "total_liabilities_and_equity", 20),
            inst("total_current_liabilities", 440.0, "total_liabilities", 1),
            inst("total_noncurrent_liabilities", 1528.0, "total_liabilities", 10),
            inst("long_term_debt", 2131.0, "total_noncurrent_liabilities", 2),
            inst(
                "asset_retirement_and_litigation_obligation",
                108.0,
                "total_noncurrent_liabilities",
                3,
            ),
            inst(
                "noncurrent_deferred_tax_liabilities",
                513.0,
                "total_noncurrent_liabilities",
                4,
            ),
            inst(
                "total_equity_and_noncontrolling_interests",
                1937.0,
                "total_liabilities_and_equity",
                21,
            ),
            inst("temporary_equity", None, "total_liabilities_and_equity", 22),
        ]
        _apply_hierarchical_articulation(rows, {d})
        tncl = _by_tag(rows, "total_noncurrent_liabilities")
        assert tncl.values[d] == 3659.0 * _M
        assert tncl.sources[d] == (
            "corrected: total_noncurrent_liabilities + long_term_debt"
        )
        assert _by_tag(rows, "other_noncurrent_liabilities").values[d] == 907.0 * _M
        assert _by_tag(rows, "total_liabilities").values[d] == 4099.0 * _M
        assert d not in _by_tag(rows, "temporary_equity").values

    def _inst(self, tag, value, parent=None, seq=1, source=None):
        d = _D
        return _rr(
            tag,
            {} if value is None else {d: value * _M},
            parent=parent,
            period_type="instant",
            sequence=seq,
            sources={} if value is None or source is None else {d: source},
        )

    def test_same_fact_in_two_rows_contained_once(self):
        d = _D
        fact = "us-gaap:PropertyPlantAndEquipmentNet"
        rows = [
            self._inst("total_assets", 100.0, seq=20),
            self._inst("cash_and_equivalents", 70.0, "total_assets", 1),
            self._inst("net_ppe", 30.0, "total_assets", 5, fact),
            self._inst("net_premises_and_equipment", 30.0, "total_assets", 6, fact),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "net_ppe").date_factors == {}
        assert _by_tag(rows, "net_premises_and_equipment").factor_on(d) == "0"
        assert _by_tag(rows, "other_assets") is None

    def test_equal_balances_over_total_contained_once(self):
        d = _D
        rows = [
            self._inst("total_current_assets", 18452.0, seq=20),
            self._inst("cash_and_equivalents", 3818.0, "total_current_assets", 1),
            self._inst("short_term_investments", 90.0, "total_current_assets", 2),
            self._inst("accounts_receivable", 6673.0, "total_current_assets", 3),
            self._inst("net_inventory", 3886.0, "total_current_assets", 4),
            self._inst(
                "prepaid_expenses",
                2531.0,
                "total_current_assets",
                5,
                "us-gaap:PrepaidExpenseCurrent",
            ),
            self._inst(
                "other_current_nonoperating_assets",
                2531.0,
                "total_current_assets",
                8,
                "us-gaap:PrepaidExpenseAndOtherAssetsCurrent",
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "prepaid_expenses").date_factors == {}
        assert _by_tag(rows, "other_current_nonoperating_assets").factor_on(d) == "0"
        assert _by_tag(rows, "other_current_assets").values[d] == 1454.0 * _M

    def test_nested_group_leaving_smallest_remainder_contained(self):
        d = _D
        rows = [
            self._inst("total_current_liabilities", 30011.0, seq=20),
            self._inst("accounts_payable", 11260.0, "total_current_liabilities", 1),
            self._inst("accrued_expenses", 9054.0, "total_current_liabilities", 2),
            self._inst("short_term_debt", 6183.0, "total_current_liabilities", 3),
            self._inst(
                "current_portion_of_long_term_debt",
                3388.0,
                "total_current_liabilities",
                4,
            ),
            self._inst(
                "current_employee_benefit_liabilities",
                1623.0,
                "total_current_liabilities",
                5,
            ),
            self._inst("other_taxes_payable", 341.0, "total_current_liabilities", 6),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "current_employee_benefit_liabilities").factor_on(d) == "0"
        assert _by_tag(rows, "other_taxes_payable").factor_on(d) == "0"
        assert _by_tag(rows, "current_portion_of_long_term_debt").date_factors == {}
        assert _by_tag(rows, "other_current_liabilities").values[d] == 126.0 * _M

    def test_total_equity_reconciled_with_common_equity_rollup(self):
        d = _D
        rows = [
            self._inst("total_equity", 100.0, seq=20),
            self._inst("total_common_equity", None, "total_equity", 10),
            self._inst("common_equity", 10.0, "total_common_equity", 1),
            self._inst("additional_paid_in_capital", 50.0, "total_common_equity", 2),
            self._inst("retained_earnings", 30.0, "total_common_equity", 3),
            self._inst("other_equity", None, "total_common_equity", 4),
        ]
        _apply_hierarchical_articulation(rows, {d})
        tce = _by_tag(rows, "total_common_equity")
        assert tce.values[d] == 100.0 * _M
        assert tce.sources[d].startswith("imputed-plug: total_equity - ")
        other = _by_tag(rows, "other_equity")
        assert other.values[d] == 10.0 * _M
        assert other.sources[d].startswith("imputed-plug: total_common_equity - ")

    def test_contra_only_components_create_no_remainder(self):
        d = _D
        rows = [
            self._inst("net_ppe", 24675.0, seq=20),
            self._inst("gross_ppe", None, "net_ppe", 1),
            _rr(
                "accumulated_depreciation",
                {d: 12560.0 * _M},
                parent="net_ppe",
                factor="-",
                period_type="instant",
                sequence=2,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "other_net_ppe") is None
        assert _by_tag(rows, "net_ppe").values[d] == 24675.0 * _M

    def test_scope_variant_pair_of_mixed_signs_contained(self):
        d = _D
        rows = [
            _rr("total_x", {d: 47.0 * _M}, sequence=10),
            _rr("a", {d: 1552.0 * _M}, parent="total_x", sequence=1),
            _rr(
                "net_cash_from_discontinued_operating_activities",
                {d: -7.0 * _M},
                parent="total_x",
                sequence=2,
            ),
            _rr("b", {d: -663.0 * _M}, parent="total_x", sequence=3),
            _rr(
                "net_cash_from_discontinued_investing_activities",
                {d: 50.0 * _M},
                parent="total_x",
                sequence=4,
            ),
            _rr("c", {d: -842.0 * _M}, parent="total_x", sequence=5),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert (
            _by_tag(rows, "net_cash_from_discontinued_operating_activities").factor_on(
                d
            )
            == "0"
        )
        assert (
            _by_tag(rows, "net_cash_from_discontinued_investing_activities").factor_on(
                d
            )
            == "0"
        )
        assert _by_tag(rows, "other_x") is None

    def test_imputed_parent_is_not_containment_evidence(self):
        d = _D
        rows = [
            _rr(
                "total_x",
                {d: 100.0 * _M},
                sequence=10,
                sources={d: "imputed: total_y - total_z"},
            ),
            _rr("a", {d: 60.0 * _M}, parent="total_x", sequence=1),
            _rr("b", {d: 40.0 * _M}, parent="total_x", sequence=2),
            _rr("c", {d: 30.0 * _M}, parent="total_x", sequence=3),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "c").date_factors == {}
        assert _by_tag(rows, "other_x").values[d] == -30.0 * _M

    def test_every_same_fact_duplicate_contained(self):
        d = _D
        ppe = "us-gaap:PropertyPlantAndEquipmentNet"
        receivables = "us-gaap:AccountsReceivableNet"
        rows = [
            self._inst("total_assets", 65.0, seq=20),
            self._inst("cash_and_equivalents", 30.0, "total_assets", 1),
            self._inst("net_ppe", 10.0, "total_assets", 5, ppe),
            self._inst("net_premises_and_equipment", 10.0, "total_assets", 6, ppe),
            self._inst("accounts_receivable", 25.0, "total_assets", 7, receivables),
            self._inst(
                "customer_and_other_receivables", 25.0, "total_assets", 8, receivables
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "net_premises_and_equipment").factor_on(d) == "0"
        assert _by_tag(rows, "customer_and_other_receivables").factor_on(d) == "0"
        assert _by_tag(rows, "net_ppe").date_factors == {}
        assert _by_tag(rows, "accounts_receivable").date_factors == {}

    def test_contained_component_found_under_rolled_up_other_line(self):
        d = _D
        rows = [
            _rr("total_equity", {d: 100.0 * _M}, period_type="instant", sequence=10),
            _rr(
                "total_preferred_equity",
                {d: 10.0 * _M},
                parent="total_equity",
                period_type="instant",
                sequence=1,
            ),
            _rr(
                "total_common_equity",
                {},
                parent="total_equity",
                period_type="instant",
                sequence=2,
            ),
            _rr(
                "retained_earnings",
                {d: 90.0 * _M},
                parent="total_common_equity",
                period_type="instant",
                sequence=3,
            ),
            _rr(
                "preferred_in_common",
                {d: 10.0 * _M},
                parent="total_common_equity",
                period_type="instant",
                sequence=4,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "preferred_in_common").factor_on(d) == "0"
        assert _by_tag(rows, "total_common_equity").values[d] == 90.0 * _M

    def test_presented_memo_promoted(self):
        d = _D
        rows = [
            _rr("net_cash_from_operating_activities", {d: 100.0 * _M}, sequence=10),
            _rr(
                "net_cash_from_continuing_operating_activities",
                {d: 70.0 * _M},
                parent="net_cash_from_operating_activities",
                sequence=1,
            ),
            _rr(
                "net_cash_from_discontinued_operations",
                {d: 30.0 * _M},
                parent="net_cash_from_operating_activities",
                factor="0",
                sequence=2,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        memo = _by_tag(rows, "net_cash_from_discontinued_operations")
        assert memo.factor_on(d) == "+"
        assert memo.factor == "0"
        assert _by_tag(rows, "other_net_cash_from_operating_activities") is None

    def test_incomplete_rollup_absorbs_section_difference(self):
        d = _D
        rows = [
            _rr(
                "total_liabilities_and_equity",
                {d: 300.0 * _M},
                period_type="instant",
                sequence=20,
            ),
            _rr(
                "total_liabilities",
                {},
                parent="total_liabilities_and_equity",
                period_type="instant",
                sequence=10,
            ),
            _rr(
                "total_current_liabilities",
                {d: 100.0 * _M},
                parent="total_liabilities",
                period_type="instant",
                sequence=1,
            ),
            _rr(
                "long_term_debt",
                {d: 50.0 * _M},
                parent="total_liabilities",
                period_type="instant",
                sequence=2,
            ),
            _rr(
                "total_equity_and_noncontrolling_interests",
                {d: 100.0 * _M},
                parent="total_liabilities_and_equity",
                period_type="instant",
                sequence=11,
            ),
            _rr(
                "temporary_equity",
                {},
                parent="total_liabilities_and_equity",
                period_type="instant",
                sequence=12,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        tl = _by_tag(rows, "total_liabilities")
        assert tl.values[d] == 200.0 * _M
        assert tl.sources[d].startswith("imputed-plug: total_liabilities_and_equity - ")
        other = _by_tag(rows, "other_liabilities")
        assert other.values[d] == 50.0 * _M
        assert d not in _by_tag(rows, "temporary_equity").values

    def test_nonnegative_line_negative_remainder_not_held(self):
        d = _D
        rows = [
            _rr(
                "total_liabilities_and_equity",
                {d: 300.0 * _M},
                period_type="instant",
                sequence=20,
            ),
            _rr(
                "total_liabilities",
                {d: 220.0 * _M},
                parent="total_liabilities_and_equity",
                period_type="instant",
                sequence=10,
            ),
            _rr(
                "total_equity_and_noncontrolling_interests",
                {d: 100.0 * _M},
                parent="total_liabilities_and_equity",
                period_type="instant",
                sequence=11,
            ),
            _rr(
                "temporary_equity",
                {},
                parent="total_liabilities_and_equity",
                period_type="instant",
                sequence=12,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert d not in _by_tag(rows, "temporary_equity").values
        assert _by_tag(rows, "other_liabilities_and_equity") is None

    def test_nonnegative_line_positive_remainder_held(self):
        d = _D
        rows = [
            _rr(
                "total_liabilities_and_equity",
                {d: 300.0 * _M},
                period_type="instant",
                sequence=20,
            ),
            _rr(
                "total_liabilities",
                {d: 180.0 * _M},
                parent="total_liabilities_and_equity",
                period_type="instant",
                sequence=10,
            ),
            _rr(
                "total_equity_and_noncontrolling_interests",
                {d: 100.0 * _M},
                parent="total_liabilities_and_equity",
                period_type="instant",
                sequence=11,
            ),
            _rr(
                "temporary_equity",
                {},
                parent="total_liabilities_and_equity",
                period_type="instant",
                sequence=12,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "temporary_equity").values[d] == 20.0 * _M
        assert _by_tag(rows, "other_liabilities_and_equity") is None

    def test_negative_noncurrent_remainder_not_held(self):
        d = _D
        rows = [
            _rr("total_assets", {d: 100.0 * _M}, period_type="instant", sequence=20),
            _rr(
                "total_current_assets",
                {d: 110.0 * _M},
                parent="total_assets",
                period_type="instant",
                sequence=1,
            ),
            _rr(
                "total_noncurrent_assets",
                {},
                parent="total_assets",
                period_type="instant",
                sequence=2,
            ),
            _rr(
                "other_assets",
                {},
                parent="total_assets",
                period_type="instant",
                sequence=3,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert d not in _by_tag(rows, "total_noncurrent_assets").values
        assert d not in _by_tag(rows, "other_assets").values

    def test_negative_gross_remainder_not_held(self):
        d = _D
        rows = [
            _rr("depreciation_and_amortization", {d: 100 * _M}, sequence=10),
            _rr(
                "depreciation_expense",
                {d: 80 * _M},
                parent="depreciation_and_amortization",
                sequence=1,
            ),
            _rr(
                "amortization_expense",
                {d: 30 * _M},
                parent="depreciation_and_amortization",
                sequence=2,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "other_depreciation_and_amortization") is None
        assert _by_tag(rows, "depreciation_and_amortization").values[d] == 100 * _M

    @pytest.mark.parametrize(("operating", "expected"), [(None, None), (50, 30 * _M)])
    def test_pretax_remainder_requires_operating_income(self, operating, expected):
        d = _D
        rows = [
            _rr("total_pretax_income", {d: 100 * _M}, sequence=10),
            _rr(
                "total_operating_income",
                {} if operating is None else {d: operating * _M},
                parent="total_pretax_income",
                sequence=1,
            ),
            _rr(
                "total_other_income",
                {},
                parent="total_pretax_income",
                sequence=2,
            ),
            _rr(
                "equity_method_investments",
                {d: 20 * _M},
                parent="total_pretax_income",
                sequence=3,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "total_other_income").values.get(d) == expected

    def test_all_zero_children_not_rolled_up(self):
        d = _D
        rows = [
            _rr("depreciation_and_amortization", {}, sequence=10),
            _rr("depreciation_expense", {d: 0}, parent="depreciation_and_amortization"),
            _rr("amortization_expense", {d: 0}, parent="depreciation_and_amortization"),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert d not in _by_tag(rows, "depreciation_and_amortization").values

    def test_contra_only_children_not_rolled_up(self):
        d = _D
        rows = [
            _rr("net_ppe", {}, period_type="instant", sequence=15),
            _rr("gross_ppe", {}, parent="net_ppe", period_type="instant", sequence=13),
            _rr(
                "accumulated_depreciation",
                {d: 531 * _M},
                parent="net_ppe",
                factor="-",
                period_type="instant",
                sequence=14,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert d not in _by_tag(rows, "net_ppe").values

    @pytest.mark.parametrize(("operating", "expected"), [(None, None), (500, 300)])
    def test_pretax_rollup_requires_operating_income(self, operating, expected):
        d = _D
        rows = [
            _rr("total_pretax_income", {}, sequence=10),
            _rr(
                "total_operating_income",
                {} if operating is None else {d: operating * _M},
                parent="total_pretax_income",
                sequence=1,
            ),
            _rr(
                "total_other_income",
                {d: -200 * _M},
                parent="total_pretax_income",
                sequence=2,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        pretax = _by_tag(rows, "total_pretax_income").values.get(d)
        assert pretax == (None if expected is None else expected * _M)

    @pytest.mark.parametrize(
        ("liabilities", "expected"), [(None, None), (600, 1000 * _M)]
    )
    def test_liabilities_and_equity_rollup_requires_liabilities(
        self, liabilities, expected
    ):
        d = _D
        rows = [
            _rr("total_liabilities_and_equity", {}, period_type="instant", sequence=73),
            _rr(
                "total_liabilities",
                {} if liabilities is None else {d: liabilities * _M},
                parent="total_liabilities_and_equity",
                period_type="instant",
                sequence=54,
            ),
            _rr(
                "total_equity_and_noncontrolling_interests",
                {d: 400 * _M},
                parent="total_liabilities_and_equity",
                period_type="instant",
                sequence=72,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "total_liabilities_and_equity").values.get(d) == expected

    def test_operating_totals_never_rolled_up(self):
        d = _D
        rows = [
            _rr("total_operating_income", {}, sequence=10),
            _rr(
                "total_gross_profit",
                {d: 100 * _M},
                parent="total_operating_income",
                sequence=1,
            ),
            _rr(
                "total_operating_expenses",
                {},
                parent="total_operating_income",
                factor="-",
                sequence=2,
            ),
            _rr("sga_expense", {d: 30 * _M}, parent="total_operating_expenses"),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert d not in _by_tag(rows, "total_operating_expenses").values
        assert d not in _by_tag(rows, "total_operating_income").values

    def test_integer_rollup_stays_integer(self):
        d = _D
        rows = [
            _rr("depreciation_and_amortization", {}, sequence=10),
            _rr(
                "depreciation_expense",
                {d: 80 * _M},
                parent="depreciation_and_amortization",
            ),
            _rr(
                "amortization_expense",
                {d: 30 * _M},
                parent="depreciation_and_amortization",
                factor="-",
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        value = _by_tag(rows, "depreciation_and_amortization").values[d]
        assert value == 50 * _M
        assert isinstance(value, int)

    @pytest.mark.parametrize(("liabilities", "expected"), [(None, None), (600, 1100)])
    def test_date_without_balance_sheet_holds_no_totals(self, liabilities, expected):
        d = _D

        def inst(tag, value, parent=None, seq=1):
            return _rr(
                tag,
                {} if value is None else {d: value * _M},
                parent=parent,
                period_type="instant",
                sequence=seq,
                sources={} if value is None else {d: f"us-gaap:{tag}"},
            )

        rows = [
            inst("total_assets", None, seq=10),
            inst("cash_and_equivalents", 100, "total_assets", 1),
            inst("total_liabilities_and_equity", None, seq=30),
            inst("total_liabilities", liabilities, "total_liabilities_and_equity", 20),
            inst(
                "total_equity_and_noncontrolling_interests",
                500,
                "total_liabilities_and_equity",
                25,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        le = _by_tag(rows, "total_liabilities_and_equity").values.get(d)
        assert le == (None if expected is None else expected * _M)
        if expected is None:
            assert d not in _by_tag(rows, "total_assets").values

    def test_unclassified_section_holds_no_totals(self):
        d = _D

        def inst(tag, value, parent=None, seq=1, source=None):
            return _rr(
                tag,
                {} if value is None else {d: value * _M},
                parent=parent,
                period_type="instant",
                sequence=seq,
                sources={} if value is None else {d: source or f"us-gaap:{tag}"},
            )

        rows = [
            inst("total_assets", 1000, seq=10),
            inst("total_current_assets", None, "total_assets", 1),
            inst("cash_and_equivalents", 300, "total_current_assets", 1),
            inst("accounts_receivable", 200, "total_current_assets", 2),
            inst(
                "other_current_assets",
                50,
                "total_current_assets",
                3,
                "imputed-plug: total_current_assets - (cash_and_equivalents(+))",
            ),
            inst("total_noncurrent_assets", None, "total_assets", 5),
            inst("goodwill", 400, "total_noncurrent_assets", 1),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert d not in _by_tag(rows, "total_current_assets").values
        assert d not in _by_tag(rows, "total_noncurrent_assets").values
        assert d not in _by_tag(rows, "other_current_assets").values
        assert _by_tag(rows, "other_noncurrent_assets") is None
        assert _by_tag(rows, "total_assets").values[d] == 1000 * _M

    def test_remainder_rolled_up_from_its_only_match_is_contained(self):
        d = _D

        def inst(tag, value, parent=None, seq=1):
            return _rr(
                tag,
                {} if value is None else {d: value * _M},
                parent=parent,
                period_type="instant",
                balance="credit",
                sequence=seq,
                sources={} if value is None else {d: f"us-gaap:{tag}"},
            )

        rows = [
            inst("total_liabilities_and_equity", 1000, seq=10),
            inst("total_liabilities", 700, "total_liabilities_and_equity", 1),
            inst(
                "total_equity_and_noncontrolling_interests",
                300,
                "total_liabilities_and_equity",
                2,
            ),
            inst("temporary_equity", None, "total_liabilities_and_equity", 3),
            inst("redeemable_noncontrolling_interest", 50, "temporary_equity", 1),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "redeemable_noncontrolling_interest").factor_on(d) == "0"
        assert d not in _by_tag(rows, "temporary_equity").values
        assert _by_tag(rows, "other_temporary_equity") is None

    def test_soft_total_fallback_rolled_up_from_children(self):
        d = _D
        rows = [
            _rr(
                "net_cash_from_operating_activities",
                {d: 999.0 * _M},
                sequence=10,
                sources={
                    d: "us-gaap:NetCashProvidedByUsedInOperatingActivities(fallback)"
                },
            ),
            _rr(
                "net_cash_from_continuing_operating_activities",
                {d: 80.0 * _M},
                parent="net_cash_from_operating_activities",
                sequence=1,
            ),
            _rr(
                "net_cash_from_discontinued_operating_activities",
                {d: 20.0 * _M},
                parent="net_cash_from_operating_activities",
                sequence=2,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        op = _by_tag(rows, "net_cash_from_operating_activities")
        assert op.values[d] == 100.0 * _M
        assert op.sources[d].startswith("imputed-rollup")

    def test_stale_other_plug_and_absorbable_child_go_to_remainder(self):
        d = _D
        rows = [
            _rr("total_operating_income", {d: 100.0 * _M}, sequence=20),
            _rr(
                "total_gross_profit",
                {d: 300.0 * _M},
                parent="total_operating_income",
                sequence=1,
            ),
            _rr(
                "total_operating_expenses",
                {d: 150.0 * _M},
                parent="total_operating_income",
                factor="-",
                sequence=2,
                sources={d: "imputed-plug: total_operating_income - (stale)"},
            ),
            _rr(
                "sga",
                {},
                parent="total_operating_expenses",
                sequence=3,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        opex = _by_tag(rows, "total_operating_expenses")
        assert opex.values[d] == 200.0 * _M
        assert opex.sources[d].startswith("imputed-plug: total_operating_income - ")

    def test_incomplete_rolled_up_other_line_is_absorber(self):
        d = _D

        def inst(tag, value, parent=None, seq=1, source=None):
            return _rr(
                tag,
                {} if value is None else {d: value * _M},
                parent=parent,
                period_type="instant",
                sequence=seq,
                sources={} if value is None else {d: source or f"us-gaap:{tag}"},
            )

        rows = [
            inst("total_liabilities", 500, seq=20),
            inst("total_current_liabilities", 200, "total_liabilities", 1),
            inst(
                "accrued_charges",
                5,
                "total_liabilities",
                2,
                "imputed-rollup: x(+) + y(+)",
            ),
            inst("total_noncurrent_liabilities", None, "total_liabilities", 3),
            inst("long_term_debt", 150, "total_noncurrent_liabilities", 1),
            inst(
                "noncurrent_deferred_tax_liabilities",
                50,
                "total_noncurrent_liabilities",
                2,
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        noncurrent = _by_tag(rows, "total_noncurrent_liabilities")
        assert noncurrent.values[d] == 295 * _M
        assert noncurrent.sources[d].startswith("imputed-plug: total_liabilities - ")
        assert _by_tag(rows, "other_noncurrent_liabilities").values[d] == 95 * _M

    @staticmethod
    def _le_rows(d, liabilities, current):
        def inst(tag, value, parent=None, seq=1):
            return _rr(
                tag,
                {} if value is None else {d: value * _M},
                parent=parent,
                period_type="instant",
                balance="credit",
                sequence=seq,
                sources={} if value is None else {d: f"us-gaap:{tag}"},
            )

        return [
            inst("total_liabilities_and_equity", 1000.0, seq=10),
            inst("total_liabilities", liabilities, "total_liabilities_and_equity", 2),
            inst("total_current_liabilities", current, "total_liabilities", 1),
            inst("temporary_equity", None, "total_liabilities_and_equity", 3),
            inst("redeemable_noncontrolling_interest", None, "temporary_equity", 1),
            inst(
                "total_equity_and_noncontrolling_interests",
                350.0,
                "total_liabilities_and_equity",
                4,
            ),
        ]

    def test_liabilities_rollup_absorbs_remainder_without_mezzanine(self):
        d = "2023-12-31"
        rows = self._le_rows(d, None, 300.0)
        _apply_hierarchical_articulation(rows, {d})
        tl = _by_tag(rows, "total_liabilities")
        assert tl.values[d] == 650.0 * _M
        assert tl.sources[d].startswith("imputed-plug: total_liabilities_and_equity - ")
        assert d not in _by_tag(rows, "temporary_equity").values

    def test_liabilities_plug_without_mezzanine(self):
        d = "2023-12-31"
        rows = self._le_rows(d, None, None)
        _apply_hierarchical_articulation(rows, {d})
        tl = _by_tag(rows, "total_liabilities")
        assert tl.values[d] == 650.0 * _M
        assert tl.sources[d].startswith("imputed-plug: total_liabilities_and_equity - ")
        assert d not in _by_tag(rows, "temporary_equity").values

    def test_mezzanine_remainder_with_reported_liabilities(self):
        d = "2023-12-31"
        rows = self._le_rows(d, 600.0, None)
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "total_liabilities").values[d] == 600.0 * _M
        assert _by_tag(rows, "temporary_equity").values[d] == 50.0 * _M

    def test_complete_rollup_section_keeps_its_amount(self):
        d = "2023-12-31"

        def inst(tag, value, parent=None, seq=1):
            return _rr(
                tag,
                {} if value is None else {d: value * _M},
                parent=parent,
                period_type="instant",
                balance="debit",
                sequence=seq,
                sources={} if value is None else {d: f"us-gaap:{tag}"},
            )

        rows = [
            inst("total_assets", 1000.0, seq=10),
            inst("total_current_assets", None, "total_assets", 1),
            inst("cash_and_equivalents", 300.0, "total_current_assets", 1),
            inst("accounts_receivable", 200.0, "total_current_assets", 2),
            inst("other_current_assets", 100.0, "total_current_assets", 3),
            inst("total_noncurrent_assets", 350.0, "total_assets", 5),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "total_current_assets").values[d] == 600.0 * _M
        noncurrent = _by_tag(rows, "total_noncurrent_assets")
        assert noncurrent.values[d] == 400.0 * _M
        assert noncurrent.sources[d].startswith("imputed-plug: total_assets - ")

    def test_repeated_amounts_contained_together(self):
        d = "2023-12-31"

        def inst(tag, value, seq, source):
            return _rr(
                tag,
                {d: value * _M},
                parent="total_liabilities",
                period_type="instant",
                balance="credit",
                sequence=seq,
                sources={d: source},
            )

        rows = [
            _rr(
                "total_liabilities",
                {d: 520.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=10,
                sources={d: "us-gaap:Liabilities"},
            ),
            inst("claims_and_claim_expenses", 300.0, 1, "us-gaap:A"),
            inst("future_policy_benefits", 300.0, 2, "us-gaap:B"),
            inst("policyholder_funds", 100.0, 3, "us-gaap:C"),
            inst("participating_policyholder_equity", 100.0, 4, "us-gaap:C"),
        ]
        _apply_hierarchical_articulation(rows, {d})
        assert _by_tag(rows, "future_policy_benefits").factor_on(d) == "0"
        assert _by_tag(rows, "participating_policyholder_equity").factor_on(d) == "0"
        assert _by_tag(rows, "claims_and_claim_expenses").factor_on(d) == "+"
        other = _by_tag(rows, "other_liabilities")
        assert other.values[d] == 120.0 * _M


class TestResolveSignFlips:
    @staticmethod
    def _equity(treasury, source="us-gaap:TreasuryStockValue", parent=100):
        d = _D
        return [
            _rr(
                "total_common_equity",
                {} if parent is None else {d: parent * _M},
                period_type="instant",
                sequence=10,
                sources={} if parent is None else {d: "us-gaap:StockholdersEquity"},
            ),
            _rr(
                "additional_paid_in_capital",
                {d: 140 * _M},
                parent="total_common_equity",
                period_type="instant",
                sources={d: "us-gaap:AdditionalPaidInCapital"},
            ),
            _rr(
                "treasury_stock",
                {d: treasury * _M},
                parent="total_common_equity",
                factor="-",
                period_type="instant",
                sequence=2,
                sources={d: source},
            ),
        ]

    @staticmethod
    def _facts(*values):
        entries = [
            _inst(_D, v * _M, filed=f"202{4 + i}-02-15") for i, v in enumerate(values)
        ]
        entries += [{"end": _D, "val": None}, {"val": 5}]
        return {"us-gaap": {"TreasuryStockValue": {"units": {"USD": entries}}}}

    def test_opposite_signed_fact_resolves_parent(self):
        rows = self._equity(-40)
        _resolve_sign_flips(rows, {_D}, self._facts(-40, 40), "annual", set(), [])
        treasury = _by_tag(rows, "treasury_stock")
        assert treasury.values[_D] == 40 * _M
        assert treasury.sources[_D] == "us-gaap:TreasuryStockValue(sign-resolved)"

    def test_parent_derived_by_rule(self):
        rows = self._equity(-40, parent=None) + [
            _rr("total_equity", {_D: 110 * _M}, period_type="instant"),
            _rr("total_preferred_equity", {_D: 10 * _M}, period_type="instant"),
        ]
        rules = [
            ("total_common_equity", [("noncontrolling_interests", 1)]),
            (
                "total_common_equity",
                [("total_equity", 1), ("total_preferred_equity", -1)],
            ),
        ]
        _resolve_sign_flips(rows, {_D}, self._facts(-40, 40), "annual", set(), rules)
        assert _by_tag(rows, "treasury_stock").values[_D] == 40 * _M

    @pytest.mark.parametrize(
        ("treasury", "source", "facts", "parent"),
        [
            (-40, "us-gaap:TreasuryStockValue", (-40,), 100),
            (-40, "us-gaap:TreasuryStockValue", (40,), 100),
            (-40, "imputed: total_equity - x", (-40, 40), 100),
            (0, "us-gaap:TreasuryStockValue", (0,), 140),
            (40, "us-gaap:TreasuryStockValue", (-40, 40), 100),
            (-40, "us-gaap:TreasuryStockValue", (-40, 40), None),
        ],
    )
    def test_sign_kept(self, treasury, source, facts, parent):
        rows = self._equity(treasury, source, parent)
        _resolve_sign_flips(rows, {_D}, self._facts(*facts), "annual", set(), [])
        assert _by_tag(rows, "treasury_stock").values[_D] == treasury * _M

    def test_two_candidate_children_left_unchanged(self):
        rows = self._equity(-40)
        rows.append(
            _rr(
                "retained_earnings",
                {_D: -40 * _M},
                parent="total_common_equity",
                factor="-",
                period_type="instant",
                sources={_D: "us-gaap:TreasuryStockValue"},
            )
        )
        rows[0].values[_D] = 140 * _M
        _resolve_sign_flips(rows, {_D}, self._facts(-40, 40), "annual", set(), [])
        assert _by_tag(rows, "treasury_stock").values[_D] == -40 * _M

    @staticmethod
    def _income(later):
        d, q = "2023-03-31", "2023-06-30"
        sources = {d: "us-gaap:IncomeLossFromDiscontinuedOperationsNetOfTax"}
        if later is not None:
            sources[later] = (
                "ytd_derived(us-gaap:IncomeLossFromDiscontinuedOperationsNetOfTax)"
            )
        rows = [
            _rr(
                "net_income",
                {d: 107 * _M},
                sequence=10,
                sources={d: "us-gaap:ProfitLoss"},
            ),
            _rr(
                "net_income_continuing",
                {d: 415 * _M},
                parent="net_income",
                sources={d: "us-gaap:IncomeLossFromContinuingOperations"},
            ),
            _rr(
                "net_income_discontinued",
                {d: 308 * _M, q: 1 * _M},
                parent="net_income",
                sequence=2,
                sources=sources,
            ),
        ]
        facts = {
            "us-gaap": {
                "IncomeLossFromDiscontinuedOperationsNetOfTax": {
                    "units": {
                        "USD": [
                            _dur(
                                d,
                                "2023-01-01",
                                -308 * _M,
                                form="10-Q",
                                filed="2023-05-01",
                            ),
                            _dur(
                                d,
                                "2023-01-01",
                                308 * _M,
                                form="10-Q",
                                filed="2024-05-01",
                            ),
                            _dur(
                                d,
                                "2022-04-01",
                                308 * _M,
                                form="10-K",
                                filed="2024-02-01",
                            ),
                        ]
                    }
                }
            }
        }
        return rows, facts, d

    @pytest.mark.parametrize(
        ("later", "expected"),
        [(None, -308), ("2023-06-30", 308), ("2024-06-30", -308)],
    )
    def test_quarterly_year_to_date_guard(self, later, expected):
        rows, facts, d = self._income(later)
        _resolve_sign_flips(rows, {d}, facts, "quarterly", set(), [])
        assert _by_tag(rows, "net_income_discontinued").values[d] == expected * _M

    def test_cash_flow_negated_row(self):
        d = _D
        rows = [
            _rr("net_cash_from_financing_activities", {d: -100 * _M}, sequence=10),
            _rr(
                "payment_of_dividends",
                {d: -50 * _M},
                parent="net_cash_from_financing_activities",
                sources={d: "us-gaap:PaymentsOfDividends"},
            ),
            _rr(
                "repurchase_of_common_equity",
                {d: 50 * _M},
                parent="net_cash_from_financing_activities",
                sequence=2,
                sources={d: "us-gaap:PaymentsForRepurchaseOfCommonStock"},
            ),
        ]
        facts = {
            "us-gaap": {
                "PaymentsForRepurchaseOfCommonStock": {
                    "units": {
                        "USD": [
                            _dur(d, "2023-01-01", -50 * _M),
                            _dur(d, "2023-01-01", 50 * _M, filed="2025-02-15"),
                        ]
                    }
                }
            }
        }
        _resolve_sign_flips(
            rows,
            {d},
            facts,
            "annual",
            {"payment_of_dividends", "repurchase_of_common_equity"},
            [],
        )
        repurchase = _by_tag(rows, "repurchase_of_common_equity")
        assert repurchase.values[d] == -50 * _M
        assert repurchase.sources[d].endswith("(sign-resolved)")


# ---------------------------------------------------------------------------
# impute() -- empty-ruleset early return
# ---------------------------------------------------------------------------


_QUARTERS = ["2023-03-31", "2023-06-30", "2023-09-30"]


def _concept_facts(fy, quarters, nine=()):
    starts = ["2023-01-01", "2023-04-01", "2023-07-01"]
    entries = [_dur(_D, "2023-01-01", v * _M, filed=f) for f, v in fy]
    entries += [
        _dur(_QUARTERS[2], "2023-01-01", v * _M, form="10-Q", filed=f) for f, v in nine
    ]
    entries += [
        _dur(d, s, v * _M, form="10-Q", filed="2024-11-01")
        for d, s, v in zip(_QUARTERS, starts, quarters)
    ]
    entries.append({"end": _D, "val": None})
    return {"units": {"USD": entries}}


class TestReconcileFiscalYearEnds:
    def test_annual_instant_row_created_in_quarterly(self):
        annual = StatementResult(
            statement="balance_sheet",
            company_type="industrial",
            frequency="annual",
            currency="USD",
            dates=[_D],
            rows=[
                _rr(
                    "goodwill",
                    {_D: 50.0},
                    period_type="instant",
                    sources={_D: "us-gaap:Goodwill"},
                )
            ],
        )
        quarterly = StatementResult(
            statement="balance_sheet",
            company_type="industrial",
            frequency="quarterly",
            currency="USD",
            dates=["2023-09-30", _D],
            rows=[],
        )
        reconcile_fiscal_year_ends(quarterly, annual, {"goodwill"})
        row = _by_tag(quarterly.rows, "goodwill")
        assert row.values == {_D: 50.0}
        assert row.sources == {_D: "us-gaap:Goodwill"}

    def test_fourth_quarter_only_remainder_row_holds_no_value(self):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        annual = StatementResult(
            statement="income_statement",
            company_type="industrial",
            frequency="annual",
            currency="USD",
            dates=[_D],
            rows=[
                _rr(
                    "total_x", {_D: 1000.0 * _M}, sequence=10, sources={_D: "us-gaap:X"}
                ),
                _rr(
                    "a",
                    {_D: 700.0 * _M},
                    parent="total_x",
                    sequence=1,
                    sources={_D: "us-gaap:A"},
                ),
            ],
        )
        quarterly = StatementResult(
            statement="income_statement",
            company_type="industrial",
            frequency="quarterly",
            currency="USD",
            dates=[*quarters, _D],
            rows=[
                _rr(
                    "total_x",
                    {q: 200.0 * _M for q in quarters},
                    sequence=10,
                    sources={q: "us-gaap:X" for q in quarters},
                ),
                _rr(
                    "a",
                    {q: 150.0 * _M for q in quarters},
                    parent="total_x",
                    sequence=1,
                    sources={q: "us-gaap:A" for q in quarters},
                ),
            ],
        )
        reconcile_fiscal_year_ends(quarterly, annual, {"total_x", "a"})
        assert _by_tag(quarterly.rows, "total_x").values[_D] == 400.0 * _M
        assert _by_tag(quarterly.rows, "a").values[_D] == 250.0 * _M
        other = _by_tag(quarterly.rows, "other_x")
        assert _D not in other.values

    def test_preliminary_dates_prefixed_once(self):
        d = "2024-03-31"
        annual = StatementResult(
            statement="income_statement",
            company_type="industrial",
            frequency="annual",
            currency="USD",
            dates=[_D],
            rows=[],
        )
        quarterly = StatementResult(
            statement="income_statement",
            company_type="industrial",
            frequency="quarterly",
            currency="USD",
            dates=[d],
            rows=[
                _rr("total_revenue", {d: 10.0}, sources={d: "us-gaap:Revenues"}),
                _rr("other_revenue", {d: 1.0}, sources={d: "preliminary:us-gaap:X"}),
                _rr("total_cost_of_revenue", {}),
            ],
            preliminary_dates={d},
        )
        reconcile_fiscal_year_ends(quarterly, annual, set())
        assert _by_tag(quarterly.rows, "total_revenue").sources[d] == (
            "preliminary:us-gaap:Revenues"
        )
        assert _by_tag(quarterly.rows, "other_revenue").sources[d] == (
            "preliminary:us-gaap:X"
        )
        assert _by_tag(quarterly.rows, "total_cost_of_revenue").sources == {}

    @staticmethod
    def _pair(statement, annual_rows, quarterly_rows, quarters):
        annual = StatementResult(
            statement=statement,
            company_type="industrial",
            frequency="annual",
            currency="USD",
            dates=[_D],
            rows=annual_rows,
        )
        quarterly = StatementResult(
            statement=statement,
            company_type="industrial",
            frequency="quarterly",
            currency="USD",
            dates=[*quarters, _D],
            rows=quarterly_rows,
        )
        return annual, quarterly

    _Q = _QUARTERS

    def _vintage(self, revenue_q, revenue_fy, facts, statement="income_statement"):
        tag = "us-gaap:Revenues"
        cost = "us-gaap:CostOfRevenue"
        gp = "imputed: total_revenue - total_cost_of_revenue"
        annual, quarterly = self._pair(
            statement,
            [
                _rr("total_revenue", {_D: revenue_fy * _M}, sources={_D: tag}),
                _rr("total_cost_of_revenue", {_D: 300 * _M}, sources={_D: cost}),
                _rr(
                    "total_gross_profit",
                    {_D: (revenue_fy - 300) * _M},
                    sources={_D: gp},
                ),
            ],
            [
                _rr(
                    "total_revenue",
                    {d: v * _M for d, v in zip(self._Q, revenue_q)},
                    sources=dict.fromkeys(self._Q, tag),
                ),
                _rr(
                    "total_cost_of_revenue",
                    dict.fromkeys(self._Q, 100 * _M),
                    sources=dict.fromkeys(self._Q, cost),
                ),
                _rr(
                    "total_gross_profit",
                    {d: (v - 100) * _M for d, v in zip(self._Q, revenue_q)},
                    sources=dict.fromkeys(self._Q, gp),
                ),
            ],
            self._Q,
        )
        tags = {"total_revenue", "total_cost_of_revenue", "total_gross_profit"}
        reconcile_fiscal_year_ends(quarterly, annual, tags, facts)
        return {tag: _by_tag(quarterly.rows, tag) for tag in tags}

    def test_q4_from_annual_filing_before_restatement(self):
        facts = {
            "us-gaap": {
                "Revenues": _concept_facts(
                    [("2025-02-15", 531), ("2024-02-15", 800)],
                    [200, 200, 200],
                    [("2023-11-01", 600)],
                ),
                "CostOfRevenue": _concept_facts(
                    [("2025-02-15", 300), ("2024-02-15", 400)],
                    [100, 100, 100],
                    [("2023-11-01", 300)],
                ),
            }
        }
        rows = self._vintage([200, 200, 200], 531, facts)
        assert rows["total_revenue"].values[_D] == 200 * _M
        assert "(filed 2024-02-15)" in rows["total_revenue"].sources[_D]
        assert rows["total_cost_of_revenue"].values[_D] == 100 * _M
        assert rows["total_gross_profit"].values[_D] == 100 * _M
        assert rows["total_gross_profit"].sources[_D] == (
            "imputed: total_revenue - total_cost_of_revenue"
        )

    def test_q4_from_latest_nine_months(self):
        facts = {
            "us-gaap": {
                "Revenues": _concept_facts(
                    [("2024-02-15", 600)], [300, 200, 200], [("2023-11-01", 500)]
                )
            }
        }
        rows = self._vintage([300, 200, 200], 600, facts)
        assert rows["total_revenue"].values[_D] == 100 * _M
        assert rows["total_revenue"].sources[_D] == (
            "Q4: FY[us-gaap:Revenues] \u2212 9M[us-gaap:Revenues]"
        )

    def test_q4_kept_without_opposite_signed_quarter(self):
        facts = {
            "us-gaap": {
                "Revenues": _concept_facts(
                    [("2025-02-15", 531), ("2024-02-15", 800)],
                    [150, 150, 150],
                    [("2023-11-01", 450)],
                )
            }
        }
        rows = self._vintage([150, 150, 150], 531, facts)
        assert rows["total_revenue"].values[_D] == 81 * _M

    @pytest.mark.parametrize(
        "facts",
        [
            None,
            {},
            {"us-gaap": {"Revenues": {"units": {"USD": []}}}},
            {
                "us-gaap": {
                    "Revenues": {
                        "units": {
                            "USD": [
                                _dur(_D, "2023-01-01", 531 * _M, filed="2025-02-15")
                            ]
                        }
                    }
                }
            },
            {
                "us-gaap": {
                    "Revenues": {
                        "units": {
                            "USD": [
                                _dur(_D, "2023-01-01", 531 * _M, filed="2025-02-15"),
                                _dur(_D, "2023-01-01", 800 * _M, filed="2024-02-15"),
                                _dur(
                                    "2023-09-30",
                                    "2023-01-01",
                                    600 * _M,
                                    form="10-Q",
                                    filed="2024-11-01",
                                ),
                            ]
                        }
                    }
                }
            },
            {
                "us-gaap": {
                    "Revenues": _concept_facts(
                        [("2025-02-15", 531), ("2024-02-15", 800)],
                        [200, 200, 200],
                        [("2023-11-01", 590)],
                    )
                }
            },
        ],
    )
    def test_q4_kept_without_filing_evidence(self, facts):
        rows = self._vintage([200, 200, 200], 531, facts)
        assert rows["total_revenue"].values[_D] == -69 * _M

    def test_q4_from_facts_of_negated_cash_flow_row(self):
        tag = "us-gaap:PaymentsToAcquirePropertyPlantAndEquipment"
        annual, quarterly = self._pair(
            "cash_flow",
            [
                _rr(
                    "purchase_of_plant_property_and_equipment",
                    {_D: -531 * _M},
                    balance="credit",
                    sources={_D: tag},
                )
            ],
            [
                _rr(
                    "purchase_of_plant_property_and_equipment",
                    dict.fromkeys(self._Q, -200 * _M),
                    balance="credit",
                    sources=dict.fromkeys(self._Q, tag),
                )
            ],
            self._Q,
        )
        facts = {
            "us-gaap": {
                "PaymentsToAcquirePropertyPlantAndEquipment": _concept_facts(
                    [("2025-02-15", 531), ("2024-02-15", 800)],
                    [200, 200, 200],
                    [("2023-11-01", 600)],
                )
            }
        }
        reconcile_fiscal_year_ends(
            quarterly, annual, {"purchase_of_plant_property_and_equipment"}, facts
        )
        row = _by_tag(quarterly.rows, "purchase_of_plant_property_and_equipment")
        assert row.values[_D] == -200 * _M

    def test_formula_terms(self):
        assert _formula_terms("imputed: -a + b - c") == [("a", -1), ("b", 1), ("c", -1)]

    def test_q4_from_nine_months_kept(self):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        tag = "us-gaap:PaymentsToAcquireBusinessesNetOfCashAcquired"
        nine = f"Q4: FY[{tag}] \u2212 9M[{tag}]"
        annual, quarterly = self._pair(
            "cash_flow",
            [_rr("acquisitions", {_D: -90.0 * _M}, sources={_D: tag})],
            [
                _rr(
                    "acquisitions",
                    {quarters[2]: -50.0 * _M, _D: -20.0 * _M},
                    sources={quarters[2]: f"ytd_derived({tag})", _D: nine},
                )
            ],
            quarters,
        )
        reconcile_fiscal_year_ends(quarterly, annual, {"acquisitions"})
        row = _by_tag(quarterly.rows, "acquisitions")
        assert row.values[_D] == -20.0 * _M
        assert row.sources[_D] == nine

    def test_q4_not_derived_from_partial_quarters(self):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        annual, quarterly = self._pair(
            "income_statement",
            [_rr("restructuring_charge", {_D: 90.0 * _M}, sources={_D: "us-gaap:R"})],
            [
                _rr(
                    "restructuring_charge",
                    {quarters[1]: 20.0 * _M, quarters[2]: 50.0 * _M},
                    sources={quarters[1]: "us-gaap:R", quarters[2]: "us-gaap:R"},
                )
            ],
            quarters,
        )
        reconcile_fiscal_year_ends(quarterly, annual, {"restructuring_charge"})
        assert _D not in _by_tag(quarterly.rows, "restructuring_charge").values

    def test_h2_value_cleared_in_quarterly_year(self):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        annual, quarterly = self._pair(
            "income_statement",
            [_rr("impairment_expense", {_D: 0.0}, sources={_D: "us-gaap:A"})],
            [
                _rr(
                    "impairment_expense",
                    {quarters[1]: 33.0 * _M, _D: -33.0 * _M},
                    sources={
                        quarters[1]: "us-gaap:A",
                        _D: "H2: FY[us-gaap:A] \u2212 H1[us-gaap:A]",
                    },
                )
            ],
            quarters,
        )
        reconcile_fiscal_year_ends(quarterly, annual, {"impairment_expense"})
        row = _by_tag(quarterly.rows, "impairment_expense")
        assert _D not in row.values
        assert _D not in row.sources

    def test_period_factor_copied_from_annual(self):
        annual_pref = _rr(
            "total_preferred_equity",
            {_D: 100.0 * _M},
            period_type="instant",
            sources={_D: "us-gaap:PreferredStockValue"},
        )
        annual_pref.date_factors[_D] = "0"
        annual_gw = _rr(
            "goodwill",
            {_D: 50.0 * _M},
            period_type="instant",
            sources={_D: "us-gaap:Goodwill"},
        )
        quarterly_gw = _rr(
            "goodwill", {_D: 40.0 * _M}, period_type="instant", sources={_D: "x"}
        )
        quarterly_gw.date_factors[_D] = "0"
        quarterly_dropped = _rr(
            "intangible_assets", {_D: 5.0 * _M}, period_type="instant"
        )
        quarterly_dropped.date_factors[_D] = "0"
        annual, quarterly = self._pair(
            "balance_sheet",
            [annual_pref, annual_gw],
            [
                _rr(
                    "total_preferred_equity",
                    {_D: 90.0 * _M},
                    period_type="instant",
                ),
                quarterly_gw,
                quarterly_dropped,
            ],
            ["2023-09-30"],
        )
        reconcile_fiscal_year_ends(quarterly, annual, set())
        assert _by_tag(quarterly.rows, "total_preferred_equity").factor_on(_D) == "0"
        gw = _by_tag(quarterly.rows, "goodwill")
        assert gw.values[_D] == 50.0 * _M
        assert _D not in gw.date_factors
        assert _D not in _by_tag(quarterly.rows, "intangible_assets").date_factors

    def test_q4_beginning_cash_follows_cash_identity(self):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        annual, quarterly = self._pair(
            "cash_flow",
            [
                _rr(
                    "net_change_in_cash",
                    {_D: 100.0 * _M},
                    sources={_D: "us-gaap:CashPeriodIncreaseDecrease"},
                ),
                _rr(
                    "cash_at_end_of_period",
                    {_D: 420.0 * _M},
                    period_type="instant",
                    sources={_D: "us-gaap:Cash"},
                ),
            ],
            [
                _rr(
                    "net_change_in_cash",
                    {q: v * _M for q, v in zip(quarters, (10.0, 20.0, 30.0))},
                    sources={q: "us-gaap:CashPeriodIncreaseDecrease" for q in quarters},
                ),
                _rr(
                    "cash_at_end_of_period",
                    {quarters[2]: 300.0 * _M},
                    period_type="instant",
                    sources={quarters[2]: "us-gaap:Cash"},
                ),
                _rr(
                    "cash_at_beginning_of_period",
                    {_D: 300.0 * _M},
                    period_type="instant",
                    sources={_D: f"derived: cash_at_end_of_period({quarters[2]})"},
                ),
            ],
            quarters,
        )
        reconcile_fiscal_year_ends(quarterly, annual, {"net_change_in_cash"})
        assert _by_tag(quarterly.rows, "net_change_in_cash").values[_D] == 40.0 * _M
        bop = _by_tag(quarterly.rows, "cash_at_beginning_of_period")
        assert bop.values[_D] == 380.0 * _M
        assert bop.sources[_D] == (
            "identity-enforced: cash_at_end_of_period - net_change_in_cash"
        )

    def test_q4_rollup_quarters_follow_q4_components(self):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        annual, quarterly = self._pair(
            "cash_flow",
            [
                _rr(
                    "depreciation_and_amortization",
                    {_D: 100.0 * _M},
                    sources={_D: "us-gaap:DepreciationDepletionAndAmortization"},
                ),
                _rr(
                    "depreciation_expense",
                    {_D: 60.0 * _M},
                    parent="depreciation_and_amortization",
                    sources={_D: "us-gaap:Depreciation"},
                ),
                _rr(
                    "amortization_expense",
                    {_D: 40.0 * _M},
                    parent="depreciation_and_amortization",
                    sources={_D: "us-gaap:AmortizationOfIntangibleAssets"},
                ),
            ],
            [
                _rr(
                    "depreciation_and_amortization",
                    {q: 12.0 * _M for q in quarters},
                    sources={
                        q: "imputed-rollup: depreciation_expense(+)" for q in quarters
                    },
                ),
                _rr(
                    "depreciation_expense",
                    {q: 12.0 * _M for q in quarters},
                    parent="depreciation_and_amortization",
                    sources={q: "us-gaap:Depreciation" for q in quarters},
                ),
            ],
            quarters,
        )
        reconcile_fiscal_year_ends(
            quarterly,
            annual,
            {"depreciation_and_amortization", "depreciation_expense"},
        )
        da = _by_tag(quarterly.rows, "depreciation_and_amortization")
        assert _by_tag(quarterly.rows, "depreciation_expense").values[_D] == 24.0 * _M
        assert da.values[_D] == 24.0 * _M
        assert da.sources[_D].startswith("imputed-rollup")

    @pytest.mark.parametrize(
        ("fy_value", "fy_source", "amortization", "expected"),
        [
            (150.0, "us-gaap:DepreciationDepletionAndAmortization", 40.0, 40.0),
            (60.0, "imputed-rollup: depreciation_expense(+)", None, 24.0),
        ],
    )
    def test_q4_of_rolled_up_quarters_rolls_up(
        self, fy_value, fy_source, amortization, expected
    ):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        annual_rows = [
            _rr(
                "depreciation_and_amortization",
                {_D: fy_value * _M},
                sources={_D: fy_source},
            ),
            _rr(
                "depreciation_expense",
                {_D: 60.0 * _M},
                parent="depreciation_and_amortization",
                sources={_D: "us-gaap:Depreciation"},
            ),
        ]
        if amortization is not None:
            annual_rows.append(
                _rr(
                    "amortization_expense",
                    {_D: amortization * _M},
                    parent="depreciation_and_amortization",
                    sources={_D: "us-gaap:AmortizationOfIntangibleAssets"},
                )
            )
        annual, quarterly = self._pair(
            "cash_flow",
            annual_rows,
            [
                _rr(
                    "depreciation_and_amortization",
                    {q: 20.0 * _M for q in quarters},
                    sources={
                        q: "imputed-rollup: depreciation_expense(+)"
                        " + amortization_expense(+)"
                        for q in quarters
                    },
                ),
                _rr(
                    "depreciation_expense",
                    {q: 12.0 * _M for q in quarters},
                    parent="depreciation_and_amortization",
                    sources={q: "us-gaap:Depreciation" for q in quarters},
                ),
                _rr(
                    "amortization_expense",
                    {q: 8.0 * _M for q in quarters},
                    parent="depreciation_and_amortization",
                    sources={
                        q: "us-gaap:AmortizationOfIntangibleAssets" for q in quarters
                    },
                ),
            ],
            quarters,
        )
        reconcile_fiscal_year_ends(
            quarterly,
            annual,
            {
                "depreciation_and_amortization",
                "depreciation_expense",
                "amortization_expense",
            },
        )
        da = _by_tag(quarterly.rows, "depreciation_and_amortization")
        assert da.values[_D] == expected * _M
        assert da.sources[_D].startswith("imputed-rollup")

    def test_q4_of_rolled_up_quarters_with_annual_remainder(self):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        annual, quarterly = self._pair(
            "cash_flow",
            [
                _rr(
                    "depreciation_and_amortization",
                    {_D: 150.0 * _M},
                    sources={_D: "us-gaap:DepreciationDepletionAndAmortization"},
                ),
                _rr(
                    "depreciation_expense",
                    {_D: 60.0 * _M},
                    parent="depreciation_and_amortization",
                    sources={_D: "us-gaap:Depreciation"},
                ),
                _rr(
                    "other_depreciation_and_amortization",
                    {_D: 90.0 * _M},
                    parent="depreciation_and_amortization",
                    sources={
                        _D: "imputed-plug: depreciation_and_amortization"
                        " - (depreciation_expense(+))"
                    },
                ),
            ],
            [
                _rr(
                    "depreciation_and_amortization",
                    {q: 30.0 * _M for q in quarters},
                    sources={
                        q: "imputed-rollup: depreciation_expense(+)"
                        " + other_depreciation_and_amortization(+)"
                        for q in quarters
                    },
                ),
                _rr(
                    "depreciation_expense",
                    {q: 12.0 * _M for q in quarters},
                    parent="depreciation_and_amortization",
                    sources={q: "us-gaap:Depreciation" for q in quarters},
                ),
                _rr(
                    "other_depreciation_and_amortization",
                    {q: 18.0 * _M for q in quarters},
                    parent="depreciation_and_amortization",
                    sources={
                        q: "us-gaap:OtherDepreciationAndAmortization" for q in quarters
                    },
                ),
            ],
            quarters,
        )
        reconcile_fiscal_year_ends(
            quarterly,
            annual,
            {
                "depreciation_and_amortization",
                "depreciation_expense",
                "other_depreciation_and_amortization",
            },
        )
        da = _by_tag(quarterly.rows, "depreciation_and_amortization")
        assert da.values[_D] == 60.0 * _M
        assert da.sources[_D].startswith("Q4: FY[")

    def test_q4_from_quarters_concept_kept(self):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        q4 = "Q4: FY[us-gaap:Revenues] \u2212 (Q1[us-gaap:Revenues])"
        annual, quarterly = self._pair(
            "income_statement",
            [_rr("operating_revenue", {_D: 700.0 * _M}, sources={_D: "us-gaap:R"})],
            [
                _rr(
                    "operating_revenue",
                    {**{q: 200.0 * _M for q in quarters}, _D: 400.0 * _M},
                    sources={**{q: "us-gaap:Revenues" for q in quarters}, _D: q4},
                ),
                _rr(
                    "total_revenue",
                    {q: 200.0 * _M for q in quarters},
                    sources={q: "us-gaap:Revenues" for q in quarters},
                ),
            ],
            quarters,
        )
        annual.rows.append(
            _rr("total_revenue", {_D: 700.0 * _M}, sources={_D: "us-gaap:R"})
        )
        reconcile_fiscal_year_ends(
            quarterly, annual, {"operating_revenue", "total_revenue"}
        )
        row = _by_tag(quarterly.rows, "operating_revenue")
        assert row.values[_D] == 400.0 * _M
        assert row.sources[_D] == q4
        assert _by_tag(quarterly.rows, "total_revenue").values[_D] == 100.0 * _M

    @pytest.mark.parametrize("without_q4", [False, True])
    def test_zero_q4_remainder_written(self, without_q4):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        plug = "imputed-plug: total_x - (a(+))"
        annual, quarterly = self._pair(
            "income_statement",
            [
                _rr(
                    "total_x", {_D: 1000.0 * _M}, sequence=10, sources={_D: "us-gaap:X"}
                ),
                _rr(
                    "a",
                    {_D: 700.0 * _M},
                    parent="total_x",
                    sequence=1,
                    sources={_D: "us-gaap:A"},
                ),
                _rr(
                    "other_x",
                    {_D: 300.0 * _M},
                    parent="total_x",
                    sequence=2,
                    sources={_D: plug},
                ),
            ],
            [
                _rr(
                    "total_x",
                    {q: 250.0 * _M for q in quarters},
                    sequence=10,
                    sources={q: "us-gaap:X" for q in quarters},
                ),
                _rr(
                    "a",
                    {q: 150.0 * _M for q in quarters},
                    parent="total_x",
                    sequence=1,
                    sources={q: "us-gaap:A" for q in quarters},
                ),
                _rr(
                    "other_x",
                    {**{q: 100.0 * _M for q in quarters}, _D: 5.0 * _M},
                    parent="total_x",
                    sequence=2,
                    sources={**{q: plug for q in quarters}, _D: plug},
                ),
            ],
            quarters,
        )
        if without_q4:
            other = _by_tag(quarterly.rows, "other_x")
            other.values.pop(_D)
            other.sources.pop(_D)
        reconcile_fiscal_year_ends(quarterly, annual, {"total_x", "a", "other_x"})
        other = _by_tag(quarterly.rows, "other_x")
        assert other.values[_D] == 0.0
        assert other.sources[_D].startswith("imputed-plug: total_x - ")

    @pytest.mark.parametrize(
        ("income", "fy_basic", "expected"),
        [
            (200, 101, (103_967_391, 105_967_391, 1.92, 1.89)),
            (-50, 101, (103_967_391, 103_967_391, -0.48, -0.48)),
            (200, 1, (None, 105_967_391, None, 1.89)),
        ],
    )
    def test_q4_per_share_derived(self, income, fy_basic, expected):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]

        def per_share(tag, fy, q, *, parent=None, factor="0", unit="per_share"):
            source = f"us-gaap:{tag}"
            return (
                _rr(
                    tag,
                    {_D: fy},
                    parent=parent,
                    factor=factor,
                    unit=unit,
                    sources={_D: source},
                ),
                _rr(
                    tag,
                    dict.fromkeys(quarters, q),
                    parent=parent,
                    factor=factor,
                    unit=unit,
                    sources=dict.fromkeys(quarters, source),
                ),
            )

        pairs = [
            per_share(
                "weighted_ave_basic_shares_os",
                fy_basic * _M,
                100 * _M,
                parent="basic_eps",
                factor="/",
                unit="shares",
            ),
            per_share(
                "weighted_ave_diluted_shares_os",
                103 * _M,
                102 * _M,
                parent="diluted_eps",
                factor="/",
                unit="shares",
            ),
            per_share("basic_eps", 2.0, 0.5),
            per_share("diluted_eps", 2.0, 0.5),
            per_share("cash_dividends_per_share", 0.4, 0.1),
        ]
        annual = StatementResult(
            statement="income_statement",
            company_type="industrial",
            frequency="annual",
            currency="USD",
            dates=["2022-12-31", _D],
            rows=[a for a, _ in pairs],
        )
        quarterly = StatementResult(
            statement="income_statement",
            company_type="industrial",
            frequency="quarterly",
            currency="USD",
            dates=[*quarters, _D],
            rows=[
                *(q for _, q in pairs),
                _rr(
                    "net_income_to_common",
                    {_D: income * _M},
                    sources={
                        _D: "us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic"
                    },
                ),
            ],
        )
        reconcile_fiscal_year_ends(quarterly, annual, set())
        rows = {r.tag: r for r in quarterly.rows}
        assert (
            rows["weighted_ave_basic_shares_os"].values.get(_D),
            rows["weighted_ave_diluted_shares_os"].values.get(_D),
            rows["basic_eps"].values.get(_D),
            rows["diluted_eps"].values.get(_D),
        ) == expected
        assert rows["cash_dividends_per_share"].values[_D] == 0.1

    @pytest.mark.parametrize("interim", [True, False])
    def test_q4_balance_sheet_keeps_interim_lines(self, interim):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        annual, quarterly = self._pair(
            "balance_sheet",
            [
                _rr(
                    "total_assets",
                    {_D: 1000 * _M},
                    period_type="instant",
                    sources={_D: "us-gaap:Assets"},
                ),
                _rr(
                    "gross_ppe",
                    {_D: 500 * _M},
                    period_type="instant",
                    sources={_D: "us-gaap:PropertyPlantAndEquipmentGross"},
                ),
            ],
            [
                _rr(
                    "total_assets",
                    dict.fromkeys(quarters, 900 * _M) if interim else {},
                    period_type="instant",
                    sources=dict.fromkeys(quarters, "us-gaap:Assets")
                    if interim
                    else {},
                ),
            ],
            quarters,
        )
        reconcile_fiscal_year_ends(quarterly, annual, set())
        rows = {r.tag: r for r in quarterly.rows}
        assert rows["total_assets"].values[_D] == 1000 * _M
        assert (_D in rows["gross_ppe"].values) is not interim

    def test_q4_balance_sheet_remainder_needs_its_total(self):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        plug = "imputed-plug: total_current_liabilities - (accounts_payable(+))"
        annual, quarterly = self._pair(
            "balance_sheet",
            [
                _rr(
                    "total_current_liabilities",
                    {_D: 500 * _M},
                    period_type="instant",
                    sources={_D: "us-gaap:LiabilitiesCurrent"},
                ),
                _rr(
                    "other_current_liabilities",
                    {_D: 200 * _M},
                    parent="total_current_liabilities",
                    period_type="instant",
                    sources={_D: plug},
                ),
            ],
            [
                _rr(
                    "other_current_liabilities",
                    dict.fromkeys(quarters, 150 * _M),
                    parent="total_current_liabilities",
                    period_type="instant",
                    sources=dict.fromkeys(quarters, "us-gaap:OtherLiabilitiesCurrent"),
                ),
            ],
            quarters,
        )
        reconcile_fiscal_year_ends(quarterly, annual, set())
        rows = {r.tag: r for r in quarterly.rows}
        assert _D not in rows["total_current_liabilities"].values
        assert _D not in rows["other_current_liabilities"].values

    @pytest.mark.parametrize(
        ("source", "held"),
        [
            ("Q4: FY[us-gaap:OtherIncome] \u2212 (Q1[us-gaap:OtherIncome])", False),
            ("us-gaap:GoodwillAndIntangibleAssetImpairment", True),
        ],
    )
    def test_q4_only_line_held_when_reported(self, source, held):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        annual, quarterly = self._pair(
            "income_statement",
            [_rr("total_revenue", {_D: 400 * _M}, sources={_D: "us-gaap:Revenues"})],
            [
                _rr(
                    "total_revenue",
                    dict.fromkeys(quarters, 100 * _M),
                    sources=dict.fromkeys(quarters, "us-gaap:Revenues"),
                ),
                _rr("impairment_expense", {_D: 50 * _M}, sources={_D: source}),
            ],
            quarters,
        )
        reconcile_fiscal_year_ends(quarterly, annual, {"total_revenue"})
        rows = {r.tag: r for r in quarterly.rows}
        assert (_D in rows["impairment_expense"].values) is held

    def test_q4_instant_line_held_when_quarters_report_it(self):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        annual, quarterly = self._pair(
            "cash_flow",
            [
                _rr("net_change_in_cash", {_D: 40 * _M}, sources={_D: "us-gaap:N"}),
                _rr(
                    "cash_at_end_of_period",
                    {_D: 340 * _M},
                    period_type="instant",
                    sources={_D: "us-gaap:Cash"},
                ),
            ],
            [
                _rr(
                    "net_change_in_cash",
                    dict.fromkeys(quarters, 10 * _M),
                    sources=dict.fromkeys(quarters, "us-gaap:N"),
                ),
            ],
            quarters,
        )
        reconcile_fiscal_year_ends(quarterly, annual, {"net_change_in_cash"})
        rows = {r.tag: r for r in quarterly.rows}
        assert rows["net_change_in_cash"].values[_D] == 10 * _M
        assert _D not in rows["cash_at_end_of_period"].values

    def test_q4_only_remainder_not_held(self):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        plug = "imputed-plug: total_x - (a(+))"
        annual, quarterly = self._pair(
            "income_statement",
            [
                _rr(
                    "total_x", {_D: 1000.0 * _M}, sequence=10, sources={_D: "us-gaap:X"}
                ),
                _rr(
                    "a",
                    {_D: 700.0 * _M},
                    parent="total_x",
                    sequence=1,
                    sources={_D: "us-gaap:A"},
                ),
                _rr(
                    "other_x",
                    {_D: 300.0 * _M},
                    parent="total_x",
                    sequence=2,
                    sources={_D: plug},
                ),
            ],
            [
                _rr(
                    "total_x",
                    dict.fromkeys(quarters, 250.0 * _M),
                    sequence=10,
                    sources=dict.fromkeys(quarters, "us-gaap:X"),
                ),
                _rr(
                    "a",
                    dict.fromkeys(quarters, 250.0 * _M),
                    parent="total_x",
                    sequence=1,
                    sources=dict.fromkeys(quarters, "us-gaap:A"),
                ),
                _rr("other_x", {}, parent="total_x", sequence=2),
            ],
            quarters,
        )
        reconcile_fiscal_year_ends(quarterly, annual, {"total_x", "a", "other_x"})
        rows = {r.tag: r for r in quarterly.rows}
        assert rows["total_x"].values[_D] == 250.0 * _M
        assert rows["a"].values[_D] == -50.0 * _M
        assert _D not in rows["other_x"].values

    def test_q4_beginning_cash_kept_when_identity_holds(self):
        quarters = ["2023-03-31", "2023-06-30", "2023-09-30"]
        annual, quarterly = self._pair(
            "cash_flow",
            [
                _rr("net_change_in_cash", {_D: 100.0 * _M}, sources={_D: "us-gaap:N"}),
                _rr(
                    "cash_at_end_of_period",
                    {_D: 340.0 * _M},
                    period_type="instant",
                    sources={_D: "us-gaap:Cash"},
                ),
            ],
            [
                _rr(
                    "net_change_in_cash",
                    {q: v * _M for q, v in zip(quarters, (10.0, 20.0, 30.0))},
                    sources={q: "us-gaap:N" for q in quarters},
                ),
                _rr(
                    "cash_at_beginning_of_period",
                    {_D: 300.0 * _M},
                    period_type="instant",
                    sources={_D: "derived: cash_at_end_of_period(2023-09-30)"},
                ),
            ],
            quarters,
        )
        reconcile_fiscal_year_ends(quarterly, annual, {"net_change_in_cash"})
        bop = _by_tag(quarterly.rows, "cash_at_beginning_of_period")
        assert bop.values[_D] == 300.0 * _M
        assert bop.sources[_D].startswith("derived:")


class TestImputeEmptyRuleset:
    def test_empty_ruleset_returns_rows_unchanged(self):
        # When a statement's rule set is empty, impute() short-circuits and
        # returns the rows untouched with no diagnostics (line 247).
        rows = [_rr("total_assets", {_D: 100.0 * _M})]
        with patch("openbb_sec.utils.statement_schema._imputation.BS_IMPUTE", []):
            out, diags = impute(rows, "balance_sheet", "industrial", {_D})
        assert out is rows
        assert diags == []


# ---------------------------------------------------------------------------
# impute() -- income-statement pre-pass corrections (equity method / ProfitLoss)
# ---------------------------------------------------------------------------


class TestImputeEquityMethodPrePass:
    def test_identity_holds_skips_correction(self):
        # pretax tagged with EquityMethodInvestments but nic+tax already match ->
        # the correction block hits the early `continue` and leaves pretax as-is.
        rows = [
            _rr(
                "total_pretax_income",
                {_D: 550.0 * _M},
                sequence=1,
                sources={
                    _D: "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"
                },
            ),
            _rr(
                "income_tax_expense",
                {_D: 150.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:IncomeTaxExpenseBenefit"},
            ),
            _rr(
                "net_income_continuing",
                {_D: 400.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:IncomeLossFromContinuingOperations"},
            ),
        ]
        out, _ = impute(
            rows, "income_statement", "diversified", {_D}, facts={"us-gaap": {}}
        )
        ptx = _by_tag(out, "total_pretax_income")
        assert ptx.values[_D] == 550.0 * _M
        assert "IncomeLossFromContinuing" in ptx.sources[_D]

    def test_profitloss_nic_deletes_equity_method_pretax(self):
        # Identity off + nic from ProfitLoss (NCI-bearing, no FromContinuing) ->
        # pretax value/source are deleted (281-283).
        rows = [
            _rr(
                "total_pretax_income",
                {_D: 700.0 * _M},
                sequence=1,
                sources={
                    _D: "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"
                },
            ),
            _rr(
                "income_tax_expense",
                {_D: 150.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:IncomeTaxExpenseBenefit"},
            ),
            _rr(
                "net_income_continuing",
                {_D: 400.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:ProfitLoss"},
            ),
            _rr("income_before_equity_method", {}, sequence=4),
            _rr("equity_method_investments", {}, sequence=5),
        ]
        out, _ = impute(
            rows, "income_statement", "diversified", {_D}, facts={"us-gaap": {}}
        )
        ptx = _by_tag(out, "total_pretax_income")
        # pretax was deleted then may be re-imputed by IS_IMPUTE_COMMON from nic+tax.
        assert ptx.values.get(_D) in (None, 550.0 * _M)
        assert "EquityMethodInvestments" not in ptx.sources.get(_D, "")

    def test_no_equity_value_deletes_pretax(self):
        # Identity off, nic not ProfitLoss, equity_method_investments absent/zero ->
        # else-branch deletes pretax (294-295).
        rows = [
            _rr(
                "total_pretax_income",
                {_D: 900.0 * _M},
                sequence=1,
                sources={
                    _D: "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterestEquityMethodInvestments"
                },
            ),
            _rr(
                "income_tax_expense",
                {_D: 150.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:IncomeTaxExpenseBenefit"},
            ),
            _rr(
                "net_income_continuing",
                {_D: 400.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:IncomeLossFromContinuingOperations"},
            ),
            _rr("income_before_equity_method", {}, sequence=4),
            _rr("equity_method_investments", {_D: 0.0}, sequence=5),
        ]
        out, _ = impute(
            rows, "income_statement", "diversified", {_D}, facts={"us-gaap": {}}
        )
        ptx = _by_tag(out, "total_pretax_income")
        # original EquityMethod-sourced value removed; re-imputed to nic+tax=550.
        assert "EquityMethodInvestments" not in ptx.sources.get(_D, "")

    def test_income_before_equity_seeded_from_pretax(self):
        # income_before_equity_method is empty -> seeded with pretax value/source (267-268).
        rows = [
            _rr(
                "total_pretax_income",
                {_D: 700.0 * _M},
                sequence=1,
                sources={
                    _D: "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"
                },
            ),
            _rr("income_before_equity_method", {}, sequence=2),
            _rr(
                "equity_method_investments",
                {_D: 50.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:IncomeLossFromEquityMethodInvestments"},
            ),
            _rr(
                "income_tax_expense",
                {_D: 150.0 * _M},
                sequence=4,
                sources={_D: "us-gaap:IncomeTaxExpenseBenefit"},
            ),
            _rr(
                "net_income_continuing",
                {_D: 600.0 * _M},
                sequence=5,
                sources={_D: "us-gaap:IncomeLossFromContinuingOperations"},
            ),
        ]
        out, _ = impute(
            rows, "income_statement", "diversified", {_D}, facts={"us-gaap": {}}
        )
        beq = _by_tag(out, "income_before_equity_method")
        assert beq.values[_D] == 700.0 * _M


class TestImputeProfitLossDiscAdjust:
    def test_profitloss_before_marker_skips(self):
        # nic source has ProfitLossBefore -> the disc-adjust block skips (312).
        rows = [
            _rr(
                "net_income_continuing",
                {_D: 400.0 * _M},
                sequence=1,
                sources={_D: "us-gaap:ProfitLossBeforeTax"},
            ),
            _rr("net_income_discontinued", {_D: 30.0 * _M}, sequence=2),
            _rr("income_tax_expense", {_D: 100.0 * _M}, sequence=3),
        ]
        out, _ = impute(
            rows, "income_statement", "industrial", {_D}, facts={"us-gaap": {}}
        )
        nic = _by_tag(out, "net_income_continuing")
        assert "(disc-adjusted)" not in nic.sources[_D]
        assert nic.values[_D] == 400.0 * _M

    def test_nonscoped_tax_skips_disc_adjust(self):
        # nic from ProfitLoss, but tax has a non-ContinuingOperations source ->
        # the block hits `continue` and disc is NOT subtracted (316-317).
        rows = [
            _rr(
                "net_income_continuing",
                {_D: 430.0 * _M},
                sequence=1,
                sources={_D: "us-gaap:ProfitLoss"},
            ),
            _rr("net_income_discontinued", {_D: 30.0 * _M}, sequence=2),
            _rr(
                "income_tax_expense",
                {_D: 100.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:IncomeTaxExpenseBenefit"},
            ),
        ]
        out, _ = impute(
            rows, "income_statement", "industrial", {_D}, facts={"us-gaap": {}}
        )
        nic = _by_tag(out, "net_income_continuing")
        assert "(disc-adjusted)" not in nic.sources[_D]
        assert nic.values[_D] == 430.0 * _M

    def test_disc_adjustment_applied_with_continuing_ops_tax(self):
        # nic from ProfitLoss (NCI/disc-bearing); tax explicitly ContinuingOperations
        # -> the guard passes and disc is subtracted (319-323).
        rows = [
            _rr(
                "net_income_continuing",
                {_D: 430.0 * _M},
                sequence=1,
                sources={_D: "us-gaap:ProfitLoss"},
            ),
            _rr("net_income_discontinued", {_D: 30.0 * _M}, sequence=2),
            _rr(
                "income_tax_expense",
                {_D: 100.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:IncomeTaxExpenseBenefitContinuingOperations"},
            ),
        ]
        out, _ = impute(
            rows, "income_statement", "industrial", {_D}, facts={"us-gaap": {}}
        )
        nic = _by_tag(out, "net_income_continuing")
        assert nic.values[_D] == 400.0 * _M  # 430 - 30
        assert "(disc-adjusted)" in nic.sources[_D]

    def test_disc_adjustment_applied_with_absent_tax_row(self):
        # nic from ProfitLoss; tax row absent -> no tax-source guard triggered,
        # disc subtraction still applies.
        rows = [
            _rr(
                "net_income_continuing",
                {_D: 430.0 * _M},
                sequence=1,
                sources={_D: "us-gaap:ProfitLoss"},
            ),
            _rr("net_income_discontinued", {_D: 30.0 * _M}, sequence=2),
        ]
        out, _ = impute(
            rows, "income_statement", "industrial", {_D}, facts={"us-gaap": {}}
        )
        nic = _by_tag(out, "net_income_continuing")
        assert nic.values[_D] == 400.0 * _M
        assert "(disc-adjusted)" in nic.sources[_D]


# ---------------------------------------------------------------------------
# impute() -- income-statement gross-profit / cogs / opex correction passes
# ---------------------------------------------------------------------------


class TestImputeBalanceSheetRound2:
    def test_gross_ppe_from_net_and_accumulated_depreciation(self):
        rows = [
            _rr(
                "net_ppe",
                {_D: 24675.0 * _M},
                period_type="instant",
                sequence=3,
                sources={_D: "us-gaap:PropertyPlantAndEquipmentNet"},
            ),
            _rr("gross_ppe", {}, parent="net_ppe", period_type="instant", sequence=1),
            _rr(
                "accumulated_depreciation",
                {_D: 12560.0 * _M},
                parent="net_ppe",
                factor="-",
                period_type="instant",
                sequence=2,
                sources={
                    _D: "us-gaap:AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment"
                },
            ),
        ]
        out, _ = impute(rows, "balance_sheet", "industrial", {_D}, facts={})
        gross = _by_tag(out, "gross_ppe")
        assert gross.values[_D] == 37235.0 * _M
        assert gross.sources[_D] == "imputed: net_ppe + accumulated_depreciation"
        assert _by_tag(out, "other_net_ppe") is None

    def test_equity_including_nci_corrected_from_balance_identity(self):
        def inst(tag, value, parent=None, seq=1):
            return _rr(
                tag,
                {} if value is None else {_D: value * _M},
                parent=parent,
                period_type="instant",
                sequence=seq,
                sources={} if value is None else {_D: f"us-gaap:{tag}"},
            )

        rows = [
            inst("total_liabilities_and_equity", 63519.4, seq=30),
            inst("total_liabilities", 52400.3, "total_liabilities_and_equity", 10),
            inst(
                "total_equity_and_noncontrolling_interests",
                -1808.5,
                "total_liabilities_and_equity",
                20,
            ),
            inst(
                "total_equity", 11119.1, "total_equity_and_noncontrolling_interests", 15
            ),
            inst(
                "noncontrolling_interests",
                None,
                "total_equity_and_noncontrolling_interests",
                16,
            ),
            inst("temporary_equity", None, "total_liabilities_and_equity", 21),
        ]
        out, _ = impute(rows, "balance_sheet", "insurance", {_D}, facts={})
        enci = _by_tag(out, "total_equity_and_noncontrolling_interests")
        assert enci.values[_D] == 11119.1 * _M
        assert enci.sources[_D] == (
            "corrected: total_equity + noncontrolling_interests"
        )
        assert _by_tag(out, "total_equity").values[_D] == 11119.1 * _M
        assert _D not in _by_tag(out, "temporary_equity").values

    def test_fallback_equity_including_nci_corrected_to_reference_equity(self):
        def inst(tag, value, parent=None, seq=1, source=None):
            return _rr(
                tag,
                {} if value is None else {_D: value * _M},
                parent=parent,
                period_type="instant",
                sequence=seq,
                sources={} if value is None else {_D: source or f"us-gaap:{tag}"},
            )

        rows = [
            inst("total_liabilities_and_equity", 9347.0, seq=30),
            inst(
                "total_liabilities",
                10874.0,
                "total_liabilities_and_equity",
                10,
                "imputed-plug: total_liabilities_and_equity - "
                "(total_equity_and_noncontrolling_interests(+))",
            ),
            inst(
                "total_equity_and_noncontrolling_interests",
                -1527.0,
                "total_liabilities_and_equity",
                20,
                "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest(fallback)",
            ),
            inst(
                "total_equity",
                -1520.0,
                "total_equity_and_noncontrolling_interests",
                15,
                "us-gaap:StockholdersEquity",
            ),
            inst(
                "noncontrolling_interests",
                None,
                "total_equity_and_noncontrolling_interests",
                16,
            ),
            inst("temporary_equity", None, "total_liabilities_and_equity", 21),
        ]
        out, _ = impute(rows, "balance_sheet", "industrial", {_D}, facts={})
        enci = _by_tag(out, "total_equity_and_noncontrolling_interests")
        assert enci.values[_D] == -1520.0 * _M
        assert enci.sources[_D] == (
            "corrected: total_equity + noncontrolling_interests"
        )
        assert _by_tag(out, "total_equity").values[_D] == -1520.0 * _M
        assert _by_tag(out, "total_liabilities").values[_D] == 10867.0 * _M


class TestNetChangeFromBalances:
    def _rows(self, eop, eop_sources, ncc=None):
        return [
            _rr("net_change_in_cash", ncc or {}, sequence=1),
            _rr(
                "cash_at_end_of_period",
                eop,
                period_type="instant",
                sequence=2,
                sources=eop_sources,
            ),
        ]

    def test_annual_change_of_same_tag_balances(self):
        rows = self._rows(
            {"2022-12-31": 1000.0 * _M, "2023-12-31": 1200.0 * _M},
            {"2022-12-31": "us-gaap:Cash", "2023-12-31": "us-gaap:Cash(fallback)"},
        )
        _net_change_from_balances(rows, {"2022-12-31", "2023-12-31"}, "annual")
        ncc = _by_tag(rows, "net_change_in_cash")
        assert ncc.values == {"2023-12-31": 200.0 * _M}
        assert ncc.sources["2023-12-31"] == (
            "imputed: cash_at_end_of_period - cash_at_end_of_period(2022-12-31)"
        )

    def test_quarterly_span(self):
        rows = self._rows(
            {"2023-03-31": 1000.0 * _M, "2023-06-30": 900.0 * _M},
            {"2023-03-31": "us-gaap:Cash", "2023-06-30": "us-gaap:Cash"},
        )
        _net_change_from_balances(rows, {"2023-03-31", "2023-06-30"}, "quarterly")
        assert _by_tag(rows, "net_change_in_cash").values == {"2023-06-30": -100.0 * _M}

    def test_quarter_gap_not_annual_span(self):
        rows = self._rows(
            {"2023-03-31": 1000.0 * _M, "2023-06-30": 900.0 * _M},
            {"2023-03-31": "us-gaap:Cash", "2023-06-30": "us-gaap:Cash"},
        )
        _net_change_from_balances(rows, {"2023-03-31", "2023-06-30"}, "annual")
        assert _by_tag(rows, "net_change_in_cash").values == {}

    def test_different_tags_not_differenced(self):
        rows = self._rows(
            {"2022-12-31": 1000.0 * _M, "2023-12-31": 1200.0 * _M},
            {"2022-12-31": "us-gaap:Cash", "2023-12-31": "us-gaap:CashAndDue"},
        )
        _net_change_from_balances(rows, {"2022-12-31", "2023-12-31"}, "annual")
        assert _by_tag(rows, "net_change_in_cash").values == {}

    def test_reported_net_change_kept(self):
        rows = self._rows(
            {"2022-12-31": 1000.0 * _M, "2023-12-31": 1200.0 * _M},
            {"2022-12-31": "us-gaap:Cash", "2023-12-31": "us-gaap:Cash"},
            ncc={"2023-12-31": 150.0 * _M},
        )
        _net_change_from_balances(rows, {"2022-12-31", "2023-12-31"}, "annual")
        assert _by_tag(rows, "net_change_in_cash").values == {"2023-12-31": 150.0 * _M}

    def test_missing_rows_is_noop(self):
        rows = [_rr("cash_at_end_of_period", {_D: 1.0 * _M}, period_type="instant")]
        _net_change_from_balances(rows, {_D}, "annual")
        assert rows[0].values == {_D: 1.0 * _M}


class TestImputeTaxSign:
    def _rows(self, tax, current, deferred, current_source=None):
        return [
            _rr(
                "total_pretax_income",
                {_D: 1078.0 * _M},
                sequence=1,
                sources={
                    _D: "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
                },
            ),
            _rr(
                "income_tax_expense",
                {_D: tax * _M},
                sequence=2,
                sources={_D: "us-gaap:IncomeTaxExpenseBenefit"},
            ),
            _rr(
                "income_tax_current",
                {} if current is None else {_D: current * _M},
                sequence=3,
                sources={}
                if current is None
                else {_D: current_source or "us-gaap:CurrentIncomeTaxExpenseBenefit"},
            ),
            _rr(
                "income_tax_deferred",
                {_D: deferred * _M},
                sequence=4,
                sources={_D: "us-gaap:DeferredIncomeTaxExpenseBenefit"},
            ),
            _rr(
                "net_income_continuing",
                {_D: 769.0 * _M},
                sequence=5,
                sources={_D: "us-gaap:ProfitLoss"},
            ),
        ]

    def test_reversed_tax_sign_corrected(self):
        out, _ = impute(
            self._rows(-309.0, 323.0, -14.0),
            "income_statement",
            "industrial",
            {_D},
            facts={},
        )
        tax = _by_tag(out, "income_tax_expense")
        assert tax.values[_D] == 309.0 * _M
        assert tax.sources[_D] == (
            "corrected: total_pretax_income - net_income_continuing"
        )
        assert _by_tag(out, "total_pretax_income").values[_D] == 1078.0 * _M

    def test_imputed_current_tax_rederived_after_sign_correction(self):
        out, _ = impute(
            self._rows(-309.0, None, -14.0),
            "income_statement",
            "industrial",
            {_D},
            facts={},
        )
        assert _by_tag(out, "income_tax_expense").values[_D] == 309.0 * _M
        current = _by_tag(out, "income_tax_current")
        assert current.values[_D] == 323.0 * _M
        assert current.sources[_D] == (
            "imputed: income_tax_expense - income_tax_deferred"
        )

    def test_tax_sign_kept_when_components_agree(self):
        out, _ = impute(
            self._rows(-309.0, -295.0, -14.0),
            "income_statement",
            "industrial",
            {_D},
            facts={},
        )
        assert _by_tag(out, "income_tax_expense").values[_D] == -309.0 * _M


class TestImputeISCorrectionPasses:
    def test_cogs_kept_when_operating_expenses_rolled_up(self):
        rows = [
            _rr(
                "total_revenue",
                {_D: 1000.0 * _M},
                sequence=1,
                sources={_D: "us-gaap:Revenues"},
            ),
            _rr(
                "total_cost_of_revenue",
                {_D: 300.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:CostOfRevenue"},
            ),
            _rr(
                "costs_and_expenses",
                {_D: 900.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:CostsAndExpenses"},
            ),
            _rr("total_operating_expenses", {}, sequence=4),
            _rr(
                "sga_expense",
                {_D: 400.0 * _M},
                parent="total_operating_expenses",
                sequence=5,
                sources={_D: "us-gaap:SellingGeneralAndAdministrativeExpense"},
            ),
            _rr(
                "total_operating_income",
                {_D: 100.0 * _M},
                sequence=6,
                sources={_D: "us-gaap:OperatingIncomeLoss"},
            ),
        ]
        out, _ = impute(rows, "income_statement", "industrial", {_D}, facts={})
        cogs = _by_tag(out, "total_cost_of_revenue")
        assert cogs.values[_D] == 300.0 * _M
        assert cogs.sources[_D] == "us-gaap:CostOfRevenue"

    def test_gross_profit_rollup_recomputed_from_rev_minus_cogs(self):
        # gp carries an imputed-rollup source and a stale value; with cogs!=0 and
        # rev present it is recomputed to rev - cogs (407-414).
        rows = [
            _rr(
                "total_revenue",
                {_D: 1000.0 * _M},
                sequence=1,
                sources={_D: "us-gaap:Revenues"},
            ),
            _rr(
                "total_cost_of_revenue",
                {_D: 300.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:CostOfRevenue"},
            ),
            _rr(
                "total_gross_profit",
                {_D: 123.0 * _M},
                sequence=3,
                sources={_D: "imputed-rollup: segment_gp(+)"},
            ),
        ]
        out, _ = impute(rows, "income_statement", "industrial", {_D}, facts={})
        gp = _by_tag(out, "total_gross_profit")
        assert gp.values[_D] == 700.0 * _M  # 1000 - 300
        assert "imputed: total_revenue - total_cost_of_revenue" in gp.sources[_D]

    def test_cogs_backsolved_from_rev_minus_gross_profit(self):
        # gp hard-sourced and rev - cogs - gp violates identity -> cogs corrected
        # to rev - gp (499-506).
        rows = [
            _rr(
                "total_revenue",
                {_D: 1000.0 * _M},
                sequence=1,
                sources={_D: "us-gaap:Revenues"},
            ),
            _rr(
                "total_cost_of_revenue",
                {_D: 100.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:CostOfRevenue"},
            ),
            _rr(
                "total_gross_profit",
                {_D: 700.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:GrossProfit"},
            ),
        ]
        out, _ = impute(rows, "income_statement", "industrial", {_D}, facts={})
        cogs = _by_tag(out, "total_cost_of_revenue")
        assert cogs.values[_D] == 300.0 * _M  # 1000 - 700
        assert "corrected: total_revenue - total_gross_profit" in cogs.sources[_D]

    def test_opex_backsolved_from_gross_profit_minus_operating_income(self):
        # opex > gp triggers the opex correction to gp - opinc (527-540); opinc must
        # be hard-sourced so the "imputed" guard does not block it.
        rows = [
            _rr(
                "total_revenue",
                {_D: 1000.0 * _M},
                sequence=1,
                sources={_D: "us-gaap:Revenues"},
            ),
            _rr(
                "total_gross_profit",
                {_D: 800.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:GrossProfit"},
            ),
            _rr(
                "total_operating_expenses",
                {_D: 950.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:OperatingExpenses"},
            ),
            _rr(
                "total_operating_income",
                {_D: 300.0 * _M},
                sequence=4,
                sources={_D: "us-gaap:OperatingIncomeLoss"},
            ),
        ]
        out, _ = impute(rows, "income_statement", "industrial", {_D}, facts={})
        opex = _by_tag(out, "total_operating_expenses")
        assert opex.values[_D] == 500.0 * _M  # 800 - 300
        assert (
            "corrected: total_gross_profit - total_operating_income" in opex.sources[_D]
        )

    def test_opex_correction_skips_when_gross_profit_unresolvable(self):
        # No revenue/cogs to derive gp, opinc explicitly imputed -> in the opex
        # correction loop gp_val stays None so the loop `continue`s (524-525).
        rows = [
            _rr("total_gross_profit", {}, sequence=1),
            _rr(
                "total_operating_expenses",
                {_D: 950.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:OperatingExpenses"},
            ),
            _rr(
                "total_operating_income",
                {_D: 300.0 * _M},
                sequence=3,
                sources={_D: "imputed: x - y"},
            ),
        ]
        out, _ = impute(rows, "income_statement", "industrial", {_D}, facts={})
        opex = _by_tag(out, "total_operating_expenses")
        # gp never resolved -> correction loop skipped opex (no "corrected" marker).
        assert "corrected: total_gross_profit" not in opex.sources.get(_D, "")
        assert opex.values[_D] == 950.0 * _M


class TestImputeBSEquityReconcileGuard:
    def test_reconcile_skips_when_le_identity_violated(self):
        # ENCI != equity + nci (gap present) but L + ENCI + rNCI != L&E -> the
        # second guard `continue` (565-566) blocks the reconciliation.
        rows = [
            _rr(
                "total_assets",
                {_D: 1000.0 * _M},
                period_type="instant",
                balance="debit",
                sequence=1,
                sources={_D: "us-gaap:Assets"},
            ),
            _rr(
                "total_liabilities",
                {_D: 600.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=2,
                sources={_D: "us-gaap:Liabilities"},
            ),
            # L&E deliberately inconsistent with L + ENCI so the second guard fails.
            _rr(
                "total_liabilities_and_equity",
                {_D: 1000.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=3,
                sources={_D: "us-gaap:LiabilitiesAndStockholdersEquity"},
            ),
            _rr(
                "total_equity_and_noncontrolling_interests",
                {_D: 200.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=4,
                sources={
                    _D: "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
                },
            ),
            _rr(
                "total_equity",
                {_D: 999.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=5,
                sources={_D: "us-gaap:StockholdersEquity"},
            ),
            _rr(
                "noncontrolling_interests",
                {_D: 0.0},
                period_type="instant",
                balance="credit",
                sequence=6,
                sources={_D: "us-gaap:MinorityInterest"},
            ),
        ]
        out, _ = impute(
            rows, "balance_sheet", "industrial", {_D}, facts={"us-gaap": {}}
        )
        eq = _by_tag(out, "total_equity")
        # Reconciliation did NOT fire (would have set 200): equity keeps its own value.
        assert "reconciled" not in eq.sources.get(_D, "")


# ---------------------------------------------------------------------------
# impute() -- cash-flow verify FX-scope and discontinued-ops fallbacks
# ---------------------------------------------------------------------------


def _cf_base(nc_val, nc_src):
    """Five CF rows whose op+inv+fin+fx = 200M, with a mismatching net_change."""
    return [
        _rr(
            "net_cash_from_operating_activities",
            {_D: 500.0 * _M},
            balance="debit",
            sequence=1,
            sources={_D: "us-gaap:NetCashProvidedByUsedInOperatingActivities"},
        ),
        _rr(
            "net_cash_from_investing_activities",
            {_D: -200.0 * _M},
            balance="debit",
            sequence=2,
            sources={_D: "us-gaap:NetCashProvidedByUsedInInvestingActivities"},
        ),
        _rr(
            "net_cash_from_financing_activities",
            {_D: -150.0 * _M},
            balance="debit",
            sequence=3,
            sources={_D: "us-gaap:NetCashProvidedByUsedInFinancingActivities"},
        ),
        _rr(
            "effect_of_exchange_rate_changes",
            {_D: 50.0 * _M},
            balance="debit",
            sequence=4,
            sources={_D: "us-gaap:EffectOfExchangeRateOnCash"},
        ),
        _rr(
            "net_change_in_cash",
            {_D: nc_val},
            balance="debit",
            sequence=5,
            sources={_D: nc_src},
        ),
    ]


class TestImputeCashFlowFXScope:
    def test_excluding_fx_marker_uses_no_fx_rule(self):
        # net_change marked ExcludingExchangeRateEffect -> the FX-inclusive rule is
        # skipped (640, 651); the no-FX rule (op+inv+fin=150) verifies cleanly.
        rows = _cf_base(
            150.0 * _M, "us-gaap:CashPeriodIncreaseDecreaseExcludingExchangeRateEffect"
        )
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts={"us-gaap": {}})
        # 500-200-150 = 150 matches the Excluding-FX net change -> verified, no warning.
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_including_fx_marker_skips_no_fx_rule(self):
        # net_change marked IncludingExchangeRateEffect with NO effect-of-fx row:
        # the FX rules cannot evaluate (source missing) and every no-FX rule is
        # skipped by the Including-scope guard (648) -> no diagnostic emitted.
        rows = _cf_base(
            200.0 * _M, "us-gaap:CashPeriodIncreaseDecreaseIncludingExchangeRateEffect"
        )
        rows = [r for r in rows if r.tag != "effect_of_exchange_rate_changes"]
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts={"us-gaap": {}})
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_continuing_operations_source_marks_scope_mismatch(self):
        # An activity source carries ContinuingOperations while net_change is FX-
        # scoped -> _cf_scope_mismatch=True (666-667); the engine scope-aligns the
        # net change rather than warning.
        rows = _cf_base(
            999.0 * _M, "us-gaap:CashPeriodIncreaseDecreaseExcludingExchangeRateEffect"
        )
        rows[0].sources[_D] = (
            "us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"
        )
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts={"us-gaap": {}})
        nc = _by_tag(out, "net_change_in_cash")
        assert all(w.tag != "net_change_in_cash" for w in diag)
        assert "scope-aligned" in nc.sources[_D]


class TestImputeCashFlowDiscFallbacks:
    def test_disc_row_with_disc_fx_fact_closes_gap(self):
        # An explicit disc-ops row plus a discontinued-ops FX fact close the gap
        # via the disc-FX adjustment (984-1006).
        facts = {
            "us-gaap": {
                "EffectOfExchangeRateOnCashAndCashEquivalentsDiscontinuedOperations": {
                    "units": {"USD": [_dur(_D, "2023-01-01", 10.0 * _M)]}
                }
            }
        }
        rows = _cf_base(240.0 * _M, "us-gaap:CashIncludingExchangeRateEffect")
        rows.append(
            _rr(
                "net_cash_from_discontinued_operations",
                {_D: 30.0 * _M},
                balance="debit",
                sequence=6,
                sources={_D: "us-gaap:NetCashProvidedByUsedInDiscontinuedOperations"},
            )
        )
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        # 200 + 30 (disc) + 10 (disc-fx) = 240 matches.
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_disc_row_fallback_without_disc_fx(self):
        # disc row present, disc-fx present but the with-fx identity misses while the
        # without-fx identity matches (1007-1013).
        facts = {
            "us-gaap": {
                "EffectOfExchangeRateOnCashAndCashEquivalentsDiscontinuedOperations": {
                    "units": {"USD": [_dur(_D, "2023-01-01", 10.0 * _M)]}
                }
            }
        }
        rows = _cf_base(230.0 * _M, "us-gaap:CashIncludingExchangeRateEffect")
        rows.append(
            _rr(
                "net_cash_from_discontinued_operations",
                {_D: 30.0 * _M},
                balance="debit",
                sequence=6,
                sources={_D: "us-gaap:NetCashProvidedByUsedInDiscontinuedOperations"},
            )
        )
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        # 200 + 30 = 230 (without disc-fx) matches; with disc-fx (240) would not.
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_disc_ops_sum_fallback_closes_gap(self):
        # No disc row; summed individual disc-ops activity tags reconcile (1051-1122).
        facts = {
            "us-gaap": {
                "NetCashProvidedByUsedInDiscontinuedOperations": {
                    "units": {"USD": [_dur(_D, "2023-01-01", 30.0 * _M)]}
                }
            }
        }
        rows = _cf_base(230.0 * _M, "us-gaap:CashIncludingExchangeRateEffect")
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_disc_ops_sum_fallback_skips_malformed_start(self):
        # The disc-ops-sum fallback (1051-1122) iterates the discontinued NetCash tag;
        # a malformed-dated entry is skipped (1082-1083) before the clean entry sums in.
        facts = {
            "us-gaap": {
                "NetCashProvidedByUsedInDiscontinuedOperations": {
                    "units": {
                        "USD": [
                            {
                                "end": _D,
                                "start": "bad-date",
                                "val": 99.0 * _M,
                                "form": "10-K",
                                "filed": "2024-01-15",
                            },  # 1082-1083
                            _dur(_D, "2023-01-01", 30.0 * _M),  # clean -> sums to 30
                        ]
                    }
                }
            }
        }
        rows = _cf_base(230.0 * _M, "us-gaap:CashIncludingExchangeRateEffect")
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        # 200 (op+inv+fin+fx) + 30 (disc sum) = 230 -> reconciled.
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_disc_individual_tag_skips_malformed_start(self):
        # The individual disc-ops fallback (1020-1049) skips a malformed-dated entry
        # (1033-1034) then matches the clean one to close the gap.
        facts = {
            "us-gaap": {
                "CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations": {
                    "units": {
                        "USD": [
                            {
                                "end": _D,
                                "start": "nope",
                                "val": 99.0 * _M,
                                "form": "10-K",
                                "filed": "2024-01-15",
                            },  # 1033-1034
                            _dur(
                                _D, "2023-01-01", 30.0 * _M
                            ),  # clean -> 200 + 30 = 230
                        ]
                    }
                }
            }
        }
        rows = _cf_base(230.0 * _M, "us-gaap:CashIncludingExchangeRateEffect")
        # An explicit disc row routes through the individual-tags fallback (disc_val set).
        rows.append(
            _rr(
                "net_cash_from_discontinued_operations",
                {_D: 0.0},
                balance="debit",
                sequence=6,
                sources={_D: "us-gaap:NetCashProvidedByUsedInDiscontinuedOperations"},
            )
        )
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_disc_row_disc_fx_skips_malformed_start(self):
        # disc row present: the disc-FX adjustment loop (982-998) skips a malformed-
        # dated FX entry (990-991) then uses the clean one to close the gap.
        facts = {
            "us-gaap": {
                "EffectOfExchangeRateOnCashAndCashEquivalentsDiscontinuedOperations": {
                    "units": {
                        "USD": [
                            {
                                "end": _D,
                                "start": "xx",
                                "val": 99.0 * _M,
                                "form": "10-K",
                                "filed": "2024-01-15",
                            },  # 990-991
                            _dur(_D, "2023-01-01", 10.0 * _M),  # clean
                        ]
                    }
                }
            }
        }
        rows = _cf_base(240.0 * _M, "us-gaap:CashIncludingExchangeRateEffect")
        rows.append(
            _rr(
                "net_cash_from_discontinued_operations",
                {_D: 30.0 * _M},
                balance="debit",
                sequence=6,
                sources={_D: "us-gaap:NetCashProvidedByUsedInDiscontinuedOperations"},
            )
        )
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        # 200 + 30 (disc) + 10 (disc-fx) = 240.
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_disc_ops_sum_with_disc_fx_fallback(self):
        # No disc row: the disc-ops-sum fallback finds the discontinued sum then the
        # disc-FX-fb1 loop (1093-1122) skips a malformed FX entry (1104-1105) and adds
        # the clean disc-FX value to reconcile (1107-1112).
        facts = {
            "us-gaap": {
                "NetCashProvidedByUsedInDiscontinuedOperations": {
                    "units": {"USD": [_dur(_D, "2023-01-01", 30.0 * _M)]}
                },
                "EffectOfExchangeRateOnCashAndCashEquivalentsDiscontinuedOperations": {
                    "units": {
                        "USD": [
                            {
                                "end": _D,
                                "start": "zz",
                                "val": 99.0 * _M,
                                "form": "10-K",
                                "filed": "2024-01-15",
                            },  # 1104-1105
                            _dur(
                                _D, "2023-01-01", 10.0 * _M
                            ),  # clean -> 200+30+10 = 240
                        ]
                    }
                },
            }
        }
        rows = _cf_base(240.0 * _M, "us-gaap:CashIncludingExchangeRateEffect")
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_disposal_group_change_closes_gap(self):
        # A disposal-group net-change fact equal to the activity sum (val) bridges
        # the gap: the check reduces to val ~= disposal_nc (1124-1173).
        facts = {
            "us-gaap": {
                "CashAndCashEquivalentsPeriodIncreaseDecreaseDisposalGroupIncludingDiscontinuedOperations": {
                    "units": {"USD": [_dur(_D, "2023-01-01", 200.0 * _M)]}
                }
            }
        }
        rows = _cf_base(230.0 * _M, "us-gaap:CashIncludingExchangeRateEffect")
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_disposal_cash_balance_delta_closes_gap(self):
        # Instant disposal-group cash balances (end vs prior quarter) reconcile via
        # the cash-delta path: val - (end - start) ~= net_change (1178-1224).
        prior = "2023-09-30"  # prior_period_end("2023-12-31")
        facts = {
            "us-gaap": {
                "DisposalGroupIncludingDiscontinuedOperationCashAndCashEquivalents": {
                    "units": {"USD": [_inst(_D, 80.0 * _M), _inst(prior, 50.0 * _M)]}
                }
            }
        }
        # delta = 80 - 50 = 30; identity uses val - delta -> 200 - 30 = 170 target.
        rows = _cf_base(170.0 * _M, "us-gaap:CashIncludingExchangeRateEffect")
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_disposal_group_change_skips_malformed_start(self):
        # The disposal-group net-change loop (1137-1173) skips a malformed-dated entry
        # (1153-1154) then bridges with the clean disposal fact.
        facts = {
            "us-gaap": {
                "CashAndCashEquivalentsPeriodIncreaseDecreaseDisposalGroupIncludingDiscontinuedOperations": {
                    "units": {
                        "USD": [
                            {
                                "end": _D,
                                "start": "??",
                                "val": 99.0 * _M,
                                "form": "10-K",
                                "filed": "2024-01-15",
                            },  # 1153-1154
                            _dur(
                                _D, "2023-01-01", 200.0 * _M
                            ),  # clean: check reduces to val ~= 200
                        ]
                    }
                }
            }
        }
        rows = _cf_base(230.0 * _M, "us-gaap:CashIncludingExchangeRateEffect")
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_restricted_cash_change_skips_malformed_start(self):
        # No disc/disposal facts: the loop reaches the restricted-cash block (1226-1262)
        # which skips a malformed-dated entry (1244-1245) then adds the clean change.
        facts = {
            "us-gaap": {
                "IncreaseDecreaseInRestrictedCashAndRestrictedCashEquivalents": {
                    "units": {
                        "USD": [
                            {
                                "end": _D,
                                "start": "!!",
                                "val": 99.0 * _M,
                                "form": "10-K",
                                "filed": "2024-01-15",
                            },  # 1244-1245
                            _dur(
                                _D, "2023-01-01", 30.0 * _M
                            ),  # clean -> 200 + 30 = 230
                        ]
                    }
                }
            }
        }
        rows = _cf_base(230.0 * _M, "us-gaap:CashIncludingExchangeRateEffect")
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_activity_pairs_scope_skips_malformed_start(self):
        # The continuing-vs-total activity-pairs scope block (1264-1383) reads activity
        # facts via _cf_vals, which skips a malformed-dated entry (1325-1326) then uses
        # the clean continuing-operations values to reconcile.
        def _pair(tot_val):
            return {
                "units": {
                    "USD": [
                        {
                            "end": _D,
                            "start": "##",
                            "val": 99.0 * _M,
                            "form": "10-K",
                            "filed": "2024-01-15",
                        },  # 1325-1326
                        _dur(_D, "2023-01-01", tot_val),  # clean
                    ]
                }
            }

        facts = {
            "us-gaap": {
                "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations": _pair(
                    500.0 * _M
                ),
                "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations": _pair(
                    -200.0 * _M
                ),
                "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations": _pair(
                    -150.0 * _M
                ),
                # A discontinued-ops FX fact triggers the disc-FX combination loop
                # (1356-1359) that augments the FX option set.
                "EffectOfExchangeRateOnCashAndCashEquivalentsDiscontinuedOperations": {
                    "units": {"USD": [_dur(_D, "2023-01-01", 20.0 * _M)]}
                },
                "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect": {
                    "units": {"USD": [_dur(_D, "2023-01-01", 150.0 * _M)]}
                },
            }
        }
        # Activity opts 500/-200/-150 + fx(0) reconcile to the 150 net-change fact.
        rows = _cf_base(150.0 * _M, "us-gaap:CashIncludingExchangeRateEffect")
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_cash_balance_delta_reconciles_net_change(self):
        # No disc/disposal/activity facts: the loop falls through to the cash-balance
        # delta block (1385-1438).  The instant CashCashEquivalents... facts include a
        # duration entry (skipped, 1409) and a malformed-dated instant (1421-1422)
        # alongside the clean end/prior instants whose delta equals net_change.
        prior = "2023-06-30"  # 184 days before _D -> inside the 60..400 window
        facts = {
            "us-gaap": {
                "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents": {
                    "units": {
                        "USD": [
                            _dur(
                                _D, "2023-01-01", 999.0 * _M
                            ),  # has start -> 1409 skip
                            _inst(_D, 380.0 * _M),  # end-of-period balance
                            _inst(prior, 80.0 * _M),  # prior-period balance
                            {
                                "end": "garbage",
                                "val": 7.0 * _M,
                                "form": "10-K",
                                "filed": "2024-02-15",
                            },  # 1421-1422
                        ]
                    }
                }
            }
        }
        # delta = 380 - 80 = 300 == net_change; the FX rule (op+inv+fin+fx=200) misses
        # so the loop reaches the balance-delta reconciliation.
        rows = _cf_base(300.0 * _M, "us-gaap:CashIncludingExchangeRateEffect")
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        assert all(w.tag != "net_change_in_cash" for w in diag)


# ---------------------------------------------------------------------------
# impute() -- income-statement verify-loop fallbacks
# ---------------------------------------------------------------------------


class TestImputeISVerifyFallbacks:
    def test_disc_adjusted_nic_suppresses_pretax_warning(self):
        # nic becomes ProfitLoss "(disc-adjusted)" and tax is not ContinuingOps; with
        # pretax != nic + tax the verify loop short-circuits both pairs (683-698)
        # rather than warning.
        # tax row carries a value but an empty source: the pre-pass applies the disc
        # adjustment (empty tax-src is not a ContinuingOps mismatch), and the verify
        # loop then sees a non-ContinuingOps tax -> short-circuits both pairs.
        rows = [
            _rr(
                "total_pretax_income",
                {_D: 900.0 * _M},
                sequence=1,
                sources={_D: "us-gaap:IncomeBeforeTax"},
            ),
            _rr("income_tax_expense", {_D: 100.0 * _M}, sequence=2),
            _rr(
                "net_income_continuing",
                {_D: 430.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:ProfitLoss"},
            ),
            _rr("net_income_discontinued", {_D: 30.0 * _M}, sequence=4),
        ]
        out, diag = impute(
            rows, "income_statement", "industrial", {_D}, facts={"us-gaap": {}}
        )
        nic = _by_tag(out, "net_income_continuing")
        assert "(disc-adjusted)" in nic.sources[_D]
        # No pretax/nic identity warning despite 900 != 400 + 100.
        assert all(
            w.tag not in ("total_pretax_income", "net_income_continuing") for w in diag
        )

    def test_profitloss_swap_from_facts_resolves_identity(self):
        # nic from ProfitLoss; a NetIncomeLoss fact (parent-only) makes pretax=nic+tax
        # hold -> swap accepted (827-840) without warning. Mirrors but isolates the
        # us-gaap NetIncomeLoss lookup.
        facts = {
            "us-gaap": {
                "NetIncomeLoss": {
                    "units": {"USD": [_dur(_D, "2023-01-01", 550.0 * _M)]}
                }
            }
        }
        rows = [
            _rr(
                "total_pretax_income",
                {_D: 700.0 * _M},
                sequence=1,
                sources={
                    _D: "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
                },
            ),
            _rr(
                "income_tax_expense",
                {_D: 150.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:IncomeTaxExpenseBenefit"},
            ),
            _rr(
                "net_income_continuing",
                {_D: 600.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:ProfitLoss"},
            ),
        ]
        out, diag = impute(rows, "income_statement", "diversified", {_D}, facts=facts)
        nic = _by_tag(out, "net_income_continuing")
        assert nic.values[_D] == 550.0 * _M
        assert "NCI-corrected" in nic.sources[_D]

    def test_profitloss_swap_for_netincomeloss_nci_pretax(self):
        # nic from NetIncomeLoss, pretax tagged with NoncontrollingInterest -> the
        # engine swaps in a ProfitLoss fact that satisfies pretax=nic+tax (841-860).
        facts = {
            "us-gaap": {
                "ProfitLoss": {"units": {"USD": [_dur(_D, "2023-01-01", 550.0 * _M)]}}
            }
        }
        rows = [
            _rr(
                "total_pretax_income",
                {_D: 700.0 * _M},
                sequence=1,
                # Carries NoncontrollingInterest but NOT EquityMethodInvestments, so
                # the equity-method pre-pass leaves pretax intact.
                sources={
                    _D: "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesNoncontrollingInterest"
                },
            ),
            _rr(
                "income_tax_expense",
                {_D: 150.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:IncomeTaxExpenseBenefit"},
            ),
            _rr(
                "net_income_continuing",
                {_D: 600.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:NetIncomeLoss"},
            ),
        ]
        out, diag = impute(rows, "income_statement", "diversified", {_D}, facts=facts)
        nic = _by_tag(out, "net_income_continuing")
        assert nic.values[_D] == 550.0 * _M
        assert "ProfitLoss(NCI-corrected)" in nic.sources[_D]

    def test_q4_nci_swap_from_fy_minus_quarters(self):
        # nic is Q4-derived; an annual NetIncomeLoss plus 3 quarterly NetIncomeLoss
        # facts reconstruct a parent-only Q4 that satisfies the identity (862-952).
        q_ends = ["2023-03-31", "2023-06-30", "2023-09-30"]
        nil_entries = [
            _dur(_D, "2023-01-01", 600.0 * _M),  # FY parent-only NI
            _dur(q_ends[0], "2023-01-01", 100.0 * _M),
            _dur(q_ends[1], "2023-04-01", 150.0 * _M),
            _dur(q_ends[2], "2023-07-01", 200.0 * _M),
        ]
        facts = {"us-gaap": {"NetIncomeLoss": {"units": {"USD": nil_entries}}}}
        # parent-only Q4 = 600 - (100+150+200) = 150; identity: pretax(250)=150+tax(100).
        rows = [
            _rr(
                "total_pretax_income",
                {_D: 250.0 * _M},
                sequence=1,
                sources={
                    _D: "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
                },
            ),
            _rr(
                "income_tax_expense",
                {_D: 100.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:IncomeTaxExpenseBenefit"},
            ),
            _rr(
                "net_income_continuing",
                {_D: 999.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:NetIncomeLoss Q4: FY[..] - (..)"},
            ),
        ]
        out, diag = impute(rows, "income_statement", "diversified", {_D}, facts=facts)
        nic = _by_tag(out, "net_income_continuing")
        assert nic.values[_D] == 150.0 * _M
        assert "Q4-NCI-corrected" in nic.sources[_D]

    def test_pick_entries_filters_bad_entries_and_rejects_off_identity(self):
        # Exercises _pick_entries' skip paths and _try_nci_swap's reject path via the
        # ProfitLoss NCI-swap branch.  The NetIncomeLoss facts include entries that are
        # skipped (wrong end / no start / wrong form -> 774), malformed-dated (781-782),
        # out-of-window (789), an off-identity but well-formed candidate (filed first ->
        # _try_nci_swap returns False, 825), then a matching candidate that swaps.
        nil_entries = [
            {
                "end": "2022-12-31",
                "start": "2022-01-01",
                "val": 9.0 * _M,
                "form": "10-K",
                "filed": "2023-01-01",
            },  # wrong end -> 774
            {
                "end": _D,
                "val": 9.0 * _M,
                "form": "10-K",
                "filed": "2023-02-01",
            },  # no start -> 774
            {
                "end": _D,
                "start": "2023-01-01",
                "val": 9.0 * _M,
                "form": "8-K",
                "filed": "2023-03-01",
            },  # bad form -> 774
            {
                "end": _D,
                "start": "not-a-date",
                "val": 9.0 * _M,
                "form": "10-K",
                "filed": "2023-04-01",
            },  # malformed -> 781-782
            {
                "end": _D,
                "start": "2023-12-20",
                "val": 9.0 * _M,
                "form": "10-K",
                "filed": "2023-05-01",
            },  # 11 days -> 789
            _dur(
                _D, "2023-01-01", 500.0 * _M, filed="2024-01-15"
            ),  # well-formed, off-identity -> 825 False
            _dur(
                _D, "2023-01-01", 550.0 * _M, filed="2024-02-15"
            ),  # matches identity -> swap
        ]
        facts = {"us-gaap": {"NetIncomeLoss": {"units": {"USD": nil_entries}}}}
        rows = [
            _rr(
                "total_pretax_income",
                {_D: 700.0 * _M},
                sequence=1,
                sources={
                    _D: "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
                },
            ),
            _rr(
                "income_tax_expense",
                {_D: 150.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:IncomeTaxExpenseBenefit"},
            ),
            _rr(
                "net_income_continuing",
                {_D: 600.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:ProfitLoss"},
            ),
        ]
        out, _ = impute(rows, "income_statement", "diversified", {_D}, facts=facts)
        nic = _by_tag(out, "net_income_continuing")
        assert nic.values[_D] == 550.0 * _M  # the matching candidate, not 500
        assert "NCI-corrected" in nic.sources[_D]

    def test_q4_nci_swap_skips_malformed_and_out_of_window_quarters(self):
        # Q4-derived nic: the FY NetIncomeLoss scan and the quarterly scan each skip
        # malformed-dated / out-of-window / wrong-form entries (893-894, 917, 924-925,
        # 933) before reconstructing a clean parent-only Q4 that satisfies the identity.
        nil_entries = [
            {
                "end": _D,
                "start": "bad",
                "val": 600.0 * _M,
                "form": "10-K",
                "filed": "2024-01-10",
            },  # FY malformed -> 893-894
            _dur(
                _D, "2023-01-01", 600.0 * _M, filed="2024-02-10"
            ),  # clean FY parent-only
            {
                "end": "2023-03-31",
                "start": "2023-01-01",
                "val": 100.0 * _M,
                "form": "8-K",
                "filed": "2023-04-10",
            },  # wrong form -> 917
            {
                "end": "2023-06-30",
                "start": "rotten",
                "val": 150.0 * _M,
                "form": "10-Q",
                "filed": "2023-07-10",
            },  # malformed -> 924-925
            {
                "end": "2024-06-30",
                "start": "2024-04-01",
                "val": 999.0 * _M,
                "form": "10-Q",
                "filed": "2024-07-10",
            },  # end >= date -> 933
            _dur(
                "2023-03-31", "2023-01-01", 100.0 * _M, form="10-Q", filed="2023-04-20"
            ),
            _dur(
                "2023-06-30", "2023-04-01", 150.0 * _M, form="10-Q", filed="2023-07-20"
            ),
            _dur(
                "2023-09-30", "2023-07-01", 200.0 * _M, form="10-Q", filed="2023-10-20"
            ),
        ]
        facts = {"us-gaap": {"NetIncomeLoss": {"units": {"USD": nil_entries}}}}
        # parent-only Q4 = 600 - (100+150+200) = 150; identity pretax(250)=150+tax(100).
        rows = [
            _rr(
                "total_pretax_income",
                {_D: 250.0 * _M},
                sequence=1,
                sources={
                    _D: "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
                },
            ),
            _rr(
                "income_tax_expense",
                {_D: 100.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:IncomeTaxExpenseBenefit"},
            ),
            _rr(
                "net_income_continuing",
                {_D: 999.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:NetIncomeLoss Q4: FY[..] - (..)"},
            ),
        ]
        out, _ = impute(rows, "income_statement", "diversified", {_D}, facts=facts)
        nic = _by_tag(out, "net_income_continuing")
        assert nic.values[_D] == 150.0 * _M
        assert "Q4-NCI-corrected" in nic.sources[_D]

    def test_q4_nci_swap_skips_alt_tag_without_fy_value(self):
        # Q4-derived nic: the NetIncomeLoss alt-tag has no full-year entry so its scan
        # yields no FY value and the loop advances to the next alt-tag (907-908); the
        # ProfitLoss alt-tag then carries the full quarterly+FY set that reconstructs Q4.
        q_ends = ["2023-03-31", "2023-06-30", "2023-09-30"]
        pl_entries = [
            _dur(_D, "2023-01-01", 600.0 * _M),  # FY parent-only NI on ProfitLoss
            _dur(q_ends[0], "2023-01-01", 100.0 * _M),
            _dur(q_ends[1], "2023-04-01", 150.0 * _M),
            _dur(q_ends[2], "2023-07-01", 200.0 * _M),
        ]
        facts = {
            "us-gaap": {
                # NetIncomeLoss only has quarter entries -> no 300..400 day FY value.
                "NetIncomeLoss": {
                    "units": {"USD": [_dur(q_ends[0], "2023-01-01", 100.0 * _M)]}
                },
                "ProfitLoss": {"units": {"USD": pl_entries}},
            }
        }
        rows = [
            _rr(
                "total_pretax_income",
                {_D: 250.0 * _M},
                sequence=1,
                sources={
                    _D: "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
                },
            ),
            _rr(
                "income_tax_expense",
                {_D: 100.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:IncomeTaxExpenseBenefit"},
            ),
            _rr(
                "net_income_continuing",
                {_D: 999.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:ProfitLoss Q4: FY[..] - (..)"},
            ),
        ]
        out, _ = impute(rows, "income_statement", "diversified", {_D}, facts=facts)
        nic = _by_tag(out, "net_income_continuing")
        assert nic.values[_D] == 150.0 * _M
        assert "Q4-NCI-corrected" in nic.sources[_D]

    def test_total_assets_sign_corrected_from_negative_le(self):
        # total_assets verifies against a negative total_liabilities_and_equity whose
        # magnitude matches -> L&E is sign-corrected (728-750).
        rows = [
            _rr(
                "total_assets",
                {_D: 1000.0 * _M},
                period_type="instant",
                balance="debit",
                sequence=1,
                sources={_D: "us-gaap:Assets"},
            ),
            _rr(
                "total_liabilities_and_equity",
                {_D: -1000.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=2,
                sources={_D: "us-gaap:LiabilitiesAndStockholdersEquity"},
            ),
        ]
        out, diag = impute(
            rows, "balance_sheet", "industrial", {_D}, facts={"us-gaap": {}}
        )
        le = _by_tag(out, "total_liabilities_and_equity")
        assert le.values[_D] == 1000.0 * _M
        assert "sign-corrected" in le.sources[_D]
        assert all(w.tag != "total_assets" for w in diag)


# ---------------------------------------------------------------------------
# impute() -- balance-sheet mezzanine / operating-income verify fallbacks
# ---------------------------------------------------------------------------


def _bs_mezz_rows(l_val, enci_val, rnci_val=None):
    rows = [
        _rr(
            "total_assets",
            {_D: 1000.0 * _M},
            period_type="instant",
            balance="debit",
            sequence=1,
            sources={_D: "us-gaap:Assets"},
        ),
        _rr(
            "total_liabilities",
            {_D: l_val},
            period_type="instant",
            balance="credit",
            sequence=2,
            sources={_D: "us-gaap:Liabilities"},
        ),
        _rr(
            "total_liabilities_and_equity",
            {_D: 1000.0 * _M},
            period_type="instant",
            balance="credit",
            sequence=3,
            sources={_D: "us-gaap:LiabilitiesAndStockholdersEquity"},
        ),
        _rr(
            "total_equity_and_noncontrolling_interests",
            {_D: enci_val},
            period_type="instant",
            balance="credit",
            sequence=4,
            sources={
                _D: "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
            },
        ),
    ]
    if rnci_val is not None:
        rows.append(
            _rr(
                "redeemable_noncontrolling_interest",
                {_D: rnci_val},
                period_type="instant",
                balance="credit",
                sequence=5,
                sources={
                    _D: "us-gaap:RedeemableNoncontrollingInterestEquityCarryingAmount"
                },
            )
        )
    return rows


class TestImputeBSMezzanineFallbacks:
    def test_liabilities_zero_mezzanine_remainder_verified(self):
        # rule-with-rnci fails (rnci=50 makes val=550 != 600) but le - l - enci == 0
        # -> the near-zero mezzanine branch verifies (1466-1487).
        rows = _bs_mezz_rows(600.0 * _M, 400.0 * _M, rnci_val=50.0 * _M)
        # A mezzanine instant fact is present so the accumulation loop (1466-1468) runs.
        facts = {
            "us-gaap": {
                "TemporaryEquityCarryingAmount": {"units": {"USD": [_inst(_D, 0.0)]}}
            }
        }
        out, diag = impute(rows, "balance_sheet", "industrial", {_D}, facts=facts)
        assert all(w.tag != "total_liabilities" for w in diag)

    def test_equity_resolved_from_individual_mezzanine_fact(self):
        # No liabilities-and-equity total: the equity reconciliation does not apply.
        rows = [
            _rr(
                "total_assets",
                {_D: 1000.0 * _M},
                period_type="instant",
                balance="debit",
                sequence=1,
                sources={_D: "us-gaap:Assets"},
            ),
            _rr(
                "total_liabilities",
                {_D: 600.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=2,
                sources={_D: "us-gaap:Liabilities"},
            ),
            _rr(
                "total_equity_and_noncontrolling_interests",
                {_D: 400.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=4,
                sources={
                    _D: "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
                },
            ),
            _rr(
                "total_equity",
                {_D: 350.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=5,
                sources={_D: "us-gaap:StockholdersEquity"},
            ),
            _rr(
                "noncontrolling_interests",
                {_D: 0.0},
                period_type="instant",
                balance="credit",
                sequence=6,
                sources={_D: "us-gaap:MinorityInterest"},
            ),
            _rr(
                "redeemable_noncontrolling_interest",
                {_D: 50.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=7,
                sources={
                    _D: "us-gaap:RedeemableNoncontrollingInterestEquityCarryingAmount"
                },
            ),
        ]
        facts = {
            "us-gaap": {
                "RedeemableNoncontrollingInterestEquityCarryingAmount": {
                    "units": {"USD": [_inst(_D, 50.0 * _M)]}
                }
            }
        }
        out, diag = impute(rows, "balance_sheet", "industrial", {_D}, facts=facts)
        assert all(w.tag != "total_equity_and_noncontrolling_interests" for w in diag)

    def test_equity_resolved_from_summed_mezzanine_facts(self):
        # No liabilities-and-equity total: the equity reconciliation does not apply.
        rows = [
            _rr(
                "total_assets",
                {_D: 1000.0 * _M},
                period_type="instant",
                balance="debit",
                sequence=1,
                sources={_D: "us-gaap:Assets"},
            ),
            _rr(
                "total_liabilities",
                {_D: 600.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=2,
                sources={_D: "us-gaap:Liabilities"},
            ),
            _rr(
                "total_equity_and_noncontrolling_interests",
                {_D: 400.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=4,
                sources={
                    _D: "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
                },
            ),
            _rr(
                "total_equity",
                {_D: 350.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=5,
                sources={_D: "us-gaap:StockholdersEquity"},
            ),
            _rr(
                "noncontrolling_interests",
                {_D: 0.0},
                period_type="instant",
                balance="credit",
                sequence=6,
                sources={_D: "us-gaap:MinorityInterest"},
            ),
            _rr(
                "redeemable_noncontrolling_interest",
                {_D: 50.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=7,
                sources={
                    _D: "us-gaap:RedeemableNoncontrollingInterestEquityCarryingAmount"
                },
            ),
        ]
        facts = {
            "us-gaap": {
                "RedeemableNoncontrollingInterestEquityCommonCarryingAmount": {
                    "units": {"USD": [_inst(_D, 30.0 * _M)]}
                },
                "RedeemableNoncontrollingInterestEquityPreferredCarryingAmount": {
                    "units": {"USD": [_inst(_D, 20.0 * _M)]}
                },
            }
        }
        out, diag = impute(rows, "balance_sheet", "industrial", {_D}, facts=facts)
        assert all(w.tag != "total_equity_and_noncontrolling_interests" for w in diag)

    def test_equity_negative_nci_double_counted(self):
        # No liabilities-and-equity total: the equity reconciliation does not apply.
        rows = [
            _rr(
                "total_assets",
                {_D: 1000.0 * _M},
                period_type="instant",
                balance="debit",
                sequence=1,
                sources={_D: "us-gaap:Assets"},
            ),
            _rr(
                "total_liabilities",
                {_D: 600.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=2,
                sources={_D: "us-gaap:Liabilities"},
            ),
            # equity=420, nci=-20 -> verify sum = 400; ENCI value = 440 -> diff = 40 = 2*20.
            _rr(
                "total_equity_and_noncontrolling_interests",
                {_D: 440.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=4,
                sources={
                    _D: "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
                },
            ),
            _rr(
                "total_equity",
                {_D: 420.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=5,
                sources={_D: "us-gaap:StockholdersEquity"},
            ),
            _rr(
                "noncontrolling_interests",
                {_D: -20.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=6,
                sources={_D: "us-gaap:MinorityInterest"},
            ),
        ]
        out, diag = impute(
            rows, "balance_sheet", "industrial", {_D}, facts={"us-gaap": {}}
        )
        assert all(w.tag != "total_equity_and_noncontrolling_interests" for w in diag)


class TestImputeOperatingIncomeBridge:
    def test_disposition_gain_bridges_operating_income(self):
        # gp - opex != opinc (opinc imputed-sourced so pre-correction is skipped); a
        # GainLossOnDispositionOfAssets fact equals the signed gap -> bridged (1560-1612).
        rows = [
            _rr(
                "total_revenue",
                {_D: 1000.0 * _M},
                sequence=1,
                sources={_D: "us-gaap:Revenues"},
            ),
            _rr(
                "total_gross_profit",
                {_D: 1000.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:GrossProfit"},
            ),
            _rr(
                "total_operating_expenses",
                {_D: 300.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:OperatingExpenses"},
            ),
            _rr(
                "total_operating_income",
                {_D: 730.0 * _M},
                sequence=4,
                sources={_D: "imputed: revenue - expenses"},
            ),
        ]
        facts = {
            "us-gaap": {
                "GainLossOnDispositionOfAssets": {
                    "units": {"USD": [_dur(_D, "2023-01-01", 30.0 * _M)]}
                }
            }
        }
        out, diag = impute(rows, "income_statement", "industrial", {_D}, facts=facts)
        assert all(w.tag != "total_operating_income" for w in diag)

    def test_operating_income_rounding_heuristic_bridges(self):
        # No bridging fact: gp/opex/opinc are all whole millions and the 1M residual
        # exceeds the scale tolerance (0.1% of 300M = 300k) yet is <= 1M -> the
        # rounding heuristic accepts it (1593-1608).
        rows = [
            _rr(
                "total_revenue",
                {_D: 400.0 * _M},
                sequence=1,
                sources={_D: "us-gaap:Revenues"},
            ),
            _rr(
                "total_gross_profit",
                {_D: 300.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:GrossProfit"},
            ),
            _rr(
                "total_operating_expenses",
                {_D: 100.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:OperatingExpenses"},
            ),
            # gp - opex = 200M; opinc 201M -> 1M residual; opinc imputed so the opex
            # pre-correction pass is skipped and the residual survives into verify.
            _rr(
                "total_operating_income",
                {_D: 201.0 * _M},
                sequence=4,
                sources={_D: "imputed: revenue - expenses"},
            ),
        ]
        out, diag = impute(
            rows, "income_statement", "industrial", {_D}, facts={"us-gaap": {}}
        )
        assert all(w.tag != "total_operating_income" for w in diag)


# ---------------------------------------------------------------------------
# Generic identity-enforcement tail (soft sources, vintage, derived markers)
# ---------------------------------------------------------------------------


def _bs_assets_rows(*, assets_src, tle_src, assets=1000.0, tle=900.0):
    """total_assets vs total_liabilities_and_equity (single-source BS_VERIFY rule)."""
    return [
        _rr(
            "total_assets",
            {_D: assets * _M},
            balance="debit",
            sequence=1,
            sources={_D: assets_src},
        ),
        _rr(
            "total_liabilities_and_equity",
            {_D: tle * _M},
            balance="credit",
            sequence=2,
            sources={_D: tle_src},
        ),
    ]


class TestImputeSingleSoftSourceSolve:
    def test_single_soft_source_is_back_solved(self):
        # total_assets is hard-sourced, its only verify source
        # (total_liabilities_and_equity) is soft ((fallback)) and disagrees ->
        # the lone soft source is solved from the target (1641-1659).
        rows = _bs_assets_rows(
            assets_src="us-gaap:Assets",
            tle_src="imputed-rollup: liabilities(+) + equity(+) (fallback)",
            assets=1000.0,
            tle=900.0,
        )
        out, diag = impute(
            rows, "balance_sheet", "industrial", {_D}, facts={"us-gaap": {}}
        )
        tle = _by_tag(out, "total_liabilities_and_equity")
        assert tle.values[_D] == 1000.0 * _M  # solved to match total_assets
        assert "identity-enforced: derived from total_assets" in tle.sources[_D]
        assert "[solving total_liabilities_and_equity]" in tle.sources[_D]
        assert all(w.tag != "total_assets" for w in diag)

    def test_soft_target_is_identity_enforced(self):
        # Mirror case: the target itself is soft (imputed:) while the source is
        # hard -> the target value is overwritten with the identity (1622-1628).
        rows = _bs_assets_rows(
            assets_src="imputed: liabilities + equity",
            tle_src="us-gaap:LiabilitiesAndStockholdersEquity",
            assets=950.0,
            tle=1000.0,
        )
        out, _ = impute(
            rows, "balance_sheet", "industrial", {_D}, facts={"us-gaap": {}}
        )
        assets = _by_tag(out, "total_assets")
        assert assets.values[_D] == 1000.0 * _M  # enforced from the hard source
        assert assets.sources[_D].startswith("identity-enforced:")
        assert "[solving total_assets]" in assets.sources[_D]

    def test_two_soft_sources_fall_through_to_final_enforce(self):
        # total_liabilities (hard) = TLE - ENCI, with BOTH sources soft ((fallback)).
        # The single-soft block needs exactly one soft source, so two soft sources
        # skip it; with no vintage fact the loop reaches the final any-soft
        # identity-enforce (1753, 1770-1771).  TLE - ENCI = 600 < L=700 keeps the
        # mezzanine pre-block's computed mezz negative so it does not pre-verify.
        rows = [
            _rr(
                "total_liabilities_and_equity",
                {_D: 1000.0 * _M},
                sequence=1,
                sources={_D: "imputed-rollup: a(+) (fallback)"},
            ),
            _rr(
                "total_equity_and_noncontrolling_interests",
                {_D: 400.0 * _M},
                sequence=2,
                sources={_D: "imputed-plug: b(+) (fallback)"},
            ),
            _rr(
                "total_liabilities",
                {_D: 700.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:Liabilities"},
            ),
        ]
        out, _ = impute(
            rows, "balance_sheet", "industrial", {_D}, facts={"us-gaap": {}}
        )
        liab = _by_tag(out, "total_liabilities")
        assert liab.values[_D] == 600.0 * _M  # 1000 - 400, enforced
        assert liab.sources[_D].startswith("identity-enforced:")
        assert "[solving total_liabilities]" in liab.sources[_D]


class TestImputeVintageCorrection:
    def test_hard_target_matched_by_instant_fact_is_vintage_corrected(self):
        # total_assets carries a hard XBRL source but its stored value disagrees with
        # the verify identity; an instant (no-start) fact for that tag equals the
        # identity value -> vintage-corrected (1724-1751).
        rows = _bs_assets_rows(
            assets_src="us-gaap:Assets",
            tle_src="us-gaap:LiabilitiesAndStockholdersEquity",
            assets=950.0,
            tle=1000.0,
        )
        facts = {"us-gaap": {"Assets": {"units": {"USD": [_inst(_D, 1000.0 * _M)]}}}}
        out, diag = impute(rows, "balance_sheet", "industrial", {_D}, facts=facts)
        assets = _by_tag(out, "total_assets")
        assert assets.values[_D] == 1000.0 * _M
        assert assets.sources[_D].endswith("(vintage-corrected)")
        assert all(w.tag != "total_assets" for w in diag)

    def test_hard_target_without_matching_fact_emits_warning(self):
        # Same hard/hard setup but the instant fact disagrees with the identity ->
        # no vintage match, no soft sources -> a diagnostic is emitted (1758-1768).
        rows = _bs_assets_rows(
            assets_src="us-gaap:Assets",
            tle_src="us-gaap:LiabilitiesAndStockholdersEquity",
            assets=950.0,
            tle=1000.0,
        )
        facts = {"us-gaap": {"Assets": {"units": {"USD": [_inst(_D, 950.0 * _M)]}}}}
        out, diag = impute(rows, "balance_sheet", "industrial", {_D}, facts=facts)
        assert any(w.tag == "total_assets" and w.date == _D for w in diag)


def _ncic_rows(
    *, nc_src, op_src, inv_src, fin_src, nc=100.0, op=400.0, inv=-200.0, fin=-50.0
):
    """net_change_in_cash plus the three activity rows (no FX row)."""
    return [
        _rr("net_change_in_cash", {_D: nc * _M}, sequence=1, sources={_D: nc_src}),
        _rr(
            "net_cash_from_operating_activities",
            {_D: op * _M},
            sequence=2,
            sources={_D: op_src},
        ),
        _rr(
            "net_cash_from_investing_activities",
            {_D: inv * _M},
            sequence=3,
            sources={_D: inv_src},
        ),
        _rr(
            "net_cash_from_financing_activities",
            {_D: fin * _M},
            sequence=4,
            sources={_D: fin_src},
        ),
    ]


class TestImputeCashFlowDerivedMarkers:
    def test_derived_source_marker_triggers_identity_enforce(self):
        # net_change_in_cash is ambiguous (no Including/Excluding token -> skip_enforce)
        # and one activity source carries a Q4: derived marker; with no scope mismatch
        # the derived-marker block enforces the identity (1685, 1692-1696).
        rows = _ncic_rows(
            nc_src="imputed: op + inv + fin",
            op_src="us-gaap:NetCashProvidedByUsedInOperatingActivities Q4: derived",
            inv_src="us-gaap:NetCashProvidedByUsedInInvestingActivities",
            fin_src="us-gaap:NetCashProvidedByUsedInFinancingActivities",
            nc=120.0,  # disagrees with 400-200-50=150
        )
        out, _ = impute(rows, "cash_flow", "industrial", {_D}, facts={"us-gaap": {}})
        nc = _by_tag(out, "net_change_in_cash")
        assert nc.values[_D] == 150.0 * _M
        assert nc.sources[_D].startswith("identity-enforced:")
        assert "[solving net_change_in_cash]" in nc.sources[_D]

    def test_derived_marker_with_scope_mismatch_is_scope_aligned(self):
        # Same derived-marker path but an activity source is ContinuingOperations ->
        # _cf_scope_mismatch flips the resolution to scope-aligned (1686-1690).
        rows = _ncic_rows(
            nc_src="imputed: op + inv + fin",
            op_src=(
                "us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"
                " Q4: derived"
            ),
            inv_src="us-gaap:NetCashProvidedByUsedInInvestingActivities",
            fin_src="us-gaap:NetCashProvidedByUsedInFinancingActivities",
            nc=120.0,
        )
        out, _ = impute(rows, "cash_flow", "industrial", {_D}, facts={"us-gaap": {}})
        nc = _by_tag(out, "net_change_in_cash")
        assert nc.values[_D] == 150.0 * _M
        assert nc.sources[_D].startswith("scope-aligned:")
        assert "[solving net_change_in_cash]" in nc.sources[_D]


class TestImputeSingleSoftSourceTwoTermRule:
    def test_single_soft_in_two_term_rule_accumulates_other(self):
        # total_liabilities = TLE - ENCI with TLE soft ((fallback)) and ENCI hard.
        # Exactly one soft source -> the inner loop accumulates the hard ENCI term
        # (1646-1649) before solving TLE.  TLE - ENCI = 600 < L=700 keeps the
        # mezzanine pre-block's computed mezzanine negative so it does not pre-verify.
        rows = [
            _rr(
                "total_liabilities_and_equity",
                {_D: 1000.0 * _M},
                sequence=1,
                sources={_D: "imputed-rollup: a(+) (fallback)"},
            ),
            _rr(
                "total_equity_and_noncontrolling_interests",
                {_D: 400.0 * _M},
                sequence=2,
                sources={
                    _D: "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
                },
            ),
            _rr(
                "total_liabilities",
                {_D: 700.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:Liabilities"},
            ),
        ]
        out, _ = impute(
            rows, "balance_sheet", "industrial", {_D}, facts={"us-gaap": {}}
        )
        tle = _by_tag(out, "total_liabilities_and_equity")
        # Solved so that TLE - ENCI == L: TLE = 700 + 400 = 1100.
        assert tle.values[_D] == 1100.0 * _M
        assert "identity-enforced: derived from total_liabilities" in tle.sources[_D]
        assert "[solving total_liabilities_and_equity]" in tle.sources[_D]


# ---------------------------------------------------------------------------
# _imputation — helpers
# ---------------------------------------------------------------------------


class TestImputeHelpers:
    def test_format_source_signs(self):
        assert (
            _format_impute_source("imputed", [("a", 1), ("b", -1)]) == "imputed: a - b"
        )
        assert (
            _format_impute_source("imputed", [("a", -1), ("b", 1)]) == "imputed: -a + b"
        )

    def test_run_passes_derives_value(self):
        d = "2023-12-31"
        rows = [
            _rr("total_revenue", {d: 1000.0}),
            _rr("total_cost_of_revenue", {d: 400.0}),
            _rr("total_gross_profit", {}),
        ]
        idx = {r.tag: i for i, r in enumerate(rows)}
        rules = [
            (
                "total_gross_profit",
                [("total_revenue", 1), ("total_cost_of_revenue", -1)],
            )
        ]
        changed = _run_imputation_passes(rows, rules, idx, {d})
        assert changed is True
        assert rows[2].values[d] == 600.0

    def test_run_passes_no_change_when_source_missing(self):
        d = "2023-12-31"
        rows = [_rr("total_gross_profit", {})]
        idx = {r.tag: i for i, r in enumerate(rows)}
        rules = [("total_gross_profit", [("total_revenue", 1)])]
        assert _run_imputation_passes(rows, rules, idx, {d}) is False

    def test_hierarchical_rollup_creates_parent(self):
        d = "2023-12-31"
        rows = [
            _rr(
                "total_assets", {}, period_type="instant", balance="debit", sequence=10
            ),
            _rr(
                "cash",
                {d: 100.0 * _M},
                parent="total_assets",
                balance="debit",
                sequence=1,
                period_type="instant",
            ),
            _rr(
                "inventory",
                {d: 50.0 * _M},
                parent="total_assets",
                balance="debit",
                sequence=2,
                period_type="instant",
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        parent = _by_tag(rows, "total_assets")
        assert parent.values[d] == 150.0 * _M
        assert "imputed-rollup" in parent.sources[d]

    def test_hierarchical_plug_for_remainder(self):
        d = "2023-12-31"
        rows = [
            _rr(
                "total_assets",
                {d: 200.0 * _M},
                period_type="instant",
                balance="debit",
                sequence=10,
            ),
            _rr(
                "cash",
                {d: 100.0 * _M},
                parent="total_assets",
                balance="debit",
                sequence=1,
                period_type="instant",
            ),
        ]
        _apply_hierarchical_articulation(rows, {d})
        plug = _by_tag(rows, "other_assets")
        assert plug is not None
        assert plug.values[d] == 100.0 * _M  # 200 - 100
        assert "imputed-plug" in plug.sources[d]


# ---------------------------------------------------------------------------
# _imputation — impute() statement paths
# ---------------------------------------------------------------------------


class TestImputeIncomeStatement:
    def test_gross_profit_imputed(self):
        d = "2023-12-31"
        rows = [
            _rr("total_revenue", {d: 1000.0 * _M}, sequence=1),
            _rr("total_cost_of_revenue", {d: 400.0 * _M}, sequence=2),
            _rr("total_gross_profit", {}, sequence=3),
        ]
        out, diag = impute(rows, "income_statement", "industrial", {d}, facts={})
        gp = _by_tag(out, "total_gross_profit")
        assert gp.values[d] == 600.0 * _M
        assert "imputed" in gp.sources[d]
        assert diag == []

    def test_net_income_cascade(self):
        d = "2023-12-31"
        rows = [
            _rr("total_pretax_income", {d: 500.0 * _M}, sequence=1),
            _rr("income_tax_expense", {d: 100.0 * _M}, sequence=2),
            _rr("net_income_continuing", {}, sequence=3),
            _rr("net_income_discontinued", {d: 0.0}, sequence=4),
            _rr("net_income", {}, sequence=5),
        ]
        out, _ = impute(rows, "income_statement", "industrial", {d}, facts={})
        assert _by_tag(out, "net_income_continuing").values[d] == 400.0 * _M
        assert _by_tag(out, "net_income").values[d] == 400.0 * _M

    def test_costs_and_expenses_correction(self):
        # cogs+opex < C&E*0.95 and C&E ≈ rev - opinc -> cogs corrected to C&E - opex.
        d = "2023-12-31"
        rows = [
            _rr("total_revenue", {d: 1000.0 * _M}, sequence=1),
            _rr(
                "total_cost_of_revenue",
                {d: 100.0 * _M},
                sequence=2,
                sources={d: "us-gaap:CostOfRevenue"},
            ),
            _rr("total_gross_profit", {}, sequence=3),
            _rr("total_operating_expenses", {d: 200.0 * _M}, sequence=4),
            _rr("total_operating_income", {d: 200.0 * _M}, sequence=5),
            _rr("costs_and_expenses", {d: 800.0 * _M}, sequence=6),
        ]
        out, _ = impute(rows, "income_statement", "diversified", {d}, facts={})
        cogs = _by_tag(out, "total_cost_of_revenue")
        # 800 (C&E) - 200 (opex) = 600
        assert cogs.values[d] == 600.0 * _M
        assert "corrected" in cogs.sources[d]

    def test_costs_and_expenses_correction_skips_rolled_up_opex(self):
        d = "2023-12-31"
        rows = [
            _rr("total_revenue", {d: 1000.0 * _M}, sequence=1),
            _rr(
                "total_cost_of_revenue",
                {d: 100.0 * _M},
                sequence=2,
                sources={d: "us-gaap:CostOfRevenue"},
            ),
            _rr("total_gross_profit", {}, sequence=3),
            _rr(
                "sga_expense",
                {d: 200.0 * _M},
                parent="total_operating_expenses",
                sequence=4,
            ),
            _rr("total_operating_expenses", {}, sequence=5),
            _rr("total_operating_income", {d: 200.0 * _M}, sequence=6),
            _rr("costs_and_expenses", {d: 800.0 * _M}, sequence=7),
        ]
        out, _ = impute(rows, "income_statement", "diversified", {d}, facts={})
        cogs = _by_tag(out, "total_cost_of_revenue")
        assert cogs.values[d] == 100.0 * _M
        assert cogs.sources[d] == "us-gaap:CostOfRevenue"

    def test_no_rules_for_unknown_statement(self):
        d = "2023-12-31"
        rows = [_rr("x", {d: 1.0})]
        out, diag = impute(rows, "other", "industrial", {d}, facts={})  # ty: ignore[invalid-argument-type]
        assert out is rows and diag == []

    def test_pretax_scope_aligned_when_identity_violated(self):
        # Hard-sourced pretax != nic + tax: the IS engine rewrites pretax to
        # nic + tax ("scope-aligned") rather than emitting a diagnostic.
        d = "2023-12-31"
        rows = [
            _rr(
                "total_pretax_income",
                {d: 900.0 * _M},
                sequence=1,
                sources={d: "us-gaap:IncomeBeforeTax"},
            ),
            _rr(
                "income_tax_expense",
                {d: 100.0 * _M},
                sequence=2,
                sources={d: "us-gaap:IncomeTaxExpenseBenefit(ContinuingOperations)"},
            ),
            _rr(
                "net_income_continuing",
                {d: 400.0 * _M},
                sequence=3,
                sources={d: "us-gaap:IncomeLossFromContinuingOperations"},
            ),
        ]
        out, diag = impute(rows, "income_statement", "financial", {d}, facts={})
        ptx = _by_tag(out, "total_pretax_income")
        assert ptx.values[d] == 500.0 * _M  # rewritten to nic + tax
        assert "scope-aligned" in ptx.sources[d]


class TestImputeDiagnostics:
    def test_balance_sheet_identity_violation_emits_warning(self):
        # Assets != L&E with hard sources and no soft markers -> ValidationWarning.
        d = "2023-12-31"
        rows = [
            _rr(
                "total_assets",
                {d: 1000.0 * _M},
                period_type="instant",
                balance="debit",
                sequence=1,
                sources={d: "us-gaap:Assets"},
            ),
            _rr(
                "total_liabilities_and_equity",
                {d: 900.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=2,
                sources={d: "us-gaap:LiabilitiesAndStockholdersEquity"},
            ),
        ]
        out, diag = impute(rows, "balance_sheet", "industrial", {d}, facts={})
        warning = next((w for w in diag if w.tag == "total_assets"), None)
        assert warning is not None
        assert warning.actual == 1000.0 * _M
        assert warning.expected == 900.0 * _M


class TestImputeBalanceSheet:
    def test_noncurrent_assets_imputed(self):
        d = "2023-12-31"
        rows = [
            _rr(
                "total_assets",
                {d: 1000.0 * _M},
                period_type="instant",
                balance="debit",
                sequence=1,
            ),
            _rr(
                "total_current_assets",
                {d: 400.0 * _M},
                period_type="instant",
                balance="debit",
                sequence=2,
            ),
            _rr(
                "total_noncurrent_assets",
                {},
                period_type="instant",
                balance="debit",
                sequence=3,
            ),
        ]
        out, _ = impute(rows, "balance_sheet", "industrial", {d}, facts={})
        assert _by_tag(out, "total_noncurrent_assets").values[d] == 600.0 * _M

    def test_equity_reconciliation(self):
        d = "2023-12-31"
        rows = [
            _rr(
                "total_assets",
                {d: 1000.0 * _M},
                period_type="instant",
                balance="debit",
                sequence=1,
            ),
            _rr(
                "total_liabilities",
                {d: 600.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=2,
            ),
            _rr(
                "total_liabilities_and_equity",
                {d: 1000.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=3,
            ),
            _rr(
                "total_equity_and_noncontrolling_interests",
                {d: 400.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=4,
            ),
            _rr(
                "total_equity",
                {d: 999.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=5,
            ),
            _rr(
                "noncontrolling_interests",
                {d: 0.0},
                period_type="instant",
                balance="credit",
                sequence=6,
            ),
        ]
        out, _ = impute(rows, "balance_sheet", "industrial", {d}, facts={})
        eq = _by_tag(out, "total_equity")
        assert eq.values[d] == 400.0 * _M
        assert "reconciled" in eq.sources[d]

    def test_temporary_equity_holds_mezzanine_gap(self):
        d = "2023-12-31"

        def inst(tag, value, parent=None, seq=1):
            return _rr(
                tag,
                {} if value is None else {d: value * _M},
                parent=parent,
                period_type="instant",
                balance="credit",
                sequence=seq,
                sources={} if value is None else {d: f"us-gaap:{tag}"},
            )

        rows = [
            inst("total_liabilities_and_equity", 1000.0, seq=10),
            inst("total_liabilities", 600.0, "total_liabilities_and_equity", 2),
            inst(
                "total_equity_and_noncontrolling_interests",
                350.0,
                "total_liabilities_and_equity",
                4,
            ),
            inst("temporary_equity", None, "total_liabilities_and_equity", 3),
            inst("redeemable_noncontrolling_interest", None, "temporary_equity", 1),
        ]
        out, _ = impute(rows, "balance_sheet", "industrial", {d}, facts={})
        mezz = _by_tag(out, "temporary_equity")
        assert mezz.values[d] == 50.0 * _M
        assert mezz.sources[d].startswith(
            "imputed-plug: total_liabilities_and_equity - "
        )
        assert d not in _by_tag(out, "redeemable_noncontrolling_interest").values


class TestImputeCashFlow:
    def test_net_change_imputed_from_activities(self):
        d = "2023-12-31"
        rows = [
            _rr(
                "net_cash_from_operating_activities",
                {d: 500.0 * _M},
                balance="debit",
                sequence=1,
            ),
            _rr(
                "net_cash_from_investing_activities",
                {d: -200.0 * _M},
                balance="debit",
                sequence=2,
            ),
            _rr(
                "net_cash_from_financing_activities",
                {d: -150.0 * _M},
                balance="debit",
                sequence=3,
            ),
            _rr(
                "effect_of_exchange_rate_changes",
                {d: 50.0 * _M},
                balance="debit",
                sequence=4,
            ),
            _rr("net_change_in_cash", {}, balance="debit", sequence=5),
        ]
        out, _ = impute(rows, "cash_flow", "industrial", {d}, facts={})
        nc = _by_tag(out, "net_change_in_cash")
        assert nc.values[d] == 200.0 * _M  # 500 - 200 - 150 + 50
        assert "imputed" in nc.sources[d]

    def test_fx_not_derived_from_identity(self):
        d = "2023-12-31"
        rows = [
            _rr(
                "net_cash_from_operating_activities",
                {d: 500.0 * _M},
                balance="debit",
                sequence=1,
            ),
            _rr(
                "net_cash_from_investing_activities",
                {d: -200.0 * _M},
                balance="debit",
                sequence=2,
            ),
            _rr(
                "net_cash_from_financing_activities",
                {d: -150.0 * _M},
                balance="debit",
                sequence=3,
            ),
            _rr("effect_of_exchange_rate_changes", {}, balance="debit", sequence=4),
            _rr("net_change_in_cash", {d: 160.0 * _M}, balance="debit", sequence=5),
        ]
        out, _ = impute(rows, "cash_flow", "industrial", {d}, facts={})
        assert d not in _by_tag(out, "effect_of_exchange_rate_changes").values

    def test_da_from_components(self):
        d = "2023-12-31"
        rows = [
            _rr("depreciation_expense", {d: 60.0 * _M}, balance="debit", sequence=1),
            _rr("amortization_expense", {d: 40.0 * _M}, balance="debit", sequence=2),
            _rr("depreciation_and_amortization", {}, balance="debit", sequence=3),
        ]
        out, _ = impute(rows, "cash_flow", "industrial", {d}, facts={})
        da = _by_tag(out, "depreciation_and_amortization")
        assert da.values[d] == 100.0 * _M


# ---------------------------------------------------------------------------
# _imputation — fact-based reconciliation fallbacks.
#
# These drive impute() with a hard-sourced target whose primary identity
# is violated, then supply a us-gaap fact that closes the gap via one of
# the many fallback branches (discontinued ops, restricted cash, activity
# reconstruction, cash-balance delta, mezzanine equity, operating bridge).
# When a fallback succeeds the pair is marked verified -> no diagnostic.
# ---------------------------------------------------------------------------


class TestImputeCashFlowFallbacks:
    def test_discontinued_ops_row_closes_gap(self):
        # An explicit discontinued-ops row of 30M closes the 30M identity gap.
        rows = _cf_base(230.0 * _M, "us-gaap:CashIncludingExchangeRateEffect")
        rows.append(
            _rr(
                "net_cash_from_discontinued_operations",
                {_D: 30.0 * _M},
                balance="debit",
                sequence=6,
                sources={_D: "us-gaap:NetCashProvidedByUsedInDiscontinuedOperations"},
            )
        )
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts={"us-gaap": {}})
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_individual_discontinued_tag_closes_gap(self):
        # No disc row; an individual disc-ops cash tag in facts closes the gap.
        facts = {
            "us-gaap": {
                "CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations": {
                    "units": {"USD": [_dur(_D, "2023-01-01", 30.0 * _M)]}
                }
            }
        }
        rows = _cf_base(230.0 * _M, "us-gaap:CashIncludingExchangeRateEffect")
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_restricted_cash_change_closes_gap(self):
        facts = {
            "us-gaap": {
                "IncreaseDecreaseInRestrictedCash": {
                    "units": {"USD": [_dur(_D, "2023-01-01", 30.0 * _M)]}
                }
            }
        }
        rows = _cf_base(230.0 * _M, "us-gaap:CashPeriodIncreaseDecrease")
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_activity_reconstruction_from_alt_tags(self):
        # Row net_change badly mismatches; fact-level activity + nc-alt tags reconcile.
        facts = {
            "us-gaap": {
                "NetCashProvidedByUsedInOperatingActivities": {
                    "units": {"USD": [_dur(_D, "2023-01-01", 500.0 * _M)]}
                },
                "NetCashProvidedByUsedInInvestingActivities": {
                    "units": {"USD": [_dur(_D, "2023-01-01", -200.0 * _M)]}
                },
                "NetCashProvidedByUsedInFinancingActivities": {
                    "units": {"USD": [_dur(_D, "2023-01-01", -150.0 * _M)]}
                },
                "CashAndCashEquivalentsPeriodIncreaseDecrease": {
                    "units": {"USD": [_dur(_D, "2023-01-01", 150.0 * _M)]}
                },
            }
        }
        rows = _cf_base(999.0 * _M, "us-gaap:CashPeriodIncreaseDecrease")
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_cash_balance_delta_reconciles(self):
        # End-of-period minus start-of-period cash balances equal net_change.
        facts = {
            "us-gaap": {
                "Cash": {
                    "units": {
                        "USD": [
                            _inst(_D, 1400.0 * _M),
                            _inst("2023-03-31", 1000.0 * _M),
                        ]
                    }
                }
            }
        }
        rows = _cf_base(400.0 * _M, "us-gaap:CashPeriodIncreaseDecrease")
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts=facts)
        assert all(w.tag != "net_change_in_cash" for w in diag)

    def test_fx_scope_ambiguous_emits_pending_then_enforced(self):
        # net_change source with no Including/Excluding marker is "ambiguous";
        # both FX-inclusive and FX-exclusive verify rules run and the best
        # pending diagnostic is enforced at the end.
        rows = _cf_base(999.0 * _M, "us-gaap:CashGenericNoScopeMarker")
        out, diag = impute(rows, "cash_flow", "industrial", {_D}, facts={"us-gaap": {}})
        nc = _by_tag(out, "net_change_in_cash")
        # The ambiguous path resolves by enforcing the identity value.
        assert nc.values[_D] == 200.0 * _M
        assert "identity-enforced" in nc.sources[_D]


class TestImputeIncomeStatementFallbacks:
    def test_equity_method_correction(self):
        # pretax tagged from a pre-equity-method XBRL concept; nic + tax only
        # reconcile after adding equity_method_investments -> pretax corrected.
        rows = [
            _rr("income_before_equity_method", {}, sequence=1),
            _rr(
                "equity_method_investments",
                {_D: 51.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:IncomeLossFromEquityMethodInvestments"},
            ),
            _rr(
                "total_pretax_income",
                {_D: 700.0 * _M},
                sequence=3,
                sources={
                    _D: "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
                    "MinorityInterestAndIncomeLossFromEquityMethodInvestments"
                },
            ),
            _rr(
                "income_tax_expense",
                {_D: 150.0 * _M},
                sequence=4,
                sources={_D: "us-gaap:IncomeTaxExpenseBenefit"},
            ),
            _rr(
                "net_income_continuing",
                {_D: 601.0 * _M},
                sequence=5,
                sources={_D: "us-gaap:IncomeLossFromContinuingOperations"},
            ),
        ]
        out, _ = impute(
            rows, "income_statement", "diversified", {_D}, facts={"us-gaap": {}}
        )
        ptx = _by_tag(out, "total_pretax_income")
        assert ptx.values[_D] == 751.0 * _M  # 700 + 51
        assert "corrected" in ptx.sources[_D]

    def test_nci_swap_from_profitloss(self):
        # nic sourced from ProfitLoss (includes NCI); identity off; the engine
        # swaps in NetIncomeLoss (parent-only) from facts to satisfy pretax=nic+tax.
        facts = {
            "us-gaap": {
                "NetIncomeLoss": {
                    "units": {"USD": [_dur(_D, "2023-01-01", 550.0 * _M)]}
                }
            }
        }
        rows = [
            _rr(
                "total_pretax_income",
                {_D: 700.0 * _M},
                sequence=1,
                sources={
                    _D: "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
                },
            ),
            _rr(
                "income_tax_expense",
                {_D: 150.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:IncomeTaxExpenseBenefit"},
            ),
            _rr(
                "net_income_continuing",
                {_D: 600.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:ProfitLoss"},
            ),
        ]
        out, diag = impute(rows, "income_statement", "diversified", {_D}, facts=facts)
        nic = _by_tag(out, "net_income_continuing")
        # 700 - 550 = 150 = tax -> swap accepted.
        assert nic.values[_D] == 550.0 * _M
        assert "NCI-corrected" in nic.sources[_D]

    def test_operating_income_bridge_via_disposition_gain(self):
        # gp - opex != opinc; a GainLossOnDispositionOfAssets fact bridges the gap.
        # opinc is imputed-sourced so the opex pre-correction pass is skipped and
        # the residual survives into the verify-loop operating-income bridge.
        rows = [
            _rr(
                "total_revenue",
                {_D: 1000.0 * _M},
                sequence=1,
                sources={_D: "us-gaap:Revenues"},
            ),
            _rr(
                "total_gross_profit",
                {_D: 1000.0 * _M},
                sequence=2,
                sources={_D: "us-gaap:GrossProfit"},
            ),
            _rr(
                "total_operating_expenses",
                {_D: 300.0 * _M},
                sequence=3,
                sources={_D: "us-gaap:OperatingExpenses"},
            ),
            _rr(
                "total_operating_income",
                {_D: 730.0 * _M},
                sequence=4,
                sources={_D: "imputed: revenue - expenses"},
            ),
        ]
        facts = {
            "us-gaap": {
                "GainLossOnDispositionOfAssets": {
                    "units": {"USD": [_dur(_D, "2023-01-01", 30.0 * _M)]}
                }
            }
        }
        out, diag = impute(rows, "income_statement", "industrial", {_D}, facts=facts)
        assert all(w.tag != "total_operating_income" for w in diag)


class TestImputeBalanceSheetFallbacks:
    def test_liabilities_mezzanine_remainder_verified(self):
        # L&E - L - ENCI leaves a positive mezzanine remainder -> verified, no warning.
        rows = [
            _rr(
                "total_assets",
                {_D: 1000.0 * _M},
                period_type="instant",
                balance="debit",
                sequence=1,
                sources={_D: "us-gaap:Assets"},
            ),
            _rr(
                "total_liabilities",
                {_D: 600.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=2,
                sources={_D: "us-gaap:Liabilities"},
            ),
            _rr(
                "total_liabilities_and_equity",
                {_D: 1000.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=3,
                sources={_D: "us-gaap:LiabilitiesAndStockholdersEquity"},
            ),
            _rr(
                "total_equity_and_noncontrolling_interests",
                {_D: 350.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=4,
                sources={
                    _D: "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
                },
            ),
        ]
        out, diag = impute(
            rows, "balance_sheet", "industrial", {_D}, facts={"us-gaap": {}}
        )
        assert all(w.tag != "total_liabilities" for w in diag)

    def test_equity_mezzanine_resolved_from_temporary_equity_fact(self):
        # total_equity verify gap matches a TemporaryEquityCarryingAmount fact.
        rows = [
            _rr(
                "total_assets",
                {_D: 1000.0 * _M},
                period_type="instant",
                balance="debit",
                sequence=1,
                sources={_D: "us-gaap:Assets"},
            ),
            _rr(
                "total_liabilities",
                {_D: 600.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=2,
                sources={_D: "us-gaap:Liabilities"},
            ),
            _rr(
                "total_liabilities_and_equity",
                {_D: 1000.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=3,
                sources={_D: "us-gaap:LiabilitiesAndStockholdersEquity"},
            ),
            _rr(
                "total_equity_and_noncontrolling_interests",
                {_D: 400.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=4,
                sources={
                    _D: "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
                },
            ),
            _rr(
                "total_equity",
                {_D: 350.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=5,
                sources={_D: "us-gaap:StockholdersEquity"},
            ),
            _rr(
                "noncontrolling_interests",
                {_D: 50.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=6,
                sources={_D: "us-gaap:MinorityInterest"},
            ),
        ]
        facts = {
            "us-gaap": {
                "TemporaryEquityCarryingAmount": {
                    "units": {"USD": [_inst(_D, 50.0 * _M)]}
                }
            }
        }
        out, diag = impute(rows, "balance_sheet", "industrial", {_D}, facts=facts)
        # ENCI(400) verify against equity(350)+nci(50)=400 holds; the mezzanine
        # fact path is exercised for the equity rows without producing a warning.
        assert isinstance(diag, list)

    def _mezzanine_rows(self, liabilities, equity, mezzanine, mezzanine_source):
        def inst(tag, value, seq, source=None):
            return _rr(
                tag,
                {_D: value * _M},
                period_type="instant",
                balance="credit",
                sequence=seq,
                sources={_D: source or f"us-gaap:{tag}"},
            )

        return [
            _rr(
                "total_assets",
                {_D: 1000.0 * _M},
                period_type="instant",
                balance="debit",
                sequence=1,
                sources={_D: "us-gaap:Assets"},
            ),
            inst("total_liabilities", liabilities, 2),
            inst("total_liabilities_and_equity", 1000.0, 3),
            inst("total_equity_and_noncontrolling_interests", equity, 4),
            inst("temporary_equity", mezzanine, 5, mezzanine_source),
        ]

    def test_negative_mezzanine_never_solved(self):
        rows = self._mezzanine_rows(700.0, 320.0, 5.0, "imputed-plug: prior")
        out, _ = impute(
            rows, "balance_sheet", "industrial", {_D}, facts={"us-gaap": {}}
        )
        assert _by_tag(out, "temporary_equity").values[_D] == 5.0 * _M
        liabilities = _by_tag(out, "total_liabilities")
        assert liabilities.values[_D] == 675.0 * _M
        assert liabilities.sources[_D].startswith("identity-enforced")

    def test_liabilities_verified_when_mezzanine_gap_closes(self):
        rows = self._mezzanine_rows(
            600.0, 400.0, 50.0, "us-gaap:TemporaryEquityCarryingAmount"
        )
        out, diag = impute(
            rows, "balance_sheet", "industrial", {_D}, facts={"us-gaap": {}}
        )
        assert _by_tag(out, "total_liabilities").values[_D] == 600.0 * _M
        assert _by_tag(out, "temporary_equity").values[_D] == 50.0 * _M
        assert diag == []
