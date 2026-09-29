from math import exp

import pytest

from openbb_cftc.utils.fx_theory import (
    _sabr_alpha_from_atm,
    calibrate_sabr,
    cip_forward_rate,
    garman_kohlhagen,
    implied_vol,
    sabr_vol,
)

S, K, T, RD, RF = 1.10, 1.12, 0.5, 0.04, 0.02


def test_cip_forward_rate_matches_the_manual():
    forward = cip_forward_rate(1.0110, rate_quote=0.0152, rate_base=0.0297, days=365)

    assert (forward - 1.0110) * 10000 == pytest.approx(-144.3, abs=0.5)
    assert forward < 1.0110


def test_garman_kohlhagen_put_call_parity():
    call = garman_kohlhagen(S, K, T, RD, RF, 0.09, True)
    put = garman_kohlhagen(S, K, T, RD, RF, 0.09, False)

    assert call - put == pytest.approx(S * exp(-RF * T) - K * exp(-RD * T), abs=1e-12)


@pytest.mark.parametrize("vol", [0.05, 0.12, 0.25])
@pytest.mark.parametrize("is_call", [True, False])
def test_implied_vol_round_trips(vol, is_call):
    price = garman_kohlhagen(S, K, T, RD, RF, vol, is_call)

    assert implied_vol(price, S, K, T, RD, RF, is_call) == pytest.approx(vol, abs=1e-6)


def test_implied_vol_returns_none_below_intrinsic_and_at_zero_time():
    forward = S * exp((RD - RF) * T)
    intrinsic = exp(-RD * T) * (forward - 1.00)

    assert implied_vol(intrinsic - 0.01, S, 1.00, T, RD, RF, True) is None
    assert implied_vol(0.02, S, K, 0.0, RD, RF, True) is None


def test_implied_vol_recovers_the_out_of_the_money_wings():
    forward = S * exp((RD - RF) * T)

    for strike, is_call in ((1.30, True), (0.95, False)):
        assert abs(strike / forward - 1.0) > 0.12
        price = garman_kohlhagen(S, strike, T, RD, RF, 0.11, is_call)

        assert implied_vol(price, S, strike, T, RD, RF, is_call) == pytest.approx(
            0.11, abs=1e-6
        )


def test_implied_vol_returns_none_when_no_root_is_sensible():
    forward = S * exp((RD - RF) * T)
    absurd = garman_kohlhagen(S, forward, T, RD, RF, 6.0, True)

    assert implied_vol(absurd, S, forward, T, RD, RF, True) is None


def test_sabr_vol_reprices_the_atm_and_prices_a_skew():
    forward, alpha, nu = 1.10, 0.10, 1.5

    atm = sabr_vol(forward, forward, T, alpha, -0.3, nu)
    assert atm == pytest.approx(alpha, abs=0.02)

    down = sabr_vol(forward, 1.00, T, alpha, -0.3, nu)
    up = sabr_vol(forward, 1.20, T, alpha, -0.3, nu)
    assert down > up


def test_sabr_alpha_from_atm_is_infeasible_for_a_steep_negative_skew():
    assert _sabr_alpha_from_atm(0.08, 2.0, -0.9, 4.4) is None
    assert _sabr_alpha_from_atm(0.10, 1.0, 0.0, 0.5) == pytest.approx(0.10, abs=0.01)


def test_calibrate_sabr_recovers_a_seeded_smile():
    forward, alpha, rho, nu = 1.10, 0.09, -0.25, 1.2
    strikes = [1.00, 1.04, 1.07, forward, 1.13, 1.16, 1.20]
    points = [(k, sabr_vol(forward, k, T, alpha, rho, nu)) for k in strikes]

    fit = calibrate_sabr(forward, T, alpha, points)
    assert fit is not None
    fit_alpha, fit_rho, fit_nu = fit
    assert fit_rho < 0
    for strike, vol in points:
        assert sabr_vol(
            forward, strike, T, fit_alpha, fit_rho, fit_nu
        ) == pytest.approx(vol, abs=0.01)


def test_calibrate_sabr_returns_none_when_thin_or_one_sided():
    forward = 1.10
    too_few = [(1.05, 0.09), (1.10, 0.08), (1.15, 0.085)]
    one_sided = [(1.02, 0.09), (1.05, 0.085), (1.07, 0.08), (1.09, 0.078)]

    assert calibrate_sabr(forward, T, 0.08, too_few) is None
    assert calibrate_sabr(forward, T, 0.08, one_sided) is None


def test_calibrate_sabr_fits_a_long_tenor_over_infeasible_trials():
    forward, alpha, rho, nu = 1.10, 0.15, -0.2, 0.6
    strikes = [0.90, 0.98, 1.05, forward, 1.16, 1.24, 1.35]
    points = [(k, sabr_vol(forward, k, 5.0, alpha, rho, nu)) for k in strikes]

    fit = calibrate_sabr(forward, 5.0, alpha, points)
    assert fit is not None
    fit_alpha, fit_rho, _ = fit
    assert fit_alpha > 0 and fit_rho < 0
