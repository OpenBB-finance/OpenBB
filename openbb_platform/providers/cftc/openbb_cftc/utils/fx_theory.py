"""FX forward and option pricing math: CIP forwards, Garman-Kohlhagen, lognormal SABR."""

from math import erf, exp, log, sqrt


def _norm_cdf(x: float) -> float:
    """Evaluate the standard normal cumulative distribution function."""
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def cip_forward_rate(
    spot: float,
    rate_quote: float,
    rate_base: float,
    days: int,
    basis_quote: float = 360.0,
    basis_base: float = 360.0,
) -> float:
    """Covered-interest-parity forward rate for a quote-per-base pair. Rates are decimals."""
    return (
        spot
        * (1.0 + rate_quote * days / basis_quote)
        / (1.0 + rate_base * days / basis_base)
    )


def d1_d2(
    spot: float, strike: float, t: float, rate_dom: float, rate_for: float, vol: float
) -> tuple[float, float]:
    """Return the d1 and d2 terms of the Garman-Kohlhagen formula."""
    vol_t = vol * sqrt(t)
    first = (log(spot / strike) + (rate_dom - rate_for + 0.5 * vol * vol) * t) / vol_t

    return first, first - vol_t


def garman_kohlhagen(
    spot: float,
    strike: float,
    t: float,
    rate_dom: float,
    rate_for: float,
    vol: float,
    is_call: bool,
) -> float:
    """Garman-Kohlhagen price of a vanilla FX option, per unit of base-currency notional."""
    d1, d2 = d1_d2(spot, strike, t, rate_dom, rate_for, vol)
    disc_for = exp(-rate_for * t)
    disc_dom = exp(-rate_dom * t)

    if is_call:
        return spot * disc_for * _norm_cdf(d1) - strike * disc_dom * _norm_cdf(d2)

    return strike * disc_dom * _norm_cdf(-d2) - spot * disc_for * _norm_cdf(-d1)


_VOL_LOW = 1e-4
_VOL_HIGH = 5.0


def implied_vol(
    price: float,
    spot: float,
    strike: float,
    t: float,
    rate_dom: float,
    rate_for: float,
    is_call: bool,
) -> float | None:
    """Bisection implied volatility repricing a vanilla FX option to ``price``, or None."""
    if t <= 0.0:
        return None

    forward = spot * exp((rate_dom - rate_for) * t)
    disc_dom = exp(-rate_dom * t)
    intrinsic = disc_dom * max(
        (forward - strike) if is_call else (strike - forward), 0.0
    )

    if price <= intrinsic:
        return None

    low, high = _VOL_LOW, _VOL_HIGH

    if price >= garman_kohlhagen(spot, strike, t, rate_dom, rate_for, high, is_call):
        return None

    for _ in range(100):
        mid = 0.5 * (low + high)

        if garman_kohlhagen(spot, strike, t, rate_dom, rate_for, mid, is_call) < price:
            low = mid
        else:
            high = mid

    return 0.5 * (low + high)


def sabr_vol(
    forward: float, strike: float, t: float, alpha: float, rho: float, nu: float
) -> float:
    """Hagan lognormal-SABR implied volatility at a strike."""
    drift = (
        1.0 + (0.25 * rho * nu * alpha + (2.0 - 3.0 * rho * rho) / 24.0 * nu * nu) * t
    )

    if abs(forward - strike) < 1e-12:
        return alpha * drift

    log_fk = log(forward / strike)
    z = nu / alpha * log_fk
    x = log((sqrt(1.0 - 2.0 * rho * z + z * z) + z - rho) / (1.0 - rho))

    return alpha * (z / x) * drift


def _sabr_alpha_from_atm(
    atm_vol: float, t: float, rho: float, nu: float
) -> float | None:
    """SABR alpha repricing the at-the-money vol for."""
    a = 0.25 * rho * nu * t
    b = 1.0 + (2.0 - 3.0 * rho * rho) / 24.0 * nu * nu * t

    if abs(a) < 1e-12:
        return atm_vol / b if b > 0.0 else None

    disc = b * b + 4.0 * a * atm_vol

    if disc < 0.0:
        return None

    root = (-b + sqrt(disc)) / (2.0 * a)

    return root if root > 0.0 else None


def calibrate_sabr(
    forward: float, t: float, atm_vol: float, points: list[tuple[float, float]]
) -> tuple[float, float, float] | None:
    """Fit SABR to points, or None if thin or one-sided."""
    below = [s for s, _ in points if s < forward]
    above = [s for s, _ in points if s > forward]

    if len(points) < 4 or not below or not above:
        return None

    def evaluate(rho: float, nu: float) -> tuple[float, float, float, float]:
        alpha = _sabr_alpha_from_atm(atm_vol, t, rho, nu)

        if alpha is None:
            return float("inf"), 0.0, rho, nu

        total = 0.0

        for strike, vol in points:
            total += (sabr_vol(forward, strike, t, alpha, rho, nu) - vol) ** 2

        return total, alpha, rho, nu

    rho_grid = [i / 10.0 for i in range(-9, 10)]
    nu_grid = [0.05 + 0.15 * i for i in range(30)]
    _, _, rho, nu = min(evaluate(r, n) for r in rho_grid for n in nu_grid)

    fine_rho = [rho + 0.02 * i for i in range(-4, 5) if -0.99 < rho + 0.02 * i < 0.99]
    fine_nu = [nu + 0.03 * i for i in range(-4, 5) if nu + 0.03 * i > 0.01]
    _, alpha, rho, nu = min(evaluate(r, n) for r in fine_rho for n in fine_nu)

    return alpha, rho, nu
