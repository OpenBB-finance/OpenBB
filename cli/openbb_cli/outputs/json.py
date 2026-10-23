"""JSON output adapter — emits raw JSON to stdout, no console styling."""

from __future__ import annotations

import json
import sys
from typing import Any

import pandas as pd


def _to_serializable(data: Any) -> Any:
    if hasattr(data, "model_dump"):
        return data.model_dump(exclude_unset=True, exclude_none=True).get("results")
    if isinstance(data, pd.DataFrame):
        return data.to_dict(orient="records")
    if isinstance(data, pd.Series):
        return data.to_dict()
    return data


class JsonOutput:
    """JSON output adapter — full payload, indented, written to stdout."""

    def display(
        self,
        data: Any,
        title: str = "",
        export: bool = False,
        chart: bool = False,
    ) -> None:
        """Serialize ``data`` as JSON to stdout."""
        if export:
            return
        results = _to_serializable(data)
        try:
            output = json.dumps(results, indent=2, default=str)
        except (TypeError, ValueError) as exc:
            error = json.dumps(
                {"error": {"type": type(exc).__name__, "message": str(exc)}}
            )
            sys.stdout.write(error + "\n")
            sys.stdout.flush()
            return
        sys.stdout.write(output + "\n")
        sys.stdout.flush()
