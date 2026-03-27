"""Safe AST-based expression engine for macro and market series."""

from __future__ import annotations

import ast
import re
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

Resolver = Callable[[str], pd.Series]

_ALLOWED_FUNCTIONS = {
    "zscore",
    "log",
    "diff",
    "pct_change",
    "lag",
    "lead",
    "rolling_mean",
    "rolling_std",
    "rolling_min",
    "rolling_max",
    "rolling_corr",
    "rolling_beta",
    "ema",
    "cagr",
    "yoy",
    "mom",
    "annualized_mom",
    "qoq_saar",
    "percentile",
    "base100",
    "real_rate",
    "spread",
    "ratio",
}
_ALLOWED_KEYWORD_NAMES = {
    "n",
    "win",
}
_TOKEN_PATTERN = re.compile(r"\b(?:FRED:[A-Za-z0-9_]+|[A-Za-z][A-Za-z0-9_.]*)\b")


class MacroExpressionError(ValueError):
    """Expression parser/evaluator error."""


@dataclass(slots=True)
class EvaluatedExpression:
    """Expression evaluation output."""

    series: pd.Series
    dependencies: list[str]


def _to_series(value: pd.Series | float | int, reference: pd.Series | None = None) -> pd.Series:
    if isinstance(value, pd.Series):
        return pd.to_numeric(value, errors="coerce").astype(float)
    scalar = float(value)
    if reference is not None and not reference.empty:
        return pd.Series(scalar, index=reference.index, dtype=float)
    return pd.Series([scalar], dtype=float)


def _align_binary(left: pd.Series, right: pd.Series) -> tuple[pd.Series, pd.Series]:
    a, b = left.align(right, join="outer")
    return a.sort_index(), b.sort_index()


def _rolling_zscore(series: pd.Series, window: int) -> pd.Series:
    if window <= 1:
        std = float(series.std(ddof=0))
        if std <= 0 or np.isnan(std):
            return pd.Series(0.0, index=series.index)
        return (series - float(series.mean())) / (std + 1e-12)
    mean = series.rolling(window, min_periods=max(2, window // 5)).mean()
    std = series.rolling(window, min_periods=max(2, window // 5)).std(ddof=0)
    std = std.replace(0, np.nan)
    return (series - mean) / (std + 1e-12)


def _infer_observation_step_days(series: pd.Series) -> float:
    if series.size < 3:
        return 30.0
    diffs = pd.Series(series.index).sort_values().diff().dropna()
    if diffs.empty:
        return 30.0
    median = diffs.median()
    return max(float(median.total_seconds()) / 86_400.0, 1.0)


def _seasonal_periods(series: pd.Series) -> int:
    step = _infer_observation_step_days(series)
    if step <= 2:
        return 252
    if step <= 9:
        return 52
    if step <= 40:
        return 12
    return 4


def _annualize_factor(series: pd.Series) -> float:
    step = _infer_observation_step_days(series)
    if step <= 2:
        return 252.0
    if step <= 9:
        return 52.0
    if step <= 40:
        return 12.0
    return 4.0


def _rolling_percentile(series: pd.Series, window: int) -> pd.Series:
    min_periods = max(5, window // 5)
    return series.rolling(window, min_periods=min_periods).apply(
        lambda arr: float((np.asarray(arr, dtype=float) <= np.asarray(arr, dtype=float)[-1]).sum() / len(arr)),
        raw=True,
    )


def _base100(series: pd.Series) -> pd.Series:
    clean = series.dropna()
    if clean.empty:
        return pd.Series(dtype=float)
    base = float(clean.iloc[0])
    if abs(base) <= 1e-12:
        return pd.Series(np.nan, index=series.index, dtype=float)
    return (series / base) * 100.0


def _cagr(series: pd.Series) -> pd.Series:
    clean = series.dropna()
    if clean.empty:
        return pd.Series(dtype=float)
    start_value = float(clean.iloc[0])
    if start_value <= 0:
        return pd.Series(np.nan, index=series.index, dtype=float)
    start_ts = clean.index[0]
    elapsed_years = (series.index.to_series().sub(start_ts).dt.total_seconds() / (365.25 * 24 * 3600)).clip(lower=1 / 365.25)
    return (series / start_value).pow(1.0 / elapsed_years) - 1.0


def _call_function(name: str, args: list[pd.Series | float], kwargs: dict[str, pd.Series | float]) -> pd.Series:
    lower = name.lower()
    if lower not in _ALLOWED_FUNCTIONS:
        raise MacroExpressionError(f"Unsupported function: {name}")

    if lower == "log":
        if len(args) != 1:
            raise MacroExpressionError("log(x) expects exactly one argument.")
        s = _to_series(args[0])
        return np.log(s.where(s > 0))

    if lower == "zscore":
        if len(args) != 1:
            raise MacroExpressionError("zscore(x, win=252) expects one series argument.")
        window = int(kwargs.get("win", 252))
        s = _to_series(args[0])
        return _rolling_zscore(s, max(1, window))

    if lower == "diff":
        if len(args) != 1:
            raise MacroExpressionError("diff(x, n=1) expects one series argument.")
        n = int(kwargs.get("n", 1))
        return _to_series(args[0]).diff(max(1, n))

    if lower == "pct_change":
        if len(args) != 1:
            raise MacroExpressionError("pct_change(x, n=1) expects one series argument.")
        n = int(kwargs.get("n", 1))
        return _to_series(args[0]).pct_change(periods=max(1, n), fill_method=None)

    if lower in {"lag", "lead"}:
        if len(args) != 1:
            raise MacroExpressionError(f"{name}(x, n=1) expects one series argument.")
        n = int(kwargs.get("n", 1))
        series = _to_series(args[0])
        return series.shift(max(1, n) if lower == "lag" else -max(1, n))

    if lower in {"rolling_mean", "rolling_std", "rolling_min", "rolling_max"}:
        if len(args) != 2:
            raise MacroExpressionError(f"{name}(x, win) expects two arguments.")
        s = _to_series(args[0])
        win = max(1, int(float(args[1])))
        min_periods = max(2, win // 4)
        if lower == "rolling_mean":
            return s.rolling(win, min_periods=min_periods).mean()
        if lower == "rolling_std":
            return s.rolling(win, min_periods=min_periods).std(ddof=0)
        if lower == "rolling_min":
            return s.rolling(win, min_periods=min_periods).min()
        return s.rolling(win, min_periods=min_periods).max()

    if lower in {"rolling_corr", "rolling_beta"}:
        if len(args) != 3:
            raise MacroExpressionError(f"{name}(x, y, win) expects three arguments.")
        x = _to_series(args[0])
        y = _to_series(args[1])
        x_aligned, y_aligned = _align_binary(x, y)
        win = max(2, int(float(args[2])))
        min_periods = max(5, win // 4)
        if lower == "rolling_corr":
            return x_aligned.rolling(win, min_periods=min_periods).corr(y_aligned)
        cov = x_aligned.rolling(win, min_periods=min_periods).cov(y_aligned)
        var = y_aligned.rolling(win, min_periods=min_periods).var(ddof=0).replace(0, np.nan)
        return cov / (var + 1e-12)

    if lower == "ema":
        if len(args) != 2:
            raise MacroExpressionError("ema(x, span) expects two arguments.")
        s = _to_series(args[0])
        span = max(1, int(float(args[1])))
        return s.ewm(span=span, adjust=False, min_periods=1).mean()

    if lower == "yoy":
        if len(args) != 1:
            raise MacroExpressionError("yoy(x) expects one series argument.")
        s = _to_series(args[0])
        periods = _seasonal_periods(s)
        return s.pct_change(periods=periods, fill_method=None)

    if lower == "mom":
        if len(args) != 1:
            raise MacroExpressionError("mom(x, n=1) expects one series argument.")
        n = int(kwargs.get("n", 1))
        return _to_series(args[0]).pct_change(periods=max(1, n), fill_method=None)

    if lower == "annualized_mom":
        if len(args) != 1:
            raise MacroExpressionError("annualized_mom(x) expects one series argument.")
        s = _to_series(args[0])
        factor = _annualize_factor(s)
        mom = s.pct_change(fill_method=None)
        return (1.0 + mom).pow(factor) - 1.0

    if lower == "qoq_saar":
        if len(args) != 1:
            raise MacroExpressionError("qoq_saar(x) expects one series argument.")
        s = _to_series(args[0])
        qoq = s.pct_change(periods=1, fill_method=None)
        return (1.0 + qoq).pow(4.0) - 1.0

    if lower == "percentile":
        if len(args) != 1:
            raise MacroExpressionError("percentile(x, win=252) expects one series argument.")
        s = _to_series(args[0])
        window = max(5, int(kwargs.get("win", max(20, _seasonal_periods(s) * 5))))
        return _rolling_percentile(s, window)

    if lower == "base100":
        if len(args) != 1:
            raise MacroExpressionError("base100(x) expects one series argument.")
        return _base100(_to_series(args[0]))

    if lower == "cagr":
        if len(args) != 1:
            raise MacroExpressionError("cagr(x) expects one series argument.")
        return _cagr(_to_series(args[0]))

    if lower in {"real_rate", "spread", "ratio"}:
        if len(args) != 2:
            raise MacroExpressionError(f"{name}(x, y) expects two arguments.")
        x = _to_series(args[0])
        y = _to_series(args[1])
        x_aligned, y_aligned = _align_binary(x, y)
        if lower == "ratio":
            return x_aligned / (y_aligned.replace(0, np.nan) + 1e-12)
        return x_aligned - y_aligned

    raise MacroExpressionError(f"Unsupported function: {name}")


def _normalize_expression(expr: str) -> tuple[str, dict[str, str], list[str]]:
    """Replace symbol-like tokens with AST-safe placeholders."""
    token_map: dict[str, str] = {}
    dependencies: list[str] = []
    counter = 0

    def replacer(match: re.Match[str]) -> str:
        nonlocal counter
        token = match.group(0)
        if token.lower() in _ALLOWED_FUNCTIONS or token in _ALLOWED_KEYWORD_NAMES:
            return token.lower()
        # Preserve FRED: prefix tokens exactly, uppercase others for consistency.
        canonical = token if token.upper().startswith("FRED:") else token.upper()
        placeholder = f"__sym_{counter}"
        counter += 1
        token_map[placeholder] = canonical
        dependencies.append(canonical)
        return placeholder

    normalized = _TOKEN_PATTERN.sub(replacer, expr.strip())
    dedup_deps: list[str] = []
    seen: set[str] = set()
    for dep in dependencies:
        if dep in seen:
            continue
        seen.add(dep)
        dedup_deps.append(dep)
    return normalized, token_map, dedup_deps


def _evaluate_ast(node: ast.AST, token_map: dict[str, str], resolver: Resolver) -> pd.Series | float:
    if isinstance(node, ast.Expression):
        return _evaluate_ast(node.body, token_map, resolver)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise MacroExpressionError("Only numeric constants are allowed.")

    if isinstance(node, ast.Name):
        name = node.id
        if name not in token_map:
            raise MacroExpressionError(f"Unknown identifier: {name}")
        series = resolver(token_map[name])
        if series.empty:
            raise MacroExpressionError(f"No data found for symbol: {token_map[name]}")
        return series.sort_index()

    if isinstance(node, ast.UnaryOp):
        operand = _evaluate_ast(node.operand, token_map, resolver)
        operand_series = _to_series(operand)
        if isinstance(node.op, ast.USub):
            return -operand_series
        if isinstance(node.op, ast.UAdd):
            return operand_series
        raise MacroExpressionError("Unsupported unary operator.")

    if isinstance(node, ast.BinOp):
        left_raw = _evaluate_ast(node.left, token_map, resolver)
        right_raw = _evaluate_ast(node.right, token_map, resolver)
        left = _to_series(left_raw, reference=_to_series(right_raw) if isinstance(right_raw, pd.Series) else None)
        right = _to_series(right_raw, reference=left if isinstance(left, pd.Series) else None)
        left, right = _align_binary(left, right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / (right.replace(0, np.nan) + 1e-12)
        raise MacroExpressionError("Unsupported binary operator.")

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise MacroExpressionError("Only simple function calls are allowed.")
        func_name = node.func.id
        args = [_evaluate_ast(arg, token_map, resolver) for arg in node.args]
        kwargs = {}
        for kw in node.keywords:
            if kw.arg is None:
                raise MacroExpressionError("Star-args are not allowed.")
            kwargs[kw.arg] = _evaluate_ast(kw.value, token_map, resolver)
        parsed_args: list[pd.Series | float] = []
        for arg in args:
            if isinstance(arg, pd.Series):
                parsed_args.append(arg)
            elif isinstance(arg, (int, float)):
                parsed_args.append(float(arg))
            else:
                raise MacroExpressionError("Invalid argument type.")
        parsed_kwargs: dict[str, pd.Series | float] = {}
        for key, value in kwargs.items():
            if isinstance(value, pd.Series):
                parsed_kwargs[key] = value
            elif isinstance(value, (int, float)):
                parsed_kwargs[key] = float(value)
            else:
                raise MacroExpressionError("Invalid keyword argument type.")
        return _call_function(func_name, parsed_args, parsed_kwargs)

    raise MacroExpressionError("Unsupported expression syntax.")


def evaluate_expression(expr: str, resolver: Resolver) -> EvaluatedExpression:
    """Parse and evaluate expression safely."""
    if any(forbidden in expr for forbidden in ["__", "import", "lambda", "eval", "exec", "[", "]", "{", "}"]):
        raise MacroExpressionError("Expression contains forbidden token.")

    normalized, token_map, dependencies = _normalize_expression(expr)
    try:
        parsed = ast.parse(normalized, mode="eval")
    except SyntaxError as exc:
        raise MacroExpressionError("Invalid expression syntax.") from exc

    # Explicitly disallow nodes that can escape the sandbox.
    for node in ast.walk(parsed):
        if isinstance(node, (ast.Attribute, ast.Subscript, ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
            raise MacroExpressionError("Unsupported expression construct.")
        if isinstance(node, ast.Call) and not isinstance(node.func, ast.Name):
            raise MacroExpressionError("Unsupported call construct.")

    result = _evaluate_ast(parsed, token_map, resolver)
    series = _to_series(result).sort_index()
    return EvaluatedExpression(series=series, dependencies=dependencies)
