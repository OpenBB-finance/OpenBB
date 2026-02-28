# P2: Strategy Configurability + Regression Hardening

## Goals
- Make provider auto-selection strategy configurable without code changes.
- Improve daily regression so results are explainable and internally consistent.

## Scope
- Strategy engine:
  - Support external JSON config via `OPENBB_PROVIDER_STRATEGY_PATH`.
  - Configurable items: provider priority, route policy bonus, credential bonuses, health weights.
  - Add `selection_reason.strategy_source` in meta for traceability.
- Daily regression:
  - Require `meta.selection_reason`.
  - Validate `provider_used` appears in `provider_candidates`.
  - Validate fallback trace final step is `success` and matches `provider_used`.
  - Support `expected_selection_mode` and optional `expected_provider_used`.

## Changed Files
- `openbb_platform/core/openbb_core/api/provider_strategy.py`
- `build/quality/run_daily_regression.py`
- `build/quality/daily_regression_cases.json`
- `build/quality/README.md`
- `openbb_integration_guide.md`

## Validation
- Router strategy tests and meta tests pass with P2 assertions.
- Regression script checks are stricter and produce auditable reports with richer check matrix.
