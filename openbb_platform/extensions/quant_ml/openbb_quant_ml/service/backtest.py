"""Portfolio construction and backtest helpers."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from scipy.stats import spearmanr

from openbb_quant_ml.models import BacktestConstraints
from openbb_quant_ml.service.data_loader import load_symbol_prices
from openbb_quant_ml.service.delisting import apply_delisting_returns
from openbb_quant_ml.service.portfolio_optimizer_v2 import optimize_weights_v2
from openbb_quant_ml.service.portfolio_policy import (
    apply_effective_max_weight,
    get_portfolio_policy,
)
from openbb_quant_ml.service.universe import get_symbol_metadata_map
from openbb_quant_ml.service.universe_policy import get_universe_policy

LOGGER = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    """Backtest output payload."""

    metrics: dict[str, float | int]
    equity_curve: list[dict[str, Any]]
    monthly_returns: list[dict[str, Any]]
    period_weights: list[dict[str, Any]]
    benchmark_symbol: str
    benchmark_curve: list[dict[str, Any]]
    base_index: float
    cost_breakdown: list[dict[str, Any]]
    consistency_checks: dict[str, float | bool]
    regime_mode_by_period: list[dict[str, str]]
    effective_constraints: dict[str, float | bool | str]
    cash_weight: float
    rebalance_history_summary: list[dict[str, Any]]
    constraint_violations: list[dict[str, Any]]
    liquidity_clip_ratio: float
    risk_contribution_max: float
    universe_stage_counts: dict[str, int]
    rebalance_reports: list[dict[str, Any]]


@dataclass
class DefensiveSettings:
    """Resolved defensive bucket policy/constraint settings."""

    enabled: bool
    floor_mode: str
    floor_fixed: float
    floor_low: float
    floor_mid: float
    floor_high: float
    floor_risk_off: float
    floor_max: float
    risk_off_drawdown_threshold: float
    risk_off_trend_regimes: set[str]
    risk_off_vol_regimes: set[str]
    symbols_defensive_core: set[str]
    symbols_defensive_credit: set[str]
    symbols_force_risk: set[str]
    credit_cap_abs_weight: float
    allow_u2_override: bool
    postcheck_enabled: bool
    postcheck_cvar_alpha: float
    postcheck_cvar_limit: float | None
    postcheck_vol_limit: float | None
    postcheck_floor_step: float
    postcheck_max_iterations: int
    postcheck_risk_scale_step: float
    postcheck_risk_scale_min: float

    @property
    def defensive_symbol_set(self) -> set[str]:
        return set(self.symbols_defensive_core) | set(self.symbols_defensive_credit)


def _safe_float(value: Any, default: float) -> float:
    try:
        output = float(value)
    except (TypeError, ValueError):
        return default
    if np.isnan(output) or np.isinf(output):
        return default
    return output


def _normalize_symbols(values: Any) -> set[str]:
    if not isinstance(values, (list, tuple, set)):
        return set()
    return {
        str(item).strip().upper()
        for item in values
        if str(item or "").strip()
    }


def _constraint_override(
    constraints: BacktestConstraints, field_name: str, fallback: Any
) -> Any:
    provided = getattr(constraints, "model_fields_set", set()) or set()
    if field_name in provided:
        return getattr(constraints, field_name)
    return fallback


def _resolve_defensive_settings(
    universe_policy: dict[str, Any], constraints: BacktestConstraints
) -> DefensiveSettings:
    backtest_cfg = (
        universe_policy.get("backtest", {}) if isinstance(universe_policy, dict) else {}
    )
    if not isinstance(backtest_cfg, dict):
        backtest_cfg = {}
    bucket_cfg = backtest_cfg.get("defensive_bucket", {})
    if not isinstance(bucket_cfg, dict):
        bucket_cfg = {}
    postcheck_cfg = bucket_cfg.get("postcheck", {})
    if not isinstance(postcheck_cfg, dict):
        postcheck_cfg = {}

    enabled = bool(
        _constraint_override(
            constraints, "defensive_bucket_enabled", bool(bucket_cfg.get("enabled", False))
        )
    )
    floor_mode = str(
        _constraint_override(
            constraints, "defensive_floor_mode", str(bucket_cfg.get("floor_mode", "regime"))
        )
    ).strip().lower()
    if floor_mode not in {"regime", "fixed"}:
        floor_mode = "regime"

    floor_fixed = _safe_float(
        _constraint_override(
            constraints, "defensive_floor_fixed", bucket_cfg.get("floor_fixed", 0.30)
        ),
        0.30,
    )
    floor_low = _safe_float(
        _constraint_override(
            constraints, "defensive_floor_low", bucket_cfg.get("floor_low", 0.25)
        ),
        0.25,
    )
    floor_mid = _safe_float(
        _constraint_override(
            constraints, "defensive_floor_mid", bucket_cfg.get("floor_mid", 0.35)
        ),
        0.35,
    )
    floor_high = _safe_float(
        _constraint_override(
            constraints, "defensive_floor_high", bucket_cfg.get("floor_high", 0.45)
        ),
        0.45,
    )
    floor_risk_off = _safe_float(
        _constraint_override(
            constraints,
            "defensive_floor_risk_off",
            bucket_cfg.get("floor_risk_off", 0.55),
        ),
        0.55,
    )
    drawdown_threshold = _safe_float(
        _constraint_override(
            constraints,
            "defensive_risk_off_drawdown",
            bucket_cfg.get("risk_off_drawdown_threshold", 0.10),
        ),
        0.10,
    )
    floor_max = _safe_float(bucket_cfg.get("floor_max", 0.80), 0.80)

    credit_cap_abs_weight = _safe_float(bucket_cfg.get("credit_cap_abs_weight", 0.15), 0.15)
    allow_u2_override = bool(bucket_cfg.get("allow_u2_override", True))

    postcheck_enabled = bool(
        _constraint_override(
            constraints,
            "defensive_postcheck_enabled",
            bool(postcheck_cfg.get("enabled", True)),
        )
    )
    postcheck_cvar_alpha = _safe_float(postcheck_cfg.get("cvar_alpha", 0.05), 0.05)
    postcheck_cvar_limit = _constraint_override(
        constraints,
        "defensive_postcheck_cvar_limit",
        postcheck_cfg.get("cvar_limit"),
    )
    if postcheck_cvar_limit is not None:
        postcheck_cvar_limit = float(postcheck_cvar_limit)
    postcheck_vol_limit = _constraint_override(
        constraints,
        "defensive_postcheck_vol_limit",
        postcheck_cfg.get("vol_limit"),
    )
    if postcheck_vol_limit is not None:
        postcheck_vol_limit = float(postcheck_vol_limit)
    postcheck_floor_step = _safe_float(postcheck_cfg.get("floor_step", 0.05), 0.05)
    postcheck_max_iterations = int(_safe_float(postcheck_cfg.get("max_iterations", 6), 6))
    postcheck_risk_scale_step = _safe_float(postcheck_cfg.get("risk_scale_step", 0.85), 0.85)
    postcheck_risk_scale_min = _safe_float(postcheck_cfg.get("risk_scale_min", 0.50), 0.50)

    return DefensiveSettings(
        enabled=enabled,
        floor_mode=floor_mode,
        floor_fixed=float(np.clip(floor_fixed, 0.0, 1.0)),
        floor_low=float(np.clip(floor_low, 0.0, 1.0)),
        floor_mid=float(np.clip(floor_mid, 0.0, 1.0)),
        floor_high=float(np.clip(floor_high, 0.0, 1.0)),
        floor_risk_off=float(np.clip(floor_risk_off, 0.0, 1.0)),
        floor_max=float(np.clip(floor_max, 0.0, 1.0)),
        risk_off_drawdown_threshold=float(np.clip(drawdown_threshold, 0.0, 1.0)),
        risk_off_trend_regimes={
            str(item).strip().lower()
            for item in bucket_cfg.get("risk_off_trend_regimes", ["bear"])
            if str(item or "").strip()
        },
        risk_off_vol_regimes={
            str(item).strip().lower()
            for item in bucket_cfg.get("risk_off_vol_regimes", ["high"])
            if str(item or "").strip()
        },
        symbols_defensive_core=_normalize_symbols(bucket_cfg.get("symbols_defensive_core", [])),
        symbols_defensive_credit=_normalize_symbols(
            bucket_cfg.get("symbols_defensive_credit", [])
        ),
        symbols_force_risk=_normalize_symbols(bucket_cfg.get("symbols_force_risk", [])),
        credit_cap_abs_weight=float(np.clip(credit_cap_abs_weight, 0.0, 1.0)),
        allow_u2_override=allow_u2_override,
        postcheck_enabled=postcheck_enabled,
        postcheck_cvar_alpha=float(np.clip(postcheck_cvar_alpha, 1e-4, 0.2)),
        postcheck_cvar_limit=postcheck_cvar_limit,
        postcheck_vol_limit=postcheck_vol_limit,
        postcheck_floor_step=float(np.clip(postcheck_floor_step, 0.01, 0.5)),
        postcheck_max_iterations=max(1, min(postcheck_max_iterations, 25)),
        postcheck_risk_scale_step=float(np.clip(postcheck_risk_scale_step, 0.5, 0.99)),
        postcheck_risk_scale_min=float(np.clip(postcheck_risk_scale_min, 0.1, 1.0)),
    )


def _classify_bucket(
    symbol: str, metadata: dict[str, Any], settings: DefensiveSettings
) -> str:
    symbol_key = str(symbol or "").strip().upper()
    if symbol_key in settings.symbols_force_risk:
        return "risk"
    if symbol_key in settings.symbols_defensive_core:
        return "defensive_core"
    if symbol_key in settings.symbols_defensive_credit:
        return "defensive_credit"
    category_key = str(metadata.get("category_l2") or metadata.get("category") or "").strip().lower()
    if category_key == "cash_proxy":
        return "risk"
    return "risk"


def _compute_defensive_floor(
    *,
    trend_regime: str,
    vol_regime: str,
    drawdown: float,
    settings: DefensiveSettings,
) -> tuple[float, bool]:
    if settings.floor_mode == "fixed":
        target = settings.floor_fixed
        return float(np.clip(target, 0.0, settings.floor_max)), False

    trend_key = str(trend_regime or "sideways").strip().lower()
    vol_key = str(vol_regime or "mid").strip().lower()
    drawdown_value = max(0.0, float(drawdown))
    risk_off = (
        trend_key in settings.risk_off_trend_regimes
        or vol_key in settings.risk_off_vol_regimes
        or drawdown_value >= settings.risk_off_drawdown_threshold
    )
    if risk_off:
        target = settings.floor_risk_off
    elif vol_key == "low":
        target = settings.floor_low
    elif vol_key == "high":
        target = settings.floor_high
    else:
        target = settings.floor_mid
    return float(np.clip(target, 0.0, settings.floor_max)), bool(risk_off)


def _estimate_ex_ante_risk(
    *,
    weights: np.ndarray,
    cov: np.ndarray,
    scenario_returns: np.ndarray,
    alpha: float,
) -> tuple[float, float]:
    if weights.size == 0:
        return 0.0, 0.0
    vol = float(np.sqrt(max(float(weights @ cov @ weights), 0.0)))
    if scenario_returns.size == 0:
        return vol, 0.0
    if scenario_returns.ndim != 2 or scenario_returns.shape[1] != len(weights):
        return vol, 0.0
    portfolio_returns = np.asarray(scenario_returns @ weights, dtype=float).reshape(-1)
    portfolio_returns = portfolio_returns[np.isfinite(portfolio_returns)]
    if portfolio_returns.size == 0:
        return vol, 0.0
    tail_n = max(1, int(math.ceil(float(alpha) * portfolio_returns.size)))
    tail = np.sort(portfolio_returns)[:tail_n]
    cvar = float(np.mean(tail))
    return vol, cvar


def _apply_defensive_candidate_reserve(
    *,
    selected_indices: list[int],
    active_indices: list[int],
    defensive_indices: set[int],
    mu: np.ndarray,
    current_weights: np.ndarray,
    candidate_cap: int,
    reserve_count: int,
) -> list[int]:
    if reserve_count <= 0 or not defensive_indices:
        return selected_indices
    selected = list(selected_indices)
    selected_set = set(selected)
    defensive_selected = {idx for idx in selected if idx in defensive_indices}
    reserve_target = min(reserve_count, len(defensive_indices), candidate_cap)
    if len(defensive_selected) >= reserve_target:
        return selected

    held_candidates = sorted(
        [
            idx
            for idx in active_indices
            if idx in defensive_indices
            and idx not in selected_set
            and abs(float(current_weights[idx])) > 1e-8
        ],
        key=lambda idx: abs(float(current_weights[idx])),
        reverse=True,
    )
    score_candidates = sorted(
        [
            idx
            for idx in active_indices
            if idx in defensive_indices and idx not in selected_set
        ],
        key=lambda idx: abs(float(mu[idx])),
        reverse=True,
    )
    for idx in held_candidates + score_candidates:
        defensive_selected = {item for item in selected if item in defensive_indices}
        if len(defensive_selected) >= reserve_target:
            break
        if idx in selected_set:
            continue
        if len(selected) < candidate_cap:
            selected.append(idx)
            selected_set.add(idx)
            continue
        non_def_positions = [
            pos for pos, existing in enumerate(selected) if existing not in defensive_indices
        ]
        if non_def_positions:
            weakest_pos = min(
                non_def_positions, key=lambda pos: abs(float(mu[selected[pos]]))
            )
        else:
            weakest_pos = min(
                range(len(selected)), key=lambda pos: abs(float(mu[selected[pos]]))
            )
        selected_set.discard(selected[weakest_pos])
        selected[weakest_pos] = idx
        selected_set.add(idx)
    return sorted(selected)


def _blend_two_bucket_weights(
    *,
    active_symbols: list[str],
    mu_active: np.ndarray,
    cov_active: np.ndarray,
    scenario_frame: pd.DataFrame,
    current_active: np.ndarray,
    metadata_active: dict[str, dict[str, Any]],
    constraints: BacktestConstraints,
    universe_policy: dict[str, Any],
    dynamic_max_weight: float,
    dynamic_risk_aversion: float,
    cost_params: dict[str, Any],
    beta_active: np.ndarray,
    target_floor: float,
    settings: DefensiveSettings,
) -> dict[str, Any]:
    """Run defensive two-bucket allocation with optional postcheck loops."""
    if not active_symbols:
        return {
            "weights": np.array([], dtype=float),
            "binding_constraints": ["no_eligible_symbols"],
            "constraint_violations": [],
            "liquidity_clip_ratio": 0.0,
            "risk_contribution_max": 0.0,
            "sector_exposure": {},
            "country_exposure": {},
            "estimated_cost": 0.0,
            "gross_exposure": 0.0,
            "net_exposure": 0.0,
            "portfolio_beta": 0.0,
            "debug": {
                "defensive_floor_target": float(target_floor),
                "defensive_weight_realized": 0.0,
                "defensive_core_weight": 0.0,
                "defensive_credit_weight": 0.0,
                "risk_weight_realized": 0.0,
                "postcheck_iterations": 0,
                "postcheck_vol_ex_ante": 0.0,
                "postcheck_cvar_ex_ante": 0.0,
                "postcheck_actions": [],
            },
            "used_two_bucket": False,
        }

    symbol_to_idx = {symbol: idx for idx, symbol in enumerate(active_symbols)}
    bucket_by_symbol = {
        symbol: _classify_bucket(symbol, metadata_active.get(symbol, {}), settings)
        for symbol in active_symbols
    }
    defensive_core_symbols = [
        symbol for symbol in active_symbols if bucket_by_symbol.get(symbol) == "defensive_core"
    ]
    defensive_credit_symbols = [
        symbol for symbol in active_symbols if bucket_by_symbol.get(symbol) == "defensive_credit"
    ]
    risk_symbols = [
        symbol for symbol in active_symbols if bucket_by_symbol.get(symbol) == "risk"
    ]
    if not defensive_core_symbols and not defensive_credit_symbols:
        return {"used_two_bucket": False}

    scenario_matrix_full = scenario_frame.fillna(0.0).to_numpy(dtype=float)
    scenario_columns = list(scenario_frame.columns)

    def _slice_scenario(local_symbols: list[str]) -> np.ndarray:
        if not local_symbols:
            return np.zeros((0, 0), dtype=float)
        if scenario_frame.empty:
            return np.zeros((0, len(local_symbols)), dtype=float)
        col_idx = [scenario_columns.index(symbol) for symbol in local_symbols]
        return scenario_matrix_full[:, col_idx]

    def _run_bucket(
        *,
        local_symbols: list[str],
        budget_min: float,
        budget_max: float,
        max_weight: float,
        sector_max_weight: float,
        country_max_weight: float | None = None,
    ) -> tuple[np.ndarray, Any]:
        if not local_symbols or budget_max <= 1e-9:
            return np.zeros(len(local_symbols), dtype=float), None
        local_indices = [symbol_to_idx[symbol] for symbol in local_symbols]
        local_meta = {
            symbol: metadata_active.get(symbol, {}) for symbol in local_symbols
        }
        exposure_constraints = {
            "allow_short": False,
            "gross_exposure_max": float(max(budget_max, 0.0)),
            "net_exposure_min": float(max(budget_min, 0.0)),
            "net_exposure_max": float(max(budget_max, 0.0)),
            "sector_max_weight": float(np.clip(sector_max_weight, 0.0, 1.0)),
            "sector_neutral": False,
            "beta_neutral": False,
            "beta_tolerance": float(getattr(constraints, "beta_tolerance", 0.05)),
            "target_beta": 0.0,
        }
        if country_max_weight is not None:
            exposure_constraints["country_max_weight"] = float(
                np.clip(country_max_weight, 0.0, 1.0)
            )
        result = optimize_weights_v2(
            mu=mu_active[local_indices],
            cov=cov_active[np.ix_(local_indices, local_indices)],
            symbols=local_symbols,
            metadata_by_symbol=local_meta,
            risk_aversion=float(dynamic_risk_aversion),
            requested_max_weight=float(max_weight),
            policy=universe_policy,
            nav=1.0,
            optimizer_mode=str(constraints.optimizer_mode),
            mv_optimizer_engine=str(
                getattr(constraints, "mv_optimizer_engine", "legacy_slsqp")
            ),
            optimizer_strict=bool(getattr(constraints, "optimizer_strict", False)),
            cvar_alpha=float(constraints.cvar_alpha),
            cvar_lambda=float(constraints.cvar_lambda),
            scenario_returns=_slice_scenario(local_symbols),
            current_weights=current_active[local_indices],
            cost_params=cost_params,
            exposure_constraints=exposure_constraints,
            beta_vector=beta_active[local_indices],
            target_vol=(
                float(constraints.target_vol)
                if getattr(constraints, "target_vol", None) is not None
                else None
            ),
        )
        return np.asarray(result.weights, dtype=float), result

    target_floor = float(np.clip(target_floor, 0.0, settings.floor_max))
    floor_current = float(target_floor)
    risk_scale = 1.0
    postcheck_actions: list[str] = []
    iterations = 0
    final_bundle: dict[str, Any] = {}
    infeasible_floor = False

    for _ in range(max(1, settings.postcheck_max_iterations)):
        iterations += 1
        floor_symbols = list(defensive_core_symbols)
        floor_budget = float(floor_current)
        local_infeasible_floor = False
        if not floor_symbols:
            floor_symbols = list(defensive_credit_symbols)
            if floor_budget > settings.credit_cap_abs_weight + 1e-12:
                floor_budget = float(settings.credit_cap_abs_weight)
                local_infeasible_floor = True

        floor_weights = np.array([], dtype=float)
        floor_result = None
        if floor_symbols and floor_budget > 1e-9:
            floor_weights, floor_result = _run_bucket(
                local_symbols=floor_symbols,
                budget_min=floor_budget,
                budget_max=floor_budget,
                max_weight=float(dynamic_max_weight),
                sector_max_weight=1.0,
                country_max_weight=1.0,
            )
        floor_map = {symbol: 0.0 for symbol in floor_symbols}
        if floor_symbols and floor_weights.size == len(floor_symbols):
            floor_map.update(
                {
                    symbol: float(weight)
                    for symbol, weight in zip(floor_symbols, floor_weights, strict=False)
                }
            )

        credit_floor_sum = float(
            sum(
                weight
                for symbol, weight in floor_map.items()
                if symbol in defensive_credit_symbols
            )
        )
        credit_budget_left = max(0.0, settings.credit_cap_abs_weight - credit_floor_sum)
        credit_extra_symbols = [
            symbol
            for symbol in defensive_credit_symbols
            if symbol not in set(floor_symbols)
        ]
        credit_extra_weights = np.array([], dtype=float)
        credit_result = None
        if credit_extra_symbols and credit_budget_left > 1e-9:
            credit_extra_weights, credit_result = _run_bucket(
                local_symbols=credit_extra_symbols,
                budget_min=0.0,
                budget_max=float(credit_budget_left),
                max_weight=float(dynamic_max_weight),
                sector_max_weight=1.0,
                country_max_weight=1.0,
            )
        credit_extra_map = {symbol: 0.0 for symbol in credit_extra_symbols}
        if credit_extra_symbols and credit_extra_weights.size == len(credit_extra_symbols):
            credit_extra_map.update(
                {
                    symbol: float(weight)
                    for symbol, weight in zip(
                        credit_extra_symbols, credit_extra_weights, strict=False
                    )
                }
            )

        defensive_pre_risk = float(
            sum(floor_map.values()) + sum(credit_extra_map.values())
        )
        risk_budget_cap = max(0.0, 1.0 - defensive_pre_risk)
        risk_budget_cap *= float(np.clip(risk_scale, settings.postcheck_risk_scale_min, 1.0))
        risk_weights = np.array([], dtype=float)
        risk_result = None
        if risk_symbols and risk_budget_cap > 1e-9:
            risk_weights, risk_result = _run_bucket(
                local_symbols=risk_symbols,
                budget_min=0.0,
                budget_max=float(risk_budget_cap),
                max_weight=float(dynamic_max_weight * risk_scale),
                sector_max_weight=float(getattr(constraints, "sector_max_weight", 0.35)),
                country_max_weight=None,
            )
        risk_map = {symbol: 0.0 for symbol in risk_symbols}
        if risk_symbols and risk_weights.size == len(risk_symbols):
            risk_map.update(
                {
                    symbol: float(weight)
                    for symbol, weight in zip(risk_symbols, risk_weights, strict=False)
                }
            )

        combined = np.zeros(len(active_symbols), dtype=float)
        for symbol, weight in floor_map.items():
            combined[symbol_to_idx[symbol]] = float(weight)
        for symbol, weight in credit_extra_map.items():
            combined[symbol_to_idx[symbol]] = float(weight)
        for symbol, weight in risk_map.items():
            combined[symbol_to_idx[symbol]] = float(weight)

        defensive_core_weight = float(
            sum(
                combined[symbol_to_idx[symbol]]
                for symbol in defensive_core_symbols
                if symbol in symbol_to_idx
            )
        )
        defensive_credit_weight = float(
            sum(
                combined[symbol_to_idx[symbol]]
                for symbol in defensive_credit_symbols
                if symbol in symbol_to_idx
            )
        )
        defensive_weight = float(defensive_core_weight + defensive_credit_weight)
        risk_weight = float(
            sum(
                combined[symbol_to_idx[symbol]]
                for symbol in risk_symbols
                if symbol in symbol_to_idx
            )
        )
        vol_ex_ante, cvar_ex_ante = _estimate_ex_ante_risk(
            weights=combined,
            cov=cov_active,
            scenario_returns=scenario_matrix_full,
            alpha=float(settings.postcheck_cvar_alpha),
        )

        vol_breach = (
            settings.postcheck_vol_limit is not None
            and vol_ex_ante > float(settings.postcheck_vol_limit) + 1e-12
        )
        cvar_breach = (
            settings.postcheck_cvar_limit is not None
            and cvar_ex_ante < float(settings.postcheck_cvar_limit) - 1e-12
        )
        floor_breach = defensive_weight < floor_current - 1e-6

        final_bundle = {
            "weights": combined,
            "defensive_weight": defensive_weight,
            "defensive_core_weight": defensive_core_weight,
            "defensive_credit_weight": defensive_credit_weight,
            "risk_weight": risk_weight,
            "vol_ex_ante": vol_ex_ante,
            "cvar_ex_ante": cvar_ex_ante,
            "floor_target": floor_current,
            "floor_result": floor_result,
            "credit_result": credit_result,
            "risk_result": risk_result,
            "local_infeasible_floor": local_infeasible_floor,
            "vol_breach": vol_breach,
            "cvar_breach": cvar_breach,
            "floor_breach": floor_breach,
        }

        if local_infeasible_floor:
            infeasible_floor = True

        if not settings.postcheck_enabled or (not vol_breach and not cvar_breach and not floor_breach):
            break

        if floor_current < settings.floor_max - 1e-12:
            next_floor = min(settings.floor_max, floor_current + settings.postcheck_floor_step)
            if next_floor > floor_current + 1e-12:
                floor_current = next_floor
                postcheck_actions.append(
                    f"raise_floor:{floor_current:.4f}"
                )
                continue
        if risk_scale > settings.postcheck_risk_scale_min + 1e-12:
            risk_scale = max(
                settings.postcheck_risk_scale_min,
                risk_scale * settings.postcheck_risk_scale_step,
            )
            postcheck_actions.append(f"scale_risk:{risk_scale:.4f}")
            continue
        break

    combined_weights = np.asarray(final_bundle.get("weights", np.zeros(len(active_symbols))), dtype=float)
    floor_result = final_bundle.get("floor_result")
    credit_result = final_bundle.get("credit_result")
    risk_result = final_bundle.get("risk_result")

    binding_constraints: list[str] = ["defensive_bucket_2stage"]
    if settings.postcheck_enabled and iterations > 1:
        binding_constraints.append("defensive_postcheck")
    if infeasible_floor or bool(final_bundle.get("floor_breach")):
        binding_constraints.append("defensive_floor_infeasible")
    if bool(final_bundle.get("vol_breach")) or bool(final_bundle.get("cvar_breach")):
        binding_constraints.append("global_risk_guard_unsatisfied")
    for prefix, result in (
        ("def_floor", floor_result),
        ("def_credit", credit_result),
        ("risk", risk_result),
    ):
        if result is None:
            continue
        for item in list(result.binding_constraints):
            binding_constraints.append(f"{prefix}:{item}")

    violations: list[dict[str, Any]] = []
    for result in (floor_result, credit_result, risk_result):
        if result is None:
            continue
        violations.extend(list(result.constraint_violations))
    if infeasible_floor or bool(final_bundle.get("floor_breach")):
        violations.append(
            {
                "type": "defensive_floor_infeasible",
                "threshold": float(final_bundle.get("floor_target", target_floor)),
                "value": float(final_bundle.get("defensive_weight", 0.0)),
            }
        )
    if bool(final_bundle.get("vol_breach")) or bool(final_bundle.get("cvar_breach")):
        violations.append(
            {
                "type": "global_risk_guard_unsatisfied",
                "threshold": float(
                    settings.postcheck_vol_limit
                    if settings.postcheck_vol_limit is not None
                    else 0.0
                ),
                "value": float(final_bundle.get("vol_ex_ante", 0.0)),
                "cvar_limit": (
                    float(settings.postcheck_cvar_limit)
                    if settings.postcheck_cvar_limit is not None
                    else None
                ),
                "cvar_value": float(final_bundle.get("cvar_ex_ante", 0.0)),
            }
        )

    liquidity_clip_ratio = float(
        max(
            [
                float(getattr(result, "liquidity_clip_ratio", 0.0))
                for result in (floor_result, credit_result, risk_result)
                if result is not None
            ]
            or [0.0]
        )
    )
    estimated_cost = float(
        sum(
            float(getattr(result, "estimated_cost", 0.0))
            for result in (floor_result, credit_result, risk_result)
            if result is not None
        )
    )
    gross_exposure = float(np.sum(np.abs(combined_weights)))
    net_exposure = float(np.sum(combined_weights))
    portfolio_beta = (
        float(np.dot(beta_active, combined_weights))
        if len(beta_active) == len(combined_weights)
        else 0.0
    )
    rc_vec = (
        combined_weights
        * (cov_active @ combined_weights)
        / max(float(np.sqrt(max(float(combined_weights @ cov_active @ combined_weights), 1e-9))), 1e-9)
    )
    risk_contribution_max = (
        float(np.max(np.abs(rc_vec))) if rc_vec.size else 0.0
    )
    sector_exposure: dict[str, float] = {}
    country_exposure: dict[str, float] = {}
    for symbol, weight in zip(active_symbols, combined_weights, strict=False):
        if abs(float(weight)) <= 1e-12:
            continue
        meta = metadata_active.get(symbol, {})
        sector = str(meta.get("sector_l1", "other")).strip() or "other"
        country = str(meta.get("country", "US")).strip().upper() or "US"
        sector_exposure[sector] = sector_exposure.get(sector, 0.0) + float(weight)
        country_exposure[country] = country_exposure.get(country, 0.0) + float(weight)

    return {
        "weights": combined_weights,
        "binding_constraints": sorted(set(binding_constraints)),
        "constraint_violations": violations,
        "liquidity_clip_ratio": liquidity_clip_ratio,
        "risk_contribution_max": risk_contribution_max,
        "sector_exposure": sector_exposure,
        "country_exposure": country_exposure,
        "estimated_cost": estimated_cost,
        "gross_exposure": gross_exposure,
        "net_exposure": net_exposure,
        "portfolio_beta": portfolio_beta,
        "debug": {
            "defensive_floor_target": float(final_bundle.get("floor_target", target_floor)),
            "defensive_weight_realized": float(final_bundle.get("defensive_weight", 0.0)),
            "defensive_core_weight": float(final_bundle.get("defensive_core_weight", 0.0)),
            "defensive_credit_weight": float(final_bundle.get("defensive_credit_weight", 0.0)),
            "risk_weight_realized": float(final_bundle.get("risk_weight", 0.0)),
            "postcheck_iterations": int(iterations),
            "postcheck_vol_ex_ante": float(final_bundle.get("vol_ex_ante", 0.0)),
            "postcheck_cvar_ex_ante": float(final_bundle.get("cvar_ex_ante", 0.0)),
            "postcheck_actions": list(postcheck_actions),
        },
        "used_two_bucket": True,
    }


def _monthly_rebalance_dates(dates: pd.DatetimeIndex) -> list[pd.Timestamp]:
    if len(dates) == 0:
        return []
    grouped = pd.Series(dates, index=dates).groupby(dates.to_period("M")).first()
    return [pd.Timestamp(value) for value in grouped.values]


def _month_end_rebalance_dates(dates: pd.DatetimeIndex) -> list[pd.Timestamp]:
    if len(dates) == 0:
        return []
    grouped = pd.Series(dates, index=dates).groupby(dates.to_period("M")).last()
    return [pd.Timestamp(value) for value in grouped.values]


def _cross_sectional_zscore(values: pd.Series) -> pd.Series:
    if values.empty:
        return values
    out = pd.to_numeric(values, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    std = float(out.std(ddof=0))
    if std <= 1e-12:
        return pd.Series(np.zeros(len(out), dtype=float), index=out.index)
    return (out - float(out.mean())) / std


def _estimate_forward_ic(
    ic_history: list[float],
    halflife: int,
    clip_min: float,
    clip_max: float,
    fallback: float,
) -> float:
    if not ic_history:
        return float(fallback)
    history = pd.Series(ic_history, dtype=float).replace([np.inf, -np.inf], np.nan).dropna()
    if history.empty:
        return float(fallback)
    if len(history) == 1:
        estimate = float(history.iloc[-1])
    else:
        estimate = float(history.ewm(halflife=max(int(halflife), 2), adjust=False).mean().iloc[-1])
    lo = min(float(clip_min), float(clip_max))
    hi = max(float(clip_min), float(clip_max))
    return float(np.clip(estimate, lo, hi))


def _resolve_candidate_cap(universe_policy: dict[str, Any]) -> int:
    """Resolve long-only optimizer candidate cap from policy."""
    portfolio_cfg = (
        universe_policy.get("portfolio_constraints", {})
        if isinstance(universe_policy, dict)
        else {}
    )
    if not isinstance(portfolio_cfg, dict):
        portfolio_cfg = {}
    backtest_cfg = universe_policy.get("backtest", {}) if isinstance(universe_policy, dict) else {}
    if not isinstance(backtest_cfg, dict):
        backtest_cfg = {}

    target_count = max(int(portfolio_cfg.get("target_count", 150)), 1)
    max_count = max(int(portfolio_cfg.get("max_count", target_count)), target_count)
    default_cap = max(target_count + 25, int(round(target_count * 1.25)))
    configured_cap = int(backtest_cfg.get("candidate_cap", default_cap))
    return max(min(configured_cap, max_count), target_count, 50)


def _select_candidate_indices(
    active_indices: list[int],
    mu: np.ndarray,
    current_weights: np.ndarray,
    *,
    candidate_cap: int,
) -> list[int]:
    """Select manageable optimizer candidates while preserving current holdings."""
    if len(active_indices) <= candidate_cap:
        return active_indices

    ranked = sorted(active_indices, key=lambda idx: abs(float(mu[idx])), reverse=True)
    selected: list[int] = ranked[:candidate_cap]
    selected_set = set(selected)

    held = [
        idx
        for idx in active_indices
        if abs(float(current_weights[idx])) > 1e-8 and idx not in selected_set
    ]
    if held:
        for idx in sorted(held, key=lambda i: abs(float(current_weights[i])), reverse=True):
            if len(selected) < candidate_cap:
                selected.append(idx)
                selected_set.add(idx)
                continue
            # Replace weakest non-held score candidate to preserve existing exposure.
            weakest_pos = min(
                range(len(selected)),
                key=lambda pos: abs(float(mu[selected[pos]])),
            )
            selected[weakest_pos] = idx
            selected_set = set(selected)

    return sorted(selected)


def _safe_initial_weights(
    asset_count: int, max_weight: float, *, allow_short: bool
) -> np.ndarray:
    if asset_count <= 0:
        return np.array([])
    equal = np.repeat(1.0 / asset_count, asset_count)
    if allow_short:
        return np.clip(equal, -max_weight, max_weight)
    clipped = np.minimum(equal, max_weight)
    clipped_sum = float(clipped.sum())
    if clipped_sum <= 0:
        return np.zeros(asset_count, dtype=float)
    if clipped_sum > 1.0:
        clipped = clipped / clipped_sum
    return clipped


def _apply_cov_shrinkage(cov: np.ndarray, shrinkage: float = 0.1) -> np.ndarray:
    """Apply Ledoit-Wolf style shrinkage toward diagonal."""
    n = cov.shape[0]
    if n == 0:
        return cov
    target = np.diag(np.diag(cov))
    return (1.0 - shrinkage) * cov + shrinkage * target


def _estimate_covariance(
    hist_returns: pd.DataFrame,
    method: str,
    ewma_halflife: int,
    shrinkage: float,
    pca_components: int = 10,
    pca_idio_floor: float = 1e-6,
) -> np.ndarray:
    """Estimate covariance matrix with configurable method."""
    hist = hist_returns.copy()
    n_assets_hint = len(hist.columns)
    if hist.empty:
        if n_assets_hint <= 0:
            return np.zeros((0, 0), dtype=float)
        return np.eye(n_assets_hint, dtype=float) * 1e-8
    hist = hist.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    arr = hist.to_numpy(dtype=float)
    n_obs, n_assets = arr.shape
    if n_assets == 0:
        return np.zeros((0, 0), dtype=float)
    if n_obs < 2:
        return np.eye(n_assets, dtype=float) * 1e-8

    method_key = str(method or "sample").strip().lower()
    if method_key == "sample":
        cov = np.cov(arr, rowvar=False, ddof=0)
    elif method_key == "ewma":
        halflife = max(int(ewma_halflife), 2)
        decay = np.exp(np.log(0.5) / float(halflife))
        weights = decay ** np.arange(n_obs - 1, -1, -1)
        weights = weights / max(float(weights.sum()), 1e-12)
        mean = np.sum(arr * weights[:, None], axis=0)
        centered = arr - mean
        cov = (centered * weights[:, None]).T @ centered
    elif method_key == "ledoit_wolf":
        try:
            from sklearn.covariance import LedoitWolf

            cov = LedoitWolf().fit(arr).covariance_
        except Exception:
            cov = np.cov(arr, rowvar=False, ddof=0)
    elif method_key == "ewma_shrink":
        ewma_cov = _estimate_covariance(
            hist_returns=hist,
            method="ewma",
            ewma_halflife=ewma_halflife,
            shrinkage=shrinkage,
            pca_components=pca_components,
            pca_idio_floor=pca_idio_floor,
        )
        cov = _apply_cov_shrinkage(ewma_cov, shrinkage=float(np.clip(shrinkage, 0.0, 1.0)))
    elif method_key == "stat_factor_pca":
        centered = arr - np.mean(arr, axis=0, keepdims=True)
        max_components = min(max(n_assets - 1, 1), max(n_obs - 1, 1))
        k = int(min(max(1, int(pca_components)), max_components))
        try:
            from sklearn.decomposition import PCA

            pca = PCA(n_components=k, svd_solver="full", random_state=42)
            factors = pca.fit_transform(centered)
            loadings = pca.components_.T
            factor_cov = np.cov(factors, rowvar=False, ddof=0)
            if np.ndim(factor_cov) == 0:
                factor_cov = np.array([[float(factor_cov)]], dtype=float)
            common = loadings @ factor_cov @ loadings.T
            reconstructed = factors @ pca.components_
            resid = centered - reconstructed
            idio = np.var(resid, axis=0, ddof=0)
            idio = np.clip(idio, float(max(pca_idio_floor, 1e-12)), None)
            cov = common + np.diag(idio)
        except Exception as exc:
            LOGGER.warning(
                "stat_factor_pca covariance failed; fallback to ewma_shrink: %s",
                exc,
            )
            cov = _estimate_covariance(
                hist_returns=hist,
                method="ewma_shrink",
                ewma_halflife=ewma_halflife,
                shrinkage=shrinkage,
                pca_components=pca_components,
                pca_idio_floor=pca_idio_floor,
            )
    else:
        cov = np.cov(arr, rowvar=False, ddof=0)

    cov = np.asarray(cov, dtype=float)
    cov = np.nan_to_num(cov, nan=0.0, posinf=0.0, neginf=0.0)
    cov = 0.5 * (cov + cov.T)
    try:
        eigvals, eigvecs = np.linalg.eigh(cov)
        eigvals = np.clip(eigvals, 1e-10, None)
        cov = eigvecs @ np.diag(eigvals) @ eigvecs.T
        cov = 0.5 * (cov + cov.T)
    except Exception:
        pass
    cov = cov + np.eye(n_assets, dtype=float) * 1e-8
    return cov


def _estimate_trade_cost_components(
    delta_w: np.ndarray,
    adv_usd: np.ndarray,
    commission_bps: float,
    half_spread_bps: float,
    impact_k: float,
    nav: float,
) -> dict[str, float]:
    """Estimate normalized trade cost components."""
    nav = max(float(nav), 1e-9)
    abs_delta = np.abs(np.asarray(delta_w, dtype=float))
    adv_arr = np.asarray(adv_usd, dtype=float)
    if adv_arr.size != abs_delta.size:
        adv_arr = np.ones(abs_delta.size, dtype=float)

    turnover = float(abs_delta.sum())
    commission = float((float(commission_bps) / 1e4) * turnover)
    spread = float((float(half_spread_bps) / 1e4) * turnover)

    adv_weight_capacity = np.clip(adv_arr / nav, 1e-6, None)
    impact = float((float(impact_k) / 1e4) * np.sum((abs_delta**2) / adv_weight_capacity))
    total = float(commission + spread + impact)
    return {
        "commission": commission,
        "spread": spread,
        "impact": impact,
        "total": total,
    }


def _optimize_weights(
    mu: np.ndarray,
    cov: np.ndarray,
    constraints: BacktestConstraints,
    *,
    allow_short: bool,
    max_weight: float,
    risk_aversion: float | None = None,
) -> np.ndarray:
    asset_count = len(mu)
    if asset_count == 0:
        return np.array([])

    weight_cap = max(float(max_weight), 1e-6)
    initial = _safe_initial_weights(asset_count, weight_cap, allow_short=allow_short)

    if float(np.abs(mu).max()) < 1e-12:
        return initial

    cov_stable = cov.copy()
    try:
        cond = float(np.linalg.cond(cov_stable))
    except (np.linalg.LinAlgError, FloatingPointError):
        cond = 1e15
    if cond > 1e10 or not np.isfinite(cond):
        cov_stable = _apply_cov_shrinkage(cov_stable, shrinkage=0.2)

    bounds = [
        (-weight_cap, weight_cap) if allow_short else (0.0, weight_cap)
        for _ in range(asset_count)
    ]

    def objective(weights: np.ndarray) -> float:
        risk_aversion_local = (
            float(risk_aversion)
            if risk_aversion is not None
            else float(constraints.risk_aversion)
        )
        mean_term = float(np.dot(mu, weights))
        risk_term = float(weights @ cov_stable @ weights)
        return -(mean_term - risk_aversion_local * risk_term)

    if allow_short:
        optimizer_constraints = [
            {"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)}
        ]
    else:
        optimizer_constraints = [
            {"type": "ineq", "fun": lambda w: float(1.0 - np.sum(w))}
        ]
    if allow_short:
        gross_cap = 1.5
        optimizer_constraints.append(
            {"type": "ineq", "fun": lambda w: float(gross_cap - np.sum(np.abs(w)))}
        )

    result = minimize(
        objective,
        initial,
        method="SLSQP",
        bounds=bounds,
        constraints=optimizer_constraints,
    )
    if result.success:
        clipped = np.clip(result.x, -weight_cap if allow_short else 0.0, weight_cap)
        if allow_short:
            gross = float(np.sum(np.abs(clipped)))
            if gross > 1.5 and gross > 0:
                clipped = clipped * (1.5 / gross)
            clipped = clipped + ((1.0 - float(np.sum(clipped))) / max(asset_count, 1))
            clipped = np.clip(clipped, -weight_cap, weight_cap)
        else:
            total = float(np.sum(clipped))
            if total > 1.0 and total > 0:
                clipped = clipped * (1.0 / total)
            clipped = np.clip(clipped, 0.0, weight_cap)
        return clipped

    positive = np.maximum(mu, 0.0)
    if allow_short:
        centered = mu - float(np.mean(mu))
        positive = np.maximum(centered, 0.0)
        negative = np.maximum(-centered, 0.0)
        if positive.sum() > 0 and negative.sum() > 0:
            short_budget = min(
                0.35, float(negative.sum() / (positive.sum() + negative.sum() + 1e-12))
            )
            long_w = positive / positive.sum()
            short_w = negative / negative.sum()
            fallback = long_w * (1.0 + short_budget) - short_w * short_budget
            fallback = np.clip(fallback, -weight_cap, weight_cap)
            fallback = fallback + (
                (1.0 - float(np.sum(fallback))) / max(asset_count, 1)
            )
            return np.clip(fallback, -weight_cap, weight_cap)
    if positive.sum() > 0:
        fallback = positive / positive.sum()
        fallback = np.clip(fallback, -weight_cap if allow_short else 0.0, weight_cap)
        if not allow_short:
            total = float(np.sum(fallback))
            if total > 1.0 and total > 0:
                fallback = fallback * (1.0 / total)
            fallback = np.clip(fallback, 0.0, weight_cap)
        return fallback
    return initial


def _compute_regime_series(
    close_panel: pd.DataFrame,
    dates: pd.DatetimeIndex,
    benchmark_symbol: str,
) -> pd.DataFrame:
    if len(dates) == 0:
        return pd.DataFrame(columns=["trend_regime", "vol_regime"])
    symbol = (
        benchmark_symbol
        if benchmark_symbol in close_panel.columns
        else str(close_panel.columns[0])
    )
    benchmark = close_panel[symbol].astype(float).reindex(dates).ffill().bfill()
    if benchmark.empty:
        return pd.DataFrame(
            index=dates, data={"trend_regime": "sideways", "vol_regime": "mid"}
        )
    ret = (
        benchmark.pct_change(fill_method=None)
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )
    ma200 = benchmark.rolling(200, min_periods=20).mean()
    trend = np.where(
        benchmark > ma200 * 1.01,
        "bull",
        np.where(benchmark < ma200 * 0.99, "bear", "sideways"),
    )
    vol20 = ret.rolling(20, min_periods=5).std(ddof=0) * np.sqrt(252)
    low_q = float(vol20.quantile(0.33))
    high_q = float(vol20.quantile(0.66))
    vol_regime = np.where(
        vol20 <= low_q, "low", np.where(vol20 >= high_q, "high", "mid")
    )
    return pd.DataFrame(
        index=dates,
        data={
            "trend_regime": trend,
            "vol_regime": vol_regime,
        },
    )


def _mixed_policy_allows_short(trend_regime: str, vol_regime: str) -> bool:
    return trend_regime == "bull" and vol_regime in {"low", "mid"}


def _dynamic_risk_budget_scale(
    trend_regime: str, vol_regime: str, current_drawdown: float
) -> float:
    """Return exposure scaling factor in mixed mode (0.30 ~ 1.00)."""
    trend_key = str(trend_regime or "sideways").lower()
    vol_key = str(vol_regime or "mid").lower()
    trend_scale = {"bull": 1.0, "sideways": 0.82, "bear": 0.62}.get(trend_key, 0.82)
    vol_scale = {"low": 1.0, "mid": 0.90, "high": 0.72}.get(vol_key, 0.9)
    dd = max(0.0, float(current_drawdown))
    dd_scale = max(0.35, 1.0 - dd * 3.0)
    return float(np.clip(trend_scale * vol_scale * dd_scale, 0.30, 1.0))


def _consistency_checks(
    period_weights: list[dict[str, Any]], turnover_values: list[float]
) -> dict[str, float | bool]:
    if not period_weights:
        return {
            "valid": False,
            "weight_sum_error_max": 0.0,
            "gross_exposure_max": 0.0,
            "net_exposure_min": 0.0,
            "net_exposure_max": 0.0,
            "turnover_mean": 0.0,
        }
    weight_sum_errors: list[float] = []
    gross_exposures: list[float] = []
    net_exposures: list[float] = []
    for row in period_weights:
        weights = [float(v) for v in row.get("weights", {}).values()]
        weight_sum = float(sum(weights))
        gross = float(sum(abs(v) for v in weights))
        net = float(sum(weights))
        weight_sum_errors.append(abs(weight_sum - 1.0))
        gross_exposures.append(gross)
        net_exposures.append(net)
    return {
        "valid": bool(max(weight_sum_errors) <= 1e-4 and max(gross_exposures) <= 1.51),
        "weight_sum_error_max": float(max(weight_sum_errors)),
        "gross_exposure_max": float(max(gross_exposures)),
        "net_exposure_min": float(min(net_exposures)),
        "net_exposure_max": float(max(net_exposures)),
        "turnover_mean": float(np.mean(turnover_values)) if turnover_values else 0.0,
    }


def _compute_metrics(
    daily_returns: pd.Series, equity_curve: pd.Series
) -> dict[str, float | int]:
    if daily_returns.empty:
        return {
            "cagr": 0.0,
            "sharpe": 0.0,
            "sortino": 0.0,
            "calmar": 0.0,
            "omega": 0.0,
            "max_consecutive_loss_days": 0,
            "max_drawdown": 0.0,
            "volatility": 0.0,
            "turnover": 0.0,
        }

    trading_days = max(len(daily_returns), 1)
    total_return = float(equity_curve.iloc[-1] / equity_curve.iloc[0] - 1.0)
    cagr = (
        float((1 + total_return) ** (252 / trading_days) - 1)
        if trading_days > 0
        else 0.0
    )

    vol = float(daily_returns.std(ddof=0) * np.sqrt(252))
    sharpe = float(
        (daily_returns.mean() / (daily_returns.std(ddof=0) + 1e-12)) * np.sqrt(252)
    )
    downside = daily_returns[daily_returns < 0.0]
    downside_std = (
        float(downside.std(ddof=0) * np.sqrt(252)) if len(downside) > 0 else 0.0
    )
    sortino = float((daily_returns.mean() * np.sqrt(252)) / (downside_std + 1e-12))

    running_max = equity_curve.cummax()
    drawdown = equity_curve / (running_max + 1e-12) - 1.0
    max_drawdown = float(drawdown.min())
    calmar = float(cagr / abs(max_drawdown)) if max_drawdown < 0 else 0.0
    gains = float(np.clip(daily_returns, 0.0, None).sum())
    losses = float(np.clip(-daily_returns, 0.0, None).sum())
    omega = float(gains / (losses + 1e-12))
    loss_mask = (daily_returns < 0.0).to_numpy(dtype=int)
    if loss_mask.size == 0:
        max_consecutive_loss_days = 0
    else:
        run_lengths: list[int] = []
        running = 0
        for value in loss_mask:
            if value:
                running += 1
            elif running > 0:
                run_lengths.append(running)
                running = 0
        if running > 0:
            run_lengths.append(running)
        max_consecutive_loss_days = int(max(run_lengths) if run_lengths else 0)
    return {
        "cagr": cagr,
        "sharpe": sharpe,
        "sortino": sortino,
        "calmar": calmar,
        "omega": omega,
        "max_consecutive_loss_days": int(max_consecutive_loss_days),
        "max_drawdown": max_drawdown,
        "volatility": vol,
    }


def _monthly_returns_matrix(
    dates: pd.Series,
    daily_returns: pd.Series,
) -> list[dict[str, Any]]:
    if daily_returns.empty or dates.empty:
        return []
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(dates).dt.tz_localize(None),
            "daily_return": pd.to_numeric(daily_returns, errors="coerce").fillna(0.0),
        }
    ).dropna(subset=["date"])
    if frame.empty:
        return []
    frame["year"] = frame["date"].dt.year.astype(int)
    frame["month"] = frame["date"].dt.month.astype(int)
    monthly = (
        frame.groupby(["year", "month"])["daily_return"]
        .apply(lambda values: float(np.prod(1.0 + values.to_numpy(dtype=float)) - 1.0))
        .reset_index(name="return")
        .sort_values(["year", "month"])
    )
    return monthly.to_dict(orient="records")


def _normalize_downloaded_close(downloaded: pd.DataFrame) -> pd.Series:
    if downloaded.empty:
        return pd.Series(dtype=float)
    frame = downloaded.copy()
    if isinstance(frame.columns, pd.MultiIndex):
        close = frame["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
    else:
        close = frame["Close"] if "Close" in frame.columns else frame.iloc[:, 0]
    series = close.astype(float)
    series.index = pd.to_datetime(series.index).tz_localize(None)
    return series.sort_index()


def _normalize_price_series(series: pd.Series) -> pd.Series:
    """Normalize benchmark series to date-aligned, unique daily index."""
    if series.empty:
        return pd.Series(dtype=float)
    normalized = pd.to_numeric(series, errors="coerce")
    index = pd.to_datetime(series.index, errors="coerce")
    if not isinstance(index, pd.DatetimeIndex):
        return pd.Series(dtype=float)
    if index.tz is not None:
        index = index.tz_convert(None)
    normalized.index = index.normalize()
    normalized = normalized[~normalized.index.isna()].dropna()
    if normalized.empty:
        return pd.Series(dtype=float)
    return normalized.groupby(level=0).last().sort_index()


def _benchmark_curve(
    close_panel: pd.DataFrame,
    curve_dates: pd.DatetimeIndex,
    benchmark_symbol: str,
    base_index: float,
) -> list[dict[str, Any]]:
    if len(curve_dates) == 0:
        return []

    prices: pd.Series
    if benchmark_symbol in close_panel.columns:
        prices = close_panel[benchmark_symbol].dropna().astype(float)
        prices.index = pd.to_datetime(prices.index).tz_localize(None)
    else:
        start_day = (curve_dates.min() - timedelta(days=10)).date()
        end_day = (curve_dates.max() + timedelta(days=10)).date()
        prices = pd.Series(dtype=float)
        try:
            # Reuse provider/cache path before direct yfinance fallback.
            benchmark_frame = load_symbol_prices(
                symbol=benchmark_symbol,
                start_date=start_day,
                end_date=end_day,
                provider="yfinance",
            )
            if not benchmark_frame.empty and "close" in benchmark_frame.columns:
                prices = pd.Series(
                    pd.to_numeric(benchmark_frame["close"], errors="coerce").to_numpy(),
                    index=pd.to_datetime(benchmark_frame["date"], errors="coerce"),
                )
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning(
                "Benchmark loader failed for %s (%s -> %s): %s",
                benchmark_symbol,
                start_day.isoformat(),
                end_day.isoformat(),
                exc,
            )
        if prices.empty:
            downloaded = yf.download(
                tickers=benchmark_symbol,
                start=start_day.isoformat(),
                end=end_day.isoformat(),
                auto_adjust=False,
                progress=False,
                group_by="column",
                threads=False,
            )
            prices = _normalize_downloaded_close(downloaded)

    curve_index = pd.DatetimeIndex(pd.to_datetime(curve_dates, errors="coerce"))
    if curve_index.tz is not None:
        curve_index = curve_index.tz_convert(None)
    curve_index = curve_index.normalize()
    price_series = _normalize_price_series(prices)
    aligned = price_series.reindex(curve_index).ffill().bfill()
    if aligned.empty or aligned.isna().all():
        return [
            {"date": d.date().isoformat(), "benchmark": float(base_index)}
            for d in curve_index
        ]

    first_valid = float(aligned.dropna().iloc[0]) if not aligned.dropna().empty else 1.0
    first_price = first_valid if abs(first_valid) > 1e-12 else 1.0
    aligned = aligned.fillna(first_price)
    index_values = (aligned / first_price) * base_index
    return [
        {"date": dt.date().isoformat(), "benchmark": float(value)}
        for dt, value in index_values.items()
    ]


def build_benchmark_curve(
    close_panel: pd.DataFrame,
    curve_dates: pd.DatetimeIndex,
    benchmark_symbol: str,
    base_index: float,
) -> list[dict[str, Any]]:
    """Public helper for rebuilding benchmark series from curve dates."""
    return _benchmark_curve(
        close_panel=close_panel,
        curve_dates=curve_dates,
        benchmark_symbol=benchmark_symbol,
        base_index=base_index,
    )


def _execution_return_panel(
    open_panel: pd.DataFrame,
    close_panel: pd.DataFrame,
    entry_price: str,
    exit_price: str,
) -> pd.DataFrame:
    entry_panel, exit_panel = _resolve_entry_exit_prices(
        entry_mode=entry_price,
        exit_mode=exit_price,
        open_panel=open_panel,
        close_panel=close_panel,
    )
    return (exit_panel / (entry_panel + 1e-12) - 1.0).replace([np.inf, -np.inf], np.nan)


def _resolve_entry_exit_prices(
    *,
    entry_mode: str,
    exit_mode: str,
    open_panel: pd.DataFrame,
    close_panel: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Resolve normalized entry/exit price panels for one-period returns."""
    vwap = (open_panel + close_panel) / 2.0
    entry_key = str(entry_mode or "next_open").strip().lower()
    exit_key = str(exit_mode or "close").strip().lower()

    entry_map: dict[str, pd.DataFrame] = {
        "next_open": open_panel,
        "close": close_panel.shift(1),
        "vwap_proxy": vwap,
    }
    exit_map: dict[str, pd.DataFrame] = {
        "close": close_panel,
        "next_open": open_panel,
        "next_close": close_panel.shift(-1),
        "vwap_proxy": vwap,
    }
    entry_panel = entry_map.get(entry_key, open_panel)
    exit_panel = exit_map.get(exit_key, close_panel)
    return entry_panel, exit_panel


def run_backtest(
    predictions: pd.DataFrame,
    open_panel: pd.DataFrame,
    close_panel: pd.DataFrame,
    start_date: date,
    end_date: date,
    constraints: BacktestConstraints,
    cost_bps: float,
    slippage_bps: float = 2.0,
    entry_price: str = "next_open",
    exit_price: str = "close",
    benchmark_symbol: str = "SPY",
    portfolio_mode: str = "long_only",
    mu_mapping: str = "quantile_mean_return",
    regime_policy: str = "fixed",
    rebalance_universe_context: dict[str, dict[str, Any]] | None = None,
    delisting_events: pd.DataFrame | None = None,
) -> BacktestResult:
    """Run monthly-rebalance mean-variance backtest with configurable execution prices."""
    if predictions.empty:
        raise ValueError("No predictions are available for backtest.")
    if close_panel.empty or open_panel.empty:
        raise ValueError("No price data is available for backtest.")

    pred = predictions.copy()
    pred["date"] = pd.to_datetime(pred["date"]).dt.tz_localize(None)
    if "score" not in pred.columns:
        pred["score"] = pd.to_numeric(
            pred.get("predicted_return", 0.0),
            errors="coerce",
        ).fillna(0.0)
    if "predicted_return" not in pred.columns:
        pred["predicted_return"] = pd.to_numeric(pred["score"], errors="coerce").fillna(0.0)
    pred["score"] = pd.to_numeric(pred["score"], errors="coerce").fillna(0.0)
    pred["predicted_return"] = pd.to_numeric(
        pred["predicted_return"], errors="coerce"
    ).fillna(0.0)
    pred_score_wide = pred.pivot(index="date", columns="symbol", values="score").sort_index()
    pred_return_wide = pred.pivot(
        index="date", columns="symbol", values="predicted_return"
    ).sort_index()

    close_panel = close_panel.copy()
    close_panel.index = pd.to_datetime(close_panel.index).tz_localize(None)
    open_panel = open_panel.copy()
    open_panel.index = pd.to_datetime(open_panel.index).tz_localize(None)
    open_panel = open_panel.reindex(
        index=close_panel.index, columns=close_panel.columns
    ).ffill()

    returns = _execution_return_panel(
        open_panel=open_panel,
        close_panel=close_panel,
        entry_price=entry_price,
        exit_price=exit_price,
    ).fillna(0.0)
    returns = apply_delisting_returns(
        returns,
        delisting_events if delisting_events is not None else pd.DataFrame(),
    )

    window_mask = (returns.index.date >= start_date) & (returns.index.date <= end_date)
    trade_dates = returns.index[window_mask]
    if len(trade_dates) == 0:
        price_min = str(returns.index.min().date()) if len(returns.index) > 0 else "N/A"
        price_max = str(returns.index.max().date()) if len(returns.index) > 0 else "N/A"
        raise ValueError(
            f"No trading days found in the selected date range "
            f"({start_date} ~ {end_date}). "
            f"Price data covers {price_min} ~ {price_max}."
        )

    trigger_rebalance_enabled = bool(getattr(constraints, "trigger_rebalance_enabled", False))
    monthly_forced_rebalance_dates = _month_end_rebalance_dates(trade_dates)
    monthly_forced_rebalance_set = set(monthly_forced_rebalance_dates)
    rebalance_dates = list(trade_dates) if trigger_rebalance_enabled else _monthly_rebalance_dates(trade_dates)
    if not rebalance_dates:
        raise ValueError("No rebalance dates were derived from trading dates.")

    symbols = sorted(list(set(pred_score_wide.columns).intersection(set(returns.columns))))
    if not symbols:
        pred_symbols_sample = list(pred_score_wide.columns[:5])
        price_symbols_sample = list(returns.columns[:5])
        raise ValueError(
            f"No overlapping symbols between predictions ({len(pred_score_wide.columns)} symbols) "
            f"and prices ({len(returns.columns)} symbols). "
            f"Sample prediction symbols: {pred_symbols_sample}. "
            f"Sample price symbols: {price_symbols_sample}. "
            f"Verify the same universe was used for training."
        )

    score_panel_for_mu = pred_score_wide[symbols].copy()
    alpha_ema_halflife_days = int(getattr(constraints, "alpha_ema_halflife_days", 0))
    if alpha_ema_halflife_days > 0:
        score_panel_for_mu = score_panel_for_mu.ewm(
            halflife=max(alpha_ema_halflife_days, 1), adjust=False
        ).mean()

    requested_mu_mapping = str(mu_mapping or "quantile_mean_return").strip().lower()
    alpha_mapping_mode = str(getattr(constraints, "alpha_mapping_mode", "legacy_score")).strip().lower()
    use_ic_vol_scaled = requested_mu_mapping == "ic_vol_scaled" or alpha_mapping_mode == "ic_vol_scaled"

    policy = get_portfolio_policy()
    universe_policy = get_universe_policy()
    defensive_settings = _resolve_defensive_settings(universe_policy, constraints)
    symbol_metadata_map = get_symbol_metadata_map()
    cash_symbol = str(policy.get("cash_symbol", "CASH")).strip().upper() or "CASH"
    policy_max_weight = float(
        universe_policy.get("portfolio_constraints", {}).get("max_weight_per_stock", 0.04)
    )
    effective_max_weight = min(
        apply_effective_max_weight(constraints.max_weight),
        policy_max_weight,
    )

    daily_rows: list[dict[str, Any]] = []
    weight_rows: list[dict[str, Any]] = []
    current_weights = np.zeros(len(symbols))
    turnover_values: list[float] = []
    strategy_returns: list[float] = []
    gross_returns: list[float] = []
    trading_costs: list[float] = []
    commission_costs: list[float] = []
    spread_costs: list[float] = []
    impact_costs: list[float] = []
    borrow_costs: list[float] = []
    cost_breakdown: list[dict[str, Any]] = []
    regime_mode_rows: list[dict[str, str]] = []
    regime_frame = _compute_regime_series(close_panel, returns.index, benchmark_symbol)
    latest_cash_weight = 0.0
    rebalance_history_rows: list[dict[str, Any]] = []
    constraint_violations: list[dict[str, Any]] = []
    rebalance_reports: list[dict[str, Any]] = []
    liquidity_clip_values: list[float] = []
    risk_contribution_values: list[float] = []
    risk_budget_scales: list[float] = []
    gross_exposure_series: list[float] = []
    net_exposure_series: list[float] = []
    long_exposure_series: list[float] = []
    short_exposure_series: list[float] = []
    ic_values: list[float] = []
    rank_ic_values: list[float] = []
    universe_stage_counts_latest: dict[str, int] = {}

    base_index = 100.0
    equity = base_index
    max_equity_seen = float(base_index)
    first_trade_date = pd.Timestamp(trade_dates[0])
    daily_rows.append(
        {
            "date": first_trade_date.date().isoformat(),
            "daily_return": 0.0,
            "equity": equity,
        }
    )

    commission_bps = (
        float(constraints.commission_bps)
        if constraints.commission_bps is not None
        else float(cost_bps)
    )
    half_spread_bps = (
        float(constraints.half_spread_bps)
        if constraints.half_spread_bps is not None
        else float(slippage_bps) / 2.0
    )
    impact_k = float(getattr(constraints, "impact_k", 0.0))
    borrow_bps = float(getattr(constraints, "borrow_bps", 0.0))
    current_cash_weight = 1.0
    for idx, rebalance_date in enumerate(rebalance_dates):
        rebalance_key = rebalance_date.date().isoformat()
        context = (rebalance_universe_context or {}).get(rebalance_key, {})
        available_pred_dates = score_panel_for_mu.index[score_panel_for_mu.index <= rebalance_date]
        if len(available_pred_dates) == 0:
            continue
        signal_date = pd.Timestamp(available_pred_dates.max())
        if bool(getattr(constraints, "leakage_guard", True)) and signal_date > rebalance_date:
            raise ValueError(
                f"leakage_detected: prediction date {signal_date.date()} exceeds rebalance date {rebalance_date.date()}"
            )
        hist = returns.loc[returns.index < rebalance_date, symbols].tail(constraints.lookback_days)
        score_snapshot = (
            score_panel_for_mu.reindex(index=[signal_date], columns=symbols)
            .iloc[0]
            .fillna(0.0)
            .astype(float)
        )
        raw_return_snapshot = (
            pred_return_wide.reindex(index=[signal_date], columns=symbols)
            .iloc[0]
            .fillna(0.0)
            .astype(float)
        )
        ic_hat = float(getattr(constraints, "ic_fallback", 0.03))
        if use_ic_vol_scaled:
            z_scores = _cross_sectional_zscore(score_snapshot)
            symbol_vol = (
                hist.std(ddof=0)
                .replace([np.inf, -np.inf], np.nan)
                .fillna(0.0)
                .clip(lower=1e-8)
            )
            ic_lookback_days = int(getattr(constraints, "ic_lookback_days", 252))
            ic_for_hat = ic_values[-ic_lookback_days:] if ic_lookback_days > 0 else ic_values
            ic_hat = _estimate_forward_ic(
                ic_history=ic_for_hat,
                halflife=int(getattr(constraints, "ic_ewma_halflife", 63)),
                clip_min=float(getattr(constraints, "ic_clip_min", -0.2)),
                clip_max=float(getattr(constraints, "ic_clip_max", 0.2)),
                fallback=float(getattr(constraints, "ic_fallback", 0.03)),
            )
            mu_series = (z_scores * symbol_vol * ic_hat).fillna(0.0)
        elif requested_mu_mapping == "z_score":
            mu_series = _cross_sectional_zscore(score_snapshot).fillna(0.0)
        elif requested_mu_mapping == "quantile_mean_return":
            mu_series = score_snapshot.fillna(0.0)
        else:
            mu_series = raw_return_snapshot.fillna(0.0)
        mu = mu_series.values.astype(float)
        cov = _estimate_covariance(
            hist_returns=hist,
            method=str(getattr(constraints, "cov_method", "sample")),
            ewma_halflife=int(getattr(constraints, "cov_ewma_halflife", 42)),
            shrinkage=float(getattr(constraints, "cov_shrinkage", 0.15)),
            pca_components=int(getattr(constraints, "cov_pca_components", 10)),
            pca_idio_floor=float(getattr(constraints, "cov_pca_idio_floor", 1e-6)),
        )
        trend_regime = "sideways"
        vol_regime = "mid"
        if not regime_frame.empty:
            regime_row = regime_frame.reindex([rebalance_date], method="ffill").iloc[0]
            trend_regime = str(regime_row.get("trend_regime", "sideways"))
            vol_regime = str(regime_row.get("vol_regime", "mid"))
        current_drawdown = max(0.0, 1.0 - float(equity / max(max_equity_seen, 1e-12)))
        risk_budget_scale = 1.0
        if regime_policy == "mixed":
            risk_budget_scale = _dynamic_risk_budget_scale(
                trend_regime=trend_regime,
                vol_regime=vol_regime,
                current_drawdown=current_drawdown,
            )
        risk_budget_scales.append(float(risk_budget_scale))
        dynamic_max_weight = max(0.005, float(effective_max_weight) * float(risk_budget_scale))
        dynamic_risk_aversion = float(constraints.risk_aversion) / max(
            float(risk_budget_scale), 0.35
        )
        allow_short = bool(portfolio_mode == "long_short" and not constraints.long_only)
        mode_used = "long_short" if allow_short else "long_only"
        if allow_short and regime_policy == "mixed":
            allow_short = _mixed_policy_allows_short(trend_regime, vol_regime)
            mode_used = "long_short" if allow_short else "long_only"

        binding_constraints: list[str] = []
        period_violations: list[dict[str, Any]] = []
        defensive_floor_target: float | None = None
        defensive_weight_realized: float | None = None
        defensive_core_weight: float | None = None
        defensive_credit_weight: float | None = None
        risk_weight_realized: float | None = None
        postcheck_iterations = 0
        postcheck_vol_ex_ante: float | None = None
        postcheck_cvar_ex_ante: float | None = None
        postcheck_actions: list[str] = []
        if allow_short:
            optimized = _optimize_weights(
                mu,
                cov,
                constraints,
                allow_short=allow_short,
                max_weight=dynamic_max_weight,
                risk_aversion=dynamic_risk_aversion,
            )
            optimized = np.clip(
                optimized,
                -dynamic_max_weight if allow_short else 0.0,
                dynamic_max_weight,
            )
            weight_sum = float(np.sum(optimized))
            cash_weight = 0.0
            if weight_sum != 1.0:
                optimized = optimized + ((1.0 - weight_sum) / max(len(optimized), 1))
                optimized = np.clip(optimized, -dynamic_max_weight, dynamic_max_weight)
            if regime_policy == "mixed" and risk_budget_scale < 0.999:
                binding_constraints.append("dynamic_risk_budget")
            if defensive_settings.enabled:
                binding_constraints.append("defensive_bucket_skipped_long_short")
            liquidity_clip_values.append(0.0)
            risk_contribution_values.append(0.0)
        else:
            eligible_symbols = set(context.get("u2_symbols", symbols))
            if defensive_settings.enabled and defensive_settings.allow_u2_override:
                eligible_symbols = eligible_symbols | {
                    symbol
                    for symbol in defensive_settings.defensive_symbol_set
                    if symbol in symbols
                }
            universe_stage_counts_latest = dict(
                context.get(
                    "stage_counts",
                    universe_stage_counts_latest,
                )
            )
            active_indices = [i for i, symbol in enumerate(symbols) if symbol in eligible_symbols]
            candidate_cap = _resolve_candidate_cap(universe_policy)
            candidate_cap_applied = False
            reserve_count = 0
            if defensive_settings.enabled:
                floor_for_reserve, _ = _compute_defensive_floor(
                    trend_regime=trend_regime,
                    vol_regime=vol_regime,
                    drawdown=current_drawdown,
                    settings=defensive_settings,
                )
                reserve_count = max(
                    1,
                    int(
                        math.ceil(
                            floor_for_reserve / max(float(effective_max_weight), 1e-9)
                        )
                    ),
                )
            if len(active_indices) > candidate_cap:
                active_indices = _select_candidate_indices(
                    active_indices,
                    mu=mu,
                    current_weights=current_weights,
                    candidate_cap=candidate_cap,
                )
                if defensive_settings.enabled and reserve_count > 0:
                    defensive_indices = {
                        i
                        for i, symbol in enumerate(symbols)
                        if symbol in defensive_settings.defensive_symbol_set
                    }
                    active_indices = _apply_defensive_candidate_reserve(
                        selected_indices=active_indices,
                        active_indices=[
                            i
                            for i, symbol in enumerate(symbols)
                            if symbol in eligible_symbols
                        ],
                        defensive_indices=defensive_indices,
                        mu=mu,
                        current_weights=current_weights,
                        candidate_cap=candidate_cap,
                        reserve_count=reserve_count,
                    )
                candidate_cap_applied = True
            optimized = np.zeros(len(symbols), dtype=float)
            if not active_indices:
                cash_weight = 1.0
                binding_constraints = ["no_eligible_symbols", "cash_buffer"]
                liquidity_clip_values.append(1.0)
                risk_contribution_values.append(0.0)
                period_violations.append(
                    {"type": "no_eligible_symbols", "date": rebalance_key}
                )
            else:
                active_symbols = [symbols[i] for i in active_indices]
                mu_active = mu[active_indices]
                cov_active = cov[np.ix_(active_indices, active_indices)]
                scenario_lookback = max(
                    int(getattr(constraints, "scenario_lookback_days", constraints.lookback_days)),
                    int(constraints.lookback_days),
                )
                scenario_frame = returns.loc[:rebalance_date, active_symbols].tail(
                    scenario_lookback
                )
                metric_rows = context.get("symbol_metrics", {})
                metadata_active: dict[str, dict[str, Any]] = {}
                for symbol in active_symbols:
                    metric_meta = {}
                    if isinstance(metric_rows, dict):
                        metric_meta = dict(metric_rows.get(symbol, {}))
                    symbol_meta = symbol_metadata_map.get(symbol, {})
                    if "adv20_usd" not in metric_meta:
                        price_hist = (
                            close_panel.loc[:rebalance_date, symbol].tail(20)
                            if symbol in close_panel.columns
                            else pd.Series(dtype=float)
                        )
                        px_mean = float(
                            pd.to_numeric(price_hist, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().mean()
                        ) if not price_hist.empty else 0.0
                        metric_meta["adv20_usd"] = max(px_mean * 100_000.0, 10_000_000.0)
                    metric_meta.setdefault("sector_l1", "other")
                    metric_meta.setdefault(
                        "country", "KR" if symbol.endswith(".KS") or symbol.endswith(".KQ") else "US"
                    )
                    metric_meta.setdefault("category_l2", str(symbol_meta.get("category_l2", "")).strip())
                    metric_meta.setdefault("category", str(symbol_meta.get("category", "")).strip())
                    metadata_active[symbol] = metric_meta

                beta_active = np.array(
                    [
                        float(
                            metadata_active.get(symbol, {}).get(
                                "beta_spy",
                                metadata_active.get(symbol, {}).get(
                                    "beta_market",
                                    metadata_active.get(symbol, {}).get("beta", 0.0),
                                ),
                            )
                        )
                        for symbol in active_symbols
                    ],
                    dtype=float,
                )
                current_active = current_weights[active_indices]
                cost_params = {
                    "commission_bps": commission_bps,
                    "half_spread_bps": half_spread_bps,
                    "impact_k": impact_k,
                    "turnover_penalty_mode": str(getattr(constraints, "turnover_penalty_mode", "none")),
                    "turnover_penalty": float(getattr(constraints, "turnover_penalty", 0.0)),
                }
                target_floor, risk_off_floor = _compute_defensive_floor(
                    trend_regime=trend_regime,
                    vol_regime=vol_regime,
                    drawdown=current_drawdown,
                    settings=defensive_settings,
                )
                two_bucket_payload: dict[str, Any] = {"used_two_bucket": False}
                if defensive_settings.enabled:
                    two_bucket_payload = _blend_two_bucket_weights(
                        active_symbols=active_symbols,
                        mu_active=mu_active,
                        cov_active=cov_active,
                        scenario_frame=scenario_frame,
                        current_active=current_active,
                        metadata_active=metadata_active,
                        constraints=constraints,
                        universe_policy=universe_policy,
                        dynamic_max_weight=dynamic_max_weight,
                        dynamic_risk_aversion=dynamic_risk_aversion,
                        cost_params=cost_params,
                        beta_active=beta_active,
                        target_floor=target_floor,
                        settings=defensive_settings,
                    )

                if bool(two_bucket_payload.get("used_two_bucket")):
                    optimized_active = np.asarray(two_bucket_payload.get("weights"), dtype=float)
                    binding_constraints = list(two_bucket_payload.get("binding_constraints", []))
                    if regime_policy == "mixed" and risk_budget_scale < 0.999:
                        binding_constraints.append("dynamic_risk_budget")
                    if candidate_cap_applied and "candidate_cap" not in binding_constraints:
                        binding_constraints.append("candidate_cap")
                    if risk_off_floor:
                        binding_constraints.append("defensive_regime_risk_off")

                    defensive_debug = dict(two_bucket_payload.get("debug", {}))
                    defensive_floor_target = float(
                        defensive_debug.get("defensive_floor_target", target_floor)
                    )
                    defensive_weight_realized = float(
                        defensive_debug.get("defensive_weight_realized", 0.0)
                    )
                    defensive_core_weight = float(
                        defensive_debug.get("defensive_core_weight", 0.0)
                    )
                    defensive_credit_weight = float(
                        defensive_debug.get("defensive_credit_weight", 0.0)
                    )
                    risk_weight_realized = float(
                        defensive_debug.get("risk_weight_realized", 0.0)
                    )
                    postcheck_iterations = int(
                        defensive_debug.get("postcheck_iterations", 0)
                    )
                    postcheck_vol_ex_ante = float(
                        defensive_debug.get("postcheck_vol_ex_ante", 0.0)
                    )
                    postcheck_cvar_ex_ante = float(
                        defensive_debug.get("postcheck_cvar_ex_ante", 0.0)
                    )
                    postcheck_actions = list(
                        defensive_debug.get("postcheck_actions", [])
                    )

                    period_violations = [
                        {"date": rebalance_key, **violation}
                        for violation in list(
                            two_bucket_payload.get("constraint_violations", [])
                        )
                    ]
                    liquidity_clip_values.append(
                        float(two_bucket_payload.get("liquidity_clip_ratio", 0.0))
                    )
                    risk_contribution_values.append(
                        float(two_bucket_payload.get("risk_contribution_max", 0.0))
                    )
                    sector_exposure_values = two_bucket_payload.get(
                        "sector_exposure", {}
                    )
                    country_exposure_values = two_bucket_payload.get(
                        "country_exposure", {}
                    )
                    estimated_cost_value = float(
                        two_bucket_payload.get("estimated_cost", 0.0)
                    )
                    gross_exposure_value = float(
                        two_bucket_payload.get("gross_exposure", 0.0)
                    )
                    net_exposure_value = float(two_bucket_payload.get("net_exposure", 0.0))
                    portfolio_beta_value = float(
                        two_bucket_payload.get("portfolio_beta", 0.0)
                    )
                else:
                    exposure_constraints = {
                        "allow_short": False,
                        "gross_exposure_max": float(getattr(constraints, "gross_exposure_max", 1.5)),
                        "net_exposure_min": float(getattr(constraints, "net_exposure_min", 0.0)),
                        "net_exposure_max": float(getattr(constraints, "net_exposure_max", 1.0)),
                        "sector_max_weight": float(getattr(constraints, "sector_max_weight", 0.35)),
                        "sector_neutral": bool(getattr(constraints, "sector_neutral", False)),
                        "beta_neutral": bool(getattr(constraints, "beta_neutral", False)),
                        "beta_tolerance": float(getattr(constraints, "beta_tolerance", 0.05)),
                        "target_beta": 0.0,
                    }

                    opt_result = optimize_weights_v2(
                        mu=mu_active,
                        cov=cov_active,
                        symbols=active_symbols,
                        metadata_by_symbol=metadata_active,
                        risk_aversion=dynamic_risk_aversion,
                        requested_max_weight=dynamic_max_weight,
                        policy=universe_policy,
                        nav=1.0,
                        optimizer_mode=str(constraints.optimizer_mode),
                        mv_optimizer_engine=str(
                            getattr(constraints, "mv_optimizer_engine", "legacy_slsqp")
                        ),
                        optimizer_strict=bool(getattr(constraints, "optimizer_strict", False)),
                        cvar_alpha=float(constraints.cvar_alpha),
                        cvar_lambda=float(constraints.cvar_lambda),
                        scenario_returns=scenario_frame.fillna(0.0).to_numpy(dtype=float),
                        current_weights=current_active,
                        cost_params=cost_params,
                        exposure_constraints=exposure_constraints,
                        beta_vector=beta_active,
                        target_vol=(
                            float(constraints.target_vol)
                            if getattr(constraints, "target_vol", None) is not None
                            else None
                        ),
                    )
                    optimized_active = np.asarray(opt_result.weights, dtype=float)
                    if regime_policy == "mixed" and risk_budget_scale < 0.999:
                        binding_constraints = list(opt_result.binding_constraints) + [
                            "dynamic_risk_budget"
                        ]
                    else:
                        binding_constraints = list(opt_result.binding_constraints)
                    if candidate_cap_applied and "candidate_cap" not in binding_constraints:
                        binding_constraints.append("candidate_cap")
                    period_violations = [
                        {"date": rebalance_key, **violation}
                        for violation in opt_result.constraint_violations
                    ]
                    liquidity_clip_values.append(float(opt_result.liquidity_clip_ratio))
                    risk_contribution_values.append(float(opt_result.risk_contribution_max))
                    sector_exposure_values = opt_result.sector_exposure
                    country_exposure_values = opt_result.country_exposure
                    estimated_cost_value = float(opt_result.estimated_cost)
                    gross_exposure_value = float(opt_result.gross_exposure)
                    net_exposure_value = float(opt_result.net_exposure)
                    portfolio_beta_value = float(opt_result.portfolio_beta)

                for local_idx, global_idx in enumerate(active_indices):
                    optimized[global_idx] = float(optimized_active[local_idx])
                cash_weight = float(max(0.0, 1.0 - float(np.sum(optimized_active))))
                latest_cash_weight = cash_weight
                rebalance_reports.append(
                    {
                        "date": rebalance_key,
                        "position_sizing_log": [
                            {
                                "symbol": symbol,
                                "weight": float(weight),
                                "sector": str(metadata_active.get(symbol, {}).get("sector_l1", "other")),
                                "country": str(metadata_active.get(symbol, {}).get("country", "US")),
                            }
                            for symbol, weight in zip(active_symbols, optimized_active, strict=False)
                            if float(weight) > 0
                        ],
                        "liquidity_constraint_report": [
                            {
                                "symbol": symbol,
                                "adv20_usd": float(
                                    metadata_active.get(symbol, {}).get("adv20_usd", 0.0)
                                ),
                                "weight_cap_adv": float(
                                    0.05
                                    * float(metadata_active.get(symbol, {}).get("adv20_usd", 0.0))
                                ),
                            }
                            for symbol in active_symbols
                        ],
                        "risk_contribution_report": [
                            {
                                "symbol": symbol,
                                "risk_contribution": float(value),
                            }
                            for symbol, value in zip(
                                active_symbols,
                                (
                                    np.zeros(len(active_symbols))
                                    if len(active_symbols) == 0
                                    else (
                                        optimized_active
                                        * (cov_active @ optimized_active)
                                        / max(
                                            float(
                                                np.sqrt(
                                                    max(
                                                        float(
                                                            optimized_active
                                                            @ cov_active
                                                            @ optimized_active
                                                        ),
                                                        1e-9,
                                                    )
                                                )
                                            ),
                                            1e-9,
                                        )
                                    )
                                ),
                                strict=False,
                            )
                        ],
                        "sector_exposure_report": [
                            {"sector": sector, "weight": float(weight)}
                            for sector, weight in sector_exposure_values.items()
                        ],
                        "country_exposure_report": [
                            {"country": country, "weight": float(weight)}
                            for country, weight in country_exposure_values.items()
                        ],
                        "binding_constraints": binding_constraints,
                        "estimated_cost": float(estimated_cost_value),
                        "gross_exposure": float(gross_exposure_value),
                        "net_exposure": float(net_exposure_value),
                        "portfolio_beta": float(portfolio_beta_value),
                        "optimizer_engine": str(
                            getattr(constraints, "mv_optimizer_engine", "legacy_slsqp")
                        ),
                        "cov_method": str(getattr(constraints, "cov_method", "sample")),
                        "ic_hat": float(ic_hat),
                        "defensive_floor_target": (
                            float(defensive_floor_target)
                            if defensive_floor_target is not None
                            else None
                        ),
                        "defensive_weight_realized": (
                            float(defensive_weight_realized)
                            if defensive_weight_realized is not None
                            else None
                        ),
                        "defensive_core_weight": (
                            float(defensive_core_weight)
                            if defensive_core_weight is not None
                            else None
                        ),
                        "defensive_credit_weight": (
                            float(defensive_credit_weight)
                            if defensive_credit_weight is not None
                            else None
                        ),
                        "risk_weight_realized": (
                            float(risk_weight_realized)
                            if risk_weight_realized is not None
                            else None
                        ),
                        "postcheck_iterations": int(postcheck_iterations),
                        "postcheck_vol_ex_ante": (
                            float(postcheck_vol_ex_ante)
                            if postcheck_vol_ex_ante is not None
                            else None
                        ),
                        "postcheck_cvar_ex_ante": (
                            float(postcheck_cvar_ex_ante)
                            if postcheck_cvar_ex_ante is not None
                            else None
                        ),
                        "postcheck_actions": postcheck_actions,
                    }
                )

        candidate_optimized = optimized.copy()
        triggered = True
        trigger_reason = "scheduled"
        utility_gain = 0.0
        estimated_trigger_cost = 0.0
        forced_month_end = pd.Timestamp(rebalance_date) in monthly_forced_rebalance_set
        if trigger_rebalance_enabled:
            if idx == 0:
                trigger_reason = "initial_rebalance"
            elif forced_month_end:
                trigger_reason = "month_end_forced"
            else:
                metric_rows_all = context.get("symbol_metrics", {})
                adv_for_trigger = np.array(
                    [
                        float(
                            (
                                metric_rows_all.get(symbol, {}).get("adv20_usd", 0.0)
                                if isinstance(metric_rows_all, dict)
                                else 0.0
                            )
                            or (
                                max(
                                    float(
                                        pd.to_numeric(
                                            close_panel.loc[:rebalance_date, symbol].tail(20),
                                            errors="coerce",
                                        )
                                        .replace([np.inf, -np.inf], np.nan)
                                        .dropna()
                                        .mean()
                                    )
                                    * 100_000.0,
                                    10_000_000.0,
                                )
                                if symbol in close_panel.columns
                                else 10_000_000.0
                            )
                        )
                        for symbol in symbols
                    ],
                    dtype=float,
                )
                trigger_cost_components = _estimate_trade_cost_components(
                    delta_w=(candidate_optimized - current_weights),
                    adv_usd=adv_for_trigger,
                    commission_bps=commission_bps,
                    half_spread_bps=half_spread_bps,
                    impact_k=impact_k,
                    nav=1.0,
                )
                estimated_trigger_cost = float(trigger_cost_components["total"])
                current_utility = float(
                    np.dot(mu, current_weights)
                    - dynamic_risk_aversion * float(current_weights @ cov @ current_weights)
                )
                candidate_utility = float(
                    np.dot(mu, candidate_optimized)
                    - dynamic_risk_aversion
                    * float(candidate_optimized @ cov @ candidate_optimized)
                )
                utility_gain = candidate_utility - current_utility - (
                    float(getattr(constraints, "trigger_cost_multiplier", 1.0))
                    * estimated_trigger_cost
                )
                trigger_threshold = float(
                    getattr(constraints, "trigger_threshold_bps", 10.0)
                ) / 10000.0
                triggered = bool(utility_gain > trigger_threshold)
                trigger_reason = "trigger_gain" if triggered else "no_trade_zone"
            if not triggered:
                optimized = current_weights.copy()
                cash_weight = float(current_cash_weight)
                period_violations = []
                if "no_trade_zone" not in binding_constraints:
                    binding_constraints.append("no_trade_zone")
        if rebalance_reports and str(rebalance_reports[-1].get("date", "")) == rebalance_key:
            rebalance_reports[-1]["triggered"] = bool(triggered)
            rebalance_reports[-1]["trigger_reason"] = str(trigger_reason)
            rebalance_reports[-1]["utility_gain"] = float(utility_gain)
            rebalance_reports[-1]["estimated_trigger_cost"] = float(estimated_trigger_cost)
            rebalance_reports[-1]["forced_rebalance"] = bool(forced_month_end)
        constraint_violations.extend(period_violations)
        turnover = float(np.abs(optimized - current_weights).sum())
        turnover_limit = float(getattr(constraints, "turnover_limit", 1.0))
        if turnover_limit >= 0.0 and turnover > turnover_limit + 1e-12:
            delta = optimized - current_weights
            scale = float(turnover_limit / max(turnover, 1e-12))
            optimized = current_weights + (delta * scale)
            turnover = float(np.abs(optimized - current_weights).sum())
            if allow_short:
                cash_weight = 0.0
            else:
                cash_weight = float(max(0.0, 1.0 - float(np.sum(optimized))))
                latest_cash_weight = cash_weight
            if "turnover_limit" not in binding_constraints:
                binding_constraints.append("turnover_limit")
        turnover_values.append(turnover)
        regime_mode_rows.append(
            {"date": rebalance_date.date().isoformat(), "mode": mode_used}
        )

        prev_map = {
            symbol: float(weight)
            for symbol, weight in zip(symbols, current_weights, strict=False)
            if float(weight) > 0
        }
        prev_map[cash_symbol] = float(current_cash_weight)
        curr_map = {
            symbol: float(weight)
            for symbol, weight in zip(symbols, optimized, strict=False)
            if float(weight) > 0
        }
        curr_map[cash_symbol] = float(cash_weight)
        added = sorted(
            [symbol for symbol, weight in curr_map.items() if symbol != cash_symbol and weight > 0 and prev_map.get(symbol, 0.0) <= 0]
        )
        sold = sorted(
            [symbol for symbol, weight in prev_map.items() if symbol != cash_symbol and weight > 0 and curr_map.get(symbol, 0.0) <= 0]
        )
        deltas = {
            symbol: float(curr_map.get(symbol, 0.0) - prev_map.get(symbol, 0.0))
            for symbol in set(prev_map) | set(curr_map)
            if symbol != cash_symbol
        }
        increases = sorted(
            [item for item in deltas.items() if item[1] > 0],
            key=lambda item: item[1],
            reverse=True,
        )[:5]
        decreases = sorted(
            [item for item in deltas.items() if item[1] < 0],
            key=lambda item: item[1],
        )[:5]
        rebalance_history_rows.append(
            {
                "date": rebalance_key,
                "previous_date": weight_rows[-1]["date"] if weight_rows else None,
                "added": added,
                "sold": sold,
                "top_weight_increases": [
                    {"symbol": symbol, "delta": float(delta)} for symbol, delta in increases
                ],
                "top_weight_decreases": [
                    {"symbol": symbol, "delta": float(delta)} for symbol, delta in decreases
                ],
                "turnover": float(turnover),
                "risk_budget_scale": float(risk_budget_scale),
                "triggered": bool(triggered),
                "trigger_reason": str(trigger_reason),
                "utility_gain": float(utility_gain),
                "estimated_trigger_cost": float(estimated_trigger_cost),
                "forced_rebalance": bool(forced_month_end),
                "ic_hat": float(ic_hat),
                "defensive_floor_target": (
                    float(defensive_floor_target)
                    if defensive_floor_target is not None
                    else None
                ),
                "defensive_weight_realized": (
                    float(defensive_weight_realized)
                    if defensive_weight_realized is not None
                    else None
                ),
                "defensive_core_weight": (
                    float(defensive_core_weight)
                    if defensive_core_weight is not None
                    else None
                ),
                "defensive_credit_weight": (
                    float(defensive_credit_weight)
                    if defensive_credit_weight is not None
                    else None
                ),
                "risk_weight_realized": (
                    float(risk_weight_realized) if risk_weight_realized is not None else None
                ),
                "postcheck_iterations": int(postcheck_iterations),
                "postcheck_vol_ex_ante": (
                    float(postcheck_vol_ex_ante)
                    if postcheck_vol_ex_ante is not None
                    else None
                ),
                "postcheck_cvar_ex_ante": (
                    float(postcheck_cvar_ex_ante)
                    if postcheck_cvar_ex_ante is not None
                    else None
                ),
                "postcheck_actions": list(postcheck_actions),
                "binding_constraints": binding_constraints,
            }
        )

        metric_rows_all = context.get("symbol_metrics", {})
        adv_full = np.array(
            [
                float(
                    (
                        metric_rows_all.get(symbol, {}).get("adv20_usd", 0.0)
                        if isinstance(metric_rows_all, dict)
                        else 0.0
                    )
                    or (
                        max(
                            float(
                                pd.to_numeric(
                                    close_panel.loc[:rebalance_date, symbol].tail(20),
                                    errors="coerce",
                                )
                                .replace([np.inf, -np.inf], np.nan)
                                .dropna()
                                .mean()
                            )
                            * 100_000.0,
                            10_000_000.0,
                        )
                        if symbol in close_panel.columns
                        else 10_000_000.0
                    )
                )
                for symbol in symbols
            ],
            dtype=float,
        )
        entry_cost_components = _estimate_trade_cost_components(
            delta_w=(optimized - current_weights),
            adv_usd=adv_full,
            commission_bps=commission_bps,
            half_spread_bps=half_spread_bps,
            impact_k=impact_k,
            nav=1.0,
        )

        next_date = (
            rebalance_dates[idx + 1]
            if idx + 1 < len(rebalance_dates)
            else pd.Timestamp(end_date)
        )
        period_mask = (returns.index > rebalance_date) & (returns.index <= next_date)
        period_dates = returns.index[period_mask]

        if len(period_dates) > 0:
            realized_first = returns.loc[period_dates[0], symbols].fillna(0.0).astype(float)
            mu_series = pd.Series(mu, index=symbols, dtype=float)
            valid_mask = np.isfinite(mu_series.values) & np.isfinite(realized_first.values)
            if int(valid_mask.sum()) >= 3:
                mu_valid = mu_series.values[valid_mask]
                ret_valid = realized_first.values[valid_mask]
                if np.std(mu_valid) > 1e-12 and np.std(ret_valid) > 1e-12:
                    ic_values.append(float(np.corrcoef(mu_valid, ret_valid)[0, 1]))
                rank_ic_stat = spearmanr(mu_valid, ret_valid, nan_policy="omit")
                if np.isfinite(rank_ic_stat.correlation):
                    rank_ic_values.append(float(rank_ic_stat.correlation))

        if len(period_dates) == 0:
            current_weights = optimized
            current_cash_weight = cash_weight
            continue

        holding_period_days = int(getattr(constraints, "holding_period_days", -1))
        if holding_period_days < 0:
            active_count = len(period_dates)
        elif holding_period_days == 0:
            active_count = min(1, len(period_dates))
        else:
            active_count = min(int(holding_period_days), len(period_dates))
        liquidate_early = bool(holding_period_days >= 0 and active_count < len(period_dates))
        exit_cost_components = (
            _estimate_trade_cost_components(
                delta_w=(-optimized),
                adv_usd=adv_full,
                commission_bps=commission_bps,
                half_spread_bps=half_spread_bps,
                impact_k=impact_k,
                nav=1.0,
            )
            if liquidate_early and active_count > 0
            else {"commission": 0.0, "spread": 0.0, "impact": 0.0, "total": 0.0}
        )

        for day_idx, trading_date in enumerate(period_dates):
            invested = bool(day_idx < active_count)
            weights_today = optimized if invested else np.zeros(len(symbols), dtype=float)
            ret_vec = returns.loc[trading_date, symbols].fillna(0.0).values.astype(float)
            gross_return = float(np.dot(weights_today, ret_vec))

            cost_commission = 0.0
            cost_spread = 0.0
            cost_impact = 0.0
            trading_cost = 0.0
            if day_idx == 0 and active_count > 0:
                cost_commission += float(entry_cost_components["commission"])
                cost_spread += float(entry_cost_components["spread"])
                cost_impact += float(entry_cost_components["impact"])
                trading_cost += float(entry_cost_components["total"])
            if liquidate_early and day_idx == active_count:
                cost_commission += float(exit_cost_components["commission"])
                cost_spread += float(exit_cost_components["spread"])
                cost_impact += float(exit_cost_components["impact"])
                trading_cost += float(exit_cost_components["total"])

            short_exposure = float(np.abs(np.minimum(weights_today, 0.0)).sum())
            borrow_cost = float(short_exposure * (borrow_bps / 1e4) / 252.0)
            net_return = gross_return - trading_cost - borrow_cost

            gross_exposure_series.append(float(np.abs(weights_today).sum()))
            long_exposure_series.append(float(np.maximum(weights_today, 0.0).sum()))
            short_exposure_series.append(short_exposure)
            net_exposure_series.append(float(np.sum(weights_today)))

            gross_returns.append(gross_return)
            trading_costs.append(trading_cost)
            commission_costs.append(cost_commission)
            spread_costs.append(cost_spread)
            impact_costs.append(cost_impact)
            borrow_costs.append(borrow_cost)
            strategy_returns.append(net_return)
            equity *= 1.0 + net_return
            daily_rows.append(
                {
                    "date": trading_date.date().isoformat(),
                    "daily_return": net_return,
                    "equity": equity,
                    "gross_return": gross_return,
                    "trading_cost": trading_cost,
                }
            )
            max_equity_seen = max(max_equity_seen, float(equity))
            cost_breakdown.append(
                {
                    "date": trading_date.date().isoformat(),
                    "gross_return": gross_return,
                    "trading_cost": trading_cost,
                    "commission_cost": cost_commission,
                    "spread_cost": cost_spread,
                    "impact_cost": cost_impact,
                    "borrow_cost": borrow_cost,
                    "net_return": net_return,
                }
            )

        weight_rows.append(
            {
                "date": rebalance_date.date().isoformat(),
                "weights": (
                    {
                        **{
                            symbol: float(weight)
                            for symbol, weight in zip(symbols, optimized, strict=False)
                        },
                        cash_symbol: float(cash_weight),
                    }
                    if mode_used == "long_only"
                    else {
                        symbol: float(weight)
                        for symbol, weight in zip(symbols, optimized, strict=False)
                    }
                ),
            }
        )
        if liquidate_early:
            current_weights = np.zeros(len(symbols), dtype=float)
            current_cash_weight = 1.0
            latest_cash_weight = 1.0
        else:
            current_weights = optimized
            current_cash_weight = cash_weight

    if not strategy_returns:
        raise ValueError("Backtest produced no return observations.")

    curve = pd.DataFrame(daily_rows)
    daily_returns = pd.Series(strategy_returns, dtype=float)
    equity_series = curve["equity"]
    metrics = _compute_metrics(daily_returns, equity_series)
    metrics["turnover"] = float(np.mean(turnover_values)) if turnover_values else 0.0
    metrics["monthly_turnover"] = float(np.mean(turnover_values)) if turnover_values else 0.0
    metrics["annual_turnover"] = float(metrics["monthly_turnover"] * 12.0)
    metrics["gross_return"] = (
        float(np.prod(1.0 + np.array(gross_returns)) - 1.0) if gross_returns else 0.0
    )
    metrics["total_cost"] = float(np.sum(trading_costs)) if trading_costs else 0.0
    metrics["total_commission"] = (
        float(np.sum(commission_costs)) if commission_costs else 0.0
    )
    metrics["total_spread_cost"] = float(np.sum(spread_costs)) if spread_costs else 0.0
    metrics["total_impact_cost"] = float(np.sum(impact_costs)) if impact_costs else 0.0
    metrics["total_borrow_cost"] = float(np.sum(borrow_costs)) if borrow_costs else 0.0
    metrics["net_return"] = float(equity_series.iloc[-1] / equity_series.iloc[0] - 1.0)
    tail = daily_returns.nsmallest(max(1, int(len(daily_returns) * 0.05)))
    metrics["cvar_95"] = float(tail.mean()) if not tail.empty else 0.0
    metrics["gross_exposure_avg"] = (
        float(np.mean(gross_exposure_series)) if gross_exposure_series else 0.0
    )
    metrics["net_exposure_avg"] = (
        float(np.mean(net_exposure_series)) if net_exposure_series else 0.0
    )
    metrics["long_exposure_avg"] = (
        float(np.mean(long_exposure_series)) if long_exposure_series else 0.0
    )
    metrics["short_exposure_avg"] = (
        float(np.mean(short_exposure_series)) if short_exposure_series else 0.0
    )
    metrics["ic_mean"] = float(np.mean(ic_values)) if ic_values else 0.0
    metrics["ic_ir"] = (
        float(np.mean(ic_values) / (np.std(ic_values, ddof=0) + 1e-12))
        if ic_values
        else 0.0
    )
    metrics["rank_ic_mean"] = float(np.mean(rank_ic_values)) if rank_ic_values else 0.0
    metrics["rank_ic_ir"] = (
        float(np.mean(rank_ic_values) / (np.std(rank_ic_values, ddof=0) + 1e-12))
        if rank_ic_values
        else 0.0
    )

    curve_dates = pd.to_datetime(curve["date"]).dt.tz_localize(None)
    benchmark_curve = _benchmark_curve(
        close_panel=close_panel,
        curve_dates=pd.DatetimeIndex(curve_dates),
        benchmark_symbol=benchmark_symbol,
        base_index=base_index,
    )

    return BacktestResult(
        metrics=metrics,
        equity_curve=curve.to_dict(orient="records"),
        monthly_returns=_monthly_returns_matrix(curve["date"], daily_returns),
        period_weights=weight_rows,
        benchmark_symbol=benchmark_symbol,
        benchmark_curve=benchmark_curve,
        base_index=base_index,
        cost_breakdown=cost_breakdown,
        consistency_checks=_consistency_checks(weight_rows, turnover_values),
        regime_mode_by_period=regime_mode_rows,
        effective_constraints={
            "max_weight_requested": float(constraints.max_weight),
            "max_weight_applied": float(effective_max_weight),
            "max_weight": float(effective_max_weight),
            "long_only": bool(constraints.long_only),
            "risk_aversion": float(constraints.risk_aversion),
            "lookback_days": float(constraints.lookback_days),
            "optimizer_mode_cvar": bool(str(constraints.optimizer_mode) == "cvar"),
            "mv_optimizer_engine": str(
                getattr(constraints, "mv_optimizer_engine", "legacy_slsqp")
            ),
            "optimizer_strict": bool(getattr(constraints, "optimizer_strict", False)),
            "cvar_alpha": float(constraints.cvar_alpha),
            "cvar_lambda": float(constraints.cvar_lambda),
            "scenario_lookback_days": float(constraints.scenario_lookback_days),
            "turnover_limit": float(getattr(constraints, "turnover_limit", 1.0)),
            "cov_method": str(getattr(constraints, "cov_method", "sample")),
            "cov_ewma_halflife": float(getattr(constraints, "cov_ewma_halflife", 42)),
            "cov_shrinkage": float(getattr(constraints, "cov_shrinkage", 0.15)),
            "cov_pca_components": float(getattr(constraints, "cov_pca_components", 10)),
            "cov_pca_idio_floor": float(
                getattr(constraints, "cov_pca_idio_floor", 1e-6)
            ),
            "commission_bps": float(commission_bps),
            "half_spread_bps": float(half_spread_bps),
            "impact_k": float(impact_k),
            "borrow_bps": float(borrow_bps),
            "gross_exposure_max": float(getattr(constraints, "gross_exposure_max", 1.5)),
            "net_exposure_min": float(getattr(constraints, "net_exposure_min", 0.0)),
            "net_exposure_max": float(getattr(constraints, "net_exposure_max", 1.0)),
            "sector_max_weight": float(getattr(constraints, "sector_max_weight", 0.35)),
            "holding_period_days": float(getattr(constraints, "holding_period_days", -1)),
            "leakage_guard": bool(getattr(constraints, "leakage_guard", True)),
            "mu_mapping": str(requested_mu_mapping),
            "alpha_mapping_mode": str(alpha_mapping_mode),
            "ic_lookback_days": float(getattr(constraints, "ic_lookback_days", 252)),
            "ic_ewma_halflife": float(
                getattr(constraints, "ic_ewma_halflife", 63)
            ),
            "ic_clip_min": float(getattr(constraints, "ic_clip_min", -0.2)),
            "ic_clip_max": float(getattr(constraints, "ic_clip_max", 0.2)),
            "ic_fallback": float(getattr(constraints, "ic_fallback", 0.03)),
            "alpha_ema_halflife_days": float(alpha_ema_halflife_days),
            "trigger_rebalance_enabled": bool(trigger_rebalance_enabled),
            "trigger_threshold_bps": float(
                getattr(constraints, "trigger_threshold_bps", 10.0)
            ),
            "trigger_cost_multiplier": float(
                getattr(constraints, "trigger_cost_multiplier", 1.0)
            ),
            "dynamic_risk_budget_mixed": bool(regime_policy == "mixed"),
            "risk_budget_scale_avg": float(np.mean(risk_budget_scales))
            if risk_budget_scales
            else 1.0,
            "risk_budget_scale_min": float(np.min(risk_budget_scales))
            if risk_budget_scales
            else 1.0,
            "defensive_bucket_enabled": bool(defensive_settings.enabled),
            "defensive_floor_mode": str(defensive_settings.floor_mode),
            "defensive_floor_fixed": float(defensive_settings.floor_fixed),
            "defensive_floor_low": float(defensive_settings.floor_low),
            "defensive_floor_mid": float(defensive_settings.floor_mid),
            "defensive_floor_high": float(defensive_settings.floor_high),
            "defensive_floor_risk_off": float(defensive_settings.floor_risk_off),
            "defensive_floor_max": float(defensive_settings.floor_max),
            "defensive_risk_off_drawdown": float(
                defensive_settings.risk_off_drawdown_threshold
            ),
            "defensive_credit_cap_abs_weight": float(
                defensive_settings.credit_cap_abs_weight
            ),
            "defensive_postcheck_enabled": bool(defensive_settings.postcheck_enabled),
            "defensive_postcheck_cvar_limit": (
                float(defensive_settings.postcheck_cvar_limit)
                if defensive_settings.postcheck_cvar_limit is not None
                else None
            ),
            "defensive_postcheck_vol_limit": (
                float(defensive_settings.postcheck_vol_limit)
                if defensive_settings.postcheck_vol_limit is not None
                else None
            ),
            "sector_cap": float(
                universe_policy.get("portfolio_constraints", {}).get("sector_cap", 0.25)
            ),
            "country_cap": float(
                universe_policy.get("portfolio_constraints", {}).get("country_cap", 0.35)
            ),
            "candidate_cap": float(_resolve_candidate_cap(universe_policy)),
        },
        cash_weight=float(latest_cash_weight),
        rebalance_history_summary=rebalance_history_rows,
        constraint_violations=constraint_violations,
        liquidity_clip_ratio=(
            float(np.mean(liquidity_clip_values)) if liquidity_clip_values else 0.0
        ),
        risk_contribution_max=(
            float(np.max(risk_contribution_values)) if risk_contribution_values else 0.0
        ),
        universe_stage_counts=universe_stage_counts_latest,
        rebalance_reports=rebalance_reports,
    )
