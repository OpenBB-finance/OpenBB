"""Constants used by the Quant ML service layer."""

from __future__ import annotations

from pathlib import Path

ARTIFACT_ROOT = Path.home() / ".openbb_platform" / "quant_ml"
CACHE_DIR = ARTIFACT_ROOT / "cache" / "market_data"
RUNS_DIR = ARTIFACT_ROOT / "runs"
REGISTRY_PATH = ARTIFACT_ROOT / "registry.json"
UNIVERSE_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "universe.yaml"

CACHE_TTL_DAYS = 7
MAX_LOG_LINES = 200
