"""Constants used by the Quant ML service layer."""

from __future__ import annotations

from pathlib import Path

ARTIFACT_ROOT = Path.home() / ".openbb_platform" / "quant_ml"
CACHE_DIR = ARTIFACT_ROOT / "cache" / "market_data"
RAW_STORE_DIR = ARTIFACT_ROOT / "raw_store"
FEATURE_STORE_DIR = ARTIFACT_ROOT / "feature_store"
LAKE_DIR = ARTIFACT_ROOT / "lake"
LAKE_BRONZE_DIR = LAKE_DIR / "bronze"
LAKE_SILVER_DIR = LAKE_DIR / "silver"
LAKE_GOLD_DIR = LAKE_DIR / "gold"
VERSIONS_DIR = ARTIFACT_ROOT / "versions"
RUNTIME_DIR = ARTIFACT_ROOT / "runtime"
INDEX_DIR = ARTIFACT_ROOT / "index"
WALKFORWARD_DIR = ARTIFACT_ROOT / "walkforward"
REPORTS_DIR = ARTIFACT_ROOT / "reports"
NOTIFICATION_DIR = ARTIFACT_ROOT / "notifications"
TRADING_DIR = ARTIFACT_ROOT / "trading"
TRADING_SIGNALS_DIR = TRADING_DIR / "signals"
TRADING_ORDERS_DIR = TRADING_DIR / "orders"
TRADING_FILLS_DIR = TRADING_DIR / "fills"
TRADING_POSITIONS_DIR = TRADING_DIR / "positions"
TRADING_PERFORMANCE_DIR = TRADING_DIR / "performance"
TRADING_LOGS_DIR = TRADING_DIR / "logs"
TRADING_RISK_DIR = TRADING_DIR / "risk"
TRADING_ALGORITHMS_DIR = TRADING_DIR / "algorithms"
TRADING_ALGORITHM_REGISTRY_DIR = TRADING_DIR / "algorithm_registry"
TRADING_VALIDATION_REPORTS_DIR = TRADING_DIR / "validation_reports"
TRADING_SETTINGS_DIR = TRADING_DIR / "settings"
TRADING_ACCOUNT_STATE_DIR = TRADING_DIR / "account_state"
DATA_VERSION_PATH = VERSIONS_DIR / "data_version.json"
FEATURE_VERSION_PATH = VERSIONS_DIR / "feature_version.json"
RUNS_DIR = ARTIFACT_ROOT / "runs"
REGISTRY_PATH = ARTIFACT_ROOT / "registry.json"
RUN_REGISTRY_DB_PATH = ARTIFACT_ROOT / "run_registry.sqlite3"
PROMOTED_MODEL_PATH = RUNTIME_DIR / "promoted_model.json"
OPS_POLICY_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "ops_policy.yaml"
)
OPS_JOBS_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "ops_jobs.yaml"
)
TRADING_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "trading.yaml"
)
RUNS_INDEX_PATH = INDEX_DIR / "runs_index.json"
WALKFORWARD_JOBS_PATH = WALKFORWARD_DIR / "jobs.json"
UNIVERSE_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "universe.yaml"
)

CACHE_TTL_DAYS = 7
MAX_LOG_LINES = 200
