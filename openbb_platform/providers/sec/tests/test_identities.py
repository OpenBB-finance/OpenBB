"""Unit tests for accounting identity enforcement in ``openbb_sec.utils.statement_schema._imputation``."""

# flake8: noqa: D101,D102,D103

from openbb_sec.utils.statement_schema._imputation import (
    _alternatives,
    _components,
    _expression,
    _failing,
    _identity,
    _identity_state,
    _identity_tolerance,
    _quarter_facts,
    _restated_fy,
    _rounding_term,
    _synthetic,
    enforce_identities,
    identity_diagnostics,
    identity_residuals,
    impute,
    reconcile_fiscal_year_ends,
    reported_derived,
)
from openbb_sec.utils.statement_schema._types import RowResult, StatementResult

_M = 1_000_000
_D = "2023-12-31"
_Q = ["2023-03-31", "2023-06-30", "2023-09-30"]
_STARTS = ["2023-01-01", "2023-04-01", "2023-07-01"]


def _rr(
    tag,
    values=None,
    *,
    parent=None,
    factor="+",
    sequence=1,
    period_type="duration",
    sources=None,
    balance="",
):
    return RowResult(
        tag=tag,
        label=tag,
        description="",
        parent=parent,
        sequence=sequence,
        factor=factor,
        balance=balance,
        unit="monetary",
        period_type=period_type,
        values=dict(values or {}),
        sources=dict(sources or {}),
    )


def _by(rows, tag):
    return next(r for r in rows if r.tag == tag)


def _children(rows):
    out: dict = {}
    for r in rows:
        if r.parent:
            out.setdefault(r.parent, []).append(r)
    return out


def _ni_rows(pretax, tax, ni, *, pretax_src="us-gaap:P", tax_src="us-gaap:T"):
    return [
        _rr(
            "total_pretax_income",
            {_D: pretax},
            parent="net_income_continuing",
            sequence=1,
            sources={_D: pretax_src},
        ),
        _rr(
            "income_tax_expense",
            {_D: tax} if tax is not None else {},
            parent="net_income_continuing",
            factor="-",
            sequence=2,
            sources={_D: tax_src} if tax is not None else {},
        ),
        _rr("net_income_continuing", {_D: ni}, sequence=3, sources={_D: "us-gaap:N"}),
    ]


def _never(row, date):
    return False


class TestHelpers:
    def test_reported_derived(self):
        row = _rr(
            "x",
            sources={
                "a": "imputed: y",
                "b": "us-gaap:X(fallback)",
                "c": "us-gaap:X",
                "d": "preliminary:derived: z",
            },
        )
        assert reported_derived(row, "a")
        assert reported_derived(row, "b")
        assert not reported_derived(row, "c")
        assert reported_derived(row, "d")

    def test_synthetic(self):
        assert _synthetic(
            _rr("other_equity_and_noncontrolling_interests"),
            "total_equity_and_noncontrolling_interests",
        )
        assert not _synthetic(_rr("total_cost_of_revenue"), "total_gross_profit")
        assert not _synthetic(_rr("other_gross_profit"), "total_net")

    def test_identity_tolerance_units(self):
        assert _identity_tolerance([10 * _M, 20 * _M], 3) == 1.5 * _M
        assert _identity_tolerance([10_000, 20_000], 4) == 0.1 * _M
        assert _identity_tolerance([10_001.5, 0], 2) == 0.1 * _M

    def test_expression(self):
        assert _expression([("a", 1), ("b", -1), ("c", 1)]) == "a - b + c"
        assert _expression([("a", -1), ("b", 1)]) == "-a + b"

    def test_rounding_term(self):
        signed = [("total_pretax_income", 1), ("income_tax_expense", -1)]
        assert (
            _rounding_term("income_statement", "net_income_continuing", signed)
            == "total_pretax_income"
        )
        assert (
            _rounding_term("income_statement", "total_gross_profit", [("x", 1)])
            == "total_gross_profit"
        )
        assert _rounding_term("other", "t", signed) == "t"


class TestIdentityTerms:
    def test_target_absent(self):
        rows = _ni_rows(10.0, 2.0, 8.0)
        by = {r.tag: r for r in rows}
        assert _identity("missing", None, by, _children(rows), _D) is None
        assert (
            _identity("net_income_continuing", None, by, _children(rows), "2020-01-01")
            is None
        )

    def test_explicit_terms_need_every_term(self):
        rows = [
            _rr("cash_at_end_of_period", {_D: 5.0}, period_type="instant"),
            _rr("cash_at_beginning_of_period", {_D: 4.0}, period_type="instant"),
            _rr("net_change_in_cash", {}),
        ]
        by = {r.tag: r for r in rows}
        terms = (("cash_at_beginning_of_period", 1), ("net_change_in_cash", 1))
        assert _identity("cash_at_end_of_period", terms, by, {}, _D) is None
        by["net_change_in_cash"].values[_D] = 1.0
        assert _identity("cash_at_end_of_period", terms, by, {}, _D) == list(terms)
        assert _identity("cash_at_end_of_period", (("nope", 1),), by, {}, _D) is None

    def test_children_need_leading_term(self):
        rows = _ni_rows(10.0, 2.0, 8.0)
        by = {r.tag: r for r in rows}
        assert _identity("net_income_continuing", None, by, _children(rows), _D) == [
            ("total_pretax_income", 1),
            ("income_tax_expense", -1),
        ]
        by["total_pretax_income"].values.pop(_D)
        assert _identity("net_income_continuing", None, by, _children(rows), _D) is None
        assert _identity("total_pretax_income", None, by, _children(rows), _D) is None

    def test_state_residuals_failing(self):
        rows = _ni_rows(10 * _M, 2 * _M, 9 * _M)
        by = {r.tag: r for r in rows}
        signed = _identity("net_income_continuing", None, by, _children(rows), _D)
        lhs, rhs, tol = _identity_state("net_income_continuing", signed, by, _D, 2 * _M)
        assert (lhs, rhs, tol) == (9 * _M, 8 * _M, 2 * _M)
        assert identity_residuals(rows, "income_statement", _D) == {
            "net_income_continuing": 1 * _M
        }
        assert _failing(rows, "income_statement", _D, {}) == {"net_income_continuing"}
        assert (
            _failing(rows, "income_statement", _D, {"net_income_continuing": 2 * _M})
            == set()
        )


class TestComponents:
    def test_requires_rollup_lines(self):
        rows = [
            _rr("total_pretax_income", {_D: 10.0}, sequence=5),
            _rr("total_operating_income", {}, parent="total_pretax_income", sequence=1),
            _rr(
                "total_other_income",
                {_D: 3.0},
                parent="total_pretax_income",
                sequence=2,
            ),
        ]
        kids = _children(rows)
        assert _components(rows[0], kids, _D) is None
        rows[1].values[_D] = 7.0
        assert _components(rows[0], kids, _D) == 10.0

    def test_through_plugs(self):
        rows = [
            _rr("total_equity", {_D: 10.0}, sequence=5),
            _rr(
                "total_common_equity",
                {_D: 10.0},
                parent="total_equity",
                sequence=2,
                sources={_D: "imputed-plug: x"},
            ),
            _rr("common_equity", {_D: 4.0}, parent="total_common_equity", sequence=1),
            _rr(
                "other_equity",
                {_D: 6.0},
                parent="total_common_equity",
                sequence=1.5,
                sources={_D: "imputed-plug: y"},
            ),
            _rr(
                "treasury_stock",
                {_D: 1.0},
                parent="total_common_equity",
                factor="-",
                sequence=1.7,
            ),
            _rr("preferred_stock", {}, parent="total_common_equity", sequence=1.8),
        ]
        kids = _children(rows)
        assert _components(rows[0], kids, _D) == 3.0
        assert _components(rows[0], kids, _D, depth=3) is None
        assert _components(rows[2], kids, _D) is None


class TestAlternatives:
    def _facts(self, entries):
        return {"us-gaap": {"P": {"units": {"USD": entries}}}}

    def test_annual_values(self):
        row = _rr("total_pretax_income", {_D: 10.0}, sources={_D: "us-gaap:P"})
        facts = self._facts(
            [
                {"end": _D, "start": "2023-01-01", "val": 12.0, "form": "10-K"},
                {"end": _D, "start": "2023-01-01", "val": 10.0, "form": "10-K"},
                {"end": _D, "start": "2023-10-01", "val": 3.0, "form": "10-K"},
                {"end": _D, "start": "2023-01-01", "val": 13.0, "form": "8-K"},
                {"end": _D, "val": 14.0, "form": "10-K"},
                {
                    "end": "2022-12-31",
                    "start": "2022-01-01",
                    "val": 15.0,
                    "form": "10-K",
                },
                {"end": _D, "start": "2023-01-01", "val": None, "form": "10-K"},
            ]
        )
        assert _alternatives(row, _D, facts, "USD", "annual") == {12.0}
        assert _alternatives(row, _D, facts, "USD", "quarterly") == {3.0}
        assert _alternatives(row, _D, None, "USD", "annual") == set()
        assert (
            _alternatives(
                _rr("x", {_D: 1.0}, sources={_D: "imputed: y"}),
                _D,
                facts,
                "USD",
                "annual",
            )
            == set()
        )
        assert (
            _alternatives(
                _rr("x", {_D: 1.0}, sources={_D: "us-gaap:Q"}),
                _D,
                facts,
                "USD",
                "annual",
            )
            == set()
        )


class TestQuarterFacts:
    def test_filed_quarters_and_restated_fy(self):
        facts = {
            "us-gaap": {
                "P": {
                    "units": {
                        "USD": [
                            {
                                "end": _D,
                                "start": "2023-10-01",
                                "val": 5.0 * _M,
                                "form": "10-K",
                            },
                            {
                                "end": _D,
                                "start": "2023-01-01",
                                "val": 20.0 * _M,
                                "form": "10-K",
                                "filed": "2024-02-01",
                            },
                            {
                                "end": _D,
                                "start": "2023-01-01",
                                "val": 18.0 * _M,
                                "form": "10-K",
                                "filed": "2025-02-01",
                            },
                            {
                                "end": _Q[2],
                                "start": "2023-07-01",
                                "val": 4.0 * _M,
                                "form": "10-Q",
                                "filed": "2024-10-01",
                            },
                            {
                                "end": _D,
                                "start": "2023-10-01",
                                "val": None,
                                "form": "10-K",
                            },
                        ]
                    }
                }
            }
        }
        row = _rr("x")
        assert _quarter_facts(
            row, {"us-gaap:P", None, "custom:Z"}, _D, facts, "USD", False
        ) == {5.0 * _M}
        assert _quarter_facts(row, {"us-gaap:P"}, _D, facts, "USD", True) == {-5.0 * _M}
        assert _quarter_facts(row, {"us-gaap:P"}, _D, None, "USD", False) == set()
        assert (
            _quarter_facts(row, {"us-gaap:Missing"}, _D, facts, "USD", False) == set()
        )
        assert _restated_fy(row, "us-gaap:P", _Q, _D, 18.0 * _M, facts, "USD", False)
        assert not _restated_fy(
            row, "us-gaap:P", _Q, _D, 20.0 * _M, facts, "USD", False
        )
        assert not _restated_fy(
            row, "imputed: y", _Q, _D, 18.0 * _M, facts, "USD", False
        )
        assert not _restated_fy(
            row, "us-gaap:Missing", _Q, _D, 18.0 * _M, facts, "USD", False
        )


class TestEnforceIdentities:
    def test_derived_term_solved(self):
        rows = _ni_rows(10 * _M, 2 * _M, 9 * _M, pretax_src="imputed: a + b")
        enforce_identities(
            rows, "income_statement", [_D], None, "USD", derived=reported_derived
        )
        pretax = _by(rows, "total_pretax_income")
        assert pretax.values[_D] == 11 * _M
        assert pretax.sources[_D] == (
            "identity-enforced: net_income_continuing + income_tax_expense [solving total_pretax_income]"
        )
        assert identity_diagnostics(rows, "income_statement", [_D]) == []

    def test_remainder_line_filled(self):
        rows = [
            _rr(
                "total_revenue",
                {_D: 100 * _M},
                parent="total_gross_profit",
                sequence=1,
                sources={_D: "us-gaap:R"},
            ),
            _rr(
                "total_cost_of_revenue",
                {},
                parent="total_gross_profit",
                factor="-",
                sequence=2,
            ),
            _rr(
                "total_gross_profit",
                {_D: 60 * _M},
                sequence=3,
                sources={_D: "us-gaap:G"},
            ),
        ]
        enforce_identities(rows, "income_statement", [_D], None, "USD", derived=_never)
        assert _by(rows, "total_cost_of_revenue").values[_D] == 40 * _M

    def test_other_filing_value(self):
        rows = _ni_rows(10 * _M, 2 * _M, 9 * _M)
        facts = {
            "us-gaap": {
                "P": {
                    "units": {
                        "USD": [
                            {
                                "end": _D,
                                "start": "2023-01-01",
                                "val": 11 * _M,
                                "form": "10-K",
                            }
                        ]
                    }
                }
            }
        }
        enforce_identities(rows, "income_statement", [_D], facts, "USD", derived=_never)
        pretax = _by(rows, "total_pretax_income")
        assert pretax.values[_D] == 11 * _M
        assert pretax.sources[_D] == "us-gaap:P (vintage-corrected)"

    def test_components_equal_implied(self):
        rows = _ni_rows(10 * _M, 2 * _M, 9 * _M)
        rows += [
            _rr(
                "income_tax_current",
                {_D: 0.5 * _M},
                parent="income_tax_expense",
                sequence=1,
            ),
            _rr(
                "income_tax_deferred",
                {_D: 0.5 * _M},
                parent="income_tax_expense",
                sequence=1.5,
            ),
        ]
        enforce_identities(rows, "income_statement", [_D], None, "USD", derived=_never)
        assert _by(rows, "income_tax_expense").values[_D] == 1 * _M

    def test_synthetic_plug_points_to_term(self):
        rows = _ni_rows(10 * _M, 2 * _M, 9 * _M)
        rows += [
            _rr(
                "total_operating_income",
                {_D: 4 * _M},
                parent="total_pretax_income",
                sequence=0.5,
            ),
            _rr(
                "other_pretax_income",
                {_D: 6 * _M},
                parent="total_pretax_income",
                sequence=0.9,
                sources={_D: "imputed-plug: x"},
            ),
        ]
        enforce_identities(rows, "income_statement", [_D], None, "USD", derived=_never)
        assert _by(rows, "total_pretax_income").values[_D] == 11 * _M

    def test_unresolved_falls_back_to_aligned_line(self):
        rows = _ni_rows(10 * _M, 2 * _M, 9 * _M)
        rows.append(
            _rr(
                "income_tax_current",
                {_D: 1.5 * _M},
                parent="income_tax_expense",
                sequence=1,
            )
        )
        enforce_identities(
            rows,
            "income_statement",
            [_D],
            None,
            "USD",
            derived=lambda r, d: r.tag != "net_income_continuing",
        )
        assert _by(rows, "income_tax_expense").values[_D] == 2 * _M
        assert _by(rows, "total_pretax_income").values[_D] == 11 * _M

    def test_fallback_needs_required_lines(self):
        rows = [
            _rr(
                "total_revenue", {_D: 100 * _M}, parent="total_gross_profit", sequence=1
            ),
            _rr(
                "total_cost_of_revenue",
                {},
                parent="total_gross_profit",
                factor="-",
                sequence=2,
            ),
            _rr("total_gross_profit", {_D: 120 * _M}, sequence=3),
        ]
        enforce_identities(
            rows, "income_statement", [_D], None, "USD", derived=lambda r, d: True
        )
        assert _by(rows, "total_gross_profit").values[_D] == 120 * _M

    def test_rounding_within_allowance(self):
        rows = _ni_rows(10 * _M, 2 * _M, 9 * _M)
        enforce_identities(
            rows,
            "income_statement",
            [_D],
            None,
            "USD",
            derived=reported_derived,
            allowance={_D: {"net_income_continuing": 1 * _M}},
        )
        assert _by(rows, "total_pretax_income").values[_D] == 11 * _M

    def test_rounding_term_settled(self):
        rows = _ni_rows(10 * _M, 2 * _M, 9 * _M)
        rows[0].values[_D] = -1 * _M
        rows[0].tag = "total_cost_of_revenue"
        rows[0].parent = "total_gross_profit"
        rows[2].tag = "total_gross_profit"
        rows[1].parent = "total_gross_profit"
        enforce_identities(
            rows,
            "income_statement",
            [_D],
            None,
            "USD",
            derived=_never,
            allowance={_D: {"total_gross_profit": 20 * _M}},
        )
        assert rows[2].values[_D] == -3 * _M

    def test_fallback_needs_every_term(self):
        rows = [
            _rr(
                "total_revenue", {_D: 100 * _M}, parent="total_gross_profit", sequence=1
            ),
            _rr("x_cost", {}, parent="total_gross_profit", factor="-", sequence=2),
            _rr("total_gross_profit", {_D: 60 * _M}, sequence=3),
        ]
        enforce_identities(rows, "income_statement", [_D], None, "USD", derived=_never)
        assert _by(rows, "total_gross_profit").values[_D] == 60 * _M
        assert len(identity_diagnostics(rows, "income_statement", [_D])) == 1

    def test_fallback_solves_aligned_line(self):
        rows = _ni_rows(10 * _M, 2 * _M, 9 * _M)
        enforce_identities(
            rows, "income_statement", [_D], None, "USD", derived=lambda r, d: True
        )
        assert _by(rows, "total_pretax_income").values[_D] == 11 * _M

    def test_nonnegative_term_excluded(self):
        rows = [
            _rr(
                "total_revenue", {_D: 50 * _M}, parent="total_gross_profit", sequence=1
            ),
            _rr(
                "total_cost_of_revenue",
                {},
                parent="total_gross_profit",
                factor="-",
                sequence=2,
            ),
            _rr("total_gross_profit", {_D: 60 * _M}, sequence=3),
        ]
        enforce_identities(rows, "income_statement", [_D], None, "USD", derived=_never)
        assert _D not in _by(rows, "total_cost_of_revenue").values

    def test_unknown_statement(self):
        rows = _ni_rows(10.0, 2.0, 9.0)
        enforce_identities(rows, "other", [_D], None, "USD", derived=_never)
        assert identity_diagnostics(rows, "other", [_D]) == []


class TestImputeNoncontrollingInterest:
    def _rows(self, *, nci, temp=None, enci=110 * _M, equity=110 * _M):
        rows = [
            _rr(
                "total_liabilities",
                {_D: 100 * _M},
                parent="total_liabilities_and_equity",
                sequence=1,
                period_type="instant",
                sources={_D: "us-gaap:Liabilities"},
            ),
            _rr(
                "temporary_equity",
                {_D: temp} if temp else {},
                parent="total_liabilities_and_equity",
                sequence=2,
                period_type="instant",
                sources={_D: "imputed-rollup: r(+)"} if temp else {},
            ),
            _rr(
                "total_equity",
                {_D: equity},
                parent="total_equity_and_noncontrolling_interests",
                sequence=3,
                period_type="instant",
                sources={_D: "us-gaap:StockholdersEquity"},
            ),
            _rr(
                "noncontrolling_interests",
                {_D: nci},
                parent="total_equity_and_noncontrolling_interests",
                sequence=4,
                period_type="instant",
                sources={_D: "us-gaap:MinorityInterest"},
            ),
            _rr(
                "total_equity_and_noncontrolling_interests",
                {_D: enci},
                parent="total_liabilities_and_equity",
                sequence=5,
                period_type="instant",
                sources={
                    _D: "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
                },
            ),
            _rr(
                "total_liabilities_and_equity",
                {_D: 100 * _M + enci + (temp or 0)},
                sequence=6,
                period_type="instant",
                sources={_D: "us-gaap:LiabilitiesAndStockholdersEquity"},
            ),
        ]
        rows[3].date_factors[_D] = "0"
        return rows

    def test_reconciled_equity_restores_nci(self):
        rows, _ = impute(self._rows(nci=10 * _M), "balance_sheet", "industrial", {_D})
        assert _by(rows, "total_equity").values[_D] == 100 * _M
        assert _by(rows, "noncontrolling_interests").factor_on(_D) == "+"

    def test_nci_equal_to_temporary_equity_not_reconciled(self):
        rows, _ = impute(
            self._rows(nci=5 * _M, temp=5 * _M), "balance_sheet", "industrial", {_D}
        )
        assert _by(rows, "total_equity").values[_D] == 110 * _M


def _statement(statement, frequency, rows, dates):
    return StatementResult(
        statement=statement,
        company_type="industrial",
        frequency=frequency,
        currency="USD",
        dates=dates,
        rows=rows,
    )


class TestReconcileQuarterIdentities:
    def test_formula_quarters_take_formula_at_q4(self):
        q_src = {q: "us-gaap:R" for q in _Q}
        c_src = {q: "us-gaap:C" for q in _Q}
        g_src = {q: "imputed: total_revenue - total_cost_of_revenue" for q in _Q}
        annual = _statement(
            "income_statement",
            "annual",
            [
                _rr(
                    "total_revenue",
                    {_D: 400 * _M},
                    parent="total_gross_profit",
                    sequence=1,
                    sources={_D: "us-gaap:R"},
                ),
                _rr(
                    "total_cost_of_revenue",
                    {_D: 100 * _M},
                    parent="total_gross_profit",
                    factor="-",
                    sequence=2,
                    sources={_D: "us-gaap:Narrow"},
                ),
                _rr(
                    "total_gross_profit",
                    {_D: 300 * _M},
                    sequence=3,
                    sources={_D: "imputed: total_revenue - total_cost_of_revenue"},
                ),
            ],
            [_D],
        )
        quarterly = _statement(
            "income_statement",
            "quarterly",
            [
                _rr(
                    "total_revenue",
                    {q: 100 * _M for q in _Q},
                    parent="total_gross_profit",
                    sequence=1,
                    sources=q_src,
                ),
                _rr(
                    "total_cost_of_revenue",
                    {**{q: 60 * _M for q in _Q}, _D: 60 * _M},
                    parent="total_gross_profit",
                    factor="-",
                    sequence=2,
                    sources={**c_src, _D: "Q4: FY[us-gaap:C] - 9M[us-gaap:C]"},
                ),
                _rr(
                    "total_gross_profit",
                    {q: 40 * _M for q in _Q},
                    sequence=3,
                    sources=g_src,
                ),
            ],
            [*_Q, _D],
        )
        reconcile_fiscal_year_ends(
            quarterly,
            annual,
            {"total_revenue", "total_cost_of_revenue", "total_gross_profit"},
        )
        gp = _by(quarterly.rows, "total_gross_profit")
        assert gp.values[_D] == 40 * _M
        assert gp.sources[_D] == "imputed: total_revenue - total_cost_of_revenue"
        assert quarterly.diagnostics == []

    def test_restated_fy_term_solved_and_filed_q4_trusted(self):
        pretax_q, tax_q, ni_q = [10, 10, 10], [2, 2, 2], [8, 8, 8]
        facts = {
            "us-gaap": {
                "P": {
                    "units": {
                        "USD": [
                            {
                                "end": _D,
                                "start": "2023-01-01",
                                "val": 50 * _M,
                                "form": "10-K",
                                "filed": "2024-02-01",
                            },
                            {
                                "end": _D,
                                "start": "2023-01-01",
                                "val": 40 * _M,
                                "form": "10-K",
                                "filed": "2025-02-01",
                            },
                            *[
                                {
                                    "end": q,
                                    "start": s,
                                    "val": v * _M,
                                    "form": "10-Q",
                                    "filed": "2024-10-01",
                                }
                                for q, s, v in zip(_Q, _STARTS, pretax_q)
                            ],
                        ]
                    }
                },
                "T": {
                    "units": {
                        "USD": [
                            {
                                "end": _D,
                                "start": "2023-10-01",
                                "val": 4 * _M,
                                "form": "10-K",
                                "filed": "2024-02-01",
                            },
                        ]
                    }
                },
            }
        }

        def rows(pretax, tax, ni, src):
            return [
                _rr(
                    "total_pretax_income",
                    pretax,
                    parent="net_income_continuing",
                    sequence=1,
                    sources={d: "us-gaap:P" for d in pretax},
                ),
                _rr(
                    "income_tax_expense",
                    tax,
                    parent="net_income_continuing",
                    factor="-",
                    sequence=2,
                    sources={d: "us-gaap:T" for d in tax},
                ),
                _rr(
                    "net_income_continuing",
                    ni,
                    sequence=3,
                    sources={d: src for d in ni},
                ),
            ]

        annual = _statement(
            "income_statement",
            "annual",
            rows({_D: 40 * _M}, {_D: 10 * _M}, {_D: 30 * _M}, "us-gaap:N"),
            [_D],
        )
        quarterly = _statement(
            "income_statement",
            "quarterly",
            rows(
                {q: v * _M for q, v in zip(_Q, pretax_q)},
                {q: v * _M for q, v in zip(_Q, tax_q)},
                {q: v * _M for q, v in zip(_Q, ni_q)},
                "us-gaap:N",
            ),
            [*_Q, _D],
        )
        reconcile_fiscal_year_ends(
            quarterly,
            annual,
            {"total_pretax_income", "income_tax_expense", "net_income_continuing"},
            facts,
        )
        assert _by(quarterly.rows, "income_tax_expense").values[_D] == 4 * _M
        assert _by(quarterly.rows, "net_income_continuing").values[_D] == 6 * _M
        assert _by(quarterly.rows, "total_pretax_income").values[_D] == 10 * _M
        assert quarterly.diagnostics == []


def _fy_facts(annual, quarters, *, q_filed="2024-11-01"):
    return {
        "units": {
            "USD": [
                *[
                    {
                        "end": _D,
                        "start": "2023-01-01",
                        "val": v * _M,
                        "form": "10-K",
                        "filed": f,
                    }
                    for f, v in annual
                ],
                *[
                    {
                        "end": q,
                        "start": s,
                        "val": v * _M,
                        "form": "10-Q",
                        "filed": q_filed,
                    }
                    for q, s, v in zip(_Q, _STARTS, quarters)
                ],
            ]
        }
    }


def _gp_statements(
    annual_values, quarter_values, annual_sources, quarter_sources, q4=None
):
    tags = ("total_revenue", "total_cost_of_revenue", "total_gross_profit")
    parents = ("total_gross_profit", "total_gross_profit", None)
    factors = ("+", "-", "+")
    annual = _statement(
        "income_statement",
        "annual",
        [
            _rr(
                t,
                {_D: v * _M} if v is not None else {},
                parent=p,
                factor=f,
                sequence=i + 1,
                sources={_D: s} if v is not None else {},
            )
            for i, (t, p, f, v, s) in enumerate(
                zip(tags, parents, factors, annual_values, annual_sources)
            )
        ],
        [_D],
    )
    quarterly = _statement(
        "income_statement",
        "quarterly",
        [
            _rr(
                t,
                {
                    **({q: v * _M for q in _Q} if v is not None else {}),
                    **({_D: (q4 or {})[t] * _M} if t in (q4 or {}) else {}),
                },
                parent=p,
                factor=f,
                sequence=i + 1,
                sources={
                    **({q: s for q in _Q} if v is not None else {}),
                    **({_D: (q4 or {})[f"{t}:source"]} if t in (q4 or {}) else {}),
                },
            )
            for i, (t, p, f, v, s) in enumerate(
                zip(tags, parents, factors, quarter_values, quarter_sources)
            )
        ],
        [*_Q, _D],
    )
    return annual, quarterly, set(tags)


class TestReconcileQuarterEvidence:
    def test_vintage_repaired_term_trusted(self):
        facts = {
            "us-gaap": {
                "Revenues": _fy_facts(
                    [("2025-02-15", 531), ("2024-02-15", 800)], [200, 200, 200]
                ),
            }
        }
        facts["us-gaap"]["Revenues"]["units"]["USD"].append(
            {
                "end": _Q[2],
                "start": "2023-01-01",
                "val": 600 * _M,
                "form": "10-Q",
                "filed": "2023-11-01",
            }
        )
        annual, quarterly, tags = _gp_statements(
            (531, 300, 231),
            (200, 100, 100),
            ("us-gaap:Revenues", "abc:Cost", "us-gaap:GrossProfit"),
            ("us-gaap:Revenues", "abc:Cost2", "us-gaap:GrossProfit"),
        )
        reconcile_fiscal_year_ends(quarterly, annual, tags, facts)
        rows = {r.tag: r for r in quarterly.rows}
        assert rows["total_revenue"].values[_D] == 200 * _M
        assert "(filed 2024-02-15)" in rows["total_revenue"].sources[_D]
        assert quarterly.diagnostics == []

    def test_filed_quarter_fact_marks_contradicted_term(self):
        facts = {
            "us-gaap": {
                "T": {
                    "units": {
                        "USD": [
                            {
                                "end": _D,
                                "start": "2023-10-01",
                                "val": 4 * _M,
                                "form": "10-K",
                            }
                        ]
                    }
                }
            }
        }

        def rows(pretax, tax, ni):
            return [
                _rr(
                    "total_pretax_income",
                    pretax,
                    parent="net_income_continuing",
                    sequence=1,
                    sources={d: "us-gaap:P" for d in pretax},
                ),
                _rr(
                    "income_tax_expense",
                    tax,
                    parent="net_income_continuing",
                    factor="-",
                    sequence=2,
                    sources={d: "us-gaap:T" for d in tax},
                ),
                _rr(
                    "net_income_continuing",
                    ni,
                    sequence=3,
                    sources={d: "us-gaap:N" for d in ni},
                ),
            ]

        annual = _statement(
            "income_statement",
            "annual",
            rows({_D: 40 * _M}, {_D: 10 * _M}, {_D: 30 * _M}),
            [_D],
        )
        quarterly = _statement(
            "income_statement",
            "quarterly",
            rows(
                {**{q: 10 * _M for q in _Q}, _D: 10 * _M},
                {**{q: 2 * _M for q in _Q}, _D: 4 * _M},
                {**{q: 8 * _M for q in _Q}, _D: 5 * _M},
            ),
            [*_Q, _D],
        )
        reconcile_fiscal_year_ends(quarterly, annual, set(), facts)
        ni = _by(quarterly.rows, "net_income_continuing")
        assert ni.values[_D] == 6 * _M
        assert ni.sources[_D].startswith("identity-enforced")
        assert quarterly.diagnostics == []

    def test_restated_terms_dropped_when_unresolved(self):
        facts = {
            "us-gaap": {
                "R2": _fy_facts(
                    [("2025-02-15", 531), ("2024-02-15", 800)], [100, 100, 100]
                ),
                "GrossProfit": _fy_facts(
                    [("2025-02-15", 600), ("2024-02-15", 500)], [100, 100, 100]
                ),
            }
        }
        annual, quarterly, tags = _gp_statements(
            (531, -69, 600),
            (100, None, 100),
            ("us-gaap:R", "us-gaap:C", "us-gaap:GrossProfit"),
            ("us-gaap:R2", None, "us-gaap:GrossProfit"),
            q4={
                "total_revenue": 231,
                "total_revenue:source": "Q4: FY[us-gaap:R2] - (Q1+Q2+Q3)",
            },
        )
        reconcile_fiscal_year_ends(quarterly, annual, tags, facts)
        rows = {r.tag: r for r in quarterly.rows}
        assert _D not in rows["total_revenue"].values
        assert _D not in rows["total_gross_profit"].values
        assert quarterly.diagnostics == []

    def test_repaired_term_kept_when_identity_fails(self):
        facts = {
            "us-gaap": {
                "P": _fy_facts(
                    [("2025-02-15", 531), ("2024-02-15", 800)], [200, 200, 200]
                )
            }
        }
        facts["us-gaap"]["P"]["units"]["USD"].append(
            {
                "end": _Q[2],
                "start": "2023-01-01",
                "val": 600 * _M,
                "form": "10-Q",
                "filed": "2023-11-01",
            }
        )

        def rows(pretax, tax, ni):
            return [
                _rr(
                    "total_pretax_income",
                    pretax,
                    parent="net_income_continuing",
                    sequence=1,
                    sources={d: "us-gaap:P" for d in pretax},
                ),
                _rr(
                    "income_tax_expense",
                    tax,
                    parent="net_income_continuing",
                    factor="-",
                    sequence=2,
                    sources={d: "us-gaap:T" for d in tax},
                ),
                _rr(
                    "net_income_continuing",
                    ni,
                    sequence=3,
                    sources={d: "us-gaap:N" for d in ni},
                ),
            ]

        annual = _statement(
            "income_statement",
            "annual",
            rows({_D: 531 * _M}, {_D: 100 * _M}, {_D: 431 * _M}),
            [_D],
        )
        quarterly = _statement(
            "income_statement",
            "quarterly",
            rows(
                {q: 200 * _M for q in _Q},
                {q: 25 * _M for q in _Q},
                {q: 175 * _M for q in _Q},
            ),
            [*_Q, _D],
        )
        reconcile_fiscal_year_ends(
            quarterly,
            annual,
            {"total_pretax_income", "income_tax_expense", "net_income_continuing"},
            facts,
        )
        assert (
            _by(quarterly.rows, "total_pretax_income")
            .sources[_D]
            .startswith("identity-enforced")
        )
        assert quarterly.diagnostics == []

    def test_balance_sheet_fourth_quarter_terms(self):
        def rows(values):
            return [
                _rr(
                    "total_liabilities",
                    {d: 60 * _M for d in values},
                    parent="total_liabilities_and_equity",
                    sequence=1,
                    period_type="instant",
                    sources={d: "us-gaap:Liabilities" for d in values},
                ),
                _rr(
                    "temporary_equity",
                    {},
                    parent="total_liabilities_and_equity",
                    sequence=2,
                    period_type="instant",
                ),
                _rr(
                    "total_equity_and_noncontrolling_interests",
                    {d: 30 * _M for d in values},
                    parent="total_liabilities_and_equity",
                    sequence=3,
                    period_type="instant",
                    sources={d: "us-gaap:E" for d in values},
                ),
                _rr(
                    "total_liabilities_and_equity",
                    {d: 100 * _M for d in values},
                    sequence=4,
                    period_type="instant",
                    sources={d: "us-gaap:LE" for d in values},
                ),
            ]

        annual = _statement("balance_sheet", "annual", rows([_D]), [_D])
        quarterly = _statement("balance_sheet", "quarterly", rows(_Q), [*_Q, _D])
        reconcile_fiscal_year_ends(quarterly, annual, set())
        assert all(w.date != _D for w in quarterly.diagnostics)

    def test_quarter_only_value_is_derived(self):
        def rows(pretax, tax, ni):
            return [
                _rr(
                    "total_pretax_income",
                    pretax,
                    parent="net_income_continuing",
                    sequence=1,
                    sources={d: "us-gaap:P" for d in pretax},
                ),
                _rr(
                    "income_tax_expense",
                    tax,
                    parent="net_income_continuing",
                    factor="-",
                    sequence=2,
                    sources={d: "us-gaap:T" for d in tax},
                ),
                _rr(
                    "net_income_continuing",
                    ni,
                    sequence=3,
                    sources={d: "us-gaap:N" for d in ni},
                ),
            ]

        annual = _statement(
            "income_statement", "annual", rows({_D: 40 * _M}, {}, {_D: 30 * _M}), [_D]
        )
        quarterly = _statement(
            "income_statement",
            "quarterly",
            rows(
                {**{q: 10 * _M for q in _Q}, _D: 10 * _M},
                {**{q: 2 * _M for q in _Q}, _D: 4 * _M},
                {**{q: 8 * _M for q in _Q}, _D: 5 * _M},
            ),
            [*_Q, _D],
        )
        reconcile_fiscal_year_ends(quarterly, annual, set())
        assert quarterly.diagnostics == []
