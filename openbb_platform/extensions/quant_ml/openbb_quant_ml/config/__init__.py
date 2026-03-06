"""Runtime configuration helpers for Quant ML extension."""

from __future__ import annotations

import os

REQUIRED_ENV_VARS = ["FRED_API_KEY"]


def validate_env() -> None:
    """Validate required environment variables and fail fast when missing."""
    skip = str(os.getenv("OPENBB_QUANT_ML_SKIP_ENV_VALIDATION", "")).strip().lower()
    if skip in {"1", "true", "yes"}:
        return

    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        raise OSError(f"Missing required env vars: {', '.join(missing)}")
