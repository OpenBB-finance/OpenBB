"""Portfolio optimizer v2 with liquidity and risk constraints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.optimize import minimize


@dataclass
class PortfolioOptimizationResult:
    """Optimizer output bundle."""

    weights: np.ndarray
    cash_weight: float
    binding_constraints: list[str]
    constraint_violations: list[dict[str, Any]]
    liquidity_clip_ratio: float
    risk_contribution_max: float
    sector_exposure: dict[str, float]
    country_exposure: dict[str, float]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    if np.isnan(out) or np.isinf(out):
        return default
    return out


def _projected_fallback(
    mu: np.ndarray,
    ub: np.ndarray,
    sectors: list[str],
    countries: list[str],
    sector_cap: float,
    country_cap: float,
) -> np.ndarray:
    order = np.argsort(-mu)
    out = np.zeros_like(mu, dtype=float)
    sec_used: dict[str, float] = {}
    cty_used: dict[str, float] = {}
    for idx in order:
        cap_i = float(max(0.0, ub[idx]))
        if cap_i <= 0:
            continue
        sec = sectors[idx]
        cty = countries[idx]
        sec_room = max(0.0, sector_cap - sec_used.get(sec, 0.0))
        cty_room = max(0.0, country_cap - cty_used.get(cty, 0.0))
        total_room = max(0.0, 1.0 - float(out.sum()))
        alloc = min(cap_i, sec_room, cty_room, total_room)
        if alloc <= 0:
            continue
        out[idx] = alloc
        sec_used[sec] = sec_used.get(sec, 0.0) + alloc
        cty_used[cty] = cty_used.get(cty, 0.0) + alloc
        if float(out.sum()) >= 1.0 - 1e-9:
            break
    return out


def _risk_contributions(weights: np.ndarray, cov: np.ndarray, epsilon: float) -> np.ndarray:
    port_vol = float(np.sqrt(max(float(weights @ cov @ weights), epsilon)))
    marginal = cov @ weights
    rc = weights * marginal / max(port_vol, epsilon)
    return np.nan_to_num(rc, nan=0.0, posinf=0.0, neginf=0.0)


def optimize_weights_v2(
    *,
    mu: np.ndarray,
    cov: np.ndarray,
    symbols: list[str],
    metadata_by_symbol: dict[str, dict[str, Any]],
    risk_aversion: float,
    requested_max_weight: float,
    policy: dict[str, Any],
    nav: float = 1.0,
) -> PortfolioOptimizationResult:
    """Solve constrained long-only optimization with cash buffer."""
    n = len(symbols)
    if n == 0:
        return PortfolioOptimizationResult(
            weights=np.array([], dtype=float),
            cash_weight=1.0,
            binding_constraints=["no_symbols"],
            constraint_violations=[],
            liquidity_clip_ratio=0.0,
            risk_contribution_max=0.0,
            sector_exposure={},
            country_exposure={},
        )

    p_cfg = policy.get("portfolio_constraints", {}) if isinstance(policy, dict) else {}
    l_cfg = policy.get("liquidity_constraints", {}) if isinstance(policy, dict) else {}
    r_cfg = policy.get("risk_constraints", {}) if isinstance(policy, dict) else {}
    max_per_stock = min(
        _safe_float(requested_max_weight, 0.04),
        _safe_float(p_cfg.get("max_weight_per_stock"), 0.04),
    )
    sector_cap = _safe_float(p_cfg.get("sector_cap"), 0.25)
    country_cap = _safe_float(p_cfg.get("country_cap"), 0.35)
    adv_participation = _safe_float(l_cfg.get("max_adv_participation"), 0.05)
    max_rc = _safe_float(r_cfg.get("max_risk_contribution_per_stock"), 0.05)
    epsilon = _safe_float(r_cfg.get("epsilon"), 1e-9)
    nav = max(_safe_float(nav, 1.0), 1e-9)

    sectors: list[str] = []
    countries: list[str] = []
    ub = np.zeros(n, dtype=float)
    clipped_by_liquidity = 0
    for idx, symbol in enumerate(symbols):
        meta = metadata_by_symbol.get(symbol, {})
        sector = str(meta.get("sector_l1", "other")).strip() or "other"
        country = str(meta.get("country", "US")).strip().upper() or "US"
        adv20 = max(_safe_float(meta.get("adv20_usd"), 0.0), 0.0)
        liq_cap = (adv_participation * adv20) / nav if adv20 > 0 else max_per_stock
        ub_i = min(max_per_stock, max(0.0, liq_cap))
        if ub_i < max_per_stock - 1e-12:
            clipped_by_liquidity += 1
        sectors.append(sector)
        countries.append(country)
        ub[idx] = ub_i

    if float(ub.sum()) <= 0:
        return PortfolioOptimizationResult(
            weights=np.zeros(n, dtype=float),
            cash_weight=1.0,
            binding_constraints=["liquidity_adv20"],
            constraint_violations=[{"type": "no_feasible_weight_budget", "value": 1.0}],
            liquidity_clip_ratio=1.0,
            risk_contribution_max=0.0,
            sector_exposure={},
            country_exposure={},
        )

    bounds = [(0.0, float(ub_i)) for ub_i in ub]
    positive_mu = np.maximum(mu, 0.0)
    if float(positive_mu.sum()) > 0:
        initial = positive_mu / float(positive_mu.sum())
    else:
        initial = np.repeat(1.0 / n, n)
    initial = np.minimum(initial, ub)
    if float(initial.sum()) > 1.0:
        initial = initial / float(initial.sum())

    sector_index: dict[str, list[int]] = {}
    country_index: dict[str, list[int]] = {}
    for idx, sector in enumerate(sectors):
        sector_index.setdefault(sector, []).append(idx)
    for idx, country in enumerate(countries):
        country_index.setdefault(country, []).append(idx)

    def objective(weights: np.ndarray) -> float:
        ret = float(np.dot(mu, weights))
        risk = float(weights @ cov @ weights)
        return -(ret - float(risk_aversion) * risk)

    constraints: list[dict[str, Any]] = [{"type": "ineq", "fun": lambda w: float(1.0 - np.sum(w))}]
    for idxs in sector_index.values():
        constraints.append(
            {
                "type": "ineq",
                "fun": lambda w, i=idxs: float(sector_cap - np.sum(w[i])),
            }
        )
    for idxs in country_index.values():
        constraints.append(
            {
                "type": "ineq",
                "fun": lambda w, i=idxs: float(country_cap - np.sum(w[i])),
            }
        )
    for i in range(n):
        constraints.append(
            {
                "type": "ineq",
                "fun": lambda w, idx=i: float(
                    max_rc - _risk_contributions(w, cov, epsilon)[idx]
                ),
            }
        )

    solved = minimize(
        objective,
        initial,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 400, "ftol": 1e-8},
    )

    if solved.success:
        weights = np.clip(solved.x, 0.0, ub)
        if float(weights.sum()) > 1.0:
            weights = weights / float(weights.sum())
    else:
        weights = _projected_fallback(mu, ub, sectors, countries, sector_cap, country_cap)

    weights = np.clip(weights, 0.0, ub)
    if float(weights.sum()) > 1.0:
        weights = weights / float(weights.sum())
    cash_weight = float(max(0.0, 1.0 - float(weights.sum())))

    sector_exposure = {
        sector: float(np.sum(weights[idxs])) for sector, idxs in sector_index.items()
    }
    country_exposure = {
        country: float(np.sum(weights[idxs])) for country, idxs in country_index.items()
    }
    rc = _risk_contributions(weights, cov, epsilon)
    risk_contribution_max = float(np.max(rc)) if rc.size else 0.0

    violations: list[dict[str, Any]] = []
    if any(float(val) > max_per_stock + 1e-4 for val in weights):
        violations.append({"type": "single_name_cap", "threshold": max_per_stock})
    for sector, exposure in sector_exposure.items():
        if exposure > sector_cap + 1e-4:
            violations.append(
                {"type": "sector_cap", "sector": sector, "threshold": sector_cap, "value": exposure}
            )
    for country, exposure in country_exposure.items():
        if exposure > country_cap + 1e-4:
            violations.append(
                {
                    "type": "country_cap",
                    "country": country,
                    "threshold": country_cap,
                    "value": exposure,
                }
            )
    if risk_contribution_max > max_rc + 1e-4:
        violations.append(
            {"type": "risk_contribution_cap", "threshold": max_rc, "value": risk_contribution_max}
        )

    binding: list[str] = []
    if clipped_by_liquidity > 0:
        binding.append("liquidity_adv20")
    if any(abs(float(val) - max_per_stock) <= 1e-3 for val in weights if val > 0):
        binding.append("single_name_cap")
    if any(abs(exposure - sector_cap) <= 1e-3 for exposure in sector_exposure.values()):
        binding.append("sector_cap")
    if any(abs(exposure - country_cap) <= 1e-3 for exposure in country_exposure.values()):
        binding.append("country_cap")
    if abs(risk_contribution_max - max_rc) <= 1e-3:
        binding.append("risk_contribution_cap")
    if cash_weight > 1e-6:
        binding.append("cash_buffer")

    return PortfolioOptimizationResult(
        weights=weights,
        cash_weight=cash_weight,
        binding_constraints=sorted(set(binding)),
        constraint_violations=violations,
        liquidity_clip_ratio=float(clipped_by_liquidity / max(n, 1)),
        risk_contribution_max=risk_contribution_max,
        sector_exposure=sector_exposure,
        country_exposure=country_exposure,
    )
