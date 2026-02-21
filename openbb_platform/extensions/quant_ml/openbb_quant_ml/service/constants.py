"""Constants used by the Quant ML service layer."""

from __future__ import annotations

from pathlib import Path

ARTIFACT_ROOT = Path.home() / ".openbb_platform" / "quant_ml"
CACHE_DIR = ARTIFACT_ROOT / "cache" / "market_data"
RAW_STORE_DIR = ARTIFACT_ROOT / "raw_store"
FEATURE_STORE_DIR = ARTIFACT_ROOT / "feature_store"
VERSIONS_DIR = ARTIFACT_ROOT / "versions"
RUNTIME_DIR = ARTIFACT_ROOT / "runtime"
INDEX_DIR = ARTIFACT_ROOT / "index"
WALKFORWARD_DIR = ARTIFACT_ROOT / "walkforward"
DATA_VERSION_PATH = VERSIONS_DIR / "data_version.json"
FEATURE_VERSION_PATH = VERSIONS_DIR / "feature_version.json"
RUNS_DIR = ARTIFACT_ROOT / "runs"
REGISTRY_PATH = ARTIFACT_ROOT / "registry.json"
RUN_REGISTRY_DB_PATH = ARTIFACT_ROOT / "run_registry.sqlite3"
PROMOTED_MODEL_PATH = RUNTIME_DIR / "promoted_model.json"
RUNS_INDEX_PATH = INDEX_DIR / "runs_index.json"
WALKFORWARD_JOBS_PATH = WALKFORWARD_DIR / "jobs.json"
UNIVERSE_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "universe.yaml"
)

CACHE_TTL_DAYS = 7
MAX_LOG_LINES = 200
