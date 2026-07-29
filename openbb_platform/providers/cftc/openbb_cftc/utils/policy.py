"""OIS forward policy-rate path from single-period forward-starting OIS."""

from collections.abc import Iterable
from datetime import date as dateType


def extract_forward_observations(
    records: Iterable[dict],
    fisn: str,
    currency: str,
    curve_date: dateType,
    min_forward_days: int = 5,
) -> list[dict]:
    """Reduce forward-starting new OIS trades to observations."""
    from openbb_cftc.utils.constants import MAX_CURVE_DAYS
    from openbb_cftc.utils.curve import (
        is_vanilla_par,
        parse_date,
        parse_notional,
        parse_rate,
        record_trade_date,
    )

    observations: list[dict] = []

    for record in records:
        if (record.get("UPI FISN") or "").strip() != fisn:
            continue

        if (record.get("Action type") or "").strip() != "NEWT":
            continue

        if (record.get("Event type") or "").strip() != "TRAD":
            continue

        if (record.get("Notional currency-Leg 1") or "").strip() != currency:
            continue

        if not is_vanilla_par(record):
            continue

        as_of = record_trade_date(record) or curve_date
        rate = parse_rate(record)
        effective = parse_date(record.get("Effective Date"))
        expiration = parse_date(record.get("Expiration Date"))

        if rate is None or effective is None or expiration is None:
            continue

        forward_days = (effective - curve_date).days

        if forward_days <= min_forward_days:
            continue

        tenor_days = (expiration - effective).days

        if not 0 < tenor_days <= MAX_CURVE_DAYS:
            continue

        notional, capped = parse_notional(record.get("Notional amount-Leg 1"))

        observations.append(
            {
                "forward_days": forward_days,
                "tenor_days": tenor_days,
                "rate": rate,
                "as_of_date": as_of,
                "effective_date": effective,
                "expiration_date": expiration,
                "notional": notional,
                "is_capped": capped,
                "day_count": (
                    record.get("Fixed rate day count convention-leg 1") or ""
                ).strip()
                or None,
            }
        )

    return observations


def build_policy_path(
    records: Iterable[dict],
    fisn: str,
    currency: str,
    curve_date: dateType,
    min_trades: int = 3,
    max_period_days: int = 55,
) -> list[dict]:
    """Build the policy-rate path: one node per forward start of single-period OIS."""
    from collections import defaultdict
    from statistics import median

    from openbb_core.provider.utils.errors import EmptyDataError

    from openbb_cftc.utils.curve import _percentile

    observations = [
        observation
        for observation in extract_forward_observations(
            records, fisn, currency, curve_date
        )
        if 0 < observation["tenor_days"] <= max_period_days
    ]

    if not observations:
        raise EmptyDataError(
            f"No single-period forward-starting {currency} OIS matching '{fisn}' was"
            + " disseminated in the window; the currency may trade no meeting-dated OIS."
        )

    groups: dict[dateType, list[dict]] = defaultdict(list)

    for observation in observations:
        groups[observation["effective_date"]].append(observation)

    nodes: list[dict] = []

    for effective, members in groups.items():
        if len(members) < min_trades:
            continue

        rates = sorted(member["rate"] for member in members)

        if len(rates) >= 5:
            low, high = _percentile(rates, 5), _percentile(rates, 95)
            rates = [rate for rate in rates if low <= rate <= high] or rates

        expirations = sorted(member["expiration_date"] for member in members)
        expiration = expirations[len(expirations) // 2]

        nodes.append(
            {
                "forward_days": (effective - curve_date).days,
                "tenor_days": (expiration - effective).days,
                "rate": median(rates),
                "min_rate": rates[0],
                "max_rate": rates[-1],
                "num_trades": len(members),
                "as_of_date": max(member["as_of_date"] for member in members),
                "start_date": effective,
                "end_date": expiration,
                "is_capped": any(member["is_capped"] for member in members),
            }
        )

    if not nodes:
        raise EmptyDataError(
            f"No forward start cleared min_trades (currently {min_trades})."
            + " Lower min_trades, or widen the window."
        )

    reference = max(node["as_of_date"] for node in nodes)

    for node in nodes:
        node["staleness_days"] = (reference - node["as_of_date"]).days

    nodes.sort(key=lambda node: node["start_date"])

    return nodes


def observed_forward_grid(
    records: Iterable[dict],
    fisn: str,
    currency: str,
    curve_date: dateType,
    *,
    forward_tenor_days: int,
    step_years: float,
    count: int | None,
    min_trades: int,
    spot_rate: float,
) -> list[dict]:
    """Forward par rates read from observed forward-starting swaps of the target tenor."""
    from collections import defaultdict
    from statistics import median

    from openbb_cftc.utils.curve import interpolate_monotone

    tolerance = max(7, round(forward_tenor_days * 0.1))
    buckets: dict[int, list[float]] = defaultdict(list)

    for observation in extract_forward_observations(
        records, fisn, currency, curve_date
    ):
        if abs(observation["tenor_days"] - forward_tenor_days) <= tolerance:
            buckets[round(observation["forward_days"] / 30.0)].append(
                observation["rate"]
            )

    observed: list[tuple[float, float, int]] = []

    for months in sorted(buckets):
        rates = buckets[months]

        if len(rates) >= min_trades:
            observed.append((months * 30.0 / 365.0, median(rates), len(rates)))

    if not observed:
        return []

    anchored = [(0.0, spot_rate)] + [
        (start, rate) for start, rate, _ in observed if start > 0.05
    ]
    anchored.sort()
    last_start = observed[-1][0]

    points: list[dict] = []
    index = 0

    while index * step_years <= last_start + 1e-9 and (count is None or index < count):
        start = index * step_years
        index += 1
        nearest = min(observed, key=lambda o: abs(o[0] - start))
        points.append(
            {
                "tenor_years": start,
                "tenor_days": round(start * 365.0),
                "forward_rate": interpolate_monotone(anchored, start),
                "forward_extrapolated": False,
                "num_trades": nearest[2],
            }
        )

    return points
