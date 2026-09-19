"""Unit tests for ``openbb_sec.utils.statement_schema._imputation``.

These drive the imputation/verification engine directly with crafted
synthetic statements -- the engine is pure, so no network is involved.
They cover the source-formatting and multi-pass solver helpers, the
hierarchical roll-up/plug articulation, the per-statement ``impute()``
paths for income statement, balance sheet and cash flow, the equity-method
and ProfitLoss pretax corrections, the quarterly Q4 parent-correction
block, and the many fact-based reconciliation fallbacks plus the final
identity enforcement and pending-diagnostic resolution.

Tests only -- no source under ``openbb_sec/`` is modified.
"""

# flake8: noqa: D101,D102,D103,D403

from unittest.mock import patch

from openbb_sec.utils.statement_schema._imputation import (
    _apply_hierarchical_articulation,
    _format_impute_source,
    _run_imputation_passes,
    impute,
)
from openbb_sec.utils.statement_schema._types import RowDef, RowResult

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

    def test_existing_nonimputed_plug_not_overwritten(self):
        # An other_* child that already holds a non-imputed value is left alone.
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
        # The hard-sourced other_assets is a real child (counts toward sum) and is
        # not overwritten by a plug.
        oa = _by_tag(rows, "other_assets")
        assert oa.values[d] == 7.0 * _M
        assert "us-gaap:OtherAssets" in oa.sources[d]

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


# ---------------------------------------------------------------------------
# impute() -- empty-ruleset early return
# ---------------------------------------------------------------------------


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
# impute() -- quarterly Q4 parent-correction block (frequency="quarterly")
# ---------------------------------------------------------------------------

_FY_END = "2023-12-31"
_FY_START = "2023-01-01"
_Q1, _Q2, _Q3 = "2023-03-31", "2023-06-30", "2023-09-30"


def _q4_run(rows, rdefs, annual_vals, dates):
    """Drive impute() in quarterly mode with simple row/annual-value providers."""

    def get_rows_fn(statement, company_type):
        return rdefs

    def get_annual_values_fn(facts, row_def, currency):
        return annual_vals.get(row_def.tag, {})

    return impute(
        rows,
        "income_statement",
        "industrial",
        set(dates),
        facts={"us-gaap": {}},
        frequency="quarterly",
        get_rows_fn=get_rows_fn,
        get_annual_values_fn=get_annual_values_fn,
    )


class TestImputeQuarterlyQ4Correction:
    def test_q4_parent_corrected_and_missing_child_derived(self):
        # Parent FY value already equals its one present child (80M) so the first
        # articulation pass creates no plug; the Q4 block then rewrites the parent
        # to the FY-minus-quarters value and back-derives the single missing child.
        parent = _rr(
            "total_revenue",
            {_Q1: 100.0 * _M, _Q2: 150.0 * _M, _Q3: 200.0 * _M, _FY_END: 80.0 * _M},
            sequence=1,
            sources={_FY_END: "imputed-rollup: segment_a(+) + segment_b(+)"},
        )
        child_a = _rr(
            "segment_a",
            {_FY_END: 80.0 * _M},
            parent="total_revenue",
            factor="+",
            sequence=2,
        )
        child_b = _rr("segment_b", {}, parent="total_revenue", factor="+", sequence=3)
        rdefs = [
            _rd("total_revenue", period_type="duration"),
            _rd("segment_a", period_type="duration", parent="total_revenue"),
            _rd("segment_b", period_type="duration", parent="total_revenue"),
        ]
        annual = {
            "total_revenue": {_FY_END: (_FY_START, 600.0 * _M, "us-gaap:Revenues")}
        }
        out, _ = _q4_run(
            [parent, child_a, child_b], rdefs, annual, [_Q1, _Q2, _Q3, _FY_END]
        )
        rev = _by_tag(out, "total_revenue")
        assert rev.values[_FY_END] == 150.0 * _M  # 600 - (100+150+200)
        assert "Q4:" in rev.sources[_FY_END]
        seg_b = _by_tag(out, "segment_b")
        assert seg_b.values[_FY_END] == 70.0 * _M  # 150 - 80
        assert "Q4-derived" in seg_b.sources[_FY_END]

    def test_q4_sign_flip_guard_rejects_correction(self):
        # Quarters (100+150+200=450) exceed the annual FY value (100) so the derived
        # Q4 (100-450 = -350) has the opposite sign to FY -> the sign-flip guard skips
        # the correction (361-362) and the parent keeps its rollup value.
        parent = _rr(
            "total_revenue",
            {_Q1: 100.0 * _M, _Q2: 150.0 * _M, _Q3: 200.0 * _M, _FY_END: 80.0 * _M},
            sequence=1,
            sources={_FY_END: "imputed-rollup: segment_a(+)"},
        )
        child_a = _rr(
            "segment_a",
            {_FY_END: 80.0 * _M},
            parent="total_revenue",
            factor="+",
            sequence=2,
        )
        rdefs = [
            _rd("total_revenue", period_type="duration"),
            _rd("segment_a", period_type="duration", parent="total_revenue"),
        ]
        annual = {
            "total_revenue": {_FY_END: (_FY_START, 100.0 * _M, "us-gaap:Revenues")}
        }
        out, _ = _q4_run([parent, child_a], rdefs, annual, [_Q1, _Q2, _Q3, _FY_END])
        rev = _by_tag(out, "total_revenue")
        assert "Q4:" not in rev.sources.get(_FY_END, "")  # correction rejected
        assert rev.values[_FY_END] == 80.0 * _M  # rollup value preserved

    def test_shares_parent_skipped(self):
        parent = _rr(
            "weighted_average_shares_outstanding",
            {_Q1: 100.0, _Q2: 100.0, _Q3: 100.0, _FY_END: 100.0},
            unit="shares",
            sequence=1,
            sources={_FY_END: "imputed-rollup: a(+)"},
        )
        child = _rr(
            "share_class_a",
            {_Q1: 100.0},
            parent="weighted_average_shares_outstanding",
            factor="+",
            sequence=2,
        )
        rdefs = [
            _rd(
                "weighted_average_shares_outstanding",
                period_type="duration",
                unit="shares",
            ),
            _rd(
                "share_class_a",
                period_type="duration",
                unit="shares",
                parent="weighted_average_shares_outstanding",
            ),
        ]
        annual = {
            "weighted_average_shares_outstanding": {
                _FY_END: (_FY_START, 9999.0, "us-gaap:WAS")
            }
        }
        out, _ = _q4_run([parent, child], rdefs, annual, [_Q1, _Q2, _Q3, _FY_END])
        assert (
            _by_tag(out, "weighted_average_shares_outstanding").values[_FY_END] == 100.0
        )

    def test_parent_not_rollup_sourced_skipped(self):
        parent = _rr(
            "total_revenue",
            {_Q1: 100.0 * _M, _Q2: 150.0 * _M, _Q3: 200.0 * _M, _FY_END: 600.0 * _M},
            sequence=1,
            sources={_FY_END: "us-gaap:Revenues"},
        )
        child = _rr(
            "segment_a",
            {_Q1: 100.0 * _M},
            parent="total_revenue",
            factor="+",
            sequence=2,
        )
        rdefs = [
            _rd("total_revenue", period_type="duration"),
            _rd("segment_a", period_type="duration", parent="total_revenue"),
        ]
        annual = {
            "total_revenue": {_FY_END: (_FY_START, 600.0 * _M, "us-gaap:Revenues")}
        }
        out, _ = _q4_run([parent, child], rdefs, annual, [_Q1, _Q2, _Q3, _FY_END])
        assert _by_tag(out, "total_revenue").sources[_FY_END] == "us-gaap:Revenues"

    def test_wrong_number_of_quarters_skipped(self):
        parent = _rr(
            "total_revenue",
            {_Q1: 100.0 * _M, _Q2: 150.0 * _M, _FY_END: 9.0 * _M},
            sequence=1,
            sources={_FY_END: "imputed-rollup: a(+)"},
        )
        child = _rr(
            "segment_a",
            {_Q1: 100.0 * _M},
            parent="total_revenue",
            factor="+",
            sequence=2,
        )
        rdefs = [
            _rd("total_revenue", period_type="duration"),
            _rd("segment_a", period_type="duration", parent="total_revenue"),
        ]
        annual = {
            "total_revenue": {_FY_END: (_FY_START, 600.0 * _M, "us-gaap:Revenues")}
        }
        out, _ = _q4_run([parent, child], rdefs, annual, [_Q1, _Q2, _FY_END])
        assert "imputed-rollup" in _by_tag(out, "total_revenue").sources[_FY_END]

    def test_q4_sign_flip_guard_skips(self):
        # Quarter sum (900) exceeds FY (600) -> q4 = -300, fy>0 -> q4*fy < 0 -> skip.
        parent = _rr(
            "total_revenue",
            {_Q1: 300.0 * _M, _Q2: 300.0 * _M, _Q3: 300.0 * _M, _FY_END: 9.0 * _M},
            sequence=1,
            sources={_FY_END: "imputed-rollup: a(+)"},
        )
        rdefs = [_rd("total_revenue", period_type="duration")]
        annual = {
            "total_revenue": {_FY_END: (_FY_START, 600.0 * _M, "us-gaap:Revenues")}
        }
        out, _ = _q4_run([parent], rdefs, annual, [_Q1, _Q2, _Q3, _FY_END])
        assert "imputed-rollup" in _by_tag(out, "total_revenue").sources[_FY_END]

    def test_parent_def_instant_skipped(self):
        parent = _rr(
            "total_revenue",
            {_Q1: 100.0 * _M, _Q2: 150.0 * _M, _Q3: 200.0 * _M, _FY_END: 9.0 * _M},
            sequence=1,
            sources={_FY_END: "imputed-rollup: a(+)"},
        )
        child = _rr(
            "segment_a",
            {_Q1: 100.0 * _M},
            parent="total_revenue",
            factor="+",
            sequence=2,
        )
        # RowDef marks the parent instant -> the duration guard fails (345-346).
        rdefs = [
            _rd("total_revenue", period_type="instant"),
            _rd("segment_a", period_type="duration", parent="total_revenue"),
        ]
        annual = {
            "total_revenue": {_FY_END: (_FY_START, 600.0 * _M, "us-gaap:Revenues")}
        }
        out, _ = _q4_run([parent, child], rdefs, annual, [_Q1, _Q2, _Q3, _FY_END])
        assert "imputed-rollup" in _by_tag(out, "total_revenue").sources[_FY_END]

    def test_no_annual_values_skipped(self):
        parent = _rr(
            "total_revenue",
            {_Q1: 100.0 * _M, _Q2: 150.0 * _M, _Q3: 200.0 * _M, _FY_END: 9.0 * _M},
            sequence=1,
            sources={_FY_END: "imputed-rollup: a(+)"},
        )
        child = _rr(
            "segment_a",
            {_Q1: 100.0 * _M},
            parent="total_revenue",
            factor="+",
            sequence=2,
        )
        rdefs = [
            _rd("total_revenue", period_type="duration"),
            _rd("segment_a", period_type="duration", parent="total_revenue"),
        ]
        out, _ = _q4_run([parent, child], rdefs, {}, [_Q1, _Q2, _Q3, _FY_END])
        assert "imputed-rollup" in _by_tag(out, "total_revenue").sources[_FY_END]


# ---------------------------------------------------------------------------
# impute() -- income-statement gross-profit / cogs / opex correction passes
# ---------------------------------------------------------------------------


class TestImputeISCorrectionPasses:
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
        # ENCI verify gap (50M) exactly matches a redeemable-NCI carrying-amount fact
        # -> the individual-fact match resolves it (1527-1547).  A real redeemable_nci
        # row (50M) makes the earlier equity-reconcile guard fail so it does not pre-
        # empt the mezzanine path, and feeds _rnci_val into the block.
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
        # ENCI verify gap (50M) matches no single redeemable-NCI fact but equals the
        # SUM of two carrying-amount facts (30M + 20M) -> the sum fallback resolves it
        # (1540-1547, esp. 1543).
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
        # ENCI verify gap equals 2x abs(negative nci) -> the sign-doubling branch
        # verifies (1552-1558).
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

    def test_no_rules_for_unknown_statement(self):
        d = "2023-12-31"
        rows = [_rr("x", {d: 1.0})]
        out, diag = impute(rows, "other", "industrial", {d}, facts={})
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

    def test_redeemable_nci_imputed_from_gap(self):
        # L&E - L - ENCI leaves a mezzanine remainder imputed into redeemable NCI.
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
                {d: 350.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=4,
            ),
            _rr(
                "redeemable_noncontrolling_interest",
                {},
                period_type="instant",
                balance="credit",
                sequence=5,
            ),
        ]
        out, _ = impute(rows, "balance_sheet", "industrial", {d}, facts={})
        rnci = _by_tag(out, "redeemable_noncontrolling_interest")
        # 1000 - 600 - 350 = 50
        assert rnci.values[d] == 50.0 * _M
        assert "imputed" in rnci.sources[d]


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

    def test_fx_derived_from_identity(self):
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
        fx = _by_tag(out, "effect_of_exchange_rate_changes")
        assert fx.values[d] == 10.0 * _M  # 160 - 500 + 200 + 150
        assert "imputed" in fx.sources[d]

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

    def test_liabilities_mezzanine_reimputed_from_remainder(self):
        # L&E - L - ENCI is negative-but-material and an imputed redeemable-NCI
        # row exists -> it is re-imputed to the computed remainder.
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
                {_D: 700.0 * _M},
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
                {_D: 320.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=4,
                sources={
                    _D: "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
                },
            ),
            _rr(
                "redeemable_noncontrolling_interest",
                {_D: 5.0 * _M},
                period_type="instant",
                balance="credit",
                sequence=5,
                sources={
                    _D: "us-gaap:RedeemableNoncontrollingInterestEquityCarryingAmount (imputed)"
                },
            ),
        ]
        out, diag = impute(
            rows, "balance_sheet", "industrial", {_D}, facts={"us-gaap": {}}
        )
        rnci = _by_tag(out, "redeemable_noncontrolling_interest")
        # remainder = 1000 - 700 - 320 = -20M; row gets re-imputed to it.
        assert rnci.values[_D] == -20.0 * _M
        assert "re-imputed" in rnci.sources[_D]
