"""Portfolio optimizer v2 with liquidity, cost, and exposure constraints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.optimize import minimize

EPS = 1e-9


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
    estimated_cost: float = 0.0
    gross_exposure: float = 0.0
    net_exposure: float = 0.0
    portfolio_beta: float = 0.0


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    if np.isnan(out) or np.isinf(out):
        return default
    return out


def _safe_array(values: Any, size: int, default: float = 0.0) -> np.ndarray:
    try:
        arr = np.asarray(values, dtype=float).reshape(-1)
    except Exception:
        arr = np.array([], dtype=float)
    if arr.size != size:
        arr = np.full(size, default, dtype=float)
    return np.nan_to_num(arr, nan=default, posinf=default, neginf=default)


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


def _estimate_cost_from_delta(
    *,
    delta: np.ndarray,
    adv_capacity: np.ndarray,
    linear_rate: float,
    impact_k: float,
    turnover_penalty_mode: str,
    turnover_penalty: float,
) -> float:
    abs_delta = np.abs(delta)
    linear_tc = float(linear_rate * abs_delta.sum())
    impact_tc = float((impact_k / 1e4) * np.sum((delta**2) / np.clip(adv_capacity, EPS, None)))

    penalty = 0.0
    mode = str(turnover_penalty_mode or "none").strip().lower()
    if mode == "l1":
        penalty = float(turnover_penalty * abs_delta.sum())
    elif mode == "l2":
        penalty = float(turnover_penalty * np.sum(delta**2))

    return linear_tc + impact_tc + penalty


def _solve_cvar_with_cvxpy(
    *,
    mu: np.ndarray,
    lb: np.ndarray,
    ub: np.ndarray,
    current_weights: np.ndarray,
    linear_rate: float,
    impact_scale: np.ndarray,
    turnover_penalty_mode: str,
    turnover_penalty: float,
    sector_index: dict[str, list[int]],
    country_index: dict[str, list[int]],
    sector_cap: float,
    country_cap: float,
    gross_exposure_max: float,
    net_exposure_min: float,
    net_exposure_max: float,
    sector_neutral: bool,
    sector_target: float,
    sector_band: float,
    beta_vector: np.ndarray | None,
    beta_neutral: bool,
    beta_tolerance: float,
    target_beta: float,
    scenarios: np.ndarray,
    alpha: float,
    cvar_lambda: float,
) -> np.ndarray:
    import cvxpy as cp

    n_assets = len(mu)
    if n_assets == 0:
        return np.array([], dtype=float)
    if scenarios.ndim != 2 or scenarios.shape[1] != n_assets:
        raise ValueError("invalid_cvar_scenarios_shape")
    n_scenarios = int(scenarios.shape[0])
    if n_scenarios < 20:
        raise ValueError("insufficient_cvar_scenarios")

    w = cp.Variable(n_assets)
    t = cp.Variable()
    u = cp.Variable(n_scenarios)
    losses = -scenarios @ w
    delta = w - current_weights

    cost_term = float(linear_rate) * cp.norm1(delta) + cp.sum(cp.multiply(impact_scale, cp.square(delta)))

    turnover_term = 0
    mode = str(turnover_penalty_mode or "none").strip().lower()
    if mode == "l1":
        turnover_term = float(turnover_penalty) * cp.norm1(delta)
    elif mode == "l2":
        turnover_term = float(turnover_penalty) * cp.sum_squares(delta)

    objective = cp.Maximize(
        mu @ w
        - float(cvar_lambda) * (t + (1.0 / (float(alpha) * n_scenarios)) * cp.sum(u))
        - cost_term
        - turnover_term
    )

    constraints = [
        w >= lb,
        w <= ub,
        cp.norm1(w) <= float(gross_exposure_max),
        cp.sum(w) >= float(net_exposure_min),
        cp.sum(w) <= float(net_exposure_max),
        u >= 0.0,
        u >= losses - t,
    ]

    for idxs in sector_index.values():
        if sector_neutral:
            constraints.append(cp.abs(cp.sum(w[idxs]) - float(sector_target)) <= float(sector_band))
        else:
            constraints.append(cp.sum(w[idxs]) <= float(sector_cap))

    for idxs in country_index.values():
        constraints.append(cp.sum(w[idxs]) <= float(country_cap))

    if beta_neutral and beta_vector is not None and len(beta_vector) == n_assets:
        beta_expr = beta_vector @ w
        constraints.append(cp.abs(beta_expr - float(target_beta)) <= float(beta_tolerance))

    problem = cp.Problem(objective, constraints)
    solved = False
    for solver_name in ("ECOS", "OSQP", "SCS"):
        try:
            problem.solve(solver=solver_name, warm_start=True, verbose=False)
        except Exception:
            continue
        if w.value is not None:
            solved = True
            break

    if not solved or w.value is None:
        raise ValueError("cvar_solver_failed")

    weights = np.asarray(w.value, dtype=float).reshape(-1)
    weights = np.nan_to_num(weights, nan=0.0, posinf=0.0, neginf=0.0)
    return np.clip(weights, lb, ub)


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
    optimizer_mode: str = "mv",
    cvar_alpha: float = 0.05,
    cvar_lambda: float = 3.0,
    scenario_returns: np.ndarray | None = None,
    current_weights: np.ndarray | None = None,
    cost_params: dict[str, Any] | None = None,
    exposure_constraints: dict[str, Any] | None = None,
    beta_vector: np.ndarray | None = None,
    target_vol: float | None = None,
) -> PortfolioOptimizationResult:
    """Solve constrained optimization with optional CVaR, cost, and exposure controls."""
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
            estimated_cost=0.0,
            gross_exposure=0.0,
            net_exposure=0.0,
            portfolio_beta=0.0,
        )

    mu = _safe_array(mu, n, 0.0)
    cov = np.asarray(cov, dtype=float)
    if cov.shape != (n, n):
        cov = np.eye(n, dtype=float) * 1e-4
    cov = np.nan_to_num(cov, nan=0.0, posinf=0.0, neginf=0.0)
    cov = 0.5 * (cov + cov.T)
    cov = cov + np.eye(n, dtype=float) * 1e-8

    p_cfg = policy.get("portfolio_constraints", {}) if isinstance(policy, dict) else {}
    l_cfg = policy.get("liquidity_constraints", {}) if isinstance(policy, dict) else {}
    r_cfg = policy.get("risk_constraints", {}) if isinstance(policy, dict) else {}
    exp_cfg = exposure_constraints or {}
    cst_cfg = cost_params or {}

    max_per_stock = min(
        _safe_float(requested_max_weight, 0.04),
        _safe_float(p_cfg.get("max_weight_per_stock"), 0.04),
    )
    sector_cap = _safe_float(exp_cfg.get("sector_max_weight"), _safe_float(p_cfg.get("sector_cap"), 0.25))
    country_cap = _safe_float(p_cfg.get("country_cap"), 0.35)
    adv_participation = _safe_float(l_cfg.get("max_adv_participation"), 0.05)
    max_rc = _safe_float(r_cfg.get("max_risk_contribution_per_stock"), 0.05)
    epsilon = _safe_float(r_cfg.get("epsilon"), 1e-9)
    nav = max(_safe_float(nav, 1.0), 1e-9)

    allow_short = bool(exp_cfg.get("allow_short", _safe_float(exp_cfg.get("net_exposure_min"), 0.0) < -1e-9))
    gross_exposure_max = _safe_float(exp_cfg.get("gross_exposure_max"), _safe_float(p_cfg.get("gross_exposure_max"), 1.5))
    net_exposure_min = _safe_float(exp_cfg.get("net_exposure_min"), -0.2 if allow_short else 0.0)
    net_exposure_max = _safe_float(exp_cfg.get("net_exposure_max"), 1.0)
    sector_neutral = bool(exp_cfg.get("sector_neutral", False))
    beta_neutral = bool(exp_cfg.get("beta_neutral", False))
    beta_tolerance = _safe_float(exp_cfg.get("beta_tolerance"), 0.05)
    target_beta = _safe_float(exp_cfg.get("target_beta"), 0.0)

    commission_bps = _safe_float(cst_cfg.get("commission_bps"), 0.0)
    half_spread_bps = _safe_float(cst_cfg.get("half_spread_bps"), 0.0)
    impact_k = _safe_float(cst_cfg.get("impact_k"), 0.0)
    turnover_penalty_mode = str(cst_cfg.get("turnover_penalty_mode", "none")).strip().lower()
    turnover_penalty = _safe_float(cst_cfg.get("turnover_penalty"), 0.0)
    linear_rate = (commission_bps + half_spread_bps) / 1e4

    sectors: list[str] = []
    countries: list[str] = []
    ub = np.zeros(n, dtype=float)
    adv_capacity = np.full(n, 0.01, dtype=float)
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
        adv_capacity[idx] = max(liq_cap, 1e-6)

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
            estimated_cost=0.0,
            gross_exposure=0.0,
            net_exposure=0.0,
            portfolio_beta=0.0,
        )

    lb = -ub if allow_short else np.zeros(n, dtype=float)
    bounds = [(float(lb_i), float(ub_i)) for lb_i, ub_i in zip(lb, ub, strict=False)]

    current = _safe_array(current_weights, n, 0.0)
    current = np.clip(current, lb, ub)

    if float(np.abs(current).sum()) > gross_exposure_max + EPS:
        current *= float(gross_exposure_max / max(np.abs(current).sum(), EPS))

    if float(np.abs(mu).sum()) > EPS:
        if allow_short:
            initial = mu - float(np.mean(mu))
            scale = max(float(np.abs(initial).sum()), EPS)
            initial = initial / scale
            initial = initial * min(gross_exposure_max, 1.0)
        else:
            positive_mu = np.maximum(mu, 0.0)
            initial = positive_mu / max(float(positive_mu.sum()), 1.0)
    else:
        initial = current.copy()
        if float(np.abs(initial).sum()) <= EPS:
            initial = np.repeat(1.0 / n, n)

    initial = np.clip(initial, lb, ub)

    sector_index: dict[str, list[int]] = {}
    country_index: dict[str, list[int]] = {}
    for idx, sector in enumerate(sectors):
        sector_index.setdefault(sector, []).append(idx)
    for idx, country in enumerate(countries):
        country_index.setdefault(country, []).append(idx)

    n_sectors = max(len(sector_index), 1)
    sector_target = 0.0 if allow_short else (min(net_exposure_max, 1.0) / n_sectors)
    sector_band = max(0.01, min(sector_cap, 0.25))

    beta_arr = None
    if beta_vector is not None:
        beta_arr = _safe_array(beta_vector, n, 0.0)

    requested_mode = str(optimizer_mode or "mv").strip().lower()
    mode_used = "mv"
    used_cvar_fallback = False
    weights = np.array([], dtype=float)

    if requested_mode == "cvar":
        try:
            if scenario_returns is None:
                raise ValueError("missing_scenarios")
            scenarios = np.asarray(scenario_returns, dtype=float)
            scenarios = np.nan_to_num(scenarios, nan=0.0, posinf=0.0, neginf=0.0)
            if scenarios.ndim == 1:
                if n == 1:
                    scenarios = scenarios.reshape(-1, 1)
                else:
                    raise ValueError("invalid_scenario_rank")
            impact_scale = (impact_k / 1e4) / np.clip(adv_capacity, EPS, None)
            weights = _solve_cvar_with_cvxpy(
                mu=mu,
                lb=lb,
                ub=ub,
                current_weights=current,
                linear_rate=linear_rate,
                impact_scale=impact_scale,
                turnover_penalty_mode=turnover_penalty_mode,
                turnover_penalty=turnover_penalty,
                sector_index=sector_index,
                country_index=country_index,
                sector_cap=sector_cap,
                country_cap=country_cap,
                gross_exposure_max=gross_exposure_max,
                net_exposure_min=net_exposure_min,
                net_exposure_max=net_exposure_max,
                sector_neutral=sector_neutral,
                sector_target=sector_target,
                sector_band=sector_band,
                beta_vector=beta_arr,
                beta_neutral=beta_neutral,
                beta_tolerance=beta_tolerance,
                target_beta=target_beta,
                scenarios=scenarios,
                alpha=max(0.001, min(float(cvar_alpha), 0.2)),
                cvar_lambda=max(0.01, float(cvar_lambda)),
            )
            mode_used = "cvar"
        except Exception:
            used_cvar_fallback = True
            weights = np.array([], dtype=float)

    def objective(w: np.ndarray) -> float:
        ret = float(np.dot(mu, w))
        risk = float(w @ cov @ w)
        cost = _estimate_cost_from_delta(
            delta=w - current,
            adv_capacity=adv_capacity,
            linear_rate=linear_rate,
            impact_k=impact_k,
            turnover_penalty_mode=turnover_penalty_mode,
            turnover_penalty=turnover_penalty,
        )
        return -(ret - float(risk_aversion) * risk - cost)

    constraints: list[dict[str, Any]] = [
        {"type": "ineq", "fun": lambda w: float(gross_exposure_max - np.sum(np.abs(w)))},
        {"type": "ineq", "fun": lambda w: float(np.sum(w) - net_exposure_min)},
        {"type": "ineq", "fun": lambda w: float(net_exposure_max - np.sum(w))},
    ]

    if not allow_short:
        constraints.append({"type": "ineq", "fun": lambda w: float(1.0 - np.sum(w))})

    for idxs in sector_index.values():
        if sector_neutral:
            constraints.append(
                {
                    "type": "ineq",
                    "fun": lambda w, i=idxs: float(
                        sector_band - abs(float(np.sum(w[i])) - sector_target)
                    ),
                }
            )
        else:
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
                    max_rc - abs(_risk_contributions(w, cov, epsilon)[idx])
                ),
            }
        )

    if beta_neutral and beta_arr is not None:
        constraints.append(
            {
                "type": "ineq",
                "fun": lambda w: float(
                    beta_tolerance - abs(float(np.dot(beta_arr, w)) - target_beta)
                ),
            }
        )

    if weights.size == 0:
        solved = minimize(
            objective,
            initial,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 500, "ftol": 1e-9},
        )

        if solved.success:
            weights = np.asarray(solved.x, dtype=float)
        else:
            if allow_short:
                centered = mu - float(np.mean(mu))
                denom = max(float(np.sum(np.abs(centered))), EPS)
                fallback = centered / denom
                fallback = fallback * min(gross_exposure_max, 1.0)
                weights = np.clip(fallback, lb, ub)
            else:
                weights = _projected_fallback(mu, ub, sectors, countries, sector_cap, country_cap)
    else:
        solved = None

    weights = np.clip(weights, lb, ub)

    # Optional volatility targeting.
    target_vol = _safe_float(target_vol, 0.0)
    if target_vol > 0.0:
        ex_ante_vol = float(np.sqrt(max(float(weights @ cov @ weights), EPS)))
        if ex_ante_vol > EPS:
            scale = float(target_vol / ex_ante_vol)
            weights = weights * scale
            weights = np.clip(weights, lb, ub)

    gross_exposure = float(np.sum(np.abs(weights)))
    if gross_exposure > gross_exposure_max + EPS:
        weights *= float(gross_exposure_max / gross_exposure)
        gross_exposure = float(np.sum(np.abs(weights)))

    net_exposure = float(np.sum(weights))
    if net_exposure > net_exposure_max + EPS:
        scale = float(net_exposure_max / max(net_exposure, EPS))
        weights *= scale
    elif net_exposure < net_exposure_min - EPS and net_exposure < -EPS:
        scale = float(abs(net_exposure_min) / abs(net_exposure))
        weights *= scale

    weights = np.clip(weights, lb, ub)
    gross_exposure = float(np.sum(np.abs(weights)))
    net_exposure = float(np.sum(weights))

    cash_weight = float(max(0.0, 1.0 - net_exposure)) if not allow_short else float(max(0.0, 1.0 - gross_exposure))

    sector_exposure = {
        sector: float(np.sum(weights[idxs])) for sector, idxs in sector_index.items()
    }
    country_exposure = {
        country: float(np.sum(weights[idxs])) for country, idxs in country_index.items()
    }

    rc = _risk_contributions(weights, cov, epsilon)
    risk_contribution_max = float(np.max(np.abs(rc))) if rc.size else 0.0

    estimated_cost = _estimate_cost_from_delta(
        delta=weights - current,
        adv_capacity=adv_capacity,
        linear_rate=linear_rate,
        impact_k=impact_k,
        turnover_penalty_mode=turnover_penalty_mode,
        turnover_penalty=turnover_penalty,
    )

    portfolio_beta = float(np.dot(beta_arr, weights)) if beta_arr is not None else 0.0

    violations: list[dict[str, Any]] = []
    if any(float(abs(val)) > max_per_stock + 1e-4 for val in weights):
        violations.append({"type": "single_name_cap", "threshold": max_per_stock})
    if gross_exposure > gross_exposure_max + 1e-4:
        violations.append({"type": "gross_exposure", "threshold": gross_exposure_max, "value": gross_exposure})
    if net_exposure < net_exposure_min - 1e-4 or net_exposure > net_exposure_max + 1e-4:
        violations.append(
            {
                "type": "net_exposure",
                "threshold_min": net_exposure_min,
                "threshold_max": net_exposure_max,
                "value": net_exposure,
            }
        )
    for sector, exposure in sector_exposure.items():
        if (not sector_neutral and exposure > sector_cap + 1e-4) or (
            sector_neutral and abs(exposure - sector_target) > sector_band + 1e-4
        ):
            violations.append(
                {
                    "type": "sector_cap" if not sector_neutral else "sector_neutral",
                    "sector": sector,
                    "threshold": sector_cap if not sector_neutral else sector_band,
                    "value": exposure,
                }
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
    if beta_neutral and beta_arr is not None and abs(portfolio_beta - target_beta) > beta_tolerance + 1e-4:
        violations.append(
            {
                "type": "beta_neutrality",
                "threshold": beta_tolerance,
                "target": target_beta,
                "value": portfolio_beta,
            }
        )

    binding: list[str] = []
    if clipped_by_liquidity > 0:
        binding.append("liquidity_adv20")
    if any(abs(float(val)) >= max_per_stock - 1e-3 for val in weights if abs(float(val)) > 0):
        binding.append("single_name_cap")
    if abs(gross_exposure - gross_exposure_max) <= 1e-3:
        binding.append("gross_exposure")
    if abs(net_exposure - net_exposure_max) <= 1e-3 or abs(net_exposure - net_exposure_min) <= 1e-3:
        binding.append("net_exposure")
    if any(abs(exposure - sector_cap) <= 1e-3 for exposure in sector_exposure.values()) and not sector_neutral:
        binding.append("sector_cap")
    if any(abs(exposure - country_cap) <= 1e-3 for exposure in country_exposure.values()):
        binding.append("country_cap")
    if abs(risk_contribution_max - max_rc) <= 1e-3:
        binding.append("risk_contribution_cap")
    if cash_weight > 1e-6:
        binding.append("cash_buffer")
    if mode_used == "cvar":
        binding.append("optimizer_cvar")
    if used_cvar_fallback:
        binding.append("optimizer_fallback_mv")
    if target_vol > 0:
        binding.append("target_vol")

    return PortfolioOptimizationResult(
        weights=weights,
        cash_weight=cash_weight,
        binding_constraints=sorted(set(binding)),
        constraint_violations=violations,
        liquidity_clip_ratio=float(clipped_by_liquidity / max(n, 1)),
        risk_contribution_max=risk_contribution_max,
        sector_exposure=sector_exposure,
        country_exposure=country_exposure,
        estimated_cost=float(estimated_cost),
        gross_exposure=float(gross_exposure),
        net_exposure=float(net_exposure),
        portfolio_beta=float(portfolio_beta),
    )
