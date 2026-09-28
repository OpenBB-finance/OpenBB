"""Imputation logic: multi-pass derivation, hierarchical articulation, and verification."""

# flake8: noqa: PLR0912

from __future__ import annotations

from datetime import datetime
from typing import Any

from openbb_sec.utils.statement_schema._detection import (
    detect_reporting_currency,
    prior_period_end,
)
from openbb_sec.utils.statement_schema._rules import (
    BS_IMPUTE,
    BS_VERIFY,
    CF_IMPUTE,
    CF_VERIFY,
    IS_IMPUTE,
    IS_IMPUTE_COMMON,
    IS_VERIFY,
    MAX_IMPUTE_PASSES,
    OTHER_LINES,
    PROMOTABLE_MEMOS,
    ROLLUP_REQUIRES,
)
from openbb_sec.utils.statement_schema._types import (
    CompanyType,
    Frequency,
    RowResult,
    StatementName,
    StatementResult,
    ValidationWarning,
    _tolerance,
)


def _format_impute_source(prefix: str, sources: list[tuple[str, int]]) -> str:
    """Build a human-readable source string for an imputation rule."""
    parts: list[str] = []

    for i, (src_tag, sign) in enumerate(sources):
        if i == 0:
            parts.append(f"{'-' if sign < 0 else ''}{src_tag}")
        else:
            parts.append(f"{'+' if sign > 0 else '-'} {src_tag}")

    return f"{prefix}: {' '.join(parts)}"


def _run_imputation_passes(
    rows: list[RowResult],
    rules: list[tuple[str, list[tuple[str, int]]]],
    tag_idx: dict[str, int],
    filing_dates: set[str],
) -> bool:
    """Run up to MAX_IMPUTE_PASSES imputation passes over all rules.

    Returns True if any value was derived across all passes.
    """
    any_changed = False
    parent_of = {r.tag: r.parent for r in rows}

    def is_ancestor(anc: str, tag: str) -> bool:
        seen: set[str] = set()
        p = parent_of.get(tag)

        while p and p not in seen:
            if p == anc:
                return True

            seen.add(p)
            p = parent_of.get(p)

        return False

    for _pass in range(MAX_IMPUTE_PASSES):
        changed = False

        for target_tag, sources in rules:
            target_i = tag_idx.get(target_tag)

            if target_i is None:
                continue

            target_row = rows[target_i]

            for date in filing_dates:
                if target_row.values.get(date) is not None:
                    continue

                val = 0.0
                all_present = True

                for src_tag, sign in sources:
                    src_i = tag_idx.get(src_tag)

                    if src_i is None:
                        all_present = False
                        break

                    src_val = rows[src_i].values.get(date)

                    if src_val is None or (
                        rows[src_i].sources.get(date, "").startswith("imputed-rollup")
                        and is_ancestor(src_tag, target_tag)
                    ):
                        all_present = False
                        break

                    val += src_val * sign

                if all_present:
                    target_row.values[date] = val
                    target_row.sources[date] = _format_impute_source("imputed", sources)
                    changed = True

        if not changed:
            break

        any_changed = True

    return any_changed


def _apply_hierarchical_articulation(
    rows: list[RowResult],
    filing_dates: set[str],
) -> None:
    """Roll up parents without a value and reconcile each reported parent with its children."""
    tag_to_row = {r.tag: r for r in rows}
    children_by_parent: dict[str, list[RowResult]] = {}
    memos_by_parent: dict[str, list[RowResult]] = {}
    depth_map: dict[str, int] = {}

    def get_depth(tag: str) -> int:
        if tag in depth_map:
            return depth_map[tag]
        row = tag_to_row.get(tag)
        if not row or not row.parent or row.parent not in tag_to_row:
            depth_map[tag] = 0
            return 0
        depth_map[tag] = 0
        d = 1 + get_depth(row.parent)
        depth_map[tag] = d
        return d

    for row in rows:
        get_depth(row.tag)

        if row.parent and row.parent in tag_to_row:
            if row.factor in ("+", "-"):
                children_by_parent.setdefault(row.parent, []).append(row)
            elif row.tag in PROMOTABLE_MEMOS:
                memos_by_parent.setdefault(row.parent, []).append(row)

    parents = list(children_by_parent.keys())
    parents.sort(key=get_depth, reverse=True)
    new_rows: list[RowResult] = []

    def sign(row: RowResult, date: str) -> float:
        return -1.0 if row.factor_on(date) == "-" else 1.0

    def ancestors(row: RowResult) -> set[str]:
        seen: set[str] = set()
        tag = row.parent

        while tag and tag not in seen and tag in tag_to_row:
            seen.add(tag)
            tag = tag_to_row[tag].parent

        return seen

    def other_line(parent_tag: str) -> RowResult | None:
        kids = children_by_parent.get(parent_tag, [])

        for line in OTHER_LINES.get(parent_tag, ()):
            for c in kids:
                if c.tag == line:
                    return c

        base = f"other_{parent_tag.removeprefix('total_')}"

        return next((c for c in kids if c.tag == base), None)

    def complete(row: RowResult, date: str) -> bool:
        if not row.sources.get(date, "").startswith("imputed-rollup"):
            return True

        line = other_line(row.tag)

        if line is None or line.values.get(date) is None:
            return False

        return not line.sources.get(date, "").startswith(("imputed", "Q4-derived"))

    def contained(
        candidates: list[tuple[RowResult, float]],
        date: str,
        gap: float,
        tolerance: float,
    ) -> list[tuple[RowResult, float]]:
        pool: list[tuple[RowResult, float]] = []

        def walk(row: RowResult, path_sign: float) -> None:
            value = row.values.get(date)

            if value is None or row.factor_on(date) not in ("+", "-"):
                return

            row_sign = path_sign * sign(row, date)
            source = row.sources.get(date, "")

            if (
                row.factor in ("+", "-")
                and abs(value) > tolerance
                and not source.startswith("imputed-plug")
            ):
                pool.append((row, row_sign * value))

            if source.startswith("imputed-rollup"):
                for child in children_by_parent.get(row.tag, []):
                    walk(child, row_sign)

        for row, path_sign in candidates:
            walk(row, path_sign)

        lineage = {id(r): ancestors(r) for r, _ in pool}
        singles = [(r, c) for r, c in pool if abs(gap + c) <= tolerance]

        if singles:
            deepest = max(singles, key=lambda rc: get_depth(rc[0].tag))

            if all(r is deepest[0] or r.tag in lineage[id(deepest[0])] for r, _ in singles):
                return [deepest]

            return []

        pairs = [
            (a, b)
            for i, a in enumerate(pool)
            for b in pool[i + 1 :]
            if a[0].tag not in lineage[id(b[0])]
            and b[0].tag not in lineage[id(a[0])]
            and abs(gap + a[1] + b[1]) <= tolerance
        ]

        return list(pairs[0]) if len(pairs) == 1 else []

    def presented(
        memos: list[RowResult], date: str, gap: float, tolerance: float
    ) -> RowResult | None:
        hits = [
            m
            for m in memos
            if m.factor_on(date) == "0"
            and m.values.get(date) is not None
            and abs(m.values[date]) > tolerance
            and abs(gap - m.values[date]) <= tolerance
        ]

        return hits[0] if len(hits) == 1 else None

    for _ in range(2 * len(parents) + 4):
        changed = False

        for parent_tag in parents:
            parent_row = tag_to_row[parent_tag]
            children = children_by_parent[parent_tag]
            memos = memos_by_parent.get(parent_tag, [])
            other_row = other_line(parent_tag)
            other_tag = (
                other_row.tag
                if other_row is not None
                else f"other_{parent_tag.removeprefix('total_')}"
            )
            required = ROLLUP_REQUIRES.get(parent_tag)
            required_children = [
                c for c in children if required is not None and c.tag in required
            ]
            own_plug = f"imputed-plug: {parent_tag} - "

            def absorbable(row: RowResult, date: str) -> bool:
                source = row.sources.get(date, "")

                if source.startswith(own_plug):  # noqa: B023
                    return True

                return source.startswith("imputed-rollup") and " + " in source

            for date in filing_dates:
                before = (
                    parent_row.values.get(date),
                    other_row.values.get(date) if other_row is not None else None,
                )

                if parent_row.sources.get(date, "").startswith("imputed-rollup"):
                    parent_row.values.pop(date, None)
                    parent_row.sources.pop(date, None)

                other_popped = False

                if other_row is not None and other_row.sources.get(date, "").startswith(
                    "imputed-plug"
                ):
                    other_row.values.pop(date, None)
                    other_row.sources.pop(date, None)
                    other_popped = True

                present = [
                    (c, c.values[date])
                    for c in children
                    if c is not other_row
                    and c.values.get(date) is not None
                    and c.factor_on(date) in ("+", "-")
                ] + [
                    (m, m.values[date])
                    for m in memos
                    if m.factor_on(date) == "+" and m.values.get(date) is not None
                ]
                other_val = (
                    other_row.values.get(date) if other_row is not None else None
                )
                other_sign = sign(other_row, date) if other_row is not None else 1.0
                explicit_sum = sum(sign(c, date) * v for c, v in present)
                detail = " + ".join(f"{c.tag}({c.factor_on(date)})" for c, _ in present)
                p_val = parent_row.values.get(date)

                if p_val is None:
                    if required is not None and not any(
                        c.values.get(date) is not None for c in required_children
                    ):
                        pass
                    elif other_val is not None and other_row is not None:
                        parent_row.values[date] = explicit_sum + other_val * other_sign
                        parent_row.sources[date] = "imputed-rollup: " + " + ".join(
                            [detail, f"{other_row.tag}({other_row.factor_on(date)})"]
                            if detail
                            else [f"{other_row.tag}({other_row.factor_on(date)})"]
                        )
                    elif present:
                        parent_row.values[date] = explicit_sum
                        parent_row.sources[date] = f"imputed-rollup: {detail}"
                elif present:
                    gap = p_val - explicit_sum
                    unexplained = gap - (other_val or 0.0) * other_sign
                    tolerance = _tolerance(p_val, explicit_sum)

                    if abs(unexplained) > tolerance:
                        candidates = [(c, 1.0) for c, _ in present]

                        if other_row is not None and other_row.sources.get(
                            date, ""
                        ).startswith("imputed-rollup"):
                            candidates += [
                                (g, other_sign)
                                for g in children_by_parent.get(other_row.tag, [])
                            ]

                        hits = contained(candidates, date, unexplained, tolerance)

                        if (
                            len(hits) == 1
                            and other_val is not None
                            and abs(other_val * other_sign - hits[0][1]) <= tolerance
                        ):
                            hits = []

                        if hits:
                            for hit, _ in hits:
                                hit.date_factors[date] = "0"
                            changed = True
                            continue

                        memo_hit = presented(memos, date, unexplained, tolerance)

                        if memo_hit is not None:
                            memo_hit.date_factors[date] = "+"
                            changed = True
                            continue

                        absorbers = [
                            c
                            for c, _ in present
                            if absorbable(c, date)
                            and (
                                c.sources.get(date, "").startswith(own_plug)
                                or not complete(c, date)
                            )
                        ]

                        if other_row is not None and (
                            other_popped
                            or (
                                other_val is not None
                                and absorbable(other_row, date)
                                and not complete(other_row, date)
                            )
                        ):
                            absorbers.append(other_row)

                        if len(absorbers) == 1 and absorbers[0] is not other_row:
                            absorber = absorbers[0]
                            absorber.values[date] += unexplained * sign(absorber, date)
                            absorber.sources[date] = own_plug + "(" + " + ".join(
                                f"{c.tag}({c.factor_on(date)})"
                                for c, _ in present
                                if c is not absorber
                            ) + ")"
                        elif other_row is not None or other_tag not in tag_to_row:
                            if other_row is None:
                                other_row = RowResult(
                                    tag=other_tag,
                                    label=f"Other {parent_row.label.removeprefix('Total ')}",
                                    description="Synthetic balancing plug derived from "
                                    + f"{parent_row.label} minus explicitly mapped children.",
                                    parent=parent_tag,
                                    sequence=parent_row.sequence - 0.01,
                                    factor="+",
                                    balance=parent_row.balance,
                                    unit=parent_row.unit,
                                    period_type=parent_row.period_type,
                                    values={},
                                    sources={},
                                )
                                tag_to_row[other_tag] = other_row
                                children.append(other_row)
                                new_rows.append(other_row)

                            other_row.values[date] = gap * sign(other_row, date)
                            other_row.sources[date] = f"{own_plug}({detail})"

                after = (
                    parent_row.values.get(date),
                    other_row.values.get(date) if other_row is not None else None,
                )

                if after != before:
                    changed = True

        if not changed:
            break

    if new_rows:
        rows.extend(new_rows)
        rows.sort(key=lambda r: float(r.sequence))


def _net_change_from_balances(
    rows: list[RowResult],
    filing_dates: set[str],
    frequency: Frequency,
) -> None:
    """Net change in cash from consecutive period-end cash balances where no net change is reported."""
    by_tag = {r.tag: r for r in rows}
    ncc = by_tag.get("net_change_in_cash")
    eop = by_tag.get("cash_at_end_of_period")

    if ncc is None or eop is None:
        return

    low, high = (330, 400) if frequency == "annual" else (80, 200)
    dates = sorted(filing_dates)

    for prev, date in zip(dates, dates[1:]):
        end, start = eop.values.get(date), eop.values.get(prev)

        if (
            ncc.values.get(date) is not None
            or end is None
            or start is None
            or eop.sources.get(date, "").removesuffix("(fallback)")
            != eop.sources.get(prev, "").removesuffix("(fallback)")
        ):
            continue

        days = (
            datetime.strptime(date, "%Y-%m-%d") - datetime.strptime(prev, "%Y-%m-%d")
        ).days

        if low <= days <= high:
            ncc.values[date] = end - start
            ncc.sources[date] = (
                f"imputed: cash_at_end_of_period - cash_at_end_of_period({prev})"
            )


def impute(
    rows: list[RowResult],
    statement: StatementName,
    company_type: CompanyType,
    filing_dates: set[str],
    facts: dict[str, Any] | None = None,
    frequency: Frequency = "annual",
    currency: str = "USD",
    *,
    get_rows_fn=None,
    get_annual_values_fn=None,
) -> tuple[list[RowResult], list[ValidationWarning]]:
    """Apply imputation rules to derive missing values, then validate.

    Parameters
    ----------
    get_rows_fn : callable, optional
        Function(statement, company_type) -> list[RowDef] for Q4 correction.
    get_annual_values_fn : callable, optional
        Function(facts, row_def, currency) -> dict for Q4 correction.
    """
    if statement == "income_statement":
        rules = IS_IMPUTE.get(company_type, []) + IS_IMPUTE_COMMON
    elif statement == "balance_sheet":
        rules = BS_IMPUTE
    elif statement == "cash_flow":
        rules = CF_IMPUTE
    else:
        return rows, []

    if not rules:
        return rows, []

    tag_idx: dict[str, int] = {r.tag: i for i, r in enumerate(rows)}

    if statement == "income_statement":
        _ptx_i = tag_idx.get("total_pretax_income")
        _beq_i = tag_idx.get("income_before_equity_method")
        _eqm_i = tag_idx.get("equity_method_investments")
        _nic_i = tag_idx.get("net_income_continuing")
        _tax_i = tag_idx.get("income_tax_expense")

        if _ptx_i is not None:
            _ptx = rows[_ptx_i]

            for _d in list(filing_dates):
                _s = _ptx.sources.get(_d, "")

                if "EquityMethodInvestments" not in _s:
                    continue
                if _beq_i is not None and _d not in rows[_beq_i].values:
                    rows[_beq_i].values[_d] = _ptx.values[_d]
                    rows[_beq_i].sources[_d] = _s
                _ni_v = rows[_nic_i].values.get(_d) if _nic_i is not None else None
                _tx_v = rows[_tax_i].values.get(_d) if _tax_i is not None else None
                _ni_src = rows[_nic_i].sources.get(_d, "") if _nic_i is not None else ""

                if (
                    _ni_v is not None
                    and _tx_v is not None
                    and abs(_ptx.values[_d] - _ni_v - _tx_v)
                    <= _tolerance(_ptx.values[_d], _ni_v, _tx_v)
                ):
                    continue
                if "ProfitLoss" in _ni_src and "FromContinuing" not in _ni_src:
                    del _ptx.values[_d]
                    del _ptx.sources[_d]
                    continue

                _eqv = rows[_eqm_i].values.get(_d) if _eqm_i is not None else None

                if _eqv is not None and _eqv != 0:
                    _ptx.values[_d] += _eqv
                    _ptx.sources[_d] = (
                        "corrected: income_before_equity_method"
                        " + equity_method_investments"
                    )
                else:
                    del _ptx.values[_d]
                    del _ptx.sources[_d]

    if statement == "income_statement":
        _nic_i = tag_idx.get("net_income_continuing")
        _disc_i = tag_idx.get("net_income_discontinued")
        _tax_i = tag_idx.get("income_tax_expense")

        if _nic_i is not None and _disc_i is not None:
            _nic = rows[_nic_i]
            _disc = rows[_disc_i]

            for _d in list(filing_dates):
                _s = _nic.sources.get(_d, "")

                if "ProfitLoss" not in _s:
                    continue
                if "ProfitLossFrom" in _s or "ProfitLossBefore" in _s:
                    continue
                if _tax_i is not None:
                    _tax_src = rows[_tax_i].sources.get(_d, "")

                    if _tax_src and "ContinuingOperations" not in _tax_src:
                        continue

                _dv = _disc.values.get(_d)

                if _dv is not None and _dv != 0:
                    _nic.values[_d] -= _dv
                    _nic.sources[_d] = _s + "(disc-adjusted)"

    if statement == "cash_flow":
        _net_change_from_balances(rows, filing_dates, frequency)

    _apply_hierarchical_articulation(rows, filing_dates)
    tag_idx = {r.tag: i for i, r in enumerate(rows)}

    if (
        frequency == "quarterly"
        and facts is not None
        and get_rows_fn is not None
        and get_annual_values_fn is not None
    ):
        rows_def = get_rows_fn(statement, company_type)
        row_def_by_tag = {rd.tag: rd for rd in rows_def}
        tag_to_row = {r.tag: r for r in rows}
        children_by_parent: dict[str, list[RowResult]] = {}
        for r in rows:
            if r.parent and r.factor in ("+", "-") and r.parent in tag_to_row:
                children_by_parent.setdefault(r.parent, []).append(r)

        for parent_tag, children in children_by_parent.items():
            parent_row = tag_to_row[parent_tag]
            parent_def = row_def_by_tag.get(parent_tag)
            if parent_def is None or parent_def.period_type != "duration":
                continue
            if parent_def.unit == "shares":
                continue
            annual_vals = get_annual_values_fn(facts, parent_def, currency)
            if not annual_vals:
                continue
            for fy_end, (fy_start, fy_val, fy_src) in annual_vals.items():
                p_src = parent_row.sources.get(fy_end, "")
                if "imputed-rollup" not in p_src:
                    continue
                q_dates = sorted(d for d in parent_row.values if fy_start < d < fy_end)
                if len(q_dates) != 3:
                    continue
                q_sum = sum(parent_row.values[d] for d in q_dates)
                q4_val = fy_val - q_sum
                if fy_val != 0 and q4_val * fy_val < 0:
                    continue
                q_srcs = [parent_row.sources.get(d, "") for d in q_dates]
                q_labels = "+".join(f"Q{i + 1}[{s}]" for i, s in enumerate(q_srcs))
                parent_row.values[fy_end] = q4_val
                parent_row.sources[fy_end] = f"Q4: FY[{fy_src}] \u2212 ({q_labels})"
                missing_children = []
                sibling_sum = 0.0
                for child in children:
                    if child.factor_on(fy_end) not in ("+", "-"):
                        continue
                    c_val = child.values.get(fy_end)
                    if c_val is None:
                        missing_children.append(child)
                    else:
                        sign = 1.0 if child.factor_on(fy_end) == "+" else -1.0
                        sibling_sum += c_val * sign
                if len(missing_children) == 1:
                    mc = missing_children[0]
                    mc_sign = 1.0 if mc.factor_on(fy_end) == "+" else -1.0
                    mc.values[fy_end] = (q4_val - sibling_sum) * mc_sign
                    mc.sources[fy_end] = f"Q4-derived: {parent_tag} \u2212 siblings"
        tag_idx = {r.tag: i for i, r in enumerate(rows)}

    _run_imputation_passes(rows, rules, tag_idx, filing_dates)

    if statement == "income_statement":
        gp_i = tag_idx.get("total_gross_profit")
        rev_i = tag_idx.get("total_revenue")
        cogs_i = tag_idx.get("total_cost_of_revenue")

        if gp_i is not None and rev_i is not None and cogs_i is not None:
            gp_row = rows[gp_i]
            rev_row = rows[rev_i]
            cogs_row = rows[cogs_i]
            gp_corrected = False

            for date in filing_dates:
                gp_src = gp_row.sources.get(date, "")
                cogs_val = cogs_row.values.get(date)
                rev_val = rev_row.values.get(date)

                if (
                    "imputed-rollup" in gp_src
                    and cogs_val is not None
                    and cogs_val != 0
                    and rev_val is not None
                ):
                    gp_row.values[date] = rev_val - cogs_val
                    gp_row.sources[date] = (
                        "imputed: total_revenue - total_cost_of_revenue"
                    )
                    gp_corrected = True

            if gp_corrected:
                _run_imputation_passes(rows, rules, tag_idx, filing_dates)

    if statement == "income_statement":
        cogs_i = tag_idx.get("total_cost_of_revenue")
        ce_i = tag_idx.get("costs_and_expenses")
        opex_i = tag_idx.get("total_operating_expenses")
        opinc_i = tag_idx.get("total_operating_income")
        rev_i = tag_idx.get("total_revenue")

        if all(i is not None for i in [cogs_i, ce_i, opex_i, opinc_i, rev_i]):
            cogs_row = rows[cogs_i]  # ty: ignore[invalid-argument-type]
            ce_row = rows[ce_i]  # ty: ignore[invalid-argument-type]
            opex_row = rows[opex_i]  # ty: ignore[invalid-argument-type]
            opinc_row = rows[opinc_i]  # ty: ignore[invalid-argument-type]
            rev_row = rows[rev_i]  # ty: ignore[invalid-argument-type]
            cogs_corrected = False

            for date in filing_dates:
                cogs_val = cogs_row.values.get(date)
                ce_val = ce_row.values.get(date)
                opex_val = opex_row.values.get(date)
                opinc_val = opinc_row.values.get(date)
                rev_val = rev_row.values.get(date)
                cogs_src = cogs_row.sources.get(date, "")

                if (
                    cogs_val is not None
                    and ce_val is not None
                    and opex_val is not None
                    and opinc_val is not None
                    and rev_val is not None
                    and "imputed" not in cogs_src
                    and "imputed" not in opex_row.sources.get(date, "")
                    and abs(ce_val - (rev_val - opinc_val))
                    <= _tolerance(ce_val, rev_val, opinc_val)
                    and (cogs_val + opex_val) < ce_val * 0.95
                ):
                    new_cogs = ce_val - opex_val
                    cogs_row.values[date] = new_cogs
                    cogs_row.sources[date] = (
                        "corrected: costs_and_expenses - total_operating_expenses"
                    )
                    cogs_corrected = True

            if cogs_corrected:
                gp_i2 = tag_idx.get("total_gross_profit")

                if gp_i2 is not None:
                    gp_row2 = rows[gp_i2]

                    for date in filing_dates:
                        rev_v = rev_row.values.get(date)
                        cogs_v = cogs_row.values.get(date)

                        if rev_v is not None and cogs_v is not None:
                            gp_row2.values[date] = rev_v - cogs_v
                            gp_row2.sources[date] = (
                                "imputed: total_revenue - total_cost_of_revenue"
                            )
                _run_imputation_passes(rows, rules, tag_idx, filing_dates)

    if statement == "income_statement":
        cogs_i = tag_idx.get("total_cost_of_revenue")
        gp_i = tag_idx.get("total_gross_profit")
        rev_i = tag_idx.get("total_revenue")

        if cogs_i is not None and gp_i is not None and rev_i is not None:
            cogs_row = rows[cogs_i]
            gp_row = rows[gp_i]
            rev_row = rows[rev_i]
            gp_corrected = False

            for date in filing_dates:
                gp_val = gp_row.values.get(date)
                rev_val = rev_row.values.get(date)
                cogs_val = cogs_row.values.get(date)
                gp_src = gp_row.sources.get(date, "")

                if (
                    gp_val is not None
                    and rev_val is not None
                    and cogs_val is not None
                    and "imputed" not in gp_src
                    and abs(rev_val - cogs_val - gp_val)
                    > _tolerance(rev_val - cogs_val, gp_val)
                ):
                    cogs_row.values[date] = rev_val - gp_val
                    cogs_row.sources[date] = (
                        "corrected: total_revenue - total_gross_profit"
                    )
                    gp_corrected = True

            if gp_corrected:
                _run_imputation_passes(rows, rules, tag_idx, filing_dates)

    if statement == "income_statement":
        opex_i = tag_idx.get("total_operating_expenses")
        gp_i = tag_idx.get("total_gross_profit")
        opinc_i = tag_idx.get("total_operating_income")

        if opex_i is not None and gp_i is not None and opinc_i is not None:
            opex_row = rows[opex_i]
            gp_row = rows[gp_i]
            opinc_row = rows[opinc_i]
            cleared = False

            for date in filing_dates:
                opex_val = opex_row.values.get(date)
                gp_val = gp_row.values.get(date)
                opinc_val = opinc_row.values.get(date)

                if opex_val is None or gp_val is None or opinc_val is None:
                    continue

                if (
                    opex_val > gp_val
                    or abs(gp_val - opex_val - opinc_val)
                    > _tolerance(gp_val - opex_val, opinc_val)
                    and "imputed" not in opinc_row.sources.get(date, "")
                ):
                    opex_row.values[date] = gp_val - opinc_val
                    opex_row.sources[date] = (
                        "corrected: total_gross_profit - total_operating_income"
                    )
                    cleared = True

            if cleared:
                _run_imputation_passes(rows, rules, tag_idx, filing_dates)

    if statement == "balance_sheet":
        enci_i = tag_idx.get("total_equity_and_noncontrolling_interests")
        ep_i = tag_idx.get("total_equity")
        nci_i = tag_idx.get("noncontrolling_interests")
        le_i = tag_idx.get("total_liabilities_and_equity")
        l_i = tag_idx.get("total_liabilities")
        rnci_i = tag_idx.get("redeemable_noncontrolling_interest")

        if all(i is not None for i in [enci_i, ep_i, nci_i, le_i, l_i]):
            for date in filing_dates:
                enci_v = rows[enci_i].values.get(date)  # ty: ignore[invalid-argument-type]
                ep_v = rows[ep_i].values.get(date)  # ty: ignore[invalid-argument-type]
                nci_v = rows[nci_i].values.get(date, 0)  # ty: ignore[invalid-argument-type]
                le_v = rows[le_i].values.get(date)  # ty: ignore[invalid-argument-type]
                l_v = rows[l_i].values.get(date)  # ty: ignore[invalid-argument-type]
                rnci_v = rows[rnci_i].values.get(date, 0) if rnci_i is not None else 0

                if any(v is None for v in [enci_v, ep_v, le_v, l_v]):
                    continue

                if abs(enci_v - ep_v - nci_v) <= _tolerance(enci_v, ep_v, nci_v):  # ty: ignore[unsupported-operator]
                    continue

                if abs(l_v + enci_v + rnci_v - le_v) > _tolerance(  # ty: ignore[unsupported-operator]
                    le_v, l_v, enci_v, rnci_v
                ):
                    continue

                rows[ep_i].values[date] = enci_v - nci_v  # ty: ignore[invalid-argument-type, unsupported-operator]
                rows[ep_i].sources[date] = (  # ty: ignore[invalid-argument-type]
                    "reconciled: total_equity_and_noncontrolling"
                    "_interests - noncontrolling_interests"
                )

    _apply_hierarchical_articulation(rows, filing_dates)
    tag_idx = {r.tag: i for i, r in enumerate(rows)}

    if statement == "income_statement":
        verify_rules = IS_VERIFY
    elif statement == "balance_sheet":
        verify_rules = BS_VERIFY
    elif statement == "cash_flow":
        verify_rules = CF_VERIFY
    else:  # pragma: no cover - an unknown statement already returned at the rules switch (line 244), so this branch is unreachable
        verify_rules = []

    _SRC_SOFT_MARKERS = (
        "imputed-rollup",
        "imputed-plug",
        "(fallback)",
    )
    _TGT_SOFT_MARKERS = _SRC_SOFT_MARKERS + ("imputed:",)

    def _is_target_soft(src: str) -> bool:
        return any(m in src for m in _TGT_SOFT_MARKERS)

    def _is_source_soft(src: str) -> bool:
        return any(m in src for m in _SRC_SOFT_MARKERS)

    diagnostics: list[ValidationWarning] = []
    verified_pairs: set[tuple[str, str]] = set()
    pending_diagnostics: dict[tuple[str, str], ValidationWarning] = {}

    _NCI_VALID_FORMS = (
        "10-K",
        "10-K/A",
        "10-Q",
        "10-Q/A",
        "20-F",
        "20-F/A",
        "40-F",
        "40-F/A",
        "6-K",
        "6-K/A",
    )

    for target_tag, sources in verify_rules:
        target_i = tag_idx.get(target_tag)

        if target_i is None:
            continue

        target_row = rows[target_i]

        for date in filing_dates:
            if (target_tag, date) in verified_pairs:
                continue

            if date not in target_row.values:
                continue

            nc_includes_fx: bool | None = True
            _cf_scope_mismatch = False

            if target_tag == "net_change_in_cash":
                nc_src = target_row.sources.get(date, "")
                has_fx_in_rule = any(
                    s == "effect_of_exchange_rate_changes" for s, _ in sources
                )
                if "ExcludingExchangeRateEffect" in nc_src:
                    nc_includes_fx = False
                elif "IncludingExchangeRateEffect" in nc_src:
                    nc_includes_fx = True
                else:
                    nc_includes_fx = None

                if nc_includes_fx is not None:
                    if not has_fx_in_rule and nc_includes_fx:
                        continue

                    if has_fx_in_rule and not nc_includes_fx:
                        continue

                for src_tag, _sign in sources:
                    if src_tag in (
                        "effect_of_exchange_rate_changes",
                        "other_net_changes_in_cash",
                    ):
                        continue

                    src_i = tag_idx.get(src_tag)

                    if src_i is not None:
                        src_src = rows[src_i].sources.get(date, "")

                        if "ContinuingOperations" in src_src:
                            _cf_scope_mismatch = True
                            break

            if (
                target_tag in ("total_pretax_income", "net_income_continuing")
                and statement == "income_statement"
            ):
                _nic_tag_i = tag_idx.get("net_income_continuing")
                _tax_tag_i = tag_idx.get("income_tax_expense")

                if _nic_tag_i is not None and _tax_tag_i is not None:
                    _nic_src = rows[_nic_tag_i].sources.get(date, "")
                    _tax_src = rows[_tax_tag_i].sources.get(date, "")
                    if (
                        "(disc-adjusted)" in _nic_src
                        and "ContinuingOperations" not in _tax_src
                    ):
                        _ptx_tag_i = tag_idx.get("total_pretax_income")

                        if _ptx_tag_i is not None:
                            _pv = rows[_ptx_tag_i].values.get(date)
                            _nv = rows[_nic_tag_i].values.get(date)
                            _tv = rows[_tax_tag_i].values.get(date)

                            if (
                                _pv is not None
                                and _nv is not None
                                and _tv is not None
                                and abs(_pv - _nv - _tv) > _tolerance(_pv, _nv, _tv)
                            ):
                                verified_pairs.add(("total_pretax_income", date))
                                verified_pairs.add(("net_income_continuing", date))
                                continue

            val = 0.0
            all_present = True

            for src_tag, sign in sources:
                src_i = tag_idx.get(src_tag)

                if src_i is None:
                    all_present = False
                    break

                src_val = rows[src_i].values.get(date)

                if src_val is None:
                    all_present = False
                    break

                val += src_val * sign

            if not all_present:
                continue

            diff = abs(val - target_row.values[date])
            _tol = _tolerance(val, target_row.values[date])

            if diff <= _tol:
                verified_pairs.add((target_tag, date))
                continue

            if (
                target_tag == "total_assets"
                and statement == "balance_sheet"
                and len(sources) == 1
                and sources[0][0] == "total_liabilities_and_equity"
            ):
                _le_src_i = tag_idx.get("total_liabilities_and_equity")

                if _le_src_i is not None:
                    _le_src_val = rows[_le_src_i].values.get(date)

                    if (
                        _le_src_val is not None
                        and _le_src_val < 0
                        and abs(target_row.values[date] + _le_src_val)
                        <= _tolerance(target_row.values[date], _le_src_val)
                    ):
                        rows[_le_src_i].values[date] = -_le_src_val
                        rows[_le_src_i].sources[date] = (
                            rows[_le_src_i].sources.get(date, "") + " (sign-corrected)"
                        )
                        verified_pairs.add((target_tag, date))
                        continue

            if (
                statement == "income_statement"
                and target_tag in ("total_pretax_income", "net_income_continuing")
                and facts is not None
            ):
                _nic_idx = tag_idx.get("net_income_continuing")

                if _nic_idx is not None:
                    _nic_src = rows[_nic_idx].sources.get(date, "")

                    def _pick_entries(
                        raw_entries: list[dict],
                        target_date: str,
                    ) -> list[tuple[str, float]]:
                        candidates: dict[str, float] = {}

                        for _e in raw_entries:
                            if (
                                _e.get("end") != target_date
                                or _e.get("form") not in _NCI_VALID_FORMS
                                or "start" not in _e
                            ):
                                continue

                            try:
                                _d = (
                                    datetime.strptime(target_date, "%Y-%m-%d")
                                    - datetime.strptime(_e["start"], "%Y-%m-%d")
                                ).days
                            except (ValueError, TypeError):
                                continue

                            if not (
                                (60 <= _d <= 135)
                                or (150 <= _d <= 200)
                                or (300 <= _d <= 400)
                            ):
                                continue

                            _f = _e.get("filed", "")

                            if _f not in candidates:
                                candidates[_f] = _e["val"]

                        return sorted(candidates.items(), key=lambda x: x[0])

                    def _try_nci_swap(
                        alt_val: float,
                        alt_tag_label: str,
                        *,
                        _date: str = date,
                        _nic_idx: int = _nic_idx,
                    ) -> bool:
                        """Test identity with alt NI and apply if passes."""
                        _tax_idx = tag_idx.get("income_tax_expense")
                        _ptx_idx = tag_idx.get("total_pretax_income")

                        if (
                            _tax_idx is None or _ptx_idx is None
                        ):  # pragma: no cover - income_tax_expense and total_pretax_income are present in every income-statement schema, and this swap is income-statement only
                            return False

                        _tv = rows[_tax_idx].values.get(_date)
                        _pv = rows[_ptx_idx].values.get(_date)

                        if (
                            _tv is None or _pv is None
                        ):  # pragma: no cover - defensive; the swap is only attempted once tax and pretax values are present for the date
                            return False

                        if abs(_pv - alt_val - _tv) <= _tolerance(_pv, alt_val, _tv):
                            rows[_nic_idx].values[_date] = alt_val
                            rows[_nic_idx].sources[_date] = alt_tag_label
                            verified_pairs.add(("total_pretax_income", _date))
                            verified_pairs.add(("net_income_continuing", _date))
                            return True

                        return False

                    if "ProfitLoss" in _nic_src and "ProfitLossFrom" not in _nic_src:
                        _nil_raw = (
                            facts.get("us-gaap", {})
                            .get("NetIncomeLoss", {})
                            .get("units", {})
                            .get("USD", [])
                        )
                        for _, _val in _pick_entries(_nil_raw, date):
                            if _try_nci_swap(
                                _val,
                                "us-gaap:NetIncomeLoss(NCI-corrected)",
                            ):
                                break

                    elif "NetIncomeLoss" in _nic_src:
                        _ptx_idx = tag_idx.get("total_pretax_income")
                        _ptx_src = (
                            rows[_ptx_idx].sources.get(date, "")
                            if _ptx_idx is not None
                            else ""
                        )
                        if "NoncontrollingInterest" in _ptx_src:
                            _pl_raw = (
                                facts.get("us-gaap", {})
                                .get("ProfitLoss", {})
                                .get("units", {})
                                .get("USD", [])
                            )
                            for _, _val in _pick_entries(_pl_raw, date):
                                if _try_nci_swap(
                                    _val,
                                    "us-gaap:ProfitLoss(NCI-corrected)",
                                ):
                                    break

                    if (target_tag, date) not in verified_pairs:
                        _nic_src_q4 = (
                            rows[_nic_idx].sources.get(date, "")
                            if _nic_idx is not None
                            else ""
                        )
                        if "Q4:" in _nic_src_q4:
                            for _alt_tag in ("NetIncomeLoss", "ProfitLoss"):
                                _alt_raw = (
                                    facts.get("us-gaap", {})
                                    .get(_alt_tag, {})
                                    .get("units", {})
                                    .get("USD", [])
                                )
                                _fy_val = None
                                _fy_best_filed = None
                                _fy_start_date = None

                                for _e in _alt_raw:
                                    if (
                                        _e.get("end") != date
                                        or "start" not in _e
                                        or _e.get("form") not in _NCI_VALID_FORMS
                                    ):
                                        continue

                                    try:
                                        _days = (
                                            datetime.strptime(date, "%Y-%m-%d")
                                            - datetime.strptime(_e["start"], "%Y-%m-%d")
                                        ).days
                                    except (ValueError, TypeError):
                                        continue

                                    if 300 <= _days <= 400:
                                        _ef = _e.get("filed", "")

                                        if (
                                            _fy_best_filed is None
                                            or _ef < _fy_best_filed
                                        ):
                                            _fy_best_filed = _ef
                                            _fy_val = _e["val"]
                                            _fy_start_date = _e["start"]

                                if _fy_val is None or _fy_start_date is None:
                                    continue

                                _q_by_end: dict[str, tuple[str, float]] = {}

                                for _e in _alt_raw:
                                    if (
                                        "start" not in _e
                                        or _e.get("form") not in _NCI_VALID_FORMS
                                    ):
                                        continue

                                    try:
                                        _qd = (
                                            datetime.strptime(_e["end"], "%Y-%m-%d")
                                            - datetime.strptime(_e["start"], "%Y-%m-%d")
                                        ).days
                                    except (ValueError, TypeError):
                                        continue

                                    if not 60 <= _qd <= 135:
                                        continue

                                    _e_end = _e["end"]

                                    if not _fy_start_date <= _e_end < date:
                                        continue

                                    _ef = _e.get("filed", "")

                                    if (
                                        _e_end not in _q_by_end
                                        or _ef < _q_by_end[_e_end][0]
                                    ):
                                        _q_by_end[_e_end] = (_ef, _e["val"])

                                if len(_q_by_end) == 3:
                                    _q4_alt = _fy_val - sum(
                                        v for _, v in _q_by_end.values()
                                    )

                                    if _nic_idx is not None and _try_nci_swap(
                                        _q4_alt,
                                        f"us-gaap:{_alt_tag}(Q4-NCI-corrected)",
                                    ):
                                        break

                    if (target_tag, date) in verified_pairs:
                        continue

            if (
                statement == "income_statement"
                and target_tag in ("total_pretax_income", "net_income_continuing")
                and (target_tag, date) not in verified_pairs
            ):
                _scope_formula = _format_impute_source("", sources).lstrip(": ")
                target_row.values[date] = val
                target_row.sources[date] = f"scope-aligned: {_scope_formula}"
                verified_pairs.add(("total_pretax_income", date))
                verified_pairs.add(("net_income_continuing", date))
                continue

            if target_tag == "net_change_in_cash":
                disc_i = tag_idx.get("net_cash_from_discontinued_operations")
                disc_val = rows[disc_i].values.get(date) if disc_i is not None else None
                _DISC_FX_TAGS = [
                    "EffectOfExchangeRateOnCashAndCashEquivalentsDiscontinuedOperations",
                    "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCash"
                    + "EquivalentsDisposalGroupIncludingDiscontinuedOperations",
                ]
                _disc_fx = 0.0

                if disc_val is not None and facts is not None:
                    _us = facts.get("us-gaap", {})

                    for _dft in _DISC_FX_TAGS:
                        for _e in _us.get(_dft, {}).get("units", {}).get("USD", []):
                            if _e.get("end") == date and "start" in _e:
                                try:
                                    _days = (
                                        datetime.strptime(date, "%Y-%m-%d")
                                        - datetime.strptime(_e["start"], "%Y-%m-%d")
                                    ).days
                                except (ValueError, TypeError):
                                    continue

                                if (60 <= _days <= 135) or (300 <= _days <= 400):
                                    _disc_fx = _e["val"]
                                    break

                        if _disc_fx != 0.0:
                            break

                if disc_val is not None:
                    adj_diff = abs(val + disc_val + _disc_fx - target_row.values[date])
                    if adj_diff <= _tolerance(
                        val, disc_val, _disc_fx, target_row.values[date]
                    ):
                        verified_pairs.add((target_tag, date))
                        continue
                    if _disc_fx != 0.0:
                        adj_diff = abs(val + disc_val - target_row.values[date])
                        if adj_diff <= _tolerance(
                            val, disc_val, target_row.values[date]
                        ):
                            verified_pairs.add((target_tag, date))
                            continue

                _DISC_INDIVIDUAL_TAGS = [
                    "CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations",
                    "CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations",
                    "CashProvidedByUsedInFinancingActivitiesDiscontinuedOperations",
                ]
                if facts is not None and (target_tag, date) not in verified_pairs:
                    _us_fb0b = facts.get("us-gaap", {})

                    for _dit in _DISC_INDIVIDUAL_TAGS:
                        for _e in (
                            _us_fb0b.get(_dit, {}).get("units", {}).get("USD", [])
                        ):
                            if _e.get("end") == date and "start" in _e:
                                try:
                                    _days = (
                                        datetime.strptime(date, "%Y-%m-%d")
                                        - datetime.strptime(_e["start"], "%Y-%m-%d")
                                    ).days
                                except (ValueError, TypeError):
                                    continue

                                if ((60 <= _days <= 135) or (300 <= _days <= 400)) and (
                                    abs(val + _e["val"] - target_row.values[date])
                                    <= _tolerance(
                                        val, _e["val"], target_row.values[date]
                                    )
                                ):
                                    verified_pairs.add((target_tag, date))
                                    break

                        if (target_tag, date) in verified_pairs:
                            break

                    if (target_tag, date) in verified_pairs:
                        continue

                if disc_val is None and facts is not None:
                    _DISC_OPS_TAGS = [
                        "CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations",
                        "CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations",
                        "CashProvidedByUsedInFinancingActivitiesDiscontinuedOperations",
                        "NetCashProvidedByUsedInDiscontinuedOperations",
                    ]
                    _DISC_OPS_IFRS = [
                        "CashFlowsFromUsedInOperatingActivitiesDiscontinuedOperations",
                        "CashFlowsFromUsedInInvestingActivitiesDiscontinuedOperations",
                        "CashFlowsFromUsedInFinancingActivitiesDiscontinuedOperations",
                    ]
                    _ccy = detect_reporting_currency(facts)
                    _disc_sum = 0.0
                    _disc_found = False

                    for _ns_key, _tags, _unit in (
                        ("us-gaap", _DISC_OPS_TAGS, "USD"),
                        ("ifrs-full", _DISC_OPS_IFRS, _ccy),
                    ):
                        _ns = facts.get(_ns_key, {})

                        for _dt in _tags:
                            _entries = _ns.get(_dt, {}).get("units", {}).get(_unit, [])
                            for _e in _entries:
                                if _e.get("end") == date and "start" in _e:
                                    try:
                                        _days = (
                                            datetime.strptime(date, "%Y-%m-%d")
                                            - datetime.strptime(_e["start"], "%Y-%m-%d")
                                        ).days
                                    except (ValueError, TypeError):
                                        continue

                                    if (60 <= _days <= 135) or (300 <= _days <= 400):
                                        _disc_sum += _e["val"]
                                        _disc_found = True
                                        break

                        if _disc_found:
                            break

                    if _disc_found:
                        _disc_fx_fb1 = 0.0

                        for _dft in _DISC_FX_TAGS:
                            for _e in _ns.get(_dft, {}).get("units", {}).get(_unit, []):
                                if _e.get("end") == date and "start" in _e:
                                    try:
                                        _days = (
                                            datetime.strptime(date, "%Y-%m-%d")
                                            - datetime.strptime(_e["start"], "%Y-%m-%d")
                                        ).days
                                    except (ValueError, TypeError):
                                        continue

                                    if (60 <= _days <= 135) or (300 <= _days <= 400):
                                        _disc_fx_fb1 = _e["val"]
                                        break

                            if _disc_fx_fb1 != 0.0:
                                break

                        adj_diff = abs(
                            val + _disc_sum + _disc_fx_fb1 - target_row.values[date]
                        )

                        if adj_diff <= _tolerance(
                            val, _disc_sum, _disc_fx_fb1, target_row.values[date]
                        ):
                            verified_pairs.add((target_tag, date))
                            continue

                if disc_val is None and facts is not None:
                    _disposal_tags = [
                        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"
                        "PeriodIncreaseDecreaseIncludingExchangeRateEffect"
                        "DisposalGroupIncludingDiscontinuedOperations",
                        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"
                        "PeriodIncreaseDecreaseExcludingExchangeRateEffect"
                        "DisposalGroupIncludingDiscontinuedOperations",
                        "CashAndCashEquivalentsPeriodIncreaseDecrease"
                        "DisposalGroupIncludingDiscontinuedOperations",
                    ]
                    _us = facts.get("us-gaap", {})

                    for _dt in _disposal_tags:
                        _entries = _us.get(_dt, {}).get("units", {}).get("USD", [])

                        for _e in _entries:
                            if (
                                _e.get("end") == date
                                and _e.get("form") in ("10-K", "10-Q", "20-F", "40-F")
                                and "start" in _e
                            ):
                                _start = _e["start"]

                                try:
                                    _days = (
                                        datetime.strptime(date, "%Y-%m-%d")
                                        - datetime.strptime(_start, "%Y-%m-%d")
                                    ).days
                                except (ValueError, TypeError):
                                    continue

                                if (60 <= _days <= 135) or (300 <= _days <= 400):
                                    _disposal_nc = _e["val"]
                                    _derived_disc = (
                                        target_row.values[date] - _disposal_nc
                                    )
                                    adj_diff = abs(
                                        val + _derived_disc - target_row.values[date]
                                    )

                                    if adj_diff <= _tolerance(
                                        val, _derived_disc, target_row.values[date]
                                    ):
                                        verified_pairs.add((target_tag, date))
                                        break
                        else:
                            continue

                        break

                    if (target_tag, date) in verified_pairs:
                        continue

                if (
                    facts is not None
                    and disc_val is None
                    and (target_tag, date) not in verified_pairs
                ):
                    _DISP_CASH_TAGS = [
                        "DisposalGroupIncludingDiscontinuedOperationCashAndCashEquivalents",
                        "DisposalGroupIncludingDiscontinuedOperationCash",
                    ]
                    _us = facts.get("us-gaap", {})
                    _disp_end = None

                    for _dct in _DISP_CASH_TAGS:
                        for _e in _us.get(_dct, {}).get("units", {}).get("USD", []):
                            if _e.get("end") == date and "start" not in _e:
                                _disp_end = _e["val"]
                                break

                        if _disp_end is not None:
                            break

                    if _disp_end is not None:
                        _disp_start = 0.0
                        _prior = prior_period_end(date)

                        if _prior:
                            for _dct in _DISP_CASH_TAGS:
                                for _e in (
                                    _us.get(_dct, {}).get("units", {}).get("USD", [])
                                ):
                                    if _e.get("end") == _prior and "start" not in _e:
                                        _disp_start = _e["val"]
                                        break

                                if _disp_start != 0.0:
                                    break

                        _disp_delta = _disp_end - _disp_start

                        if abs(_disp_delta) > 0:
                            adj_diff = abs(val - _disp_delta - target_row.values[date])

                            if adj_diff <= _tolerance(
                                val, _disp_delta, target_row.values[date]
                            ):
                                verified_pairs.add((target_tag, date))
                                continue

                if facts is not None and (target_tag, date) not in verified_pairs:
                    _RESTRICTED_TAGS = [
                        "IncreaseDecreaseInRestrictedCashAndRestrictedCashEquivalents",
                        "IncreaseDecreaseInRestrictedCash",
                        "IncreaseDecreaseInRestrictedCashAndInvestments",
                    ]
                    _us = facts.get("us-gaap", {})

                    for _rt in _RESTRICTED_TAGS:
                        _entries = _us.get(_rt, {}).get("units", {}).get("USD", [])

                        for _e in _entries:
                            if _e.get("end") == date and "start" in _e:
                                try:
                                    _days = (
                                        datetime.strptime(date, "%Y-%m-%d")
                                        - datetime.strptime(_e["start"], "%Y-%m-%d")
                                    ).days
                                except (ValueError, TypeError):
                                    continue

                                if (60 <= _days <= 135) or (300 <= _days <= 400):
                                    adj_diff = abs(
                                        val + _e["val"] - target_row.values[date]
                                    )

                                    if adj_diff <= _tolerance(
                                        val, _e["val"], target_row.values[date]
                                    ):
                                        verified_pairs.add((target_tag, date))
                                        break

                        if (target_tag, date) in verified_pairs:
                            break

                    if (target_tag, date) in verified_pairs:
                        continue

                if facts is not None and (target_tag, date) not in verified_pairs:
                    _ACTIVITY_PAIRS = [
                        (
                            "NetCashProvidedByUsedInOperatingActivities",
                            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
                        ),
                        (
                            "NetCashProvidedByUsedInInvestingActivities",
                            "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
                        ),
                        (
                            "NetCashProvidedByUsedInFinancingActivities",
                            "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
                        ),
                    ]
                    _FX_ALT = [
                        "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
                        "EffectOfExchangeRateOnCashAndCashEquivalents",
                        "EffectOfExchangeRateOnCashAndCashEquivalentsContinuingOperations",
                    ]
                    _NC_ALT = [
                        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriod"
                        + "IncreaseDecreaseIncludingExchangeRateEffect",
                        "CashAndCashEquivalentsPeriodIncreaseDecrease",
                        "CashAndCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect",
                    ]
                    _IFRS_ACTIVITY_PAIRS = [
                        (
                            "CashFlowsFromUsedInOperatingActivities",
                            "CashFlowsFromUsedInOperatingActivitiesContinuingOperations",
                        ),
                        (
                            "CashFlowsFromUsedInInvestingActivities",
                            "CashFlowsFromUsedInInvestingActivitiesContinuingOperations",
                        ),
                        (
                            "CashFlowsFromUsedInFinancingActivities",
                            "CashFlowsFromUsedInFinancingActivitiesContinuingOperations",
                        ),
                    ]
                    _IFRS_FX_ALT = [
                        "EffectOfExchangeRateChangesOnCashAndCashEquivalents",
                    ]
                    _IFRS_NC_ALT = [
                        "IncreaseDecreaseInCashAndCashEquivalents",
                    ]
                    _us = facts.get("us-gaap", {})
                    _ifrs = facts.get("ifrs-full", {})
                    _ccy = detect_reporting_currency(facts)

                    def _cf_vals(
                        tag_name: str, ns: dict, unit: str, *, _date: str = date
                    ) -> set:
                        out: set = set()
                        for _e in ns.get(tag_name, {}).get("units", {}).get(unit, []):
                            if _e.get("end") == _date and "start" in _e:
                                try:
                                    _d = (
                                        datetime.strptime(_date, "%Y-%m-%d")
                                        - datetime.strptime(_e["start"], "%Y-%m-%d")
                                    ).days
                                except (ValueError, TypeError):
                                    continue
                                if (60 <= _d <= 135) or (300 <= _d <= 400):
                                    out.add(_e["val"])
                        return out

                    _act_opts = []

                    for _tot, _cont in _ACTIVITY_PAIRS:
                        _act_opts.append(
                            _cf_vals(_tot, _us, "USD") | _cf_vals(_cont, _us, "USD")
                        )

                    for idx, (_tot, _cont) in enumerate(_IFRS_ACTIVITY_PAIRS):
                        _act_opts[idx] |= _cf_vals(_tot, _ifrs, _ccy) | _cf_vals(
                            _cont, _ifrs, _ccy
                        )

                    _fx_opts = {0.0}

                    for _ft in _FX_ALT:
                        _fx_opts |= _cf_vals(_ft, _us, "USD")

                    for _ft in _IFRS_FX_ALT:
                        _fx_opts |= _cf_vals(_ft, _ifrs, _ccy)

                    _disc_fx_vals: set = set()

                    for _dft in _DISC_FX_TAGS:
                        _disc_fx_vals |= _cf_vals(_dft, _us, "USD")

                    if _disc_fx_vals:
                        for _fv in list(_fx_opts):
                            for _dfv in _disc_fx_vals:
                                _fx_opts.add(_fv + _dfv)

                    _nc_opts: set = set()

                    for _nt in _NC_ALT:
                        _nc_opts |= _cf_vals(_nt, _us, "USD")

                    for _nt in _IFRS_NC_ALT:
                        _nc_opts |= _cf_vals(_nt, _ifrs, _ccy)

                    if (
                        all(_act_opts)
                        and _nc_opts
                        and any(
                            abs(_o + _i + _f + _fx - _nc)
                            <= _tolerance(_o, _i, _f, _fx, _nc)
                            for _o in _act_opts[0]
                            for _i in _act_opts[1]
                            for _f in _act_opts[2]
                            for _fx in _fx_opts
                            for _nc in _nc_opts
                        )
                    ):
                        verified_pairs.add((target_tag, date))
                        continue

                if facts is not None and (target_tag, date) not in verified_pairs:
                    _us = facts.get("us-gaap", {})
                    _ifrs = facts.get("ifrs-full", {})
                    _ccy = detect_reporting_currency(facts)
                    _nc_val = target_row.values.get(date)
                    _CASH_BAL_TAGS = [
                        (
                            "us-gaap",
                            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
                            "USD",
                        ),
                        ("us-gaap", "CashAndCashEquivalentsAtCarryingValue", "USD"),
                        ("us-gaap", "Cash", "USD"),
                        ("ifrs-full", "CashAndCashEquivalents", _ccy),
                    ]

                    for _ns_key, _cbt, _unit in _CASH_BAL_TAGS:
                        _ns = _ifrs if _ns_key == "ifrs-full" else _us
                        _entries = _ns.get(_cbt, {}).get("units", {}).get(_unit, [])
                        _end_vals: set = set()
                        _start_vals: set = set()

                        for _e in _entries:
                            if "start" in _e:
                                continue

                            _edate = _e.get("end", "")

                            if _edate == date:
                                _end_vals.add(_e["val"])
                            elif _edate:
                                try:
                                    _dd = (
                                        datetime.strptime(date, "%Y-%m-%d")
                                        - datetime.strptime(_edate, "%Y-%m-%d")
                                    ).days
                                except (ValueError, TypeError):
                                    continue

                                if 60 <= _dd <= 400:
                                    _start_vals.add(_e["val"])

                        if (
                            _end_vals
                            and _start_vals
                            and _nc_val is not None
                            and any(
                                abs((ev - sv) - _nc_val) <= _tolerance(ev, sv, _nc_val)
                                for ev in _end_vals
                                for sv in _start_vals
                            )
                        ):
                            verified_pairs.add((target_tag, date))
                            break

                    if (target_tag, date) in verified_pairs:
                        continue

            if (
                target_tag == "total_liabilities"
                and facts is not None
                and (target_tag, date) not in verified_pairs
                and diff > 0
            ):
                _MEZZ_TAGS = (
                    "RedeemableNoncontrollingInterestEquityCarryingAmount",
                    "RedeemableNoncontrollingInterestEquityCommonCarryingAmount",
                    "RedeemableNoncontrollingInterestEquityPreferredCarryingAmount",
                    "RedeemablePreferredStockCarryingAmountOrRedemptionValue",
                    "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests",
                    "TemporaryEquityCarryingAmountAttributableToParent",
                    "TemporaryEquityCarryingAmountAttributableToNoncontrollingInterest",
                    "TemporaryEquityCarryingAmount",
                )
                _us = facts.get("us-gaap", {})
                _mezz_total = 0.0

                for _mt in _MEZZ_TAGS:
                    _entries = _us.get(_mt, {}).get("units", {}).get("USD", [])

                    for _e in _entries:
                        if _e.get("end") == date and "start" not in _e:
                            _mezz_total += _e["val"]
                            break

                _le_i = tag_idx.get("total_liabilities_and_equity")
                _enci_i = tag_idx.get("total_equity_and_noncontrolling_interests")
                _le_v = rows[_le_i].values.get(date) if _le_i is not None else None
                _enci_v = (
                    rows[_enci_i].values.get(date) if _enci_i is not None else None
                )
                _l_v = target_row.values.get(date)

                if _le_v is not None and _enci_v is not None and _l_v is not None:
                    _total_mezz_computed = _le_v - _l_v - _enci_v

                    if _total_mezz_computed > 0:
                        verified_pairs.add((target_tag, date))
                        continue

                    if abs(_total_mezz_computed) <= _tolerance(_le_v, _l_v, _enci_v):
                        verified_pairs.add((target_tag, date))
                        continue

                    _rnci_i2 = tag_idx.get("redeemable_noncontrolling_interest")
                    if _rnci_i2 is not None:
                        _rnci_src2 = rows[_rnci_i2].sources.get(date, "")
                        if "imputed" in _rnci_src2:
                            rows[_rnci_i2].values[date] = _total_mezz_computed
                            rows[_rnci_i2].sources[date] = _rnci_src2 + " (re-imputed)"
                            verified_pairs.add((target_tag, date))
                            continue

            if (
                target_tag
                in (
                    "total_equity_and_noncontrolling_interests",
                    "total_equity",
                )
                and facts is not None
                and (target_tag, date) not in verified_pairs
            ):
                _rnci_i = tag_idx.get("redeemable_noncontrolling_interest")
                _rnci_val = (
                    rows[_rnci_i].values.get(date, 0) if _rnci_i is not None else 0
                )
                if abs(_rnci_val) > 0 or diff > _tolerance(diff, _rnci_val):
                    _MEZZ_TAGS_EQ = (
                        "RedeemableNoncontrollingInterestEquityCarryingAmount",
                        "RedeemableNoncontrollingInterestEquityCommonCarryingAmount",
                        "RedeemableNoncontrollingInterestEquityPreferredCarryingAmount",
                        "TemporaryEquityCarryingAmountAttributableToParent",
                        "TemporaryEquityCarryingAmountAttributableToNoncontrollingInterest",
                        "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests",
                        "TemporaryEquityCarryingAmount",
                        "RedeemablePreferredStockCarryingAmountOrRedemptionValue",
                        "PreferredStockValue",
                    )
                    _us = facts.get("us-gaap", {})
                    _eq_resolved = False
                    _mezz_sum = 0.0

                    for _mt in _MEZZ_TAGS_EQ:
                        _entries = _us.get(_mt, {}).get("units", {}).get("USD", [])

                        for _e in _entries:
                            if _e.get("end") == date and "start" not in _e:
                                if abs(diff - _e["val"]) <= _tolerance(diff, _e["val"]):
                                    _eq_resolved = True
                                _mezz_sum += _e["val"]
                                break

                        if _eq_resolved:
                            break

                    if not _eq_resolved and abs(diff - _mezz_sum) <= _tolerance(
                        diff, _mezz_sum
                    ):
                        _eq_resolved = True

                    if _eq_resolved:
                        verified_pairs.add((target_tag, date))
                        continue

                _nci_i = tag_idx.get("noncontrolling_interests")
                _nci_val = rows[_nci_i].values.get(date) if _nci_i is not None else None

                if (
                    _nci_val is not None
                    and _nci_val < 0
                    and abs(diff - 2 * abs(_nci_val)) <= _tolerance(diff, _nci_val)
                ):
                    verified_pairs.add((target_tag, date))
                    continue

            if (
                target_tag == "total_operating_income"
                and statement == "income_statement"
                and facts is not None
                and (target_tag, date) not in verified_pairs
            ):
                _signed_gap = target_row.values[date] - val
                _us = facts.get("us-gaap", {})
                _OTHER_OP_TAGS = (
                    "GainLossOnDispositionOfAssets",
                    "GainLossOnSaleOfPropertyPlantEquipment",
                    "GainLossOnDispositionOfProperty",
                    "OtherOperatingIncomeExpenseNet",
                )
                _oi_bridge_resolved = False

                for _ot in _OTHER_OP_TAGS:
                    _entries = _us.get(_ot, {}).get("units", {}).get("USD", [])

                    for _e in _entries:
                        if (
                            _e.get("end") == date
                            and "start" in _e
                            and _e["val"] != 0
                            and abs(_signed_gap - _e["val"])
                            <= _tolerance(_signed_gap, _e["val"])
                        ):
                            _oi_bridge_resolved = True
                            break

                    if _oi_bridge_resolved:
                        break

                if not _oi_bridge_resolved:
                    _gp_i = tag_idx.get("total_gross_profit")
                    _opex_i = tag_idx.get("total_operating_expenses")
                    _opinc_i = tag_idx.get("total_operating_income")
                    _vals = []
                    for _idx in (_gp_i, _opex_i, _opinc_i):
                        if _idx is not None:
                            _v = rows[_idx].values.get(date)
                            if _v is not None:
                                _vals.append(abs(int(_v)))
                    if (
                        len(_vals) == 3
                        and all(v % 1_000_000 == 0 for v in _vals)
                        and diff <= 1_000_000
                    ):
                        _oi_bridge_resolved = True

                if _oi_bridge_resolved:
                    verified_pairs.add((target_tag, date))
                    continue

            target_src = target_row.sources.get(date, "")
            _formula = _format_impute_source("", sources).lstrip(": ")
            _ambiguous_cf = (
                target_tag == "net_change_in_cash" and nc_includes_fx is None  # noqa: F821
            )
            _skip_enforce = _ambiguous_cf or _cf_scope_mismatch

            if _is_target_soft(target_src) and not _skip_enforce:
                target_row.values[date] = val
                target_row.sources[date] = (
                    f"identity-enforced: {_formula} [solving {target_tag}]"
                )
                verified_pairs.add((target_tag, date))
                continue

            if not _skip_enforce:
                soft_src_tags = []

                for src_tag, _sign in sources:
                    src_i = tag_idx.get(src_tag)

                    if src_i is not None:
                        src_src = rows[src_i].sources.get(date, "")
                        if _is_source_soft(src_src):
                            soft_src_tags.append((src_tag, _sign))

                if len(soft_src_tags) == 1:
                    fix_tag, fix_sign = soft_src_tags[0]
                    fix_i = tag_idx[fix_tag]
                    other_sum = 0.0

                    for src_tag, sign in sources:
                        if src_tag == fix_tag:
                            continue
                        other_sum += rows[tag_idx[src_tag]].values[date] * sign

                    rows[fix_i].values[date] = (
                        target_row.values[date] - other_sum
                    ) / fix_sign
                    rows[fix_i].sources[date] = (
                        f"identity-enforced: derived from {target_tag}"
                        f" [solving {fix_tag}]"
                    )
                    verified_pairs.add((target_tag, date))
                    continue

            if (
                target_tag == "net_change_in_cash"
                and (target_tag, date) not in verified_pairs
            ):
                _DERIVED_MARKERS = (
                    "ytd_derived",
                    "Q4:",
                    "H2:",
                    "q4_h2_derived",
                )
                _nc_is_derived = any(m in target_src for m in _DERIVED_MARKERS)
                _any_src_derived = False

                if not _nc_is_derived:
                    for _st, _ in sources:
                        _si = tag_idx.get(_st)

                        if _si is not None:
                            _ss = rows[_si].sources.get(date, "")

                            if any(m in _ss for m in _DERIVED_MARKERS):
                                _any_src_derived = True
                                break

                if _nc_is_derived or _any_src_derived:
                    if _cf_scope_mismatch:
                        target_row.values[date] = val
                        target_row.sources[date] = (
                            f"scope-aligned: {_formula} [solving {target_tag}]"
                        )
                    else:
                        target_row.values[date] = val
                        target_row.sources[date] = (
                            f"identity-enforced: {_formula} [solving {target_tag}]"
                        )
                    verified_pairs.add((target_tag, date))
                    continue

            if _ambiguous_cf:
                _new_warning = ValidationWarning(
                    date=date,
                    tag=target_tag,
                    expected=val,
                    actual=target_row.values[date],
                    formula=_formula,
                    identity=f"{target_tag} = {_formula}",
                )
                _existing = pending_diagnostics.get((target_tag, date))
                if _existing is not None:
                    if diff < abs(_existing.actual - _existing.expected):
                        pending_diagnostics[(target_tag, date)] = (
                            _new_warning  # pragma: no cover - diagnostic refinement; needs the same target+date to resolve ambiguously twice with a strictly smaller discrepancy on the later pass
                        )
                else:
                    pending_diagnostics[(target_tag, date)] = _new_warning
                continue

            if _cf_scope_mismatch:
                target_row.values[date] = val
                target_row.sources[date] = (
                    f"scope-aligned: {_formula} [solving {target_tag}]"
                )
                verified_pairs.add((target_tag, date))
                continue

            if (
                facts is not None
                and ":" in target_src
                and "identity-enforced" not in target_src
                and "imputed" not in target_src
            ):
                _parts = target_src.split(":")
                _tgt_ns = _parts[0]
                _tgt_xbrl = _parts[1].split()[0]
                _ns_facts = facts.get(_tgt_ns, {})
                _tgt_entries = _ns_facts.get(_tgt_xbrl, {}).get("units", {})
                _vintage_match = False
                for _unit_entries in _tgt_entries.values():
                    for _e in _unit_entries:
                        if (
                            _e.get("end") == date
                            and "start" not in _e
                            and abs(_e["val"] - val) <= _tolerance(val, _e["val"])
                        ):
                            _vintage_match = True
                            break
                    if _vintage_match:
                        break
                if _vintage_match:
                    target_row.values[date] = val
                    target_row.sources[date] = target_src + " (vintage-corrected)"
                    verified_pairs.add((target_tag, date))
                    continue

            _any_src_soft = any(
                _is_source_soft(rows[tag_idx[st]].sources.get(date, ""))
                for st, _ in sources
                if tag_idx.get(st) is not None
            )
            if not _any_src_soft:
                diagnostics.append(
                    ValidationWarning(
                        date=date,
                        tag=target_tag,
                        expected=val,
                        actual=target_row.values[date],
                        formula=_formula,
                        identity=f"{target_tag} = {_formula}",
                    )
                )
            else:
                target_row.values[date] = val
                target_row.sources[date] = (
                    f"identity-enforced: {_formula} [solving {target_tag}]"
                )
            verified_pairs.add((target_tag, date))
            continue

    for key, warning in pending_diagnostics.items():
        if key not in verified_pairs:
            _tag, _date = key
            _ti = tag_idx.get(_tag)
            if _ti is not None:
                rows[_ti].values[_date] = warning.expected
                rows[_ti].sources[_date] = (
                    f"identity-enforced: {warning.formula} [solving {_tag}]"
                )
                verified_pairs.add(key)

    if any(
        "identity-enforced" in r.sources.get(d, "")
        or "scope-aligned" in r.sources.get(d, "")
        for r in rows
        for d in filing_dates
    ):
        _apply_hierarchical_articulation(rows, filing_dates)

    return rows, diagnostics


def reconcile_fiscal_year_ends(
    quarterly: StatementResult,
    annual: StatementResult,
    schema_tags: set[str],
) -> None:
    """Rebuild each fiscal-year-end column of a quarterly statement from the annual statement.

    Balance-sheet rows and instant rows take the annual value. Monetary duration rows take
    FY minus the three interim quarters of the fiscal year, and balancing plugs are
    re-articulated.
    """
    annual_rows = {r.tag: r for r in annual.rows}
    quarterly_rows = {r.tag: r for r in quarterly.rows}
    quarterly_dates = sorted(quarterly.dates)
    common = sorted(set(annual.dates) & set(quarterly.dates))
    balance_sheet = quarterly.statement == "balance_sheet"
    copied_tags = sorted(
        {r.tag for r in annual.rows if balance_sheet or r.period_type == "instant"}
        | {r.tag for r in quarterly.rows if balance_sheet or r.period_type == "instant"}
    )

    for fy_end in common:
        for tag in copied_tags:
            if tag == "cash_at_beginning_of_period":
                continue

            a_row = annual_rows.get(tag)
            a_val = a_row.values.get(fy_end) if a_row is not None else None
            q_row = quarterly_rows.get(tag)

            if a_row is None or a_val is None:
                if q_row is not None:
                    q_row.values.pop(fy_end, None)
                    q_row.sources.pop(fy_end, None)
                continue

            if q_row is None:
                q_row = RowResult(
                    tag=a_row.tag,
                    label=a_row.label,
                    description=a_row.description,
                    parent=a_row.parent,
                    sequence=a_row.sequence,
                    factor=a_row.factor,
                    balance=a_row.balance,
                    unit=a_row.unit,
                    period_type=a_row.period_type,
                    values={},
                    sources={},
                )
                quarterly.rows.append(q_row)
                quarterly_rows[tag] = q_row

            q_row.values[fy_end] = a_val
            q_row.sources[fy_end] = a_row.sources.get(fy_end, "")

        end_dt = datetime.strptime(fy_end, "%Y-%m-%d")
        window = [
            d
            for d in quarterly_dates
            if 0 < (end_dt - datetime.strptime(d, "%Y-%m-%d")).days < 355
        ]

        if balance_sheet or len(window) != 3:
            continue

        for row in quarterly.rows:
            if row.period_type != "duration":
                continue

            a_row = annual_rows.get(row.tag)
            a_val = a_row.values.get(fy_end) if a_row is not None else None
            a_source = a_row.sources.get(fy_end, "") if a_row is not None else ""

            if "imputed-plug" in row.sources.get(fy_end, ""):
                row.values.pop(fy_end, None)
                row.sources.pop(fy_end, None)

            if row.tag not in schema_tags or "imputed-plug" in a_source:
                continue

            parts = [row.values.get(d) for d in window]

            if (
                row.unit != "monetary"
                or a_row is None
                or a_val is None
                or any(p is None for p in parts)
            ):
                continue

            labels = "+".join(
                f"Q{i + 1}[{row.sources.get(d, '')}]" for i, d in enumerate(window)
            )
            row.values[fy_end] = a_val - sum(p for p in parts if p is not None)
            row.sources[fy_end] = f"Q4: FY[{a_source}] \u2212 ({labels})"

        rows = list(quarterly.rows)
        existing = {id(r) for r in rows}
        _apply_hierarchical_articulation(rows, {fy_end})
        added = [r for r in rows if id(r) not in existing]

        if added:
            quarterly.rows.extend(added)
            quarterly.rows.sort(key=lambda r: float(r.sequence))
            quarterly_rows.update({r.tag: r for r in added})

    for date in quarterly.preliminary_dates:
        for row in quarterly.rows:
            source = row.sources.get(date)
            if source is not None and not source.startswith("preliminary:"):
                row.sources[date] = f"preliminary:{source}"
