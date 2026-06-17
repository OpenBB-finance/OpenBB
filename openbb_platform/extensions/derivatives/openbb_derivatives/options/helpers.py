"""Helpers for options endpoints."""

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.standard_models.options_chains import OptionsChainsData


def options_data_to_df(data: list[Data] | Data, underlying_price: float | None = None):
    """Normalize options chain inputs into a DataFrame."""
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame

    if isinstance(data, OptionsChainsData):
        df = DataFrame(data.model_dump(exclude_none=True, exclude_unset=True))
        if underlying_price is None and data.last_price is not None:
            underlying_price = data.last_price
    elif isinstance(data, DataFrame):
        df = DataFrame(data.copy())
    elif isinstance(data, dict):
        df = DataFrame(
            data if all(isinstance(value, list) for value in data.values()) else [data]
        )
    elif isinstance(data, list):
        if all(isinstance(record, dict) for record in data):
            df = DataFrame(data)
        elif all(isinstance(record, Data) for record in data):
            df = DataFrame(
                [
                    record.model_dump(exclude_none=True, exclude_unset=True)
                    for record in data
                ]
            )
        else:
            df = DataFrame()
    elif isinstance(data, Data):
        df = DataFrame([data.model_dump(exclude_none=True, exclude_unset=True)])
    else:
        df = DataFrame()

    if not df.empty and underlying_price is not None:
        df["underlying_price"] = underlying_price

    return df


def prepare_options_exposure_df(df, underlying_price: float | None = None):
    """Prepare chain data for exposure aggregation."""
    # pylint: disable=import-outside-toplevel
    from datetime import datetime

    from pandas import Timestamp, to_datetime, to_numeric

    options = df.copy()

    if "option_type" not in options.columns:
        raise OpenBBError("Error: No option_type field found.")
    if "strike" not in options.columns:
        raise OpenBBError("Error: No strike field found.")

    options["option_type"] = options["option_type"].astype(str).str.lower()
    options = options[options["option_type"].isin(["call", "put"])]

    if "open_interest" not in options.columns:
        options["open_interest"] = 0
    if "volume" not in options.columns:
        options["volume"] = 0
    if "contract_size" not in options.columns:
        options["contract_size"] = 100

    numeric_cols = [
        "strike",
        "open_interest",
        "volume",
        "contract_size",
        "delta",
        "gamma",
        "dte",
        "underlying_price",
    ]
    for col in [col for col in numeric_cols if col in options.columns]:
        options[col] = to_numeric(options[col], errors="coerce")

    if underlying_price is not None:
        options["underlying_price"] = underlying_price
    elif "underlying_price" in options.columns:
        last_price = options["underlying_price"].dropna()
        if not last_price.empty:
            options["underlying_price"] = last_price.iloc[0]

    if "expiration" in options.columns:
        options["expiration"] = to_datetime(options["expiration"], errors="coerce")
    if "eod_date" in options.columns:
        options["eod_date"] = to_datetime(options["eod_date"], errors="coerce")

    if "expiration" in options.columns and (
        "dte" not in options.columns or options["dte"].isna().any()
    ):
        if "eod_date" in options.columns and options["eod_date"].notna().any():
            derived_dte = (options["expiration"] - options["eod_date"]).dt.days
        else:
            today = Timestamp(datetime.today().date())
            derived_dte = (options["expiration"] - today).dt.days
        options["dte"] = (
            derived_dte
            if "dte" not in options.columns
            else options["dte"].fillna(derived_dte)
        )

    options["open_interest"] = options["open_interest"].fillna(0)
    options["volume"] = options["volume"].fillna(0)
    options["contract_size"] = options["contract_size"].fillna(100)

    if _can_calculate_exposure(options, "delta"):
        options["DEX"] = (
            options["delta"]
            * options["contract_size"]
            * options["open_interest"]
            * options["underlying_price"]
        ).fillna(0)

    if _can_calculate_exposure(options, "gamma"):
        gex = (
            options["gamma"]
            * options["contract_size"]
            * options["open_interest"]
            * (options["underlying_price"] * options["underlying_price"])
            * 0.01
        ).fillna(0)
        options["GEX"] = gex.where(options["option_type"] == "call", -gex)

    return options.reset_index(drop=True)


def has_underlying_price(options) -> bool:
    """Return whether a prepared options DataFrame has a usable underlying price."""
    return (
        "underlying_price" in options.columns
        and options["underlying_price"].notna().any()
    )


def build_exposure_rows(options, by: Literal["expiration", "strike"]):
    """Build per-expiration or per-strike exposure rows."""
    records: list[dict[str, Any]] = []
    metrics = ["open_interest", "volume"]

    if "DEX" in options.columns:
        metrics.append("DEX")
    if "GEX" in options.columns:
        metrics.append("GEX")

    grouped = options.groupby(by, dropna=False, sort=True)

    for key, group in grouped:
        row: dict[str, Any] = {by: _as_native(key)}

        for metric in metrics:
            calls = _sum_metric(group, metric, "call")
            puts = _sum_metric(group, metric, "put")
            prefix = metric.lower()
            row[f"call_{prefix}"] = calls
            row[f"put_{prefix}"] = puts
            row[f"total_{prefix}"] = _total_metric(metric, calls, puts)
            row[f"net_{prefix}"] = (
                calls - puts if metric in ["open_interest", "volume"] else calls + puts
            )
            row[f"put_call_ratio_{prefix}"] = _safe_ratio(abs(puts), abs(calls))

        records.append(row)

    return records


def build_exposure_summary(
    options, rows: list[dict[str, Any]], by: str
) -> dict[str, Any]:
    """Build global exposure summary and wall levels."""
    summary: dict[str, Any] = {
        "by": by,
        "records": len(rows),
        "call_open_interest": _sum_metric(options, "open_interest", "call"),
        "put_open_interest": _sum_metric(options, "open_interest", "put"),
        "call_volume": _sum_metric(options, "volume", "call"),
        "put_volume": _sum_metric(options, "volume", "put"),
    }
    summary["total_open_interest"] = (
        summary["call_open_interest"] + summary["put_open_interest"]
    )
    summary["total_volume"] = summary["call_volume"] + summary["put_volume"]
    summary["put_call_ratio_open_interest"] = _safe_ratio(
        summary["put_open_interest"], summary["call_open_interest"]
    )
    summary["put_call_ratio_volume"] = _safe_ratio(
        summary["put_volume"], summary["call_volume"]
    )

    for metric in ["DEX", "GEX"]:
        if metric not in options.columns:
            continue
        metric_key = metric.lower()
        summary[f"call_{metric_key}"] = _sum_metric(options, metric, "call")
        summary[f"put_{metric_key}"] = _sum_metric(options, metric, "put")
        summary[f"total_{metric_key}"] = _total_metric(
            metric,
            summary[f"call_{metric_key}"],
            summary[f"put_{metric_key}"],
        )
        summary[f"net_{metric_key}"] = (
            summary[f"call_{metric_key}"] + summary[f"put_{metric_key}"]
        )

    if "GEX" in options.columns and "strike" in options.columns:
        gex_by_strike = options.groupby("strike", dropna=False)["GEX"].sum()
        call_gex_by_strike = (
            options[options["option_type"] == "call"].groupby("strike")["GEX"].sum()
        )
        put_gex_by_strike = (
            options[options["option_type"] == "put"].groupby("strike")["GEX"].sum()
        )

        if not gex_by_strike.empty:
            gamma_wall = gex_by_strike.abs().idxmax()
            summary["gamma_wall"] = _as_native(gamma_wall)
            summary["gamma_wall_gex"] = float(gex_by_strike.loc[gamma_wall])
        if not call_gex_by_strike.empty:
            call_wall = call_gex_by_strike.idxmax()
            summary["call_gamma_wall"] = _as_native(call_wall)
            summary["call_gamma_wall_gex"] = float(call_gex_by_strike.loc[call_wall])
        if not put_gex_by_strike.empty:
            put_wall = put_gex_by_strike.idxmin()
            summary["put_gamma_wall"] = _as_native(put_wall)
            summary["put_gamma_wall_gex"] = float(put_gex_by_strike.loc[put_wall])

    return {key: _as_native(value) for key, value in summary.items()}


def _can_calculate_exposure(options, greek: Literal["delta", "gamma"]) -> bool:
    """Return whether the greek and underlying price can produce exposure."""
    return (
        greek in options.columns
        and options[greek].notna().any()
        and has_underlying_price(options)
    )


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    """Return a rounded ratio when the denominator is non-zero."""
    return round(numerator / denominator, 4) if denominator else None


def _total_metric(metric: str, calls: float, puts: float) -> float:
    """Return the metric total using gross totals for signed exposure metrics."""
    return abs(calls) + abs(puts) if metric in ["DEX", "GEX"] else calls + puts


def _as_native(value: Any) -> Any:
    """Convert Pandas/Numpy values to API-safe Python values."""
    # pylint: disable=import-outside-toplevel
    from pandas import isna

    if isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    if hasattr(value, "date"):
        return value.date().isoformat()
    return value


def _sum_metric(df, metric: str, option_type: Literal["call", "put"] | None = None):
    """Sum a metric, optionally for one side of the chain."""
    if metric not in df.columns:
        return 0
    if option_type:
        df = df[df["option_type"] == option_type]
    return float(df[metric].sum())
