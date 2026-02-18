# OpenBB Extension Sync Policy

## Source Of Truth

- Primary runtime tree: `openbb_platform/...`
- Mirror tree for release verification only: `OpenBB/openbb_platform/...`

## Regeneration Procedure

1. Regenerate package/reference from installed entry points:
   - `python -m openbb_core.app.static.package_builder`
2. Copy generated artifacts to mirror tree:
   - `openbb_platform/core/openbb/assets/reference.json`
   - `openbb_platform/core/openbb/package/__extensions__.py`
3. Ensure optional quant plugin policy matches in both pyproject files:
   - `openbb_platform/pyproject.toml`
   - `OpenBB/openbb_platform/pyproject.toml`

## Validation Commands

1. Unused feature audit report:
   - `python openbb_platform/tools/unused_features_audit.py`
2. Mirror sync policy check:
   - `python openbb_platform/tools/check_openbb_sync.py`

Both commands are wired in CI and should remain green before release cut.
