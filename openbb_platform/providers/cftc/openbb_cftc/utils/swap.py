"""Fixed-rate swap valuation against a bootstrapped DTCC rate curve."""

from collections.abc import Callable, Iterable
from datetime import (
    date as dateType,
    timedelta,
)

from openbb_cftc.utils.dtcc import qualified_keys

_BUS_252_BASIS = 252.0
_ONE_ONE_BASIS = -1.0


def _leg_day_count_basis(code: str | None, default: str) -> float | None:
    """Resolve one leg's reported day count, honouring BUS/252 and 1/1 first."""
    from openbb_cftc.utils.constants import day_count_basis

    reported = (code or "").strip()

    if not reported:
        return None

    if reported == "A018":
        return _BUS_252_BASIS

    if reported == "A020":
        return _ONE_ONE_BASIS

    return day_count_basis(reported, default)


def _year_fraction(begin: dateType, finish: dateType, basis: float) -> float:
    """Return a period's accrued fraction of a year, honouring non-divisor bases."""
    if basis == _ONE_ONE_BASIS:
        return 1.0

    if basis == _BUS_252_BASIS:
        from openbb_cftc.utils.br_calendar import brl_business_days_between

        return brl_business_days_between(begin, finish) / _BUS_252_BASIS

    return (finish - begin).days / basis


def _discount_curve(
    records: Iterable[dict], currency: str, trade_date: dateType, min_trades: int
) -> tuple[Callable[[float], float], float, int]:
    """Return the currency's discount function, fixed-leg accrual basis and coupon period."""
    from openbb_cftc.utils.curve import curve_day_count_basis, curve_payment_period
    from openbb_cftc.utils.fx_vol import rate_discount_factor

    discount = rate_discount_factor(records, currency, trade_date, min_trades)
    basis = curve_day_count_basis(records, currency, trade_date, min_trades)
    period = curve_payment_period(records, currency, trade_date, min_trades)

    return discount, basis, period


def parse_leg_schedule(
    record: dict, leg: str
) -> list[tuple[dateType, dateType, float]] | None:
    """Return a leg's reported accrual periods as, or None."""
    from openbb_cftc.utils.curve import parse_date, parse_notional

    starts = (
        record.get(f"Effective date of the notional amount-Leg {leg}") or ""
    ).strip()
    ends = (record.get(f"End date of the notional amount-Leg {leg}") or "").strip()
    amounts = (
        record.get(f"Notional amount in effect on associated effective date-Leg {leg}")
        or ""
    ).strip()

    if not (starts and ends and amounts):
        return None

    opened = [parse_date(value) for value in starts.split(";")]
    closed = [parse_date(value) for value in ends.split(";")]
    sizes = [parse_notional(value)[0] for value in amounts.split(";")]

    if not len(opened) == len(closed) == len(sizes):
        return None

    periods = [
        (begin, finish, size)
        for begin, finish, size in zip(opened, closed, sizes)
        if begin and finish and size and finish > begin
    ]

    return sorted(periods) or None


def _advance(when: dateType, unit: str, count: int) -> dateType:
    """Advance a date by a reported calendar frequency."""
    if unit in ("YEAR", "MNTH"):
        import calendar

        months = when.month - 1 + count * (12 if unit == "YEAR" else 1)
        year = when.year + months // 12
        month = months % 12 + 1
        day = min(when.day, calendar.monthrange(year, month)[1])

        return dateType(year, month, day)

    if unit == "WEEK":
        return when + timedelta(weeks=count)

    return when + timedelta(days=count)


def leg_periods(
    curve_date: dateType,
    effective: dateType,
    expiration: dateType,
    notional: float,
    basis: float,
    frequency: tuple[str, int] | None,
    fallback_period_days: int,
    schedule: list[tuple[dateType, dateType, float]] | None = None,
) -> list[dict]:
    """Return one leg's accrual periods, on the terms the trade reported for it."""
    from openbb_cftc.utils.curve import _payment_offsets

    periods: list[dict] = []

    def add(begin: dateType, finish: dateType, size: float) -> None:
        if finish <= curve_date:
            return

        elapsed = 0.0

        if begin < curve_date:
            elapsed = _year_fraction(begin, curve_date, basis)
            begin = curve_date

        periods.append(
            {
                "start_days": (begin - curve_date).days,
                "end_days": (finish - curve_date).days,
                "year_fraction": _year_fraction(begin, finish, basis),
                "elapsed_year_fraction": elapsed,
                "notional": size,
            }
        )

    def roll(start: dateType, size: float) -> None:
        if frequency is not None and frequency[0] == "EXPI":
            add(start, expiration, size)
            return

        if frequency is not None:
            current = start

            while current < expiration:
                finish = min(_advance(current, *frequency), expiration)
                add(current, finish, size)
                current = finish

            return

        previous = 0

        for offset in _payment_offsets((expiration - start).days, fallback_period_days):
            add(
                start + timedelta(days=previous),
                start + timedelta(days=offset),
                size,
            )
            previous = offset

    if schedule:
        for begin, finish, size in schedule:
            add(begin, finish, size)

        if schedule[-1][1] < expiration:
            roll(schedule[-1][1], schedule[-1][2])
    else:
        roll(effective, notional)

    return periods


def classify_fixed_vs_float(record: dict, currency: str, today: dateType) -> str | None:
    """'spot' or 'forward': a single-currency fixed-vs-floating swap in a recognized."""
    from openbb_cftc.utils.constants import rate_curve_fisns
    from openbb_cftc.utils.curve import parse_date

    fisn = (record.get("UPI FISN") or "").strip()

    if fisn not in set(rate_curve_fisns(currency)):
        return None

    effective = parse_date(record.get("Effective Date"))

    if effective is None:
        return None

    return "forward" if effective > today else "spot"


def classify_float_float(record: dict, currency: str) -> str | None:
    """'basis' or 'cross_currency': a genuine."""
    currency_2 = (record.get("Notional currency-Leg 2") or "").strip()

    if not currency or not currency_2:
        return None

    fisn = (record.get("UPI FISN") or "").strip()

    if not fisn.startswith("NA/Swap Flt Flt"):
        return None

    return "cross_currency" if currency != currency_2 else "basis"


def classify_rates_swap(record: dict, today: dateType) -> str | None:
    """Classify a rates-asset-class print into one of five trade-type families, or."""
    from openbb_cftc.utils.curve import parse_date, parse_rate

    if (record.get("Action type") or "").strip() != "NEWT":
        return None

    if (record.get("Event type") or "").strip() != "TRAD":
        return None

    expiration = parse_date(record.get("Expiration Date"))

    if expiration is None or expiration <= today:
        return None

    currency = (record.get("Notional currency-Leg 1") or "").strip()

    if parse_rate(record) is None:
        return classify_float_float(record, currency)

    if (record.get("UPI FISN") or "").strip().startswith("NA/Swap Infl Idx"):
        return "inflation"

    return classify_fixed_vs_float(record, currency, today)


def parse_spread(record: dict) -> tuple[int, float] | None:
    """Return the carrying a real, nonzero spread, or None if neither."""
    for leg in (1, 2):
        text = (record.get(f"Spread-Leg {leg}") or "").strip()

        if not text:
            continue

        try:
            spread = float(text)
        except ValueError:
            continue

        if spread:
            return leg, spread

    return None


def indices_for_spread_underlier(
    underlier: str | None,
) -> tuple[str | None, str | None]:
    """Return the fixing indices a basis/cross-currency underlier."""
    from openbb_cftc.utils.fixings import index_for_underlier

    parts = (underlier or "").split(" vs ")

    if len(parts) != 2:
        return None, None

    return index_for_underlier(parts[0]), index_for_underlier(parts[1])


def parse_other_payments(record: dict) -> list[dict]:
    """Return a print's disseminated other payments, one per semicolon-joined entry."""
    types = [t.strip() for t in (record.get("Other payment type") or "").split(";")]
    amounts = [a.strip() for a in (record.get("Other payment amount") or "").split(";")]
    currencies = [
        c.strip() for c in (record.get("Other payment currency") or "").split(";")
    ]
    payments: list[dict] = []

    for index, kind in enumerate(types):
        if not kind:
            continue

        raw = amounts[index] if index < len(amounts) else ""

        try:
            amount = float(raw.replace(",", ""))
        except ValueError:
            continue

        payments.append(
            {
                "type": kind,
                "amount": amount,
                "currency": (currencies[index] if index < len(currencies) else "")
                or None,
            }
        )

    return payments


def parse_package_price(record: dict) -> dict | None:
    """Return a package print's monetary package price, or None when not disseminated."""
    if (record.get("Package transaction price notation") or "").strip() != "1":
        return None

    raw = (record.get("Package transaction price") or "").strip().replace(",", "")

    try:
        amount = float(raw)
    except ValueError:
        return None

    return {
        "amount": amount,
        "currency": (record.get("Package transaction price currency") or "").strip()
        or None,
    }


def extract_inflation_trade(
    record: dict, curve_date: dateType, min_notional: float = 0.0
) -> dict | None:
    """Return one zero-coupon inflation print's own priceable terms, or None."""
    from openbb_cftc.utils.curve import parse_date, parse_notional, parse_rate
    from openbb_cftc.utils.inflation import index_for_inflation_underlier

    if classify_rates_swap(record, curve_date) != "inflation":
        return None

    rate = parse_rate(record)
    effective = parse_date(record.get("Effective Date"))
    expiration = parse_date(record.get("Expiration Date"))

    if rate is None or effective is None or expiration is None:
        return None

    maturity_days = (expiration - effective).days

    if maturity_days <= 0:
        return None

    notional, capped = parse_notional(record.get("Notional amount-Leg 1"))

    if not notional or notional < min_notional:
        return None

    underlier = (record.get("UPI Underlier Name") or "").strip() or None

    return {
        "dissemination_identifier": (
            record.get("Dissemination Identifier") or ""
        ).strip(),
        "trade_key": qualified_keys(record).get("Trade Key"),
        "upi_fisn": (record.get("UPI FISN") or "").strip(),
        "underlier": underlier,
        "index": index_for_inflation_underlier(underlier),
        "trade_type": "inflation",
        "currency": (record.get("Notional currency-Leg 1") or "").strip(),
        "traded_breakeven": rate,
        "effective_date": effective,
        "expiration_date": expiration,
        "start_days": (effective - curve_date).days,
        "maturity_days": maturity_days,
        "notional": notional,
        "is_capped": capped,
        "cleared": (record.get("Cleared") or "").strip().upper() or None,
        "other_payments": parse_other_payments(record),
        "package_indicator": (record.get("Package indicator") or "").strip().upper()
        == "TRUE",
        "package_price": parse_package_price(record),
    }


def extract_spread_trade(
    record: dict, curve_date: dateType, min_notional: float = 0.0
) -> dict | None:
    """Return one basis/cross-currency print's own priceable terms, or None."""
    from openbb_cftc.utils.curve import parse_date, parse_frequency, parse_notional

    trade_type = classify_rates_swap(record, curve_date)

    if trade_type not in ("basis", "cross_currency"):
        return None

    spread = parse_spread(record)

    if spread is None:
        return None

    leg, traded_spread = spread
    other_leg = 2 if leg == 1 else 1
    currency = (record.get(f"Notional currency-Leg {leg}") or "").strip()
    other_currency = (record.get(f"Notional currency-Leg {other_leg}") or "").strip()
    notional, capped = parse_notional(record.get(f"Notional amount-Leg {leg}"))
    other_notional, other_capped = parse_notional(
        record.get(f"Notional amount-Leg {other_leg}")
    )
    effective = parse_date(record.get("Effective Date"))
    expiration = parse_date(record.get("Expiration Date"))

    if effective is None or expiration is None:
        return None

    maturity_days = (expiration - effective).days

    if maturity_days <= 0:
        return None

    if not notional or notional < min_notional:
        return None

    if trade_type == "cross_currency" and (
        capped or other_capped or other_notional is None or other_notional <= 0
    ):
        return None

    underlier = (record.get("UPI Underlier Name") or "").strip() or None
    leg_1_index, leg_2_index = indices_for_spread_underlier(underlier)
    spread_index = leg_1_index if leg == 1 else leg_2_index
    other_index = leg_2_index if leg == 1 else leg_1_index

    def leg_basis(field_leg: int) -> float | None:
        return _leg_day_count_basis(
            record.get(f"Floating rate day count convention-leg {field_leg}"), "A004"
        )

    def leg_frequency(field_leg: int) -> tuple[str, int] | None:
        return parse_frequency(
            record.get(f"Floating rate payment frequency period-Leg {field_leg}"),
            record.get(
                f"Floating rate payment frequency period multiplier-Leg {field_leg}"
            ),
        )

    return {
        "dissemination_identifier": (
            record.get("Dissemination Identifier") or ""
        ).strip(),
        "trade_key": qualified_keys(record).get("Trade Key"),
        "upi_fisn": (record.get("UPI FISN") or "").strip(),
        "underlier": underlier,
        "trade_type": trade_type,
        "currency": currency,
        "spread_leg": leg,
        "traded_spread": traded_spread,
        "spread_index": spread_index,
        "effective_date": effective,
        "expiration_date": expiration,
        "start_days": (effective - curve_date).days,
        "maturity_days": maturity_days,
        "notional": notional,
        "is_capped": capped,
        "cleared": (record.get("Cleared") or "").strip().upper() or None,
        "basis": leg_basis(leg),
        "frequency": leg_frequency(leg),
        "other_currency": other_currency,
        "other_notional": other_notional,
        "other_index": other_index,
        "other_basis": leg_basis(other_leg),
        "other_frequency": leg_frequency(other_leg),
        "other_payments": parse_other_payments(record),
        "package_indicator": (record.get("Package indicator") or "").strip().upper()
        == "TRUE",
        "package_price": parse_package_price(record),
    }


def reference_spread(
    records: Iterable[dict],
    underlier: str,
    trade_type: str,
    spread_leg: int,
    curve_date: dateType,
    min_trades: int = 1,
) -> tuple[float, int] | None:
    """Return the same-day median traded spread for this exact underlier and leg, and."""
    from statistics import median

    spreads = [
        parsed[1]
        for record in records
        if classify_rates_swap(record, curve_date) == trade_type
        and (record.get("UPI Underlier Name") or "").strip() == underlier
        and (parsed := parse_spread(record)) is not None
        and parsed[0] == spread_leg
    ]

    if len(spreads) < min_trades:
        return None

    return median(spreads), len(spreads)


def _price_spread(
    discount: Callable[[float], float],
    periods: list[dict],
    trade_date: dateType,
    reference_level: float,
    traded_spread: float,
    side: str,
) -> tuple[list[dict], dict]:
    """Price a basis/cross-currency swap's spread-bearing leg against a same-day."""
    from openbb_cftc.utils.constants import ZERO_RATE_BASIS

    annuity = 0.0
    schedule: list[dict] = []

    for index, period in enumerate(periods, start=1):
        factor = discount(period["end_days"] / ZERO_RATE_BASIS)
        annuity += period["notional"] * period["year_fraction"] * factor
        schedule.append(
            {
                "period": index,
                "start_date": trade_date + timedelta(days=period["start_days"]),
                "payment_date": trade_date + timedelta(days=period["end_days"]),
                "year_fraction": period["year_fraction"],
                "notional": period["notional"],
                "discount_factor": factor,
                "fixed_rate": traded_spread,
                "fixed_cashflow": period["notional"]
                * traded_spread
                * period["year_fraction"],
                "forward_rate": reference_level,
                "floating_rate": reference_level,
                "floating_notional": period["notional"],
                "floating_cashflow": period["notional"]
                * reference_level
                * period["year_fraction"],
            }
        )

    for row in schedule:
        row["fixed_pv"] = row["fixed_cashflow"] * row["discount_factor"]
        row["floating_pv"] = row["floating_cashflow"] * row["discount_factor"]

    sign = 1.0 if side == "pay" else -1.0
    fixed_leg_pv = traded_spread * annuity
    floating_leg_pv = reference_level * annuity
    npv = sign * (reference_level - traded_spread) * annuity

    summary = {
        "par_rate": reference_level,
        "annuity": annuity,
        "fixed_leg_pv": fixed_leg_pv,
        "floating_leg_pv": floating_leg_pv,
        "npv": npv,
        "dv01": annuity * 1e-4,
    }

    return schedule, summary


def value_spread_swap(
    records: Iterable[dict],
    trade: dict,
    curve_date: dateType,
    side: str = "pay",
    min_trades: int = 1,
) -> tuple[list[dict], dict]:
    """Value a same-currency basis swap's spread-bearing leg against a same-day."""
    from openbb_core.provider.utils.errors import EmptyDataError

    reference = reference_spread(
        records,
        trade["underlier"],
        trade["trade_type"],
        trade["spread_leg"],
        curve_date,
        min_trades,
    )

    if reference is None:
        raise EmptyDataError(
            f"Not enough same-day '{trade['underlier']}' prints to derive a"
            + f" reference spread on {curve_date} (need at least {min_trades})."
        )

    reference_level, num_trades = reference
    discount, curve_basis, curve_period = _discount_curve(
        records, trade["currency"], curve_date, min_trades
    )
    periods = leg_periods(
        curve_date,
        trade["effective_date"],
        trade["expiration_date"],
        trade["notional"],
        trade["basis"] or curve_basis,
        trade["frequency"],
        curve_period,
        None,
    )

    schedule, summary = _price_spread(
        discount, periods, curve_date, reference_level, trade["traded_spread"], side
    )
    summary["reference_trade_count"] = num_trades

    return schedule, summary


def _price_cross_currency(
    spread_discount: Callable[[float], float],
    other_discount: Callable[[float], float],
    spread_periods: list[dict],
    other_periods: list[dict],
    spread_notional: float,
    other_notional: float,
    *,
    spot: float,
    trade_date: dateType,
    traded_spread: float,
    side: str,
) -> tuple[list[dict], dict]:
    """Price a cross-currency swap by projecting and discounting each leg entirely on."""
    from openbb_cftc.utils.constants import ZERO_RATE_BASIS

    spread_annuity = 0.0
    spread_leg_pv = 0.0
    schedule: list[dict] = []

    for index, period in enumerate(spread_periods, start=1):
        opening = spread_discount(period["start_days"] / ZERO_RATE_BASIS)
        closing = spread_discount(period["end_days"] / ZERO_RATE_BASIS)
        year_fraction = period["year_fraction"]
        forward = (opening / closing - 1.0) / year_fraction

        spread_annuity += period["notional"] * year_fraction * closing
        spread_leg_pv += period["notional"] * forward * year_fraction * closing

        schedule.append(
            {
                "period": index,
                "start_date": trade_date + timedelta(days=period["start_days"]),
                "payment_date": trade_date + timedelta(days=period["end_days"]),
                "year_fraction": year_fraction,
                "notional": period["notional"],
                "discount_factor": closing,
            }
        )

    other_leg_pv_native = 0.0

    for period in other_periods:
        opening = other_discount(period["start_days"] / ZERO_RATE_BASIS)
        closing = other_discount(period["end_days"] / ZERO_RATE_BASIS)
        year_fraction = period["year_fraction"]
        forward = (opening / closing - 1.0) / year_fraction
        other_leg_pv_native += period["notional"] * forward * year_fraction * closing

    other_leg_pv = other_leg_pv_native * spot

    for row in schedule:
        row["fixed_rate"] = traded_spread
        row["fixed_cashflow"] = row["notional"] * traded_spread * row["year_fraction"]
        row["fixed_pv"] = row["fixed_cashflow"] * row["discount_factor"]

    maturity_years = spread_periods[-1]["end_days"] / ZERO_RATE_BASIS
    exchange_pv = other_notional * spot * other_discount(
        maturity_years
    ) - spread_notional * spread_discount(maturity_years)

    fixed_leg_pv = traded_spread * spread_annuity
    par_rate = (other_leg_pv - spread_leg_pv + exchange_pv) / spread_annuity
    sign = 1.0 if side == "pay" else -1.0
    npv = sign * (other_leg_pv - spread_leg_pv - fixed_leg_pv + exchange_pv)

    summary = {
        "par_rate": par_rate,
        "annuity": spread_annuity,
        "fixed_leg_pv": fixed_leg_pv,
        "floating_leg_pv": other_leg_pv,
        "exchange_pv": exchange_pv,
        "npv": npv,
        "dv01": spread_annuity * 1e-4,
    }

    return schedule, summary


def value_cross_currency_swap(
    records: Iterable[dict],
    trade: dict,
    curve_date: dateType,
    spot: float,
    side: str = "pay",
    min_trades: int = 1,
) -> tuple[list[dict], dict]:
    """Value a cross-currency swap's spread-bearing leg against the other leg's own."""
    spread_discount, spread_curve_basis, spread_curve_period = _discount_curve(
        records, trade["currency"], curve_date, min_trades
    )
    other_discount, other_curve_basis, other_curve_period = _discount_curve(
        records, trade["other_currency"], curve_date, min_trades
    )

    spread_periods = leg_periods(
        curve_date,
        trade["effective_date"],
        trade["expiration_date"],
        trade["notional"],
        trade["basis"] or spread_curve_basis,
        trade["frequency"],
        spread_curve_period,
        None,
    )
    other_periods = leg_periods(
        curve_date,
        trade["effective_date"],
        trade["expiration_date"],
        trade["other_notional"],
        trade["other_basis"] or other_curve_basis,
        trade["other_frequency"],
        other_curve_period,
        None,
    )

    return _price_cross_currency(
        spread_discount,
        other_discount,
        spread_periods,
        other_periods,
        trade["notional"],
        trade["other_notional"],
        spot=spot,
        trade_date=curve_date,
        traded_spread=trade["traded_spread"],
        side=side,
    )


def value_inflation_swap(
    records: Iterable[dict],
    trade: dict,
    curve_date: dateType,
    levels: dict[dateType, float] | None = None,
    side: str = "pay",
    min_trades: int = 1,
    breakeven_records: list[dict] | None = None,
    breakeven_date: dateType | None = None,
) -> tuple[list[dict], dict]:
    """Value a zero-coupon inflation swap off traded breakevens and its base index."""
    from openbb_core.provider.utils.errors import EmptyDataError

    from openbb_cftc.utils.inflation import (
        INFLATION_INDICES,
        breakeven_at,
        build_breakeven_curve,
        index_ratio,
    )

    currency = trade["currency"]
    discount, _, _ = _discount_curve(records, currency, curve_date, min_trades)
    curve = build_breakeven_curve(
        breakeven_records if breakeven_records is not None else records,
        currency,
        breakeven_date or curve_date,
        min_trades,
    )

    if not curve:
        raise EmptyDataError(
            f"No {currency} zero-coupon inflation prints were disseminated on"
            f" {breakeven_date or curve_date} to imply a breakeven."
        )

    effective = trade["effective_date"]
    expiration = trade["expiration_date"]
    total_years = (expiration - effective).days / 365.0
    remaining_years = max((expiration - curve_date).days, 0) / 365.0
    forward_breakeven = breakeven_at(curve, remaining_years or total_years)

    if forward_breakeven is None:
        raise EmptyDataError(
            f"The {currency} inflation curve on {curve_date} could not price a"
            f" {total_years:.2f}-year tenor."
        )

    spec = INFLATION_INDICES.get(trade["index"] or "") or {}
    realized_ratio = None
    realized_note = None

    if effective < curve_date:
        if not levels or not spec:
            realized_note = (
                "The elapsed index ratio needs the published index this trade"
                " references, which is not available."
            )
        else:
            realized_ratio = index_ratio(
                levels,
                effective,
                curve_date,
                spec["lag_months"],
                spec["interpolate"],
            )

            if realized_ratio is None:
                realized_note = (
                    "The published index does not yet cover this trade's base"
                    " reference month."
                )

    elapsed_years = max((curve_date - effective).days, 0) / 365.0
    projected_ratio = (1.0 + forward_breakeven) ** remaining_years

    if effective >= curve_date:
        index_ratio_total = (1.0 + forward_breakeven) ** total_years
        par_breakeven = forward_breakeven
    elif realized_ratio is not None:
        index_ratio_total = realized_ratio * projected_ratio
        par_breakeven = index_ratio_total ** (1.0 / total_years) - 1.0
    else:
        index_ratio_total = None
        par_breakeven = None

    notional = trade["notional"]
    traded = trade["traded_breakeven"]
    fixed_terminal = notional * ((1.0 + traded) ** total_years - 1.0)
    discount_factor = discount(remaining_years)

    if index_ratio_total is None:
        raise EmptyDataError(
            realized_note
            or f"'{trade['dissemination_identifier']}' has no priceable index ratio."
        )

    inflation_terminal = notional * (index_ratio_total - 1.0)
    net = (inflation_terminal - fixed_terminal) * discount_factor
    npv = net if side == "pay" else -net
    bumped = notional * ((1.0 + traded + 1e-4) ** total_years - 1.0) - notional * (
        (1.0 + traded) ** total_years - 1.0
    )

    schedule = [
        {
            "period": 1,
            "start_date": effective,
            "payment_date": expiration,
            "year_fraction": round(total_years, 6),
            "discount_factor": discount_factor,
            "index_ratio": round(index_ratio_total, 8),
            "realized_ratio": round(realized_ratio, 8)
            if realized_ratio is not None
            else None,
            "projected_ratio": round(projected_ratio, 8),
            "notional": notional,
            "fixed_rate": traded,
            "fixed_cashflow": round(fixed_terminal, 2),
            "fixed_pv": round(fixed_terminal * discount_factor, 2),
            "floating_cashflow": round(inflation_terminal, 2),
            "floating_pv": round(inflation_terminal * discount_factor, 2),
        }
    ]
    summary = {
        "par_rate": par_breakeven,
        "forward_breakeven": forward_breakeven,
        "index_ratio": index_ratio_total,
        "realized_ratio": realized_ratio,
        "projected_ratio": projected_ratio,
        "elapsed_years": elapsed_years,
        "remaining_years": remaining_years,
        "annuity": notional * total_years * discount_factor,
        "fixed_leg_pv": fixed_terminal * discount_factor,
        "floating_leg_pv": inflation_terminal * discount_factor,
        "npv": npv,
        "dv01": abs(bumped * discount_factor),
        "realized_note": realized_note,
        "reference_count": len(curve),
        "breakeven_date": breakeven_date or curve_date,
    }

    return schedule, summary


def spread_realized_carry(
    trade: dict,
    spread_fixings: dict[dateType, float],
    other_fixings: dict[dateType, float],
    valuation_date: dateType,
    curve_basis: float,
    curve_period: int,
) -> dict | None:
    """Return the carry a seasoned basis/cross-currency swap has already realized."""
    from openbb_cftc.utils.fixings import compound_fixings, fixing_basis

    base = trade["effective_date"]

    if base >= valuation_date:
        return {
            "spread_leg_settled": 0.0,
            "other_leg_settled": 0.0,
            "spread_leg_accrued": 0.0,
            "other_leg_accrued": 0.0,
        }

    def accrued(
        notional: float,
        basis: float | None,
        frequency: tuple[str, int] | None,
        fixings: dict[dateType, float],
        index_basis: float,
        spread: float = 0.0,
    ) -> tuple[float, float] | None:
        periods = leg_periods(
            base,
            base,
            trade["expiration_date"],
            notional,
            basis or curve_basis,
            frequency,
            curve_period,
            None,
        )
        settled = 0.0
        unsettled = 0.0

        for period in periods:
            starts = base + timedelta(days=period["start_days"])
            pays = base + timedelta(days=period["end_days"])
            ends = min(pays, valuation_date)

            if ends <= starts:
                continue

            accrual = compound_fixings(fixings, starts, ends, index_basis)

            if accrual is None:
                return None

            amount = period["notional"] * (
                accrual + spread * _year_fraction(starts, ends, index_basis)
            )

            if pays <= valuation_date:
                settled += amount
            else:
                unsettled += amount

        return settled, unsettled

    spread_accrued = accrued(
        trade["notional"],
        trade["basis"],
        trade["frequency"],
        spread_fixings,
        fixing_basis(trade["spread_index"]),
        trade["traded_spread"],
    )

    if spread_accrued is None:
        return None

    other_accrued = accrued(
        trade["other_notional"],
        trade["other_basis"],
        trade["other_frequency"],
        other_fixings,
        fixing_basis(trade["other_index"]),
    )

    if other_accrued is None:
        return None

    scale = (
        trade["notional"] / trade["other_notional"] if trade["other_notional"] else 1.0
    )

    return {
        "spread_leg_settled": spread_accrued[0],
        "other_leg_settled": other_accrued[0] * scale,
        "spread_leg_accrued": spread_accrued[1],
        "other_leg_accrued": other_accrued[1] * scale,
    }


def parse_trade_record(
    record: dict,
    curve_date: dateType,
    min_notional: float = 0.0,
    currency: str | None = None,
) -> dict | None:
    """Return one record's own priceable trade terms, or None if it fails a pricing gate."""
    from openbb_cftc.utils.constants import rate_curve_fisns
    from openbb_cftc.utils.curve import (
        is_vanilla_par,
        parse_date,
        parse_frequency,
        parse_notional,
        parse_rate,
    )

    record_currency = (record.get("Notional currency-Leg 1") or "").strip()

    if currency is not None and record_currency != currency:
        return None

    fisn = (record.get("UPI FISN") or "").strip()

    if fisn not in set(rate_curve_fisns(record_currency)):
        return None

    if (record.get("Action type") or "").strip() != "NEWT":
        return None

    if (record.get("Event type") or "").strip() != "TRAD":
        return None

    rate = parse_rate(record)
    effective = parse_date(record.get("Effective Date"))
    expiration = parse_date(record.get("Expiration Date"))
    notional, capped = parse_notional(record.get("Notional amount-Leg 1"))

    if rate is None or effective is None or expiration is None:
        return None

    start_days = (effective - curve_date).days
    maturity_days = (expiration - effective).days

    if maturity_days <= 0 or expiration <= curve_date:
        return None

    if not notional or notional < min_notional:
        return None

    def leg_basis(field: str) -> float | None:
        return _leg_day_count_basis(record.get(field), "A004")

    return {
        "dissemination_identifier": (
            record.get("Dissemination Identifier") or ""
        ).strip(),
        "trade_key": qualified_keys(record).get("Trade Key"),
        "upi_fisn": fisn,
        "underlier": (record.get("UPI Underlier Name") or "").strip() or None,
        "currency": record_currency,
        "fixed_rate": rate,
        "effective_date": effective,
        "expiration_date": expiration,
        "start_days": start_days,
        "maturity_days": maturity_days,
        "notional": notional,
        "is_capped": capped,
        "is_vanilla_par": is_vanilla_par(record),
        "cleared": (record.get("Cleared") or "").strip().upper() or None,
        "fixed_schedule": parse_leg_schedule(record, "1"),
        "floating_schedule": parse_leg_schedule(record, "2"),
        "fixed_frequency": parse_frequency(
            record.get("Fixed rate payment frequency period-Leg 1"),
            record.get("Fixed rate payment frequency period multiplier-Leg 1"),
        ),
        "floating_frequency": parse_frequency(
            record.get("Floating rate payment frequency period-Leg 2"),
            record.get("Floating rate payment frequency period multiplier-Leg 2"),
        ),
        "reset_frequency": parse_frequency(
            record.get("Floating rate reset frequency period-leg 2"),
            record.get("Floating rate reset frequency period multiplier-leg 2"),
        ),
        "fixed_basis": leg_basis("Fixed rate day count convention-leg 1"),
        "floating_basis": leg_basis("Floating rate day count convention-leg 2"),
        "other_payments": parse_other_payments(record),
        "package_indicator": (record.get("Package indicator") or "").strip().upper()
        == "TRUE",
        "package_price": parse_package_price(record),
    }


def extract_swap_trades(
    records: Iterable[dict],
    currency: str,
    curve_date: dateType,
    min_notional: float = 0.0,
) -> list[dict]:
    """Return the disseminated swaps of a currency that can be priced off its curve."""
    trades = [
        trade
        for record in records
        if (trade := parse_trade_record(record, curve_date, min_notional, currency))
        is not None
    ]
    trades.sort(key=lambda t: (-t["notional"], t["dissemination_identifier"]))

    return trades


def record_disseminated_day(record: dict) -> str | None:
    """Return the ISO day a cached raw record was disseminated."""
    stamp = (
        record.get("Dissemination Timestamp")
        or record.get("Execution Timestamp")
        or record.get("Event timestamp")
        or ""
    )

    return stamp[:10] or None


def find_trade(
    records: Iterable[dict],
    dissemination_identifier: str,
    curve_date: dateType,
    min_notional: float = 0.0,
) -> dict | None:
    """Return one named trade, parsed once straight off its own record."""
    target = (dissemination_identifier or "").strip()

    for record in records:
        candidate = (record.get("Dissemination Identifier") or "").strip()

        if candidate == target:
            return parse_trade_record(record, curve_date, min_notional)

    return None


def realized_carry(
    trade: dict,
    fixings: dict[dateType, float],
    valuation_date: dateType,
    curve_basis: float,
    curve_period: int,
) -> dict | None:
    """Return the carry a seasoned trade has already realized, from published fixings."""
    from openbb_cftc.utils.fixings import (
        compound_fixings,
        fixing_basis,
        index_for_underlier,
    )

    base = trade["effective_date"]
    index_basis = fixing_basis(index_for_underlier(trade["underlier"]))

    if base >= valuation_date:
        return {
            "floating_settled": 0.0,
            "fixed_settled": 0.0,
            "floating_accrued": 0.0,
            "fixed_accrued": 0.0,
        }

    floating_settled = 0.0
    floating_accrued = 0.0
    floating_periods = leg_periods(
        base,
        base,
        trade["expiration_date"],
        trade["notional"],
        trade["floating_basis"] or trade["fixed_basis"] or curve_basis,
        trade["floating_frequency"] or trade["fixed_frequency"],
        curve_period,
        trade["floating_schedule"] or trade["fixed_schedule"],
    )

    for period in floating_periods:
        starts = base + timedelta(days=period["start_days"])
        pays = base + timedelta(days=period["end_days"])
        ends = min(pays, valuation_date)

        if ends <= starts:
            continue

        accrual = compound_fixings(fixings, starts, ends, index_basis)

        if accrual is None:
            return None

        if pays <= valuation_date:
            floating_settled += period["notional"] * accrual
        else:
            floating_accrued += period["notional"] * accrual

    fixed_settled = 0.0
    fixed_accrued = 0.0
    fixed_basis = trade["fixed_basis"] or curve_basis
    fixed_periods = leg_periods(
        base,
        base,
        trade["expiration_date"],
        trade["notional"],
        fixed_basis,
        trade["fixed_frequency"],
        curve_period,
        trade["fixed_schedule"],
    )

    for period in fixed_periods:
        starts = base + timedelta(days=period["start_days"])
        pays = base + timedelta(days=period["end_days"])
        ends = min(pays, valuation_date)

        if ends > starts:
            amount = (
                period["notional"]
                * trade["fixed_rate"]
                * _year_fraction(starts, ends, fixed_basis)
            )

            if pays <= valuation_date:
                fixed_settled += amount
            else:
                fixed_accrued += amount

    return {
        "floating_settled": floating_settled,
        "fixed_settled": fixed_settled,
        "floating_accrued": floating_accrued,
        "fixed_accrued": fixed_accrued,
    }


def select_swap_trade(
    records: Iterable[dict],
    currency: str,
    curve_date: dateType,
    dissemination_identifier: str | None = None,
    min_notional: float = 0.0,
) -> dict:
    """Return one disseminated swap: the named print, or the day's largest par one."""
    from openbb_core.provider.utils.errors import EmptyDataError

    if dissemination_identifier is not None:
        trade = find_trade(records, dissemination_identifier, curve_date, min_notional)

        if trade is None:
            raise EmptyDataError(
                f"No {currency} swap on {curve_date} carries dissemination identifier"
                + f" '{dissemination_identifier}'."
            )

        return trade

    trades = extract_swap_trades(records, currency, curve_date, min_notional)

    if not trades:
        raise EmptyDataError(
            f"No priceable {currency} swap was disseminated on {curve_date}."
        )

    vanilla = [trade for trade in trades if trade["is_vanilla_par"]]

    if not vanilla:
        raise EmptyDataError(
            f"No standalone-par {currency} swap was disseminated on {curve_date}."
        )

    return vanilla[0]


def _price(
    discount: Callable[[float], float],
    fixed_periods: list[dict],
    floating_periods: list[dict],
    trade_date: dateType,
    fixed_rate: float | None,
    side: str,
    spread: float = 0.0,
) -> tuple[list[dict], dict]:
    """Price a fixed-vs-floating swap, each leg over its own accrual periods."""
    from openbb_cftc.utils.constants import ZERO_RATE_BASIS

    floating_leg_pv = 0.0
    floating_rows: list[dict] = []

    for period in floating_periods:
        opening = discount(period["start_days"] / ZERO_RATE_BASIS)
        factor = discount(period["end_days"] / ZERO_RATE_BASIS)
        year_fraction = period["year_fraction"]
        forward = (opening / factor - 1.0) / year_fraction
        floating = forward + spread
        cashflow = period["notional"] * floating * year_fraction
        floating_leg_pv += cashflow * factor
        floating_rows.append(
            {
                "start_days": period["start_days"],
                "end_days": period["end_days"],
                "year_fraction": year_fraction,
                "notional": period["notional"],
                "forward_rate": forward,
                "floating_rate": floating,
                "floating_cashflow": cashflow,
                "floating_pv": cashflow * factor,
            }
        )

    annuity = 0.0
    accrued_weight = 0.0
    schedule: list[dict] = []

    for index, period in enumerate(fixed_periods, start=1):
        factor = discount(period["end_days"] / ZERO_RATE_BASIS)
        annuity += period["notional"] * period["year_fraction"] * factor
        accrued_weight += period["notional"] * period.get("elapsed_year_fraction", 0.0)
        schedule.append(
            {
                "period": index,
                "start_date": trade_date + timedelta(days=period["start_days"]),
                "payment_date": trade_date + timedelta(days=period["end_days"]),
                "year_fraction": period["year_fraction"],
                "notional": period["notional"],
                "discount_factor": factor,
            }
        )

    par_rate = floating_leg_pv / annuity
    rate = par_rate if fixed_rate is None else fixed_rate

    for row, period in zip(schedule, fixed_periods):
        covering = [
            floating_row
            for floating_row in floating_rows
            if floating_row["start_days"] >= period["start_days"]
            and floating_row["end_days"] <= period["end_days"]
        ]

        if not covering:
            continue

        covering_year_fraction = sum(fr["year_fraction"] for fr in covering)
        row["forward_rate"] = (
            sum(fr["forward_rate"] * fr["year_fraction"] for fr in covering)
            / covering_year_fraction
        )
        row["floating_rate"] = (
            sum(fr["floating_rate"] * fr["year_fraction"] for fr in covering)
            / covering_year_fraction
        )
        row["floating_notional"] = covering[0]["notional"]
        row["floating_cashflow"] = sum(fr["floating_cashflow"] for fr in covering)
        row["floating_pv"] = sum(fr["floating_pv"] for fr in covering)

    for row in schedule:
        row["fixed_rate"] = rate
        row["fixed_cashflow"] = row["notional"] * rate * row["year_fraction"]
        row["fixed_pv"] = row["fixed_cashflow"] * row["discount_factor"]

    fixed_leg_pv = rate * annuity
    npv = (
        floating_leg_pv - fixed_leg_pv
        if side == "pay"
        else fixed_leg_pv - floating_leg_pv
    )

    summary = {
        "par_rate": par_rate,
        "annuity": annuity,
        "fixed_leg_pv": fixed_leg_pv,
        "floating_leg_pv": floating_leg_pv,
        "npv": npv,
        "dv01": annuity * 1e-4,
        "fixed_accrued": rate * accrued_weight,
    }

    return schedule, summary


def value_swap(
    records: Iterable[dict],
    currency: str,
    trade_date: dateType,
    maturity_days: int,
    *,
    fixed_rate: float | None = None,
    notional: float = 10_000_000.0,
    side: str = "pay",
    min_trades: int = 1,
    start_days: int = 0,
    spread: float = 0.0,
    fixed_schedule: list[tuple[dateType, dateType, float]] | None = None,
    floating_schedule: list[tuple[dateType, dateType, float]] | None = None,
    fixed_basis: float | None = None,
    floating_basis: float | None = None,
    fixed_frequency: tuple[str, int] | None = None,
    floating_frequency: tuple[str, int] | None = None,
) -> tuple[list[dict], dict]:
    """Value a single-currency fixed-vs-floating swap against the currency's rate curve."""
    discount, curve_basis, curve_period = _discount_curve(
        records, currency, trade_date, min_trades
    )
    effective = trade_date + timedelta(days=start_days)
    expiration = effective + timedelta(days=maturity_days)
    fixed_periods = leg_periods(
        trade_date,
        effective,
        expiration,
        notional,
        fixed_basis or curve_basis,
        fixed_frequency,
        curve_period,
        fixed_schedule,
    )
    floating_periods = leg_periods(
        trade_date,
        effective,
        expiration,
        notional,
        floating_basis or fixed_basis or curve_basis,
        floating_frequency or fixed_frequency,
        curve_period,
        floating_schedule or fixed_schedule,
    )

    return _price(
        discount,
        fixed_periods,
        floating_periods,
        trade_date,
        fixed_rate,
        side,
        spread,
    )
