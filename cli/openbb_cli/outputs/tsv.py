"""TSV output adapter — line-oriented, ANSI-free, safe for shell pipelines."""

from __future__ import annotations

import sys
from typing import Any

import pandas as pd


def _coerce_results(results: Any) -> pd.DataFrame | None:
    """Coerce the ``results`` payload of an OBBject into a DataFrame."""
    if isinstance(results, pd.DataFrame):
        return results
    if isinstance(results, list):
        return pd.DataFrame(results)
    if isinstance(results, dict):
        return pd.DataFrame([results])
    return None


def _to_dataframe(data: Any) -> pd.DataFrame | None:
    """Best-effort coerce arbitrary CLI payloads into a DataFrame."""
    if hasattr(data, "model_dump"):
        results = data.model_dump().get("results")
        return _coerce_results(results) if results is not None else None
    if isinstance(data, pd.DataFrame):
        return data
    if isinstance(data, pd.Series):
        return data.to_frame()
    if isinstance(data, dict):
        return pd.DataFrame.from_dict(data, orient="columns")
    if isinstance(data, (list, tuple)):
        return pd.DataFrame(list(data))
    return None


class TsvOutput:
    """TSV output adapter — emits the complete DataFrame as TSV to stdout."""

    def display(
        self,
        data: Any,
        title: str = "",
        export: bool = False,
        chart: bool = False,
    ) -> None:
        """Print the data as TSV. No styling, no truncation."""
        if export:
            return
        if chart and hasattr(data, "chart") and data.chart is not None:
            return
        df = _to_dataframe(data)
        if df is not None:
            df.to_csv(sys.stdout, sep="\t", index=False)
            sys.stdout.flush()
            return
        if hasattr(data, "model_dump"):
            return
        sys.stdout.write(f"{data!r}\n")
        sys.stdout.flush()
