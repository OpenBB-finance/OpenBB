"""Imputation logic: multi-pass derivation, hierarchical articulation, and verification."""

# flake8: noqa: PLR0912

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from datetime import datetime
from decimal import Decimal
from itertools import combinations
from typing import Any

from openbb_sec.utils.statement_schema._detection import (
    detect_reporting_currency,
    prior_period_end,
)
from openbb_sec.utils.statement_schema._extraction import _get_unit_data
from openbb_sec.utils.statement_schema._rules import (
    ADDITIVE_PER_SHARE,
    BALANCE_IDENTITY_LINES,
    BALANCE_TOTALS,
    BS_IMPUTE,
    BS_VERIFY,
    CF_IMPUTE,
    CF_SIGN_KEEP,
    CF_VERIFY,
    CLASSIFIED_SECTIONS,
    CONTAINABLE,
    DILUTED_SHARES,
    EPS_NUMERATOR,
    EVIDENCED_LINES,
    IDENTITIES,
    IS_IMPUTE,
    IS_IMPUTE_COMMON,
    IS_VERIFY,
    MAX_IMPUTE_PASSES,
    NONNEGATIVE_LINES,
    OTHER_LINES,
    PROMOTABLE_MEMOS,
    REMAINDER_REQUIRES,
    ROLLUP_REQUIRES,
    SCOPE_VARIANTS,
    SINGLE_STEP,
    SOFT_TOTALS,
    WHOLE_REMAINDERS,
)
from openbb_sec.utils.statement_schema._types import (
    ALL_FORMS,
    ANNUAL_FORMS,
    CompanyType,
    Frequency,
    RowResult,
    StatementName,
    StatementResult,
    ValidationWarning,
    _tolerance,
    source_tag,
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

    A reported costs total that is revenue less pretax income is no input at its date, and
    a balance or gross line derived as zero holds no value.
    Returns True if any value was derived across all passes.
    """
    any_changed = False
    parent_of = {r.tag: r.parent for r in rows}
    revenue, costs, pretax = (
        rows[tag_idx[t]] if t in tag_idx else None for t in SINGLE_STEP
    )

    def pretax_on(date: str) -> float | None:
        """Return pretax income as reported or from the first rule without revenue or costs."""
        if pretax is not None and pretax.values.get(date) is not None:
            return pretax.values[date]

        for target, sources in rules:
            values = [
                rows[tag_idx[t]].values.get(date) if t in tag_idx else None
                for t, _ in sources
            ]

            if (
                target == SINGLE_STEP[2]
                and not {t for t, _ in sources} & set(SINGLE_STEP[:2])
                and all(v is not None for v in values)
            ):
                return sum((v or 0) * s for v, (_, s) in zip(values, sources))

        return None

    single_step = (
        {
            date
            for date in filing_dates
            if revenue.values.get(date) is not None
            and costs.values.get(date) is not None
            and (p := pretax_on(date)) is not None
            and not costs.sources.get(date, "").startswith(
                ("imputed", "corrected", "identity-enforced")
            )
            and abs(revenue.values[date] - costs.values[date] - p)
            <= _tolerance(revenue.values[date], costs.values[date])
        }
        if revenue is not None and costs is not None
        else set()
    )

    def is_ancestor(ancestor: str, tag: str) -> bool:
        seen: set[str] = set()
        p = parent_of.get(tag)

        while p and p not in seen:
            if p == ancestor:
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

                val = 0
                all_present = True

                for src_tag, sign in sources:
                    src_i = tag_idx.get(src_tag)

                    if src_i is None:
                        all_present = False
                        break

                    src_val = rows[src_i].values.get(date)

                    if (
                        src_val is None
                        or (src_tag == SINGLE_STEP[1] and date in single_step)
                        or (
                            rows[src_i]
                            .sources.get(date, "")
                            .startswith("imputed-rollup")
                            and is_ancestor(src_tag, target_tag)
                        )
                    ):
                        all_present = False
                        break

                    val += src_val * sign

                if all_present and not (val == 0 and target_tag in NONNEGATIVE_LINES):
                    target_row.values[date] = val
                    target_row.sources[date] = _format_impute_source("imputed", sources)
                    changed = True

        if not changed:
            break

        any_changed = True

    return any_changed


_DIRECT_SOURCE = re.compile(
    r"(us-gaap|ifrs-full|srt|dei):([A-Za-z0-9_]+)"
    r"(?:\((?:fallback|identity_lock:[a-z_]+)\))?"
)


def _tag_facts(
    facts: dict[str, Any],
    namespace: str,
    tag: str,
    row: RowResult,
    currency: str,
) -> dict[str, list[tuple[str, int, float]]]:
    """Return {end: [(filed, days, value)]} for a tag's facts; instants have zero days."""
    tag_data = facts.get(namespace, {}).get(tag)
    entries = _get_unit_data(tag_data, row.unit, currency) if tag_data else None
    by_end: dict[str, list[tuple[str, int, float]]] = {}

    for entry in entries or []:
        val, end, start = entry.get("val"), entry.get("end"), entry.get("start")

        if val is None or not end:
            continue

        days = (
            (
                datetime.strptime(end, "%Y-%m-%d")
                - datetime.strptime(start, "%Y-%m-%d")
            ).days
            if start
            else 0
        )
        by_end.setdefault(end, []).append((entry.get("filed", ""), days, val))

    return by_end


def _resolve_sign_flips(
    rows: list[RowResult],
    filing_dates: set[str],
    facts: dict[str, Any],
    frequency: Frequency,
    negated: set[str],
    rules: list[tuple[str, list[tuple[str, int]]]],
) -> None:
    """Take another filing's opposite-signed fact for the one child whose sign alone breaks its parent.

    A parent without a value is derived by the first rule whose inputs all have values.
    """
    currency = detect_reporting_currency(facts)
    tag_to_row = {r.tag: r for r in rows}
    children_by_parent: dict[str, list[RowResult]] = {}
    grouped: dict[tuple[str, str], dict[str, list[tuple[str, int, float]]]] = {}
    low, high = (300, 400) if frequency == "annual" else (60, 135)

    for row in rows:
        if row.parent in tag_to_row and row.factor in ("+", "-"):
            children_by_parent.setdefault(row.parent, []).append(row)

    def opposite(child: RowResult, date: str) -> float | None:
        """Return the opposite-signed value another filing reports for a child's direct fact."""
        value = child.values.get(date)
        match = _DIRECT_SOURCE.fullmatch(child.sources.get(date, ""))

        if not value or match is None:
            return None

        if frequency == "quarterly" and any(
            s.startswith("ytd_derived(")
            and 0
            < (
                datetime.strptime(d, "%Y-%m-%d") - datetime.strptime(date, "%Y-%m-%d")
            ).days
            < 280
            for d, s in child.sources.items()
        ):
            return None

        key = (match[1], match[2])

        if key not in grouped:
            grouped[key] = _tag_facts(facts, match[1], match[2], child, currency)

        raw = -value if child.tag in negated else value
        same = [
            (filed, v)
            for filed, days, v in grouped[key].get(date, [])
            if (low <= days <= high if child.period_type == "duration" else days == 0)
            and abs(abs(v) - abs(raw)) <= 0.005 * abs(raw)
        ]
        flipped = [(f, v) for f, v in same if (v > 0) != (raw > 0)]

        if not flipped or all(v != raw for _, v in same):
            return None

        alt = max(flipped)[1]

        return -alt if child.tag in negated else alt

    def parent_value(parent: RowResult, date: str) -> float | None:
        if parent.values.get(date) is not None:
            return parent.values[date]

        for target, sources in rules:
            inputs = [(tag_to_row.get(tag), s) for tag, s in sources]

            if target == parent.tag and all(
                r is not None and r.values.get(date) is not None for r, _ in inputs
            ):
                return sum(r.values[date] * s for r, s in inputs if r is not None)

        return None

    for parent_tag, children in children_by_parent.items():
        parent = tag_to_row[parent_tag]

        for date in filing_dates:
            p_val = parent_value(parent, date)
            present = [
                (c, c.values[date]) for c in children if c.values.get(date) is not None
            ]

            if p_val is None or not present:
                continue

            children_sum = sum(v if c.factor == "+" else -v for c, v in present)
            diff = p_val - children_sum
            tolerance = _tolerance(p_val, children_sum)

            if abs(diff) <= tolerance:
                continue

            fixes = []

            for child, value in present:
                alt = opposite(child, date)
                sign = 1 if child.factor == "+" else -1

                if alt is not None and abs(diff + (value - alt) * sign) <= tolerance:
                    fixes.append((child, alt))

            if len(fixes) == 1:
                child, alt = fixes[0]
                child.values[date] = alt
                child.sources[date] = f"{child.sources[date]}(sign-resolved)"


def _apply_hierarchical_articulation(
    rows: list[RowResult],
    filing_dates: set[str],
    cleared: set[int] | None = None,
) -> None:
    """Roll up parents without a value and reconcile each reported parent with its children.

    A cleared remainder line (id in cleared) within tolerance of zero is written back.
    """
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
    blocked = {
        (tag, date)
        for section in (*CLASSIFIED_SECTIONS, BALANCE_TOTALS)
        if all(tag in tag_to_row for tag in section)
        for date in filing_dates
        if all(tag_to_row[tag].values.get(date) is None for tag in section)
        for tag in section
    }

    def sign(row: RowResult, date: str) -> int:
        return -1 if row.factor_on(date) == "-" else 1

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
        line = other_line(row.tag)

        if line is None or line.values.get(date) is None:
            return False

        return not line.sources.get(date, "").startswith("imputed")

    def evidential(row: RowResult, date: str) -> bool:
        """Return whether a total is reported or derived in one step from reported totals."""
        source = row.sources.get(date, "")

        if not source.startswith("imputed"):
            return True

        formula = "" if source.startswith("imputed-rollup") else source.split(":", 1)[1]

        if source.startswith("imputed-plug"):
            formula = formula.split("(", 1)[0]

        inputs = [
            tag_to_row[tag]
            for tag in re.findall(r"[a-z][a-z0-9_]*", formula)
            if tag in tag_to_row and tag != row.tag
        ]

        return bool(inputs) and not any(
            r.sources.get(date, "").startswith("imputed") for r in inputs
        )

    def contained(
        candidates: list[tuple[RowResult, float]],
        holders: list[tuple[RowResult, float]],
        direct: set[int],
        date: str,
        gap: float,
        balance: float,
        tolerance: float,
    ) -> list[tuple[RowResult, float]]:
        pool: list[tuple[RowResult, float]] = []

        def fits(members: list[tuple[RowResult, float]]) -> bool:
            """Each member is a scope variant or fits inside another present line."""
            excluded = {id(r) for r, _ in members}
            outer = set().union(*(ancestors(r) for r, _ in members))
            room = [
                y
                for r, y in pool + holders
                if id(r) not in excluded
                and r.tag not in outer
                and not r.tag.startswith("net_income")
            ]

            return all(
                r.tag in SCOPE_VARIANTS
                or any(y * c > 0 and abs(y) >= abs(c) - tolerance for y in room)
                for r, c in members
            )

        def walk(row: RowResult, path_sign: float) -> None:
            value = row.values.get(date)

            if value is None or row.factor_on(date) not in ("+", "-"):
                return

            row_sign = path_sign * sign(row, date)
            source = row.sources.get(date, "")

            if (
                row.factor in ("+", "-")
                and row.tag not in children_by_parent
                and abs(value) > tolerance
                and not source.startswith("imputed-plug")
                and (row.parent is None or other_line(row.parent) is not row)
            ):
                pool.append((row, row_sign * value))

            if source.startswith("imputed-rollup"):
                for child in children_by_parent.get(row.tag, []):
                    walk(child, row_sign)

        for row, path_sign in candidates:
            walk(row, path_sign)

        def twin(a: tuple[RowResult, float], b: tuple[RowResult, float]) -> bool:
            """Two components carrying one amount: the same fact, or equal balances over the parent."""
            source = a[0].sources.get(date, "")

            return abs(a[1] - b[1]) <= tolerance and (
                bool(source)
                and source == b[0].sources.get(date, "")
                or (
                    a[0].period_type == "instant"
                    and id(a[0]) in direct
                    and id(b[0]) in direct
                    and balance < -tolerance
                    and balance + a[1] >= -tolerance
                )
            )

        lineage = {id(r): ancestors(r) for r, _ in pool}
        singles = [
            (r, c) for r, c in pool if abs(gap + c) <= tolerance and fits([(r, c)])
        ]

        if singles:
            deepest = max(singles, key=lambda rc: get_depth(rc[0].tag))

            if all(
                r is deepest[0] or r.tag in lineage[id(deepest[0])] for r, _ in singles
            ):
                return [deepest]

            if len(singles) == 2 and twin(singles[0], singles[1]):
                return [max(singles, key=lambda rc: float(rc[0].sequence))]

            return []

        pairs = [
            (a, b)
            for i, a in enumerate(pool)
            for b in pool[i + 1 :]
            if a[0].tag not in lineage[id(b[0])]
            and b[0].tag not in lineage[id(a[0])]
            and (
                a[1] * b[1] > 0
                or a[0].tag in SCOPE_VARIANTS
                and b[0].tag in SCOPE_VARIANTS
            )
            and abs(gap + a[1] + b[1]) <= tolerance
            and fits([a, b])
        ]

        if len(pairs) == 1:
            return list(pairs[0])

        twins = [
            (a, b) for i, a in enumerate(pool) for b in pool[i + 1 :] if twin(a, b)
        ]
        facts = [
            pair
            for pair in twins
            if pair[0][0].sources.get(date, "")
            and pair[0][0].sources.get(date, "") == pair[1][0].sources.get(date, "")
        ]

        if facts and len(facts) == len(twins):
            later = [max(pair, key=lambda rc: float(rc[0].sequence)) for pair in facts]
            return list({id(r): (r, c) for r, c in later}.values())

        if len(twins) == 1:
            return [max(twins[0], key=lambda rc: float(rc[0].sequence))]

        repeats = list(
            {
                id(r): (r, c)
                for r, c in (
                    max(pair, key=lambda rc: float(rc[0].sequence)) for pair in twins
                )
            }.values()
        )

        if (
            len(twins) > 1
            and balance < -tolerance
            and balance + sum(c for _, c in repeats) >= -tolerance
        ):
            return repeats

        if balance >= -tolerance or any(r.period_type != "instant" for r, _ in pool):
            return []

        nested = [
            (r, c)
            for r, c in pool
            if r.tag in CONTAINABLE
            and id(r) in direct
            and c > tolerance
            and fits([(r, c)])
        ][:10]
        best: tuple[float, tuple[tuple[RowResult, float], ...]] | None = None

        for size in range(1, len(nested) + 1):
            for group in combinations(nested, size):
                rest = balance + sum(c for _, c in group)

                if rest >= -tolerance and (best is None or rest < best[0]):
                    best = (rest, group)

        return [] if best is None else list(best[1])

    def relocated(
        present: list[tuple[RowResult, float]],
        date: str,
        gap: float,
        tolerance: float,
    ) -> tuple[RowResult, RowResult] | None:
        """Return the reported section total excluding exactly the missing component."""
        found: list[tuple[RowResult, RowResult]] = []

        def visit(row: RowResult, path_sign: float) -> None:
            kids = children_by_parent.get(row.tag, [])
            value = row.values.get(date)

            if value is None or not kids:
                return

            row_sign = path_sign * sign(row, date)
            source = row.sources.get(date, "")

            if source.startswith("imputed-rollup"):
                for kid in kids:
                    if kid.factor_on(date) in ("+", "-"):
                        visit(kid, row_sign)
                return

            if source.startswith(("imputed", "corrected", "identity-enforced")):
                return

            line = other_line(row.tag)
            members = [
                (kid, sign(kid, date) * kid.values[date])
                for kid in kids
                if kid is not line
                and kid.values.get(date) is not None
                and kid.factor_on(date) in ("+", "-")
            ]
            inner = sum(c for _, c in members)

            if value - inner >= -tolerance:
                return

            found.extend(
                (row, kid)
                for kid, c in members
                if kid.tag not in children_by_parent
                and abs(row_sign * c - gap) <= tolerance
                and value - inner + c >= -tolerance
            )

        for component, _ in present:
            visit(component, 1)

        return found[0] if len(found) == 1 else None

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
            sections = [
                c for c in children if c.tag in REMAINDER_REQUIRES.get(parent_tag, ())
            ]
            own_plug = f"imputed-plug: {parent_tag} - "

            def state(date: str) -> tuple[float | None, ...]:
                return (
                    parent_row.values.get(date),  # noqa: B023
                    other_row.values.get(date) if other_row is not None else None,  # noqa: B023
                )

            def absorbable(row: RowResult, date: str) -> bool:
                source = row.sources.get(date, "")

                if source.startswith(own_plug):  # noqa: B023
                    return True

                return source.startswith("imputed-rollup") and " + " in source

            for date in filing_dates:
                if (parent_tag, date) in blocked or (other_tag, date) in blocked:
                    continue

                before = state(date)

                parent_source = parent_row.sources.get(date, "")

                if parent_source.startswith("imputed-rollup") or (
                    parent_tag in SOFT_TOTALS
                    and parent_source.endswith("(fallback)")
                    and any(c.values.get(date) is not None for c in children)
                ):
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
                other_sign = sign(other_row, date) if other_row is not None else 1
                explicit_sum = sum(sign(c, date) * v for c, v in present)
                detail = " + ".join(f"{c.tag}({c.factor_on(date)})" for c, _ in present)
                p_val = parent_row.values.get(date)

                if p_val is None:
                    if (
                        required is not None
                        and (
                            not required
                            or (
                                required_children
                                and not any(
                                    c.values.get(date) is not None
                                    for c in required_children
                                )
                            )
                        )
                        or (not other_val and not any(v for _, v in present))
                        or (
                            other_val is None
                            and all(c.factor_on(date) == "-" for c, _ in present)
                        )
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
                elif (
                    present
                    or (
                        parent_tag in WHOLE_REMAINDERS
                        and other_row is not None
                        and (
                            other_popped
                            or other_row.sources.get(date, "").startswith(
                                "imputed-rollup"
                            )
                        )
                    )
                ) and (
                    not sections
                    or any(c.values.get(date) is not None for c in sections)
                ):
                    gap = p_val - explicit_sum
                    unexplained = gap - (other_val or 0) * other_sign
                    tolerance = _tolerance(p_val, explicit_sum)

                    if abs(unexplained) > tolerance:
                        candidates: list[tuple[RowResult, float]] = [
                            (c, 1) for c, _ in present
                        ]
                        holders = [(c, sign(c, date) * v) for c, v in present]

                        balance = gap

                        if other_row is not None and other_val is not None:
                            holders.append((other_row, other_val * other_sign))

                            if other_row.sources.get(date, "").startswith(
                                "imputed-rollup"
                            ):
                                balance = unexplained
                                candidates += [
                                    (g, other_sign)
                                    for g in children_by_parent.get(other_row.tag, [])
                                ]

                        hits = (
                            contained(
                                candidates,
                                holders,
                                {id(c) for c, _ in present},
                                date,
                                unexplained,
                                balance,
                                tolerance,
                            )
                            if evidential(parent_row, date)
                            else []
                        )

                        if (
                            len(hits) == 1
                            and other_val is not None
                            and abs(other_val * other_sign - hits[0][1]) <= tolerance
                            and not (
                                hits[0][0].parent == other_tag
                                and other_row is not None
                                and other_row.sources.get(date, "").startswith(
                                    "imputed-rollup"
                                )
                            )
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

                        moved = relocated(present, date, unexplained, tolerance)

                        if moved is not None:
                            section_row, leaf = moved
                            section_row.values[date] += (
                                sign(leaf, date) * leaf.values[date]
                            )
                            section_row.sources[date] = (
                                f"corrected: {section_row.tag} + {leaf.tag}"
                            )
                            changed = True
                            continue

                        section = (
                            other_row is not None
                            and not other_row.tag.startswith("other_")
                            and other_row.tag != "redeemable_nci_other"
                        )
                        absorbers = [
                            c
                            for c, _ in present
                            if section
                            and absorbable(c, date)
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

                        fallback_row = (
                            tag_to_row.get(EVIDENCED_LINES.get(other_row.tag, ""))
                            if other_row is not None
                            and other_val is None
                            and unexplained * other_sign > 0
                            else None
                        )

                        if (
                            fallback_row is not None
                            and fallback_row.parent == parent_tag
                            and fallback_row.values.get(date) is None
                        ):
                            fallback_row.date_factors.pop(date, None)
                            fallback_row.values[date] = unexplained * sign(
                                fallback_row, date
                            )
                            fallback_row.sources[date] = f"{own_plug}({detail})"
                            changed = True
                            continue

                        if (
                            fallback_row is not None
                            and any(c is fallback_row for c, _ in present)
                            and fallback_row.sources.get(date, "").startswith(
                                ("imputed-rollup", own_plug)
                            )
                        ):
                            absorbers = [fallback_row]

                        if len(absorbers) == 1 and absorbers[0] is not other_row:
                            absorber = absorbers[0]
                            absorber.values[date] += unexplained * sign(absorber, date)
                            absorber.sources[date] = (
                                own_plug
                                + "("
                                + " + ".join(
                                    f"{c.tag}({c.factor_on(date)})"
                                    for c, _ in present
                                    if c is not absorber
                                )
                                + ")"
                            )
                        elif (
                            other_tag in NONNEGATIVE_LINES
                            and gap
                            * (1 if other_row is None else sign(other_row, date))
                            < -tolerance
                        ):
                            pass
                        elif other_row is not None or (
                            other_tag not in tag_to_row
                            and any(c.factor_on(date) != "-" for c, _ in present)
                        ):
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

                            other_row.date_factors.pop(date, None)
                            other_row.values[date] = gap * sign(other_row, date)
                            other_row.sources[date] = f"{own_plug}({detail})"
                    elif (
                        cleared
                        and other_row is not None
                        and other_val is None
                        and id(other_row) in cleared
                    ):
                        other_row.date_factors.pop(date, None)
                        other_row.values[date] = gap * sign(other_row, date)
                        other_row.sources[date] = f"{own_plug}({detail})"

                after = state(date)

                if after != before:
                    changed = True

        if not changed:
            break

    for parent_tag in parents:
        parent_row = tag_to_row[parent_tag]
        own_plug = f"imputed-plug: {parent_tag} - "

        for child in children_by_parent[parent_tag]:
            for date in [
                d
                for d, s in child.sources.items()
                if s.startswith(own_plug) and parent_row.values.get(d) is None
            ]:
                child.values.pop(date, None)
                child.sources.pop(date, None)

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
) -> tuple[list[RowResult], list[ValidationWarning]]:
    """Apply imputation rules to derive missing values, then validate."""
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

    if facts is not None:
        _resolve_sign_flips(
            rows,
            filing_dates,
            facts,
            frequency,
            {
                r.tag
                for r in rows
                if statement == "cash_flow"
                and r.balance == "credit"
                and r.factor != "0"
                and r.tag not in CF_SIGN_KEEP
            },
            rules,
        )

    _apply_hierarchical_articulation(rows, filing_dates)
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
        rnci_i = tag_idx.get("temporary_equity")

        if all(i is not None for i in [enci_i, ep_i, nci_i, le_i, l_i]):
            for date in filing_dates:
                enci_v = rows[enci_i].values.get(date)  # ty: ignore[invalid-argument-type]
                ep_v = rows[ep_i].values.get(date)  # ty: ignore[invalid-argument-type]
                nci_v = rows[nci_i].values.get(date, 0)  # ty: ignore[invalid-argument-type]
                le_v = rows[le_i].values.get(date)  # ty: ignore[invalid-argument-type]
                l_v = rows[l_i].values.get(date)  # ty: ignore[invalid-argument-type]
                rnci_v = rows[rnci_i].values.get(date, 0) if rnci_i is not None else 0
                rnci_reported = (
                    0
                    if rnci_i is not None
                    and rows[rnci_i].sources.get(date, "").startswith("imputed-plug")
                    else rnci_v
                )

                if any(v is None for v in [enci_v, ep_v, le_v, l_v]):
                    continue

                if abs(enci_v - ep_v - nci_v) <= _tolerance(enci_v, ep_v, nci_v) or (  # ty: ignore[unsupported-operator]
                    rnci_v and abs(nci_v - rnci_v) <= _tolerance(nci_v, rnci_v)
                ):
                    continue

                circular = "total_equity_and_noncontrolling_interests" in rows[  # ty: ignore[invalid-argument-type]
                    l_i
                ].sources.get(date, "")

                if not circular and abs(
                    l_v + ep_v + nci_v + rnci_reported - le_v  # ty: ignore[unsupported-operator]
                ) <= _tolerance(le_v, l_v, ep_v, nci_v, rnci_reported):
                    rows[enci_i].values[date] = ep_v + nci_v  # ty: ignore[invalid-argument-type, unsupported-operator]
                    rows[enci_i].sources[date] = (  # ty: ignore[invalid-argument-type]
                        "corrected: total_equity + noncontrolling_interests"
                    )
                    rows[nci_i].date_factors.pop(date, None)  # ty: ignore[invalid-argument-type]
                    continue

                if abs(l_v + enci_v + rnci_v - le_v) > _tolerance(  # ty: ignore[unsupported-operator]
                    le_v, l_v, enci_v, rnci_v
                ):
                    continue

                if (
                    circular
                    and rows[enci_i].sources.get(date, "").endswith("(fallback)")  # ty: ignore[invalid-argument-type]
                    and not rows[ep_i].sources.get(date, "").endswith("(fallback)")  # ty: ignore[invalid-argument-type]
                ):
                    rows[enci_i].values[date] = ep_v + nci_v  # ty: ignore[invalid-argument-type, unsupported-operator]
                    rows[enci_i].sources[date] = (  # ty: ignore[invalid-argument-type]
                        "corrected: total_equity + noncontrolling_interests"
                    )
                    rows[nci_i].date_factors.pop(date, None)  # ty: ignore[invalid-argument-type]
                    continue

                rows[ep_i].values[date] = enci_v - nci_v  # ty: ignore[invalid-argument-type, unsupported-operator]
                rows[ep_i].sources[date] = (  # ty: ignore[invalid-argument-type]
                    "reconciled: total_equity_and_noncontrolling"
                    "_interests - noncontrolling_interests"
                )
                rows[nci_i].date_factors.pop(date, None)  # ty: ignore[invalid-argument-type]

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

            val = 0
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

            if statement == "income_statement" and target_tag in (
                "total_pretax_income",
                "net_income_continuing",
            ):
                _ptx = rows[tag_idx["total_pretax_income"]]
                _nic = rows[tag_idx["net_income_continuing"]]
                _tax = rows[tag_idx["income_tax_expense"]]
                _pv = _ptx.values[date]
                _nv = _nic.values[date]
                _tv = _tax.values[date]
                _parts = [
                    rows[tag_idx[t]]
                    for t in ("income_tax_current", "income_tax_deferred")
                    if t in tag_idx
                ]
                _hard_parts = [
                    p
                    for p in _parts
                    if p.values.get(date) is not None
                    and not p.sources.get(date, "").startswith("imputed")
                ]

                if (
                    not _is_target_soft(_ptx.sources.get(date, ""))
                    and not _is_target_soft(_nic.sources.get(date, ""))
                    and abs(_pv - _nv + _tv) <= _tolerance(_pv, _nv, _tv)
                    and not (
                        len(_hard_parts) == 2
                        and abs(sum(p.values[date] for p in _hard_parts) - _tv)
                        <= _tolerance(_tv)
                    )
                ):
                    _tax.values[date] = -_tv
                    _tax.sources[date] = (
                        "corrected: total_pretax_income - net_income_continuing"
                    )

                    if len(_parts) == 2 and len(_hard_parts) == 1:
                        _peer = _hard_parts[0]
                        _part = _parts[1] if _peer is _parts[0] else _parts[0]

                        if _part.sources.get(date, "").startswith("imputed"):
                            _part.values[date] = -_tv - _peer.values[date]
                            _part.sources[date] = (
                                f"imputed: income_tax_expense - {_peer.tag}"
                            )

                    verified_pairs.add(("total_pretax_income", date))
                    verified_pairs.add(("net_income_continuing", date))
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

            if (
                target_tag
                in (
                    "total_equity_and_noncontrolling_interests",
                    "total_equity",
                )
                and facts is not None
                and (target_tag, date) not in verified_pairs
            ):
                _rnci_i = tag_idx.get("temporary_equity")
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
                    other_sum = sum(
                        rows[tag_idx[src_tag]].values[date] * sign
                        for src_tag, sign in sources
                        if src_tag != fix_tag
                    )
                    solved = (target_row.values[date] - other_sum) * fix_sign

                    if fix_tag not in NONNEGATIVE_LINES or solved >= -_tolerance(
                        solved
                    ):
                        fix_i = tag_idx[fix_tag]
                        rows[fix_i].values[date] = solved
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
        or r.sources.get(d, "").startswith("corrected: total_pretax_income")
        for r in rows
        for d in filing_dates
    ):
        _apply_hierarchical_articulation(rows, filing_dates)

    return rows, diagnostics


def _rollup_parts(source: str) -> frozenset[str] | None:
    """Return the components of a rollup source, or None for any other source."""
    source = source.removeprefix("preliminary:")

    if not source.startswith("imputed-rollup"):
        return None

    return frozenset(re.findall(r"([a-z][a-z0-9_]*)\(", source.split(":", 1)[1]))


def _formula_terms(source: str) -> list[tuple[str, int]]:
    """Return the (tag, sign) terms of an imputation source formula."""
    terms: list[tuple[str, int]] = []
    sign = 1

    for term in source.split(":", 1)[1].split():
        if term in ("+", "-"):
            sign = 1 if term == "+" else -1
        else:
            terms.append((term.lstrip("-"), -sign if term.startswith("-") else sign))
            sign = 1

    return terms


def _days(entry: dict) -> int:
    """Return the length of a duration fact in days."""
    return (
        datetime.strptime(entry["end"], "%Y-%m-%d")
        - datetime.strptime(entry["start"], "%Y-%m-%d")
    ).days


def _consistent_q4(
    row: RowResult,
    fy_source: str,
    window: list[str],
    fy_end: str,
    fy_value: float,
    facts: dict[str, Any],
    currency: str,
    negate: bool,
) -> tuple[float, str] | None:
    """Return a Q4 on the quarters' filing basis from the concept's nine-month and annual facts.

    FY less the latest nine-month value filed with the annual value when the quarters do not
    sum to it; otherwise the fiscal year as filed before a restatement, when a nine-month
    value filed before it equals the quarters.
    """
    match = _DIRECT_SOURCE.fullmatch(fy_source)

    if match is None:
        return None

    tag_data = facts.get(match[1], {}).get(match[2])
    entries = [
        e
        for e in (
            _get_unit_data(tag_data, row.unit, currency) or [] if tag_data else []
        )
        if e.get("val") is not None and e.get("start") and e.get("end")
    ]
    sign = -1 if negate else 1
    quarters = [row.values[d] for d in window]
    q_sum = sum(quarters)
    annual = [
        e
        for e in entries
        if e["end"] == fy_end
        and e.get("form") in ANNUAL_FORMS
        and 300 <= _days(e) <= 400
    ]
    ref = [e for e in annual if abs(sign * e["val"] - fy_value) <= _tolerance(fy_value)]

    if not ref:
        return None

    start = ref[0]["start"]
    ref_filed = max(e.get("filed", "") for e in ref)
    nine = [
        e
        for e in entries
        if e.get("form") not in ANNUAL_FORMS
        and e["start"] == start
        and e["end"] == window[2]
    ]
    filed_nine = [e for e in nine if e.get("filed", "") <= ref_filed]

    if filed_nine:
        c9 = sign * max(filed_nine, key=lambda e: e.get("filed", ""))["val"]

        if abs(c9 - q_sum) > _identity_tolerance([c9, *quarters], 4):
            return (
                fy_value - c9,
                f"Q4: FY[{fy_source}] \u2212 9M[{match[1]}:{match[2]}]",
            )

    t_q = max(
        (
            e.get("filed", "")
            for e in entries
            if e["end"] in window and e.get("form") not in ANNUAL_FORMS
        ),
        default="",
    )
    prior = [e for e in annual if e.get("filed", "") <= t_q]

    if not prior:
        return None

    last = max(prior, key=lambda e: e.get("filed", ""))
    fy_prior = sign * last["val"]

    if abs(fy_prior - fy_value) > _tolerance(fy_prior, fy_value) and any(
        e.get("filed", "") <= last.get("filed", "")
        and abs(sign * e["val"] - q_sum)
        <= _identity_tolerance([sign * e["val"], *quarters], 4)
        for e in nine
    ):
        labels = "+".join(
            f"Q{i + 1}[{row.sources.get(d, '')}]" for i, d in enumerate(window)
        )
        return fy_prior - q_sum, (
            f"Q4: FY[{match[1]}:{match[2]}(filed {last.get('filed', '')})]"
            f" \u2212 ({labels})"
        )

    return None


def _quarter_facts(
    row: RowResult,
    concepts: set[str | None],
    end: str,
    facts: dict[str, Any] | None,
    currency: str,
    negate: bool,
) -> set[float]:
    """Return the three-month values filed for a row's concepts ending at a date."""
    found: set[float] = set()

    for concept in concepts:
        match = _DIRECT_SOURCE.fullmatch(concept or "")

        if facts is None or match is None:
            continue

        tag_data = facts.get(match[1], {}).get(match[2])

        for e in _get_unit_data(tag_data, row.unit, currency) or [] if tag_data else []:
            if (
                e.get("end") == end
                and e.get("start")
                and e.get("val") is not None
                and e.get("form") in ALL_FORMS
                and 60 <= _days(e) <= 135
            ):
                found.add((-1 if negate else 1) * e["val"])

    return found


def _restated_fy(
    row: RowResult,
    fy_source: str,
    window: list[str],
    fy_end: str,
    fy_value: float,
    facts: dict[str, Any],
    currency: str,
    negate: bool,
) -> bool:
    """Return whether the annual value differs from the fiscal year as filed by the quarters' last filing."""
    match = _DIRECT_SOURCE.fullmatch(fy_source)

    if match is None:
        return False

    tag_data = facts.get(match[1], {}).get(match[2])
    entries = [
        e
        for e in (
            _get_unit_data(tag_data, row.unit, currency) or [] if tag_data else []
        )
        if e.get("val") is not None and e.get("start") and e.get("end")
    ]
    t_q = max(
        (
            e.get("filed", "")
            for e in entries
            if e["end"] in window and e.get("form") not in ANNUAL_FORMS
        ),
        default="",
    )
    prior = [
        e
        for e in entries
        if e["end"] == fy_end
        and e.get("form") in ANNUAL_FORMS
        and 300 <= _days(e) <= 400
        and e.get("filed", "") <= t_q
    ]

    if not prior:
        return False

    last = max(prior, key=lambda e: e.get("filed", ""))

    return abs((-1 if negate else 1) * last["val"] - fy_value) > _tolerance(fy_value)


def _q4_per_share(
    rows: list[RowResult],
    annual_rows: dict[str, RowResult],
    window: list[str],
    fy_start: str,
    fy_end: str,
) -> None:
    """Derive the Q4 share counts, dividends per share and EPS the filings do not report.

    A weighted average share count is the day-weighted average of its quarters, dividends per
    share add across quarters, and EPS is Q4 net income to common over the Q4 share count; a
    loss quarter's diluted shares are its basic shares.
    """
    by_tag = {r.tag: r for r in rows}
    ends = [datetime.strptime(d, "%Y-%m-%d") for d in (fy_start, *window, fy_end)]
    spans = [(b - a).days for a, b in zip(ends, ends[1:])]
    derived: set[str] = set()

    for row in rows:
        a_row = annual_rows.get(row.tag)
        a_val = a_row.values.get(fy_end) if a_row is not None else None
        quarters = [row.values.get(d) for d in window]

        if (
            a_row is None
            or a_val is None
            or row.values.get(fy_end) is not None
            or None in quarters
            or row.unit not in ("shares", "per_share")
            or (row.unit == "per_share" and row.tag not in ADDITIVE_PER_SHARE)
        ):
            continue

        if row.unit == "shares":
            value: float = (
                a_val * sum(spans) - sum((q or 0) * s for q, s in zip(quarters, spans))
            ) / spans[3]
        else:
            value = float(
                Decimal(str(a_val))
                - sum((Decimal(str(q)) for q in quarters), Decimal(0))
            )

        if value < 0 or (row.unit == "shares" and value == 0):
            continue

        labels = "+".join(
            f"Q{i + 1}[{row.sources.get(d, '')}]" for i, d in enumerate(window)
        )
        row.values[fy_end] = round(value) if row.unit == "shares" else value
        row.sources[fy_end] = (
            f"Q4: FY[{a_row.sources.get(fy_end, '')}] \u2212 ({labels})"
            + (", day-weighted" if row.unit == "shares" else "")
        )
        derived.add(row.tag)

    numerator = by_tag.get(EPS_NUMERATOR)
    income = numerator.values.get(fy_end) if numerator is not None else None

    for diluted, basic in DILUTED_SHARES.items():
        d_row, b_row = by_tag.get(diluted), by_tag.get(basic)

        if (
            income is not None
            and income < 0
            and d_row is not None
            and b_row is not None
            and b_row.values.get(fy_end) is not None
            and (diluted in derived or d_row.values.get(fy_end) is None)
            and any(d_row.values.get(d) is not None for d in window)
        ):
            d_row.values[fy_end] = b_row.values[fy_end]
            d_row.sources[fy_end] = f"Q4: {basic} (antidilutive loss)"

    for row in rows:
        shares = next(
            (r for r in rows if r.parent == row.tag and r.factor == "/"), None
        )

        if (
            row.unit != "per_share"
            or row.tag in ADDITIVE_PER_SHARE
            or row.values.get(fy_end) is not None
            or not any(row.values.get(d) is not None for d in window)
            or shares is None
            or income is None
        ):
            continue

        count = shares.values.get(fy_end)

        if count is None or count <= 0:
            continue

        row.values[fy_end] = round(income / count, 2)
        row.sources[fy_end] = f"Q4: {EPS_NUMERATOR} \u00f7 {shares.tag}"


def reconcile_fiscal_year_ends(
    quarterly: StatementResult,
    annual: StatementResult,
    schema_tags: set[str],
    facts: dict[str, Any] | None = None,
    currency: str = "USD",
) -> None:
    """Rebuild each fiscal-year-end column of a quarterly statement from the annual statement.

    Balance-sheet rows and instant rows take the annual value, for the lines the interim
    quarters report. Monetary duration rows take
    FY minus the three interim quarters of the fiscal year, and otherwise keep FY minus the
    nine-month value derived at extraction; a row whose quarters all roll up rolls
    up in Q4 as well when the annual statement reports a component the quarters lack,
    reports every component they roll up, or is itself a rollup, and a row whose
    quarters come from another concept keeps the Q4 derived from that concept. H2
    values and balancing plugs are cleared, and plugs are re-articulated; a line none of the
    interim quarters report holds no derived Q4 value. A Q4 of the opposite sign of three
    quarters of one concept is taken from that concept's facts when they give one on the
    quarters' filing basis. Share counts, dividends per share and EPS the filings do not
    report for Q4 are derived from the annual and interim values.
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
    windows: dict[str, list[str]] = {}
    allowance: dict[str, dict[str, float]] = {}
    restated: dict[str, set[str]] = {}
    trusted: dict[str, set[str]] = {}

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
                    q_row.date_factors.pop(fy_end, None)
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

            if fy_end in a_row.date_factors:
                q_row.date_factors[fy_end] = a_row.date_factors[fy_end]
            else:
                q_row.date_factors.pop(fy_end, None)

        end_dt = datetime.strptime(fy_end, "%Y-%m-%d")
        window = [
            d
            for d in quarterly_dates
            if 0 < (end_dt - datetime.strptime(d, "%Y-%m-%d")).days < 355
        ]
        windows[fy_end] = window

        if any(r.values.get(d) is not None for r in quarterly.rows for d in window):
            for row in quarterly.rows:
                if (
                    row.tag in copied_tags
                    and row.tag != "cash_at_beginning_of_period"
                    and row.tag not in BALANCE_IDENTITY_LINES
                    and all(row.values.get(d) is None for d in window)
                ):
                    row.values.pop(fy_end, None)
                    row.sources.pop(fy_end, None)
                    row.date_factors.pop(fy_end, None)

            for row in quarterly.rows:
                parent = quarterly_rows.get(row.parent or "")

                if row.sources.get(fy_end, "").startswith(
                    ("imputed-plug", "imputed-zero-plug")
                ) and (parent is None or parent.values.get(fy_end) is None):
                    row.values.pop(fy_end, None)
                    row.sources.pop(fy_end, None)
                    row.date_factors.pop(fy_end, None)

        inherited = identity_residuals(annual.rows, quarterly.statement, fy_end)

        for d in [] if balance_sheet else window:
            for target, residual in identity_residuals(
                quarterly.rows, quarterly.statement, d
            ).items():
                inherited[target] = abs(inherited.get(target, 0)) + abs(residual)

        allowance[fy_end] = {t: abs(r) for t, r in inherited.items()}

        if balance_sheet or len(window) != 3:
            continue

        cleared: set[int] = set()
        repaired: set[str] = set()
        candidates: list[tuple[RowResult, tuple[float, str]]] = []
        broken_fixed = False

        for row in quarterly.rows:
            if row.period_type != "duration":
                continue

            a_row = annual_rows.get(row.tag)
            a_val = a_row.values.get(fy_end) if a_row is not None else None
            a_source = a_row.sources.get(fy_end, "") if a_row is not None else ""

            quarter_sources = [row.sources[d] for d in window if d in row.sources]

            if "imputed-plug" in row.sources.get(fy_end, "") or (
                quarter_sources
                and all("imputed-plug" in source for source in quarter_sources)
            ):
                cleared.add(id(row))

            if any(
                key in row.sources.get(fy_end, "") for key in ("imputed-plug", "H2:")
            ):
                row.values.pop(fy_end, None)
                row.sources.pop(fy_end, None)

            if row.tag not in schema_tags or "imputed-plug" in a_source:
                continue

            present = [d for d in window if row.values.get(d) is not None]

            if row.unit != "monetary" or a_val is None or len(present) != 3:
                continue

            parts = [_rollup_parts(row.sources.get(d, "")) for d in present]
            annual_parts = {
                c.tag
                for c in annual.rows
                if c.parent == row.tag
                and c.values.get(fy_end) is not None
                and c.factor_on(fy_end) in ("+", "-")
            }

            q_parts = {tag for part in parts if part is not None for tag in part}
            reported_parts = {
                c.tag
                for c in annual.rows
                if c.tag in annual_parts
                and "imputed-plug" not in c.sources.get(fy_end, "")
            }

            if None not in parts and (
                annual_parts - q_parts
                or q_parts <= reported_parts
                or _rollup_parts(a_source) is not None
            ):
                if not row.sources.get(fy_end, "").startswith("imputed-rollup"):
                    row.values.pop(fy_end, None)
                    row.sources.pop(fy_end, None)
                continue

            q_tags = {source_tag(row.sources.get(d, "")) for d in present}
            current = row.sources.get(fy_end, "").removeprefix("preliminary:")
            negate = (
                quarterly.statement == "cash_flow"
                and row.balance == "credit"
                and row.factor != "0"
                and row.tag not in CF_SIGN_KEEP
            )

            if (
                len(q_tags) == 1
                and None not in q_tags
                and q_tags != {source_tag(a_source)}
                and {source_tag(current.removeprefix("Q4: FY["))} == q_tags
            ):
                if (
                    facts is not None
                    and (q4 := row.values.get(fy_end)) is not None
                    and _restated_fy(
                        row,
                        next(iter(q_tags)) or "",
                        present,
                        fy_end,
                        q4 + sum(row.values[d] for d in present),
                        facts,
                        currency,
                        negate,
                    )
                ):
                    restated.setdefault(fy_end, set()).add(row.tag)

                continue

            labels = "+".join(
                f"Q{window.index(d) + 1}[{row.sources.get(d, '')}]" for d in present
            )
            row.values[fy_end] = a_val - sum(row.values[d] for d in present)
            row.sources[fy_end] = f"Q4: FY[{a_source}] \u2212 ({labels})"
            quarters = [row.values[d] for d in present]
            tolerance = _tolerance(a_val, *quarters)

            if facts is not None and _restated_fy(
                row,
                next(iter(q_tags)) or ""
                if len(q_tags) == 1 and None not in q_tags
                else a_source,
                present,
                fy_end,
                a_val,
                facts,
                currency,
                negate,
            ):
                restated.setdefault(fy_end, set()).add(row.tag)

            if facts is not None and len(q_tags) == 1 and None not in q_tags:
                fixed = _consistent_q4(
                    row,
                    a_source
                    if q_tags == {source_tag(a_source)}
                    else next(iter(q_tags)) or "",
                    present,
                    fy_end,
                    a_val,
                    facts,
                    currency,
                    negate,
                )

                if fixed is not None:
                    candidates.append((row, fixed))
                    broken_fixed = broken_fixed or (
                        (
                            all(v > tolerance for v in quarters)
                            and row.values[fy_end] < -tolerance
                            or all(v < -tolerance for v in quarters)
                            and row.values[fy_end] > tolerance
                        )
                        and fixed[0] * quarters[0] > 0
                    )

        if candidates and not broken_fixed:
            failing = _failing(
                quarterly.rows, quarterly.statement, fy_end, allowance[fy_end]
            )
            kept = [
                (row, (row.values[fy_end], row.sources[fy_end]))
                for row, _ in candidates
            ]

            for row, (value, source) in candidates:
                row.values[fy_end], row.sources[fy_end] = value, source

            broken_fixed = (
                _failing(quarterly.rows, quarterly.statement, fy_end, allowance[fy_end])
                < failing
            )

            for row, (value, source) in [] if broken_fixed else kept:
                row.values[fy_end], row.sources[fy_end] = value, source

        for row, (value, source) in candidates if broken_fixed else []:
            row.values[fy_end], row.sources[fy_end] = value, source
            repaired.add(row.tag)

        while repaired:
            derived = set()

            for row in quarterly.rows:
                a_row = annual_rows.get(row.tag)
                a_source = a_row.sources.get(fy_end, "") if a_row is not None else ""

                if row.tag in repaired or not a_source.startswith("imputed: "):
                    continue

                terms = _formula_terms(a_source)
                inputs = [(quarterly_rows.get(tag), s) for tag, s in terms]

                if repaired & {tag for tag, _ in terms} and all(
                    r is not None and r.values.get(fy_end) is not None
                    for r, _ in inputs
                ):
                    row.values[fy_end] = sum(
                        r.values[fy_end] * s for r, s in inputs if r is not None
                    )
                    row.sources[fy_end] = a_source
                    derived.add(row.tag)

            if not derived:
                break

            repaired |= derived

        trusted[fy_end] = set(repaired)
        imputed = {
            row.tag: formula
            for row in quarterly.rows
            if row.tag not in repaired
            and len(
                formulas := {
                    row.sources.get(d, "").removeprefix("preliminary:") for d in window
                }
            )
            == 1
            and (formula := next(iter(formulas))).startswith("imputed: ")
        }

        for tag, formula in imputed.items():
            if restated.get(fy_end, set()) & {t for t, _ in _formula_terms(formula)}:
                restated[fy_end].add(tag)

        for _ in imputed:
            changed = False

            for tag, formula in imputed.items():
                inputs = [
                    (quarterly_rows.get(term), s) for term, s in _formula_terms(formula)
                ]
                row = quarterly_rows[tag]

                if all(
                    r is not None and r.values.get(fy_end) is not None
                    for r, _ in inputs
                ) and (
                    value := sum(
                        r.values[fy_end] * s for r, s in inputs if r is not None
                    )
                ) != row.values.get(fy_end):
                    row.values[fy_end], row.sources[fy_end] = value, formula
                    changed = True

            if not changed:
                break

        rows = list(quarterly.rows)
        existing = {id(r) for r in rows}
        _apply_hierarchical_articulation(rows, {fy_end}, cleared)
        added = [r for r in rows if id(r) not in existing]

        if added:
            quarterly.rows.extend(added)
            quarterly.rows.sort(key=lambda r: float(r.sequence))
            quarterly_rows.update({r.tag: r for r in added})

        prior = [
            d for d in sorted(set(quarterly_dates) | set(annual.dates)) if d < window[0]
        ]

        if (
            prior
            and 60
            <= (
                datetime.strptime(window[0], "%Y-%m-%d")
                - datetime.strptime(prior[-1], "%Y-%m-%d")
            ).days
            <= 135
        ):
            _q4_per_share(quarterly.rows, annual_rows, window, prior[-1], fy_end)

        for row in quarterly.rows:
            if (
                row.period_type == "duration"
                and row.values.get(fy_end) is not None
                and all(row.values.get(d) is None for d in window)
                and _DIRECT_SOURCE.fullmatch(row.sources.get(fy_end, "")) is None
            ):
                row.values.pop(fy_end, None)
                row.sources.pop(fy_end, None)
                row.date_factors.pop(fy_end, None)

        bop, ncc, eop = (
            quarterly_rows.get(tag)
            for tag in (
                "cash_at_beginning_of_period",
                "net_change_in_cash",
                "cash_at_end_of_period",
            )
        )

        if bop is None or ncc is None or eop is None:
            continue

        bop_val, ncc_val, eop_val = (
            bop.values.get(fy_end),
            ncc.values.get(fy_end),
            eop.values.get(fy_end),
        )

        if (
            bop_val is not None
            and ncc_val is not None
            and eop_val is not None
            and abs(bop_val + ncc_val - eop_val) > _tolerance(eop_val, bop_val, ncc_val)
        ):
            bop.values[fy_end] = eop_val - ncc_val
            bop.sources[fy_end] = (
                "identity-enforced: cash_at_end_of_period - net_change_in_cash"
            )

    def fourth_quarter_derived(row: RowResult, date: str) -> bool:
        value = row.values.get(date)
        a_row = annual_rows.get(row.tag)
        a_val = a_row.values.get(date) if a_row is not None else None

        if value is None or a_val is None:
            return True

        if balance_sheet or row.period_type == "instant":
            return value != a_val

        if row.tag in trusted.get(date, set()):
            return False

        filed = _quarter_facts(
            row,
            {source_tag(row.sources.get(d, "")) for d in windows[date]}
            | {source_tag(a_row.sources.get(date, "")) if a_row is not None else None},
            date,
            facts,
            currency,
            quarterly.statement == "cash_flow"
            and row.balance == "credit"
            and row.factor != "0"
            and row.tag not in CF_SIGN_KEEP,
        )

        if filed:
            return all(abs(value - v) > _tolerance(value, v) for v in filed)

        quarters = [row.values.get(d) for d in windows[date]]

        return (
            len(quarters) != 3
            or any(q is None for q in quarters)
            or abs(a_val - sum(q or 0 for q in quarters) - value) > 1
            or row.tag in restated.get(date, set())
        )

    enforce_identities(
        quarterly.rows,
        quarterly.statement,
        windows,
        None,
        currency,
        derived=fourth_quarter_derived,
        frequency="quarterly",
        allowance=allowance,
    )

    for fy_end, tags in restated.items():
        by_tag = {r.tag: r for r in quarterly.rows}
        children: dict[str, list[RowResult]] = {}

        for r in quarterly.rows:
            if r.parent:
                children.setdefault(r.parent, []).append(r)

        for target, terms in IDENTITIES.get(quarterly.statement, ()):
            signed = _identity(target, terms, by_tag, children, fy_end)

            if signed is None:
                continue

            lhs, rhs, tolerance = _identity_state(target, signed, by_tag, fy_end)

            for tag in (
                tags & {target, *dict(signed)} if abs(lhs - rhs) > tolerance else ()
            ):
                by_tag[tag].values.pop(fy_end, None)
                by_tag[tag].sources.pop(fy_end, None)
                by_tag[tag].date_factors.pop(fy_end, None)

    quarterly.diagnostics = identity_diagnostics(
        quarterly.rows, quarterly.statement, quarterly.dates
    )

    for date in quarterly.preliminary_dates:
        for row in quarterly.rows:
            source = row.sources.get(date)
            if source is not None and not source.startswith("preliminary:"):
                row.sources[date] = f"preliminary:{source}"


def reported_derived(row: RowResult, date: str) -> bool:
    """Return whether a value is derived rather than read from a filing for its period."""
    source = row.sources.get(date, "").removeprefix("preliminary:")

    return (
        source.startswith(("imputed", "identity-enforced", "derived:"))
        or "(fallback)" in source
    )


def _synthetic(row: RowResult, parent: str) -> bool:
    """Return whether a row is the plug articulation creates for a parent without a remainder line."""
    return row.tag == f"other_{parent.removeprefix('total_')}" and row.tag not in (
        OTHER_LINES.get(parent, ())
    )


def _identity_tolerance(values: list[float], figures: int) -> float:
    """Return the scale tolerance, at least the rounding of `figures` reported figures."""
    present = [v for v in values if v]
    unit = next(
        (
            u
            for u in (1_000_000, 1_000)
            if present
            and all(float(v).is_integer() and int(v) % u == 0 for v in present)
        ),
        1,
    )

    return max(_tolerance(*values), unit * figures / 2)


def _identity(
    target: str,
    terms: tuple[tuple[str, int], ...] | None,
    by_tag: dict[str, RowResult],
    children: dict[str, list[RowResult]],
    date: str,
) -> list[tuple[str, int]] | None:
    """Return the signed terms of an identity at a date, or None when it does not apply."""
    row = by_tag.get(target)

    if row is None or row.values.get(date) is None:
        return None

    if terms is not None:
        signed = [(tag, sign) for tag, sign in terms if tag in by_tag]

        if not signed or any(by_tag[tag].values.get(date) is None for tag, _ in signed):
            return None

        return signed

    kids = sorted(
        (
            c
            for c in children.get(target, [])
            if c.factor_on(date) in ("+", "-") and not _synthetic(c, target)
        ),
        key=lambda c: float(c.sequence),
    )

    if not kids or kids[0].values.get(date) is None:
        return None

    return [(c.tag, 1 if c.factor_on(date) == "+" else -1) for c in kids]


def _identity_state(
    target: str,
    signed: list[tuple[str, int]],
    by_tag: dict[str, RowResult],
    date: str,
    allowance: float = 0,
) -> tuple[float, float, float]:
    """Return the target value, the sum of the terms and the identity's tolerance at a date."""
    lhs = by_tag[target].values[date]
    values = [by_tag[tag].values.get(date) or 0 for tag, _ in signed]
    rhs = sum(sign * v for (_, sign), v in zip(signed, values, strict=True))
    return lhs, rhs, max(_tolerance(lhs, rhs), allowance)


def _failing(
    rows: list[RowResult],
    statement: str,
    date: str,
    allowance: dict[str, float],
) -> set[str]:
    """Return the targets of the statement's IDENTITIES that do not hold at a date."""
    by_tag = {r.tag: r for r in rows}
    children: dict[str, list[RowResult]] = {}

    for r in rows:
        if r.parent:
            children.setdefault(r.parent, []).append(r)

    failing: set[str] = set()

    for target, terms in IDENTITIES.get(statement, ()):
        signed = _identity(target, terms, by_tag, children, date)

        if signed is not None:
            lhs, rhs, tolerance = _identity_state(
                target, signed, by_tag, date, allowance.get(target, 0)
            )

            if abs(lhs - rhs) > tolerance:
                failing.add(target)

    return failing


def identity_residuals(
    rows: list[RowResult], statement: str, date: str
) -> dict[str, float]:
    """Return {target: target value less the sum of its terms} for the statement's IDENTITIES at a date."""
    by_tag = {r.tag: r for r in rows}
    children: dict[str, list[RowResult]] = {}

    for r in rows:
        if r.parent:
            children.setdefault(r.parent, []).append(r)

    residuals: dict[str, float] = {}

    for target, terms in IDENTITIES.get(statement, ()):
        signed = _identity(target, terms, by_tag, children, date)

        if signed is not None:
            lhs, rhs, _ = _identity_state(target, signed, by_tag, date)
            residuals[target] = lhs - rhs

    return residuals


def _rounding_term(statement: str, target: str, signed: list[tuple[str, int]]) -> str:
    """Return the line a verify rule over an identity's terms aligns, else the identity's target."""
    terms = {target, *dict(signed)}
    rules = {
        "income_statement": IS_VERIFY,
        "balance_sheet": BS_VERIFY,
        "cash_flow": CF_VERIFY,
    }.get(statement, [])

    return next(
        (
            line
            for line, sources in rules
            if {line, *(tag for tag, _ in sources)} == terms
        ),
        target,
    )


def _components(
    row: RowResult, children: dict[str, list[RowResult]], date: str, depth: int = 0
) -> float | None:
    """Return the sum of a row's reported lines at a date, through articulation plugs, when its ROLLUP_REQUIRES lines are present."""
    lines = [
        c
        for c in children.get(row.tag, [])
        if c.factor_on(date) in ("+", "-") and not _synthetic(c, row.tag)
    ]
    present = {c.tag for c in lines if c.values.get(date) is not None}

    if not present or not set(ROLLUP_REQUIRES.get(row.tag, ())) <= present:
        return None

    total: float = 0
    found = False

    for c in lines:
        factor = c.factor_on(date)

        if c.values.get(date) is None:
            continue

        sign = 1 if factor == "+" else -1

        if c.sources.get(date, "").startswith(("imputed-plug", "imputed-zero-plug")):
            sub = _components(c, children, date, depth + 1) if depth < 3 else None

            if sub is None:
                continue

            total += sign * sub
        else:
            total += sign * c.values[date]

        found = True

    return total if found else None


def _alternatives(
    row: RowResult,
    date: str,
    facts: dict[str, Any] | None,
    currency: str,
    frequency: Frequency,
) -> set[float]:
    """Return other filings' values of a row's concept for its period."""
    concept = source_tag(row.sources.get(date, "").removeprefix("preliminary:"))

    if facts is None or concept is None:
        return set()

    namespace, tag = concept.split(":", 1)
    tag_data = facts.get(namespace, {}).get(tag)
    entries = _get_unit_data(tag_data, row.unit, currency) if tag_data else None
    span = (300, 400) if frequency == "annual" else (60, 135)
    found: set[float] = set()

    for entry in entries or []:
        start = entry.get("start")

        if (
            entry.get("end") != date
            or entry.get("val") is None
            or entry.get("form") not in ALL_FORMS
            or bool(start) != (row.period_type == "duration")
        ):
            continue

        if start and not (
            span[0]
            <= (
                datetime.strptime(date, "%Y-%m-%d")
                - datetime.strptime(start, "%Y-%m-%d")
            ).days
            <= span[1]
        ):
            continue

        found.add(entry["val"])

    found.discard(row.values.get(date))

    return found


def _expression(coefficients: list[tuple[str, int]]) -> str:
    """Return 'a + b - c' for signed tags."""
    parts = [("-" if coefficients[0][1] < 0 else "") + coefficients[0][0]]

    for tag, sign in coefficients[1:]:
        parts.append(f"{'+' if sign > 0 else '-'} {tag}")

    return " ".join(parts)


def _choose_term(  # noqa: PLR0913
    target: str,
    signed: list[tuple[str, int]],
    by_tag: dict[str, RowResult],
    children: dict[str, list[RowResult]],
    date: str,
    *,
    context: tuple[
        dict[str, Any] | None, str, Frequency, Callable[[RowResult, str], bool]
    ],
    settled: set[str],
    elsewhere: set[str],
    tolerance: float,
    rounding: str | None = None,
    fallback: str | None = None,
) -> tuple[str, float, str] | None:
    """Return the term an identity's evidence points to, its value and its source."""
    facts, currency, frequency, derived = context
    sign = dict(signed)
    value = {tag: by_tag[tag].values.get(date) for tag in (target, *sign)}
    total = by_tag[target].values[date]
    rhs = sum(s * (value[tag] or 0) for tag, s in signed)

    def implied(tag: str) -> float:
        if tag == target:
            return rhs

        return sign[tag] * (total - (rhs - sign[tag] * (value[tag] or 0)))

    pool = [
        tag
        for tag in value
        if tag not in settled
        and not (tag in NONNEGATIVE_LINES and implied(tag) < -tolerance)
        and (value[tag] is not None or tag in OTHER_LINES.get(target, ()))
    ]
    alternatives = {
        tag: [
            a
            for a in _alternatives(by_tag[tag], date, facts, currency, frequency)
            if abs(a - implied(tag)) <= tolerance
        ]
        for tag in pool
        if value[tag] is not None and not derived(by_tag[tag], date)
    }
    components = {
        tag: _components(by_tag[tag], children, date) for tag in pool if tag != target
    }

    def confirmed(tag: str) -> bool:
        found, current = components.get(tag), value[tag]

        return tag in elsewhere or (
            found is not None
            and current is not None
            and abs(found - current) <= tolerance
        )

    levels: list[Callable[[str], bool]] = [
        lambda tag: value[tag] is None or derived(by_tag[tag], date),
        lambda tag: tag in OTHER_LINES.get(target, ()),
        lambda tag: bool(alternatives.get(tag)),
        lambda tag: (
            (found := components.get(tag)) is not None
            and abs(found - implied(tag)) <= tolerance
        ),
        lambda tag: (
            tag != target
            and any(
                _synthetic(c, tag) and abs(c.values.get(date) or 0) > tolerance
                for c in children.get(tag, [])
            )
        ),
        lambda tag: not confirmed(tag),
    ]

    def solved(tag: str) -> tuple[str, float, str]:
        coefficients = (
            list(signed)
            if tag == target
            else [(target, sign[tag])]
            + [(t, -s * sign[tag]) for t, s in signed if t != tag]
        )

        return (
            tag,
            implied(tag),
            f"identity-enforced: {_expression(coefficients)} [solving {tag}]",
        )

    if rounding is not None:
        return solved(rounding) if rounding in pool else None

    eligible = set(pool)

    for level, check in enumerate(levels):
        matched = [tag for tag in pool if check(tag)]

        if len(matched) > 1:
            pool = matched

        if len(matched) != 1:
            continue

        tag = matched[0]

        if level == 2:
            source = by_tag[tag].sources[date].removeprefix("preliminary:")
            return tag, alternatives[tag][0], f"{source} (vintage-corrected)"

        return solved(tag)

    if (
        fallback is None
        or fallback not in eligible
        or any(value.get(tag) is None for tag in ROLLUP_REQUIRES.get(target, ()))
    ):
        return None

    return solved(fallback)


def enforce_identities(  # noqa: PLR0913
    rows: list[RowResult],
    statement: str,
    dates: Iterable[str],
    facts: dict[str, Any] | None,
    currency: str,
    *,
    derived: Callable[[RowResult, str], bool],
    frequency: Frequency = "annual",
    allowance: dict[str, dict[str, float]] | None = None,
) -> None:
    """Make each of the statement's IDENTITIES hold at each date, changing the term the evidence points to.

    Evidence in order: a derived term (`derived`), the target's remainder line (OTHER_LINES),
    another filing's value of a term that satisfies the identity, a term whose reported
    lines sum to its implied value, a term whose own articulation needed a synthetic plug,
    and the only term not confirmed by its lines or by another identity. A difference
    within `allowance` {date: {target: amount}} changes the line the statement's verify
    rules align instead, as does any difference the evidence does not resolve when the
    target's ROLLUP_REQUIRES lines are present. A term set this way is not changed again
    at that date.
    """
    context = (facts, currency, frequency, derived)
    identities = IDENTITIES.get(statement, ())

    for date in sorted(dates):
        settled: set[str] = set()
        allowed = (allowance or {}).get(date, {})

        for _ in range(4 * len(identities)):
            by_tag = {r.tag: r for r in rows}
            children: dict[str, list[RowResult]] = {}

            for r in rows:
                if r.parent:
                    children.setdefault(r.parent, []).append(r)

            states = {}

            for target, terms in identities:
                signed = _identity(target, terms, by_tag, children, date)

                if signed is not None:
                    states[target] = (
                        signed,
                        *_identity_state(target, signed, by_tag, date),
                    )

            choice = None

            for target, (signed, lhs, rhs, tol) in states.items():
                if abs(lhs - rhs) <= tol:
                    continue

                choice = _choose_term(
                    target,
                    signed,
                    by_tag,
                    children,
                    date,
                    context=context,
                    settled=settled,
                    elsewhere={
                        tag
                        for t, (s, a, b, c) in states.items()
                        if t != target and abs(a - b) <= c
                        for tag in (t, *dict(s))
                    },
                    tolerance=tol,
                    rounding=_rounding_term(statement, target, signed)
                    if abs(lhs - rhs) <= tol + allowed.get(target, 0)
                    else None,
                    fallback=_rounding_term(statement, target, signed),
                )

                if choice is not None:
                    break

            if choice is None:
                break

            tag, new_value, source = choice
            by_tag[tag].values[date] = new_value
            by_tag[tag].sources[date] = source
            settled.add(tag)
            _apply_hierarchical_articulation(rows, {date})


def identity_diagnostics(
    rows: list[RowResult],
    statement: str,
    dates: Iterable[str],
) -> list[ValidationWarning]:
    """Return a warning for each of the statement's IDENTITIES that does not hold at a date."""
    by_tag = {r.tag: r for r in rows}
    children: dict[str, list[RowResult]] = {}
    warnings: list[ValidationWarning] = []

    for r in rows:
        if r.parent:
            children.setdefault(r.parent, []).append(r)

    for date in sorted(dates):
        for target, terms in IDENTITIES.get(statement, ()):
            signed = _identity(target, terms, by_tag, children, date)

            if signed is None:
                continue

            lhs, rhs, tol = _identity_state(target, signed, by_tag, date)

            if abs(lhs - rhs) > tol:
                formula = _expression(signed)
                warnings.append(
                    ValidationWarning(
                        date=date,
                        tag=target,
                        expected=rhs,
                        actual=lhs,
                        formula=formula,
                        identity=f"{target} = {formula}",
                    )
                )

    return warnings
