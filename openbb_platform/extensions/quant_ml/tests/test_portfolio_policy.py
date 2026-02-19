"""Portfolio policy tests."""

from __future__ import annotations

from openbb_quant_ml.service.portfolio_policy import (
    apply_effective_max_weight,
    get_policy_max_weight_cap,
    get_portfolio_policy_response,
)


def test_policy_exposes_hard_cap():
    response = get_portfolio_policy_response()
    assert response.single_name_max_abs_weight == 0.10
    assert response.template == "diversified_long_only"
    assert response.small_universe_policy == "cash_buffer"


def test_apply_effective_max_weight_clamps_to_policy():
    cap = get_policy_max_weight_cap()
    assert cap == 0.10
    assert apply_effective_max_weight(0.2) == 0.10
    assert apply_effective_max_weight(0.05) == 0.05
